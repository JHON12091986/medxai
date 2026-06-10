#!/usr/bin/env bash
# NINA Governance Bootstrap Installer

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "================================================"
echo " NINA GOVERNANCE BOOTSTRAP INSTALLER"
echo "================================================"

# 1. Set Git Hooks Path
echo "[1/3] Configuring local Git hooks..."
git config core.hooksPath git-hooks
chmod +x git-hooks/*
echo "✅ Git hooks configured successfully."

# 2. Check Python Environment
echo "[2/3] Checking Python environment..."
if [ -d "venv" ]; then
    echo "✅ Python virtual environment found (venv)."
    source venv/bin/activate
elif [ -d "ninavenv" ]; then
    echo "✅ Python virtual environment found (ninavenv)."
    source ninavenv/bin/activate
else
    echo "⚠️  No virtual environment found. Proceeding with system python3."
fi

# 3. Initial Validation Run
echo "[3/3] Running initial governance validation..."
python3 tools/update_index.py
if python3 tools/validate_index.py; then
    echo "✅ Governance validation passed."
else
    echo "❌ Governance validation failed. Please fix the reported issues."
    exit 1
fi

if ./nina_audit.sh; then
    echo "✅ Hygiene audit passed."
else
    echo "⚠️ Hygiene audit reported issues. Review docs/space/nina_repo_hygiene_dashboard.md."
fi

echo "================================================"
echo "🎉 NINA Governance installed successfully!"
echo "================================================"
