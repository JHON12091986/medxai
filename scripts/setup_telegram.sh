#!/usr/bin/env bash
# =============================================================================
# NINA TELEGRAM SETUP — scripts/setup_telegram.sh
# One-click: sets TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in ~/nina/.env
# The ouroboros service already loads .env via EnvironmentFile=.
# Run: bash ~/nina/scripts/setup_telegram.sh
# =============================================================================
set -euo pipefail

ENV_FILE="${HOME}/nina/.env"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   NINA — Telegram Notification Setup    ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Step 1: Create a bot → message @BotFather on Telegram → /newbot"
echo "Step 2: Get your chat ID → message @userinfobot on Telegram"
echo ""

# ── Read token ──────────────────────────────────────────────────────────────
current_token=$(grep -oP 'TELEGRAM_BOT_TOKEN=\K.*' "${ENV_FILE}" 2>/dev/null || true)
if [[ -n "${current_token}" ]]; then
    echo "Current token: ${current_token:0:12}..."
    read -rp "Bot token [press Enter to keep]: " input_token
    BOT_TOKEN="${input_token:-${current_token}}"
else
    read -rp "Bot token (from @BotFather): " BOT_TOKEN
fi
[[ -z "${BOT_TOKEN}" ]] && { echo "ERROR: token cannot be empty."; exit 1; }

# ── Read chat ID ─────────────────────────────────────────────────────────────
current_chat=$(grep -oP 'TELEGRAM_CHAT_ID=\K.*' "${ENV_FILE}" 2>/dev/null || true)
if [[ -n "${current_chat}" ]]; then
    echo "Current chat ID: ${current_chat}"
    read -rp "Chat ID [press Enter to keep]: " input_chat
    CHAT_ID="${input_chat:-${current_chat}}"
else
    read -rp "Chat ID (from @userinfobot): " CHAT_ID
fi
[[ -z "${CHAT_ID}" ]] && { echo "ERROR: chat ID cannot be empty."; exit 1; }

# ── Write to .env ────────────────────────────────────────────────────────────
touch "${ENV_FILE}"
# Remove old lines if present, then append fresh
sed -i '/^TELEGRAM_BOT_TOKEN=/d' "${ENV_FILE}"
sed -i '/^TELEGRAM_CHAT_ID=/d'   "${ENV_FILE}"
echo "TELEGRAM_BOT_TOKEN=${BOT_TOKEN}" >> "${ENV_FILE}"
echo "TELEGRAM_CHAT_ID=${CHAT_ID}"     >> "${ENV_FILE}"

echo ""
echo "✓ Written to ${ENV_FILE}"

# ── Test the bot right now ───────────────────────────────────────────────────
echo "Sending test message..."
response=$(curl -sf --max-time 10 \
    -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d parse_mode="HTML" \
    --data-urlencode text="🐍 <b>NINA Ouroboros</b> connected!
Telegram notifications are live.
<code>$(date '+%Y-%m-%d %H:%M:%S')</code>" \
    2>&1) && echo "✓ Test message sent — check Telegram!" \
          || echo "✗ Send failed. Check token/chat_id. Response: ${response}"

# ── Reload the service so it picks up the new .env ───────────────────────────
echo ""
echo "Reloading nina-ouroboros service..."
systemctl --user daemon-reload
systemctl --user restart nina-ouroboros.service && \
    echo "✓ Service restarted. You will get a startup ping on Telegram." || \
    echo "✗ Service restart failed — run: systemctl --user status nina-ouroboros.service"
echo ""
