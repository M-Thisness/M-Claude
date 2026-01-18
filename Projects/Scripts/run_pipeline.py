#!/usr/bin/env python3
"""
M-Claude Pipeline Runner

Orchestrates the full sync → index → journal pipeline.
Usage: python run_pipeline.py [--full]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import get_paths, setup_logging
from db import get_db
from pipeline import Indexer, JournalGenerator, SyncManager

logger = setup_logging(__name__)


def run_pipeline(full_reindex: bool = False):
    """Run the complete sync → index → journal pipeline."""
    paths = get_paths()

    # Database path
    db_path = paths.repo_root / ".m-claude" / "index.db"

    print("=" * 60)
    print("M-Claude Pipeline v2")
    print("=" * 60)
    print(f"Source: ~/.claude/projects/")
    print(f"Archives: {paths.archives}")
    print(f"Journals: {paths.journals}")
    print(f"Database: {db_path}")
    print()

    # Initialize database
    print("[1/4] Initializing database...")
    db = get_db(db_path)
    print(f"      Database ready (v2.0)")
    print()

    # Sync raw logs (with comprehensive email redaction)
    print("[2/4] Syncing raw logs...")
    sync_manager = SyncManager(
        source_base=paths.claude_projects_dir(),
        dest_dir=paths.archives,
        db=db
    )
    synced = sync_manager.sync_all()
    print(f"      Synced: {len(synced)} sessions (email content auto-redacted)")
    print()

    # Index sessions
    print("[3/4] Indexing sessions...")
    indexer = Indexer(db)
    if full_reindex:
        count = indexer.index_all(paths.archives)
        print(f"      Indexed: {count} sessions (full reindex)")
    else:
        # Index only synced sessions
        count = 0
        for session_id in synced:
            jsonl_path = paths.archives / f"{session_id}.jsonl"
            if jsonl_path.exists():
                if indexer.index_session(session_id, jsonl_path, jsonl_path):
                    count += 1
        print(f"      Indexed: {count} sessions (incremental)")
    print()

    # Generate journals
    print("[4/4] Generating journals...")
    journal_gen = JournalGenerator(db, paths.journals)
    if full_reindex:
        journal_count = journal_gen.generate_all()
        print(f"      Generated: {journal_count} journals (full)")
    else:
        journal_count = journal_gen.generate_dirty()
        print(f"      Generated: {journal_count} journals (dirty only)")
    print()

    # Summary
    print("=" * 60)
    print("✅ Complete! (all email content auto-redacted)")

    # Stats
    session_count = db.fetchone("SELECT COUNT(*) as c FROM sessions")
    message_count = db.fetchone("SELECT COUNT(*) as c FROM messages")
    print(f"\nDatabase stats:")
    print(f"  - Sessions: {session_count['c']}")
    print(f"  - Messages: {message_count['c']}")
    print("=" * 60)

    return 0


def main():
    parser = argparse.ArgumentParser(description="M-Claude Pipeline Runner")
    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Full reindex (ignore checksums)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    try:
        return run_pipeline(full_reindex=args.full)
    except KeyboardInterrupt:
        print("\nInterrupted")
        return 1
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
