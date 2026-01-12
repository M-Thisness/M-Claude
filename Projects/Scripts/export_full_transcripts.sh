#!/bin/bash
# Claude Code Full Transcript Exporter
# This script creates a comprehensive export with all full conversation transcripts

OUTPUT_FILE="$HOME/claude_code_FULL_export_$(date +%Y%m%d_%H%M%S).md"

echo "# Claude Code Complete History - Full Transcripts Export" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**Export Date:** $(date '+%B %d, %Y at %I:%M %p')" >> "$OUTPUT_FILE"
echo "**Export Type:** Complete with full conversation transcripts" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Counter
SESSION_NUM=0

# Read history.jsonl and process in order
python3 << 'PYTHON_SCRIPT' >> "$OUTPUT_FILE"
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

history_file = Path.home() / '.claude' / 'history.jsonl'
debug_dir = Path.home() / '.claude' / 'debug'

# Parse history
sessions = defaultdict(list)
with open(history_file, 'r') as f:
    for line in f:
        if line.strip():
            entry = json.loads(line)
            session_id = entry.get('sessionId')
            timestamp = entry.get('timestamp', 0)
            display = entry.get('display', '')

            if session_id and display.strip():
                dt = datetime.fromtimestamp(timestamp / 1000.0)
                sessions[session_id].append({
                    'timestamp': dt,
                    'display': display,
                    'project': entry.get('project', '')
                })

# Sort sessions by first timestamp
session_order = sorted(sessions.items(), key=lambda x: x[1][0]['timestamp'])

# Process each session
for idx, (session_id, prompts) in enumerate(session_order, 1):
    first_prompt = prompts[0]
    date_str = first_prompt['timestamp'].strftime('%B %d, %Y at %I:%M %p')

    print(f"\n## Session {idx}: {date_str}")
    print(f"**Session ID:** `{session_id}`")
    print(f"**Working Directory:** `{first_prompt['project']}`")
    print(f"**Number of Prompts:** {len(prompts)}\n")

    # List prompts
    print("### User Prompts:")
    for i, prompt in enumerate(prompts, 1):
        time_str = prompt['timestamp'].strftime('%I:%M:%S %p')
        display_text = prompt['display'].replace('`', '\\`')
        print(f"{i}. [{time_str}] {display_text}")

    # Include full transcript if available
    debug_file = debug_dir / f"{session_id}.txt"
    if debug_file.exists():
        print(f"\n### Full Conversation Transcript:")
        print("```")
        try:
            with open(debug_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Truncate very long transcripts
                if len(content) > 50000:
                    print(content[:50000])
                    print("\n\n[... Transcript truncated - too long to display fully ...]")
                else:
                    print(content)
        except Exception as e:
            print(f"Error reading transcript: {e}")
        print("```")
    else:
        print(f"\n**Full Transcript:** Not available")

    print("\n" + "="*80 + "\n")

PYTHON_SCRIPT

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**Export Complete**" >> "$OUTPUT_FILE"
echo "This file contains all available conversation transcripts from Claude Code." >> "$OUTPUT_FILE"

echo ""
echo "✓ Full transcript export created at: $OUTPUT_FILE"
echo ""
echo "Warning: This file may be very large (>1MB) as it contains full conversation history."
echo ""
