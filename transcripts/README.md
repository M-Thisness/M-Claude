# Full Conversation Transcripts

This directory contains complete conversation transcripts from Claude Code sessions.

## Contents

Each `.txt` file is a full transcript of a conversation session, named by session ID.

**Total Transcripts:** 28
**Total Size:** ~760KB
**Date Range:** December 23, 2024 - December 31, 2024

## Format

Each transcript contains:
- Complete user prompts and Claude's responses
- Tool usage and function calls
- Command outputs and results
- File contents that were read or modified
- Error messages and debugging information
- System reminders and context

## Finding Specific Sessions

Refer to the main `claude_code_chat_history_export.md` file for a chronological index of sessions with:
- Session IDs
- Timestamps
- User prompts summary
- Topics covered

## Privacy Note

⚠️ These transcripts may contain:
- System file paths
- Directory structures
- Configuration details
- Personal workflow information

This repository is **PRIVATE** for this reason. Do not make it public without thorough review.

## File Naming

Files are named by session UUID from Claude Code's internal tracking:
```
<session-uuid>.txt
```

Example: `0300ad9d-25f5-4e67-8fb7-bcee5f9000a5.txt`

## Viewing Transcripts

**In terminal:**
```bash
cat transcripts/SESSION-ID.txt | less
```

**With syntax highlighting:**
```bash
bat transcripts/SESSION-ID.txt
```

**Search across all transcripts:**
```bash
grep -r "search term" transcripts/
```

---

**Last Updated:** December 31, 2024
**Source:** `~/.claude/debug/`
