#!/usr/bin/env bash
# =============================================================================
# install_ninamcp.sh — 1-click fix for NinaMCP server dependencies
# Ensures mcp + fastmcp-slim[server] are installed inside ~/nina/venv
# Usage: bash scripts/install_ninamcp.sh
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PIP="$REPO_ROOT/venv/bin/pip"
VENV_PYTHON="$REPO_ROOT/venv/bin/python"

echo "[ninamcp] Repo root : $REPO_ROOT"
echo "[ninamcp] Venv pip  : $VENV_PIP"
echo "[ninamcp] Python    : $($VENV_PYTHON --version)"

# Sanity check — venv must exist
if [[ ! -f "$VENV_PIP" ]]; then
    echo "[ninamcp] ERROR: venv not found at $REPO_ROOT/venv"
    echo "          Run: python3 -m venv $REPO_ROOT/venv"
    exit 1
fi

# Wipe stale mcp/fastmcp installs
echo "[ninamcp] Removing old mcp/fastmcp installs..."
"$VENV_PIP" uninstall -y mcp fastmcp fastmcp-slim 2>/dev/null || true

# Reinstall — fastmcp-slim[server] is the correct server-capable package
echo "[ninamcp] Installing mcp + fastmcp-slim[server]..."
"$VENV_PIP" install --quiet "mcp" "fastmcp-slim[server]"

# Verify FastMCP imports cleanly — run from /tmp to avoid cwd shadowing nina/mcp/
echo "[ninamcp] Verifying FastMCP import (from /tmp to avoid path shadowing)..."
if cd /tmp && "$VENV_PYTHON" -c "from fastmcp import FastMCP; print('[ninamcp] FastMCP OK:', FastMCP)"; then
    echo "[ninamcp] ✓ mcp + fastmcp-slim[server] installed correctly"
else
    echo "[ninamcp] ERROR: FastMCP still not importable"
    echo "          Run: $VENV_PIP show mcp fastmcp-slim"
    exit 1
fi
cd "$REPO_ROOT"

# Smoke test — server should wait silently on stdin (timeout 124 = success)
echo "[ninamcp] Smoke-testing ninamcp.server (2s timeout)..."
set +e
timeout 2s "$VENV_PYTHON" -m ninamcp.server 2>/tmp/ninamcp_smoke.log
SMOKE_EXIT=$?
set -e

if [[ $SMOKE_EXIT -eq 124 ]]; then
    echo "[ninamcp] ✓ Server started and waited on stdin — all good"
elif [[ $SMOKE_EXIT -eq 0 ]]; then
    echo "[ninamcp] ✓ Server exited cleanly"
else
    echo "[ninamcp] WARNING: Server exited with code $SMOKE_EXIT"
    echo "--- stderr ---"
    cat /tmp/ninamcp_smoke.log
fi

echo ""
echo "========================================"
echo " NinaMCP ready. Restart OpenCode now."
echo " Server: $VENV_PYTHON -m ninamcp.server"
echo "========================================"
