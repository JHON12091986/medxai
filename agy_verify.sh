#!/usr/bin/env bash
# agy_verify.sh — post-task verification: compile + pyflakes + impact + guardian drift check
# Usage: ./agy_verify.sh <file> [task_id]
# Example: ./agy_verify.sh tools/ninaflash.py nina-20260616-001

set -euo pipefail

FILE="${1:-}"
TASK_ID="${2:-unknown}"
PASS=true

if [[ -z "$FILE" ]]; then
  echo "Usage: ./agy_verify.sh <file> [task_id]"
  exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " POST-TASK VERIFY: $FILE"
echo " TASK ID: $TASK_ID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Compile check
if python3 -m py_compile "$FILE" 2>&1; then
  echo "✅ py_compile: PASS"
else
  echo "❌ py_compile: FAIL"
  PASS=false
fi

# 2. Pyflakes
if pyflakes "$FILE" 2>&1; then
  echo "✅ pyflakes: PASS"
else
  echo "⚠️  pyflakes: warnings (review above)"
fi

# 3. Impact check (if script exists)
if [[ -f ~/nina/agy_impact_check.py ]]; then
  echo ""
  echo "--- Impact Check ---"
  cd ~/nina && python3 agy_impact_check.py "$FILE" || true
  echo "--- End Impact Check ---"
fi

# 4. Guardian post-snapshot + drift compare
if [[ -f ~/nina/guardian_engine.py ]]; then
  SNAP_PRE="/tmp/nina_guardian_pre_${TASK_ID}.snap"
  GUARDIAN_POST=$(cd ~/nina && python3 guardian_engine.py --snapshot 2>/dev/null || echo "guardian_unavailable")
  if [[ -f "$SNAP_PRE" && "$GUARDIAN_POST" != "guardian_unavailable" ]]; then
    echo ""
    echo "--- Guardian Drift Check ---"
    DIFF=$(diff "$SNAP_PRE" <(echo "$GUARDIAN_POST") || true)
    if [[ -z "$DIFF" ]]; then
      echo "✅ Guardian: no drift detected"
    else
      echo "⚠️  Guardian drift detected:"
      echo "$DIFF"
    fi
    rm -f "$SNAP_PRE"
    echo "--- End Guardian Drift ---"
  else
    echo "ℹ️  Guardian: no pre-snapshot found for $TASK_ID (skipping drift check)"
  fi
fi

echo ""
if [[ "$PASS" == true ]]; then
  echo "✅ VERIFY PASSED — safe to commit."
else
  echo "❌ VERIFY FAILED — fix errors before committing."
  exit 1
fi
