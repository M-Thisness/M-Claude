#!/usr/bin/env python3
"""
M-Claude Database Schema

SQLite schema definitions with FTS5 full-text search support.
Supports incremental sync via checksums and dirty flags.
"""

from __future__ import annotations

SCHEMA_VERSION = "2.0.0"

# Core schema SQL statements
SCHEMA_SQL = """
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_info (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Sessions with checksums for incremental sync
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,                    -- UUID from JSONL filename
    file_path TEXT NOT NULL UNIQUE,         -- Absolute path to source JSONL
    archive_path TEXT,                      -- Path in Archives/
    checksum TEXT NOT NULL,                 -- SHA256 for change detection
    file_size INTEGER NOT NULL,
    first_timestamp TEXT,                   -- ISO8601
    last_timestamp TEXT,                    -- ISO8601
    message_count INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    title TEXT,                             -- Session title/summary
    cwd TEXT,                               -- Working directory
    git_branch TEXT,
    platform TEXT,                          -- windows/macos/linux/termux
    claude_version TEXT,                    -- Claude Code version
    has_email_content INTEGER DEFAULT 0,    -- Flag for manual review
    indexed_at TEXT NOT NULL,               -- When last processed
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_timestamp ON sessions(first_timestamp);
CREATE INDEX IF NOT EXISTS idx_sessions_checksum ON sessions(checksum);

-- Structured message storage
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    uuid TEXT,                              -- Message UUID from JSONL
    parent_uuid TEXT,                       -- For threading
    timestamp TEXT NOT NULL,
    type TEXT NOT NULL,                     -- user/assistant/system/summary
    role TEXT,                              -- user/assistant
    content_text TEXT,                      -- Extracted plaintext
    content_raw TEXT,                       -- Original JSON (compressed)
    thinking_text TEXT,                     -- Extended thinking content
    has_tool_use INTEGER DEFAULT 0,
    tool_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(type);

-- FTS5 virtual table for full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    session_id,
    content,
    role,
    content='messages',
    content_rowid='id',
    tokenize='porter unicode61'
);

-- Triggers to keep FTS5 in sync
CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, session_id, content, role)
    VALUES (new.id, new.session_id, new.content_text, new.role);
END;

CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, session_id, content, role)
    VALUES ('delete', old.id, old.session_id, old.content_text, old.role);
END;

CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, session_id, content, role)
    VALUES ('delete', old.id, old.session_id, old.content_text, old.role);
    INSERT INTO messages_fts(rowid, session_id, content, role)
    VALUES (new.id, new.session_id, new.content_text, new.role);
END;

-- Tool calls with outcomes
CREATE TABLE IF NOT EXISTS tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    tool_id TEXT,                           -- Tool use ID from API
    tool_name TEXT NOT NULL,
    input_json TEXT,                        -- Full input as JSON
    file_path TEXT,                         -- Extracted from Read/Write/Edit
    command TEXT,                           -- Extracted from Bash
    description TEXT,                       -- Human-readable description
    outcome TEXT DEFAULT 'unknown',         -- success/error/unknown
    output_preview TEXT,                    -- First 500 chars of output
    duration_ms INTEGER,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tool_calls_session ON tool_calls(session_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_tool ON tool_calls(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_calls_outcome ON tool_calls(outcome);

-- Auto-detected tags/categories
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,                      -- e.g., "git", "docker", "debugging"
    confidence REAL DEFAULT 1.0,
    source TEXT DEFAULT 'auto',             -- auto/manual
    created_at TEXT NOT NULL,
    UNIQUE(session_id, tag)
);

CREATE INDEX IF NOT EXISTS idx_tags_session ON tags(session_id);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);

-- Journal cache for incremental generation
CREATE TABLE IF NOT EXISTS journal_cache (
    date TEXT PRIMARY KEY,                  -- YYYY-MM-DD
    markdown TEXT NOT NULL,
    session_ids TEXT NOT NULL,              -- JSON array of session IDs
    generated_at TEXT NOT NULL,
    dirty INTEGER DEFAULT 0                 -- Needs regeneration
);

CREATE INDEX IF NOT EXISTS idx_journal_dirty ON journal_cache(dirty);

-- Sync state for incremental processing
CREATE TABLE IF NOT EXISTS sync_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

# Tag detection patterns (tag -> list of keywords/patterns)
TAG_PATTERNS = {
    "git": ["git ", "commit", "branch", "merge", "rebase", "push", "pull"],
    "docker": ["docker", "container", "dockerfile", "compose"],
    "security": ["security", "vulnerability", "credential", "password", "secret", "auth"],
    "debugging": ["debug", "error", "traceback", "exception", "fix", "bug"],
    "testing": ["test", "pytest", "unittest", "coverage", "assert"],
    "documentation": ["readme", "docs", "documentation", "comment", "docstring"],
    "refactoring": ["refactor", "cleanup", "reorganize", "rename"],
    "ssh": ["ssh", "remote", "scp", "sftp"],
    "database": ["sql", "database", "query", "postgres", "mysql", "sqlite"],
    "api": ["api", "endpoint", "request", "response", "http", "rest"],
    "frontend": ["css", "html", "react", "component", "style", "ui"],
    "config": ["config", "settings", "environment", ".env", "yaml", "json"],
}


def get_schema_sql() -> str:
    """Return the full schema SQL."""
    return SCHEMA_SQL


def get_tag_patterns() -> dict:
    """Return tag detection patterns."""
    return TAG_PATTERNS.copy()
