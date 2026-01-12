#!/usr/bin/env python3
"""
Claude Code Raw Log Sync + Convert Script

Syncs conversation logs from ~/.claude to Archives with redaction,
then converts ONLY newly synced sessions into daily journal entries.

Supported Platforms: Windows 11, macOS, Linux, Android (Termux)
"""

import os
import re
import json
import platform
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
HOME = Path.home()
REPO_ROOT = Path(__file__).parent.parent.parent  # Projects/Scripts -> Projects -> M-Claude
ARCHIVES_DEST = REPO_ROOT / "Archives"
JOURNALS_DEST = REPO_ROOT / "Journals"

# ============================================================================
# PLATFORM DETECTION
# ============================================================================

def get_claude_project_dirs() -> List[Path]:
    """Detect Claude Code project directories dynamically."""
    claude_base = HOME / ".claude" / "projects"
    project_dirs = []
    
    if not claude_base.exists():
        logger.warning(f"Claude base directory not found: {claude_base}")
        return project_dirs
    
    try:
        for entry in claude_base.iterdir():
            if entry.is_dir():
                jsonl_files = list(entry.glob("*.jsonl"))
                if jsonl_files:
                    project_dirs.append(entry)
    except PermissionError as e:
        logger.error(f"Permission denied accessing {claude_base}: {e}")
    
    return project_dirs

def get_platform_info() -> str:
    """Get detailed platform information."""
    if os.path.exists("/data/data/com.termux"):
        return "Android (Termux)"
    
    system = platform.system()
    if system == "Darwin":
        return f"macOS {platform.mac_ver()[0]}"
    elif system == "Windows":
        return f"Windows {platform.release()}"
    elif system == "Linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=")[1].strip().strip('"')
        except FileNotFoundError:
            pass
        return f"Linux {platform.release()}"
    
    return system

# ============================================================================
# REDACTION
# ============================================================================

BS = chr(92)  # backslash

SECRET_PATTERNS = [
    (r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]"),
    (r"(ghp_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]"),
    (r"(gho_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]"),
    (r"(xox[baprs]-[a-zA-Z0-9]{10,})", "[REDACTED_SLACK_TOKEN]"),
    (r"(AKIA[0-9A-Z]{16})", "[REDACTED_AWS_KEY]"),
    (r"(ya29\.[a-zA-Z0-9_-]{50,})", "[REDACTED_GOOGLE_TOKEN]"),
    # Stripe API keys
    (r"(sk_live_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]"),
    (r"(pk_live_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]"),
    (r"(sk_test_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]"),
    (r"(pk_test_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]"),
    (r"(rk_live_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]"),
    (r"(-----BEGIN [A-Z]+ PRIVATE KEY-----[^-]+-----END [A-Z]+ PRIVATE KEY-----)", "[REDACTED_PRIVATE_KEY]"),
    (r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", "[REDACTED_EMAIL]"),
    (r"(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})", "[REDACTED_CARD]"),
    (r"(\d{3}-\d{2}-\d{4})", "[REDACTED_SSN]"),
    (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", "[REDACTED_IP]"),
    (r"(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})", "[REDACTED_JWT]"),
    (r"(password\s*[:=]\s*['\"]?[^\s'\"]{8,}['\"]?)", "password=[REDACTED]"),
    (r"(token\s*[:=]\s*['\"]?[^\s'\"]{20,}['\"]?)", "token=[REDACTED]"),
    (r"(postgres://[^\s]+)", "[REDACTED_DB_CONNECTION]"),
    (r"(mysql://[^\s]+)", "[REDACTED_DB_CONNECTION]"),
    (r"(mongodb://[^\s]+)", "[REDACTED_DB_CONNECTION]"),
    (r"(/home/[a-zA-Z0-9_-]+)", "/home/[USER]"),
    (r"(/Users/[a-zA-Z0-9_-]+)", "/Users/[USER]"),
    (r"(C:/Users/[a-zA-Z0-9_-]+)", "C:/Users/[USER]"),
    (r"(/data/data/com\.termux/files/home)", "[TERMUX_HOME]"),
]

WIN_PATH_PATTERN = f'C:{BS}{BS}Users{BS}{BS}[a-zA-Z0-9_-]+'
WIN_PATH_REPLACEMENT = f'C:{BS}Users{BS}[USER]'

def redact_text(text: str) -> str:
    """Apply all redaction patterns to text."""
    if not isinstance(text, str):
        return text

    for pattern, replacement in SECRET_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    text = re.sub(WIN_PATH_PATTERN, lambda m: WIN_PATH_REPLACEMENT, text, flags=re.IGNORECASE)
    return text

# ============================================================================
# SYNC
# ============================================================================

def sync_jsonl_logs() -> Set[str]:
    """
    Sync and redact .jsonl conversation logs.
    Returns set of session IDs that were newly synced or updated.
    """
    os.makedirs(ARCHIVES_DEST, exist_ok=True)
    
    project_dirs = get_claude_project_dirs()
    newly_synced: Set[str] = set()
    
    if not project_dirs:
        logger.error("No Claude Code project directories found!")
        return newly_synced

    for claude_projects in project_dirs:
        jsonl_files = list(claude_projects.glob("*.jsonl"))
        logger.info(f"Found {len(jsonl_files)} logs in {claude_projects.name}")

        for src_file in jsonl_files:
            dest_file = ARCHIVES_DEST / src_file.name
            session_id = src_file.stem

            try:
                with open(src_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                redacted_content = redact_text(content)

                # Check if update needed
                should_write = True
                if dest_file.exists():
                    try:
                        with open(dest_file, 'r', encoding='utf-8', errors='replace') as f:
                            existing_content = f.read()
                        if existing_content == redacted_content:
                            should_write = False
                    except Exception:
                        pass

                if should_write:
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(redacted_content)
                    newly_synced.add(session_id)

            except Exception as e:
                logger.error(f"Error processing {src_file.name}: {e}")

    return newly_synced

# ============================================================================
# CONVERT - Parse JSONL to structured data
# ============================================================================

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    try:
        ts = timestamp_str.replace('Z', '+00:00')
        return datetime.fromisoformat(ts)
    except (ValueError, AttributeError):
        return None

def parse_session(jsonl_path: Path) -> Tuple[datetime, str, List[Dict]]:
    """
    Parse a JSONL session file into structured data.
    Returns: (first_timestamp, session_id, messages)
    """
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
                        
                        if first_timestamp is None and 'timestamp' in msg:
                            ts = parse_timestamp(msg['timestamp'])
                            if ts:
                                first_timestamp = ts
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error(f"Error reading {jsonl_path}: {e}")
    
    return first_timestamp, session_id, messages

def extract_session_summary(messages: List[Dict]) -> Dict:
    """
    Extract comprehensive summary from session messages.
    Parses user prompts, assistant responses, tool usage, and outcomes.
    """
    summary = {
        'title': '',           # Session summary/title from JSONL
        'user_prompts': [],    # All user prompts
        'assistant_texts': [], # Assistant text responses
        'tools_used': set(),   # Tool names used
        'files_modified': [],  # Files written/edited
        'files_read': [],      # Files read/analyzed
        'commands_run': [],    # Bash commands executed
        'key_actions': [],     # Notable actions taken
        'duration_ms': 0,      # Session duration
    }
    
    for msg in messages:
        msg_type = msg.get('type')
        
        # Extract session title from summary type
        if msg_type == 'summary':
            summary['title'] = msg.get('summary', '')
        
        # Extract duration
        if msg_type == 'system' and msg.get('subtype') == 'turn_duration':
            summary['duration_ms'] += msg.get('durationMs', 0)
        
        # User messages
        if msg_type == 'user':
            content = msg.get('message', {}).get('content', '')
            if isinstance(content, str) and content:
                # Skip system/meta messages
                skip_patterns = [
                    'caveat:', 'command-name', 'local-command', 'stdout', 'stderr',
                    'rate-limit', 'login successful', 'touch_key', 'warmup', 'resume',
                    '[file content]', 'file-history', 'is-snapshot', 'trackedfilebackups'
                ]
                lower_content = content.lower()
                if not any(x in lower_content for x in skip_patterns):
                    clean = content.strip()
                    if clean and len(clean) > 3 and len(clean) < 1000:
                        summary['user_prompts'].append(clean)
        
        # Assistant messages - extract text and tool usage
        elif msg_type == 'assistant':
            content = msg.get('message', {}).get('content', [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        # Text responses
                        if item.get('type') == 'text':
                            text = item.get('text', '')
                            if text and len(text) > 20:
                                # Extract first meaningful paragraph
                                lines = [l.strip() for l in text.split('\n') if l.strip()]
                                if lines:
                                    first_para = lines[0]
                                    if len(first_para) > 30 and not first_para.startswith('```'):
                                        summary['assistant_texts'].append(first_para[:300])
                        
                        # Tool usage
                        elif item.get('type') == 'tool_use':
                            tool = item.get('name', '')
                            inp = item.get('input', {})
                            summary['tools_used'].add(tool)
                            
                            # File writes/edits
                            if tool in ['Write', 'Edit', 'MultiEdit', 'write_to_file', 'edit_file']:
                                filepath = inp.get('file_path', '') or inp.get('filePath', '') or inp.get('path', '')
                                if filepath:
                                    filename = Path(filepath).name
                                    if filename and filename not in summary['files_modified']:
                                        summary['files_modified'].append(filename)
                                        summary['key_actions'].append(f"Modified `{filename}`")
                            
                            # File reads
                            elif tool in ['Read', 'read_file', 'view_file']:
                                filepath = inp.get('file_path', '') or inp.get('path', '')
                                if filepath:
                                    filename = Path(filepath).name
                                    if filename and filename not in summary['files_read']:
                                        summary['files_read'].append(filename)
                            
                            # Command executions
                            elif tool in ['Bash', 'run_command']:
                                cmd = inp.get('command', '') or inp.get('CommandLine', '')
                                if cmd and len(cmd) < 150:
                                    # Clean up and truncate command
                                    cmd_clean = cmd.strip().split('\n')[0][:80]
                                    summary['commands_run'].append(cmd_clean)
                                    summary['key_actions'].append(f"Ran `{cmd_clean}`")
                            
                            # Sub-agents/tasks
                            elif tool in ['Task', 'dispatch_agent']:
                                task_desc = inp.get('description', '') or inp.get('task', '')
                                if task_desc:
                                    summary['key_actions'].append(f"Spawned agent: {task_desc[:60]}")
    
    return summary

def summarize_session_narrative(summary: Dict) -> Tuple[str, str]:
    """
    Create rich human-readable narrative from session summary.
    Returns: (title, body_markdown)
    """
    # Title: use session title if available, else first prompt
    title = summary.get('title', '')
    if not title and summary['user_prompts']:
        title = summary['user_prompts'][0]
        if len(title) > 80:
            title = title[:77] + "..."
    
    if not title:
        title = "Brief interaction"
    
    # Build body
    body_parts = []
    
    # Key actions performed
    if summary['key_actions']:
        actions = summary['key_actions'][:5]  # Limit to 5
        body_parts.append("**Actions:** " + " • ".join(actions))
    
    # Files modified
    if summary['files_modified']:
        files = summary['files_modified'][:5]
        body_parts.append(f"**Files:** `{'`, `'.join(files)}`")
    
    # Duration
    if summary['duration_ms'] > 0:
        duration_sec = summary['duration_ms'] / 1000
        if duration_sec > 60:
            duration_str = f"{duration_sec / 60:.1f}m"
        else:
            duration_str = f"{duration_sec:.0f}s"
        body_parts.append(f"⏱️ {duration_str}")
    
    body = " | ".join(body_parts) if body_parts else ""
    
    return title, body

# ============================================================================
# JOURNAL GENERATION
# ============================================================================

def format_duration(ms: int) -> str:
    """Format milliseconds to human readable duration."""
    if ms <= 0:
        return ""
    sec = ms / 1000
    if sec > 3600:
        return f"{sec / 3600:.1f}h"
    elif sec > 60:
        return f"{sec / 60:.0f}m"
    else:
        return f"{sec:.0f}s"

def update_journal_for_date(date_str: str, sessions: List[Tuple[datetime, str, List[Dict]]]):
    """
    Create rich journal entry for a specific date.
    Produces human-readable markdown with session details.
    """
    os.makedirs(JOURNALS_DEST, exist_ok=True)
    journal_path = JOURNALS_DEST / f"{date_str}.md"
    
    # Build entries for all sessions
    entries = []
    total_duration = 0
    
    for timestamp, session_id, messages in sessions:
        if not timestamp:
            continue
        
        summary = extract_session_summary(messages)
        title, body = summarize_session_narrative(summary)
        
        total_duration += summary['duration_ms']
        
        if title and title != "Brief interaction":
            time_str = timestamp.strftime('%I:%M %p')
            entries.append({
                'timestamp': timestamp,
                'time_str': time_str,
                'title': title,
                'body': body,
                'prompts': summary['user_prompts'][1:4],  # Additional prompts
                'files': summary['files_modified'],
            })
    
    # Sort by time
    entries.sort(key=lambda x: x['timestamp'])
    
    # Build markdown
    md_lines = [f"# {date_str}\n\n"]
    
    # Summary line
    if entries:
        duration_str = format_duration(total_duration)
        if duration_str:
            md_lines.append(f"*{len(entries)} sessions • {duration_str} total*\n\n")
        else:
            md_lines.append(f"*{len(entries)} sessions*\n\n")
        md_lines.append("---\n\n")
    
    # Each session entry
    for entry in entries:
        md_lines.append(f"### {entry['time_str']} — {entry['title']}\n\n")
        
        if entry['body']:
            md_lines.append(f"{entry['body']}\n\n")
        
        # Show additional prompts if interesting
        if entry['prompts']:
            for prompt in entry['prompts'][:2]:
                if len(prompt) > 20:
                    short = prompt[:100] + "..." if len(prompt) > 100 else prompt
                    md_lines.append(f"> {short}\n\n")
    
    if not entries:
        md_lines.append("*No significant activity recorded*\n\n")
    
    # Write file
    with open(journal_path, 'w', encoding='utf-8') as f:
        f.write(''.join(md_lines))
    
    return len(entries)

def convert_sessions_to_journals(session_ids: Set[str]):
    """
    Convert specified sessions to journal entries.
    Groups sessions by date, then updates each day's journal.
    """
    if not session_ids:
        logger.info("No new sessions to convert")
        return
    
    # Group sessions by date
    sessions_by_date: Dict[str, List] = defaultdict(list)
    
    for session_id in session_ids:
        jsonl_path = ARCHIVES_DEST / f"{session_id}.jsonl"
        if not jsonl_path.exists():
            continue
            
        timestamp, sid, messages = parse_session(jsonl_path)
        if timestamp and messages:
            date_key = timestamp.strftime('%Y-%m-%d')
            sessions_by_date[date_key].append((timestamp, sid, messages))
    
    # Update journals for each affected date
    for date_str in sorted(sessions_by_date.keys()):
        sessions = sessions_by_date[date_str]
        entry_count = update_journal_for_date(date_str, sessions)
        logger.info(f"  Journal {date_str}: {entry_count} entries")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("Claude Code: Sync + Convert")
    print("=" * 60)
    print(f"Platform: {get_platform_info()}")
    print(f"Archives: {ARCHIVES_DEST}")
    print(f"Journals: {JOURNALS_DEST}")
    print()
    
    # Step 1: Sync
    print("[1/2] Syncing raw logs...")
    newly_synced = sync_jsonl_logs()
    print(f"      Synced: {len(newly_synced)} new/updated sessions")
    print()
    
    # Step 2: Convert
    print("[2/2] Converting to journals...")
    convert_sessions_to_journals(newly_synced)
    print()
    
    print("=" * 60)
    print("Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
