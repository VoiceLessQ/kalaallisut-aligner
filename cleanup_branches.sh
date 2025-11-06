#!/bin/bash
# Cleanup script to delete old claude branches after merging to master

set -e

echo "╔════════════════════════════════════════════╗"
echo "║  Branch Cleanup Script                    ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if on master
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "master" ] && [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: You're not on master/main branch"
    echo "   Current branch: $CURRENT_BRANCH"
    read -p "   Do you want to switch to master? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout master || git checkout main
    else
        echo "Exiting. Please switch to master/main first."
        exit 1
    fi
fi

echo "📥 Fetching latest from origin..."
git fetch origin

echo ""
echo "🗑️  Deleting local claude branches..."

# List of branches to delete
LOCAL_BRANCHES=(
    "claude/analyze-project-feasibility-011CUqpQ81Brx5sTdtUgpb4f"
    "claude/sync-and-analyse-011CUqSHENQuQJsFKBtVcqG4"
    "claude/update-readme-and-merge-011CUqpQ81Brx5sTdtUgpb4f"
)

for branch in "${LOCAL_BRANCHES[@]}"; do
    if git show-ref --verify --quiet "refs/heads/$branch"; then
        git branch -D "$branch" && echo "   ✅ Deleted local: $branch"
    else
        echo "   ⏭️  Already deleted: $branch"
    fi
done

echo ""
echo "🗑️  Deleting remote claude branches..."

REMOTE_BRANCHES=(
    "claude/add-license-011CUqSHENQuQJsFKBtVcqG4"
    "claude/analyze-language-references-011CUqTpEYZfnLhkJHJAPAFF"
    "claude/analyze-project-feasibility-011CUqpQ81Brx5sTdtUgpb4f"
    "claude/sync-and-analyse-011CUqSHENQuQJsFKBtVcqG4"
    "claude/update-readme-and-merge-011CUqpQ81Brx5sTdtUgpb4f"
)

for branch in "${REMOTE_BRANCHES[@]}"; do
    if git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
        git push origin --delete "$branch" 2>/dev/null && echo "   ✅ Deleted remote: $branch" || echo "   ⚠️  Failed to delete: $branch"
    else
        echo "   ⏭️  Already deleted: $branch"
    fi
done

echo ""
echo "🧹 Pruning remote references..."
git remote prune origin

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  ✅ Cleanup Complete!                      ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📊 Remaining branches:"
git branch -a

echo ""
echo "💡 Tip: If you want to rename master to main:"
echo "   git branch -m master main"
echo "   git push origin main"
echo "   git push origin --delete master"
echo "   (Then update default branch on GitHub)"
