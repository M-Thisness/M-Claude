# M-Claude

Claude Code conversation archive with automated processing, security scanning, and daily journals.

**System:** Lenovo Legion Pro 7 | CachyOS (Arch) | COSMIC Desktop
**Repository:** https://github.com/M-Thisness/M-Claude

## Repository Structure

```
M-Claude/
├── CHAT_LOG.md              # Chronological transcript (6,014 messages, 31K lines)
├── CHAT_LOGS/               # Raw JSONL conversations (114 files, 13MB)
├── CHAT_LOGS-markdown/      # Individual markdown transcripts (110 files)
├── journals/                # Daily summaries (13 days)
├── scripts/                 # Automation & processing
│   ├── sync_raw_logs.py
│   ├── convert_to_markdown.py
│   ├── generate_journals.py
│   └── secure-boot/         # rEFInd + Secure Boot setup
└── docs/                    # Technical documentation
    ├── SECURE-BOOT-SETUP.md
    ├── M-SECURITY.md
    ├── HARDENING-APPLIED.md
    ├── SECURITY.md
    └── SETUP.md
```

## Quick Start

**View chronological transcript:**
```bash
glow CHAT_LOG.md
```

**View daily journals:**
```bash
glow journals/2026-01-09.md
```

**Sync latest conversations:**
```bash
python3 scripts/sync_raw_logs.py       # Copy & redact from ~/.claude
python3 scripts/convert_to_markdown.py # Generate CHAT_LOG.md
python3 scripts/generate_journals.py   # Generate daily journals
```

## Statistics

- **114 conversations** (Dec 6, 2025 - Jan 10, 2026)
- **6,014 messages** in chronological log
- **13MB** raw JSONL data (redacted)
- **13 daily journals**
- **110 markdown transcripts**

## Key Projects Documented

### System Configuration
- **Secure Boot setup** for rEFInd + CachyOS (sbctl, shim, MOK)
- **System hardening** (LUKS encryption, firewall, ASLR, seccomp)
- **Security analysis** (hardware, kernel, network stack)

### Development
- **COSMIC power monitor applet** (Rust, libcosmic, iced)
- **Chat log automation** (Python, JSONL parsing, GitHub Actions)
- **Git security hooks** (gitleaks, PII detection, credential scanning)

## Security Features

### Pre-commit Hook (3-Layer)
1. **Gitleaks** - API keys, tokens, credentials
2. **PII Detection** - Emails, phones, SSN, IPs
3. **Pattern Matching** - Custom blocked strings (`~/.config/git_hooks/blocked_patterns.txt`)

### Automatic Redaction
- API keys & auth tokens (OpenAI, GitHub, AWS, Slack, Stripe, etc.)
- Email addresses & phone numbers
- IP addresses & UUIDs
- File paths containing usernames
- Custom blocked patterns

**All redaction occurs during sync** - source files in `~/.claude` remain unmodified.

## Claude Code Data Locations

```
~/.claude/
├── projects/-home-mischa/*.jsonl  # Full conversation transcripts
├── history.jsonl                   # User prompts index
├── debug/*.txt                     # Debug logs
└── settings.local.json            # Settings & permissions
```

## Scripts

**sync_raw_logs.py**
- Copies from `~/.claude/projects/-home-mischa/`
- Applies comprehensive redaction (API keys, PII, custom patterns)
- Outputs to `CHAT_LOGS/`

**convert_to_markdown.py**
- Loads all JSONL files
- Sorts chronologically by timestamp
- Generates single `CHAT_LOG.md` transcript
- Formats with session headers

**generate_journals.py**
- Groups conversations by date
- Creates daily summaries with timestamps
- Lists files modified and actions taken
- Outputs to `journals/YYYY-MM-DD.md`

## GitHub Actions

Workflow: `.github/workflows/generate-markdown.yml`

**Triggers:** Push to `CHAT_LOGS/*.jsonl`

**Actions:**
1. Run `convert_to_markdown.py`
2. Commit regenerated `CHAT_LOG.md`
3. Push to `main`

## Documentation

- **[SECURE-BOOT-SETUP.md](docs/SECURE-BOOT-SETUP.md)** - rEFInd + sbctl configuration
- **[M-SECURITY.md](docs/M-SECURITY.md)** - System security analysis
- **[HARDENING-APPLIED.md](docs/HARDENING-APPLIED.md)** - Applied hardening measures
- **[SECURITY.md](docs/SECURITY.md)** - Repository security features
- **[SETUP.md](docs/SETUP.md)** - Setup guide

## License

MIT License - See [LICENSE](LICENSE)

---

*Last sync: 2026-01-09 | All sensitive data redacted*
