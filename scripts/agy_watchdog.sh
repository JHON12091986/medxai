#!/usr/bin/env bash
# agy_watchdog.sh — real-time commit monitor during an agy session
# Alerts if agy commits to a protected or locked file
# Usage: ./scripts/agy_watchdog.sh   (runs in background; Ctrl+C to stop)

set -euo pipefail

PROTECTED=(
  "interfaces/telegram_interface.py"
  ".env"
  "core/router.py"
  "main.py"
  "guardian_engine.py"
  "tools/shell.py"
  "ninagate/main.py"
  "tools/ninasync.py"
  "tests/test_ninasync.py"
  ".ninaignore"
  "requirements.txt"
)

cd ~/nina

LAST_SHA=$(git rev-parse HEAD 2>/dev/null || echo "")

echo "\ud83d\udc15 agy_watchdog active — monitoring $(git rev-parse --abbrev-ref HEAD) branch"
echo "   Watching ${#PROTECTED[@]} protected files. Ctrl+C to stop."
echo ""

while true; do
  sleep 3
  CURRENT_SHA=$(git rev-parse HEAD 2>/dev/null || echo "")

  if [[ "$CURRENT_SHA" != "$LAST_SHA" && -n "$CURRENT_SHA" ]]; then
    CHANGED=$(git diff --name-only "$LAST_SHA" "$CURRENT_SHA" 2>/dev/null || true)
    NEW_COMMIT_MSG=$(git log -1 --pretty=%s 2>/dev/null || true)

    ALARM=false
    for pfile in "${PROTECTED[@]}"; do
      if echo "$CHANGED" | grep -qF "$pfile"; then
        echo "\ud83d\udea8 WATCHDOG ALERT: protected file touched in commit $CURRENT_SHA"
        echo "   File   : $pfile"
        echo "   Commit : $NEW_COMMIT_MSG"
        echo "   Action : review immediately before running nina_sync.sh"
        ALARM=true
      fi
    done

    if [[ -f ~/nina/juleslock.txt ]]; then
      while IFS= read -r locked_file; do
        [[ -z "$locked_file" ]] && continue
        if echo "$CHANGED" | grep -qF "$locked_file"; then
          echo "\ud83d\udea8 WATCHDOG ALERT: juleslock file modified in commit $CURRENT_SHA"
          echo "   Locked : $locked_file"
          echo "   Commit : $NEW_COMMIT_MSG"
          ALARM=true
        fi
      done < ~/nina/juleslock.txt
    fi

    if [[ "$ALARM" == false ]]; then
      echo "\u2705 Commit $CURRENT_SHA clean: $NEW_COMMIT_MSG"
    fi

    LAST_SHA="$CURRENT_SHA"
  fi
done
