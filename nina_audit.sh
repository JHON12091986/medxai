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

if [ "$1" == "--strict" ]; then
    echo "Running in STRICT mode..."
    python3 tools/audit_repo_hygiene.py --strict
else
    echo "Running in DRY RUN (warn-only) mode..."
    python3 tools/audit_repo_hygiene.py
fi
