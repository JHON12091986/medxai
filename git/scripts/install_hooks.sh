#!/usr/bin/env bash
# Install NINA git hooks from git/hooks/ into .git/hooks/
# Run once after clone: bash git/scripts/install_hooks.sh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "[install-hooks] Installing NINA git hooks..."

for HOOK in git/hooks/*; do
  HOOK_NAME=$(basename "$HOOK")
  cp "$HOOK" ".git/hooks/$HOOK_NAME"
  chmod +x ".git/hooks/$HOOK_NAME"
  echo "  ✅ $HOOK_NAME installed"
done

# Also sync to legacy git-hooks/ folder for compatibility
mkdir -p git-hooks
for HOOK in git/hooks/*; do
  HOOK_NAME=$(basename "$HOOK")
  cp "$HOOK" "git-hooks/$HOOK_NAME"
  chmod +x "git-hooks/$HOOK_NAME"
done

echo "[install-hooks] ✅ All hooks installed. Run 'git status' to verify clean state."
