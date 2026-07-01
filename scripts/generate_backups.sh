#!/usr/bin/env bash
# =============================================================================
# generate_backups.sh v2.0 — NINA Unified Backup
# Produces exactly 2 outputs:
#   1. nina_claude_feed_TIMESTAMP.md  — AI context feed (onboarding snapshot)
#   2. nina_full_backup_TIMESTAMP.md  — Full codebase snapshot
#
# Age guard: skips if last backup < 6 hours old (unless --force passed)
# =============================================================================
set -euo pipefail

NINA_DIR="$HOME/nina"
BACKUP_DIR="$NINA_DIR/upgrades/backups"
mkdir -p "$BACKUP_DIR"

DATETIME=$(date +"%Y-%m-%d %H:%M:%S")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
GIT_HEAD=$(git -C "$NINA_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git -C "$NINA_DIR" branch --show-current 2>/dev/null || echo "unknown")

# ── Age guard (skip if last backup < 6h old, unless --force) ─────────────────
FORCE="${1:-}"
LAST_BACKUP=$(ls -t "$BACKUP_DIR"/nina_full_backup_*.md 2>/dev/null | head -1 || true)
if [[ -z "$FORCE" && -n "$LAST_BACKUP" ]]; then
    LAST_AGE=$(( $(date +%s) - $(stat -c %Y "$LAST_BACKUP") ))
    if [[ "$LAST_AGE" -lt 21600 ]]; then
        echo "[generate_backups] Last backup $(( LAST_AGE/3600 ))h ago — skipping (use --force to override)"
        exit 0
    fi
fi

# =============================================================================
# OUTPUT 1 — Claude Feed (AI onboarding context)
# =============================================================================
CLAUDE_OUT="$BACKUP_DIR/nina_claude_feed_${TIMESTAMP}.md"

{
echo "# NINA Claude Feed"
echo "Generated: $DATETIME | Branch: $GIT_BRANCH | SHA: $GIT_HEAD"
echo ""
echo "> This file is the canonical AI onboarding snapshot for NINA."
echo "> Feed to Claude/GPT/Gemini at session start for full context."
echo ""

CLAUDE_FILES=(
    "AGENTS.md"
    "README.md"
    "nina_context.md"
    "CODEBASE_MAP.md"
    "docs/space/nina_index.md"
    "docs/space/nina_error_register.md"
    "jules_backlog.md"
    "jules_lock.txt"
)

for rel in "${CLAUDE_FILES[@]}"; do
    f="$NINA_DIR/$rel"
    [[ ! -f "$f" ]] && continue
    size=$(stat -c "%s" "$f")
    mtime=$(stat -c "%y" "$f" | cut -d'.' -f1)
    echo "## $rel"
    echo "_Size: ${size}B | Modified: ${mtime}_"
    echo ""
    ext="${f##*.}"
    case "$ext" in
        py) echo '```python' ;;
        sh) echo '```bash' ;;
        json) echo '```json' ;;
        *) echo '```markdown' ;;
    esac
    cat "$f"
    echo '```'
    echo ""
done
} > "$CLAUDE_OUT"

echo "✅ Claude feed → $CLAUDE_OUT"

# =============================================================================
# OUTPUT 2 — Full Backup (complete codebase snapshot)
# =============================================================================
FULL_OUT="$BACKUP_DIR/nina_full_backup_${TIMESTAMP}.md"

PY_COUNT=$(find "$NINA_DIR" -type f -name "*.py" ! -path "*/venv/*" ! -path "*/.venv/*" ! -path "*/__pycache__/*" ! -path "*/.git/*" ! -path "*/upgrades/*" | wc -l)
SH_COUNT=$(find "$NINA_DIR" -type f -name "*.sh" ! -path "*/venv/*" ! -path "*/.venv/*" ! -path "*/.git/*" ! -path "*/upgrades/*" | wc -l)

{
echo "# NINA Full Backup"
echo "Generated: $DATETIME | Branch: $GIT_BRANCH | SHA: $GIT_HEAD"
echo "Python files: $PY_COUNT | Shell files: $SH_COUNT"
echo ""

echo "## Directory Tree"
echo '```'
tree "$NINA_DIR/" -I "venv|.venv|__pycache__|*.pyc|*.log|upgrades|.git|*.tar.gz|*.zip" --prune 2>/dev/null || true
echo '```'
echo ""

echo "## Source Files"
find "$NINA_DIR" -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.json" \)     ! -path "*/venv/*" ! -path "*/.venv/*" ! -path "*/__pycache__/*" ! -path "*/.git/*"     ! -path "*/upgrades/*" ! -path "*/data/dependency_graph*" ! -path "*/data/symbol_map*"     ! -path "*/logs/*" | sort | while read f; do
    rel="${f#$NINA_DIR/}"
    size=$(stat -c "%s" "$f")
    mtime=$(stat -c "%y" "$f" | cut -d'.' -f1)
    echo "### $rel"
    echo "_Size: ${size}B | Modified: ${mtime}_"
    ext="${f##*.}"
    case "$ext" in
        py) echo '```python' ;;
        sh) echo '```bash' ;;
        json) echo '```json' ;;
        *) echo '```markdown' ;;
    esac
    cat "$f"
    echo '```'
    echo ""
done
} > "$FULL_OUT"

echo "✅ Full backup  → $FULL_OUT"

# ── Retention: keep only last 5 of each ──────────────────────────────────────
ls -t "$BACKUP_DIR"/nina_claude_feed_*.md 2>/dev/null | tail -n +6 | xargs rm -f || true
ls -t "$BACKUP_DIR"/nina_full_backup_*.md 2>/dev/null | tail -n +6 | xargs rm -f || true

echo ""
echo "✅ Backup complete. Retained last 5 of each type."
