#!/usr/bin/env bash
NINA=~/nina
DOWNLOADS=~/Downloads
declare -A SPACE_SOURCES=(
  [nina_context.md]="$NINA/nina_context.md"
  [nina_dev_policy.md]="$NINA/nina_dev_policy.md"
  [nina_phase1_roadmap.md]="$NINA/nina_phase1_roadmap.md"
  [nina_v12_blueprint.md]="$NINA/nina_v12_blueprint.md"
  [nina_update_log.md]="$NINA/logs/nina_update_log.md"
  [nina_problem_log.md]="$NINA/logs/nina_problem_log.md"
)
echo "================================================"
echo " NINA POST-SESSION SYNC  $(date '+%Y-%m-%d %H:%M')"
echo "================================================"
cd "$NINA"

echo "[0/4] Health check..."
HYPHEN_FILES=$(find "$NINA" -maxdepth 1 -name "nina-*.md" -o -name "nina-*.sh" | sed "s|$NINA/||" | sort)
UNDER_FILES=$(find "$NINA" -maxdepth 1 -name "nina_*.md" -o -name "nina_*.sh" | sed "s|$NINA/||" | sort)
if [ -n "$HYPHEN_FILES" ] && [ -n "$UNDER_FILES" ]; then
  echo "  ⚠ Naming inconsistency detected in ~/nina/ root:"
  echo "    Hyphen files:    $(echo $HYPHEN_FILES | tr ' ' ',')"
  echo "    Underscore files: $(echo $UNDER_FILES | tr ' ' ',')"
  echo "    → Consider standardizing to underscore (see nina_dev_policy.md)"
else
  echo "  ✓ Naming convention consistent"
fi

echo "[1/4] Auto-fetch from Downloads..."
for f in "${!SPACE_SOURCES[@]}"; do
  if [ -f "$DOWNLOADS/$f" ]; then
    cp "$DOWNLOADS/$f" "${SPACE_SOURCES[$f]}" && echo "  ↓ $f (applied)"
    rm "$DOWNLOADS/$f" && echo "    └ cleaned from Downloads"
  fi
done

echo "[2/4] Mirror to docs/space/..."
mkdir -p "$NINA/docs/space"
ALL_OK=true
for f in "${!SPACE_SOURCES[@]}"; do
  src="${SPACE_SOURCES[$f]}"
  dst="$NINA/docs/space/$f"
  if [ -f "$src" ]; then
    if ! cmp -s "$src" "$dst" 2>/dev/null; then
      cp "$src" "$dst" && echo "  ✓ $f (updated)"
    else
      echo "  = $f (unchanged)"
    fi
  else
    echo "  MISSING: $f (expected at $src)"
    ALL_OK=false
  fi
done
$ALL_OK || echo "  ⚠ Some files missing — check above"

echo "[3/4] Staging..."
git add docs/space/ nina_context.md nina_dev_policy.md nina_phase1_roadmap.md \
        nina_v12_blueprint.md core/memory.py data/memory/facts.json \
        nina-sync.sh 2>/dev/null || true
git add -u 2>/dev/null || true

echo "[4/4] Committing..."
STAGED=$(git diff --cached --name-only)
if [ -n "$STAGED" ]; then
  echo "  Changed files:"
  git diff --cached --stat | sed 's/^/    /'
  git commit -m "docs: post-session sync $(date '+%Y-%m-%d %H:%M')"
  git push origin main && echo "  ✓ Pushed"
else
  echo "  Nothing to commit"
fi
echo "════════════ SYNC COMPLETE ════════════"
