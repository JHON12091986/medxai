#!/usr/bin/env bash
# NINA Repository Hygiene Audit Wrapper

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
# Scripts are in scripts/ subdirectory; project root is one level up
cd "$DIR/.."

PYTHON="python3"
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
elif [ -f "ninavenv/bin/python" ]; then
    PYTHON="ninavenv/bin/python"
fi

echo "================================================"
echo " NINA REPOSITORY HYGIENE AUDIT"
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

STRICT_MODE=false
NOTIFY_MODE=false

for arg in "$@"; do
    case $arg in
        --strict)
            STRICT_MODE=true
            shift
            ;;
        --notify)
            NOTIFY_MODE=true
            shift
            ;;
    esac
done

CMD="$PYTHON tools/audit_repo_hygiene.py"

if [ "$STRICT_MODE" = true ]; then
    echo "Running in STRICT mode..."
    CMD="$CMD --strict"
else
    echo "Running in DRY RUN (warn-only) mode..."
fi

if [ "$NOTIFY_MODE" = true ]; then
    echo "Telegram Notifications ENABLED."
    CMD="$CMD --notify"
fi

$CMD
