#!/usr/bin/env bash
# NinaMCP P1 — Install cloudflared as systemctl --user service
# Run AFTER: cloudflared tunnel login && tunnel create nina-mcp && route dns
# =============================================================================
set -euo pipefail

TUNNEL_NAME="nina-mcp"
LOCAL_PORT="7432"
SERVICE_DIR="$HOME/.config/systemd/user"
CF_CONFIG_DIR="$HOME/.cloudflared"

mkdir -p "$SERVICE_DIR" "$CF_CONFIG_DIR"

# ── Write cloudflared config ──────────────────────────────────────────────────
TUNNEL_ID=$(cloudflared tunnel list 2>/dev/null | awk '/nina-mcp/{print $1}' | head -1)
if [[ -z "$TUNNEL_ID" ]]; then
  echo "ERROR: Tunnel '$TUNNEL_NAME' not found. Run: cloudflared tunnel create $TUNNEL_NAME" >&2
  exit 1
fi
echo "[nina-cf] Tunnel ID: $TUNNEL_ID"

cat > "$CF_CONFIG_DIR/config.yml" << EOF
tunnel: $TUNNEL_ID
credentials-file: $CF_CONFIG_DIR/$TUNNEL_ID.json

ingress:
  - hostname: nina-mcp.YOUR_DOMAIN.com
    service: http://localhost:$LOCAL_PORT
  - service: http_status:404
EOF
echo "[nina-cf] Written: $CF_CONFIG_DIR/config.yml"
echo "[nina-cf] EDIT config.yml — replace 'nina-mcp.YOUR_DOMAIN.com' with your actual hostname."

# ── Write systemd --user unit ─────────────────────────────────────────────────
cat > "$SERVICE_DIR/cloudflared-nina-mcp.service" << EOF
[Unit]
Description=Cloudflare Tunnel — NinaMCP (localhost:$LOCAL_PORT)
After=network.target

[Service]
Type=simple
ExecStart=$(which cloudflared || echo $HOME/.local/bin/cloudflared) tunnel --config $CF_CONFIG_DIR/config.yml run
Restart=on-failure
RestartSec=5
Environment=PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
EOF
echo "[nina-cf] Written: $SERVICE_DIR/cloudflared-nina-mcp.service"

# ── Enable and start ──────────────────────────────────────────────────────────
systemctl --user daemon-reload
systemctl --user enable cloudflared-nina-mcp.service
systemctl --user start  cloudflared-nina-mcp.service

echo ""
echo "[nina-cf] ✅ Cloudflare tunnel service installed and started."
echo "[nina-cf] Check status: systemctl --user status cloudflared-nina-mcp.service"
echo "[nina-cf] Live logs:    journalctl --user -u cloudflared-nina-mcp.service -f"
echo "[nina-cf] Add your public URL to Perplexity Space MCP settings."
