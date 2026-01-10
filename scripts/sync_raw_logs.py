#!/usr/bin/env python3
"""
Claude Code Raw Log Sync Script
Syncs conversation logs from ~/.claude to M-Claude repo with comprehensive redaction
Supports both Linux (CachyOS) and Windows platforms
"""

import os
import shutil
import json
import re
import platform
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
HOME = Path.home()
REPO_ROOT = Path(__file__).parent.parent
TRANSCRIPTS_DEST = REPO_ROOT / "CHAT_LOGS"

# Platform-specific source directories
if platform.system() == "Windows":
    # Windows: multiple project directories with encoded paths
    CLAUDE_PROJECT_DIRS = [
        HOME / ".claude/projects/C--Users-Mischa",
        HOME / ".claude/projects/C--Windows-System32",
    ]
else:
    # Linux/CachyOS
    CLAUDE_PROJECT_DIRS = [
        HOME / ".claude/projects/-home-mischa",
    ]

# Build backslash strings using chr() to avoid escape issues
BS = chr(92)  # backslash character

# Comprehensive secret and PII patterns
SECRET_PATTERNS = [
    # API Keys & Tokens
    (r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]"),
    (r"(ghp_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]"),
    (r"(xox[baprs]-[a-zA-Z0-9]{10,})", "[REDACTED_SLACK_TOKEN]"),
    (r"(AKIA[0-9A-Z]{16})", "[REDACTED_AWS_KEY]"),
    (r"(ya29\.[a-zA-Z0-9_-]{50,})", "[REDACTED_GOOGLE_TOKEN]"),

    # Private Keys
    (r"(-----BEGIN [A-Z]+ PRIVATE KEY-----[^-]+-----END [A-Z]+ PRIVATE KEY-----)", "[REDACTED_PRIVATE_KEY]"),
    (r"(-----BEGIN RSA PRIVATE KEY-----)", "[REDACTED_RSA_KEY_HEADER]"),

    # Email addresses (PII)
    (r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", "[REDACTED_EMAIL]"),

    # Phone numbers (PII) - but NOT ISO timestamps or UUIDs
    # Negative lookbehind: not after timestamp or UUID segment
    # Negative lookahead: not before timestamp continuation or UUID segment
    (r"(?<!\d{4}-\d{2}-\d{2}T\d{2}:)(?<![-a-f0-9]{4}-)(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})(?!:\d{2})(?!-[a-f0-9]{4})", "[REDACTED_PHONE]"),

    # Credit card numbers (PII)
    (r"(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})", "[REDACTED_CARD]"),

    # SSN-like patterns (PII)
    (r"(\d{3}-\d{2}-\d{4})", "[REDACTED_SSN]"),

    # IP Addresses (potentially sensitive)
    (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", "[REDACTED_IP]"),

    # JWT tokens
    (r"(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})", "[REDACTED_JWT]"),

    # Generic secrets (password=, token=, etc.)
    (r"(password\s*[:=]\s*['\"]?[^\s'\"]{8,}['\"]?)", "password=[REDACTED]"),
    (r"(token\s*[:=]\s*['\"]?[^\s'\"]{20,}['\"]?)", "token=[REDACTED]"),
    (r"(secret\s*[:=]\s*['\"]?[^\s'\"]{20,}['\"]?)", "secret=[REDACTED]"),
    (r"(api_key\s*[:=]\s*['\"]?[^\s'\"]{20,}['\"]?)", "api_key=[REDACTED]"),

    # Database connection strings
    (r"(postgres://[^\s]+)", "[REDACTED_DB_CONNECTION]"),
    (r"(mysql://[^\s]+)", "[REDACTED_DB_CONNECTION]"),
    (r"(mongodb://[^\s]+)", "[REDACTED_DB_CONNECTION]"),

    # File paths that might contain usernames
    (r"(/home/[a-zA-Z0-9_-]+)", "/home/[USER]"),
    (r"(/Users/[a-zA-Z0-9_-]+)", "/Users/[USER]"),
    # Windows paths with usernames (forward slashes)
    (r"(C:/Users/[a-zA-Z0-9_-]+)", "C:/Users/[USER]"),
]

# Windows backslash path pattern (built with chr() to avoid escape issues)
WIN_PATH_PATTERN = f'C:{BS}{BS}Users{BS}{BS}[a-zA-Z0-9_-]+'
WIN_PATH_REPLACEMENT = f'C:{BS}Users{BS}[USER]'

def redact_text(text):
    """Apply all redaction patterns to text."""
    if not isinstance(text, str):
        return text

    for pattern, replacement in SECRET_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Handle Windows backslash paths using lambda to avoid escape issues
    text = re.sub(WIN_PATH_PATTERN, lambda m: WIN_PATH_REPLACEMENT, text, flags=re.IGNORECASE)

    return text

def sync_jsonl_logs():
    """Sync and redact .jsonl conversation logs using text-based redaction."""
    os.makedirs(TRANSCRIPTS_DEST, exist_ok=True)

    total_synced = 0
    total_updated = 0
    total_skipped = 0

    for claude_projects in CLAUDE_PROJECT_DIRS:
        if not claude_projects.exists():
            logger.info(f"Skipping (not found): {claude_projects}")
            continue

        jsonl_files = list(claude_projects.glob("*.jsonl"))
        logger.info(f"Found {len(jsonl_files)} conversation logs in {claude_projects}")

        synced_count = 0
        updated_count = 0
        skipped_count = 0

        for src_file in jsonl_files:
            dest_file = TRANSCRIPTS_DEST / src_file.name

            try:
                # Read entire file as text and apply redaction
                with open(src_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                # Apply redaction
                redacted_content = redact_text(content)

                # Check if we need to update
                should_write = True
                if dest_file.exists():
                    try:
                        with open(dest_file, 'r', encoding='utf-8', errors='replace') as f:
                            existing_content = f.read()
                        if existing_content == redacted_content:
                            should_write = False
                            skipped_count += 1
                    except:
                        pass

                if should_write:
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(redacted_content)

                    if os.path.getsize(dest_file) > 0:
                        try:
                            src_size = os.path.getsize(src_file)
                            if abs(src_size - os.path.getsize(dest_file)) > 100:
                                updated_count += 1
                            else:
                                synced_count += 1
                        except:
                            synced_count += 1

            except Exception as e:
                logger.error(f"Error processing {src_file.name}: {e}")

        logger.info(f"  Synced: {synced_count}, Updated: {updated_count}, Skipped: {skipped_count}")
        total_synced += synced_count
        total_updated += updated_count
        total_skipped += skipped_count

    logger.info(f"\nTotal: Synced/updated {total_synced + total_updated} files, skipped {total_skipped} unchanged files")

def update_readme():
    """Update README with sync timestamp."""
    readme_path = TRANSCRIPTS_DEST / "README.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system = platform.system()

    content = f"""# Claude Code Raw Conversation Logs

This directory contains redacted raw conversation logs from Claude Code sessions.

**Last Sync:** {timestamp}
**Platform:** {system}

## Format
- Files are in JSONL format (one JSON object per line)
- Each line represents a conversation event (user message, assistant response, tool use, etc.)
- All sensitive data is automatically redacted before syncing

## Redacted Information
The sync script automatically redacts:
- API keys and authentication tokens
- Email addresses
- Phone numbers
- IP addresses
- Private keys
- Database connection strings
- File paths containing usernames
- Other PII and secrets

## Syncing
To sync the latest logs:
```bash
python scripts/sync_raw_logs.py
```
"""

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("=" * 60)
    print("Claude Code Raw Log Sync")
    print("=" * 60)
    print(f"Platform: {platform.system()}")
    print(f"Source directories:")
    for d in CLAUDE_PROJECT_DIRS:
        exists = "[OK]" if d.exists() else "[--]"
        print(f"  {exists} {d}")
    print(f"Destination: {TRANSCRIPTS_DEST}")
    print()

    sync_jsonl_logs()
    update_readme()

    print()
    print("=" * 60)
    print("Sync complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
