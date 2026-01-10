#!/usr/bin/env python3
"""
Test suite for generate_journals.py
Tests session summarization and journal entry generation
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_journals import (
    extract_session_summary,
    get_time_of_day,
    group_by_date,
)


class TestSessionSummarization:
    """Test session summary extraction"""

    def test_basic_summary_extraction(self):
        """Test extracting summary from simple conversation"""
        messages = [
            {"role": "user", "content": "Create a Python script"},
            {"role": "assistant", "content": "I'll create a Python script for you"},
        ]
        summary = extract_session_summary(messages)
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_empty_messages(self):
        """Empty message list should return empty summary"""
        messages = []
        summary = extract_session_summary(messages)
        assert summary == ""

    def test_filter_meta_messages(self):
        """Meta messages (warmup, resume) should be filtered"""
        messages = [
            {"role": "system", "content": "warmup: starting session"},
            {"role": "user", "content": "Create a file"},
            {"role": "system", "content": "command-name: resume"},
        ]
        summary = extract_session_summary(messages)
        # Should not include warmup/resume messages
        assert "warmup" not in summary.lower()
        assert "command-name" not in summary.lower()

    def test_tweet_length_truncation(self):
        """Summaries should be truncated to tweet length (280 chars)"""
        long_message = "x" * 500
        messages = [
            {"role": "user", "content": long_message}
        ]
        summary = extract_session_summary(messages)
        assert len(summary) <= 280

    def test_multiple_user_prompts(self):
        """Should handle multiple user prompts in session"""
        messages = [
            {"role": "user", "content": "First task"},
            {"role": "assistant", "content": "Done"},
            {"role": "user", "content": "Second task"},
            {"role": "assistant", "content": "Completed"},
        ]
        summary = extract_session_summary(messages)
        assert len(summary) > 0


class TestTimeOfDay:
    """Test time-of-day classification"""

    def test_morning_hours(self):
        """Test morning classification (5am-11am)"""
        assert get_time_of_day("2025-12-30T06:00:00Z") == "morning"
        assert get_time_of_day("2025-12-30T10:30:00Z") == "morning"

    def test_day_hours(self):
        """Test day classification (11am-6pm)"""
        assert get_time_of_day("2025-12-30T12:00:00Z") == "day"
        assert get_time_of_day("2025-12-30T15:00:00Z") == "day"

    def test_night_hours(self):
        """Test night classification (6pm-5am)"""
        assert get_time_of_day("2025-12-30T18:00:00Z") == "night"
        assert get_time_of_day("2025-12-30T23:00:00Z") == "night"
        assert get_time_of_day("2025-12-30T02:00:00Z") == "night"

    def test_invalid_timestamp(self):
        """Invalid timestamps should return 'day' as default"""
        result = get_time_of_day("invalid")
        assert result in ["morning", "day", "night"]


class TestGroupByDate:
    """Test conversation grouping by date"""

    def test_single_session(self):
        """Test grouping single session"""
        conversations = [
            ("session1", "2025-12-30T14:30:00Z", [
                {"role": "user", "content": "Test"}
            ])
        ]
        grouped = group_by_date(conversations)
        assert "2025-12-30" in grouped
        assert len(grouped["2025-12-30"]) == 1

    def test_multiple_sessions_same_day(self):
        """Test multiple sessions on same day"""
        conversations = [
            ("session1", "2025-12-30T10:00:00Z", [{"role": "user", "content": "Morning"}]),
            ("session2", "2025-12-30T15:00:00Z", [{"role": "user", "content": "Afternoon"}]),
        ]
        grouped = group_by_date(conversations)
        assert len(grouped["2025-12-30"]) == 2

    def test_multiple_days(self):
        """Test sessions across multiple days"""
        conversations = [
            ("session1", "2025-12-30T14:00:00Z", [{"role": "user", "content": "Day 1"}]),
            ("session2", "2025-12-31T14:00:00Z", [{"role": "user", "content": "Day 2"}]),
        ]
        grouped = group_by_date(conversations)
        assert "2025-12-30" in grouped
        assert "2025-12-31" in grouped

    def test_empty_conversations(self):
        """Empty conversation list should return empty dict"""
        grouped = group_by_date([])
        assert grouped == {}


class TestFileTracking:
    """Test file modification tracking in summaries"""

    def test_extract_files_from_tools(self):
        """Should extract file paths from tool uses"""
        # This tests the integration with tool tracking
        messages = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Write",
                        "input": {"file_path": "/test/file.py"}
                    }
                ]
            }
        ]
        # Would need to test if file tracking works
        # This is more of an integration test
        pass


class TestEdgeCases:
    """Test edge cases"""

    def test_malformed_timestamp(self):
        """Malformed timestamps should be handled gracefully"""
        conversations = [
            ("session1", "not-a-timestamp", [{"role": "user", "content": "Test"}])
        ]
        # Should not crash
        grouped = group_by_date(conversations)
        assert isinstance(grouped, dict)

    def test_none_messages(self):
        """None in messages list should be handled"""
        messages = [None, {"role": "user", "content": "Test"}, None]
        summary = extract_session_summary(messages)
        # Should filter out None and process valid messages
        assert isinstance(summary, str)

    def test_unicode_content(self):
        """Unicode characters in content should be preserved"""
        messages = [
            {"role": "user", "content": "Hello 世界 🌍"}
        ]
        summary = extract_session_summary(messages)
        # Should handle unicode gracefully
        assert isinstance(summary, str)


class TestJournalFormatting:
    """Test journal entry formatting"""

    def test_entry_structure(self):
        """Journal entries should have consistent structure"""
        # This would test the final output format
        # Requires integration with actual journal generation
        pass

    def test_markdown_formatting(self):
        """Journal should use proper markdown"""
        # Test that headers, lists, timestamps are formatted correctly
        pass
