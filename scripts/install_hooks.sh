#!/usr/bin/env bash
# NINA Hook Installer — run once after clone or whenever git-hooks/ changes.
# Usage: bash scripts/install_hooks.sh
#
# Copies every file from git-hooks/ into .git/hooks/ and sets +x.
# Idempotent — safe to run multiple times.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$REPO_ROOT/git-hooks"
HOOKS_DST="$REPO_ROOT/.git/hooks"

if [ ! -d "$HOOKS_SRC" ]; then
    echo "❌ git-hooks/ directory not found at $HOOKS_SRC"
    exit 1
fi

echo "Installing NINA git hooks..."
for hook in "$HOOKS_SRC"/*; do
    name=$(basename "$hook")
    dest="$HOOKS_DST/$name"
    cp "$hook" "$dest"
    chmod +x "$dest"
    echo "  ✓ Installed: .git/hooks/$name"
done

echo ""
echo "✅ All hooks installed. They will run automatically on git operations."
echo "   Hooks installed: $(ls $HOOKS_DST | tr '\n' ' ')"
