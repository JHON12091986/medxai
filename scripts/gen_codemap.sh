#!/usr/bin/env bash
# ============================================================
# NINA — gen_codemap.sh
# Regenerates CODEBASE_MAP.md locally then pushes to GitHub.
# Usage:  bash scripts/gen_codemap.sh [--no-push]
# ============================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.."; pwd)"
VENV="${REPO_ROOT}/nina/venv"
SCRIPT="${REPO_ROOT}/tools/generate_codemap.py"
OUTPUT="${REPO_ROOT}/CODEBASE_MAP.md"
PUSH=true

[[ "${1:-}" == "--no-push" ]] && PUSH=false

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " NINA  gen_codemap.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Repo  : $REPO_ROOT"
echo "  Script: $SCRIPT"
echo "  Output: $OUTPUT"
echo ""

# ── 1. activate venv ────────────────────────────────────────
if [[ -f "${VENV}/bin/activate" ]]; then
  source "${VENV}/bin/activate"
  echo "[✓] venv activated: $VENV"
else
  echo "[!] venv not found at $VENV — using system Python3"
fi

# ── 2. run generator ────────────────────────────────────────
echo "[→] Running generate_codemap.py …"
python3 "$SCRIPT"

if [[ ! -f "$OUTPUT" ]]; then
  echo "[✗] Output file not created: $OUTPUT"
  exit 1
fi

LINES=$(wc -l < "$OUTPUT")
echo "[✓] CODEBASE_MAP.md written — ${LINES} lines"

# ── 3. git status check ─────────────────────────────────────
cd "$REPO_ROOT"

if git diff --quiet "$OUTPUT" 2>/dev/null && git ls-files --error-unmatch "$OUTPUT" &>/dev/null; then
  echo "[=] No changes to CODEBASE_MAP.md — nothing to commit."
  exit 0
fi

# ── 4. stage & commit ───────────────────────────────────────
git add "$OUTPUT"
COMMIT_MSG="chore: regenerate CODEBASE_MAP.md [$(date '+%Y-%m-%d %H:%M')]"
git commit -m "$COMMIT_MSG"
echo "[✓] Committed: $COMMIT_MSG"

# ── 5. push ─────────────────────────────────────────────────
if [[ "$PUSH" == true ]]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "[→] Pushing to origin/$BRANCH …"
  git push origin "$BRANCH"
  echo "[✓] Pushed."
else
  echo "[!] --no-push flag set — skipping push."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Done."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
