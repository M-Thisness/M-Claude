# Setup Guide

## Prerequisites

- Linux/macOS/Windows
- Python 3.11+
- Git
- GitHub CLI (optional)

## Install Claude Code

```bash
# Follow official guide
# https://github.com/anthropics/claude-code
```

## Install Dependencies

**Arch Linux / CachyOS:**
```bash
sudo pacman -S glow github-cli python
```

**Other distros:**
```bash
# glow: https://github.com/charmbracelet/glow
# gh: https://cli.github.com/
```

## Clone Repository

```bash
gh repo clone M-Thisness/M-Claude
# OR
git clone https://github.com/M-Thisness/M-Claude.git
```

## Python Scripts

**No external dependencies required** - uses stdlib only:
- `json`
- `pathlib`
- `datetime`
- `re`

## Sync Workflow

### 1. Copy Latest Conversations

```bash
cd M-Claude
python3 scripts/sync_raw_logs.py
```

**Source:** `~/.claude/projects/-home-mischa/*.jsonl`
**Destination:** `CHAT_LOGS/*.jsonl` (redacted)

### 2. Generate Markdown

```bash
python3 scripts/convert_to_markdown.py
```

**Generates:** `CHAT_LOG.md` (chronological transcript)

### 3. Update Journals

```bash
python3 scripts/generate_journals.py
```

**Generates:** `journals/YYYY-MM-DD.md` (daily summaries)

### 4. Commit & Push

```bash
git add .
git commit -m "Sync chat logs $(date +%Y-%m-%d)"
git push
```

## GitHub Actions

**Workflow:** `.github/workflows/generate-markdown.yml`

**Auto-triggers on:**
- Push to `main` affecting `CHAT_LOGS/*.jsonl`
- Manual workflow dispatch

**Automatic actions:**
1. Runs `convert_to_markdown.py`
2. Commits updated `CHAT_LOG.md`
3. Pushes to repository

## Security Setup

### Install Pre-commit Hook

```bash
# Clone includes .git/hooks/pre-commit
# Ensure it's executable
chmod +x .git/hooks/pre-commit
```

### Install Gitleaks

**Arch Linux / CachyOS:**
```bash
sudo pacman -S gitleaks
```

**Other:**
```bash
# https://github.com/gitleaks/gitleaks
```

### Configure Blocked Patterns

```bash
# Create custom pattern file
mkdir -p ~/.config/git_hooks
echo "sensitive_string" >> ~/.config/git_hooks/blocked_patterns.txt
```

**Hook checks:**
1. Gitleaks scan (API keys, tokens)
2. PII detection (email, phone, SSN, IP)
3. Custom patterns (`~/.config/git_hooks/blocked_patterns.txt`)

## Viewing Markdown

**glow (recommended):**
```bash
glow CHAT_LOG.md              # Simple view
glow -p journals/2026-01-09.md  # Pager mode
glow -s dark file.md          # Dark theme
glow -w 120 file.md           # Custom width
```

**Alternatives:**
- `mdcat`
- `pandoc | lynx -stdin`
- VSCode/VSCodium
- GitHub web interface

## Backup Strategy

### Manual Backup

```bash
# Copy to external storage
rsync -av ~/M-Claude /mnt/backup/

# Create archive
tar -czf M-Claude-$(date +%Y%m%d).tar.gz ~/M-Claude
```

### Automated Backup

**Script:** `~/backup-claude.sh`
```bash
#!/bin/bash
rsync -av ~/.claude/projects/-home-mischa/ ~/M-Claude/backups/raw/
tar -czf ~/backups/M-Claude-$(date +%Y%m%d).tar.gz ~/M-Claude
```

**Crontab (weekly):**
```bash
0 0 * * 0 ~/backup-claude.sh
```

## Troubleshooting

### Permission Issues

```bash
# Fix hook permissions
chmod +x .git/hooks/pre-commit

# Fix script permissions
chmod +x scripts/*.py
```

### JSONL Parse Errors

**Symptom:** `Expecting value: line 1 column X`

**Solution:**
- Corrupted JSONL file in `~/.claude/projects/`
- Check with: `python3 -m json.tool < file.jsonl`
- Skip or repair corrupted files

### GitHub Push Rejected

**Symptom:** `! [rejected] main -> main (fetch first)`

**Solution:**
```bash
git pull --rebase
git push
```

## Development

### Script Locations

```
scripts/
├── sync_raw_logs.py           # Redaction & sync
├── convert_to_markdown.py     # Markdown generation
├── generate_journals.py       # Daily journals
└── secure-boot/
    ├── setup_secureboot_refind.sh
    ├── install_hook.sh
    └── sbctl-pacman-hook.hook
```

### Adding Custom Redaction

Edit `scripts/sync_raw_logs.py`:

```python
REDACTION_PATTERNS = [
    # Add custom patterns
    (r'my_pattern', '[REDACTED_CUSTOM]'),
]
```

### Testing Pre-commit Hook

```bash
# Test without committing
.git/hooks/pre-commit

# Bypass (NOT RECOMMENDED)
git commit --no-verify -m "message"
```

---

*For security features, see [SECURITY.md](SECURITY.md)*
*For Secure Boot setup, see [SECURE-BOOT-SETUP.md](SECURE-BOOT-SETUP.md)*
