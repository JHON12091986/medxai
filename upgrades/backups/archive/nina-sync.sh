#!/usr/bin/env bash
set -e
NINA=~/nina
SPACE_FILES=(nina_context.md nina-dev-policy.md nina-phase1-roadmap.md nina_v12_blueprint.md)
echo "================================================"
echo " NINA POST-SESSION SYNC  $(date '+%Y-%m-%d %H:%M')"
echo "================================================"
cd "$NINA"
echo "[1/3] F-02 check..."
CHANGED=$(git status --porcelain core/memory.py data/memory/facts.json 2>/dev/null || true)
[ -n "$CHANGED" ] && git add core/memory.py data/memory/facts.json && git commit -m "feat: personal context injection (F-02)" && echo "F-02 committed" || echo "F-02 already committed"
echo "[2/3] Cleanup..."
[ -f "$NINA/NINACONTEXT.md" ] && rm "$NINA/NINACONTEXT.md"
[ -f "$NINA/nina_update_log.md" ] && rm "$NINA/nina_update_log.md"
[ -f "$NINA/docs/ninacontext.md.bak20260604" ] && rm "$NINA/docs/ninacontext.md.bak20260604"
echo "[3/3] Space mirror..."
mkdir -p "$NINA/docs/space"
for f in "${SPACE_FILES[@]}"; do
    [ -f "$HOME/Downloads/$f" ] && cp "$HOME/Downloads/$f" "$NINA/docs/space/$f" && echo "Copied $f" || echo "MISSING: $f"
done
git add docs/space/ 2>/dev/null || true
git add -u 2>/dev/null || true
STAGED=$(git diff --cached --name-only)
[ -n "$STAGED" ] && git commit -m "docs: post-session sync $(date '+%Y-%m-%d')" && git push origin main && echo "Pushed" || echo "Nothing to push"
echo "SYNC COMPLETE"
