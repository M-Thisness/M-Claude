#!/usr/bin/env python3
"""
M-Claude Unified CLI

A single command-line interface for all M-Claude operations.

Usage:
    m-claude sync              Sync conversation logs and generate journals
    m-claude search <query>    Search conversations
    m-claude stats             Generate statistics report
    m-claude convert           Convert JSONL to markdown
    m-claude journals          Generate journal entries
    m-claude redact            Run gitleaks redaction on staged files
    m-claude hooks install     Install git hooks
    m-claude config            Show current configuration

Examples:
    m-claude sync
    m-claude search "docker" --from 2025-12-01
    m-claude stats --output custom-stats.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

# Add scripts directory to path for imports
_scripts_dir = Path(__file__).parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from config import get_paths, get_platform, setup_logging


# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"


# =============================================================================
# SUBCOMMAND HANDLERS
# =============================================================================

def cmd_sync(args: argparse.Namespace) -> int:
    """Handle 'sync' subcommand."""
    from sync_raw_logs import main as sync_main

    try:
        sync_main()
        return 0
    except Exception as e:
        print(f"Error during sync: {e}")
        return 1


def cmd_search(args: argparse.Namespace) -> int:
    """Handle 'search' subcommand."""
    from search import search_conversations, format_result, parse_timestamp
    from datetime import datetime

    logger = setup_logging("m-claude.search")

    # Parse dates
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

    if args.date_from:
        try:
            date_from = datetime.fromisoformat(args.date_from)
        except ValueError:
            print(f"Invalid date format: {args.date_from}. Use YYYY-MM-DD")
            return 1

    if args.date_to:
        try:
            date_to = datetime.fromisoformat(args.date_to)
        except ValueError:
            print(f"Invalid date format: {args.date_to}. Use YYYY-MM-DD")
            return 1

    # Perform search
    results = search_conversations(
        query=args.query,
        date_from=date_from,
        date_to=date_to,
        tool_filter=args.tool,
        limit=args.limit,
    )

    # Display results
    if args.json:
        import json

        print(json.dumps([r["message"] for r in results], indent=2))
    else:
        print(f"\n🔍 Found {len(results)} results for '{args.query}'")
        if results:
            for result in results:
                print(format_result(result, show_full=args.full))
        else:
            print("\nNo results found.")

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Handle 'stats' subcommand."""
    from generate_stats import analyze_conversations, generate_markdown_report

    paths = get_paths()
    logger = setup_logging("m-claude.stats")

    logger.info("Analyzing conversations...")
    stats = analyze_conversations()

    logger.info("Generating report...")
    report = generate_markdown_report(stats)

    # Write to file
    output_path = paths.repo_root / args.output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ Statistics report generated: {output_path}")
    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    """Handle 'convert' subcommand."""
    from convert_to_markdown import main as convert_main

    try:
        convert_main()
        return 0
    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1


def cmd_journals(args: argparse.Namespace) -> int:
    """Handle 'journals' subcommand."""
    from generate_journals import main as journals_main

    try:
        journals_main()
        return 0
    except Exception as e:
        print(f"Error generating journals: {e}")
        return 1


def cmd_redact(args: argparse.Namespace) -> int:
    """Handle 'redact' subcommand."""
    from redact_gitleaks_secrets import main as redact_main

    return redact_main()


def cmd_hooks(args: argparse.Namespace) -> int:
    """Handle 'hooks' subcommand."""
    if args.hooks_action == "install":
        from hooks.install import main as install_main

        install_main()
        return 0
    else:
        print(f"Unknown hooks action: {args.hooks_action}")
        return 1


def cmd_config(args: argparse.Namespace) -> int:
    """Handle 'config' subcommand - show current configuration."""
    paths = get_paths()
    platform_info = get_platform()

    print("=" * 60)
    print("M-Claude Configuration")
    print("=" * 60)
    print()

    print("Platform:")
    print(f"  System:     {platform_info.display_name()}")
    print()

    print("Paths:")
    print(f"  Repository: {paths.repo_root}")
    print(f"  Archives:   {paths.archives}")
    print(f"  Journals:   {paths.journals}")
    print(f"  Scripts:    {paths.scripts}")
    print(f"  Chat Logs:  {paths.chat_logs}")
    print()

    print("Claude Code Projects:")
    project_dirs = paths.get_claude_project_dirs()
    if project_dirs:
        for pdir in project_dirs:
            jsonl_count = len(list(pdir.glob("*.jsonl")))
            print(f"  {pdir.name}: {jsonl_count} conversations")
    else:
        print("  (none found)")
    print()

    print("Directory Status:")
    for name, path in [
        ("Archives", paths.archives),
        ("Journals", paths.journals),
        ("Chat Logs", paths.chat_logs),
    ]:
        status = "✅ exists" if path.exists() else "❌ missing"
        print(f"  {name}: {status}")

    print()
    print("=" * 60)
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    """Handle 'version' subcommand."""
    print(f"m-claude version {__version__}")
    return 0


# =============================================================================
# ARGUMENT PARSER
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="m-claude",
        description="M-Claude: Claude Code conversation management toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  m-claude sync                          Sync logs and generate journals
  m-claude search "docker"               Search for 'docker' in conversations
  m-claude search "test" --tool Bash     Search for 'test' in Bash commands
  m-claude stats                         Generate statistics report
  m-claude config                        Show current configuration
        """,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        description="Available commands",
    )

    # sync
    sync_parser = subparsers.add_parser(
        "sync",
        help="Sync conversation logs and generate journals",
        description="Sync raw conversation logs from Claude Code and generate daily journal entries.",
    )
    sync_parser.set_defaults(func=cmd_sync)

    # search
    search_parser = subparsers.add_parser(
        "search",
        help="Search conversations",
        description="Full-text search across all conversation logs.",
    )
    search_parser.add_argument("query", help="Search query string")
    search_parser.add_argument(
        "--from",
        dest="date_from",
        help="Filter from date (YYYY-MM-DD)",
    )
    search_parser.add_argument(
        "--to",
        dest="date_to",
        help="Filter to date (YYYY-MM-DD)",
    )
    search_parser.add_argument(
        "--tool",
        help="Filter by tool name (Bash, Read, Write, etc.)",
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum results (default: 50)",
    )
    search_parser.add_argument(
        "--full",
        action="store_true",
        help="Show full content (not truncated)",
    )
    search_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    search_parser.set_defaults(func=cmd_search)

    # stats
    stats_parser = subparsers.add_parser(
        "stats",
        help="Generate statistics report",
        description="Analyze conversations and generate a statistics dashboard.",
    )
    stats_parser.add_argument(
        "--output",
        default="STATS.md",
        help="Output file path (default: STATS.md)",
    )
    stats_parser.set_defaults(func=cmd_stats)

    # convert
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert JSONL to chronological markdown",
        description="Convert all conversation logs to a single markdown file.",
    )
    convert_parser.set_defaults(func=cmd_convert)

    # journals
    journals_parser = subparsers.add_parser(
        "journals",
        help="Generate journal entries",
        description="Generate daily journal entries from conversation logs.",
    )
    journals_parser.set_defaults(func=cmd_journals)

    # redact
    redact_parser = subparsers.add_parser(
        "redact",
        help="Run gitleaks redaction on staged files",
        description="Scan staged files with gitleaks and auto-redact detected secrets.",
    )
    redact_parser.set_defaults(func=cmd_redact)

    # hooks
    hooks_parser = subparsers.add_parser(
        "hooks",
        help="Manage git hooks",
        description="Install and manage git hooks for M-Claude.",
    )
    hooks_subparsers = hooks_parser.add_subparsers(
        dest="hooks_action",
        title="hooks actions",
    )
    hooks_install = hooks_subparsers.add_parser(
        "install",
        help="Install git hooks",
    )
    hooks_parser.set_defaults(func=cmd_hooks)

    # config
    config_parser = subparsers.add_parser(
        "config",
        help="Show current configuration",
        description="Display current M-Claude configuration and paths.",
    )
    config_parser.set_defaults(func=cmd_config)

    return parser


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if hasattr(args, "func"):
        return args.func(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
