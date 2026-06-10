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
fi
