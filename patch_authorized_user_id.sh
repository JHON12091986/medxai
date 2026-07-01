#!/usr/bin/env bash
# patch_authorized_user_id.sh
# One-shot patcher: replaces all AUTHORIZED_USER_ID / authorized_user_id
# refs across live code with TELEGRAM_CHAT_ID / telegram_chat_id.
#
# Run from ~/nina:
#   chmod +x patch_authorized_user_id.sh
#   bash patch_authorized_user_id.sh
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${BLUE}[PATCH]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC}    $*"; }
warn() { echo -e "${YELLOW}[SKIP]${NC}  $*"; }

# ---------------------------------------------------------------------------
# 1. checks/env_checks.py
#    AUTHORIZED_USER_ID blocker → TELEGRAM_CHAT_ID
# ---------------------------------------------------------------------------
F="checks/env_checks.py"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/("AUTHORIZED_USER_ID",  "config.missing_env.authorizeduserid")/("TELEGRAM_CHAT_ID",     "config.missing_env.telegramchatid")/g' \
    "$F"
  # Remove the now-duplicate ADVISORY_KEYS entry for TELEGRAMCHATID
  # (TELEGRAM_CHAT_ID is now a BLOCKER, not advisory)
  sed -i \
    '/"config.missing_env.telegramchatid".*ADVISORY/d' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 2. interfaces/cli_interface.py
#    uid = env.get("AUTHORIZED_USER_ID", "")  → TELEGRAM_CHAT_ID
#    authorized_user_id=uid                   → telegram_chat_id=uid
# ---------------------------------------------------------------------------
F="interfaces/cli_interface.py"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/env.get("AUTHORIZED_USER_ID", "")/env.get("TELEGRAM_CHAT_ID", "") or env.get("AUTHORIZED_USER_ID", "")/g' \
    "$F"
  sed -i \
    's/authorized_user_id=uid/telegram_chat_id=uid/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 3. core/task_manager/dispatcher.py
#    os.environ.get("AUTHORIZED_USER_ID") → TELEGRAM_CHAT_ID
#    cfg.authorized_user_id               → cfg.telegram_chat_id
# ---------------------------------------------------------------------------
F="core/task_manager/dispatcher.py"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/os.environ.get("AUTHORIZED_USER_ID")/os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("AUTHORIZED_USER_ID")/g' \
    "$F"
  sed -i \
    's/getattr(cfg, "authorized_user_id", None)/getattr(cfg, "telegram_chat_id", None)/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 4. tools/jules.py
#    module-level CHAT_ID = os.environ.get("AUTHORIZED_USER_ID")
#    cfg.authorized_user_id in session_end()
# ---------------------------------------------------------------------------
F="tools/jules.py"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/CHAT_ID = os.environ.get("AUTHORIZED_USER_ID")/CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("AUTHORIZED_USER_ID")/g' \
    "$F"
  sed -i \
    's/cfg.authorized_user_id/cfg.telegram_chat_id/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 5. tools/pipeline_autopilot.py
#    _send_telegram: os.environ.get("AUTHORIZED_USER_ID")
# ---------------------------------------------------------------------------
F="tools/pipeline_autopilot.py"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/chat_id = os.environ.get("AUTHORIZED_USER_ID")/chat_id = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("AUTHORIZED_USER_ID")/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 6. tools/guardian_engine.py
#    "AUTHORIZED_USER_ID" in required keys list
#    "AUTHORIZED_USER_ID missing from .env" title string
# ---------------------------------------------------------------------------
F="tools/guardian_engine.py"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/"AUTHORIZED_USER_ID",/"TELEGRAM_CHAT_ID",/g' \
    "$F"
  sed -i \
    's/"AUTHORIZED_USER_ID missing from .env"/"TELEGRAM_CHAT_ID missing from .env"/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 7. bin/guardian
#    check_env_key "AUTHORIZED_USER_ID" "BLOCKER"
# ---------------------------------------------------------------------------
F="bin/guardian"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/check_env_key "AUTHORIZED_USER_ID"   "BLOCKER"/check_env_key "TELEGRAM_CHAT_ID"    "BLOCKER"/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 8. scripts/ensure_env.sh
#    REQUIRED=(... AUTHORIZED_USER_ID ...)
# ---------------------------------------------------------------------------
F="scripts/ensure_env.sh"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/AUTHORIZED_USER_ID/TELEGRAM_CHAT_ID/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 9. .env.example — comment out AUTHORIZED_USER_ID line, keep as tombstone
# ---------------------------------------------------------------------------
F=".env.example"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/^AUTHORIZED_USER_ID=.*$/# AUTHORIZED_USER_ID= # DEAD — use TELEGRAM_CHAT_ID instead/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 10. .env.local.template — same tombstone treatment
# ---------------------------------------------------------------------------
F=".env.local.template"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/^AUTHORIZED_USER_ID=.*$/# AUTHORIZED_USER_ID= # DEAD — use TELEGRAM_CHAT_ID instead/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 11. nina_env_fix.sh
#    AUTH_UID=$(get_val "AUTHORIZED_USER_ID")
# ---------------------------------------------------------------------------
F="nina_env_fix.sh"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/AUTH_UID=$(get_val  "AUTHORIZED_USER_ID")/AUTH_UID=$(get_val "TELEGRAM_CHAT_ID") 2>\/dev\/null || AUTH_UID=$(get_val "AUTHORIZED_USER_ID")/g' \
    "$F"
  sed -i \
    's/\[\[ -z "\$AUTH_UID"  \]\] && err "AUTHORIZED_USER_ID not found/[[ -z "$AUTH_UID"  ]] \&\& err "TELEGRAM_CHAT_ID not found/g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 12. scripts/nina_diag.py
#    "AUTHORIZED_USER_ID" in REQUIRED_KEYS list
# ---------------------------------------------------------------------------
F="scripts/nina_diag.py"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/"AUTHORIZED_USER_ID", /"TELEGRAM_CHAT_ID", /g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# 13. nina_fix.sh  — env key audit array
# ---------------------------------------------------------------------------
F="nina_fix.sh"
if [[ -f "$F" ]]; then
  log "$F"
  sed -i \
    's/AUTHORIZED_USER_ID /TELEGRAM_CHAT_ID /g' \
    "$F"
  ok "$F patched"
else
  warn "$F not found"
fi

# ---------------------------------------------------------------------------
# Compile-check all patched .py files
# ---------------------------------------------------------------------------
echo ""
log "Running py_compile on patched Python files..."
PY_OK=0; PY_FAIL=0
for pyf in \
  checks/env_checks.py \
  interfaces/cli_interface.py \
  core/task_manager/dispatcher.py \
  tools/jules.py \
  tools/pipeline_autopilot.py \
  tools/guardian_engine.py \
  scripts/nina_diag.py; do
  if [[ -f "$pyf" ]]; then
    if python3 -m py_compile "$pyf" 2>/dev/null; then
      ok "$pyf compiles OK"
      (( PY_OK++ )) || true
    else
      echo -e "\033[0;31m[FAIL]\033[0m  $pyf COMPILE ERROR"
      (( PY_FAIL++ )) || true
    fi
  fi
done

# ---------------------------------------------------------------------------
# Git commit + push
# ---------------------------------------------------------------------------
echo ""
log "Staging and committing..."
git add \
  checks/env_checks.py \
  interfaces/cli_interface.py \
  core/task_manager/dispatcher.py \
  tools/jules.py \
  tools/pipeline_autopilot.py \
  tools/guardian_engine.py \
  bin/guardian \
  scripts/ensure_env.sh \
  .env.example \
  .env.local.template \
  nina_env_fix.sh \
  scripts/nina_diag.py \
  nina_fix.sh \
  2>/dev/null || true

git diff --cached --name-only

if git diff --cached --quiet; then
  warn "Nothing to commit — files may already be patched."
else
  git commit -m "fix: replace AUTHORIZED_USER_ID with TELEGRAM_CHAT_ID across all live code

- checks/env_checks.py: BLOCKER key → TELEGRAM_CHAT_ID
- interfaces/cli_interface.py: constructor arg → telegram_chat_id
- core/task_manager/dispatcher.py: env + cfg attr
- tools/jules.py: module-level CHAT_ID + session_end cfg attr
- tools/pipeline_autopilot.py: _send_telegram helper
- tools/guardian_engine.py: required keys + error strings
- bin/guardian: check_env_key blocker
- scripts/ensure_env.sh: REQUIRED array
- .env.example + .env.local.template: tombstone comments
- nina_env_fix.sh + scripts/nina_diag.py + nina_fix.sh: misc refs"
  git push origin main
  echo ""
  ok "All patches committed and pushed to origin/main."
fi

echo ""
echo -e "${GREEN}=== PATCH COMPLETE ===${NC}"
echo "PY compile OK: $PY_OK  FAIL: $PY_FAIL"
if [[ $PY_FAIL -gt 0 ]]; then
  echo -e "${YELLOW}Fix compile errors above before restarting NINA.${NC}"
  exit 1
fi
echo ""
echo "Next steps:"
echo "  1. Edit .env — remove AUTHORIZED_USER_ID line"
echo "  2. .venv/bin/python tools/nina_ssot.py --report"
echo "  3. systemctl --user restart nina"
