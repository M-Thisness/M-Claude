#!/usr/bin/env python3
"""
M-Claude Configuration Module

Centralized configuration for all M-Claude scripts. This module provides:
- Path discovery with environment variable overrides
- Platform detection
- Consistent logging setup
- Type-safe configuration access

Environment Variables:
    M_CLAUDE_ROOT: Override repository root path
    M_CLAUDE_ARCHIVES: Override archives directory path
    M_CLAUDE_JOURNALS: Override journals directory path
    M_CLAUDE_CHAT_LOGS: Override chat logs directory path
    M_CLAUDE_LOG_LEVEL: Set logging level (DEBUG, INFO, WARNING, ERROR)
"""

from __future__ import annotations

import logging
import os
import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Final, List, Optional


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SIMPLE_LOG_FORMAT: Final[str] = "%(levelname)s - %(message)s"


# =============================================================================
# PLATFORM DETECTION
# =============================================================================

@dataclass(frozen=True)
class PlatformInfo:
    """Immutable platform information."""

    system: str
    release: str
    is_termux: bool
    is_windows: bool
    is_macos: bool
    is_linux: bool

    @classmethod
    def detect(cls) -> PlatformInfo:
        """Detect current platform information."""
        system = platform.system()
        is_termux = os.path.exists("/data/data/com.termux")

        return cls(
            system=system,
            release=platform.release(),
            is_termux=is_termux,
            is_windows=system == "Windows",
            is_macos=system == "Darwin",
            is_linux=system == "Linux" and not is_termux,
        )

    def display_name(self) -> str:
        """Get human-readable platform name."""
        if self.is_termux:
            return "Android (Termux)"
        elif self.is_macos:
            try:
                mac_ver = platform.mac_ver()[0]
                return f"macOS {mac_ver}"
            except Exception:
                return "macOS"
        elif self.is_windows:
            return f"Windows {self.release}"
        elif self.is_linux:
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            return line.split("=")[1].strip().strip('"')
            except FileNotFoundError:
                pass
            return f"Linux {self.release}"
        return self.system


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

def _discover_repo_root() -> Path:
    """
    Discover repository root using multiple strategies.

    Priority:
    1. M_CLAUDE_ROOT environment variable
    2. Walk up from this file looking for .git directory
    3. Walk up from current working directory looking for .git

    Raises:
        RuntimeError: If repository root cannot be found
    """
    # Strategy 1: Environment variable
    env_root = os.environ.get("M_CLAUDE_ROOT")
    if env_root:
        path = Path(env_root)
        if path.exists():
            return path.resolve()

    # Strategy 2: Walk up from this file
    current = Path(__file__).resolve().parent
    for _ in range(10):  # Limit depth to prevent infinite loop
        if (current / ".git").exists():
            return current
        if (current / "Projects" / "Scripts").exists():
            return current
        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent

    # Strategy 3: Walk up from cwd
    current = Path.cwd().resolve()
    for _ in range(10):
        if (current / ".git").exists():
            return current
        if (current / "Projects" / "Scripts").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    # Fallback: assume we're in Projects/Scripts
    fallback = Path(__file__).resolve().parent.parent.parent
    if fallback.exists():
        return fallback

    raise RuntimeError(
        "Could not discover M-Claude repository root. "
        "Set M_CLAUDE_ROOT environment variable or run from within the repository."
    )


@dataclass
class PathConfig:
    """
    Path configuration with lazy initialization and environment overrides.

    All paths are resolved to absolute paths on first access.
    """

    _repo_root: Optional[Path] = field(default=None, repr=False)
    _initialized: bool = field(default=False, repr=False)

    # Class-level cache
    _instance: ClassVar[Optional[PathConfig]] = None

    def __post_init__(self) -> None:
        """Initialize paths on creation."""
        if not self._initialized:
            self._initialize()

    def _initialize(self) -> None:
        """Lazy initialization of paths."""
        self._repo_root = _discover_repo_root()
        self._initialized = True

    @classmethod
    def get_instance(cls) -> PathConfig:
        """Get singleton instance of PathConfig."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def repo_root(self) -> Path:
        """Repository root directory."""
        if self._repo_root is None:
            self._initialize()
        assert self._repo_root is not None
        return self._repo_root

    @property
    def home(self) -> Path:
        """User home directory."""
        return Path.home()

    @property
    def archives(self) -> Path:
        """Archives directory for JSONL conversation logs."""
        env_path = os.environ.get("M_CLAUDE_ARCHIVES")
        if env_path:
            return Path(env_path).resolve()
        return self.repo_root / "Archives"

    @property
    def journals(self) -> Path:
        """Journals directory for daily summaries."""
        env_path = os.environ.get("M_CLAUDE_JOURNALS")
        if env_path:
            return Path(env_path).resolve()
        return self.repo_root / "Journals"

    @property
    def chat_logs(self) -> Path:
        """Chat logs directory (alias for archives, legacy compatibility)."""
        env_path = os.environ.get("M_CLAUDE_CHAT_LOGS")
        if env_path:
            return Path(env_path).resolve()
        return self.repo_root / "CHAT_LOGS"

    @property
    def scripts(self) -> Path:
        """Scripts directory."""
        return self.repo_root / "Projects" / "Scripts"

    @property
    def tests(self) -> Path:
        """Tests directory."""
        return self.repo_root / "Projects" / "Tests"

    @property
    def docs(self) -> Path:
        """Documentation directory."""
        return self.repo_root / "Docs"

    @property
    def projects(self) -> Path:
        """Projects directory."""
        return self.repo_root / "Projects"

    def claude_projects_dir(self) -> Path:
        """Claude Code projects directory (~/.claude/projects)."""
        return self.home / ".claude" / "projects"

    def get_claude_project_dirs(self) -> List[Path]:
        """
        Discover Claude Code project directories containing JSONL files.

        Returns:
            List of directories containing conversation logs
        """
        claude_base = self.claude_projects_dir()
        project_dirs: List[Path] = []

        if not claude_base.exists():
            return project_dirs

        try:
            for entry in claude_base.iterdir():
                if entry.is_dir():
                    jsonl_files = list(entry.glob("*.jsonl"))
                    if jsonl_files:
                        project_dirs.append(entry)
        except PermissionError:
            pass

        return project_dirs

    def ensure_directories(self) -> None:
        """Create all configured directories if they don't exist."""
        for path in [self.archives, self.journals]:
            path.mkdir(parents=True, exist_ok=True)


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging(
    name: Optional[str] = None,
    level: Optional[int] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Configure and return a logger with consistent settings.

    Args:
        name: Logger name (None for root logger)
        level: Logging level (default: from M_CLAUDE_LOG_LEVEL env or INFO)
        format_string: Log format (default: DEFAULT_LOG_FORMAT)

    Returns:
        Configured logger instance
    """
    if level is None:
        env_level = os.environ.get("M_CLAUDE_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, env_level, logging.INFO)

    if format_string is None:
        format_string = DEFAULT_LOG_FORMAT

    logging.basicConfig(level=level, format=format_string)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    return logger


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_paths() -> PathConfig:
    """Get the singleton PathConfig instance."""
    return PathConfig.get_instance()


def get_platform() -> PlatformInfo:
    """Get current platform information."""
    return PlatformInfo.detect()


# =============================================================================
# MODULE-LEVEL INITIALIZATION
# =============================================================================

# Pre-initialize for module-level access
paths = PathConfig.get_instance()
platform_info = PlatformInfo.detect()
