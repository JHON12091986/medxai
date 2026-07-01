#!/usr/bin/env bash
# ============================================================
# DULAL MODEL BENCHMARK v4.1 — GPU-aware | Interactive | REST API tok/s
# M. Baizid Alam | NINA Project | aibony/nina
#
# Usage:
#   bash ~/nina/scripts/dulal_model_bench.sh
#              → auto-scan + interactive model picker
#   bash ~/nina/scripts/dulal_model_bench.sh --non-interactive
#              → run all VRAM-fit models without prompting (CI/auto)
#   bash ~/nina/scripts/dulal_model_bench.sh --all-models
#              → include over-budget models in picker
#   bash ~/nina/scripts/dulal_model_bench.sh --models "qwen3:1.7b deepseek-r1:1.5b"
#              → skip scanner, test specific models in given order
#   bash ~/nina/scripts/dulal_model_bench.sh --start-from deepseek-r1:1.5b
#              → resume from this model (skip everything before it)
#   bash ~/nina/scripts/dulal_model_bench.sh --skip-gpu-tune
#              → skip GPU tuner (already configured)
#   bash ~/nina/scripts/dulal_model_bench.sh --vram 1800
#              → override VRAM budget in MiB
# ============================================================
set -uo pipefail

# ── Paths ────────────────────────────────────────────────────
NINA_DIR="$HOME/nina"
LOG_DIR="$NINA_DIR/logs"
RESULTS_FILE="$LOG_DIR/model_bench_$(date +%Y%m%d_%H%M%S).md"
OLLAMA_USER_OVERRIDE_DIR="$HOME/.config/systemd/user/ollama.service.d"
OLLAMA_SYS_OVERRIDE_DIR="/etc/systemd/system/ollama.service.d"
OLLAMA_API="http://localhost:11434/api/generate"
PROMPT_TIMEOUT=300
INTER_MODEL_SLEEP=5
VRAM_BUDGET_OVERRIDE=0
# 50MB explicit overhead — overrides ollama's default 10% auto-reservation
OLLAMA_OVERHEAD_BYTES=52428800
mkdir -p "$LOG_DIR"

# ── Colours ──────────────────────────────────────────────────
RED='\033[0;31m'; YEL='\033[1;33m'; GRN='\033[0;32m'
CYN='\033[0;36m'; MAG='\033[0;35m'; BLD='\033[1m'; RST='\033[0m'
log()  { echo -e "${BLD}[BENCH]${RST} $*"; }
ok()   { echo -e "${GRN}[OK]${RST}    $*"; }
warn() { echo -e "${YEL}[WARN]${RST}  $*"; }
err()  { echo -e "${RED}[ERR]${RST}   $*"; }
tlog() { echo "$*" | tee -a "$RESULTS_FILE"; }

# ── CLI args ─────────────────────────────────────────────────
SKIP_GPU_TUNE=0; CUSTOM_MODELS=""; ALL_MODELS=0; NON_INTERACTIVE=0; START_FROM=""
for arg in "$@"; do
  case "$arg" in
    --skip-gpu-tune)   SKIP_GPU_TUNE=1 ;;
    --all-models)      ALL_MODELS=1 ;;
    --non-interactive) NON_INTERACTIVE=1 ;;
    --models)          shift; CUSTOM_MODELS="$1" ;;
    --start-from)      shift; START_FROM="$1" ;;
    --vram)            shift; VRAM_BUDGET_OVERRIDE="$1" ;;
  esac
done

# ============================================================
# SECTION 1 — GPU TUNER
# OLLAMA_NUM_GPU=1  → 1 GPU card (MX150). NOT layers, NOT VRAM.
# OLLAMA_GPU_OVERHEAD=52428800 → explicit 50MB buffer, kills 10% default.
# ============================================================
VRAM_TOTAL_MIB=2048
VRAM_FREE_MIB=2048

gpu_tune() {
  echo ""
  echo -e "${CYN}══════════════════════════════════════════${RST}"
  echo -e "${CYN}  OLLAMA GPU AUTO-TUNER v4.1              ${RST}"
  echo -e "${CYN}══════════════════════════════════════════${RST}"

  if ! command -v nvidia-smi &>/dev/null; then
    warn "nvidia-smi not found — CPU-only mode"; return 0
  fi

  VRAM_TOTAL_MIB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  VRAM_FREE_MIB=$(nvidia-smi  --query-gpu=memory.free  --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  GPU_NAME=$(nvidia-smi --query-gpu=name             --format=csv,noheader 2>/dev/null | head -1)
  DRIVER_VER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
  ok "GPU: $GPU_NAME | VRAM total: ${VRAM_TOTAL_MIB}MiB | free: ${VRAM_FREE_MIB}MiB | Driver: $DRIVER_VER"

  OLLAMA_SVC_TYPE="none"
  if systemctl --user is-active ollama &>/dev/null 2>&1; then
    OLLAMA_SVC_TYPE="user";   ok "Ollama: systemd --user"
  elif systemctl is-active ollama &>/dev/null 2>&1; then
    OLLAMA_SVC_TYPE="system"; log "Ollama: systemd system"
  else
    warn "Ollama: manual process"
  fi

  GPU_OVERRIDE_STATUS="session-only"
  # NUM_GPU=1 = one GPU card (correct for MX150). 999 was wrong.
  GPU_CONF_CONTENT="[Service]
Environment=\"OLLAMA_NUM_GPU=1\"
Environment=\"CUDA_VISIBLE_DEVICES=0\"
Environment=\"OLLAMA_GPU_OVERHEAD=${OLLAMA_OVERHEAD_BYTES}\"
Environment=\"LLAMA_ARG_FIT_TARGET=50\""

  if [[ "$OLLAMA_SVC_TYPE" == "user" ]]; then
    mkdir -p "$OLLAMA_USER_OVERRIDE_DIR"
    echo "$GPU_CONF_CONTENT" > "$OLLAMA_USER_OVERRIDE_DIR/gpu.conf"
    systemctl --user daemon-reload
    systemctl --user restart ollama && sleep 4
    ok "--user drop-in written + restarted"
    GPU_OVERRIDE_STATUS="persistent-user"

  elif [[ "$OLLAMA_SVC_TYPE" == "system" ]]; then
    CURRENT_OH=$(grep "OLLAMA_GPU_OVERHEAD" "$OLLAMA_SYS_OVERRIDE_DIR/gpu.conf" 2>/dev/null | grep -o '[0-9]*' || echo "0")
    CURRENT_NG=$(grep "OLLAMA_NUM_GPU" "$OLLAMA_SYS_OVERRIDE_DIR/gpu.conf" 2>/dev/null | grep -o '[0-9]*' || echo "0")
    CURRENT_FT=$(grep "LLAMA_ARG_FIT_TARGET" "$OLLAMA_SYS_OVERRIDE_DIR/gpu.conf" 2>/dev/null | grep -o '[0-9]*' || echo "0")
    if [[ "$CURRENT_OH" == "$OLLAMA_OVERHEAD_BYTES" && "$CURRENT_NG" == "1" && "$CURRENT_FT" == "50" ]]; then
      ok "System drop-in already correct (NUM_GPU=1 overhead=${OLLAMA_OVERHEAD_BYTES} fit_target=50)"
      GPU_OVERRIDE_STATUS="persistent-system (existing)"
    elif sudo -n true 2>/dev/null; then
      sudo mkdir -p "$OLLAMA_SYS_OVERRIDE_DIR"
      echo "$GPU_CONF_CONTENT" | sudo tee "$OLLAMA_SYS_OVERRIDE_DIR/gpu.conf" > /dev/null
      sudo systemctl daemon-reload
      sudo systemctl restart ollama && sleep 4
      ok "System drop-in updated + restarted"
      GPU_OVERRIDE_STATUS="persistent-system"
    else
      warn "sudo requires password — session-only."
      echo ""
      echo -e "${YEL}  Run once to make permanent:${RST}"
      echo -e "${YEL}  sudo mkdir -p ${OLLAMA_SYS_OVERRIDE_DIR} && sudo tee ${OLLAMA_SYS_OVERRIDE_DIR}/gpu.conf <<'EOF'${RST}"
      echo -e "${YEL}${GPU_CONF_CONTENT}${RST}"
      echo -e "${YEL}EOF${RST}"
      echo -e "${YEL}  sudo systemctl daemon-reload && sudo systemctl restart ollama${RST}"
      echo ""
    fi
  fi

  # Session export — NUM_GPU=1 is the correct value for 1 GPU card
  export OLLAMA_NUM_GPU=1
  export CUDA_VISIBLE_DEVICES=0
  export OLLAMA_GPU_OVERHEAD=$OLLAMA_OVERHEAD_BYTES
  export LLAMA_ARG_FIT_TARGET=50
  ok "Session env: OLLAMA_NUM_GPU=1 | OLLAMA_GPU_OVERHEAD=${OLLAMA_OVERHEAD_BYTES} (50MB) | LLAMA_ARG_FIT_TARGET=50"
  ok "GPU override status: $GPU_OVERRIDE_STATUS"
  tlog "> GPU override: $GPU_OVERRIDE_STATUS | NUM_GPU=1 | overhead: ${OLLAMA_OVERHEAD_BYTES}B (50MB)"

  sleep 2
  VRAM_FREE_MIB=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  ok "VRAM free after tune: ${VRAM_FREE_MIB}MiB"

  # Smoke test
  SMOKE_MODEL=$(ollama list 2>/dev/null | awk 'NR>1 {print $3, $4, $1}' \
    | awk '$2=="MB" && $1+0 < 1200 {print $3; exit} $2=="GB" && $1+0 < 1.2 {print $3; exit}')
  [[ -z "$SMOKE_MODEL" ]] && SMOKE_MODEL=$(ollama list 2>/dev/null | awk 'NR==2{print $1}')

  if [[ -n "$SMOKE_MODEL" ]]; then
    log "Smoke test: ${SMOKE_MODEL} (15s poll) ..."
    ollama ps 2>/dev/null | awk 'NR>1{print $1}' | xargs -r -I{} ollama stop {} 2>/dev/null || true
    sleep 2
    timeout 90 ollama run "$SMOKE_MODEL" "Write a one-line Python hello world" --nowordwrap &>/dev/null &
    SMOKE_PID=$!
    SMOKE_CONFIRMED=0
    for _T in 1 2 3 4 5; do
      sleep 3
      GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
      VRAM_USED=$(nvidia-smi --query-gpu=memory.used    --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
      [[ "${GPU_UTIL:-0}" -gt 5 ]] && { SMOKE_CONFIRMED=1; break; }
    done
    wait $SMOKE_PID 2>/dev/null || true
    if [[ "$SMOKE_CONFIRMED" -eq 1 ]]; then
      ok "✅ GPU confirmed — Util: ${GPU_UTIL}% | VRAM: ${VRAM_USED}/${VRAM_TOTAL_MIB}MiB"
      tlog "> Smoke test: ✅ ${GPU_UTIL}% | ${VRAM_USED}/${VRAM_TOTAL_MIB}MiB"
    else
      warn "GPU-Util 0% after 15s"
      tlog "> Smoke test: ⚠️ 0% | ${VRAM_USED:-?}/${VRAM_TOTAL_MIB}MiB"
    fi
    ollama stop "$SMOKE_MODEL" 2>/dev/null || true
    sleep 2
  fi
  echo ""
}

# ============================================================
# SECTION 2 — MODEL SIZE PARSER
# ============================================================
model_size_mb() {
  local MODEL="$1" ROW NUM UNIT
  ROW=$(ollama list 2>/dev/null | awk -v m="$MODEL" '$1==m {print $3, $4; exit}')
  [[ -z "$ROW" ]] && { echo 9999; return; }
  NUM=$(echo "$ROW" | awk '{print $1}')
  UNIT=$(echo "$ROW" | awk '{print $2}')
  case "$UNIT" in
    GB) echo "$(echo "scale=0; $NUM * 1024 / 1" | bc)" ;;
    MB) echo "${NUM%.*}" ;;
    *)  echo 9999 ;;
  esac
}

# ============================================================
# SECTION 3 — INTELLIGENT MODEL SCANNER
# Budget = VRAM_TOTAL * 90% (total is stable; free fluctuates
# depending on smoke test residue and driver overhead)
# ============================================================
auto_scan_models() {
  local BUDGET="$1"
  echo ""
  echo -e "${CYN}══════════════════════════════════════════${RST}"
  echo -e "${CYN}  INTELLIGENT MODEL SCANNER               ${RST}"
  echo -e "${CYN}  Budget: ${BUDGET}MiB (90% of ${VRAM_TOTAL_MIB}MiB total)${RST}"
  echo -e "${CYN}══════════════════════════════════════════${RST}"

  local SKIP_PATTERNS="nomic-embed|all-minilm|bge-|e5-|mxbai-embed|snowflake-arctic-embed|paraphrase"
  local SCANNED=0 ACCEPTED=0 SKIPPED_EMBED=0 SKIPPED_SIZE=0
  local -a FIT_MODELS=() WARN_MODELS=()

  while IFS= read -r LINE; do
    [[ -z "$LINE" || "$LINE" == NAME* ]] && continue
    local NAME SIZE_NUM SIZE_UNIT SIZE_MB
    NAME=$(echo "$LINE" | awk '{print $1}')
    SIZE_NUM=$(echo "$LINE" | awk '{print $3}')
    SIZE_UNIT=$(echo "$LINE" | awk '{print $4}')
    SCANNED=$((SCANNED + 1))

    if echo "$NAME" | grep -qiE "$SKIP_PATTERNS"; then
      log "  SKIP embed: $NAME"; SKIPPED_EMBED=$((SKIPPED_EMBED + 1)); continue
    fi

    case "$SIZE_UNIT" in
      GB) SIZE_MB=$(echo "scale=0; $SIZE_NUM * 1024 / 1" | bc 2>/dev/null || echo 9999) ;;
      MB) SIZE_MB="${SIZE_NUM%.*}" ;;
      *)  SIZE_MB=9999 ;;
    esac

    if [[ "$SIZE_MB" -le "$BUDGET" ]]; then
      ok "  FITS  ✅ $NAME (${SIZE_NUM}${SIZE_UNIT} = ${SIZE_MB}MiB)"
      FIT_MODELS+=("$NAME"); ACCEPTED=$((ACCEPTED + 1))
    elif [[ "$ALL_MODELS" -eq 1 ]]; then
      warn "  LARGE ⚠️  $NAME (${SIZE_NUM}${SIZE_UNIT} = ${SIZE_MB}MiB) — --all-models"
      WARN_MODELS+=("$NAME")
    else
      warn "  SKIP  🔴 $NAME (${SIZE_NUM}${SIZE_UNIT} = ${SIZE_MB}MiB > ${BUDGET}MiB)"
      SKIPPED_SIZE=$((SKIPPED_SIZE + 1))
    fi
  done < <(ollama list 2>/dev/null)

  echo ""
  log "Scan: $SCANNED total | $ACCEPTED fit | $SKIPPED_SIZE over-budget | $SKIPPED_EMBED embed"
  SCANNED_MODELS=("${FIT_MODELS[@]}" ${WARN_MODELS[@]+"${WARN_MODELS[@]}"})

  if [[ ${#SCANNED_MODELS[@]} -eq 0 ]]; then
    err "No models within budget ${BUDGET}MiB. Use --all-models."; exit 1
  fi
  tlog "> Auto-scan: $ACCEPTED fit | $SKIPPED_SIZE skipped | $SKIPPED_EMBED embed"
  tlog "> Budget: ${BUDGET}MiB (90% of ${VRAM_TOTAL_MIB}MiB total)"
}

# ============================================================
# SECTION 4 — INTERACTIVE MODEL PICKER
# ============================================================
interactive_picker() {
  local -a POOL=("$@")
  local -a SELECTED=()
  local -a ORDER=()
  local N=${#POOL[@]}

  for i in "${!POOL[@]}"; do
    SELECTED+=("1")
    ORDER+=("$i")
  done

  while true; do
    clear
    echo -e "${CYN}╔══════════════════════════════════════════════╗${RST}"
    echo -e "${CYN}║   DULAL BENCHMARK — Model Selection v4.1     ║${RST}"
    echo -e "${CYN}╚══════════════════════════════════════════════╝${RST}"
    echo ""
    echo -e "  ${BLD}Run order  [toggle = number | move = u/d | order = o1,2,3]${RST}"
    echo ""

    local IDX=0
    for POS in "${ORDER[@]}"; do
      IDX=$((IDX + 1))
      local NAME="${POOL[$POS]}"
      local SIZE_MB; SIZE_MB=$(model_size_mb "$NAME")
      local FIT; FIT=$(vram_fit_label "$SIZE_MB" "$VRAM_BUDGET")
      local CHECK
      [[ "${SELECTED[$POS]}" == "1" ]] && CHECK="${GRN}[✓]${RST}" || CHECK="${RED}[✗]${RST}"
      echo -e "  ${BLD}${IDX}.${RST} ${CHECK} ${BLD}${NAME}${RST}  ${SIZE_MB}MiB  ${FIT}"
    done

    echo ""
    echo -e "  ${MAG}[number]${RST} toggle  ${MAG}u/d[n]${RST} move  ${MAG}o[n,n..]${RST} reorder  ${MAG}a${RST} all  ${MAG}n${RST} none  ${MAG}r${RST} reset  ${MAG}go${RST} start  ${MAG}q${RST} quit"
    echo ""
    echo -ne "  ${BLD}> ${RST}"
    read -r CMD

    case "$CMD" in
      go)
        FINAL_MODELS=()
        for POS in "${ORDER[@]}"; do
          [[ "${SELECTED[$POS]}" == "1" ]] && FINAL_MODELS+=("${POOL[$POS]}")
        done
        if [[ ${#FINAL_MODELS[@]} -eq 0 ]]; then
          echo -e "  ${RED}Select at least one model.${RST}"; sleep 2; continue
        fi
        echo -e "  ${GRN}Starting: ${FINAL_MODELS[*]}${RST}"; sleep 1; return 0 ;;
      q|quit) echo "Aborted."; exit 0 ;;
      a) for i in "${!SELECTED[@]}"; do SELECTED[$i]="1"; done ;;
      n) for i in "${!SELECTED[@]}"; do SELECTED[$i]="0"; done ;;
      r) ORDER=(); for i in "${!POOL[@]}"; do ORDER+=("$i"); done ;;
      [0-9]*)
        local TPOS=$(( CMD - 1 ))
        if [[ $TPOS -ge 0 && $TPOS -lt $N ]]; then
          local REAL_IDX=${ORDER[$TPOS]}
          [[ "${SELECTED[$REAL_IDX]}" == "1" ]] && SELECTED[$REAL_IDX]="0" || SELECTED[$REAL_IDX]="1"
        fi ;;
      u[0-9]*)
        local UPOS=$(( ${CMD#u} - 1 ))
        if [[ $UPOS -gt 0 && $UPOS -lt $N ]]; then
          local TMP="${ORDER[$UPOS]}"; ORDER[$UPOS]="${ORDER[$((UPOS-1))]}"; ORDER[$((UPOS-1))]="$TMP"
        fi ;;
      d[0-9]*)
        local DPOS=$(( ${CMD#d} - 1 ))
        if [[ $DPOS -ge 0 && $DPOS -lt $((N-1)) ]]; then
          local TMP="${ORDER[$DPOS]}"; ORDER[$DPOS]="${ORDER[$((DPOS+1))]}"; ORDER[$((DPOS+1))]="$TMP"
        fi ;;
      o*)
        local RAW="${CMD#o}"
        IFS=',' read -ra NUMS <<< "$RAW"
        local -a NEW_ORDER=()
        local VALID=1
        for NUM in "${NUMS[@]}"; do
          local P=$(( NUM - 1 ))
          if [[ $P -ge 0 && $P -lt $N ]]; then NEW_ORDER+=("${ORDER[$P]}")
          else warn "Bad pos: $NUM"; VALID=0; break; fi
        done
        [[ "$VALID" -eq 1 && ${#NEW_ORDER[@]} -eq $N ]] && ORDER=("${NEW_ORDER[@]}") \
          || { warn "Must include all $N positions"; sleep 2; } ;;
      *) warn "Unknown: $CMD"; sleep 1 ;;
    esac
  done
}

# ============================================================
# SECTION 5 — VRAM FIT LABEL
# ============================================================
vram_fit_label() {
  local SIZE_MB="$1" BUDGET="$2"
  if   [[ "$SIZE_MB" -le $(( BUDGET / 2 )) ]]; then echo "✅ Full GPU"
  elif [[ "$SIZE_MB" -le "$BUDGET" ]];          then echo "⚠️  Tight"
  else                                                echo "🔴 CPU risk"
  fi
}

# ============================================================
# SECTION 6 — REST API INFERENCE (real tok/s from ollama)
# Uses POST /api/generate → eval_count / eval_duration (ns)
# Falls back to ollama run + wc -w estimate if curl fails
# ============================================================
run_prompt() {
  local MODEL="$1" PROMPT="$2"
  local RESPONSE="" TPS="?" EXIT_CODE=0 ELAPSED=0

  START=$(date +%s)

  # Try REST API first
  if command -v curl &>/dev/null; then
    local JSON_PROMPT
    JSON_PROMPT=$(printf '%s' "$PROMPT" | python3 -c \
      "import sys,json; print(json.dumps(sys.stdin.read()))" 2>/dev/null || \
      printf '"'"$PROMPT"'"')

    local API_RESP
    API_RESP=$(curl -s --max-time "$PROMPT_TIMEOUT" \
      "$OLLAMA_API" \
      -H 'Content-Type: application/json' \
      -d "{\"model\":\"${MODEL}\",\"prompt\":${JSON_PROMPT},\"stream\":false}" 2>/dev/null)
    EXIT_CODE=$?
    ELAPSED=$(( $(date +%s) - START ))

    if [[ $EXIT_CODE -eq 0 && -n "$API_RESP" ]]; then
      RESPONSE=$(echo "$API_RESP" | python3 -c \
        "import sys,json; d=json.load(sys.stdin); print(d.get('response',''))" 2>/dev/null)
      local EVAL_COUNT EVAL_NS
      EVAL_COUNT=$(echo "$API_RESP" | python3 -c \
        "import sys,json; d=json.load(sys.stdin); print(d.get('eval_count',0))" 2>/dev/null || echo 0)
      EVAL_NS=$(echo "$API_RESP" | python3 -c \
        "import sys,json; d=json.load(sys.stdin); print(d.get('eval_duration',1))" 2>/dev/null || echo 1)
      # Real tok/s from ollama metadata
      if [[ "${EVAL_COUNT:-0}" -gt 0 && "${EVAL_NS:-1}" -gt 0 ]]; then
        TPS=$(echo "scale=1; $EVAL_COUNT * 1000000000 / $EVAL_NS" | bc 2>/dev/null || echo "?")
      fi
      BENCH_METHOD="REST"
      return 0
    fi
  fi

  # Fallback: ollama run + wc estimate
  BENCH_METHOD="CLI"
  RESPONSE=$(timeout "$PROMPT_TIMEOUT" ollama run "$MODEL" "$PROMPT" --nowordwrap 2>/dev/null)
  EXIT_CODE=$?
  ELAPSED=$(( $(date +%s) - START ))
  if [[ $EXIT_CODE -eq 0 && -n "$RESPONSE" ]]; then
    local WORDS; WORDS=$(echo "$RESPONSE" | wc -w)
    TPS=$(echo "scale=1; $WORDS * 1.3 / $ELAPSED" | bc 2>/dev/null || echo "?")
  fi
  return $EXIT_CODE
}

# ============================================================
# SECTION 7 — HEADER
# ============================================================
tlog "# DULAL Model Benchmark v4.1 — $(date)"
tlog "Hardware: i5-8265U | MX150 2GB | 16GB RAM"
tlog ""
tlog "> Script: dulal_model_bench.sh v4.1 | GPU-aware | REST tok/s | Timeout: ${PROMPT_TIMEOUT}s"
tlog ""

# ============================================================
# SECTION 8 — GPU TUNER
# ============================================================
if [[ "$SKIP_GPU_TUNE" -eq 0 ]]; then
  gpu_tune
else
  log "GPU tune skipped"
  if command -v nvidia-smi &>/dev/null; then
    VRAM_TOTAL_MIB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
    VRAM_FREE_MIB=$(nvidia-smi  --query-gpu=memory.free  --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
    export OLLAMA_NUM_GPU=1 CUDA_VISIBLE_DEVICES=0 OLLAMA_GPU_OVERHEAD=$OLLAMA_OVERHEAD_BYTES LLAMA_ARG_FIT_TARGET=50
    ok "Session env set | VRAM: ${VRAM_FREE_MIB}MiB free / ${VRAM_TOTAL_MIB}MiB total | LLAMA_ARG_FIT_TARGET=50"
  fi
fi
tlog "> VRAM: ${VRAM_FREE_MIB}MiB free / ${VRAM_TOTAL_MIB}MiB total"

# ============================================================
# SECTION 8.5 — HARD CPU INFERENCE GUARD
# ============================================================
# Call the ollama REST API /api/generate with a 3-token test
TEST_MODEL=$(ollama list 2>/dev/null | awk 'NR>1 {print $3, $4, $1}' \
  | grep -vE "embed|all-minilm" \
  | awk '$2=="MB" && $1+0 < 1200 {print $3; exit} $2=="GB" && $1+0 < 1.6 {print $3; exit}')
[[ -z "$TEST_MODEL" ]] && TEST_MODEL=$(ollama list 2>/dev/null | awk 'NR>1 && $1 !~ /embed/ {print $1; exit}')

if [[ -n "$TEST_MODEL" ]]; then
  log "Running CPU fallback check on $TEST_MODEL..."
  ollama ps 2>/dev/null | awk 'NR>1{print $1}' | xargs -r -I{} ollama stop {} 2>/dev/null || true
  sleep 1
  
  GUARD_RESP=$(curl -s --max-time 30 \
    "$OLLAMA_API" \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"${TEST_MODEL}\",\"prompt\":\"Hi\",\"stream\":false,\"options\":{\"num_predict\":3}}" 2>/dev/null)
  
  EVAL_COUNT=$(echo "$GUARD_RESP" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('eval_count',0))" 2>/dev/null || echo 0)
  EVAL_NS=$(echo "$GUARD_RESP" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('eval_duration',1))" 2>/dev/null || echo 1)
  
  if [[ "${EVAL_COUNT:-0}" -gt 0 && "${EVAL_NS:-1}" -gt 0 ]]; then
    TPS_VAL=$(echo "scale=1; $EVAL_COUNT * 1000000000 / $EVAL_NS" | bc 2>/dev/null || echo "0")
  else
    TPS_VAL="0"
  fi

  IS_SLOW=$(echo "$TPS_VAL < 10" | bc 2>/dev/null || echo "1")
  if [[ "$IS_SLOW" -eq 1 ]]; then
    echo "🔥 CPU FALLBACK DETECTED — aborting benchmark"
    exit 1
  else
    ok "CPU fallback guard passed: $TPS_VAL tok/s on $TEST_MODEL"
  fi
else
  warn "No test model found for CPU fallback check"
fi

# ============================================================
# SECTION 9 — RESOLVE MODEL LIST
# Budget = 90% of TOTAL VRAM (stable; not free which fluctuates)
# ============================================================
if [[ "$VRAM_BUDGET_OVERRIDE" -gt 0 ]]; then
  VRAM_BUDGET="$VRAM_BUDGET_OVERRIDE"
else
  VRAM_BUDGET=$(echo "scale=0; $VRAM_TOTAL_MIB * 90 / 100" | bc)
fi

declare -a MODELS=() SCANNED_MODELS=() FINAL_MODELS=()

if [[ -n "$CUSTOM_MODELS" ]]; then
  read -ra MODELS <<< "$CUSTOM_MODELS"
  log "Custom list: ${MODELS[*]}"
  tlog "> Model source: --models flag"
  FINAL_MODELS=("${MODELS[@]}")
else
  auto_scan_models "$VRAM_BUDGET"
  MODELS=("${SCANNED_MODELS[@]}")

  if [[ "$NON_INTERACTIVE" -eq 1 ]]; then
    log "--non-interactive: all scanned models, scan order"
    FINAL_MODELS=("${MODELS[@]}")
  else
    interactive_picker "${MODELS[@]}"
  fi
fi

# ── --start-from: drop everything before the named model ─────
if [[ -n "$START_FROM" ]]; then
  log "--start-from: skipping to ${START_FROM}"
  TRIMMED=()
  FOUND=0
  for M in "${FINAL_MODELS[@]}"; do
    [[ "$M" == "$START_FROM" ]] && FOUND=1
    [[ $FOUND -eq 1 ]] && TRIMMED+=("$M")
  done
  if [[ ${#TRIMMED[@]} -eq 0 ]]; then
    warn "--start-from '${START_FROM}' not found in model list — running all"
  else
    FINAL_MODELS=("${TRIMMED[@]}")
    log "Trimmed list: ${FINAL_MODELS[*]}"
  fi
fi

[[ ${#FINAL_MODELS[@]} -eq 0 ]] && { err "No models selected."; exit 1; }
log "Final order (${#FINAL_MODELS[@]}): ${FINAL_MODELS[*]}"
tlog "> Models: ${FINAL_MODELS[*]}"
tlog "> Budget: ${VRAM_BUDGET}MiB (90% of ${VRAM_TOTAL_MIB}MiB)"

# ── Nina-relevant prompts ────────────────────────────────────
PROMPTS=(
  "Write a FastAPI GET /health endpoint that returns {status: ok, ts: datetime}"
  "Write a Python async function that reads a file with pathlib and returns its contents"
  "One-liner bash: list all systemctl --user services that are running"
  "Fix this Python: import os; f = open('test.txt'); data = f.read()"
  "Write a Python dataclass for ProviderHealth with fields: name str, score float, last_used datetime"
)

tlog ""
tlog "## Results"
tlog ""
tlog "| Model | VRAM Fit | Prompt | tok/s | Method | Pass? | Time | VRAM used |"
tlog "|---|---|---|---|---|---|---|---|"

declare -a SUMMARY_LINES=()

# ============================================================
# SECTION 10 — BENCHMARK LOOP
# ============================================================
for MODEL in "${FINAL_MODELS[@]}"; do
  echo ""
  echo -e "${CYN}══════════════════════════════════════════${RST}"
  echo -e "${CYN}  Testing: ${BLD}$MODEL${RST}"
  echo -e "${CYN}══════════════════════════════════════════${RST}"

  if ! ollama list 2>/dev/null | awk 'NR>1{print $1}' | grep -qx "$MODEL"; then
    log "Pulling $MODEL ..."
    ollama pull "$MODEL" 2>&1 | tail -1 || {
      err "Pull failed — skipping $MODEL"
      tlog "| $MODEL | N/A | PULL FAILED | — | — | ❌ | — | — |"
      continue
    }
  else
    ok "$MODEL available"
  fi

  MODEL_MB=$(model_size_mb "$MODEL")
  FIT_LABEL=$(vram_fit_label "$MODEL_MB" "$VRAM_BUDGET")
  log "Size: ${MODEL_MB}MiB | Fit: $FIT_LABEL | Budget: ${VRAM_BUDGET}MiB"

  # Unload any other model
  ollama ps 2>/dev/null | awk 'NR>1{print $1}' | grep -v "^${MODEL}$" \
    | xargs -r -I{} bash -c 'ollama stop "{}" 2>/dev/null || true'
  sleep 2

  TOTAL_TPS=0; PASS_COUNT=0; PROMPT_NUM=0; MODEL_FAILED=0

  for PROMPT in "${PROMPTS[@]}"; do
    PROMPT_NUM=$((PROMPT_NUM + 1))
    SHORT="${PROMPT:0:50}"
    echo ""
    log "Prompt $PROMPT_NUM: ${SHORT}..."

    # Reset shared vars before run_prompt
    RESPONSE=""; TPS="?"; BENCH_METHOD="?"; EXIT_CODE=0; ELAPSED=0; START=$(date +%s)

    run_prompt "$MODEL" "$PROMPT"
    RUN_EXIT=$?
    ELAPSED=$(( $(date +%s) - START ))

    VRAM_NOW=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
    VRAM_LABEL="${VRAM_NOW:-?}MiB"

    if [[ $RUN_EXIT -eq 124 ]]; then
      warn "TIMEOUT after ${ELAPSED}s"
      tlog "| $MODEL | $FIT_LABEL | ${SHORT} | — | $BENCH_METHOD | ❌ TIMEOUT | ${ELAPSED}s | $VRAM_LABEL |"
      MODEL_FAILED=$((MODEL_FAILED + 1))
      ollama stop "$MODEL" 2>/dev/null || true; sleep 3; continue
    elif [[ $RUN_EXIT -ne 0 ]] || [[ -z "${RESPONSE:-}" ]]; then
      warn "Empty/error (exit $RUN_EXIT)"
      tlog "| $MODEL | $FIT_LABEL | ${SHORT} | — | $BENCH_METHOD | ❌ FAIL | ${ELAPSED}s | $VRAM_LABEL |"
      MODEL_FAILED=$((MODEL_FAILED + 1)); continue
    fi

    if echo "$RESPONSE" | grep -qiE "def |async |return |import |class |\{|\}|systemctl|with open"; then
      PASS="✅"; PASS_COUNT=$((PASS_COUNT + 1))
    else
      PASS="❌"
    fi

    TOTAL_TPS=$(echo "scale=1; $TOTAL_TPS + ${TPS:-0}" | bc 2>/dev/null || echo "$TOTAL_TPS")
    echo "    → ${ELAPSED}s | ${TPS} tok/s (${BENCH_METHOD}) | $PASS | VRAM: $VRAM_LABEL"
    tlog "| $MODEL | $FIT_LABEL | ${SHORT} | ${TPS} | ${BENCH_METHOD} | $PASS | ${ELAPSED}s | $VRAM_LABEL |"
  done

  TOTAL_PROMPTS=${#PROMPTS[@]}
  AVG_TPS=$(echo "scale=1; $TOTAL_TPS / $TOTAL_PROMPTS" | bc 2>/dev/null || echo "?")
  tlog ""
  tlog "**$MODEL — $PASS_COUNT/${TOTAL_PROMPTS} passed | avg ${AVG_TPS} tok/s | timeouts: $MODEL_FAILED | $FIT_LABEL**"
  tlog ""
  SUMMARY_LINES+=("$PASS_COUNT/$TOTAL_PROMPTS | ${AVG_TPS} tok/s | $MODEL_FAILED timeouts | $FIT_LABEL | $MODEL")

  log "Unloading $MODEL ..."
  ollama stop "$MODEL" 2>/dev/null || true
  sleep "$INTER_MODEL_SLEEP"
done

# ============================================================
# SECTION 11 — LEADERBOARD
# ============================================================
tlog "---"
tlog "## Leaderboard (sorted by pass rate)"
tlog ""
tlog "| Rank | Model | Pass | Avg tok/s | Timeouts | VRAM Fit |"
tlog "|---|---|---|---|---|---|"
RANK=0
while IFS= read -r LINE; do
  RANK=$((RANK + 1))
  PASS_F=$(echo "$LINE" | cut -d'|' -f1 | tr -d ' ')
  TPS_F=$(echo "$LINE"  | cut -d'|' -f2 | tr -d ' ')
  TO_F=$(echo "$LINE"   | cut -d'|' -f3 | tr -d ' ')
  FIT_F=$(echo "$LINE"  | cut -d'|' -f4 | xargs)
  MOD_F=$(echo "$LINE"  | cut -d'|' -f5 | tr -d ' ')
  tlog "| $RANK | $MOD_F | $PASS_F | $TPS_F | $TO_F | $FIT_F |"
done < <(printf '%s\n' "${SUMMARY_LINES[@]}" | sort -t'|' -k1 -rn)

tlog ""
tlog "---"
tlog "> Generated by dulal_model_bench.sh v4.1 | $(date)"

# ============================================================
# SECTION 12 — DONE
# ============================================================
echo ""
echo -e "${GRN}══════════════════════════════════════════${RST}"
echo -e "${GRN}  BENCHMARK COMPLETE${RST}"
echo -e "${GRN}  Results: $RESULTS_FILE${RST}"
echo -e "${GRN}══════════════════════════════════════════${RST}"
echo ""
cat "$RESULTS_FILE"
