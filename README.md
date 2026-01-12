# M-Claude

Claude Code conversation archive with automated processing, cosmic security, and daily journals.

**System:** Lenovo Legion Pro 7 | CachyOS (Arch) | COSMIC Desktop  
**Repository:** https://github.com/M-Thisness/M-Claude

## Repository Structure

```
M-Claude/
├── Archives/                # Raw JSONL conversations (117 files)
├── Docs/                    # Technical documentation
│   ├── SECURE-BOOT-SETUP.md
│   ├── M-SECURITY.md
│   ├── HARDENING-APPLIED.md
│   └── IMPROVEMENTS.md
├── Journals/                # Daily summaries (14+ days)
├── Projects/
│   ├── Scripts/             # Automation & processing
│   │   ├── sync_raw_logs.py
│   │   ├── convert_to_markdown.py
│   │   └── generate_journals.py
│   ├── Gemini-Slate/        # GL-BE3600 router project
│   └── Tests/               # Test suite
├── CHAT_LOG.md              # Chronological transcript
├── SECURITY.md              # Security policy
└── README.md
```

## Quick Start

```bash
# View chronological transcript
glow CHAT_LOG.md

# View daily journals
glow Journals/2026-01-12.md

# Sync latest conversations
python Projects/Scripts/sync_raw_logs.py
python Projects/Scripts/convert_to_markdown.py
python Projects/Scripts/generate_journals.py
```

## Cosmic Security

**4 GitHub Actions workflows with 18 parallel security jobs:**

| Workflow | Tools |
|----------|-------|
| 🔐 Secret Detection | Gitleaks, TruffleHog, detect-secrets, PII scan |
| 📦 Dependency Audit | pip-audit, Safety, OSV-Scanner, license check |
| 🔬 SAST Analysis | Semgrep, Bandit, CodeQL, Pylint |
| 🛡️ Repo Hardening | OpenSSF Scorecard, commit signatures, sensitive files |

## Key Projects

### Gemini-Slate (`Projects/Gemini-Slate/`)
GL-BE3600 router configuration with WiFi 7, Mullvad VPN, and Blocky DNS.

### Scripts (`Projects/Scripts/`)
Automation for log syncing, markdown generation, and journal creation.

## Statistics

- **117+ conversations** archived
- **6,600+ messages** in chronological log
- **14+ daily journals**
- **Comprehensive redaction** of all sensitive data

## License

MIT License - See [LICENSE](LICENSE)

---

*Cosmic security enabled | All sensitive data redacted*
