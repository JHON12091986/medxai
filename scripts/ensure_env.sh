#!/bin/bash
# ensure_env.sh — auto-restore ~/nina/.env from .env.local
# Called by: nina.service ExecStartPre + systemd user boot target
# Never commits .env to git (it's in .gitignore)

NINA_DIR="$HOME/nina"
ENV_FILE="$NINA_DIR/.env"
ENV_LOCAL="$NINA_DIR/.env.local"
LOG="$NINA_DIR/runtime/logs/ensure_env.log"
TS=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$(dirname "$LOG")"

if [ ! -f "$ENV_LOCAL" ]; then
    echo "[$TS] ERROR: .env.local not found — cannot restore .env" | tee -a "$LOG"
    exit 1
fi

# Restore if .env is missing, empty, or stale vs .env.local
if [ ! -f "$ENV_FILE" ] || [ ! -s "$ENV_FILE" ] || [ "$ENV_LOCAL" -nt "$ENV_FILE" ]; then
    cp "$ENV_LOCAL" "$ENV_FILE"
    echo "[$TS] .env restored from .env.local" | tee -a "$LOG"
else
    echo "[$TS] .env OK (up to date)" >> "$LOG"
fi

# Validate required keys
REQUIRED=(TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID API_SECRET_KEY TELEGRAM_CHAT_ID)
MISSING=()
for KEY in "${REQUIRED[@]}"; do
    if ! grep -q "^${KEY}=." "$ENV_FILE" 2>/dev/null; then
        MISSING+=("$KEY")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "[$TS] WARNING: missing keys in .env: ${MISSING[*]}" | tee -a "$LOG"
    exit 2
fi

echo "[$TS] All required keys present ✅" >> "$LOG"
exit 0
