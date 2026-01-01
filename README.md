# M-Claude-Code

Personal repository for Claude Code chat history, scripts, and documentation.

## Overview

This repository contains:
- **Chat History**: Complete conversation logs with Claude Code
- **Scripts**: Custom tools and utilities created with Claude Code
- **Documentation**: Notes, guides, and reference materials

## Repository Structure

```
M-Claude-Code/
├── README.md                           # This file
├── claude_code_chat_history_export.md  # Main chat history export
├── scripts/                            # Utility scripts
│   └── export_full_transcripts.sh      # Script to export full conversation transcripts
├── transcripts/                        # Full conversation transcripts (28 files, ~760KB)
└── docs/                               # Additional documentation
```

## Chat History

### Summary Export

The `claude_code_chat_history_export.md` file contains a chronological summary of all interactions with Claude Code, including:
- Session timestamps
- User prompts
- Session IDs for full transcript lookup
- Statistics and topic summaries

### Full Transcripts

The `transcripts/` directory contains complete conversation logs with:
- Full user prompts and Claude's responses
- Tool usage and command outputs
- File contents read or modified
- Error messages and debugging information

See `transcripts/README.md` for details.

### Viewing Chat History

**Terminal (with glow):**
```bash
glow claude_code_chat_history_export.md
```

**In a new terminal window:**
```bash
alacritty -e glow -p claude_code_chat_history_export.md &
```

**Plain text:**
```bash
cat claude_code_chat_history_export.md
```

## Scripts

### export_full_transcripts.sh

Exports complete conversation transcripts from `~/.claude/debug/` into a comprehensive markdown document.

**Usage:**
```bash
./scripts/export_full_transcripts.sh
```

This generates a timestamped export file with all available conversation transcripts.

## Local Claude Code Data

Claude Code stores data in several locations on your system:

- **History Index**: `~/.claude/history.jsonl`
- **Full Transcripts**: `~/.claude/debug/*.txt`
- **File History**: `~/.claude/file-history/`
- **Settings**: `~/.claude/settings.local.json`

## Backup & Export

To create a backup of all Claude Code conversations:

```bash
# Backup history file
cp ~/.claude/history.jsonl ~/claude_history_backup_$(date +%Y%m%d).jsonl

# Backup all transcripts
tar -czf ~/claude_transcripts_backup_$(date +%Y%m%d).tar.gz ~/.claude/debug/
```

## Privacy Notice

This is a **private repository** containing personal chat history and may include:
- System configuration details
- File paths and directory structures
- Personal workflow patterns

Do not make this repository public without reviewing all content first.

## Statistics

**As of Last Update:**
- Total Sessions: 15+
- Total User Prompts: 68+
- Date Range: December 23, 2024 - Present
- Most Active Topics: Cosmic Desktop, System Configuration, Terminal Setup

## Topics Covered

1. Desktop Environment Configuration (Cosmic Desktop)
2. Terminal Customization (Alacritty)
3. System Administration (Shortcuts, Launchers, Admin Access)
4. Audio Troubleshooting
5. UI/Theme Management
6. Browser Integration (Claude for Chrome)
7. Network Diagnostics
8. Security Tools (1Password CLI)

## Updates

This repository is updated periodically with new chat sessions and scripts created with Claude Code.

---

**Created**: December 31, 2024
**Repository**: https://github.com/mischa-thisness/M-Claude-Code
**Visibility**: Private
