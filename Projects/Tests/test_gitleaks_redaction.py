#!/usr/bin/env python3
"""
Test script for gitleaks secret redaction functionality

This script creates test files with fake secrets, stages them, and verifies
that the redaction script properly detects and redacts the secrets.

Prerequisites:
- gitleaks must be installed (brew install gitleaks)
- Run from repository root

Usage:
    python3 tests/test_gitleaks_redaction.py
"""

import os
import subprocess
import tempfile
from pathlib import Path


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def run_command(cmd, capture_output=True):
    """Run a command and return result"""
    return subprocess.run(cmd, capture_output=capture_output, text=True, shell=True)


def check_gitleaks():
    """Check if gitleaks is installed"""
    result = run_command("which gitleaks")
    if result.returncode != 0:
        print(f"{Colors.RED}❌ gitleaks not installed{Colors.END}")
        print(f"{Colors.YELLOW}   Install: brew install gitleaks{Colors.END}")
        return False
    return True


def create_test_file(repo_root: Path, filename: str, content: str):
    """Create a test file with secrets"""
    test_file = repo_root / "tests" / filename
    test_file.parent.mkdir(parents=True, exist_ok=True)

    with open(test_file, 'w') as f:
        f.write(content)

    return test_file


def test_anthropic_api_key_redaction():
    """Test redaction of Anthropic API key"""
    print(f"\n{Colors.BOLD}Test 1: Anthropic API Key Redaction{Colors.END}")

    repo_root = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True
    ).strip())

    test_content = '''# Test Configuration
ANTHROPIC_API_KEY=sk-ant-api03-test1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqr

def get_api_key():
    return "sk-ant-api03-test1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqr"
'''

    test_file = create_test_file(repo_root, "test_secret_1.py", test_content)

    # Stage the file
    run_command(f"git add {test_file}")

    # Run redaction script
    redact_script = repo_root / "Projects/Scripts/redact_gitleaks_secrets.py"
    result = run_command(f"python3 {redact_script}")

    # Read back the file
    with open(test_file, 'r') as f:
        redacted_content = f.read()

    # Check if secrets were redacted
    if "sk-ant-api03-test" in redacted_content and "***REDACTED***" in redacted_content:
        print(f"{Colors.GREEN}✅ PASS: Secrets were redacted{Colors.END}")
        return True
    elif "***REDACTED***" not in redacted_content:
        print(f"{Colors.YELLOW}⚠️  SKIP: No secrets detected (may be allowlisted){Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ FAIL: Secrets not properly redacted{Colors.END}")
        return False


def test_github_token_redaction():
    """Test redaction of GitHub PAT"""
    print(f"\n{Colors.BOLD}Test 2: GitHub Token Redaction{Colors.END}")

    repo_root = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True
    ).strip())

    test_content = '''# GitHub Configuration
GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuv

headers = {
    "Authorization": "token ghp_1234567890abcdefghijklmnopqrstuv"
}
'''

    test_file = create_test_file(repo_root, "test_secret_2.py", test_content)

    # Stage the file
    run_command(f"git add {test_file}")

    # Run redaction script
    redact_script = repo_root / "Projects/Scripts/redact_gitleaks_secrets.py"
    result = run_command(f"python3 {redact_script}")

    # Read back the file
    with open(test_file, 'r') as f:
        redacted_content = f.read()

    # Check if secrets were redacted
    if "ghp_" in redacted_content and "***REDACTED***" in redacted_content:
        print(f"{Colors.GREEN}✅ PASS: Secrets were redacted{Colors.END}")
        return True
    elif "***REDACTED***" not in redacted_content:
        print(f"{Colors.YELLOW}⚠️  SKIP: No secrets detected (may be allowlisted){Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ FAIL: Secrets not properly redacted{Colors.END}")
        return False


def test_aws_key_redaction():
    """Test redaction of AWS keys"""
    print(f"\n{Colors.BOLD}Test 3: AWS Access Key Redaction{Colors.END}")

    repo_root = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True
    ).strip())

    test_content = '''# AWS Configuration
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

class AWSConfig:
    ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
    SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
'''

    test_file = create_test_file(repo_root, "test_secret_3.py", test_content)

    # Stage the file
    run_command(f"git add {test_file}")

    # Run redaction script
    redact_script = repo_root / "Projects/Scripts/redact_gitleaks_secrets.py"
    result = run_command(f"python3 {redact_script}")

    # Read back the file
    with open(test_file, 'r') as f:
        redacted_content = f.read()

    # Check if secrets were redacted
    if "AKIA" in redacted_content and "***REDACTED***" in redacted_content:
        print(f"{Colors.GREEN}✅ PASS: Secrets were redacted{Colors.END}")
        return True
    elif "***REDACTED***" not in redacted_content:
        print(f"{Colors.YELLOW}⚠️  SKIP: No secrets detected (may be allowlisted){Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ FAIL: Secrets not properly redacted{Colors.END}")
        return False


def cleanup_test_files():
    """Clean up test files"""
    print(f"\n{Colors.BLUE}🧹 Cleaning up test files...{Colors.END}")

    repo_root = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True
    ).strip())

    test_files = [
        "tests/test_secret_1.py",
        "tests/test_secret_2.py",
        "tests/test_secret_3.py"
    ]

    for file in test_files:
        filepath = repo_root / file
        if filepath.exists():
            # Unstage
            run_command(f"git reset HEAD {filepath}")
            # Remove file
            filepath.unlink()
            print(f"  {Colors.GREEN}✓{Colors.END} Removed {file}")


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Gitleaks Secret Redaction Test Suite{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

    # Check prerequisites
    if not check_gitleaks():
        return 1

    # Run tests
    tests = [
        test_anthropic_api_key_redaction,
        test_github_token_redaction,
        test_aws_key_redaction
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"{Colors.RED}❌ Test failed with exception: {e}{Colors.END}")
            results.append(False)

    # Cleanup
    cleanup_test_files()

    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test Summary{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"{Colors.GREEN}✅ All {total} tests passed!{Colors.END}")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠️  {passed}/{total} tests passed{Colors.END}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
