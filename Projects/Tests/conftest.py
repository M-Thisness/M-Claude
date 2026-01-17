#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for M-Claude tests.

This module provides:
- Path configuration for importing Scripts modules
- Shared fixtures for testing
- Test environment setup
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Add Scripts directory to Python path for all tests
_scripts_dir = Path(__file__).parent.parent / "Scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_jsonl_content() -> str:
    """Sample JSONL content for testing."""
    import json

    lines = [
        json.dumps(
            {
                "type": "user",
                "timestamp": "2026-01-15T10:00:00Z",
                "message": {"content": "Hello, Claude!"},
            }
        ),
        json.dumps(
            {
                "type": "assistant",
                "timestamp": "2026-01-15T10:00:05Z",
                "message": {
                    "content": [{"type": "text", "text": "Hello! How can I help you today?"}]
                },
            }
        ),
    ]
    return "\n".join(lines) + "\n"


@pytest.fixture
def sample_jsonl_file(temp_dir: Path, sample_jsonl_content: str) -> Path:
    """Create a sample JSONL file for testing."""
    file_path = temp_dir / "test_session.jsonl"
    file_path.write_text(sample_jsonl_content)
    return file_path
