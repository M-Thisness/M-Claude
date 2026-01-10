#!/usr/bin/env python3
"""
Generate statistics dashboard from conversations.

Analyzes conversation logs to generate:
- Message count by date
- Tool usage frequency
- File modification tracking
- Session duration statistics
- Activity heatmaps

Usage:
    python scripts/generate_stats.py [--output stats.md]
"""

import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional

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
    except (ValueError, AttributeError, TypeError):
        return None


def extract_tools_from_message(message: Dict[str, Any]) -> List[str]:
    """Extract tool names used in a message."""
    tools = []
    content = message.get('content', [])

    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'tool_use':
                tool_name = item.get('name')
                if tool_name:
                    tools.append(tool_name)

    return tools


def extract_file_paths(message: Dict[str, Any]) -> List[str]:
    """Extract file paths from tool uses."""
    files = []
    content = message.get('content', [])

    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'tool_use':
                tool_input = item.get('input', {})

                # Common file path keys
                for key in ['file_path', 'path', 'notebook_path']:
                    if key in tool_input:
                        files.append(tool_input[key])

    return files


class ConversationStats:
    """Container for conversation statistics."""

    def __init__(self):
        self.total_messages = 0
        self.total_conversations = 0
        self.messages_by_date = defaultdict(int)
        self.messages_by_hour = defaultdict(int)
        self.tool_usage = Counter()
        self.file_modifications = Counter()
        self.session_durations = []
        self.messages_by_role = Counter()
        self.first_message = None
        self.last_message = None


def analyze_conversations() -> ConversationStats:
    """Analyze all conversation files and generate statistics."""
    stats = ConversationStats()

    if not CHAT_LOGS.exists():
        logger.error(f"CHAT_LOGS directory not found: {CHAT_LOGS}")
        return stats

    jsonl_files = sorted(CHAT_LOGS.glob("*.jsonl"))
    logger.info(f"Analyzing {len(jsonl_files)} conversation files...")

    stats.total_conversations = len(jsonl_files)

    for jsonl_file in jsonl_files:
        session_start = None
        session_end = None

        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        message = json.loads(line)
                        stats.total_messages += 1

                        # Track role
                        role = message.get('role', 'unknown')
                        stats.messages_by_role[role] += 1

                        # Parse timestamp
                        timestamp = parse_timestamp(message.get('timestamp'))
                        if timestamp:
                            # Track first/last messages
                            if not stats.first_message or timestamp < stats.first_message:
                                stats.first_message = timestamp
                            if not stats.last_message or timestamp > stats.last_message:
                                stats.last_message = timestamp

                            # Track session duration
                            if not session_start:
                                session_start = timestamp
                            session_end = timestamp

                            # Track by date
                            date_key = timestamp.strftime('%Y-%m-%d')
                            stats.messages_by_date[date_key] += 1

                            # Track by hour
                            stats.messages_by_hour[timestamp.hour] += 1

                        # Extract tools
                        tools = extract_tools_from_message(message)
                        for tool in tools:
                            stats.tool_usage[tool] += 1

                        # Extract file paths
                        files = extract_file_paths(message)
                        for file in files:
                            stats.file_modifications[file] += 1

                    except json.JSONDecodeError:
                        continue

            # Calculate session duration
            if session_start and session_end:
                duration = (session_end - session_start).total_seconds() / 60  # minutes
                stats.session_durations.append(duration)

        except Exception as e:
            logger.error(f"Error reading {jsonl_file.name}: {e}")

    return stats


def generate_markdown_report(stats: ConversationStats) -> str:
    """Generate a markdown statistics report."""
    report = []

    report.append("# M-Claude Conversation Statistics\n")
    report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

    # Overview
    report.append("## 📊 Overview\n")
    report.append(f"- **Total Conversations**: {stats.total_conversations}\n")
    report.append(f"- **Total Messages**: {stats.total_messages:,}\n")

    if stats.first_message and stats.last_message:
        date_range = (stats.last_message - stats.first_message).days
        report.append(f"- **Date Range**: {stats.first_message.strftime('%Y-%m-%d')} to "
                      f"{stats.last_message.strftime('%Y-%m-%d')} ({date_range} days)\n")
        avg_messages_per_day = stats.total_messages / max(date_range, 1)
        report.append(f"- **Average Messages/Day**: {avg_messages_per_day:.1f}\n")

    report.append("\n")

    # Messages by role
    report.append("## 👥 Messages by Role\n")
    for role, count in stats.messages_by_role.most_common():
        percentage = (count / stats.total_messages) * 100
        report.append(f"- **{role.capitalize()}**: {count:,} ({percentage:.1f}%)\n")
    report.append("\n")

    # Tool usage
    report.append("## 🔧 Tool Usage (Top 15)\n")
    if stats.tool_usage:
        total_tool_uses = sum(stats.tool_usage.values())
        for tool, count in stats.tool_usage.most_common(15):
            percentage = (count / total_tool_uses) * 100
            bar = '█' * min(int(percentage / 2), 50)
            report.append(f"- **{tool}**: {count:,} uses ({percentage:.1f}%) {bar}\n")
    else:
        report.append("*No tool usage data*\n")
    report.append("\n")

    # Activity by date
    report.append("## 📅 Activity by Date (Last 30 Days)\n")
    if stats.messages_by_date:
        sorted_dates = sorted(stats.messages_by_date.items(), reverse=True)[:30]
        for date, count in sorted_dates:
            bar = '█' * min(count // 10, 50)
            report.append(f"- **{date}**: {count:,} messages {bar}\n")
    else:
        report.append("*No date data*\n")
    report.append("\n")

    # Activity by hour
    report.append("## 🕐 Activity by Hour of Day\n")
    if stats.messages_by_hour:
        max_count = max(stats.messages_by_hour.values())
        for hour in range(24):
            count = stats.messages_by_hour.get(hour, 0)
            percentage = (count / max_count) * 100 if max_count > 0 else 0
            bar = '█' * min(int(percentage / 2), 50)
            report.append(f"- **{hour:02d}:00**: {count:,} messages {bar}\n")
    else:
        report.append("*No hourly data*\n")
    report.append("\n")

    # Session durations
    if stats.session_durations:
        report.append("## ⏱️  Session Duration Statistics\n")
        avg_duration = sum(stats.session_durations) / len(stats.session_durations)
        max_duration = max(stats.session_durations)
        min_duration = min(stats.session_durations)

        report.append(f"- **Average Session**: {avg_duration:.1f} minutes\n")
        report.append(f"- **Longest Session**: {max_duration:.1f} minutes\n")
        report.append(f"- **Shortest Session**: {min_duration:.1f} minutes\n")
        report.append("\n")

    # File modifications
    report.append("## 📁 Most Modified Files (Top 20)\n")
    if stats.file_modifications:
        for file, count in stats.file_modifications.most_common(20):
            # Shorten long paths
            display_path = file
            if len(display_path) > 80:
                display_path = "..." + display_path[-77:]
            report.append(f"- `{display_path}`: {count} modifications\n")
    else:
        report.append("*No file modification data*\n")
    report.append("\n")

    # Busiest days
    if stats.messages_by_date:
        report.append("## 🔥 Busiest Days (Top 10)\n")
        busiest = sorted(stats.messages_by_date.items(), key=lambda x: x[1], reverse=True)[:10]
        for date, count in busiest:
            report.append(f"- **{date}**: {count:,} messages\n")
        report.append("\n")

    return ''.join(report)


def main():
    """Main entry point for stats generator."""
    parser = argparse.ArgumentParser(
        description='Generate statistics dashboard from conversations'
    )

    parser.add_argument(
        '--output',
        default='STATS.md',
        help='Output file path (default: STATS.md)'
    )

    args = parser.parse_args()

    # Analyze conversations
    logger.info("Analyzing conversations...")
    stats = analyze_conversations()

    # Generate report
    logger.info("Generating report...")
    report = generate_markdown_report(stats)

    # Write to file
    output_path = REPO_ROOT / args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"Statistics report saved to: {output_path}")
    print(f"\n✅ Statistics report generated: {output_path}")


if __name__ == "__main__":
    main()
