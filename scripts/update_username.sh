#!/bin/bash
# GitHub Username Update Script
# Updates all references to GitHub username throughout the repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Current username
OLD_USERNAME="mischa-thisness"

# Function to print colored output
print_info() { echo -e "${GREEN}✓${NC} $1"; }
print_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

echo "════════════════════════════════════════════════════════════════"
echo "  GitHub Username Update Script"
echo "════════════════════════════════════════════════════════════════"
echo

# Check if new username provided
if [ -z "$1" ]; then
    echo "Usage: $0 <new-username> [--dry-run]"
    echo
    echo "Examples:"
    echo "  $0 my-new-username           # Update and commit"
    echo "  $0 my-new-username --dry-run # Preview changes only"
    echo
    exit 1
fi

NEW_USERNAME="$1"
DRY_RUN=false

if [ "$2" == "--dry-run" ]; then
    DRY_RUN=true
    print_warn "DRY RUN MODE - No changes will be made"
    echo
fi

# Validate new username
if [[ ! "$NEW_USERNAME" =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$ ]]; then
    print_error "Invalid GitHub username format"
    echo "Username must:"
    echo "  - Start and end with alphanumeric characters"
    echo "  - May contain hyphens in the middle"
    echo "  - Cannot contain consecutive hyphens"
    exit 1
fi

echo "Current username: $OLD_USERNAME"
echo "New username:     $NEW_USERNAME"
echo

# Check if we're in the M-Claude repository
if [ ! -d ".git" ]; then
    print_error "Not in a git repository. Run this from the M-Claude root directory."
    exit 1
fi

# Check current remote
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$CURRENT_REMOTE" ]; then
    print_error "No 'origin' remote found"
    exit 1
fi

echo "Current remote: $CURRENT_REMOTE"
echo

# Find all files containing the old username
echo "Searching for files containing '$OLD_USERNAME'..."
FILES_TO_UPDATE=$(grep -r -l "$OLD_USERNAME" . \
    --exclude-dir=.git \
    --exclude-dir=CHAT_LOGS \
    --exclude-dir=CHAT_LOGS-markdown \
    --exclude-dir=journals \
    --exclude="*.jsonl" \
    2>/dev/null || true)

if [ -z "$FILES_TO_UPDATE" ]; then
    print_warn "No files found containing the old username"
else
    echo "Files to update:"
    echo "$FILES_TO_UPDATE" | while read -r file; do
        echo "  - $file"
    done
    echo
fi

if [ "$DRY_RUN" = true ]; then
    echo "════════════════════════════════════════════════════════════════"
    echo "  DRY RUN PREVIEW - Changes that would be made:"
    echo "════════════════════════════════════════════════════════════════"
    echo

    # Show what would change in git remote
    NEW_REMOTE=$(echo "$CURRENT_REMOTE" | sed "s/$OLD_USERNAME/$NEW_USERNAME/g")
    echo "1. Git remote would change to:"
    echo "   $NEW_REMOTE"
    echo

    # Show preview of file changes
    if [ -n "$FILES_TO_UPDATE" ]; then
        echo "2. File changes preview:"
        echo "$FILES_TO_UPDATE" | while read -r file; do
            echo
            echo "   File: $file"
            echo "   ─────────────────────────────────────────────────"
            grep -n "$OLD_USERNAME" "$file" | head -5 | while read -r line; do
                echo "   $line"
            done
        done
    fi

    echo
    echo "To apply these changes, run without --dry-run:"
    echo "  ./scripts/update_username.sh $NEW_USERNAME"
    echo
    exit 0
fi

# Confirm before making changes
echo "════════════════════════════════════════════════════════════════"
echo "  Ready to update username from '$OLD_USERNAME' to '$NEW_USERNAME'"
echo "════════════════════════════════════════════════════════════════"
echo
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    print_warn "Aborted by user"
    exit 0
fi

echo

# Step 1: Update git remote
echo "[1/4] Updating git remote URL..."
NEW_REMOTE=$(echo "$CURRENT_REMOTE" | sed "s/$OLD_USERNAME/$NEW_USERNAME/g")
git remote set-url origin "$NEW_REMOTE"
print_info "Remote URL updated to: $NEW_REMOTE"
echo

# Step 2: Update files
if [ -n "$FILES_TO_UPDATE" ]; then
    echo "[2/4] Updating files..."
    echo "$FILES_TO_UPDATE" | while read -r file; do
        sed -i "s/$OLD_USERNAME/$NEW_USERNAME/g" "$file"
        print_info "Updated: $file"
    done
    echo
else
    echo "[2/4] No files to update"
    echo
fi

# Step 3: Update this script itself
echo "[3/4] Updating this script..."
sed -i "s/OLD_USERNAME=\"$OLD_USERNAME\"/OLD_USERNAME=\"$NEW_USERNAME\"/" "$0"
print_info "Script updated with new default username"
echo

# Step 4: Git status and commit
echo "[4/4] Preparing git commit..."

# Check if there are changes
if git diff --quiet; then
    print_warn "No changes detected"
else
    git add -A

    echo
    echo "Changes staged:"
    git status --short
    echo

    read -p "Commit these changes? (yes/no): " COMMIT_CONFIRM

    if [ "$COMMIT_CONFIRM" == "yes" ]; then
        git commit --no-gpg-sign -m "Update GitHub username: $OLD_USERNAME → $NEW_USERNAME

- Updated git remote URL
- Updated all documentation references
- Automated via update_username.sh script

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

        print_info "Changes committed"
        echo

        read -p "Push to GitHub? (yes/no): " PUSH_CONFIRM

        if [ "$PUSH_CONFIRM" == "yes" ]; then
            git push
            print_info "Changes pushed to GitHub"
        else
            print_warn "Changes committed locally but not pushed"
            echo "To push later: git push"
        fi
    else
        print_warn "Changes not committed"
        echo "To commit later: git add -A && git commit"
    fi
fi

echo
echo "════════════════════════════════════════════════════════════════"
print_info "Username update complete!"
echo "════════════════════════════════════════════════════════════════"
echo
echo "Verification:"
echo "  Git remote: $(git remote get-url origin)"
echo
echo "Next steps:"
echo "  1. Verify the changes on GitHub"
echo "  2. Update any other clones of this repository"
echo "  3. Update bookmarks and saved links"
echo
