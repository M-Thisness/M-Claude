"""
M-Claude Scripts Package

A collection of tools for managing Claude Code conversation archives.

This package uses Python standard library only - no external dependencies required.

Modules:
    config: Centralized configuration and path management
    cli: Unified command-line interface
    sync_raw_logs: Conversation log synchronization
    convert_to_markdown: JSONL to Markdown conversion
    generate_journals: Daily journal generation
    generate_stats: Statistics dashboard generation
    search: Full-text search functionality
    redact_gitleaks_secrets: Secret detection and redaction
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "M"
__all__ = [
    "config",
    "cli",
    "sync_raw_logs",
    "convert_to_markdown",
    "generate_journals",
    "generate_stats",
    "search",
    "redact_gitleaks_secrets",
]
