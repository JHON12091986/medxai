#!/usr/bin/env bash
# NINA Governance Cleanup Script

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR/.."

PYTHON="python3"
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
elif [ -f "ninavenv/bin/python" ]; then
    PYTHON="ninavenv/bin/python"
fi

echo "================================================"
echo " NINA SAFE DUPLICATE CLEANUP"
echo "================================================"

if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "ninavenv" ]; then
        source ninavenv/bin/activate
    else
        echo "\u26a0\ufe0f Virtual environment not found. Proceeding with $PYTHON."
    fi
fi

ONESHOT_PATTERNS=(
    "fix_caps_again.py"
    "modify_agent_final.py"
    "modify_nina_final.py"
    "modify_nina_url_parse.py"
    "modify_ninagate_format.py"
    "commit_message.txt"
    "pr_desc.txt"
)

if [ "$1" == "--purge-oneshots" ] && [ "${2:-}" != "--execute" ]; then
    echo ""
    echo "=== One-shot script purge ==="
    FOUND=0
    for f in "${ONESHOT_PATTERNS[@]}"; do
        if [ -f "$DIR/$f" ]; then
            echo "  \u2714 Would remove: $f"
            FOUND=$((FOUND+1))
        fi
    done
    if [ $FOUND -eq 0 ]; then
        echo "  Nothing to purge — root is already clean."
        exit 0
    fi
    echo ""
    echo "Re-run with --execute to apply."
    exit 0
fi

if [ "$1" == "--purge-oneshots" ] && [ "${2:-}" == "--execute" ]; then
    echo ""
    echo "=== Executing one-shot script purge ==="
    for f in "${ONESHOT_PATTERNS[@]}"; do
        if [ -f "$DIR/$f" ]; then
            git rm -f "$f" 2>/dev/null || rm -f "$DIR/$f"
            echo "  Removed: $f"
        fi
    done
    exit 0
fi

$PYTHON tools/cleanup_duplicates.py "$@"
