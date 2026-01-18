#!/usr/bin/env python3
"""
M-Claude Journal Generator

Generates rich daily journal entries from indexed sessions.
Only regenerates journals for dates marked as dirty.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def format_duration(ms: int) -> str:
    """Format milliseconds to human readable duration."""
    if ms <= 0:
        return ""
    sec = ms / 1000
    if sec > 3600:
        return f"{sec / 3600:.1f}h"
    elif sec > 60:
        return f"{sec / 60:.0f}m"
    return f"{sec:.0f}s"


def format_time(timestamp: str) -> str:
    """Format ISO timestamp to readable time."""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%I:%M %p')
    except (ValueError, AttributeError):
        return ""


class JournalGenerator:
    """Generates journal entries from database."""

    def __init__(self, db, output_dir: Path):
        self.db = db
        self.output_dir = output_dir

    def get_dirty_dates(self) -> List[str]:
        """Get list of dates that need journal regeneration."""
        rows = self.db.fetchall(
            "SELECT date FROM journal_cache WHERE dirty = 1 ORDER BY date"
        )
        return [row["date"] for row in rows]

    def get_all_dates(self) -> List[str]:
        """Get all dates with sessions."""
        rows = self.db.fetchall("""
            SELECT DISTINCT substr(first_timestamp, 1, 10) as date
            FROM sessions
            WHERE first_timestamp IS NOT NULL
            ORDER BY date
        """)
        return [row["date"] for row in rows]

    def get_sessions_for_date(self, date: str) -> List[Dict]:
        """Get all sessions for a specific date."""
        rows = self.db.fetchall("""
            SELECT s.*, GROUP_CONCAT(t.tag) as tags
            FROM sessions s
            LEFT JOIN tags t ON t.session_id = s.id
            WHERE substr(s.first_timestamp, 1, 10) = ?
            GROUP BY s.id
            ORDER BY s.first_timestamp
        """, (date,))
        return [dict(row) for row in rows]

    def get_tool_calls_for_session(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get tool calls for a session."""
        rows = self.db.fetchall("""
            SELECT * FROM tool_calls
            WHERE session_id = ?
            ORDER BY id
            LIMIT ?
        """, (session_id, limit))
        return [dict(row) for row in rows]

    def get_user_prompts(self, session_id: str, limit: int = 5) -> List[str]:
        """Get user prompts for a session."""
        rows = self.db.fetchall("""
            SELECT content_text FROM messages
            WHERE session_id = ? AND role = 'user' AND content_text IS NOT NULL
            ORDER BY timestamp
            LIMIT ?
        """, (session_id, limit))
        prompts = []
        for row in rows:
            text = row["content_text"]
            if text and len(text) > 10 and not text.startswith('<'):
                prompts.append(text[:200])
        return prompts

    def render_session(self, session: Dict) -> str:
        """Render a single session entry."""
        lines = []

        # Time and title
        time_str = format_time(session.get('first_timestamp', ''))
        title = session.get('title', 'Untitled session')
        if len(title) > 80:
            title = title[:77] + "..."

        lines.append(f"### {time_str} — {title}\n")

        # Tags
        tags = session.get('tags')
        if tags:
            tag_list = tags.split(',')[:5]
            lines.append(f"*Tags: {', '.join(tag_list)}*\n")

        # Tool actions
        tool_calls = self.get_tool_calls_for_session(session['id'], limit=8)
        if tool_calls:
            lines.append("\n**Actions:**\n")
            for tc in tool_calls:
                icon = "✓" if tc.get('outcome') == 'success' else "○"
                desc = tc.get('description', tc.get('tool_name', 'Unknown'))
                lines.append(f"- {icon} `{tc['tool_name']}`: {desc}\n")

        # Duration and stats
        meta_parts = []
        duration = format_duration(session.get('duration_ms', 0))
        if duration:
            meta_parts.append(f"⏱️ {duration}")
        msg_count = session.get('message_count', 0)
        if msg_count:
            meta_parts.append(f"{msg_count} messages")

        if meta_parts:
            lines.append(f"\n*{' | '.join(meta_parts)}*\n")

        # User prompts (collapsed)
        prompts = self.get_user_prompts(session['id'], limit=3)
        if prompts and len(prompts) > 1:
            lines.append("\n<details>\n<summary>Conversation highlights</summary>\n\n")
            for prompt in prompts[1:]:  # Skip first (it's the title)
                if len(prompt) > 100:
                    prompt = prompt[:97] + "..."
                lines.append(f"> {prompt}\n\n")
            lines.append("</details>\n")

        lines.append("\n---\n")
        return ''.join(lines)

    def render_journal(self, date: str, sessions: List[Dict]) -> str:
        """Render a complete journal for a date."""
        lines = [f"# {date}\n\n"]

        # Summary stats
        total_duration = sum(s.get('duration_ms', 0) for s in sessions)
        duration_str = format_duration(total_duration)

        if duration_str:
            lines.append(f"*{len(sessions)} sessions • {duration_str} total*\n\n")
        else:
            lines.append(f"*{len(sessions)} sessions*\n\n")

        lines.append("---\n\n")

        # Render each session
        for session in sessions:
            lines.append(self.render_session(session))

        return ''.join(lines)

    def generate_for_date(self, date: str) -> bool:
        """Generate journal for a specific date."""
        sessions = self.get_sessions_for_date(date)
        if not sessions:
            return False

        markdown = self.render_journal(date, sessions)

        # Write to file
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{date}.md"

        temp_path = output_path.with_suffix('.tmp')
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            os.replace(temp_path, output_path)
        except Exception as e:
            logger.error(f"Failed to write journal {date}: {e}")
            if temp_path.exists():
                temp_path.unlink()
            return False

        # Update cache
        now = datetime.now().isoformat()
        session_ids = json.dumps([s['id'] for s in sessions])
        self.db.execute("""
            INSERT INTO journal_cache (date, markdown, session_ids, generated_at, dirty)
            VALUES (?, ?, ?, ?, 0)
            ON CONFLICT(date) DO UPDATE SET
                markdown = excluded.markdown,
                session_ids = excluded.session_ids,
                generated_at = excluded.generated_at,
                dirty = 0
        """, (date, markdown, session_ids, now))

        logger.info(f"Generated journal for {date}: {len(sessions)} sessions")
        return True

    def generate_dirty(self) -> int:
        """Generate journals for all dirty dates."""
        dirty_dates = self.get_dirty_dates()
        count = 0
        for date in dirty_dates:
            if self.generate_for_date(date):
                count += 1
        return count

    def generate_all(self) -> int:
        """Regenerate all journals."""
        dates = self.get_all_dates()
        count = 0
        for date in dates:
            if self.generate_for_date(date):
                count += 1
        return count
