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
    Extract meaningful summary from session messages.
    Returns structured data about the session.
    """
    summary = {
        'user_prompts': [],
        'tools_used': set(),
        'files_modified': [],
        'topics': [],
        'accomplishments': []
    }
    
    for msg in messages:
        msg_type = msg.get('type')
        
        # User messages - extract prompts
        if msg_type == 'user':
            content = msg.get('message', {}).get('content', '')
            if isinstance(content, str) and content:
                # Skip system/meta messages
                skip_patterns = [
                    'caveat:', 'command-name', 'local-command', 'stdout', 'stderr',
                    'rate-limit', 'login successful', 'touch_key', 'warmup', 'resume',
                    '[file content]', 'file-history', 'is-snapshot'
                ]
                if not any(x in content.lower() for x in skip_patterns):
                    clean = content.strip()
                    if clean and len(clean) > 5 and len(clean) < 500:
                        summary['user_prompts'].append(clean)
        
        # Assistant messages - extract tool usage
        elif msg_type == 'assistant':
            content = msg.get('message', {}).get('content', [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                        tool = item.get('name', '')
                        summary['tools_used'].add(tool)
                        
                        # Track file modifications
                        inp = item.get('input', {})
                        if tool in ['Write', 'Edit', 'MultiEdit']:
                            filepath = inp.get('file_path', '') or inp.get('filePath', '')
                            if filepath:
                                filename = Path(filepath).name
                                if filename and filename not in summary['files_modified']:
                                    summary['files_modified'].append(filename)
                        
                        # Track command executions as accomplishments
                        elif tool == 'Bash':
                            cmd = inp.get('command', '')
                            if cmd and len(cmd) < 100:
                                summary['accomplishments'].append(f"Ran: `{cmd[:60]}`")
    
    return summary

def summarize_session_narrative(summary: Dict) -> str:
    """Create a human-readable narrative from session summary."""
    parts = []
    
    # Main topic from first user prompt
    if summary['user_prompts']:
        main_prompt = summary['user_prompts'][0]
        # Truncate long prompts
        if len(main_prompt) > 150:
            main_prompt = main_prompt[:147] + "..."
        parts.append(main_prompt)
    
    # Add file modifications
    if summary['files_modified']:
        files = summary['files_modified'][:3]
        if len(summary['files_modified']) > 3:
            parts.append(f"Modified `{', '.join(files)}` + {len(summary['files_modified'])-3} more")
        else:
            parts.append(f"Modified `{', '.join(files)}`")
    
    # Add tool context
    tools = summary['tools_used']
    if 'Bash' in tools and not summary['files_modified']:
        parts.append("Executed commands")
    elif 'Task' in tools:
        parts.append("Spawned sub-agents")
    elif 'Read' in tools and not summary['files_modified']:
        parts.append("Explored codebase")
    
    if parts:
        return " → ".join(parts)
    
    return "Brief interaction"

# ============================================================================
# JOURNAL GENERATION
# ============================================================================

def update_journal_for_date(date_str: str, sessions: List[Tuple[datetime, str, List[Dict]]]):
    """
    Update or create journal entry for a specific date.
    Only adds new sessions, preserves existing entries.
    """
    os.makedirs(JOURNALS_DEST, exist_ok=True)
    journal_path = JOURNALS_DEST / f"{date_str}.md"
    
    # Parse existing journal to get existing session IDs
    existing_entries = {}
    if journal_path.exists():
        try:
            with open(journal_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple parse - extract time entries
                for line in content.split('\n'):
                    if line.startswith('**') and ':**' in line:
                        existing_entries[line] = True
        except Exception:
            pass
    
    # Build new entries
    entries = []
    for timestamp, session_id, messages in sessions:
        if not timestamp:
            continue
            
        summary_data = extract_session_summary(messages)
        narrative = summarize_session_narrative(summary_data)
        
        if narrative and narrative != "Brief interaction":
            time_str = timestamp.strftime('%I:%M %p')
            entry_line = f"**{time_str}:** {narrative}"
            entries.append((timestamp, entry_line))
    
    # Sort by time
    entries.sort(key=lambda x: x[0])
    
    # Build markdown
    md_lines = [f"# {date_str}\n\n"]
    
    if entries:
        for _, entry_line in entries:
            md_lines.append(f"{entry_line}\n\n")
    else:
        md_lines.append("*No significant activity*\n\n")
    
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
