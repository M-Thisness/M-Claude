#!/usr/bin/env python3
"""
Convert Claude Code JSONL transcripts to a single chronological Markdown file.

This script processes all conversation transcripts from Claude Code and generates
a single, chronologically ordered Markdown file for easy reading.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

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

def load_all_messages(transcripts_dir: Path) -> List[Tuple[Dict[str, Any], str]]:
    """Load all messages from all JSONL files with their session IDs."""
    all_messages = []

    jsonl_files = list(transcripts_dir.glob('*.jsonl'))
    print(f"Loading messages from {len(jsonl_files)} conversation files...")

    for jsonl_path in jsonl_files:
        try:
            with open(jsonl_path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            session_id = msg.get('sessionId', jsonl_path.stem)
                            # Store message with session ID
                            all_messages.append((msg, session_id))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"  Warning: Error reading {jsonl_path.name}: {e}")

    return all_messages

def create_chronological_markdown(messages_with_sessions: List[Tuple[Dict[str, Any], str]], output_path: Path):
    """Create a single chronologically ordered markdown file."""

    # Sort all messages by timestamp
    print("Sorting messages chronologically...")
    sorted_messages = sorted(
        messages_with_sessions,
        key=lambda x: x[0].get('timestamp', '')
    )

    # Start building markdown
    md_lines = []
    md_lines.append("# Claude Code Conversations - Complete Chronological History\n\n")
    md_lines.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
    md_lines.append(f"**Total Messages:** {len(sorted_messages)}\n\n")
    md_lines.append("All conversations merged and sorted chronologically from oldest to newest.\n\n")
    md_lines.append("---\n\n")

    current_session = None
    session_start_time = None

    for msg, session_id in sorted_messages:
        msg_type = msg.get('type')
        timestamp = msg.get('timestamp', '')

        # Add session header when we encounter a new session
        if session_id != current_session:
            if current_session is not None:
                md_lines.append("\n---\n\n")  # Separator between sessions

            current_session = session_id
            session_start_time = timestamp

            md_lines.append(f"## Session: {session_id}\n\n")
            if timestamp:
                md_lines.append(f"*Started: {format_timestamp(timestamp)}*\n\n")

        # Format messages
        if msg_type == 'user':
            formatted = format_user_message(msg)
            if formatted:
                md_lines.append(formatted)

        elif msg_type == 'assistant':
            formatted = format_assistant_message(msg)
            if formatted:
                md_lines.append(formatted)

    # Footer
    md_lines.append("\n\n---\n\n")
    md_lines.append("*Generated automatically from Claude Code conversation logs*\n")

    # Write to file
    print(f"Writing chronological markdown to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(md_lines))

    print(f"✓ Created chronological transcript with {len(sorted_messages)} messages")

def main():
    """Main conversion process."""
    # Setup paths
    project_root = Path(__file__).parent.parent
    transcripts_dir = project_root / 'transcripts'
    output_file = project_root / 'CHRONOLOGICAL_TRANSCRIPT.md'

    print("=" * 70)
    print("Claude Code JSONL → Chronological Markdown Converter")
    print("=" * 70)
    print()

    # Load all messages from all files
    messages_with_sessions = load_all_messages(transcripts_dir)

    if not messages_with_sessions:
        print("No messages found!")
        return

    print(f"Loaded {len(messages_with_sessions)} total messages")
    print()

    # Create single chronological markdown file
    create_chronological_markdown(messages_with_sessions, output_file)

    print()
    print("=" * 70)
    print(f"✓ Complete! Output: {output_file}")
    print("=" * 70)

if __name__ == '__main__':
    main()
