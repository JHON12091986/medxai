#!/usr/bin/env bash
# agy_verify.sh — post-task verification for agy edits
# Usage: ./agy_verify.sh <file>
# Example: ./agy_verify.sh tools/ninaflash.py

set -euo pipefail

FILE="${1:-}"

if [[ -z "$FILE" ]]; then
  echo "Usage: ./agy_verify.sh <file>"
  exit 1
fi

if [[ ! -f "$FILE" ]]; then
  echo "❌ File not found: $FILE"
  exit 1
fi

PASS=0
FAIL=0

check() {
  local label="$1"
  local cmd="$2"
  if eval "$cmd" &>/dev/null; then
    echo "  ✅ $label"
    (( PASS++ )) || true
  else
    echo "  ❌ $label"
    eval "$cmd" 2>&1 | sed 's/^/     /'
    (( FAIL++ )) || true
  fi
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " agy_verify: $FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Syntax check
if [[ "$FILE" == *.py ]]; then
  check "py_compile (syntax)" "python3 -m py_compile '$FILE'"
  check "pyflakes (lint)" "python3 -m pyflakes '$FILE'"
fi

# 2. Git diff summary
echo ""
echo "  📄 git diff --stat (last commit):"
git diff HEAD~1 --stat -- "$FILE" 2>/dev/null | sed 's/^/     /' || echo "     (no diff available)"

# 3. juleslock check
if grep -qF "$FILE" ~/nina/juleslock.txt 2>/dev/null; then
  echo ""
  echo "  ⚠️  $FILE is still in juleslock.txt — remove it if task is complete."
fi

# 4. Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ $FAIL -eq 0 ]]; then
  echo " RESULT: PASS ($PASS checks passed)"
  echo " Next: ./nina_sync.sh"
else
  echo " RESULT: FAIL ($FAIL failed, $PASS passed)"
  echo " Fix errors before syncing."
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

[[ $FAIL -eq 0 ]]
