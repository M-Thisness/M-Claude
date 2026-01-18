#!/usr/bin/env python3
"""
M-Claude Indexer

Indexes JSONL files into SQLite with FTS5 full-text search.
Extracts messages, tool calls, and auto-detects tags.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from .extractor import (
    extract_message_content,
    extract_session_metadata,
    extract_tool_calls,
    iter_jsonl,
)
from .sync import compute_checksum

logger = logging.getLogger(__name__)

# Tag detection patterns
TAG_KEYWORDS = {
    "git": ["git ", "commit", "branch", "merge", "rebase", "push", "pull", ".git"],
    "docker": ["docker", "container", "dockerfile", "compose", "kubernetes", "k8s"],
    "security": ["security", "vulnerability", "credential", "password", "secret", "auth", "ssl", "tls"],
    "debugging": ["debug", "error", "traceback", "exception", "fix", "bug", "issue"],
    "testing": ["test", "pytest", "unittest", "coverage", "assert", "mock", "spec"],
    "documentation": ["readme", "docs", "documentation", "comment", "docstring", "markdown"],
    "refactoring": ["refactor", "cleanup", "reorganize", "rename", "restructure"],
    "ssh": ["ssh", "remote", "scp", "sftp", "rsync"],
    "database": ["sql", "database", "query", "postgres", "mysql", "sqlite", "mongodb"],
    "api": ["api", "endpoint", "request", "response", "http", "rest", "graphql"],
    "frontend": ["css", "html", "react", "component", "style", "ui", "tailwind"],
    "config": ["config", "settings", "environment", ".env", "yaml", "toml"],
    "python": ["python", "pip", "venv", "pytest", ".py"],
    "javascript": ["javascript", "npm", "node", "typescript", ".js", ".ts"],
    "rust": ["rust", "cargo", "rustc", ".rs"],
}


def detect_tags(text: str) -> List[tuple]:
    """
    Detect tags from text content.

    Returns list of (tag, confidence) tuples.
    """
    if not text:
        return []

    text_lower = text.lower()
    detected = []

    for tag, keywords in TAG_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)
        if matches > 0:
            # Confidence based on number of keyword matches
            confidence = min(1.0, matches * 0.3)
            detected.append((tag, confidence))

    return detected


class Indexer:
    """Indexes sessions into SQLite database."""

    def __init__(self, db):
        self.db = db

    def index_session(
        self,
        session_id: str,
        jsonl_path: Path,
        archive_path: Optional[Path] = None
    ) -> bool:
        """
        Parse and index a session into the database.

        Returns True on success.
        """
        try:
            # Load all messages
            messages = list(iter_jsonl(jsonl_path))
            if not messages:
                logger.warning(f"No messages in {session_id}")
                return False

            # Extract metadata
            metadata = extract_session_metadata(messages)
            checksum = compute_checksum(jsonl_path)
            now = datetime.now().isoformat()

            with self.db.transaction() as cursor:
                # Delete existing data for this session
                cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

                # Insert session
                cursor.execute("""
                    INSERT INTO sessions (
                        id, file_path, archive_path, checksum, file_size,
                        first_timestamp, last_timestamp, message_count,
                        duration_ms, title, cwd, git_branch, platform,
                        claude_version, has_email_content, indexed_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    str(jsonl_path),
                    str(archive_path) if archive_path else None,
                    checksum,
                    jsonl_path.stat().st_size,
                    metadata['first_timestamp'],
                    metadata['last_timestamp'],
                    len(messages),
                    metadata['duration_ms'],
                    metadata['title'],
                    metadata['cwd'],
                    metadata['git_branch'],
                    metadata['platform'],
                    metadata['claude_version'],
                    0,  # has_email_content
                    now,
                    now,
                ))

                # Collect all text for tag detection
                all_text = []

                # Index messages
                for msg in messages:
                    msg_type = msg.get('type', 'unknown')

                    # Skip file-history and other meta types
                    if msg_type in ('file-history-snapshot',):
                        continue

                    content = extract_message_content(msg)
                    all_text.append(content.text)

                    cursor.execute("""
                        INSERT INTO messages (
                            session_id, uuid, parent_uuid, timestamp, type,
                            role, content_text, content_raw, thinking_text,
                            has_tool_use, tool_count
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        session_id,
                        msg.get('uuid'),
                        msg.get('parentUuid'),
                        msg.get('timestamp', now),
                        msg_type,
                        msg.get('message', {}).get('role'),
                        content.text[:10000] if content.text else None,  # Limit size
                        json.dumps(msg) if msg_type in ('user', 'assistant') else None,
                        content.thinking[:5000] if content.thinking else None,
                        1 if content.has_tool_use else 0,
                        len(content.tool_uses),
                    ))
                    message_id = cursor.lastrowid

                    # Index tool calls
                    for tc in extract_tool_calls(msg):
                        cursor.execute("""
                            INSERT INTO tool_calls (
                                message_id, session_id, tool_id, tool_name,
                                input_json, file_path, command, description,
                                outcome, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            message_id,
                            session_id,
                            tc.tool_id,
                            tc.tool_name,
                            tc.input_json,
                            tc.file_path,
                            tc.command,
                            tc.description,
                            'unknown',
                            now,
                        ))

                # Detect and insert tags
                combined_text = '\n'.join(all_text)
                tags = detect_tags(combined_text)
                for tag, confidence in tags:
                    cursor.execute("""
                        INSERT OR IGNORE INTO tags (session_id, tag, confidence, source, created_at)
                        VALUES (?, ?, ?, 'auto', ?)
                    """, (session_id, tag, confidence, now))

                # Mark affected journal dates as dirty
                if metadata['first_timestamp']:
                    date = metadata['first_timestamp'][:10]  # YYYY-MM-DD
                    cursor.execute("""
                        INSERT INTO journal_cache (date, markdown, session_ids, generated_at, dirty)
                        VALUES (?, '', '[]', ?, 1)
                        ON CONFLICT(date) DO UPDATE SET dirty = 1
                    """, (date, now))

            logger.info(f"Indexed {session_id}: {len(messages)} messages, {len(tags)} tags")
            return True

        except Exception as e:
            logger.error(f"Failed to index {session_id}: {e}")
            return False

    def index_all(self, archives_dir: Path) -> int:
        """Index all JSONL files in archives directory."""
        count = 0
        for jsonl_path in archives_dir.glob("*.jsonl"):
            session_id = jsonl_path.stem
            if self.index_session(session_id, jsonl_path, jsonl_path):
                count += 1
        return count

    def reindex_dirty(self, archives_dir: Path) -> int:
        """Reindex only sessions that need updating."""
        # For now, just index all - incremental will check checksums
        return self.index_all(archives_dir)
