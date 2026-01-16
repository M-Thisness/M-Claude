#!/usr/bin/env python3
"""
Gitleaks Secret Auto-Redaction Script

Runs gitleaks scan on staged files and automatically redacts any detected secrets.
Instead of blocking commits, this script redacts secrets in-place and allows the
commit to proceed.

Usage:
    python3 redact_gitleaks_secrets.py

Features:
- Scans only staged files for performance
- Redacts individual secrets (not entire lines)
- Preserves file structure and formatting
- Works with MAX STRICT MODE gitleaks configuration
- Provides detailed reporting of redactions
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def run_command(cmd: List[str], capture_output=True, check=False) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        return e


def check_gitleaks_installed() -> bool:
    """Check if gitleaks is installed"""
    result = run_command(["which", "gitleaks"])
    return result.returncode == 0


def get_repo_root() -> Path:
    """Get the repository root directory"""
    result = run_command(["git", "rev-parse", "--show-toplevel"])
    if result.returncode == 0:
        return Path(result.stdout.strip())
    raise RuntimeError("Not in a git repository")


def get_staged_files() -> List[str]:
    """Get list of staged files"""
    result = run_command(["git", "diff", "--cached", "--name-only"])
    if result.returncode == 0 and result.stdout:
        return [f for f in result.stdout.strip().split('\n') if f]
    return []


def run_gitleaks_scan(repo_root: Path) -> Tuple[List[Dict], int]:
    """
    Run gitleaks on staged files and return findings.

    Returns:
        Tuple of (findings_list, return_code)
    """
    config_path = repo_root / ".gitleaks.toml"

    # Run gitleaks protect (scans staged files) with JSON output
    cmd = [
        "gitleaks",
        "protect",
        "--staged",
        f"--config={config_path}",
        "--redact",
        "--report-format=json",
        "--report-path=/tmp/gitleaks-findings.json",
        "--verbose"
    ]

    result = run_command(cmd, check=False)

    # Parse findings from JSON report
    findings = []
    report_path = Path("/tmp/gitleaks-findings.json")

    if report_path.exists():
        try:
            with open(report_path, 'r') as f:
                findings = json.load(f)
            # Clean up temp file
            report_path.unlink()
        except (json.JSONDecodeError, IOError) as e:
            print(f"{Colors.YELLOW}⚠️  Warning: Could not parse gitleaks JSON report: {e}{Colors.END}")

    return findings, result.returncode


def redact_secret(content: str, secret: str, line_number: int, start_col: int, end_col: int) -> Tuple[str, bool]:
    """
    Redact a specific secret from content.

    Args:
        content: Full file content
        secret: The secret string to redact
        line_number: Line number (1-indexed)
        start_col: Start column (1-indexed)
        end_col: End column (1-indexed)

    Returns:
        Tuple of (modified_content, was_modified)
    """
    lines = content.split('\n')

    # Convert to 0-indexed
    line_idx = line_number - 1
    start_idx = start_col - 1
    end_idx = end_col - 1

    if line_idx >= len(lines):
        return content, False

    line = lines[line_idx]

    # Extract the secret from the line using position
    if start_idx >= 0 and end_idx <= len(line):
        actual_secret = line[start_idx:end_idx]

        # Create redaction marker
        # Preserve first 4 and last 4 characters for identification
        secret_len = len(actual_secret)
        if secret_len <= 8:
            redacted = "***REDACTED***"
        else:
            prefix = actual_secret[:4]
            suffix = actual_secret[-4:]
            redacted = f"{prefix}***REDACTED***{suffix}"

        # Replace the secret in the line
        new_line = line[:start_idx] + redacted + line[end_idx:]
        lines[line_idx] = new_line

        return '\n'.join(lines), True

    # Fallback: try to find and replace the secret in the line
    if secret in line:
        secret_len = len(secret)
        if secret_len <= 8:
            redacted = "***REDACTED***"
        else:
            prefix = secret[:4]
            suffix = secret[-4:]
            redacted = f"{prefix}***REDACTED***{suffix}"

        new_line = line.replace(secret, redacted, 1)
        lines[line_idx] = new_line
        return '\n'.join(lines), True

    return content, False


def process_findings(findings: List[Dict], repo_root: Path) -> Dict[str, int]:
    """
    Process gitleaks findings and redact secrets in files.

    Returns:
        Dictionary mapping file paths to number of redactions
    """
    files_modified = {}

    # Group findings by file
    findings_by_file = {}
    for finding in findings:
        file_path = finding.get('File', '')
        if file_path not in findings_by_file:
            findings_by_file[file_path] = []
        findings_by_file[file_path].append(finding)

    # Process each file
    for rel_path, file_findings in findings_by_file.items():
        abs_path = repo_root / rel_path

        if not abs_path.exists():
            print(f"{Colors.YELLOW}⚠️  File not found: {rel_path}{Colors.END}")
            continue

        # Read file content
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"{Colors.RED}❌ Error reading {rel_path}: {e}{Colors.END}")
            continue

        # Sort findings by line number (descending) to avoid position shifts
        sorted_findings = sorted(
            file_findings,
            key=lambda x: (x.get('StartLine', 0), x.get('StartColumn', 0)),
            reverse=True
        )

        redaction_count = 0
        modified_content = content

        # Redact each secret
        for finding in sorted_findings:
            secret = finding.get('Secret', '')
            line_num = finding.get('StartLine', 0)
            start_col = finding.get('StartColumn', 0)
            end_col = finding.get('EndColumn', 0)
            rule_id = finding.get('RuleID', 'unknown')

            if not secret or not line_num:
                continue

            modified_content, was_modified = redact_secret(
                modified_content,
                secret,
                line_num,
                start_col,
                end_col
            )

            if was_modified:
                redaction_count += 1
                print(f"  {Colors.CYAN}🔒 Redacted {rule_id} at line {line_num}{Colors.END}")

        # Write back modified content
        if redaction_count > 0:
            try:
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                files_modified[rel_path] = redaction_count
                print(f"{Colors.GREEN}✅ Modified {rel_path} ({redaction_count} redactions){Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error writing {rel_path}: {e}{Colors.END}")

    return files_modified


def restage_files(files: List[str], repo_root: Path):
    """Re-stage modified files"""
    if not files:
        return

    print(f"\n{Colors.BLUE}📝 Re-staging modified files...{Colors.END}")
    for file in files:
        result = run_command(["git", "add", str(repo_root / file)])
        if result.returncode == 0:
            print(f"  {Colors.GREEN}✓{Colors.END} {file}")
        else:
            print(f"  {Colors.RED}✗{Colors.END} {file}")


def main():
    """Main entry point"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}🔍 Gitleaks Secret Auto-Redaction (⚡ MAX STRICT MODE){Colors.END}\n")

    # Check if gitleaks is installed
    if not check_gitleaks_installed():
        print(f"{Colors.YELLOW}⚠️  gitleaks not installed - skipping secret scanning{Colors.END}")
        print(f"{Colors.YELLOW}   Install: brew install gitleaks{Colors.END}")
        return 0

    # Get repo root
    try:
        repo_root = get_repo_root()
    except RuntimeError as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        return 1

    # Check for staged files
    staged_files = get_staged_files()
    if not staged_files:
        print(f"{Colors.BLUE}ℹ️  No staged files to scan{Colors.END}")
        return 0

    print(f"{Colors.BLUE}📂 Scanning {len(staged_files)} staged file(s)...{Colors.END}")

    # Run gitleaks scan
    findings, return_code = run_gitleaks_scan(repo_root)

    if not findings:
        print(f"{Colors.GREEN}✅ No secrets detected - commit can proceed{Colors.END}\n")
        return 0

    print(f"\n{Colors.YELLOW}⚠️  Found {len(findings)} potential secret(s){Colors.END}")
    print(f"{Colors.CYAN}🔧 Auto-redacting secrets...{Colors.END}\n")

    # Process findings and redact secrets
    files_modified = process_findings(findings, repo_root)

    # Re-stage modified files
    if files_modified:
        restage_files(list(files_modified.keys()), repo_root)

        total_redactions = sum(files_modified.values())
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Redacted {total_redactions} secret(s) in {len(files_modified)} file(s){Colors.END}")
        print(f"{Colors.GREEN}✅ Modified files have been re-staged{Colors.END}")
        print(f"{Colors.GREEN}✅ Commit will proceed with redacted content{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}⚠️  No secrets could be redacted (may be false positives){Colors.END}")
        print(f"{Colors.YELLOW}   Review gitleaks output above{Colors.END}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
