#!/usr/bin/env python3
"""
Generate daily journal entries from chronological transcript.

Creates journal files organized by day with Morning/Day/Night sections
summarizing collaborative work accomplished.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    try:
        # Handle Z suffix
        ts = timestamp_str.replace('Z', '+00:00')
        return datetime.fromisoformat(ts)
    except:
        return None

def get_time_of_day(hour: int) -> str:
    """Determine if hour is morning, day, or night."""
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 20:
        return "Day"
    else:
        return "Night"

def summarize_session(messages: List[Dict]) -> str:
    """Create a tweet-length summary of what was accomplished in a session."""
    # Extract user prompts and key actions
    user_prompts = []
    tools_used = set()
    files_modified = []

    for msg in messages:
        msg_type = msg.get('type')

        if msg_type == 'user':
            content = msg.get('message', {}).get('content', '')
            if isinstance(content, str) and content:
                # Skip meta messages and warmups
                if not any(x in content.lower() for x in [
                    'caveat:', 'command-name', 'local-command', 'stdout', 'stderr',
                    'rate-limit', 'login successful', 'touch_key', 'warmup', 'resume'
                ]):
                    clean = content.strip()
                    if clean and len(clean) > 3:
                        user_prompts.append(clean)

        elif msg_type == 'assistant':
            content = msg.get('message', {}).get('content', [])
            if isinstance(content, list):
                for item in content:
                    if item.get('type') == 'tool_use':
                        tool = item.get('name', '')
                        tools_used.add(tool)

                        # Track files
                        if tool in ['Write', 'Edit']:
                            inp = item.get('input', {})
                            filepath = inp.get('file_path', '')
                            if filepath:
                                filename = Path(filepath).name
                                if filename not in files_modified:
                                    files_modified.append(filename)

    # Build summary
    if user_prompts:
        # Use first meaningful prompt
        main_task = user_prompts[0]

        # Add action context
        context = []
        if 'Write' in tools_used or 'Edit' in tools_used:
            if files_modified:
                context.append(f"Modified {', '.join(files_modified[:2])}")
        elif 'Bash' in tools_used:
            context.append("Ran commands")
        elif 'Task' in tools_used:
            context.append("Spawned agents")

        # Build full summary
        if context:
            summary = f"{main_task} → {' + '.join(context)}"
        else:
            summary = main_task

        # Truncate to tweet length (280 chars)
        if len(summary) > 280:
            summary = summary[:277] + "..."

        return summary

    # Fallback based on tools
    if tools_used:
        return f"Used {', '.join(sorted(tools_used)[:3])}"

    return "Brief session"

def load_all_sessions(transcripts_dir: Path) -> Dict[str, List[Tuple[datetime, str, List[Dict]]]]:
    """Load all sessions grouped by date."""
    sessions_by_date = defaultdict(list)

    jsonl_files = list(transcripts_dir.glob('*.jsonl'))
    print(f"Loading {len(jsonl_files)} conversation files...")

    for jsonl_path in jsonl_files:
        session_id = jsonl_path.stem
        messages = []
        first_timestamp = None

        try:
            with open(jsonl_path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            messages.append(msg)

                            # Get first timestamp
                            if first_timestamp is None and 'timestamp' in msg:
                                ts = parse_timestamp(msg['timestamp'])
                                if ts:
                                    first_timestamp = ts
                        except:
                            continue
        except:
            continue

        if first_timestamp and messages:
            # Group by date
            date_key = first_timestamp.strftime('%Y-%m-%d')
            sessions_by_date[date_key].append((first_timestamp, session_id, messages))

    return sessions_by_date

def create_journal_entry(date: str, sessions: List[Tuple[datetime, str, List[Dict]]], output_path: Path):
    """Create a daily journal entry."""
    # Collect all entries for the day
    entries = []

    for timestamp, session_id, messages in sessions:
        summary = summarize_session(messages)

        # Only include meaningful summaries
        if summary and summary != "Brief session":
            time_str = timestamp.strftime('%I:%M %p')
            entries.append((timestamp, time_str, summary))

    # Sort all entries by time
    entries.sort(key=lambda x: x[0])

    # Build markdown
    md_lines = []
    md_lines.append(f"# {date}\n\n")

    if entries:
        for _, time_str, summary in entries:
            md_lines.append(f"**{time_str}:** {summary}\n\n")
    else:
        md_lines.append("*No activity*\n\n")

    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(md_lines))

def main():
    """Generate all journal entries."""
    project_root = Path(__file__).parent.parent
    transcripts_dir = project_root / 'CHAT_LOGS'
    journals_dir = project_root / 'journals'

    # Create journals directory
    journals_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("Daily Journal Generator")
    print("=" * 70)
    print()

    # Load all sessions grouped by date
    sessions_by_date = load_all_sessions(transcripts_dir)

    print(f"Found activity across {len(sessions_by_date)} days")
    print()

    # Create journal entry for each date
    for date in sorted(sessions_by_date.keys()):
        sessions = sessions_by_date[date]

        # Create filename from date
        filename = f"{date}.md"
        output_path = journals_dir / filename

        create_journal_entry(date, sessions, output_path)
        print(f"  Created: {filename} ({len(sessions)} sessions)")

    print()
    print("=" * 70)
    print(f"✓ Generated {len(sessions_by_date)} journal entries")
    print(f"✓ Output: {journals_dir}")
    print("=" * 70)

if __name__ == '__main__':
    main()
