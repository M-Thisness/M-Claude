#!/usr/bin/env python3
"""
Install M-Claude git hooks.
Run this once to set up pre-commit sync.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# Add parent directory for config import
_parent = Path(__file__).parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

from config import get_paths


def main() -> None:
    """Install git hooks to the repository."""
    paths = get_paths()
    repo_root = paths.repo_root
    hooks_src = paths.scripts / "hooks"
    hooks_dest = repo_root / ".git" / "hooks"

    if not hooks_dest.exists():
        print(f"Error: {hooks_dest} not found. Are you in a git repo?")
        return

    # Install pre-commit hook
    src = hooks_src / "pre-commit"
    dest = hooks_dest / "pre-commit"

    if src.exists():
        shutil.copy2(src, dest)
        # Make executable on Unix
        if os.name != "nt":
            os.chmod(dest, 0o755)
        print("✅ Installed pre-commit hook")
        print(f"   {dest}")
    else:
        print(f"Error: {src} not found")


if __name__ == "__main__":
    main()
