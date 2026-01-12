# Security & Secret Protection

This document explains the security measures configured for all GitHub repositories.

## Automated Protection Layers

### 1. GitHub Cloud Protection (All Public Repos)

**✅ Automatically Active:**
- **Secret Scanning**: GitHub scans all public repositories for 200+ secret patterns
- **Partner Alerts**: Immediate notification to service providers when their tokens are detected
- **Automatic Detection**: Scans commits, pull requests, and repository contents

**🔐 Manual Setup Required:**
- **Push Protection**: Visit https://github.com/settings/security_analysis
  - Enable "Push protection for yourself"
  - Prevents pushing commits containing secrets
  - Shows warning and blocks push when secrets detected

**Detected Secret Types:**
- API keys (AWS, Google Cloud, Azure, Stripe, etc.)
- Authentication tokens (GitHub, GitLab, npm, etc.)
- Database credentials
- Private keys (SSH, RSA, PGP)
- OAuth tokens
- Service account credentials
- And 200+ more patterns

### 2. Local Protection (Your Machine)

**✅ Configured:**

#### Global .gitignore (`~/.gitignore_global`)
Automatically prevents common secret files from being staged:
- `.env` files and variants
- API key files (`*api_key*`, `*apikey*`)
- Credential files (`credentials*`, `*secrets*`)
- Private keys (`*.pem`, `*.key`, `id_rsa`)
- Cloud provider configs (`.aws/credentials`, etc.)
- Password files
- Certificates
- And 100+ more patterns

**Location:** `~/.gitignore_global`

#### Gitleaks Pre-commit Hook
Scans every commit before it's created:
- Runs automatically on `git commit`
- Blocks commits containing secrets
- Provides clear error messages
- Can be bypassed with `--no-verify` (not recommended)

**Installed in:**
- `~/.git-templates/hooks/pre-commit` (template for new repos)
- All existing repos need manual installation (see below)

**Test it:**
```bash
cd ~/M-Claude
echo "AWS_SECRET_KEY=AKIAIOSFODNN7EXAMPLE" > test.txt
git add test.txt
git commit -m "test"  # This should be blocked!
rm test.txt
```

### 3. Repository-Specific Protection

Each repository has a `.gitignore` file that prevents sensitive files from being tracked.

## Setup Status

### ✅ Completed Automatically

- [x] Global .gitignore configured
- [x] Gitleaks installed (v8.30.0)
- [x] Pre-commit hook template created
- [x] M-Claude repository has pre-commit hook
- [x] GitHub secret scanning (enabled by default for public repos)

### ⚠️ Requires Manual Action

- [ ] **Enable GitHub Push Protection:**
  1. Visit: https://github.com/settings/security_analysis
  2. Under "Push protection", click "Enable"
  3. Optects all your repositories

- [ ] **Enable Dependabot (Recommended):**
  1. Visit: https://github.com/settings/security_analysis
  2. Enable "Dependency graph"
  3. Enable "Dependabot alerts"
  4. Enable "Dependabot security updates"

## For Future Repositories

### New Repositories
Pre-commit hooks are automatically installed via `~/.git-templates/`

### Existing Repositories
Install the pre-commit hook manually:

```bash
cp ~/.git-templates/hooks/pre-commit /path/to/repo/.git/hooks/pre-commit
chmod +x /path/to/repo/.git/hooks/pre-commit
```

Or use this one-liner:
```bash
find ~/Projects -name ".git" -type d -exec cp ~/.git-templates/hooks/pre-commit {}/hooks/pre-commit \; -exec chmod +x {}/hooks/pre-commit \;
```

## Best Practices

### ✅ DO:
- Use environment variables for secrets
- Use secret management tools (1Password, Bitwarden, etc.)
- Store secrets in `.env` files (which are gitignored)
- Use GitHub Secrets for CI/CD
- Review secret scanning alerts promptly
- Rotate secrets immediately if exposed

### ❌ DON'T:
- Commit API keys, tokens, or passwords
- Store credentials in code
- Use `--no-verify` to bypass pre-commit hooks
- Ignore secret scanning alerts
- Share private repositories publicly without review

## What If I Accidentally Commit a Secret?

### Immediate Actions:

1. **Rotate the Secret Immediately**
   - Generate a new API key/token
   - Revoke the old one
   - Never assume an exposed secret is safe

2. **Remove from Git History**
   ```bash
   # Use BFG Repo-Cleaner or git-filter-repo
   # DO NOT use git filter-branch (deprecated)

   # Install git-filter-repo
   pip install git-filter-repo

   # Remove the secret
   git-filter-repo --path-match secret_file.txt --invert-paths

   # Force push (requires coordination with team)
   git push --force
   ```

3. **Contact GitHub Support** (for serious exposures)
   - They can help with cache purging
   - Can expedite partner notifications

## Testing Your Protection

### Test Local Protection:
```bash
# Create a test repo
mkdir ~/test-repo && cd ~/test-repo
git init

# Try to commit a secret
echo "password=SuperSecret123" > config.txt
git add config.txt
git commit -m "test"
# Should be blocked by gitleaks!

# Cleanup
cd ~ && rm -rf ~/test-repo
```

### Test GitHub Protection:
1. Enable push protection (see Manual Action above)
2. Try pushing a commit with a fake AWS key
3. GitHub should block the push

## Monitoring & Alerts

### GitHub Notifications:
- Email alerts for detected secrets
- Dependabot security alerts
- Partner program alerts (automatic provider notification)

### Check Alerts:
```bash
# List security alerts for a repo
gh api repos/mischa-thisness/REPO_NAME/secret-scanning/alerts

# View all alerts
# Visit: https://github.com/mischa-thisness?tab=security
```

## Additional Resources

- **GitHub Secret Scanning**: https://docs.github.com/en/code-security/secret-scanning
- **Gitleaks**: https://github.com/gitleaks/gitleaks
- **OWASP Secrets Management**: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

## Support

For issues or questions about this security setup:
1. Review this document
2. Check GitHub's secret scanning documentation
3. Run `gitleaks detect` manually to test

---

**Last Updated:** December 31, 2024
**Protection Level:** Multi-layered (GitHub Cloud + Local)
**Status:** Active ✅
