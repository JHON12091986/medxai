#!/usr/bin/env bash
# setup_hooks.sh — install all NINA git hooks from git-hooks/
# Run once after every fresh clone or when hooks need reset.
# nina_sync.sh calls this automatically on every run.

NINA="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$NINA/git-hooks"
HOOKS_DST="$NINA/.git/hooks"

echo "Installing NINA git hooks..."
for hook in pre-commit pre-push post-commit; do
  if [ -f "$HOOKS_SRC/$hook" ]; then
    cp "$HOOKS_SRC/$hook" "$HOOKS_DST/$hook"
    chmod +x "$HOOKS_DST/$hook"
    chmod +x "$HOOKS_SRC/$hook"
    echo "  ✓ $hook"
  else
    echo "  WARN: $HOOKS_SRC/$hook not found"
  fi
done
echo "Done. Hooks active:"
ls -la "$HOOKS_DST/pre-commit" "$HOOKS_DST/pre-push" "$HOOKS_DST/post-commit" 2>/dev/null
