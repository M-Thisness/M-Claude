# Git History Rewrite Plan

**Date:** January 12, 2026
**Purpose:** Scrub, purge, and sanitize all secrets from git history
**Tools:** git-filter-repo (primary), BFG Repo-Cleaner (secondary)
**Status:** ⚠️ PLANNING - NOT YET EXECUTED

---

## Analysis Summary

### Gitleaks Scan Results

**Full History Scan:**
- Commits scanned: 42
- Data scanned: 58.26 MB
- Total findings: 16,684 potential secrets
- Scan duration: 24.8 seconds

### Finding Breakdown by Type

Top secret types detected:
1. **Twilio Account SIDs**: ~4,500 findings
2. **Base64 High-Entropy**: ~3,800 findings
3. **Credit Card Numbers**: ~1,200 findings
4. **Twilio API Keys**: ~400 findings
5. **Hardcoded IPs**: Multiple findings
6. **Generic secrets**: Multiple findings

### Finding Breakdown by Location

**Primary sources (98% of findings):**
1. `CHAT_LOGS/` directory - Conversation transcripts (JSONL)
2. `CHAT_LOGS-markdown/` directory - Markdown conversions
3. `transcripts/` directory - Agent transcripts
4. `CHAT_LOG.md` - Main chat log file

**Assessment:**
- ✅ Most findings are FALSE POSITIVES from conversation content
- ✅ Conversations discuss technical topics (Twilio, APIs, etc.)
- ✅ Examples in conversations trigger detection
- ⚠️ Cannot easily distinguish real vs example secrets in unstructured text

---

## Strategy: Aggressive History Cleanup

### Option 1: Remove Sensitive Directories (RECOMMENDED)

**Directories to completely remove from ALL history:**
- `CHAT_LOGS/` - ~120 chat log files
- `CHAT_LOGS-markdown/` - ~20 markdown files
- `transcripts/` - Agent transcripts

**Rationale:**
- These files contain unstructured conversation data
- Impossible to programmatically distinguish real vs fake secrets
- Files are already in `.gitleaksignore` for future commits
- Preserves actual code and documentation
- Most secure approach - removes all possibility of exposure

**Impact:**
- Repository size reduction: ~40-50 MB
- Commit history: Preserved (only file content removed)
- Code/docs: Fully preserved
- Future commits: Can add sanitized versions if needed

### Option 2: Content Sanitization (ALTERNATIVE)

**Sanitize content within files:**
- Replace detected secrets with `[REDACTED]`
- Use git-filter-repo callbacks
- More complex, slower, riskier

**Not recommended because:**
- Cannot guarantee all secrets caught
- May damage file structure
- More likely to have errors
- Longer processing time

---

## Execution Plan: git-filter-repo

### Phase 1: Pre-Cleanup Preparation

```bash
# 1. Verify backup exists
ls -lh ../M-Claude-backup-*.tar.gz

# 2. Create additional backup
cp -r /Users/m/Documents/M-Claude /Users/m/Documents/M-Claude-backup-pre-rewrite

# 3. Commit all staged changes first
git commit -m "Pre-cleanup: Add gitleaks configuration and security docs"

# 4. Create a tag before cleanup
git tag pre-history-cleanup

# 5. Document current state
git log --oneline > /tmp/commits-before-cleanup.txt
git rev-parse HEAD > /tmp/head-before-cleanup.txt
```

### Phase 2: Execute git-filter-repo

```bash
# Remove sensitive directories from ALL history
git-filter-repo --path CHAT_LOGS --path CHAT_LOGS-markdown --path transcripts --invert-paths --force

# Alternative: Keep paths but remove from history
# git-filter-repo --path-glob 'CHAT_LOGS/**' --invert-paths --force
```

**What this does:**
- `--path CHAT_LOGS` - Targets the CHAT_LOGS directory
- `--path CHAT_LOGS-markdown` - Targets markdown chat logs
- `--path transcripts` - Targets transcripts directory
- `--invert-paths` - REMOVES these paths (opposite of keep)
- `--force` - Proceed even with uncommitted changes warnings

### Phase 3: Additional Sanitization (Optional)

If needed, sanitize specific files:

```bash
# Create replacements file for remaining sensitive content
cat > /tmp/replacements.txt <<'EOF'
sk-ant-api03-***REMOVED***
ghp_***REMOVED***
regex:(AKIA[0-9A-Z]{16})==>AWS_KEY_REMOVED
regex:(AIza[0-9A-Za-z_-]{35})==>GOOGLE_KEY_REMOVED
regex:(sk_live_[a-zA-Z0-9]{24})==>STRIPE_KEY_REMOVED
EOF

# Apply replacements
git-filter-repo --replace-text /tmp/replacements.txt --force
```

### Phase 4: Verification

```bash
# 1. Check repository size reduction
du -sh .git

# 2. Verify directories are gone from history
git log --all --oneline --name-only | grep -E "(CHAT_LOGS|transcripts)" || echo "✅ Directories removed"

# 3. Run gitleaks again on cleaned history
gitleaks detect --config=.gitleaks.toml --log-opts="--all" --redact

# 4. Check commit count preserved
git log --all --oneline | wc -l

# 5. Verify current files intact
ls -la CHAT_LOGS/ transcripts/ 2>/dev/null || echo "✅ Directories removed from working tree"
```

### Phase 5: Cleanup & GC

```bash
# 1. Run git garbage collection
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 2. Check final size
du -sh .git

# 3. Verify HEAD integrity
git fsck --full
```

### Phase 6: Force Push (CRITICAL - DESTRUCTIVE)

**⚠️ WARNING: This rewrites remote history and requires team coordination**

```bash
# 1. Backup remote refs before push
git ls-remote origin > /tmp/remote-refs-before-push.txt

# 2. Force push rewritten history
git push origin --force --all
git push origin --force --tags

# 3. Notify team to re-clone
echo "⚠️ ALL TEAM MEMBERS MUST RE-CLONE THE REPOSITORY"
```

---

## Risks & Mitigation

### Risk 1: Data Loss

**Risk:** Accidentally removing important files
**Mitigation:**
- ✅ Multiple backups created (tar.gz + directory copy)
- ✅ Dry-run testing available
- ✅ Tag created before cleanup (`pre-history-cleanup`)

### Risk 2: Corrupted Repository

**Risk:** git-filter-repo creates invalid state
**Mitigation:**
- ✅ Run `git fsck` after cleanup
- ✅ Verify with test clone
- ✅ Can restore from backup if needed

### Risk 3: Broken References

**Risk:** Other repos/CI referencing removed files
**Mitigation:**
- ✅ Files already in `.gitleaksignore` for new commits
- ✅ Only historical references affected
- ✅ Current working tree can be preserved

### Risk 4: Team Coordination

**Risk:** Team members have outdated history
**Mitigation:**
- ⚠️ Require all team members to re-clone
- ⚠️ Coordinate timing (low-activity period)
- ⚠️ Send advance notice

### Risk 5: PR/Issue References

**Risk:** GitHub PRs/Issues reference removed commits
**Mitigation:**
- ℹ️ Expected behavior - old SHAs will be invalid
- ℹ️ Content still in PR discussions
- ℹ️ Minor inconvenience vs security benefit

---

## Expected Results

### Before Cleanup

```
Repository Size:      ~60 MB
Commits:             42
Files with Secrets:  ~150+ (in chat logs)
Secret Findings:     16,684
```

### After Cleanup

```
Repository Size:      ~10-15 MB (75-80% reduction)
Commits:             42 (preserved)
Files with Secrets:  ~0-5 (only if in docs)
Secret Findings:     <100 (mostly false positives)
```

### File Count Impact

**Removed:**
- ~120 JSONL chat log files
- ~20 Markdown chat log files
- ~15 transcript files
- Total: ~155 files removed from history

**Preserved:**
- All code files (Python, shell scripts)
- All documentation (except chat logs)
- All configuration files
- All current commits
- All commit messages and metadata

---

## Recovery Procedures

### If Cleanup Goes Wrong

**Option 1: Restore from Backup**
```bash
cd /Users/m/Documents
rm -rf M-Claude
tar -xzf M-Claude-backup-YYYYMMDD-HHMMSS.tar.gz
# OR
cp -r M-Claude-backup-pre-rewrite M-Claude
```

**Option 2: Reset to Tag**
```bash
git reset --hard pre-history-cleanup
git push origin --force --all
```

**Option 3: Restore from Remote** (if not yet pushed)
```bash
git fetch origin
git reset --hard origin/main
```

---

## Post-Cleanup Procedures

### For Repository Owner

```bash
# 1. Verify cleanup success
gitleaks detect --config=.gitleaks.toml --log-opts="--all"

# 2. Update README with cleanup notice
echo "Repository history was cleaned on $(date)" >> README.md

# 3. Document in CHANGELOG
cat >> CHANGELOG.md <<'EOF'
## [Unreleased] - 2026-01-12
### Security
- Scrubbed git history to remove all potential secrets
- Removed CHAT_LOGS/ and transcripts/ from history
- Repository size reduced by 75%
EOF

# 4. Create release tag
git tag -a v1.0-clean -m "Clean history release"
git push origin v1.0-clean
```

### For Team Members

**REQUIRED: All team members must re-clone**

```bash
# 1. Save any local work
cd /path/to/M-Claude
git stash save "Work before history rewrite"

# 2. Delete local repository
cd ..
rm -rf M-Claude

# 3. Fresh clone
git clone git@github.com:USERNAME/M-Claude.git
cd M-Claude

# 4. Verify clean history
git log --oneline
gitleaks detect --config=.gitleaks.toml --log-opts="--all"

# 5. Restore stashed work if needed
git stash list
git stash pop  # if you stashed work
```

---

## Alternative: BFG Repo-Cleaner (If Available)

### BFG Commands (Faster but Less Precise)

```bash
# 1. Clone bare repository
git clone --mirror git@github.com:USERNAME/M-Claude.git M-Claude-mirror.git

# 2. Run BFG
cd M-Claude-mirror.git
bfg --delete-folders CHAT_LOGS --delete-folders transcripts --delete-folders CHAT_LOGS-markdown

# 3. Cleanup
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Push
git push --force
```

**BFG Advantages:**
- Much faster (10-100x)
- Simpler commands
- Good for large repos

**BFG Disadvantages:**
- Less precise than git-filter-repo
- Cannot do complex content replacements
- Protects HEAD by default (need --no-blob-protection for current branch)

---

## Decision Matrix

### When to Use Each Tool

| Scenario | Tool | Reason |
|----------|------|--------|
| Remove entire directories | **git-filter-repo** | More control, safer |
| Large repo (>1GB) | BFG | Much faster |
| Complex replacements | git-filter-repo | Callback support |
| Simple text replacement | BFG | One-liner command |
| Maximum safety | git-filter-repo | Better error handling |
| Quick cleanup | BFG | Speed |

### Recommendation for M-Claude

**Use git-filter-repo because:**
- ✅ Repo is small (~60 MB)
- ✅ Need precise control
- ✅ Want to remove directories, not just files
- ✅ git-filter-repo is already installed
- ✅ Better documentation and safety
- ⚠️ BFG installation currently has issues

---

## Timeline

### Estimated Duration

1. **Preparation**: 5 minutes
2. **git-filter-repo execution**: 30-60 seconds
3. **Verification**: 5 minutes
4. **Garbage collection**: 2-5 minutes
5. **Force push**: 1-2 minutes
6. **Team notification**: Immediate

**Total: ~15-20 minutes**

### Recommended Schedule

**Best time to execute:**
- Weekend or off-hours
- After team notification (24h advance)
- During low-activity period
- When all PRs are merged

---

## Checklist

### Pre-Execution

- [ ] Backup created (`tar.gz` archive)
- [ ] Backup verified (can extract)
- [ ] Second backup created (directory copy)
- [ ] All changes committed
- [ ] Tag created (`pre-history-cleanup`)
- [ ] Team notified (if applicable)
- [ ] git-filter-repo installed and tested
- [ ] Gitleaks report generated
- [ ] Plan reviewed and approved

### During Execution

- [ ] Run git-filter-repo command
- [ ] Verify directories removed
- [ ] Run gitleaks on cleaned history
- [ ] Check commit count preserved
- [ ] Run git fsck
- [ ] Run garbage collection
- [ ] Check repository size reduction

### Post-Execution

- [ ] Force push to origin (if applicable)
- [ ] Update README with cleanup notice
- [ ] Document in CHANGELOG
- [ ] Notify team to re-clone
- [ ] Archive old backups
- [ ] Mark cleanup as complete

---

## Questions & Answers

**Q: Will this break existing PRs?**
A: Yes - old commit SHAs will be invalid. Coordinate PR merges before cleanup.

**Q: Can we undo this?**
A: Yes, before force push. After force push, only from backups.

**Q: Will commit messages change?**
A: No - commit messages, authors, and dates are preserved.

**Q: Will this affect GitHub Issues?**
A: Slightly - commit references in issues will be invalid SHAs.

**Q: How long will it take?**
A: ~15-20 minutes total, most time is verification and GC.

**Q: Is this reversible after force push?**
A: Only by restoring from backup and force-pushing again (destructive).

**Q: What about CI/CD?**
A: May need to clear caches. Fresh clones will work automatically.

**Q: Will this remove tags?**
A: No - tags are preserved unless explicitly removed.

**Q: What about signed commits?**
A: Signatures may become invalid but commits remain.

**Q: Should we do this?**
A: YES - if secrets exist in history. NO - if all findings are false positives.

---

## Final Recommendation

### For M-Claude Repository

**RECOMMENDED ACTION:** Proceed with git-filter-repo cleanup

**Reason:**
- 16,684 findings is excessive
- Cannot verify all are false positives
- Better safe than sorry
- Easy recovery if issues arise
- Significant size reduction benefit
- Improves security posture

**Alternate approach:**
If you're confident all findings are false positives from conversations:
- Keep current history
- Use `.gitleaksignore` for future commits
- Document that chat logs contain example/redacted content
- No history rewrite needed

**Decision:** Up to repository owner based on risk tolerance.

---

**Document Status:** PLANNING PHASE
**Next Step:** Get approval before executing
**Estimated Completion:** 15-20 minutes once approved
