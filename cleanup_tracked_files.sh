#!/bin/bash
# Cleanup script to remove tracked files that should be ignored
# This script removes files from git tracking but keeps them on disk

set -e

echo "========================================================================"
echo "Repository Cleanup Script"
echo "========================================================================"
echo ""
echo "This script will remove the following files from git tracking:"
echo "  - data/aligned/*.txt (generated outputs)"
echo "  - deploy_*.sh (deployment scripts)"
echo ""
echo "Files will remain on your local disk but won't be committed to git."
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "Error: Not in a git repository!"
    exit 1
fi

# Ask for confirmation
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Removing files from git tracking..."
echo "========================================================================"

# Remove aligned output files
for file in data/aligned/*.txt; do
    if [ -f "$file" ] && git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "Removing: $file"
        git rm --cached "$file" || true
    fi
done

# Remove deployment scripts
for file in deploy_*.sh; do
    if [ -f "$file" ] && git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "Removing: $file"
        git rm --cached "$file" || true
    fi
done

# Remove backup files if any
for file in data/processed/*.backup; do
    if [ -f "$file" ] && git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "Removing: $file"
        git rm --cached "$file" || true
    fi
done

# Remove audio files if tracked
if [ -d Audio ] && git ls-files --error-unmatch Audio/ >/dev/null 2>&1; then
    echo "Removing: Audio/"
    git rm -r --cached Audio/ || true
fi

# Remove example outputs
if git ls-files --error-unmatch "examples/example_output.txt" >/dev/null 2>&1; then
    echo "Removing: examples/example_output.txt"
    git rm --cached "examples/example_output.txt" || true
fi

echo ""
echo "========================================================================"
echo "Cleanup Complete!"
echo "========================================================================"
echo ""
echo "Files removed from git tracking (but kept on disk):"
git status --short | grep "^D" || echo "  (none - all may have been already untracked)"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Stage .gitignore: git add .gitignore"
echo "  3. Commit changes: git commit -m 'Clean up repository and update .gitignore'"
echo ""
echo "Note: The removed files still exist on your disk - they're just not"
echo "      tracked by git anymore. They're now covered by .gitignore."
echo ""
