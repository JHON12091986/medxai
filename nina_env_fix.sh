#!/usr/bin/env bash
set -euo pipefail
NINA="$HOME/nina"
cd "$NINA"

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; BLU='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "${GRN}✓ $*${NC}"; }
warn() { echo -e "${YLW}⚠ $*${NC}"; }
err()  { echo -e "${RED}✗ $*${NC}"; exit 1; }
step() { echo -e "\n${BLU}── $* ──${NC}"; }

step "1/6 STOP SERVICE"
systemctl --user stop nina.service 2>/dev/null && ok "Stopped" || warn "Not running"
sleep 1

step "2/6 FIX EXECSTART PATH"
UNIT="$HOME/.config/systemd/user/nina.service"
if grep -q "nina/venv/bin/python" "$UNIT" 2>/dev/null; then
    sed -i 's|nina/venv/bin/python[^ ]*|nina/.venv/bin/python3|g' "$UNIT"
    ok "ExecStart → .venv/bin/python3"
else
    ok "ExecStart already correct"
fi

step "3/6 READ REAL VALUES FROM .env"
get_val() {
    local k="$1"
    grep -E "^${k}=" "$NINA/.env.local" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '"'"'" | xargs 2>/dev/null || \
    grep -E "^${k}=" "$NINA/.env"       2>/dev/null | tail -1 | cut -d= -f2- | tr -d '"'"'" | xargs 2>/dev/null || true
}

BOT_TOKEN=$(get_val "TELEGRAM_BOT_TOKEN");  [[ -z "$BOT_TOKEN"  ]] && BOT_TOKEN=$(get_val  "TELEGRAMBOTTOKEN")
AUTH_UID=$(get_val "TELEGRAM_CHAT_ID") 2>/dev/null || AUTH_UID=$(get_val "AUTHORIZED_USER_ID")
CHAT_ID=$(get_val   "TELEGRAM_CHAT_ID");    [[ -z "$CHAT_ID"    ]] && CHAT_ID=$(get_val    "TELEGRAMCHATID")
API_KEY=$(get_val   "API_SECRET_KEY");      [[ -z "$API_KEY"    ]] && API_KEY=$(.venv/bin/python3 -c "import secrets; print(secrets.token_urlsafe(32))")

[[ -z "$BOT_TOKEN" ]] && err "TELEGRAM_BOT_TOKEN not found in .env or .env.local"
[[ -z "$AUTH_UID"  ]] && err "TELEGRAM_CHAT_ID not found in .env or .env.local"
[[ -z "$CHAT_ID"   ]] && err "TELEGRAM_CHAT_ID / TELEGRAMCHATID not found — set it manually first"

ok "BOT_TOKEN  = ${BOT_TOKEN:0:10}…"
ok "AUTH_UID   = $AUTH_UID"
ok "CHAT_ID    = ${CHAT_ID:0:6}…"
ok "API_SECRET = SET"

step "4/6 REWRITE .env.local (NORMALISED — BOTH KEY FORMS)"
cp "$NINA/.env.local" "$NINA/.env.local.bak.$(date +%H%M%S)" 2>/dev/null || true

TMP=$(mktemp)
grep -Ev "^(TELEGRAM_BOT_TOKEN|TELEGRAMBOTTOKEN|TELEGRAM_CHAT_ID|TELEGRAMCHATID|AUTHORIZED_USER_ID|API_SECRET_KEY|ALLOWED_USERS)=" \
    "$NINA/.env.local" 2>/dev/null | grep -v '^\${' | grep -v 'valid-chat-id' > "$TMP" || true

cat >> "$TMP" << KEYS

# ── Normalised $(date '+%Y-%m-%d') by nina_env_fix.sh ──
TELEGRAM_BOT_TOKEN=$BOT_TOKEN
TELEGRAMBOTTOKEN=$BOT_TOKEN
AUTHORIZED_USER_ID=$AUTH_UID
TELEGRAM_CHAT_ID=$CHAT_ID
TELEGRAMCHATID=$CHAT_ID
API_SECRET_KEY=$API_KEY
KEYS

mv "$TMP" "$NINA/.env.local"
cp "$NINA/.env.local" "$NINA/.env"
ok ".env.local rewritten + synced to .env"

step "5/6 VERIFY config.py LOADS CLEAN"
PYRESULT=$(.venv/bin/python3 -c "
import sys, os; sys.path.insert(0,'$NINA'); os.chdir('$NINA')
from core.config import load_config
cfg = load_config()
print(f'chat_id={cfg.telegram_chat_id[:6]}... OK')
" 2>&1)
echo "  $PYRESULT"
echo "$PYRESULT" | grep -q "OK" || err "config.py still failing — $PYRESULT"

step "6/6 RELOAD + RESTART"
systemctl --user daemon-reload
systemctl --user restart nina.service
sleep 5
systemctl --user status nina.service --no-pager -l | tail -10

echo -e "\n${GRN}══ ALL DONE ══${NC}  backup → .env.local.bak.*"
