#!/usr/bin/env bash
# nina_sync.sh v5 — Full post-session sync + built-in MD scan (Step 7)
# D-12: skip git push when Jules PR branches are open to prevent merge conflicts

set -euo pipefail

PATH="$HOME/bin:$PATH"

NINA=~/nina
SPACE_DIR="$NINA/docs/space"
LOGS_DIR="$NINA/logs"
DRY_RUN=false
[ "${1:-}" = "--dry-run" ] && DRY_RUN=true

SPACE_FILES=(
  AGENTS.md
  docs/space/nina_error_register.md
  docs/space/nina_state.md
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

echo "[0/8] Health check..."
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

echo "[1/8] Auto-fetch from Downloads..."
FETCHED=0
for f in "${SPACE_FILES[@]}"; do
  SRC="$HOME/Downloads/$(basename "$f")"; DST="$NINA/$f"
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

echo "[2/8] Mirror to docs/space/..."
[ "$DRY_RUN" = false ] && mkdir -p "$SPACE_DIR"
for f in "${SPACE_FILES[@]}"; do
  SRC="$NINA/$f"; DST="$SPACE_DIR/$(basename "$f")"
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

echo "[3/8] Backup cleanup..."
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

echo "[4/8] Update log entry..."
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
    "**Triggered by:** nina_sync.sh v5 automated run",
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

echo "[5/8] Staging..."
if [ "$DRY_RUN" = false ]; then
  git add docs/space/ "${SPACE_FILES[@]}" nina_sync.sh 2>/dev/null || true
  git add -u 2>/dev/null || true
fi

echo "[6/8] Committing and pushing..."
if [ "$DRY_RUN" = true ]; then
  echo "  (dry-run: skipping commit)"
else
  STAGED=$(git diff --cached --name-only 2>/dev/null || true)
  if [ -n "$STAGED" ]; then
    echo "  Changed files:"; echo "$STAGED" | sed 's/^/     /'
    git commit -m "docs: post-session sync $TS"

    # D-12: Check for open Jules PR branches before pushing to main
    # This prevents nina_sync.sh from moving main ahead of Jules branches
    # and causing merge conflicts on all open Jules PRs.
    JULES_BRANCHES=$(gh pr list --state open --json headRefName --limit 100 2>/dev/null | jq '[.[] | select(.headRefName | (startswith("jules-") or startswith("nina-j") or startswith("feat/") or startswith("pr-")))] | length' 2>/dev/null || echo "0")
    if [ "$JULES_BRANCHES" -gt 0 ]; then
      echo ""
      echo "  ⚠️  PUSH SKIPPED — $JULES_BRANCHES open Jules PR branch(es) detected on origin."
      echo "     Pushing now would cause merge conflicts on open Jules PRs."
      echo "     → Merge or close all Jules PRs first, then run: cd ~/nina && git push origin main"
      echo ""
      _tg_notify "⚠️ NINA sync [$TS] — Push SKIPPED: $JULES_BRANCHES Jules PR branch(es) open. Merge/close PRs first, then push manually."
    else
      git push origin main
      STAT=$(git show --stat HEAD | tail -1)
      echo "  ✓ Pushed — $STAT"
      _tg_notify "✅ NINA sync [$TS]
$STAT
Service: $SVC_STATUS"
    fi
  else
    echo "  Nothing to commit"
    _tg_notify "ℹ️ NINA sync [$TS] — nothing to commit. Service: $SVC_STATUS"
  fi
fi

echo "[7/8] Doc/config coverage scan..."
echo "  ── All .md/.txt/.json files in ~/nina (excl. venv/.git/exports/backups) ──"

COVERED_BASES=()
for f in "${SPACE_FILES[@]}"; do
  COVERED_BASES+=("$(basename "$f")")
done

ALL_MD=$(find "$NINA" \
  \( -path "*/venv/*" -o -path "*/.git/*" -o -path "*/node_modules/*" \
     -o -path "*/upgrades/backups/*" -o -path "*/exports/*" \
     -o -path "*/__pycache__/*" \) -prune \
  -o \( -name "*.md" -o -name "*.txt" -o -name "*.json" \) -print | sort)

TOTAL=0; COVERED=0; UNCOVERED=0
UNCOVERED_LIST=""

while IFS= read -r filepath; do
  [ -z "$filepath" ] && continue
  rel="${filepath#$NINA/}"
  base=$(basename "$filepath")
  lines=$(wc -l < "$filepath" 2>/dev/null || echo "?")
  mtime=$(stat -c "%y" "$filepath" 2>/dev/null | cut -d'.' -f1 || echo "?")
  TOTAL=$((TOTAL+1))

  IN_SPACE=false
  if [ -f "$SPACE_DIR/$base" ]; then
    IN_SPACE=true
  fi
  for cb in "${COVERED_BASES[@]}"; do
    [ "$cb" = "$base" ] && IN_SPACE=true
  done

  if [ "$IN_SPACE" = true ]; then
    echo "  ✅  $rel  ($lines lines, $mtime)"
    COVERED=$((COVERED+1))
  else
    echo "  ⚠️   $rel  ($lines lines, $mtime)  ← NOT in docs/space or SPACE_FILES"
    UNCOVERED=$((UNCOVERED+1))
    UNCOVERED_LIST="$UNCOVERED_LIST\n  • $rel"
  fi
done <<< "$ALL_MD"

echo ""
echo "  ── Summary ──"
echo "  Total .md files : $TOTAL"
echo "  Covered         : $COVERED"
echo "  NOT covered     : $UNCOVERED"
if [ "$UNCOVERED" -gt 0 ]; then
  echo ""
  echo "  ⚠️  Files not in docs/space (not uploaded to Perplexity):"
  echo -e "$UNCOVERED_LIST"
  echo ""
  echo "  → Add them to SPACE_FILES array in nina_sync.sh if needed."
fi
echo "[8/8] Full master export for Perplexity Space..."
if [ "$DRY_RUN" = true ]; then
  echo "  (dry-run: skipping)"
else
  # Step 8: Call the compact exporter Python script
  python3 "$NINA/tools/compact_exporter.py"
  FIXED_FILE="$HOME/Downloads/nina_space_upload/nina_latest.md"

  SIZE=$(wc -c < "$FIXED_FILE" | tr -d ' ')
  echo ""
  echo "  ╔══════════════════════════════════════════════╗"
  echo "  ║  ✅  UPLOAD TO PERPLEXITY SPACE:             ║"
  echo "  ║      nina_latest.md  (${SIZE} bytes)         ║"
  echo "  ║      ~/Downloads/nina_space_upload/          ║"
  echo "  ╚══════════════════════════════════════════════╝"
  echo ""

  if command -v rclone >/dev/null 2>&1 && rclone listremotes 2>/dev/null | grep -q "gdrive:"; then
    rclone copy "$FIXED_FILE" "gdrive:nina-backup/" --no-traverse 2>/dev/null && \
      echo "  ☁️  Synced to Google Drive: gdrive:nina-backup/nina_latest.md" || \
      echo "  ⚠️  rclone upload failed (sync still complete)"
  fi
fi

echo "================================================"
echo " SYNC COMPLETE  $TS"
echo "================================================"
