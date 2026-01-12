#!/usr/bin/env python3
"""
Claude Code Raw Log Sync Script
Syncs conversation logs from ~/.claude to M-Claude repo with comprehensive redaction

Supported Platforms:
- Windows 11
- macOS
- Linux (CachyOS, Arch, Ubuntu, Debian)
- Android (Termux/Debian proot)
"""

import os
import re
import platform
import logging
from pathlib import Path
from datetime import datetime

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

def get_claude_project_dirs():
    """
    Detect Claude Code project directories based on platform.
    Claude Code stores conversations in ~/.claude/projects/<encoded-path>/
    """
    claude_base = HOME / ".claude" / "projects"
    project_dirs = []
    
    if not claude_base.exists():
        logger.warning(f"Claude base directory not found: {claude_base}")
        return project_dirs
    
    # Find all project directories dynamically
    try:
        for entry in claude_base.iterdir():
            if entry.is_dir():
                # Check if it contains .jsonl files
                jsonl_files = list(entry.glob("*.jsonl"))
                if jsonl_files:
                    project_dirs.append(entry)
                    logger.debug(f"Found project directory: {entry}")
    except PermissionError as e:
        logger.error(f"Permission denied accessing {claude_base}: {e}")
    
    # Platform-specific fallback paths if dynamic detection fails
    if not project_dirs:
        system = platform.system()
        
        if system == "Windows":
            # Windows uses C--Users-Username format
            fallback_dirs = [
                claude_base / f"C--Users-{HOME.name}",
                claude_base / "C--Windows-System32",
            ]
        elif system == "Darwin":  # macOS
            fallback_dirs = [
                claude_base / f"-Users-{HOME.name}",
            ]
        else:  # Linux, Android (Termux)
            # Check for Termux/Android
            is_android = os.path.exists("/data/data/com.termux")
            if is_android:
                fallback_dirs = [
                    claude_base / "-data-data-com.termux-files-home",
                    claude_base / f"-home-{HOME.name}",
                ]
            else:
                fallback_dirs = [
                    claude_base / f"-home-{HOME.name}",
                ]
        
        for d in fallback_dirs:
            if d.exists():
                project_dirs.append(d)
    
    return project_dirs

# Build backslash strings using chr() to avoid escape issues
BS = chr(92)  # backslash character

# Comprehensive secret and PII patterns
SECRET_PATTERNS = [
    # API Keys & Tokens
    (r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]"),
    (r"(ghp_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]"),
    (r"(gho_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]"),
    (r"(xox[baprs]-[a-zA-Z0-9]{10,})", "[REDACTED_SLACK_TOKEN]"),
    (r"(AKIA[0-9A-Z]{16})", "[REDACTED_AWS_KEY]"),
    (r"(ya29\.[a-zA-Z0-9_-]{50,})", "[REDACTED_GOOGLE_TOKEN]"),

    # Private Keys
    (r"(-----BEGIN [A-Z]+ PRIVATE KEY-----[^-]+-----END [A-Z]+ PRIVATE KEY-----)", "[REDACTED_PRIVATE_KEY]"),
    (r"(-----BEGIN RSA PRIVATE KEY-----)", "[REDACTED_RSA_KEY_HEADER]"),

    # Email addresses (PII)
    (r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", "[REDACTED_EMAIL]"),

    # Phone numbers (PII) - avoid matching timestamps/UUIDs
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

    # File paths that might contain usernames (forward slashes)
    (r"(/home/[a-zA-Z0-9_-]+)", "/home/[USER]"),
    (r"(/Users/[a-zA-Z0-9_-]+)", "/Users/[USER]"),
    (r"(C:/Users/[a-zA-Z0-9_-]+)", "C:/Users/[USER]"),
    
    # Android/Termux paths
    (r"(/data/data/com\.termux/files/home)", "[TERMUX_HOME]"),
]

# Windows backslash path pattern
WIN_PATH_PATTERN = f'C:{BS}{BS}Users{BS}{BS}[a-zA-Z0-9_-]+'
WIN_PATH_REPLACEMENT = f'C:{BS}Users{BS}[USER]'

def redact_text(text):
    """Apply all redaction patterns to text."""
    if not isinstance(text, str):
        return text

    for pattern, replacement in SECRET_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Handle Windows backslash paths
    text = re.sub(WIN_PATH_PATTERN, lambda m: WIN_PATH_REPLACEMENT, text, flags=re.IGNORECASE)

    return text

def sync_jsonl_logs():
    """Sync and redact .jsonl conversation logs."""
    os.makedirs(ARCHIVES_DEST, exist_ok=True)

    project_dirs = get_claude_project_dirs()
    
    if not project_dirs:
        logger.error("No Claude Code project directories found!")
        logger.info(f"Expected location: {HOME / '.claude' / 'projects'}")
        return 0, 0

    total_updated = 0
    total_skipped = 0

    for claude_projects in project_dirs:
        jsonl_files = list(claude_projects.glob("*.jsonl"))
        logger.info(f"Found {len(jsonl_files)} logs in {claude_projects.name}")

        for src_file in jsonl_files:
            dest_file = ARCHIVES_DEST / src_file.name

            try:
                # Read and redact
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
                            total_skipped += 1
                    except Exception:
                        pass

                if should_write:
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(redacted_content)
                    total_updated += 1

            except Exception as e:
                logger.error(f"Error processing {src_file.name}: {e}")

    return total_updated, total_skipped

def get_platform_info():
    """Get detailed platform information."""
    system = platform.system()
    
    # Check for Android/Termux
    if os.path.exists("/data/data/com.termux"):
        return "Android (Termux)"
    
    if system == "Darwin":
        return f"macOS {platform.mac_ver()[0]}"
    elif system == "Windows":
        return f"Windows {platform.release()}"
    elif system == "Linux":
        # Try to get distro info
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=")[1].strip().strip('"')
        except FileNotFoundError:
            pass
        return f"Linux {platform.release()}"
    
    return system

def main():
    print("=" * 60)
    print("Claude Code Raw Log Sync")
    print("=" * 60)
    
    platform_info = get_platform_info()
    print(f"Platform: {platform_info}")
    
    project_dirs = get_claude_project_dirs()
    print(f"Source directories:")
    if project_dirs:
        for d in project_dirs:
            print(f"  [OK] {d}")
    else:
        print(f"  [--] No directories found in {HOME / '.claude' / 'projects'}")
    
    print(f"Destination: {ARCHIVES_DEST}")
    print()

    updated, skipped = sync_jsonl_logs()

    print()
    print("=" * 60)
    print(f"Sync complete! Updated: {updated}, Skipped: {skipped}")
    print("=" * 60)

if __name__ == "__main__":
    main()
