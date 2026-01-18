#!/usr/bin/env python3
"""
M-Claude Pipeline Module

Modular processing pipeline for sync, indexing, and journal generation.
"""

from .redactor import Redactor, detect_gmail_content, get_redactor, redact
from .extractor import (
    ExtractedContent,
    ExtractedToolCall,
    extract_message_content,
    extract_session_metadata,
    extract_tool_calls,
    iter_jsonl,
)
from .sync import SyncManager, compute_checksum, sync_file_streaming
from .indexer import Indexer, detect_tags
from .journal import JournalGenerator, format_duration

__all__ = [
    # Redactor
    "Redactor",
    "get_redactor",
    "redact",
    "detect_gmail_content",
    # Extractor
    "ExtractedContent",
    "ExtractedToolCall",
    "extract_message_content",
    "extract_session_metadata",
    "extract_tool_calls",
    "iter_jsonl",
    # Sync
    "SyncManager",
    "compute_checksum",
    "sync_file_streaming",
    # Indexer
    "Indexer",
    "detect_tags",
    # Journal
    "JournalGenerator",
    "format_duration",
]
