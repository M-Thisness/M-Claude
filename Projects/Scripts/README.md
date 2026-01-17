# M-Claude Scripts

Utility scripts for the M-Claude repository.

## Scripts

### `redact_gitleaks_secrets.py`

Automatically redacts secrets detected by gitleaks in staged files.

**Features:**
- Scans staged files using gitleaks (MAX STRICT MODE)
- Parses JSON findings and redacts individual secrets
- Re-stages modified files
- Non-blocking (allows commits to proceed)

**Usage:**
```bash
# Runs automatically in pre-commit hook
git commit -m "message"

# Manual execution
python3 Projects/Scripts/redact_gitleaks_secrets.py
```

**Documentation:** See [Docs/GITLEAKS-AUTO-REDACTION.md](../../Docs/GITLEAKS-AUTO-REDACTION.md)

---

### `sync_raw_logs.py`

Syncs Claude CLI conversation logs and converts them to journal entries.

**Features:**
- Syncs conversations from Claude CLI
- Converts to journal markdown format
- Runs automatically before each commit

**Usage:**
```bash
# Runs automatically in pre-commit hook
git commit -m "message"

# Manual execution
python3 Projects/Scripts/sync_raw_logs.py
```

---

### `hooks/pre-commit`

Git pre-commit hook that runs:
1. Gitleaks secret scanning with auto-redaction
2. Conversation sync and journal conversion

**Installation:**
```bash
# Recommended
python3 Projects/Scripts/hooks/install.py

# Manual
cp Projects/Scripts/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Documentation:** See [Docs/GITLEAKS-AUTO-REDACTION.md](../../Docs/GITLEAKS-AUTO-REDACTION.md)

---

### `hooks/install.py`

Installer script for git hooks.

**Usage:**
```bash
python3 Projects/Scripts/hooks/install.py
```

Copies `hooks/pre-commit` to `.git/hooks/pre-commit` and makes it executable.

---

## Testing

### Test Gitleaks Redaction

```bash
python3 tests/test_gitleaks_redaction.py
```

Runs comprehensive tests for the auto-redaction functionality.

---

## Requirements

- Python 3.6+
- gitleaks (optional, will warn if not installed)
  - Install: `brew install gitleaks`

---

## Related Documentation

- [GITLEAKS-AUTO-REDACTION.md](../../Docs/GITLEAKS-AUTO-REDACTION.md) - Auto-redaction feature
- [GITLEAKS-MAX-STRICT.md](../../Docs/GITLEAKS-MAX-STRICT.md) - Max strict mode config
- [GITLEAKS-SECURITY.md](../../Docs/GITLEAKS-SECURITY.md) - Security overview
