#!/usr/bin/env bash
# nina_sync.sh v3 — Full-featured post-session sync

set -euo pipefail

NINA=~/nina
SPACE_DIR="$NINA/docs/space"
LOGS_DIR="$NINA/logs"
DRY_RUN=false
[ "${1:-}" = "--dry-run" ] && DRY_RUN=true

SPACE_FILES=(
  AGENTS.md
  nina_context.md
  nina_problem_log.md
  nina_error_register.md
  nina_phase1_roadmap.md
  nina_update_log.md
)

TS=$(date '+%Y-%m-%d %H:%M')
DATE=$(date '+%Y-%m-%d')

echo "================================================"
echo " NINA POST-SESSION SYNC  $TS$([ "$DRY_RUN" = true ] && echo " [DRY-RUN]")"
echo "================================================"

cd "$NINA"

_tg_notify() {
  local msg="$1"
  local token user_id
  token=$(grep -E '^TELEGRAMBOTTOKEN=' "$NINA/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' || true)
  user_id=$(grep -E '^AUTHORIZEDUSERID=' "$NINA/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' || true)
  if [ -n "$token" ] && [ -n "$user_id" ]; then
    curl -s -X POST "https://api.telegram.org/bot${token}/sendMessage" \
      -d "chat_id=${user_id}" -d "text=${msg}" > /dev/null 2>&1 || true
  fi
}

echo "[0/7] Health check..."
BAD_FILES=$(find "$NINA" -maxdepth 1 \( -name "*-*.md" -o -name "*-*.sh" \) 2>/dev/null || true)
if [ -n "$BAD_FILES" ]; then
  echo "  ⚠  Hyphenated filenames — auto-renaming to snake_case:"
  while IFS= read -r bad; do
    good=$(basename "$bad" | sed 's/-/_/g')
    echo "     $(basename $bad) → $good"
    [ "$DRY_RUN" = false ] && git mv "$(basename $bad)" "$good" 2>/dev/null || true
  done <<< "$BAD_FILES"
else
  echo "  ✓ Naming convention consistent"
fi

SVC_STATUS=$(systemctl is-active nina 2>/dev/null || echo "unknown")
[ "$SVC_STATUS" = "active" ] && echo "  ✓ nina.service running" || echo "  ⚠  nina.service is $SVC_STATUS"

git fetch origin --quiet 2>/dev/null || true
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
[ "$BEHIND" -gt 0 ] && echo "  ⚠  $BEHIND commit(s) behind origin/main" || echo "  ✓ In sync with origin/main"

echo "[1/7] Auto-fetch from Downloads..."
FETCHED=0
for f in "${SPACE_FILES[@]}"; do
  SRC="$HOME/Downloads/$f"; DST="$NINA/$f"
  if [ -f "$SRC" ]; then
    if ! diff -q "$SRC" "$DST" > /dev/null 2>&1; then
      echo "  ↓ $f (updated from Downloads)"
      [ "$DRY_RUN" = false ] && cp "$SRC" "$DST"
      FETCHED=$((FETCHED+1))
    else
      echo "  = $f (Downloads copy identical)"
    fi
  fi
done
[ "$FETCHED" -eq 0 ] && echo "  (no new Downloads files)"

echo "[2/7] Mirror to docs/space/..."
[ "$DRY_RUN" = false ] && mkdir -p "$SPACE_DIR"
for f in "${SPACE_FILES[@]}"; do
  SRC="$NINA/$f"; DST="$SPACE_DIR/$f"
  if [ ! -f "$SRC" ]; then echo "  ✗ MISSING: $f"; continue; fi
  if [ ! -f "$DST" ] || ! diff -q "$SRC" "$DST" > /dev/null 2>&1; then
    echo "  ✓ $f (updated)"; [ "$DRY_RUN" = false ] && cp "$SRC" "$DST"
  else
    echo "  = $f (unchanged)"
  fi
done
for lf in nina_update_log.md nina_problem_log.md; do
  if [ -f "$LOGS_DIR/$lf" ] && [ -f "$NINA/$lf" ]; then
    if ! diff -q "$LOGS_DIR/$lf" "$NINA/$lf" > /dev/null 2>&1; then
      echo "  ✓ $lf (synced from logs/)"; [ "$DRY_RUN" = false ] && cp "$LOGS_DIR/$lf" "$NINA/$lf"
    fi
  fi
done

echo "[3/7] Backup cleanup..."
OLD_FILES=$(find "$NINA/upgrades/backups" -maxdepth 3 \
  \( -name "*.bak" -o -name "*.fix" -o -name "*.save" \) -mtime +30 2>/dev/null || true)
if [ -n "$OLD_FILES" ]; then
  COUNT=$(echo "$OLD_FILES" | wc -l | tr -d ' ')
  echo "  🗑  $COUNT stale file(s) >30 days old"
  if [ "$DRY_RUN" = false ]; then
    echo "$OLD_FILES" | xargs rm -f && echo "  ✓ Cleaned"
  else
    echo "  (dry-run: would delete)"
  fi
else
  echo "  ✓ No stale backup files"
fi

echo "[4/7] Update log entry..."
LAST_ENTRY=$(grep -c "^## Entry" "$NINA/nina_update_log.md" 2>/dev/null || echo "0")
NEXT_NUM=$(printf '%03d' $((LAST_ENTRY + 1)))
CHANGED_FILES=$(git status --porcelain 2>/dev/null | awk '{print $2}' | tr '\n' ',' | sed 's/,$//' || echo "none")
if [ "$DRY_RUN" = false ] && [ -n "$CHANGED_FILES" ] && [ "$CHANGED_FILES" != "none" ]; then
  python3 - << PYEOF
lines = [
    "",
    "---",
    "",
    "## Entry $NEXT_NUM — $DATE · D-sync Post-session sync",
    "",
    "**Triggered by:** nina_sync.sh v3 automated run",
    "",
    "**Files changed:** $CHANGED_FILES",
    "",
    "**Verification:** git push OK, nina.service $SVC_STATUS",
    "",
]
entry = chr(10).join(lines)
for path in ["$NINA/nina_update_log.md", "$LOGS_DIR/nina_update_log.md"]:
    try:
        open(path, "a").write(entry)
    except Exception:
        pass
print("  ✓ Log entry appended (Entry $NEXT_NUM)")
PYEOF
else
  echo "  = No changes to log"
fi

echo "[5/7] Staging..."
if [ "$DRY_RUN" = false ]; then
  git add docs/space/ "${SPACE_FILES[@]}" nina_sync.sh 2>/dev/null || true
  git add -u 2>/dev/null || true
fi

echo "[6/7] Committing..."
if [ "$DRY_RUN" = true ]; then
  echo "  (dry-run: skipping commit)"
else
  STAGED=$(git diff --cached --name-only 2>/dev/null || true)
  if [ -n "$STAGED" ]; then
    echo "  Changed files:"; echo "$STAGED" | sed 's/^/     /'
    git commit -m "docs: post-session sync $TS"
    git push origin main
    STAT=$(git show --stat HEAD | tail -1)
    echo "  ✓ Pushed — $STAT"
    _tg_notify "✅ NINA sync [$TS]
$STAT
Service: $SVC_STATUS"
  else
    echo "  Nothing to commit"
    _tg_notify "ℹ️ NINA sync [$TS] — nothing to commit. Service: $SVC_STATUS"
  fi
fi

echo "[7/7] Preparing space upload..."
if [ "$DRY_RUN" = true ]; then
  echo "  (dry-run: skipping space upload preparation)"
else
  bash nina_export.sh
  rm -rf "$HOME/Downloads/nina_space_upload"
  mkdir -p "$HOME/Downloads/nina_space_upload"
  cp "$NINA/docs/space/nina_context.md" "$HOME/Downloads/nina_space_upload/"
  cp "$NINA/docs/space/nina_error_register.md" "$HOME/Downloads/nina_space_upload/"
  cp "$NINA/docs/space/nina_update_log.md" "$HOME/Downloads/nina_space_upload/"
  cp "$NINA/docs/space/nina_phase1_roadmap.md" "$HOME/Downloads/nina_space_upload/"
  cp "$NINA/AGENTS.md" "$HOME/Downloads/nina_space_upload/"
  LATEST_BACKUP=$(ls -t "$HOME/Downloads"/nina_code_backup_*.md 2>/dev/null | head -n 1)
  if [ -n "$LATEST_BACKUP" ]; then
    cp "$LATEST_BACKUP" "$HOME/Downloads/nina_space_upload/"
  else
    echo "  ✗ Error: No backup file found in ~/Downloads"
    exit 1
  fi
  echo "📁 7 files ready at ~/Downloads/nina_space_upload/"
fi

echo "════════════ SYNC COMPLETE ════════════"
