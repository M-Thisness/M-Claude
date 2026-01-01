# Setup Guide

## Installing Claude Code

Claude Code is Anthropic's official CLI tool for interacting with Claude.

### Prerequisites

- Linux, macOS, or Windows
- Terminal access
- GitHub account (optional, for GitHub integration)

### Installation

Follow the official installation guide at: https://github.com/anthropics/claude-code

## Viewing Markdown Files

### Install glow (recommended)

**Arch Linux / CachyOS:**
```bash
sudo pacman -S glow
```

**Other systems:**
See https://github.com/charmbracelet/glow

**Usage:**
```bash
glow file.md                    # Simple view
glow -p file.md                 # Pager mode (scrollable)
glow -s dark file.md            # Dark theme
glow -w 120 file.md             # Custom width
```

## GitHub CLI Setup

### Install gh

**Arch Linux / CachyOS:**
```bash
sudo pacman -S github-cli
```

### Authenticate

```bash
gh auth login
```

Follow the prompts to authenticate via web browser.

### Verify Authentication

```bash
gh auth status
```

## Repository Management

### Clone this repository

```bash
gh repo clone mischa-thisness/M-Claude-Code
```

### Update chat history

1. Export new history:
```bash
# Run the export script or create new export
```

2. Commit changes:
```bash
git add .
git commit -m "Update chat history - $(date +%Y-%m-%d)"
git push
```

## Backup Strategy

### Automated Backup Script

Create a backup script to regularly export Claude Code history:

```bash
#!/bin/bash
BACKUP_DIR=~/M-Claude-Code
DATE=$(date +%Y%m%d)

# Copy latest history
cp ~/.claude/history.jsonl $BACKUP_DIR/backups/history_$DATE.jsonl

# Create transcript archive
tar -czf $BACKUP_DIR/backups/transcripts_$DATE.tar.gz ~/.claude/debug/

echo "Backup complete: $DATE"
```

### Scheduled Backups

Add to crontab for weekly backups:
```bash
0 0 * * 0 ~/M-Claude-Code/scripts/backup.sh
```
