#!/usr/bin/env python3
"""
Install M-Claude git hooks.
Run this once to set up pre-commit sync.
"""

import os
import shutil
from pathlib import Path

def main():
    repo_root = Path(__file__).parent.parent.parent.parent
    hooks_src = repo_root / "Projects" / "Scripts" / "hooks"
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
        if os.name != 'nt':
            os.chmod(dest, 0o755)
        print(f"✅ Installed pre-commit hook")
        print(f"   {dest}")
    else:
        print(f"Error: {src} not found")

if __name__ == "__main__":
    main()
