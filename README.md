# M-Claude

Personal archive of Claude Code conversations with automated processing, security scanning, and daily journals.

## 📂 Repository Structure

### 📝 Conversations
- **[CHRONOLOGICAL_TRANSCRIPT.md](CHRONOLOGICAL_TRANSCRIPT.md)** - All 66 conversations merged, chronologically ordered (741KB, 3,889 messages)
- **[transcripts/](transcripts/)** - Raw JSONL conversation logs (66 files, 8.4MB) with comprehensive redaction
- **[transcripts-markdown/](transcripts-markdown/)** - Individual markdown files per conversation

### 📔 Daily Journals
- **[journals/](journals/)** - Daily activity summaries organized by date
  - Format: `YYYY-MM-DD.md` (e.g., `2026-01-01.md`)
  - Tweet-length summaries of collaborative work
  - Chronological entries with timestamps
  - Shows files modified and actions taken

### 🛠️ Scripts
- **[sync_raw_logs.py](scripts/sync_raw_logs.py)** - Syncs & redacts conversations from `~/.claude`
- **[convert_to_markdown.py](scripts/convert_to_markdown.py)** - Generates chronological transcript
- **[generate_journals.py](scripts/generate_journals.py)** - Creates daily journal entries

### 📚 Documentation
- **[SECURITY.md](docs/SECURITY.md)** - Multi-layer secret protection setup
- **[SETUP.md](docs/SETUP.md)** - Repository setup guide

## 🔒 Security Features

### Comprehensive Leak Prevention

**Pre-commit Hook (3-Layer Scanning):**
1. **Gitleaks** - Professional secret detection (API keys, tokens, credentials)
2. **PII Detection** - Emails, phones, SSN, credit cards, IP addresses
3. **Credential Scanning** - Hardcoded passwords, DB strings, private keys

**Automatic Redaction in Sync:**
- API keys & authentication tokens (OpenAI, GitHub, AWS, Slack, etc.)
- Email addresses & phone numbers
- SSN patterns & credit card numbers
- IP addresses & JWT tokens
- Database connection strings
- Private keys (PEM format)
- File paths with usernames

**Enforces Best Practices:**
- Environment variables for secrets
- `.env` files (gitignored) for local development
- GitHub Secrets for CI/CD
- Clear error messages when violations detected

## 🚀 Quick Start

### View Conversations

**Browse the complete timeline:**
```bash
glow CHRONOLOGICAL_TRANSCRIPT.md
```

**Read daily journals:**
```bash
glow journals/2026-01-01.md
```

**Browse individual conversations:**
```bash
glow transcripts-markdown/
```

### Sync Latest Conversations

**Manual sync:**
```bash
python scripts/sync_raw_logs.py
```

**Regenerate chronological transcript:**
```bash
python scripts/convert_to_markdown.py
```

**Update journals:**
```bash
python scripts/generate_journals.py
```

### Automatic Updates

The GitHub Action automatically:
1. Triggers when raw logs are pushed to `transcripts/*.jsonl`
2. Regenerates `CHRONOLOGICAL_TRANSCRIPT.md`
3. Commits and pushes the updated transcript

## 📊 Statistics

- **66 conversations** across 6 days (Dec 25, 2025 - Jan 1, 2026)
- **3,889 messages** in chronological transcript
- **8.4MB** raw conversation data (fully redacted)
- **6 daily journals** with activity summaries

## 📍 Claude Code Data Locations

- `~/.claude/projects/-home-mischa/*.jsonl` - Full conversation transcripts
- `~/.claude/history.jsonl` - History index (user prompts only)
- `~/.claude/debug/*.txt` - Debug logs
- `~/.claude/settings.local.json` - Settings & permissions

## 🔧 Development

### Scripts Overview

**sync_raw_logs.py:**
- Syncs from `~/.claude/projects/-home-mischa/`
- Applies comprehensive redaction patterns
- Updates `transcripts/` directory
- Updates README with sync timestamp

**convert_to_markdown.py:**
- Loads all JSONL files
- Sorts messages chronologically
- Generates single `CHRONOLOGICAL_TRANSCRIPT.md`
- Formats with session headers and timestamps

**generate_journals.py:**
- Parses all conversations
- Groups by date
- Creates tweet-length summaries
- Tracks files modified and actions taken
- Outputs to `journals/YYYY-MM-DD.md`

### Pre-commit Hook

Located at `.git/hooks/pre-commit` - runs automatically on every commit:

```bash
# Test the hook
.git/hooks/pre-commit

# Bypass (NOT RECOMMENDED)
git commit --no-verify
```

## 🌐 Repository

**GitHub:** https://github.com/mischa-thisness/M-Claude
**Created:** December 31, 2024
**Auto-updated:** Via GitHub Actions on every push

---

*All sensitive data automatically redacted. Best security practices enforced.*
