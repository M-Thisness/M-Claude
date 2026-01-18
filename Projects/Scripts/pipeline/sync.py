#!/usr/bin/env python3
"""
M-Claude Incremental Sync

Checksum-based incremental sync with streaming redaction.
Only processes files that have changed since last sync.
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional, Set, Tuple

from .redactor import detect_gmail_content, get_redactor

logger = logging.getLogger(__name__)


def compute_checksum(path: Path, chunk_size: int = 65536) -> str:
    """Compute SHA256 checksum without loading full file into memory."""
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def sync_file_streaming(
    src_path: Path,
    dest_path: Path,
    redactor=None
) -> bool:
    """
    Sync a single file with streaming redaction.

    Returns: success
    """
    if redactor is None:
        redactor = get_redactor()

    temp_path = dest_path.with_suffix('.tmp')

    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(src_path, 'r', encoding='utf-8', errors='replace') as src:
            with open(temp_path, 'w', encoding='utf-8') as dst:
                for line in src:
                    # Apply comprehensive redaction (including all email content)
                    redacted_line = redactor.redact(line)
                    dst.write(redacted_line)

        # Atomic rename
        os.replace(temp_path, dest_path)
        return True

    except Exception as e:
        logger.error(f"Failed to sync {src_path}: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False


def discover_jsonl_files(base_path: Path) -> Iterator[Path]:
    """Discover all JSONL files in Claude projects directory."""
    if not base_path.exists():
        return

    for project_dir in base_path.iterdir():
        if project_dir.is_dir():
            for jsonl_file in project_dir.glob("*.jsonl"):
                yield jsonl_file


class SyncManager:
    """Manages incremental sync of conversation logs."""

    def __init__(
        self,
        source_base: Path,
        dest_dir: Path,
        db=None
    ):
        self.source_base = source_base
        self.dest_dir = dest_dir
        self.db = db
        self.redactor = get_redactor()

    def get_session_checksum(self, session_id: str) -> Optional[str]:
        """Get stored checksum for a session."""
        if self.db is None:
            return None
        row = self.db.fetchone(
            "SELECT checksum FROM sessions WHERE id = ?",
            (session_id,)
        )
        return row["checksum"] if row else None

    def should_sync(self, src_path: Path) -> bool:
        """Check if file needs syncing based on checksum."""
        session_id = src_path.stem
        dest_path = self.dest_dir / src_path.name

        # Always sync if dest doesn't exist
        if not dest_path.exists():
            return True

        # Check checksum if we have DB
        stored_checksum = self.get_session_checksum(session_id)
        if stored_checksum:
            current_checksum = compute_checksum(src_path)
            return current_checksum != stored_checksum

        # Fallback: compare file sizes
        return src_path.stat().st_size != dest_path.stat().st_size

    def sync_all(self) -> Set[str]:
        """
        Sync all JSONL files with comprehensive redaction.

        Returns: synced_session_ids
        """
        synced: Set[str] = set()

        self.dest_dir.mkdir(parents=True, exist_ok=True)

        for src_path in discover_jsonl_files(self.source_base):
            session_id = src_path.stem

            if not self.should_sync(src_path):
                logger.debug(f"Skipping {session_id} (unchanged)")
                continue

            dest_path = self.dest_dir / src_path.name
            logger.info(f"Syncing {session_id}")

            success = sync_file_streaming(src_path, dest_path, self.redactor)

            if success:
                synced.add(session_id)

        return synced
