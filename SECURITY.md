# Security Policy

## 🔐 Cosmic Security Posture

This repository implements **defense-in-depth** security with multiple automated scanning layers.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **DO NOT** create a public GitHub issue
2. Email the maintainer directly with details
3. Allow 48 hours for initial response
4. Provide sufficient information to reproduce

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested remediation (if any)

## Security Measures

### Automated Scanning

| Layer | Tools | Frequency |
|-------|-------|-----------|
| **Secrets** | Gitleaks, TruffleHog, detect-secrets | Every push |
| **Dependencies** | pip-audit, Safety, OSV-Scanner | Daily |
| **SAST** | Semgrep, Bandit, CodeQL | Weekly + PR |
| **Repository** | OpenSSF Scorecard | Weekly |

### Pre-commit Hooks

Local development includes:
- Gitleaks secret scanning
- PII pattern detection
- Credential leak prevention

### Data Protection

- All sensitive data automatically redacted before commit
- File paths with usernames sanitized
- API keys and tokens stripped from logs

## Acknowledgments

Security researchers who responsibly disclose vulnerabilities will be credited (with permission) in release notes.
