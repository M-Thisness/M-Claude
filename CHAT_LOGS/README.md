# Claude Code Raw Conversation Logs

This directory contains redacted raw conversation logs from Claude Code sessions.

**Last Sync:** 2026-01-01 03:20:09

## Format
- Files are in JSONL format (one JSON object per line)
- Each line represents a conversation event (user message, assistant response, tool use, etc.)
- All sensitive data is automatically redacted before syncing

## Redacted Information
The sync script automatically redacts:
- API keys and authentication tokens
- Email addresses
- Phone numbers
- IP addresses
- Private keys
- Database connection strings
- File paths containing usernames
- Other PII and secrets

## Syncing
To sync the latest logs:
```bash
python scripts/sync_raw_logs.py
```

This is automatically triggered by the GitHub Action when changes are pushed.
