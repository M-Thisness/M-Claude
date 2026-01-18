#!/usr/bin/env python3
"""
M-Claude Database Module

Provides SQLite-based indexing with FTS5 full-text search.
"""

from .connection import ConnectionManager, DatabaseError, get_db
from .models import (
    JournalCache,
    Message,
    SearchResult,
    Session,
    Tag,
    ToolCall,
    format_timestamp,
    parse_timestamp,
)
from .schema import SCHEMA_VERSION, get_schema_sql, get_tag_patterns

__all__ = [
    # Connection
    "ConnectionManager",
    "DatabaseError",
    "get_db",
    # Models
    "Session",
    "Message",
    "ToolCall",
    "Tag",
    "JournalCache",
    "SearchResult",
    # Utilities
    "parse_timestamp",
    "format_timestamp",
    # Schema
    "SCHEMA_VERSION",
    "get_schema_sql",
    "get_tag_patterns",
]
