#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════
#  nina_layout_fix.sh  —  1-click FOLDER_TREE.md alignment
#  Run from: ~/nina    (must be inside the git repo)
#  Safe to re-run:     fully idempotent
# ══════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || git rev-parse --show-toplevel)"
cd "$REPO"
echo "━━━ nina_layout_fix ━━━ repo: $REPO"
echo ""

OK="  ✓"; MV="  →"; ADD="  +"; SKIP="  ="

# ──────────────────────────────────────────────────────────────────────
# 1. CREATE MISSING AGENT CONFIG DOTDIRS
# ──────────────────────────────────────────────────────────────────────
echo "[ 1/4 ] Agent config dotdirs"
for DOTDIR in .agy .gemini .jules; do
  if [ ! -d "$DOTDIR" ]; then
    mkdir -p "$DOTDIR"
    touch "$DOTDIR/.keep"
    git add "$DOTDIR/.keep"
    echo "$ADD $DOTDIR/ created"
  else
    echo "$SKIP $DOTDIR/ already exists"
  fi
done
echo ""

# ──────────────────────────────────────────────────────────────────────
# 2. CREATE juleslock.txt AT ROOT
# ──────────────────────────────────────────────────────────────────────
echo "[ 2/4 ] juleslock.txt"
if [ ! -f "juleslock.txt" ]; then
  touch juleslock.txt
  git add juleslock.txt
  echo "$ADD juleslock.txt created"
else
  echo "$SKIP juleslock.txt already exists"
fi
echo ""

# ──────────────────────────────────────────────────────────────────────
# 3. CREATE prompts/ AND MOVE agy_prompt*.md + agy_antipatterns.md
#    Source: agy/  (confirmed location in live repo)
# ──────────────────────────────────────────────────────────────────────
echo "[ 3/4 ] prompts/ directory"
mkdir -p prompts
MOVED=0
for F in agy_prompt.md agy_prompt_core.md agy_prompt_multifile.md \
          agy_prompt_rules.md agy_antipatterns.md; do
  if [ -f "agy/$F" ] && [ ! -f "prompts/$F" ]; then
    git mv "agy/$F" "prompts/$F"
    echo "$MV agy/$F  →  prompts/$F"
    MOVED=$((MOVED+1))
  elif [ -f "$F" ] && [ ! -f "prompts/$F" ]; then
    git mv "$F" "prompts/$F"
    echo "$MV $F  →  prompts/$F"
    MOVED=$((MOVED+1))
  elif [ -f "prompts/$F" ]; then
    echo "$SKIP prompts/$F already in place"
  fi
done
# git won't stage an empty dir; add a .keep only if prompts is empty
if [ $MOVED -eq 0 ] && [ -z "$(ls -A prompts 2>/dev/null)" ]; then
  touch prompts/.keep && git add prompts/.keep
fi
echo ""

# ──────────────────────────────────────────────────────────────────────
# 4. MOVE nina_sync.sh  →  scripts/nina_sync.sh
# ──────────────────────────────────────────────────────────────────────
echo "[ 4/4 ] nina_sync.sh location"
if [ -f "nina_sync.sh" ] && [ ! -f "scripts/nina_sync.sh" ]; then
  mkdir -p scripts
  git mv nina_sync.sh scripts/nina_sync.sh
  echo "$MV nina_sync.sh  →  scripts/nina_sync.sh"
elif [ -f "scripts/nina_sync.sh" ] && [ ! -f "nina_sync.sh" ]; then
  echo "$SKIP scripts/nina_sync.sh already correct"
elif [ -f "nina_sync.sh" ] && [ -f "scripts/nina_sync.sh" ]; then
  echo "  ⚠  both root & scripts/ copy exist — removing root duplicate"
  git rm nina_sync.sh
fi
echo ""

# ──────────────────────────────────────────────────────────────────────
# COMMIT (or report clean)
# ──────────────────────────────────────────────────────────────────────
if git diff --cached --quiet; then
  echo "━━━ ✅  Nothing to commit — repo already matches FOLDER_TREE.md spec."
else
  git commit -m "chore: align repo layout to FOLDER_TREE.md

- Add .agy/ .gemini/ .jules/ agent config dotdirs
- Add juleslock.txt at root
- Create prompts/, move agy_prompt*.md + agy_antipatterns.md from agy/
- Move nina_sync.sh → scripts/nina_sync.sh"

  echo ""
  echo "━━━ ✅  Done. Now run:  git push"
fi
