#!/usr/bin/env bash
# =================================================================
# nina_rescue.sh — NINA Safe-Mode Bootstrap v1.1
# "Windows Safe Mode" for NINA — detect, fix, infer, emit.
#
# LOOP:
#   1. Forensic detect  (nina_diag.py)
#   2. Self-repair      (pip, pkill, systemctl)
#   3. Smoke-test       (import checks)
#   4. Service restart  (nina + ninagate)
#   5. Infer            (NinaGate->Groq->Mistral->Ollama)
#   6. Emit             (rescue_brief.md for Perplexity)
#   7. Deploy fix       (git pull + run AI-generated script)
#   8. Final report
#
# Usage:
#   bash ~/nina/scripts/nina_rescue.sh           # full rescue
#   bash ~/nina/scripts/nina_rescue.sh --dry-run # diagnose only
#   bash ~/nina/scripts/nina_rescue.sh --phase 3 # start at phase N
#   bash ~/nina/scripts/nina_rescue.sh --force   # skip idempotency
# =================================================================
set -uo pipefail

# -- Config -------------------------------------------------------
NINA_DIR="${HOME}/nina"
VENV="${NINA_DIR}/.venv"
PY="${VENV}/bin/python3"
PIP="${VENV}/bin/pip"
DATA_DIR="${NINA_DIR}/data"
LOGS_DIR="${NINA_DIR}/logs"
ENV_FILE="${NINA_DIR}/.env"
IDEM_LEDGER="${DATA_DIR}/rescue_idempotency.json"
BRIEF_FILE="${DATA_DIR}/rescue_brief.md"
RESCUE_LOG="${LOGS_DIR}/nina_rescue.log"
FIX_SCRIPTS_DIR="${DATA_DIR}/rescue_fixes"
NINAGATE_URL="http://localhost:7860"
OLLAMA_URL="http://localhost:11434"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
DATE_HUMAN=$(date '+%Y-%m-%d %H:%M:%S %Z')
RESCUE_ID="rescue_${TIMESTAMP}"
VERSION="1.1"

# -- CLI flags ----------------------------------------------------
DRY_RUN=false
FORCE=false
START_PHASE=1
for arg in "$@"; do
  case "$arg" in
    --dry-run)  DRY_RUN=true ;;
    --force)    FORCE=true ;;
    --phase=*)  START_PHASE="${arg#--phase=}" ;;
  esac
done

# -- Colors -------------------------------------------------------
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'
CYN='\033[0;36m'; MAG='\033[0;35m'; BLD='\033[1m'
DIM='\033[2m'; RST='\033[0m'

# -- Bootstrap dirs + log -----------------------------------------
mkdir -p "${DATA_DIR}" "${LOGS_DIR}" "${FIX_SCRIPTS_DIR}"
exec > >(tee -a "${RESCUE_LOG}") 2>&1

# -- Helpers ------------------------------------------------------
banner() {
  echo -e "\n${CYN}${BLD}+------------------------------------------------------+"
  echo -e   "| NINA RESCUE  |  Phase $1/$2  |  $3"
  echo -e   "+------------------------------------------------------+${RST}"
}
ok()   { echo -e "  ${GRN}[OK]${RST}  $*"; }
warn() { echo -e "  ${YLW}[WN]${RST}  $*"; }
fail() { echo -e "  ${RED}[!!]${RST}  $*"; }
info() { echo -e "  ${DIM}[..]${RST}  $*"; }
step() { echo -e "  ${MAG}[>>]${RST}  $*"; }

# FIX: tr -d removes only double-quote; use single-arg form with no quoting magic
env_val() {
  [[ -f "$ENV_FILE" ]] || { echo ""; return; }
  local raw
  raw=$(grep -E "^${1}=" "$ENV_FILE" | head -1 | cut -d= -f2-)
  # strip surrounding double or single quotes
  raw="${raw#\"}"; raw="${raw%\"}"
  raw="${raw#\'}"; raw="${raw%\'}"
  echo "$raw"
}

idempotent_mark() {
  local op_id="$1" status="$2"
  python3 -c "
import json, time, os
p = '${IDEM_LEDGER}'
d = json.load(open(p)) if os.path.exists(p) else {}
d['${op_id}'] = {'ts': time.time(), 'status': '${status}', 'id': '${RESCUE_ID}'}
with open(p, 'w') as f: json.dump(d, f, indent=2)
" 2>/dev/null || true
}

idempotent_skip() {
  local op_id="$1"
  [[ "$FORCE" == "true" ]] && return 1
  python3 -c "
import json, sys, time, os
p = '${IDEM_LEDGER}'
if not os.path.exists(p): sys.exit(1)
d = json.load(open(p))
e = d.get('${op_id}')
if e and (time.time() - e.get('ts', 0)) < 300: sys.exit(0)
sys.exit(1)
" 2>/dev/null
}

curl_json_post() {
  local url="$1" payload="$2" token="$3"
  if [[ -n "$token" ]]; then
    curl -sf -X POST "$url" \
      -H 'Content-Type: application/json' \
      -H "Authorization: Bearer $token" \
      -d "$payload" --max-time 30 2>/dev/null
  else
    curl -sf -X POST "$url" \
      -H 'Content-Type: application/json' \
      -d "$payload" --max-time 30 2>/dev/null
  fi
}

extract_content() {
  python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('choices',[{}])[0].get('message',{}).get('content',''))
except Exception:
    print('')
" 2>/dev/null || echo ""
}

echo -e "${BLD}${CYN}"
echo "  ███╗   ██╗██╗███╗   ██╗ █████╗     ██████╗ ███████╗███████╗ ██████╗██╗   ██╗███████╗"
echo "  ████╗  ██║██║████╗  ██║██╔══██╗    ██╔══██╗██╔════╝██╔════╝██╔════╝██║   ██║██╔════╝"
echo "  ██╔██╗ ██║██║██╔██╗ ██║███████║    ██████╔╝█████╗  ███████╗██║     ██║   ██║█████╗  "
echo "  ██║╚██╗██║██║██║╚██╗██║██╔══██║    ██╔══██╗██╔══╝  ╚════██║██║     ██║   ██║██╔══╝  "
echo "  ██║ ╚████║██║██║ ╚████║██║  ██║    ██║  ██║███████╗███████║╚██████╗╚██████╔╝███████╗"
echo "  ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚══════╝"
echo -e "${RST}"
echo -e "${BLD}  Safe-Mode Bootstrap  v${VERSION}  |  ${DATE_HUMAN}${RST}"
echo -e "${DIM}  ID: ${RESCUE_ID}  |  Log: ${RESCUE_LOG}${RST}\n"
[[ "$DRY_RUN" == "true" ]] && echo -e "  ${YLW}${BLD}[DRY-RUN MODE - no changes will be made]${RST}\n"

cd "${NINA_DIR}" || { fail "Cannot cd to ${NINA_DIR}"; exit 1; }

# Global state
ROOT_CAUSE=""
IMPORT_ERRORS=""
IMPORT_FAIL=0
NEEDS_INFERENCE=false
INFERENCE_SOURCE=""
FIX_SCRIPT_CONTENT=""

# ================================================================
# PHASE 1 -- FORENSIC DETECT
# ================================================================
if [[ $START_PHASE -le 1 ]]; then
  banner 1 8 "FORENSIC DETECT"
  step "Running nina_diag.py..."
  DIAG_OUT=$("$PY" scripts/nina_diag.py 2>&1 || true)
  echo "$DIAG_OUT" > "${DATA_DIR}/last_diag_raw.txt"
  ROOT_CAUSE=$(echo "$DIAG_OUT" | grep -E 'Unhandled exception:|ModuleNotFoundError|ImportError|SyntaxError|AttributeError|TypeError' | head -3 || echo "")
  SERVICE_STATE=$(systemctl --user is-active nina.service 2>/dev/null || echo "unknown")
  NINAGATE_STATE=$(systemctl --user is-active ninagate.service 2>/dev/null || echo "unknown")
  GHOST_COUNT=$(pgrep -cf 'python.*main\.py' 2>/dev/null || echo 0)
  info "nina.service     : ${SERVICE_STATE}"
  info "ninagate.service : ${NINAGATE_STATE}"
  info "Ghost procs      : ${GHOST_COUNT}"
  info "Root cause hint  : ${ROOT_CAUSE:-none detected}"
  ok "Phase 1 complete"
  idempotent_mark "phase1_detect" "done"
else
  info "Skipping phase 1 (--phase=$START_PHASE)"
  DIAG_OUT=$(cat "${DATA_DIR}/last_diag_raw.txt" 2>/dev/null || echo "")
  ROOT_CAUSE=$(echo "$DIAG_OUT" | grep -E 'ModuleNotFoundError|ImportError|SyntaxError|AttributeError' | head -3 || echo "")
fi

# ================================================================
# PHASE 2 -- SELF-REPAIR
# ================================================================
if [[ $START_PHASE -le 2 ]]; then
  banner 2 8 "SELF-REPAIR"
  if [[ "$DRY_RUN" == "true" ]]; then
    warn "[DRY-RUN] Skipping repair actions"
  else
    # 2a. Kill ghosts
    step "Killing ghost main.py processes..."
    GHOSTS=$(pgrep -f 'python.*main\.py' 2>/dev/null || true)
    if [[ -n "$GHOSTS" ]]; then
      pkill -f 'python.*main\.py' && ok "Killed ghosts" || warn "pkill non-zero"
      sleep 1
    else
      ok "No ghost processes"
    fi

    # 2b. Ensure .venv exists
    step "Checking .venv..."
    if [[ ! -x "$PY" ]]; then
      warn ".venv missing -- creating..."
      python3 -m venv "${VENV}" && "$PIP" install --quiet --upgrade pip
    else
      ok ".venv OK: $($PY --version)"
    fi

    # 2c. Install required packages
    REQUIRED_PACKAGES=(
      sentence-transformers
      python-telegram-bot
      apscheduler
      fastapi
      uvicorn
      httpx
      pydantic
      aiofiles
      psutil
    )
    step "Checking required packages..."
    MISSING_PKGS=()
    for pkg in "${REQUIRED_PACKAGES[@]}"; do
      module="${pkg//-/_}"
      [[ "$module" == "python_telegram_bot" ]] && module="telegram"
      "$PY" -c "import ${module}" 2>/dev/null || MISSING_PKGS+=("$pkg")
    done
    if [[ ${#MISSING_PKGS[@]} -gt 0 ]]; then
      warn "Installing missing: ${MISSING_PKGS[*]}"
      "$PIP" install --quiet "${MISSING_PKGS[@]}" && ok "Installed" || { fail "pip install failed"; exit 1; }
    else
      ok "All required packages present"
    fi

    # 2d. Check .env for critical keys
    step "Checking .env keys..."
    ENV_MISSING=()
    for key in TELEGRAM_BOT_TOKEN AUTHORIZED_USER_ID API_SECRET_KEY; do
      val=$(env_val "$key")
      [[ -z "$val" ]] && ENV_MISSING+=("$key")
    done
    if [[ ${#ENV_MISSING[@]} -gt 0 ]]; then
      warn "Missing .env keys (HUMAN-ACTION-REQUIRED): ${ENV_MISSING[*]}"
    else
      ok ".env critical keys present"
    fi

    # 2e. Remove stale lock/pid files
    step "Clearing stale lock/pid files..."
    for f in "${DATA_DIR}/nina.lock" "${DATA_DIR}/nina.pid"; do
      [[ -f "$f" ]] && { rm -f "$f"; ok "Removed $f"; } || true
    done
  fi
  ok "Phase 2 complete"
  idempotent_mark "phase2_repair" "done"
else
  info "Skipping phase 2"
fi

# ================================================================
# PHASE 3 -- SMOKE-TEST IMPORTS
# ================================================================
if [[ $START_PHASE -le 3 ]]; then
  banner 3 8 "SMOKE-TEST IMPORTS"
  CRITICAL_IMPORTS=(
    "from core.nina import Nina"
    "from core.router import HybridRouter"
    "from core.memory import MemorySystem"
    "from core.scheduler import NinaScheduler"
    "from core.reflexion import ReflexionEngine"
    "from core.observability import get_hub"
    "from core.semantic_router import NINASemanticRouter"
  )
  for imp in "${CRITICAL_IMPORTS[@]}"; do
    err=$("$PY" -c "$imp" 2>&1)
    if [[ $? -eq 0 ]]; then
      ok "$imp"
    else
      fail "$imp"
      info "  $(echo "$err" | tail -1)"
      IMPORT_FAIL=$((IMPORT_FAIL+1))
      IMPORT_ERRORS="${IMPORT_ERRORS}\n  - $imp: $(echo "$err" | tail -1)"
    fi
  done
  if [[ $IMPORT_FAIL -gt 0 ]]; then
    warn "$IMPORT_FAIL import(s) failing -- will attempt inference in Phase 5"
    NEEDS_INFERENCE=true
  else
    ok "All imports clean"
  fi
  idempotent_mark "phase3_imports" "fail=${IMPORT_FAIL}"
else
  info "Skipping phase 3"
fi

# ================================================================
# PHASE 4 -- SERVICE RESTART
# ================================================================
if [[ $START_PHASE -le 4 ]]; then
  banner 4 8 "SERVICE RESTART"
  if [[ "$DRY_RUN" == "true" ]]; then
    warn "[DRY-RUN] Skipping service restart"
  else
    systemctl --user daemon-reload
    if [[ "$NEEDS_INFERENCE" == "true" ]]; then
      warn "Import failures -- skipping nina.service restart until fixed"
    else
      step "Restarting nina.service..."
      systemctl --user restart nina.service && sleep 4
      NINA_ACTIVE=$(systemctl --user is-active nina.service 2>/dev/null || echo "unknown")
      if [[ "$NINA_ACTIVE" == "active" ]]; then
        ok "nina.service ACTIVE"
      else
        fail "nina.service is ${NINA_ACTIVE}"
        info "$(journalctl --user -u nina.service -n 5 --no-pager 2>/dev/null | tail -3)"
        NEEDS_INFERENCE=true
      fi
    fi
    step "Restarting ninagate.service..."
    if systemctl --user cat ninagate.service &>/dev/null; then
      systemctl --user restart ninagate.service && sleep 3
      NG_ACTIVE=$(systemctl --user is-active ninagate.service 2>/dev/null || echo "unknown")
      [[ "$NG_ACTIVE" == "active" ]] && ok "ninagate.service ACTIVE" || warn "ninagate: ${NG_ACTIVE}"
    else
      warn "ninagate.service unit not found"
    fi
  fi
  ok "Phase 4 complete"
  idempotent_mark "phase4_services" "done"
else
  info "Skipping phase 4"
fi

# ================================================================
# PHASE 5 -- INFERENCE CHAIN
# ================================================================
if [[ $START_PHASE -le 5 ]]; then
  banner 5 8 "INFERENCE CHAIN"

  DIAG_RAW=$(head -80 "${DATA_DIR}/last_diag_raw.txt" 2>/dev/null || echo "Diagnostic not available")
  # Build prompt using python to avoid shell quoting hell
  PROMPT=$(python3 - <<PYEOF
import json, textwrap
root = """${ROOT_CAUSE}"""
diag = """${DIAG_RAW:0:1500}"""
msg = f"""You are a NINA infrastructure expert. NINA is Python 3.14 on Ubuntu, systemd user services, .venv, Ollama, Telegram bot.\n\nFailure:\n{root}\n\nDiag:\n{diag}\n\nWrite a single idempotent bash script that fixes the root cause above.\nRules: use only pip install (into .venv), pkill, systemctl --user, git pull.\nSafe to re-run. Print [OK] or [!!] per step. Do NOT touch .env.\nOutput ONLY the bash script, no explanation."""
print(msg)
PYEOF
)

  # 5a. NinaGate local
  step "5a. Trying NinaGate local (${NINAGATE_URL})..."
  NG_HEALTH=$(curl -sf "${NINAGATE_URL}/health" --max-time 5 2>/dev/null || echo "")
  if [[ -n "$NG_HEALTH" ]]; then
    ok "NinaGate reachable"
    NG_PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'messages':[{'role':'user','content':sys.argv[1]}]}))" "$PROMPT" 2>/dev/null || echo '{}')
    FIX_SCRIPT_CONTENT=$(curl_json_post "${NINAGATE_URL}/v1/chat" "$NG_PAYLOAD" "" | extract_content)
    [[ -n "$FIX_SCRIPT_CONTENT" ]] && INFERENCE_SOURCE="NinaGate-local"
  else
    warn "NinaGate not reachable"
  fi

  # 5b. Groq
  if [[ -z "$INFERENCE_SOURCE" ]]; then
    step "5b. Trying Groq..."
    GROQ_KEY=$(env_val "GROQ_API_KEY")
    if [[ -n "$GROQ_KEY" ]]; then
      GROQ_PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'model':'llama3-8b-8192','messages':[{'role':'user','content':sys.argv[1]}],'max_tokens':1500}))" "$PROMPT" 2>/dev/null || echo '{}')
      FIX_SCRIPT_CONTENT=$(curl_json_post "https://api.groq.com/openai/v1/chat/completions" "$GROQ_PAYLOAD" "$GROQ_KEY" | extract_content)
      [[ -n "$FIX_SCRIPT_CONTENT" ]] && { ok "Groq responded"; INFERENCE_SOURCE="Groq"; } || warn "Groq failed"
    else
      warn "GROQ_API_KEY not in .env"
    fi
  fi

  # 5c. Mistral
  if [[ -z "$INFERENCE_SOURCE" ]]; then
    step "5c. Trying Mistral..."
    MISTRAL_KEY=$(env_val "MISTRAL_API_KEY")
    if [[ -n "$MISTRAL_KEY" ]]; then
      MISTRAL_PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'model':'mistral-small-latest','messages':[{'role':'user','content':sys.argv[1]}],'max_tokens':1500}))" "$PROMPT" 2>/dev/null || echo '{}')
      FIX_SCRIPT_CONTENT=$(curl_json_post "https://api.mistral.ai/v1/chat/completions" "$MISTRAL_PAYLOAD" "$MISTRAL_KEY" | extract_content)
      [[ -n "$FIX_SCRIPT_CONTENT" ]] && { ok "Mistral responded"; INFERENCE_SOURCE="Mistral"; } || warn "Mistral failed"
    else
      warn "MISTRAL_API_KEY not in .env"
    fi
  fi

  # 5d. Ollama
  if [[ -z "$INFERENCE_SOURCE" ]]; then
    step "5d. Trying Ollama local..."
    OLLAMA_ALIVE=$(curl -sf "${OLLAMA_URL}/api/tags" --max-time 5 2>/dev/null || echo "")
    if [[ -n "$OLLAMA_ALIVE" ]]; then
      OLLAMA_PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'model':'qwen2.5-coder:3b','prompt':sys.argv[1],'stream':False}))" "$PROMPT" 2>/dev/null || echo '{}')
      FIX_SCRIPT_CONTENT=$(curl_json_post "${OLLAMA_URL}/api/generate" "$OLLAMA_PAYLOAD" "" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('response',''))" 2>/dev/null || echo "")
      [[ -n "$FIX_SCRIPT_CONTENT" ]] && { ok "Ollama responded"; INFERENCE_SOURCE="Ollama-local"; } || warn "Ollama generate failed"
    else
      warn "Ollama not reachable"
    fi
  fi

  # 5e. Save and optionally run AI fix
  if [[ -n "$INFERENCE_SOURCE" && -n "$FIX_SCRIPT_CONTENT" ]]; then
    ok "Inference succeeded via: ${INFERENCE_SOURCE}"
    AI_FIX_PATH="${FIX_SCRIPTS_DIR}/nina_fix_${TIMESTAMP}.sh"
    # Strip markdown code fences if model wrapped it
    echo "$FIX_SCRIPT_CONTENT" | sed '/^```/d' > "$AI_FIX_PATH"
    chmod +x "$AI_FIX_PATH"
    ok "AI fix script saved: ${AI_FIX_PATH}"
    echo ""
    echo -e "  ${YLW}Review: cat ${AI_FIX_PATH}${RST}"
    echo ""
    read -r -t 20 -p "  Execute AI fix script? [y/N] (auto-skip 20s): " EXEC_CHOICE || EXEC_CHOICE="N"
    if [[ "${EXEC_CHOICE,,}" == "y" ]] && [[ "$DRY_RUN" == "false" ]]; then
      bash "$AI_FIX_PATH" && ok "AI fix executed" || fail "AI fix returned non-zero"
    else
      info "Not executed -- run manually: bash ${AI_FIX_PATH}"
    fi
  else
    warn "All inference sources exhausted -- Perplexity brief will be emitted in Phase 6"
  fi
  idempotent_mark "phase5_inference" "source=${INFERENCE_SOURCE:-none}"
else
  info "Skipping phase 5"
fi

# ================================================================
# PHASE 6 -- EMIT PERPLEXITY BRIEF
# ================================================================
if [[ $START_PHASE -le 6 ]]; then
  banner 6 8 "EMIT PERPLEXITY BRIEF"

  # Pre-capture ALL dynamic values before the heredoc
  BRIEF_NINA_STATUS=$(systemctl --user is-active nina.service 2>/dev/null || echo unknown)
  BRIEF_NG_STATUS=$(systemctl --user is-active ninagate.service 2>/dev/null || echo unknown)
  BRIEF_INF_SOURCE="${INFERENCE_SOURCE:-ALL FAILED}"
  BRIEF_ROOT="${ROOT_CAUSE:-Not detected}"
  BRIEF_IMPORT_ERRORS="${IMPORT_ERRORS:-none}"
  BRIEF_DIAG=$(grep -E 'ERROR|Traceback|ModuleNotFound|BLOCKER' "${DATA_DIR}/last_diag_raw.txt" 2>/dev/null | head -20 || echo "No signals")
  BRIEF_PY=$("$PY" --version 2>&1 || echo unknown)
  BRIEF_OS=$(uname -srm)
  BRIEF_DISK=$(df -h "${NINA_DIR}" 2>/dev/null | tail -1 || echo unknown)
  BRIEF_RAM=$(free -h 2>/dev/null | awk '/Mem/{print $4" free of "$2}' || echo unknown)
  BRIEF_COMMITS=$(git -C "${NINA_DIR}" log --oneline -3 2>/dev/null || echo unknown)
  BRIEF_FIX_NAME="scripts/nina_fix_${TIMESTAMP}.sh"

  cat > "$BRIEF_FILE" <<BRIEF_EOF
---
title: NINA Rescue Brief
rescue_id: ${RESCUE_ID}
timestamp: ${DATE_HUMAN}
version: ${VERSION}
inference_attempted: ${BRIEF_INF_SOURCE}
---

# NINA Rescue Brief -- ${DATE_HUMAN}

## Status
- nina.service: ${BRIEF_NINA_STATUS}
- ninagate.service: ${BRIEF_NG_STATUS}
- Inference sources tried: NinaGate-local -> Groq -> Mistral -> Ollama-local
- Inference result: ${BRIEF_INF_SOURCE}

## Root Cause (detected)
${BRIEF_ROOT}
${BRIEF_IMPORT_ERRORS}

## Diagnostic Signals
${BRIEF_DIAG}

## System Context
- Python: ${BRIEF_PY}
- OS: ${BRIEF_OS}
- Disk: ${BRIEF_DISK}
- RAM: ${BRIEF_RAM}
- Last commits:
${BRIEF_COMMITS}

## Already Attempted
- Killed ghost main.py processes
- pip install sentence-transformers + 8 other packages
- Cleared stale lock/pid files
- systemctl --user restart nina + ninagate
- Tried inference: NinaGate -> Groq -> Mistral -> Ollama

## Request for Perplexity Architect Overwatch
Generate a 1-click idempotent bash fix script at:
  ${BRIEF_FIX_NAME}

Rules:
1. Fix the root cause above
2. Idempotent (safe to re-run)
3. Only: pip install (into .venv), pkill, systemctl --user, git pull
4. Do NOT touch .env secrets
5. End with: python scripts/nina_diag.py

Push to: aibony/nina main branch

Deploy after push:
  cd ~/nina && git pull && bash ${BRIEF_FIX_NAME}
BRIEF_EOF

  ok "Rescue brief written: ${BRIEF_FILE}"
  echo ""
  echo -e "  ${YLW}${BLD}+--[ PASTE TO PERPLEXITY ARCHITECT OVERWATCH ]--------+${RST}"
  echo -e "  ${DIM}cat ${BRIEF_FILE}${RST}\n"
  cat "$BRIEF_FILE"
  idempotent_mark "phase6_brief" "done"
else
  info "Skipping phase 6"
fi

# ================================================================
# PHASE 7 -- DEPLOY LOOP
# ================================================================
if [[ $START_PHASE -le 7 ]]; then
  banner 7 8 "DEPLOY LOOP"
  step "Checking for new fix scripts pushed by Architect Overwatch..."
  git -C "${NINA_DIR}" fetch origin main --quiet 2>/dev/null || warn "git fetch failed"
  NEW_FIXES=$(git -C "${NINA_DIR}" diff HEAD origin/main --name-only 2>/dev/null | grep 'scripts/nina_fix_' || echo "")
  if [[ -n "$NEW_FIXES" ]]; then
    ok "New fix script(s) found: $NEW_FIXES"
    if [[ "$DRY_RUN" == "false" ]]; then
      git -C "${NINA_DIR}" pull --quiet
      for fix in $NEW_FIXES; do
        if [[ -f "${NINA_DIR}/${fix}" ]]; then
          chmod +x "${NINA_DIR}/${fix}"
          info "Running: ${fix}"
          bash "${NINA_DIR}/${fix}" && ok "${fix} done" || fail "${fix} failed"
        fi
      done
    else
      warn "[DRY-RUN] Would pull and run: $NEW_FIXES"
    fi
  else
    info "No new fix scripts in origin/main -- Perplexity loop pending"
  fi
  idempotent_mark "phase7_deploy" "done"
else
  info "Skipping phase 7"
fi

# ================================================================
# PHASE 8 -- FINAL REPORT
# ================================================================
banner 8 8 "FINAL REPORT"
NINA_FINAL=$(systemctl --user is-active nina.service 2>/dev/null || echo "unknown")
NG_FINAL=$(systemctl --user is-active ninagate.service 2>/dev/null || echo "unknown")
NG_HTTP=$(curl -s -o /dev/null -w '%{http_code}' "${NINAGATE_URL}/health" --max-time 5 2>/dev/null || echo "000")
IMPORT_FINAL=0
for imp in "from core.nina import Nina" "from core.router import HybridRouter" "from core.semantic_router import NINASemanticRouter"; do
  "$PY" -c "$imp" 2>/dev/null || IMPORT_FINAL=$((IMPORT_FINAL+1))
done

echo ""
if [[ "$NINA_FINAL" == "active" && $IMPORT_FINAL -eq 0 ]]; then
  echo -e "${BLD}${GRN}+------------------------------------------------------+"
  echo -e          "|         NINA IS FULLY OPERATIONAL  [OK]              |"
  echo -e          "+------------------------------------------------------+${RST}"
else
  echo -e "${BLD}${YLW}+------------------------------------------------------+"
  echo -e          "|   NINA RESCUE COMPLETE -- PARTIAL / LOOP ACTIVE      |"
  echo -e          "+------------------------------------------------------+${RST}"
fi
echo ""
echo -e "  nina.service         : ${NINA_FINAL}"
echo -e "  ninagate.service     : ${NG_FINAL}"
echo -e "  NinaGate /health     : HTTP ${NG_HTTP}"
echo -e "  Critical imports OK  : $((3 - IMPORT_FINAL))/3"
echo -e "  Inference source     : ${INFERENCE_SOURCE:-none}"
echo -e "  Rescue ID            : ${RESCUE_ID}"
echo -e "  Log                  : ${RESCUE_LOG}"
echo -e "  Brief                : ${BRIEF_FILE}"
echo ""
echo -e "  ${DIM}Re-run  : bash ~/nina/scripts/nina_rescue.sh"
echo -e "  Diag    : python scripts/nina_diag.py"
echo -e "  Logs    : journalctl --user -u nina.service -f${RST}\n"
idempotent_mark "phase8_final" "nina=${NINA_FINAL},imports_fail=${IMPORT_FINAL}"
