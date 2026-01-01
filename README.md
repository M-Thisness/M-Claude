# M-Claude

Personal archive of Claude Code conversations, scripts, and utilities.

## 📂 What's Inside

- **[Transcripts (Markdown)](transcripts-markdown/)** - 52 conversations in beautiful, chat-like format
- **[Transcripts (JSONL)](transcripts/)** - Raw conversation data (55 files, 3.8MB)
- **[Scripts](scripts/)** - Python converter & export utilities
- **[Security Docs](docs/SECURITY.md)** - Multi-layer secret protection setup
- **[System Security Analysis](docs/M-SECURITY.md)** - Complete hardware-to-GitHub security audit
- **[Chat Export](claude_code_chat_history_export.md)** - Chronological summary

## 🚀 Quick Links

**Browse Conversations:**
- [📊 Conversation Index](transcripts-markdown/README.md)
- [🔍 View All Transcripts](transcripts-markdown/)

**Automation:**
- [GitHub Action](.github/workflows/generate-markdown.yml) - Auto-generates markdown from JSONL
- [Conversion Script](scripts/convert_to_markdown.py) - JSONL → Markdown converter

## 💻 Local Usage

**View chat history:**
```bash
glow claude_code_chat_history_export.md
```

**Backup conversations:**
```bash
cp ~/.claude/history.jsonl ~/backup_$(date +%Y%m%d).jsonl
```

**Regenerate markdown:**
```bash
python3 scripts/convert_to_markdown.py
```

## 📍 Claude Code Data Locations

- `~/.claude/history.jsonl` - History index
- `~/.claude/projects/-home-mischa/` - Full transcripts
- `~/.claude/settings.local.json` - Settings

## 🔒 Security

**Repository Protection:**
- Global `.gitignore` for secrets
- [Gitleaks](https://github.com/gitleaks/gitleaks) pre-commit hooks
- GitHub secret scanning

**System Security:**
- [M-SECURITY.md](docs/M-SECURITY.md) - Complete security analysis (legion-cachy → M-Claude)
- [SECURITY.md](docs/SECURITY.md) - Multi-layer secret protection guide

---

**Stats:** 52 conversations • 3.8MB JSONL • Auto-updated via GitHub Actions
**Repository:** https://github.com/mischa-thisness/M-Claude
**Created:** December 31, 2024
