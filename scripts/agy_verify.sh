#!/usr/bin/env bash
# agy_verify.sh — post-task verification: compile + pyflakes + impact + guardian drift check
# Usage: ./scripts/agy_verify.sh <file> [task_id]
# Example: ./scripts/agy_verify.sh tools/ninaflash.py nina-20260616-001

set -euo pipefail

PYTHON="python3"
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
elif [ -f "ninavenv/bin/python" ]; then
    PYTHON="ninavenv/bin/python"
fi

FILE="${1:-}"
TASK_ID="${2:-unknown}"
PASS=true

if [[ -z "$FILE" ]]; then
  echo "Usage: ./scripts/agy_verify.sh <file> [task_id]"
  exit 1
fi

echo "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
echo " POST-TASK VERIFY: $FILE"
echo " TASK ID: $TASK_ID"
echo "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"

# 1. Compile check
if "$PYTHON" -m py_compile "$FILE" 2>&1; then
  echo "\u2705 py_compile: PASS"
else
  echo "\u274c py_compile: FAIL"
  PASS=false
fi

# 2. Pyflakes
if pyflakes "$FILE" 2>&1; then
  echo "\u2705 pyflakes: PASS"
else
  echo "\u26a0\ufe0f  pyflakes: warnings (review above)"
fi

# 3. Impact check (if script exists)
if [[ -f ~/nina/agy_impact_check.py ]]; then
  echo ""
  echo "--- Impact Check ---"
  cd ~/nina && "$PYTHON" agy_impact_check.py "$FILE" || true
  echo "--- End Impact Check ---"
fi

# 4. Guardian post-snapshot + drift compare
if [[ -f ~/nina/guardian_engine.py ]]; then
  SNAP_PRE="/tmp/nina_guardian_pre_${TASK_ID}.snap"
  GUARDIAN_POST=$(cd ~/nina && "$PYTHON" guardian_engine.py --snapshot 2>/dev/null || echo "guardian_unavailable")
  if [[ -f "$SNAP_PRE" && "$GUARDIAN_POST" != "guardian_unavailable" ]]; then
    echo ""
    echo "--- Guardian Drift Check ---"
    DIFF=$(diff "$SNAP_PRE" <(echo "$GUARDIAN_POST") || true)
    if [[ -z "$DIFF" ]]; then
      echo "\u2705 Guardian: no drift detected"
    else
      echo "\u26a0\ufe0f  Guardian drift detected:"
      echo "$DIFF"
    fi
    rm -f "$SNAP_PRE"
    echo "--- End Guardian Drift ---"
  else
    echo "\u2139\ufe0f  Guardian: no pre-snapshot found for $TASK_ID (skipping drift check)"
  fi
fi

echo ""
if [[ "$PASS" == true ]]; then
  echo "\u2705 VERIFY PASSED — safe to commit."
  "$PYTHON" -c "import asyncio, sys; sys.path.append('/home/aibony/nina'); from core.event_bus import EventBus; bus = EventBus(); asyncio.run(bus.publish('TASK_VERIFIED', {'file': '$FILE', 'task_id': '$TASK_ID'}, 'agy'))" 2>/dev/null || true
else
  echo "\u274c VERIFY FAILED — fix errors before committing."
  exit 1
fi
