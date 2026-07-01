#!/usr/bin/env bash
# NINA Branch Cleanup — deletes orphaned Jules branches (no open PR)
# Cron: 0 0 * * 0 ~/nina/git/scripts/branch_cleanup.sh >> ~/nina/logs/branch_cleanup.log 2>&1
set -euo pipefail

cd ~/nina

echo "[branch-cleanup] $(date) — Scanning for stale orphaned branches..."

git fetch --prune origin 2>/dev/null

DELETED=0
for BRANCH in $(git branch -r | grep 'origin/jules-' | sed 's|  origin/||'); do
  PR=$(gh pr list --head "$BRANCH" --state open --json number -q '.[0].number' 2>/dev/null || echo "")
  if [ -z "$PR" ]; then
    echo "[branch-cleanup] 🗑 Deleting orphaned: $BRANCH"
    git push origin --delete "$BRANCH" 2>/dev/null && DELETED=$((DELETED+1)) || echo "[branch-cleanup] ⚠ Could not delete $BRANCH"
  else
    echo "[branch-cleanup] ✓ Active PR #$PR — keeping: $BRANCH"
  fi
done

echo "[branch-cleanup] ✅ Done. $DELETED branch(es) deleted."
