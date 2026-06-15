#!/usr/bin/env bash
# NINA Governance Cleanup Script

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "================================================"
echo " NINA SAFE DUPLICATE CLEANUP"
echo "================================================"

# Check for venv
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "ninavenv" ]; then
        source ninavenv/bin/activate
    else
        echo "⚠️ Virtual environment not found. Proceeding with system python3."
    fi
fi

# ---------------------------------------------------------------------------
# --purge-oneshots : remove stray one-shot modifier scripts from repo root
# These are single-use patch scripts that were never meant to live in root.
# Safe to delete — they are NOT imported by any core module.
# ---------------------------------------------------------------------------
ONESHOT_PATTERNS=(
    "fix_caps_again.py"
    "modify_agent_final.py"
    "modify_nina_final.py"
    "modify_nina_url_parse.py"
    "modify_ninagate_format.py"
    "commit_message.txt"
    "pr_desc.txt"
)

if [ "$1" == "--purge-oneshots" ]; then
    echo ""
    echo "=== One-shot script purge ==="
    FOUND=0
    for f in "${ONESHOT_PATTERNS[@]}"; do
        if [ -f "$DIR/$f" ]; then
            echo "  ✔ Would remove: $f"
            FOUND=$((FOUND+1))
        fi
    done
    if [ $FOUND -eq 0 ]; then
        echo "  Nothing to purge — root is already clean."
        exit 0
    fi
    echo ""
    echo "Found $FOUND file(s). Re-run with --purge-oneshots --execute to delete."
    exit 0
fi

if [ "$1" == "--purge-oneshots" ] && [ "$2" == "--execute" ] || \
   [ "$1" == "--execute" ] && [ "$2" == "--purge-oneshots" ]; then
    echo ""
    echo "=== One-shot script purge (EXECUTE) ==="
    for f in "${ONESHOT_PATTERNS[@]}"; do
        if [ -f "$DIR/$f" ]; then
            rm "$DIR/$f"
            echo "  Ὕ1 Removed: $f"
        fi
    done
    echo "  ✅ Purge complete."
    exit 0
fi

# ---------------------------------------------------------------------------
# Default: duplicate pruning (existing behaviour — unchanged)
# ---------------------------------------------------------------------------
if [ "$1" == "--execute" ]; then
    echo "Running in EXECUTE mode..."
    python3 tools/prune_duplicates.py --execute

    echo ""
    echo "Refreshing Governance Engine..."
    python3 tools/update_index.py
    python3 tools/validate_index.py
    python3 tools/generate_dashboard.py

    echo ""
    echo "✅ Governance refresh complete."
else
    echo "Running in DRY RUN mode..."
    python3 tools/prune_duplicates.py
    echo ""
    echo "To actually delete these files, run: ./nina_cleanup.sh --execute"
    echo ""
    echo "Other options:"
    echo "  ./nina_cleanup.sh --purge-oneshots           # preview stray one-shot scripts"
    echo "  ./nina_cleanup.sh --purge-oneshots --execute # delete them"
fi
