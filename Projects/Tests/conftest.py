#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to Python path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
