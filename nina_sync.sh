#!/usr/bin/env bash
set -euo pipefail
NINA=~/nina
SPACE_DIR="$NINA/docs/space"
LOGS_DIR="$NINA/logs"
SPACE_FILES=(
  nina_context.md
  nina_problem_log.md
  nina_dev_policy.md
  nina_phase1_roadmap.md
  nina_v12_blueprint.md
  nina_update_log.md
)
TS=$(date '+%Y-%m-%d %H:%M')
echo "================================================"
echo " NINA POST-SESSION SYNC  $TS"
echo "================================================"
cd "$NINA"

echo "[0/4] Health check..."
BAD=$(find "$NINA" -maxdepth 1 \( -name "*-*.md" -o -name "*-*.sh" \) 2>/dev/null || true)
if [ -n "$BAD" ]; then
  echo "  ⚠  Hyphenated filenames found (should be snake_case):"
  echo "$BAD" | sed 's/^/     /'
else
  echo "  ✓ Naming convention consistent"
fi

echo "[1/4] Auto-fetch from Downloads..."
FETCHED=0
for f in "${SPACE_FILES[@]}"; do
  SRC="$HOME/Downloads/$f"
  DST="$NINA/$f"
  if [ -f "$SRC" ]; then
    if ! diff -q "$SRC" "$DST" > /dev/null 2>&1; then
      cp "$SRC" "$DST"
      echo "  ↓ $f (updated from Downloads)"
      FETCHED=$((FETCHED+1))
    else
      echo "  = $f (Downloads copy identical)"
    fi
  fi
done
[ "$FETCHED" -eq 0 ] && echo "  (no Downloads files picked up)"

echo "[2/4] Mirror to docs/space/..."
mkdir -p "$SPACE_DIR"
for f in "${SPACE_FILES[@]}"; do
  SRC="$NINA/$f"
  DST="$SPACE_DIR/$f"
  if [ ! -f "$SRC" ]; then
    echo "  ✗ MISSING: $f"
    continue
  fi
  if [ ! -f "$DST" ] || ! diff -q "$SRC" "$DST" > /dev/null 2>&1; then
    cp "$SRC" "$DST"
    echo "  ✓ $f (updated)"
  else
    echo "  = $f (unchanged)"
  fi
done
for lf in nina_update_log.md nina_problem_log.md; do
  if [ -f "$LOGS_DIR/$lf" ] && [ -f "$NINA/$lf" ]; then
    if ! diff -q "$LOGS_DIR/$lf" "$NINA/$lf" > /dev/null 2>&1; then
      cp "$LOGS_DIR/$lf" "$NINA/$lf"
      echo "  ✓ $lf (synced from logs/)"
    fi
  fi
done

echo "[3/4] Staging..."
git add docs/space/ "${SPACE_FILES[@]}" 2>/dev/null || true
git add -u 2>/dev/null || true

echo "[4/4] Committing..."
STAGED=$(git diff --cached --name-only 2>/dev/null || true)
if [ -n "$STAGED" ]; then
  echo "  Changed files:"
  echo "$STAGED" | sed 's/^/     /'
  git commit -m "docs: post-session sync $(date '+%Y-%m-%d %H:%M')"
  git push origin main
  echo "  ✓ Pushed"
else
  echo "  Nothing to commit — repo already up to date"
fi

echo "════════════ SYNC COMPLETE ════════════"
