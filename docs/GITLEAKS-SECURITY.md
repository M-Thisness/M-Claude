# Gitleaks Security Configuration

**Date:** January 12, 2026
**Purpose:** Prevent secrets and credentials from being committed to the repository
**Status:** ✅ Fully Configured and Active

---

## Overview

Gitleaks is a SAST (Static Application Security Testing) tool that scans git repositories for secrets, passwords, API keys, and other sensitive information. This repository has been hardened with comprehensive gitleaks protection.

### What's Protected

- 🔐 API keys (Anthropic, OpenAI, GitHub, AWS, Google, etc.)
- 🔑 Authentication tokens (OAuth, JWT, PAT)
- 🗝️ Private keys (SSH, PGP, RSA, etc.)
- 🔒 Passwords and credentials
- 🌐 Webhook URLs
- 💳 Payment service tokens (Stripe, PayPal, etc.)
- 📧 Email service keys (SendGrid, Mailgun, etc.)

---

## Configuration Files

### 1. `.gitleaks.toml`

**Location:** Repository root
**Purpose:** Defines scanning rules, allowlists, and custom patterns

**Key Features:**
- ✅ Extended from default gitleaks rules
- ✅ Custom rules for 30+ service providers
- ✅ Allowlists for test files and false positives
- ✅ Entropy-based detection (min: 3.5, max: 7.0)
- ✅ Regex patterns for common secret formats

**Allowlisted Paths:**
```
- tests/**              # Test files
- CHAT_LOGS/**          # Chat logs (may contain examples)
- docs/*.md             # Documentation
- *.example, *.sample   # Example/template files
```

### 2. `.git/hooks/pre-commit`

**Location:** `.git/hooks/pre-commit`
**Purpose:** Automatic secret scanning before each commit

**Behavior:**
- 🚫 Blocks commits containing secrets
- ✅ Only scans staged files (fast)
- 📋 Provides clear remediation instructions
- ⚠️ Can be bypassed with `--no-verify` (use with caution)

### 3. `.github/workflows/gitleaks.yml`

**Location:** `.github/workflows/gitleaks.yml`
**Purpose:** Continuous security scanning via GitHub Actions

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Weekly scheduled scan (Mondays at 9 AM UTC)
- Manual workflow dispatch

**Features:**
- 📊 Uploads scan reports as artifacts
- 💬 Comments on PRs when secrets detected
- 📋 Creates security issues for scheduled scans
- 🔄 Scans full history weekly

---

## Usage

### Pre-Commit Hook (Local Development)

The pre-commit hook runs automatically when you commit:

```bash
git add myfile.py
git commit -m "Add new feature"

# Gitleaks will scan automatically
# If secrets found, commit is blocked
```

**Output Example (Success):**
```
🔍 Running gitleaks scan on staged files...
✅ No secrets detected - commit allowed
```

**Output Example (Secrets Found):**
```
🔍 Running gitleaks scan on staged files...
❌ Secrets detected! Commit blocked.

Finding:     secret = "sk-ant-api03-..."
RuleID:      anthropic-api-key
File:        config.py
Line:        42
```

### Manual Scanning

#### Scan Current Branch

```bash
# Scan all uncommitted changes
gitleaks detect --config=.gitleaks.toml --verbose

# Scan entire repository
gitleaks detect --source=. --config=.gitleaks.toml --verbose

# Scan with redaction (masks secrets in output)
gitleaks detect --config=.gitleaks.toml --redact
```

#### Scan Staged Files Only

```bash
gitleaks protect --staged --config=.gitleaks.toml --verbose
```

#### Scan Specific Files

```bash
gitleaks detect --config=.gitleaks.toml --verbose --log-opts="myfile.py"
```

#### Scan Git History

```bash
# Scan all commits in history
gitleaks detect --config=.gitleaks.toml --verbose --log-opts="--all"

# Scan specific commit range
gitleaks detect --config=.gitleaks.toml --log-opts="abc123..def456"

# Scan last 10 commits
gitleaks detect --config=.gitleaks.toml --log-opts="-10"
```

### GitHub Actions

Scans run automatically on:
- Every push to `main`/`develop`
- Every pull request
- Weekly (scheduled)
- Manual trigger via Actions tab

**View Results:**
1. Go to repository on GitHub
2. Click "Actions" tab
3. Select "Gitleaks Security Scan" workflow
4. View results and download reports

---

## Handling Findings

### Real Secrets (CRITICAL)

If gitleaks detects a **real secret**:

1. **DO NOT commit the code**
2. **Remove the secret immediately**
3. **Rotate/revoke the exposed credential**
4. **Use environment variables or secrets management:**

   ```python
   # ❌ BAD - Hardcoded secret
   API_KEY = "sk-ant-api03-abc123..."

   # ✅ GOOD - Environment variable
   import os
   API_KEY = os.getenv("ANTHROPIC_API_KEY")
   ```

5. **Update `.gitignore` if needed:**
   ```
   .env
   .env.local
   secrets/
   *.pem
   *.key
   ```

6. **If already committed, remove from history:**
   ```bash
   # Option 1: BFG Repo Cleaner (recommended)
   bfg --replace-text passwords.txt

   # Option 2: git-filter-repo
   git filter-repo --path path/to/file --invert-paths
   ```

### False Positives

If gitleaks detects a **false positive** (test data, examples):

#### Option 1: Update `.gitleaks.toml` Allowlist

```toml
[allowlist]
paths = [
    '''path/to/test/file\.py''',
]

regexes = [
    '''sk-test-example''',  # Test API key pattern
]
```

#### Option 2: Inline Comment

Add a comment to suppress the finding:

```python
# gitleaks:allow
API_KEY = "sk-test-example-not-real"
```

#### Option 3: Bypass Pre-Commit (Use Sparingly)

```bash
git commit --no-verify -m "Commit message"
```

⚠️ **Warning:** Only use `--no-verify` when absolutely certain the findings are false positives.

---

## Detected Secret Types

Gitleaks scans for 60+ secret patterns including:

### Cloud Providers
- AWS Access Keys (AKIA...)
- Google API Keys (AIza...)
- Azure Credentials
- Heroku API Keys

### AI/ML Services
- **Anthropic/Claude API Keys** (`sk-ant-api03-...`)
- **OpenAI API Keys** (`sk-...`)
- Hugging Face tokens

### Version Control
- **GitHub Personal Access Tokens** (`ghp_...`, `github_pat_...`)
- GitHub OAuth tokens (`gho_...`)
- GitLab tokens

### Communication
- Slack tokens (`xox...`)
- Slack webhooks
- Discord bot tokens
- Twilio API keys

### Payment Services
- Stripe API keys (`sk_live_...`)
- PayPal credentials
- Square tokens

### Email Services
- SendGrid API keys
- Mailgun API keys
- Mailchimp credentials

### Infrastructure
- SSH Private Keys
- Database connection strings
- JWT tokens
- Generic API keys (entropy-based detection)

---

## Configuration Customization

### Add New Secret Pattern

Edit `.gitleaks.toml`:

```toml
[[rules]]
id = "my-custom-api-key"
description = "My Custom Service API Key"
regex = '''(?i)(myservice_[a-zA-Z0-9]{32})'''
keywords = ["myservice_"]
entropy = 4.0
```

### Add Path to Allowlist

```toml
[allowlist]
paths = [
    '''new/path/to/ignore/.*''',
]
```

### Adjust Entropy Threshold

```toml
[entropy]
min = 3.0  # Lower = more sensitive (more false positives)
max = 7.0  # Higher = less sensitive (may miss secrets)
```

### Disable Specific Rule

```toml
[[rules]]
id = "rule-to-disable"
description = "Rule Description"
[rules.allowlist]
regexes = [
    '''.*''',  # Matches everything, effectively disabling rule
]
```

---

## Best Practices

### 1. Never Commit Secrets
- ✅ Use environment variables
- ✅ Use secrets management (1Password, Vault, AWS Secrets Manager)
- ✅ Use `.env` files (and gitignore them)
- ❌ Never hardcode credentials

### 2. Use Separate Keys for Environments
- Development: `sk-ant-api03-dev-...`
- Staging: `sk-ant-api03-staging-...`
- Production: `sk-ant-api03-prod-...`

### 3. Rotate Keys Regularly
- Set expiration dates
- Rotate every 90 days
- Rotate immediately if exposed

### 4. Limit Key Permissions
- Use least-privilege principle
- Scope API keys to specific resources
- Use read-only keys when possible

### 5. Monitor and Audit
- Review gitleaks reports weekly
- Check GitHub Actions results
- Audit access logs for API keys

### 6. Educate Team
- Train developers on secret management
- Document proper practices
- Review code for secrets in PRs

---

## Troubleshooting

### Hook Not Running

**Problem:** Pre-commit hook doesn't execute

**Solution:**
```bash
# Ensure hook is executable
chmod +x .git/hooks/pre-commit

# Verify hook exists
ls -la .git/hooks/pre-commit

# Test hook manually
.git/hooks/pre-commit
```

### Too Many False Positives

**Problem:** Gitleaks flags legitimate test data

**Solution:**
1. Add specific patterns to `.gitleaks.toml` allowlist
2. Use `# gitleaks:allow` comments
3. Adjust entropy thresholds
4. Move test data to allowlisted directories

### GitHub Action Failing

**Problem:** Workflow fails unexpectedly

**Solution:**
```bash
# Test locally first
gitleaks detect --config=.gitleaks.toml --verbose

# Check workflow logs on GitHub
# Actions > Gitleaks Security Scan > Select failed run

# Verify .gitleaks.toml is committed
git ls-files | grep gitleaks.toml
```

### Need to Bypass Hook Temporarily

**Problem:** Need to commit urgently with false positive

**Solution:**
```bash
# Bypass pre-commit hook (use responsibly)
git commit --no-verify -m "Commit message"

# OR set environment variable
SKIP_GITLEAKS=1 git commit -m "Commit message"
```

⚠️ **Important:** Always fix the underlying issue after bypassing.

---

## Emergency Response: Secret Exposed

If a secret was accidentally committed and pushed:

### Immediate Actions (Within 1 hour)

1. **Rotate the Exposed Secret Immediately**
   - Revoke/delete the exposed API key
   - Generate new credentials
   - Update all systems using the old secret

2. **Remove from Git History**
   ```bash
   # Using BFG Repo-Cleaner (recommended)
   java -jar bfg.jar --replace-text secrets.txt .git
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive

   # Force push (⚠️ coordinate with team)
   git push --force --all
   git push --force --tags
   ```

3. **Notify Team**
   - Alert all team members
   - Ensure everyone pulls latest changes
   - Document incident

4. **Monitor for Abuse**
   - Check API usage logs
   - Review access logs
   - Monitor for unusual activity

5. **Investigate Root Cause**
   - How did secret get committed?
   - Update processes to prevent recurrence
   - Consider additional training

### Within 24 Hours

6. **Audit All Credentials**
   - Review all API keys
   - Check for other exposed secrets
   - Verify principle of least privilege

7. **Update Documentation**
   - Document incident
   - Update security procedures
   - Create post-mortem report

8. **Enhance Prevention**
   - Add patterns to `.gitleaks.toml`
   - Implement additional pre-commit checks
   - Schedule team training

---

## Performance Considerations

### Pre-Commit Hook
- **Speed:** ~1-5 seconds for typical commits
- **Impact:** Minimal - only scans staged files
- **Optimization:** Use `--staged` flag (already configured)

### GitHub Actions
- **Speed:** ~30 seconds to 2 minutes
- **Impact:** Runs in parallel, doesn't block development
- **Optimization:**
  - Scans only on relevant branches
  - Caches dependencies
  - Parallel execution

### Large Repositories
```bash
# For repositories with extensive history
# Limit scan depth
gitleaks detect --log-opts="--max-count=1000"

# Or scan specific time range
gitleaks detect --log-opts="--since='2024-01-01'"
```

---

## Maintenance

### Weekly Tasks
- ✅ Review GitHub Actions scan results
- ✅ Update allowlist for new false positives
- ✅ Check for gitleaks updates

### Monthly Tasks
- ✅ Audit `.gitleaks.toml` configuration
- ✅ Review and rotate API keys
- ✅ Update custom rules as needed

### Quarterly Tasks
- ✅ Full history scan
- ✅ Team security training refresher
- ✅ Review and update documentation

### Update Gitleaks

```bash
# Update via Homebrew
brew upgrade gitleaks

# Verify version
gitleaks version

# Test after update
gitleaks detect --config=.gitleaks.toml --verbose
```

---

## Integration with CI/CD

### Pre-Commit Hook (Local)
- Runs before every commit
- Fast feedback loop
- Prevents secrets from entering history

### GitHub Actions (CI)
- Runs on push/PR
- Catches anything that bypassed pre-commit
- Provides team visibility

### Scheduled Scans
- Weekly full history scan
- Catches secrets from before gitleaks was implemented
- Creates issues for tracking

**Defense in Depth:** Multiple layers ensure comprehensive protection.

---

## Additional Resources

### Official Documentation
- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [Gitleaks Configuration Guide](https://github.com/gitleaks/gitleaks#configuration)
- [GitHub Secrets Scanning](https://docs.github.com/en/code-security/secret-scanning)

### Secret Management Tools
- [1Password Secrets Automation](https://developer.1password.com/)
- [HashiCorp Vault](https://www.vaultproject.io/)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Google Secret Manager](https://cloud.google.com/secret-manager)

### Git History Cleaning
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [git-filter-repo](https://github.com/newren/git-filter-repo)
- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

### Security Best Practices
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_CheatSheet.html)
- [CIS Benchmark for Secret Management](https://www.cisecurity.org/)

---

## Support and Issues

### Getting Help

**Local Issues:**
```bash
# Check gitleaks version
gitleaks version

# View help
gitleaks detect --help
gitleaks protect --help

# Enable verbose logging
gitleaks detect --verbose --config=.gitleaks.toml
```

**GitHub Actions Issues:**
- Check workflow logs in Actions tab
- Verify `.gitleaks.toml` is committed
- Ensure gitleaks-action version is current

**Questions or Improvements:**
- Create an issue in the repository
- Tag with `security` and `gitleaks` labels
- Include relevant error messages and logs

---

## Summary

✅ **Gitleaks is fully configured and active**

**Protection Layers:**
1. 🔒 Pre-commit hook (local enforcement)
2. 🔒 GitHub Actions (CI enforcement)
3. 🔒 Weekly scheduled scans (historical audit)
4. 🔒 Custom rules for 60+ secret types
5. 🔒 Comprehensive allowlists for false positives

**Your repository is now hardened against accidental secret exposure.**

---

**Last Updated:** January 12, 2026
**Gitleaks Version:** 8.30.0
**Configuration Version:** 1.0
