#!/usr/bin/env python3
"""
Search functionality for Claude Code conversations.

Provides full-text search across all JSONL conversation files with filtering by:
- Date range
- Tool usage
- File paths mentioned
- Session ID

Usage:
    python scripts/search.py "your query" [--from DATE] [--to DATE] [--tool TOOL]
"""

import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REPO_ROOT = Path(__file__).parent.parent
CHAT_LOGS = REPO_ROOT / "CHAT_LOGS"


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse ISO timestamp string to datetime."""
    try:
        ts = timestamp_str.replace('Z', '+00:00')
        return datetime.fromisoformat(ts)
    except (ValueError, AttributeError, TypeError) as e:
        logger.debug(f"Invalid timestamp: {timestamp_str}: {e}")
        return None


def search_message(message: Dict[str, Any], query: str) -> bool:
    """Check if message contains search query."""
    query_lower = query.lower()

    # Check text content
    content = message.get('content', '')
    if isinstance(content, str) and query_lower in content.lower():
        return True

    # Check list content (tool uses, etc.)
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                # Check tool input/output
                if 'input' in item and query_lower in str(item['input']).lower():
                    return True
                if 'content' in item and query_lower in str(item['content']).lower():
                    return True

    return False


def extract_tool_name(message: Dict[str, Any]) -> Optional[str]:
    """Extract tool name from message if it's a tool use."""
    content = message.get('content', [])
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'tool_use':
                return item.get('name')
    return None


def search_conversations(
    query: str,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    tool_filter: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Search across all conversations.

    Args:
        query: Search query string
        date_from: Filter messages from this date onwards
        date_to: Filter messages up to this date
        tool_filter: Only show messages involving this tool
        limit: Maximum number of results to return

    Returns:
        List of matching messages with metadata
    """
    results = []

    if not CHAT_LOGS.exists():
        logger.error(f"CHAT_LOGS directory not found: {CHAT_LOGS}")
        return results

    jsonl_files = sorted(CHAT_LOGS.glob("*.jsonl"))
    logger.info(f"Searching {len(jsonl_files)} conversation files...")

    for jsonl_file in jsonl_files:
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        message = json.loads(line)

                        # Parse timestamp for filtering
                        timestamp = parse_timestamp(message.get('timestamp'))

                        # Apply date filters
                        if date_from and timestamp and timestamp < date_from:
                            continue
                        if date_to and timestamp and timestamp > date_to:
                            continue

                        # Apply tool filter
                        if tool_filter:
                            tool_name = extract_tool_name(message)
                            if not tool_name or tool_name.lower() != tool_filter.lower():
                                continue

                        # Check if message matches query
                        if search_message(message, query):
                            results.append({
                                'file': jsonl_file.name,
                                'line': line_num,
                                'timestamp': message.get('timestamp', 'Unknown'),
                                'role': message.get('role', 'unknown'),
                                'message': message,
                            })

                            if len(results) >= limit:
                                logger.info(f"Reached result limit ({limit})")
                                return results

                    except json.JSONDecodeError as e:
                        logger.debug(f"Invalid JSON in {jsonl_file.name}:{line_num}: {e}")

        except Exception as e:
            logger.error(f"Error reading {jsonl_file.name}: {e}")

    return results


def format_result(result: Dict[str, Any], show_full: bool = False) -> str:
    """Format a search result for display."""
    timestamp = result['timestamp']
    file = result['file']
    line = result['line']
    role = result['role']

    output = f"\n{'='*80}\n"
    output += f"📍 {file}:{line} | {timestamp} | {role.upper()}\n"
    output += f"{'='*80}\n"

    content = result['message'].get('content', '')

    if isinstance(content, str):
        # Truncate long content unless show_full
        if not show_full and len(content) > 500:
            output += content[:500] + "...\n"
        else:
            output += content + "\n"

    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'tool_use':
                    tool_name = item.get('name', 'Unknown')
                    tool_input = item.get('input', {})
                    output += f"\n🔧 Tool: {tool_name}\n"
                    output += f"Input: {json.dumps(tool_input, indent=2)[:300]}\n"
                elif item.get('type') == 'text':
                    text = item.get('text', '')
                    if not show_full and len(text) > 500:
                        output += text[:500] + "...\n"
                    else:
                        output += text + "\n"

    return output


def main():
    """Main entry point for search CLI."""
    parser = argparse.ArgumentParser(
        description='Search Claude Code conversations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for a specific term
  python scripts/search.py "docker"

  # Search with date range
  python scripts/search.py "pytest" --from 2025-12-25 --to 2025-12-31

  # Search for specific tool usage
  python scripts/search.py "test" --tool Bash

  # Show full content (not truncated)
  python scripts/search.py "error" --full
        """
    )

    parser.add_argument('query', help='Search query string')
    parser.add_argument('--from', dest='date_from', help='Filter from date (YYYY-MM-DD)')
    parser.add_argument('--to', dest='date_to', help='Filter to date (YYYY-MM-DD)')
    parser.add_argument('--tool', help='Filter by tool name (Bash, Read, Write, etc.)')
    parser.add_argument('--limit', type=int, default=50, help='Maximum results (default: 50)')
    parser.add_argument('--full', action='store_true', help='Show full content (not truncated)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')

    args = parser.parse_args()

    # Parse dates
    date_from = None
    date_to = None

    if args.date_from:
        try:
            date_from = datetime.fromisoformat(args.date_from)
        except ValueError:
            logger.error(f"Invalid date format: {args.date_from}. Use YYYY-MM-DD")
            return

    if args.date_to:
        try:
            date_to = datetime.fromisoformat(args.date_to)
        except ValueError:
            logger.error(f"Invalid date format: {args.date_to}. Use YYYY-MM-DD")
            return

    # Perform search
    results = search_conversations(
        query=args.query,
        date_from=date_from,
        date_to=date_to,
        tool_filter=args.tool,
        limit=args.limit
    )

    # Display results
    if args.json:
        # JSON output
        import json
        print(json.dumps([r['message'] for r in results], indent=2))
    else:
        # Formatted output
        print(f"\n🔍 Found {len(results)} results for '{args.query}'")

        if results:
            for result in results:
                print(format_result(result, show_full=args.full))
        else:
            print("\nNo results found.")

    logger.info(f"Search complete. Found {len(results)} results.")


if __name__ == "__main__":
    main()
