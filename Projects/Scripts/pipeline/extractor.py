#!/usr/bin/env python3
"""
M-Claude Content Extractor

Extracts structured content from JSONL conversation messages.
Preserves full assistant responses (not just first paragraph).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple


@dataclass
class ExtractedContent:
    """Structured content extracted from a message."""

    text: str = ""                          # Full plaintext content
    summary: str = ""                       # Smart summary (first 1000 chars)
    thinking: str = ""                      # Extended thinking content
    code_blocks: List[Dict[str, str]] = field(default_factory=list)  # {language, code}
    tool_uses: List[Dict[str, Any]] = field(default_factory=list)
    has_tool_use: bool = False


@dataclass
class ExtractedToolCall:
    """Structured tool call information."""

    tool_id: str
    tool_name: str
    input_json: str
    file_path: Optional[str] = None
    command: Optional[str] = None
    description: str = ""


def iter_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    """
    Memory-efficient JSONL iterator.

    Yields one parsed JSON object per line, skipping malformed lines.
    """
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # Skip malformed lines silently (logged elsewhere)
                continue


def extract_text_content(msg: Dict[str, Any]) -> str:
    """
    Extract plaintext content from a message.

    Handles both string content and list content formats.
    """
    content = msg.get('message', {}).get('content', '')

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif item.get('type') == 'thinking':
                    # Include thinking in search but mark it
                    thinking = item.get('thinking', '')
                    if thinking:
                        text_parts.append(f"[THINKING] {thinking}")
        return '\n'.join(text_parts)

    return ''


def extract_thinking(msg: Dict[str, Any]) -> str:
    """Extract extended thinking content if present."""
    content = msg.get('message', {}).get('content', [])

    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'thinking':
                return item.get('thinking', '')

    return ''


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract fenced code blocks from text.

    Returns list of {language: str, code: str} dicts.
    """
    pattern = r'```(\w*)\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    return [
        {'language': lang or 'text', 'code': code.strip()}
        for lang, code in matches
    ]


def extract_tool_calls(msg: Dict[str, Any]) -> List[ExtractedToolCall]:
    """
    Extract tool call information from a message.

    Parses tool_use content blocks and extracts relevant fields.
    """
    content = msg.get('message', {}).get('content', [])
    tool_calls = []

    if not isinstance(content, list):
        return tool_calls

    for item in content:
        if isinstance(item, dict) and item.get('type') == 'tool_use':
            tool_name = item.get('name', 'unknown')
            tool_input = item.get('input', {})

            # Extract file path from various tool inputs
            file_path = (
                tool_input.get('file_path') or
                tool_input.get('filePath') or
                tool_input.get('path')
            )

            # Extract command from Bash tool
            command = tool_input.get('command') if tool_name == 'Bash' else None

            # Generate human-readable description
            description = generate_tool_description(tool_name, tool_input)

            tool_calls.append(ExtractedToolCall(
                tool_id=item.get('id', ''),
                tool_name=tool_name,
                input_json=json.dumps(tool_input),
                file_path=file_path,
                command=command,
                description=description,
            ))

    return tool_calls


def generate_tool_description(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Generate a human-readable description of a tool call."""
    if tool_name == 'Bash':
        cmd = tool_input.get('command', '')
        if not cmd:
            return "Run shell command"
        # Extract first meaningful part of command
        cmd_short = cmd.split('\n')[0].split('&&')[0].strip()[:60]
        if len(cmd) > 60:
            cmd_short += "..."
        return f"`{cmd_short}`"

    elif tool_name == 'Read':
        path = tool_input.get('file_path', '')
        filename = Path(path).name if path else 'file'
        return f"Read {filename}"

    elif tool_name in ('Write', 'write_to_file'):
        path = tool_input.get('file_path', '')
        filename = Path(path).name if path else 'file'
        return f"Create {filename}"

    elif tool_name in ('Edit', 'MultiEdit', 'edit_file'):
        path = tool_input.get('file_path', '')
        filename = Path(path).name if path else 'file'
        return f"Edit {filename}"

    elif tool_name == 'Grep':
        pattern = tool_input.get('pattern', '')[:30]
        return f"Search for `{pattern}`"

    elif tool_name == 'Glob':
        pattern = tool_input.get('pattern', '')[:30]
        return f"Find files matching `{pattern}`"

    elif tool_name == 'Task':
        desc = tool_input.get('description', '')
        return desc[:50] if desc else "Run subagent"

    elif tool_name == 'WebFetch':
        url = tool_input.get('url', '')
        return f"Fetch {url[:40]}..." if len(url) > 40 else f"Fetch {url}"

    elif tool_name == 'WebSearch':
        query = tool_input.get('query', '')[:30]
        return f"Search web for `{query}`"

    elif tool_name == 'TodoWrite':
        return "Update todo list"

    elif tool_name == 'AskUserQuestion':
        return "Ask user question"

    else:
        return f"{tool_name} operation"


def generate_smart_summary(text: str, max_length: int = 1000) -> str:
    """
    Generate an intelligent summary of text content.

    Preserves meaningful content, not just truncation.
    """
    if not text:
        return ""

    # Remove code blocks for summary (they're stored separately)
    text_no_code = re.sub(r'```[\s\S]*?```', '[CODE]', text)

    # Split into paragraphs
    paragraphs = [p.strip() for p in text_no_code.split('\n\n') if p.strip()]

    if not paragraphs:
        return text[:max_length]

    # Take first few meaningful paragraphs
    summary_parts = []
    current_length = 0

    for para in paragraphs:
        # Skip very short or meta paragraphs
        if len(para) < 20:
            continue
        if para.startswith('```') or para.startswith('---'):
            continue

        if current_length + len(para) > max_length:
            # Truncate last paragraph if needed
            remaining = max_length - current_length
            if remaining > 50:
                summary_parts.append(para[:remaining] + "...")
            break

        summary_parts.append(para)
        current_length += len(para) + 2  # +2 for newlines

    return '\n\n'.join(summary_parts) or text[:max_length]


def extract_message_content(msg: Dict[str, Any]) -> ExtractedContent:
    """
    Extract comprehensive content from a message.

    Returns structured content with text, summary, thinking, code blocks, and tool uses.
    """
    result = ExtractedContent()

    # Get basic text content
    result.text = extract_text_content(msg)
    result.thinking = extract_thinking(msg)

    # Extract code blocks
    result.code_blocks = extract_code_blocks(result.text)

    # Generate smart summary
    result.summary = generate_smart_summary(result.text)

    # Extract tool calls
    tool_calls = extract_tool_calls(msg)
    result.tool_uses = [
        {
            'id': tc.tool_id,
            'name': tc.tool_name,
            'input': json.loads(tc.input_json),
            'description': tc.description,
        }
        for tc in tool_calls
    ]
    result.has_tool_use = len(tool_calls) > 0

    return result


def extract_session_metadata(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract session-level metadata from messages.

    Scans for title, duration, platform info, etc.
    """
    metadata = {
        'title': '',
        'duration_ms': 0,
        'cwd': '',
        'git_branch': '',
        'platform': '',
        'claude_version': '',
        'first_timestamp': None,
        'last_timestamp': None,
    }

    for msg in messages:
        # Get title from summary messages
        if msg.get('type') == 'summary':
            metadata['title'] = msg.get('summary', '') or metadata['title']

        # Accumulate duration
        if msg.get('type') == 'system' and msg.get('subtype') == 'turn_duration':
            metadata['duration_ms'] += msg.get('durationMs', 0)

        # Get platform info from first message
        if not metadata['cwd'] and msg.get('cwd'):
            metadata['cwd'] = msg.get('cwd')
            metadata['git_branch'] = msg.get('gitBranch', '')
            metadata['claude_version'] = msg.get('version', '')

            # Detect platform from cwd
            cwd = metadata['cwd']
            if cwd.startswith('/Users/'):
                metadata['platform'] = 'macos'
            elif cwd.startswith('/home/'):
                metadata['platform'] = 'linux'
            elif cwd.startswith('C:\\') or cwd.startswith('C:/'):
                metadata['platform'] = 'windows'
            elif '/com.termux/' in cwd:
                metadata['platform'] = 'termux'

        # Track timestamps
        ts = msg.get('timestamp')
        if ts:
            if not metadata['first_timestamp']:
                metadata['first_timestamp'] = ts
            metadata['last_timestamp'] = ts

    # Generate title from first user prompt if not found
    if not metadata['title']:
        for msg in messages:
            if msg.get('type') == 'user' and not msg.get('isMeta'):
                content = extract_text_content(msg)
                if content and len(content) > 10:
                    metadata['title'] = content[:80]
                    if len(content) > 80:
                        metadata['title'] += '...'
                    break

    return metadata
