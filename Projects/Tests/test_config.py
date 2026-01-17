#!/usr/bin/env python3
"""
Tests for the centralized configuration module.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from config import PathConfig, PlatformInfo, get_paths, get_platform, setup_logging


class TestPlatformInfo:
    """Tests for PlatformInfo class."""

    def test_detect_returns_platform_info(self) -> None:
        """Test that detect() returns a PlatformInfo instance."""
        info = PlatformInfo.detect()
        assert isinstance(info, PlatformInfo)
        assert isinstance(info.system, str)
        assert isinstance(info.release, str)

    def test_platform_flags_are_mutually_consistent(self) -> None:
        """Test that platform flags make sense together."""
        info = PlatformInfo.detect()
        # At most one of these should be True (except termux which is a special case)
        platforms = [info.is_windows, info.is_macos, info.is_linux]
        if not info.is_termux:
            assert sum(platforms) == 1, "Exactly one platform flag should be True"

    def test_display_name_returns_string(self) -> None:
        """Test that display_name() returns a non-empty string."""
        info = PlatformInfo.detect()
        name = info.display_name()
        assert isinstance(name, str)
        assert len(name) > 0

    def test_frozen_dataclass_is_immutable(self) -> None:
        """Test that PlatformInfo is immutable."""
        info = PlatformInfo.detect()
        with pytest.raises(AttributeError):
            info.system = "NewSystem"  # type: ignore


class TestPathConfig:
    """Tests for PathConfig class."""

    def test_singleton_instance(self) -> None:
        """Test that get_instance returns the same instance."""
        instance1 = PathConfig.get_instance()
        instance2 = PathConfig.get_instance()
        assert instance1 is instance2

    def test_repo_root_exists(self) -> None:
        """Test that repo_root points to an existing directory."""
        paths = get_paths()
        # The repo root should exist when running tests
        assert paths.repo_root.exists()

    def test_archives_path(self) -> None:
        """Test that archives path is under repo root."""
        paths = get_paths()
        assert paths.repo_root in paths.archives.parents or paths.archives == paths.repo_root

    def test_journals_path(self) -> None:
        """Test that journals path is under repo root."""
        paths = get_paths()
        assert paths.repo_root in paths.journals.parents or paths.journals == paths.repo_root

    def test_scripts_path(self) -> None:
        """Test that scripts path exists."""
        paths = get_paths()
        assert paths.scripts.exists()
        assert paths.scripts.is_dir()

    def test_home_is_user_home(self) -> None:
        """Test that home returns the user's home directory."""
        paths = get_paths()
        assert paths.home == Path.home()

    def test_env_override_archives(self) -> None:
        """Test that M_CLAUDE_ARCHIVES env var overrides archives path."""
        with patch.dict(os.environ, {"M_CLAUDE_ARCHIVES": "/custom/archives"}):
            # Create a new instance to pick up the env var
            config = PathConfig()
            config._initialized = False
            config._initialize()
            assert config.archives == Path("/custom/archives")

    def test_env_override_journals(self) -> None:
        """Test that M_CLAUDE_JOURNALS env var overrides journals path."""
        with patch.dict(os.environ, {"M_CLAUDE_JOURNALS": "/custom/journals"}):
            config = PathConfig()
            config._initialized = False
            config._initialize()
            assert config.journals == Path("/custom/journals")

    def test_get_claude_project_dirs_returns_list(self) -> None:
        """Test that get_claude_project_dirs returns a list."""
        paths = get_paths()
        dirs = paths.get_claude_project_dirs()
        assert isinstance(dirs, list)


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_returns_logger(self) -> None:
        """Test that setup_logging returns a logger."""
        import logging

        logger = setup_logging("test_logger")
        assert isinstance(logger, logging.Logger)

    def test_named_logger(self) -> None:
        """Test that setup_logging creates a named logger."""
        logger = setup_logging("custom_name")
        assert logger.name == "custom_name"

    def test_env_log_level(self) -> None:
        """Test that M_CLAUDE_LOG_LEVEL env var sets log level."""
        import logging

        with patch.dict(os.environ, {"M_CLAUDE_LOG_LEVEL": "DEBUG"}):
            logger = setup_logging("debug_test_logger")
            assert logger.level == logging.DEBUG


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_paths_returns_path_config(self) -> None:
        """Test that get_paths returns a PathConfig instance."""
        paths = get_paths()
        assert isinstance(paths, PathConfig)

    def test_get_platform_returns_platform_info(self) -> None:
        """Test that get_platform returns a PlatformInfo instance."""
        platform = get_platform()
        assert isinstance(platform, PlatformInfo)
