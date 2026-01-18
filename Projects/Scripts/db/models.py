#!/usr/bin/env python3
"""
M-Claude Data Models

Dataclasses for database records with conversion utilities.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import sqlite3


def parse_timestamp(ts: str | None) -> Optional[datetime]:
    """Parse ISO8601 timestamp string to datetime."""
    if not ts:
        return None
    try:
        # Handle Z suffix
        ts = ts.replace('Z', '+00:00')
        return datetime.fromisoformat(ts)
    except (ValueError, AttributeError):
        return None


def format_timestamp(dt: datetime | None) -> Optional[str]:
    """Format datetime to ISO8601 string."""
    if not dt:
        return None
    return dt.isoformat()


@dataclass
class Session:
    """Represents a Claude Code conversation session."""

    id: str
    file_path: str
    checksum: str
    file_size: int
    indexed_at: str
    created_at: str
    archive_path: Optional[str] = None
    first_timestamp: Optional[str] = None
    last_timestamp: Optional[str] = None
    message_count: int = 0
    duration_ms: int = 0
    title: Optional[str] = None
    cwd: Optional[str] = None
    git_branch: Optional[str] = None
    platform: Optional[str] = None
    claude_version: Optional[str] = None
    has_email_content: bool = False

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Session:
        """Create Session from database row."""
        return cls(
            id=row["id"],
            file_path=row["file_path"],
            archive_path=row["archive_path"],
            checksum=row["checksum"],
            file_size=row["file_size"],
            first_timestamp=row["first_timestamp"],
            last_timestamp=row["last_timestamp"],
            message_count=row["message_count"],
            duration_ms=row["duration_ms"],
            title=row["title"],
            cwd=row["cwd"],
            git_branch=row["git_branch"],
            platform=row["platform"],
            claude_version=row["claude_version"],
            has_email_content=bool(row["has_email_content"]),
            indexed_at=row["indexed_at"],
            created_at=row["created_at"],
        )

    @property
    def first_datetime(self) -> Optional[datetime]:
        """Get first_timestamp as datetime."""
        return parse_timestamp(self.first_timestamp)

    @property
    def duration_str(self) -> str:
        """Human-readable duration."""
        if self.duration_ms <= 0:
            return ""
        sec = self.duration_ms / 1000
        if sec > 3600:
            return f"{sec / 3600:.1f}h"
        elif sec > 60:
            return f"{sec / 60:.0f}m"
        return f"{sec:.0f}s"


@dataclass
class Message:
    """Represents a conversation message."""

    id: int
    session_id: str
    timestamp: str
    type: str  # user/assistant/system/summary
    uuid: Optional[str] = None
    parent_uuid: Optional[str] = None
    role: Optional[str] = None
    content_text: Optional[str] = None
    content_raw: Optional[str] = None
    thinking_text: Optional[str] = None
    has_tool_use: bool = False
    tool_count: int = 0

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Message:
        """Create Message from database row."""
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            uuid=row["uuid"],
            parent_uuid=row["parent_uuid"],
            timestamp=row["timestamp"],
            type=row["type"],
            role=row["role"],
            content_text=row["content_text"],
            content_raw=row["content_raw"],
            thinking_text=row["thinking_text"],
            has_tool_use=bool(row["has_tool_use"]),
            tool_count=row["tool_count"],
        )

    @property
    def datetime(self) -> Optional[datetime]:
        """Get timestamp as datetime."""
        return parse_timestamp(self.timestamp)

    @property
    def content_preview(self) -> str:
        """Get first 200 chars of content."""
        if not self.content_text:
            return ""
        text = self.content_text[:200]
        if len(self.content_text) > 200:
            text += "..."
        return text

    def get_raw_content(self) -> Any:
        """Parse and return raw JSON content."""
        if not self.content_raw:
            return None
        try:
            return json.loads(self.content_raw)
        except json.JSONDecodeError:
            return None


@dataclass
class ToolCall:
    """Represents a tool invocation."""

    id: int
    message_id: int
    session_id: str
    tool_name: str
    created_at: str
    tool_id: Optional[str] = None
    input_json: Optional[str] = None
    file_path: Optional[str] = None
    command: Optional[str] = None
    description: Optional[str] = None
    outcome: str = "unknown"  # success/error/unknown
    output_preview: Optional[str] = None
    duration_ms: Optional[int] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> ToolCall:
        """Create ToolCall from database row."""
        return cls(
            id=row["id"],
            message_id=row["message_id"],
            session_id=row["session_id"],
            tool_id=row["tool_id"],
            tool_name=row["tool_name"],
            input_json=row["input_json"],
            file_path=row["file_path"],
            command=row["command"],
            description=row["description"],
            outcome=row["outcome"],
            output_preview=row["output_preview"],
            duration_ms=row["duration_ms"],
            created_at=row["created_at"],
        )

    @property
    def outcome_icon(self) -> str:
        """Get icon for outcome status."""
        return {
            "success": "✓",
            "error": "✗",
            "unknown": "○",
        }.get(self.outcome, "?")

    def get_input(self) -> dict:
        """Parse and return input JSON."""
        if not self.input_json:
            return {}
        try:
            return json.loads(self.input_json)
        except json.JSONDecodeError:
            return {}


@dataclass
class Tag:
    """Represents a session tag/category."""

    id: int
    session_id: str
    tag: str
    created_at: str
    confidence: float = 1.0
    source: str = "auto"  # auto/manual

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Tag:
        """Create Tag from database row."""
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            tag=row["tag"],
            confidence=row["confidence"],
            source=row["source"],
            created_at=row["created_at"],
        )


@dataclass
class JournalCache:
    """Represents a cached journal entry."""

    date: str
    markdown: str
    session_ids: list[str]
    generated_at: str
    dirty: bool = False

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> JournalCache:
        """Create JournalCache from database row."""
        session_ids = json.loads(row["session_ids"]) if row["session_ids"] else []
        return cls(
            date=row["date"],
            markdown=row["markdown"],
            session_ids=session_ids,
            generated_at=row["generated_at"],
            dirty=bool(row["dirty"]),
        )


@dataclass
class SearchResult:
    """Represents a search result."""

    session_id: str
    message_id: int
    timestamp: str
    role: str
    snippet: str
    session_title: Optional[str] = None
    rank: float = 0.0

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> SearchResult:
        """Create SearchResult from database row."""
        return cls(
            session_id=row["session_id"],
            message_id=row.get("id", 0),
            timestamp=row["timestamp"],
            role=row["role"] or "unknown",
            snippet=row["snippet"],
            session_title=row.get("session_title"),
            rank=row.get("rank", 0.0),
        )

    @property
    def datetime(self) -> Optional[datetime]:
        """Get timestamp as datetime."""
        return parse_timestamp(self.timestamp)
