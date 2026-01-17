#!/usr/bin/env python3
"""
Tests for the unified CLI module.
"""

from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from cli import __version__, create_parser, main


class TestCLIParser:
    """Tests for CLI argument parsing."""

    def test_parser_creation(self) -> None:
        """Test that parser is created without errors."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "m-claude"

    def test_version_flag(self) -> None:
        """Test --version flag."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0

    def test_no_args_shows_help(self) -> None:
        """Test that no arguments shows help and returns 0."""
        result = main([])
        assert result == 0

    def test_sync_command_parsing(self) -> None:
        """Test sync command is parsed correctly."""
        parser = create_parser()
        args = parser.parse_args(["sync"])
        assert args.command == "sync"

    def test_search_command_parsing(self) -> None:
        """Test search command with query."""
        parser = create_parser()
        args = parser.parse_args(["search", "test query"])
        assert args.command == "search"
        assert args.query == "test query"

    def test_search_with_date_filters(self) -> None:
        """Test search command with date filters."""
        parser = create_parser()
        args = parser.parse_args(["search", "query", "--from", "2025-01-01", "--to", "2025-12-31"])
        assert args.date_from == "2025-01-01"
        assert args.date_to == "2025-12-31"

    def test_search_with_tool_filter(self) -> None:
        """Test search command with tool filter."""
        parser = create_parser()
        args = parser.parse_args(["search", "query", "--tool", "Bash"])
        assert args.tool == "Bash"

    def test_search_with_limit(self) -> None:
        """Test search command with custom limit."""
        parser = create_parser()
        args = parser.parse_args(["search", "query", "--limit", "100"])
        assert args.limit == 100

    def test_search_default_limit(self) -> None:
        """Test search command has default limit of 50."""
        parser = create_parser()
        args = parser.parse_args(["search", "query"])
        assert args.limit == 50

    def test_stats_command_parsing(self) -> None:
        """Test stats command is parsed correctly."""
        parser = create_parser()
        args = parser.parse_args(["stats"])
        assert args.command == "stats"
        assert args.output == "STATS.md"

    def test_stats_with_custom_output(self) -> None:
        """Test stats command with custom output."""
        parser = create_parser()
        args = parser.parse_args(["stats", "--output", "custom.md"])
        assert args.output == "custom.md"

    def test_config_command_parsing(self) -> None:
        """Test config command is parsed correctly."""
        parser = create_parser()
        args = parser.parse_args(["config"])
        assert args.command == "config"

    def test_hooks_install_command(self) -> None:
        """Test hooks install subcommand."""
        parser = create_parser()
        args = parser.parse_args(["hooks", "install"])
        assert args.command == "hooks"
        assert args.hooks_action == "install"


class TestCLICommands:
    """Tests for CLI command execution."""

    def test_config_command_runs(self) -> None:
        """Test that config command runs without errors."""
        # Capture stdout
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            result = main(["config"])
        assert result == 0
        output = captured_output.getvalue()
        assert "M-Claude Configuration" in output
        assert "Platform:" in output
        assert "Paths:" in output


class TestCLIVersion:
    """Tests for version handling."""

    def test_version_is_string(self) -> None:
        """Test that version is a valid string."""
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_format(self) -> None:
        """Test that version follows semver format."""
        parts = __version__.split(".")
        assert len(parts) >= 2  # At least major.minor
        for part in parts:
            assert part.isdigit(), f"Version part '{part}' is not a digit"
