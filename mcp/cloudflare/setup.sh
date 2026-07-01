#!/usr/bin/env bash
# NinaMCP P1 — Cloudflare Tunnel setup
# Exposes localhost:7432 at a persistent public URL for live MCP.
# Uses systemctl --user (no sudo required).
# =============================================================================
set -euo pipefail

NINA_ROOT="${NINA_ROOT:-$HOME/nina}"
TUNNEL_NAME="nina-mcp"
LOCAL_PORT="7432"

echo "[nina-cf] NinaMCP Cloudflare Tunnel setup"
echo "[nina-cf] Tunnel name: $TUNNEL_NAME"
echo "[nina-cf] Local port: $LOCAL_PORT"
echo ""

# ── Step 1: Install cloudflared ───────────────────────────────────────────────
if ! command -v cloudflared &>/dev/null; then
  echo "[nina-cf] Downloading cloudflared…"
  ARCH=$(uname -m)
  if [[ "$ARCH" == "x86_64" ]]; then
    BIN="cloudflared-linux-amd64"
  elif [[ "$ARCH" == "aarch64" ]]; then
    BIN="cloudflared-linux-arm64"
  else
    echo "[nina-cf] ERROR: Unsupported arch: $ARCH" >&2
    exit 1
  fi
  curl -fsSL "https://github.com/cloudflare/cloudflared/releases/latest/download/$BIN" \
    -o "$HOME/.local/bin/cloudflared"
  chmod +x "$HOME/.local/bin/cloudflared"
  mkdir -p "$HOME/.local/bin"
  echo "[nina-cf] cloudflared installed to ~/.local/bin/cloudflared"
  echo "[nina-cf] Add ~/.local/bin to PATH if not already there:"
  echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
else
  echo "[nina-cf] cloudflared already installed: $(cloudflared --version 2>&1 | head -1)"
fi

# ── Step 2: Quick-start option (no domain needed) ────────────────────────────
echo ""
echo "[nina-cf] OPTION A — Quick PoC (no domain, URL changes on restart):"
echo "  cloudflared tunnel --url http://localhost:$LOCAL_PORT"
echo "  Copy the *.trycloudflare.com URL and add it to Perplexity Space MCP settings."
echo ""
echo "[nina-cf] OPTION B — Permanent named tunnel (requires Cloudflare domain):"
echo "  1. cloudflared tunnel login"
echo "  2. cloudflared tunnel create $TUNNEL_NAME"
echo "  3. cloudflared tunnel route dns $TUNNEL_NAME nina-mcp.YOUR_DOMAIN.com"
echo "  4. Run: $NINA_ROOT/mcp/cloudflare/install_service.sh"
echo ""

# ── Quick-start execution ─────────────────────────────────────────────────────
read -rp "[nina-cf] Start quick PoC tunnel now? (y/N): " answer
if [[ "${answer,,}" == "y" ]]; then
  echo "[nina-cf] Starting trycloudflare tunnel on port $LOCAL_PORT…"
  echo "[nina-cf] Watch for 'Your quick Tunnel has been created' URL below:"
  echo ""
  exec cloudflared tunnel --url "http://localhost:$LOCAL_PORT"
fi

echo "[nina-cf] Setup guidance printed. Run option A or B above to proceed."
