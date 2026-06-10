#!/usr/bin/env bash
# NINA Repository Hygiene Audit Wrapper

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "================================================"
echo " NINA REPOSITORY HYGIENE AUDIT"
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

CMD="python3 tools/audit_repo_hygiene.py"

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
