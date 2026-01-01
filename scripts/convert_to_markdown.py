#!/usr/bin/env python3
"""
Convert Claude Code JSONL transcripts to beautiful human-readable Markdown.

This script processes conversation transcripts from Claude Code and generates
clean, formatted Markdown files that are easy to read and navigate.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def format_timestamp(timestamp_str: str) -> str:
    """Convert ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M:%S %p')
    except:
        return timestamp_str

def format_user_message(msg: Dict[str, Any]) -> str:
    """Format a user message."""
    content = msg.get('message', {}).get('content', '')

    # Handle string content
    if isinstance(content, str):
        return f"**You:** {content}\n\n"

    # Handle tool results
    if isinstance(content, list):
        results = []
        for item in content:
            if item.get('type') == 'tool_result':
                tool_content = item.get('content', '')
                if item.get('is_error'):
                    results.append(f"❌ Error:\n```\n{tool_content}\n```")
                else:
                    # Don't show tool results in chat view - too verbose
                    pass
        if results:
            return '\n'.join(results) + '\n\n'

    return ""

def format_assistant_message(msg: Dict[str, Any]) -> str:
    """Format an assistant message with thinking, text, and tool usage."""
    content = msg.get('message', {}).get('content', [])
    if not isinstance(content, list):
        return ""

    output = []
    has_text = False

    for item in content:
        item_type = item.get('type')

        if item_type == 'thinking':
            thinking = item.get('thinking', '')
            if thinking:
                output.append(f"<details><summary>💭 thinking</summary>\n{thinking}\n</details>")

        elif item_type == 'text':
            text = item.get('text', '')
            if text:
                output.append(f"**Claude:** {text}")
                has_text = True

        elif item_type == 'tool_use':
            tool_name = item.get('name', 'Unknown')
            tool_input = item.get('input', {})

            # Format based on tool type - much more compact
            if tool_name == 'Bash':
                cmd = tool_input.get('command', '')
                output.append(f"```bash\n$ {cmd}\n```")

            elif tool_name in ['Read', 'Write', 'Edit']:
                file_path = tool_input.get('file_path', '')
                output.append(f"*{tool_name}: `{file_path}`*")

            elif tool_name == 'WebSearch':
                query = tool_input.get('query', '')
                output.append(f"*🔍 {query}*")

            elif tool_name == 'WebFetch':
                url = tool_input.get('url', '')
                output.append(f"*🌐 {url}*")

            elif tool_name == 'Task':
                subagent = tool_input.get('subagent_type', '')
                desc = tool_input.get('description', '')
                output.append(f"*→ Task: {desc} ({subagent})*")

            else:
                output.append(f"*Tool: {tool_name}*")

    return '\n'.join(output) + '\n\n' if output else ''

def convert_jsonl_to_markdown(jsonl_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Convert a single JSONL file to markdown."""
    messages = []

    # Read JSONL file
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not messages:
        return None

    # Extract metadata
    first_msg = messages[0]
    session_id = first_msg.get('sessionId', jsonl_path.stem)
    timestamp = first_msg.get('timestamp', '')

    # Start building markdown
    md_lines = []
    md_lines.append(f"# {session_id}\n\n")

    # Count messages
    user_count = sum(1 for m in messages if m.get('type') == 'user')
    assistant_count = sum(1 for m in messages if m.get('type') == 'assistant')
    md_lines.append(f"*{format_timestamp(timestamp)} • {user_count} prompts, {assistant_count} responses*\n\n")
    md_lines.append("---\n\n")

    # Process messages
    for msg in messages:
        msg_type = msg.get('type')

        if msg_type == 'user':
            formatted = format_user_message(msg)
            if formatted:
                md_lines.append(formatted)

        elif msg_type == 'assistant':
            formatted = format_assistant_message(msg)
            if formatted:
                md_lines.append(formatted)

        elif msg_type == 'file-history-snapshot':
            # Add a subtle separator for file snapshots
            md_lines.append("---\n\n")

    # Write markdown file
    md_filename = jsonl_path.stem + '.md'
    md_path = output_dir / md_filename

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(''.join(md_lines))

    return {
        'session_id': session_id,
        'filename': md_filename,
        'timestamp': timestamp,
        'user_messages': user_count,
        'assistant_messages': assistant_count
    }

def create_index(sessions: List[Dict[str, Any]], output_dir: Path):
    """Create an index markdown file."""
    md_lines = [
        "# Claude Code Conversations - Markdown Transcripts\n\n",
        "Beautiful, human-readable versions of all conversation transcripts.\n\n",
        f"**Total Conversations:** {len(sessions)}\n",
        f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n",
        "---\n\n",
        "## Conversations\n\n"
    ]

    # Sort by timestamp (newest first)
    sorted_sessions = sorted(
        sessions,
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )

    for session in sorted_sessions:
        session_id = session['session_id']
        filename = session['filename']
        timestamp = format_timestamp(session.get('timestamp', ''))
        user_msgs = session.get('user_messages', 0)
        assistant_msgs = session.get('assistant_messages', 0)

        md_lines.append(
            f"### [{session_id}]({filename})\n\n"
            f"- **Date:** {timestamp}\n"
            f"- **Messages:** {user_msgs} prompts, {assistant_msgs} responses\n\n"
        )

    md_lines.append("\n---\n\n")
    md_lines.append("*Generated automatically by GitHub Actions*\n")

    index_path = output_dir / 'README.md'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(''.join(md_lines))

def main():
    """Main conversion process."""
    # Setup paths
    project_root = Path(__file__).parent.parent
    transcripts_dir = project_root / 'transcripts'
    output_dir = project_root / 'transcripts-markdown'

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Process all JSONL files
    sessions = []
    jsonl_files = list(transcripts_dir.glob('*.jsonl'))

    print(f"Converting {len(jsonl_files)} JSONL files to Markdown...")

    for jsonl_path in jsonl_files:
        print(f"  Processing: {jsonl_path.name}")
        session_info = convert_jsonl_to_markdown(jsonl_path, output_dir)
        if session_info:
            sessions.append(session_info)

    # Create index
    print("Creating index...")
    create_index(sessions, output_dir)

    print(f"✓ Converted {len(sessions)} conversations to Markdown")
    print(f"✓ Output directory: {output_dir}")

if __name__ == '__main__':
    main()
