#!/bin/bash
# upload_debug_out.sh — NDEV pipeline uploader v3
# Bidirectional sync: stashes local changes, pulls, pops, pushes output.
# Never silently skips. Never fails on unstaged changes.
# Usage: bash upload_debug_out.sh
set -euo pipefail
cd ~/nina

# ── Collect metadata ─────────────────────────────────
COMMIT_SHA=$(git rev-parse HEAD)
SHORT_SHA=$(git rev-parse --short HEAD)
TASK_ROUND=$(python3 -c "import json; t=json.load(open('nina_debug_task.json')); print(t.get('round','?'))" 2>/dev/null || echo "?")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
RUN_ID="run-$(date '+%Y%m%d-%H%M%S')-r${TASK_ROUND}"
NINA_VER=$(head -3 nina_debug.py | grep -o 'v[0-9]*' | head -1 || echo "v?")

# ── STEP 1: Push any unpushed local commits first ──────────
LOCAL_AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
if [ "$LOCAL_AHEAD" -gt 0 ]; then
  echo "↕️  $LOCAL_AHEAD local commit(s) ahead — pushing first..."
  git push
  echo "   ✅ Push complete"
fi

# ── STEP 2: Stash any unstaged/staged changes, pull, pop ─────
STASH_OUT=$(git stash 2>&1)
if echo "$STASH_OUT" | grep -q 'No local changes'; then
  STASHED=0
else
  STASHED=1
  echo "📦 Stashed local changes for clean pull"
fi

git pull --quiet --rebase

if [ "$STASHED" -eq 1 ]; then
  git stash pop
  echo "📦 Stash restored"
fi

# ── STEP 3: Append tracking footer to output ─────────────
COMMIT_SHA=$(git rev-parse HEAD)
SHORT_SHA=$(git rev-parse --short HEAD)
{
  echo ""
  echo "========================================"
  echo " NDEV TRACKING FOOTER"
  echo " Run ID     : $RUN_ID"
  echo " Timestamp  : $TIMESTAMP"
  echo " Task round : $TASK_ROUND"
  echo " Git HEAD   : $COMMIT_SHA"
  echo " nina_debug : $NINA_VER"
  echo " Status     : UPLOAD COMPLETED ✅"
  echo "========================================"
} >> ~/nina_debug_out.txt

# ── STEP 4: Copy output + update history log ─────────────
cp ~/nina_debug_out.txt docs/space/nina_debug_out.txt
HISTORY="docs/space/ndev_upload_history.md"
if [ ! -f "$HISTORY" ]; then
  printf '# NDEV Upload History\n\n| Run ID | Round | SHA | Timestamp | Status |\n|--------|-------|-----|-----------|--------|\n' > "$HISTORY"
fi
echo "| $RUN_ID | $TASK_ROUND | \`$SHORT_SHA\` | $TIMESTAMP | ✅ UPLOADED |" >> "$HISTORY"

# ── STEP 5: Commit + push (unique RUN_ID = never skipped) ────
git add docs/space/nina_debug_out.txt "$HISTORY"
git commit -m "chore(ndev): $RUN_ID | round=$TASK_ROUND sha=$SHORT_SHA"
git push

# ── STEP 6: Print confirmation ─────────────────────────
echo ""
echo "✅ UPLOAD COMPLETED"
echo "   Run ID     : $RUN_ID"
echo "   Task round : $TASK_ROUND"
echo "   Git HEAD   : $SHORT_SHA"
echo "   History    : $HISTORY"
