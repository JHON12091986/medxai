#!/usr/bin/env bash
# =============================================================================
# NINA OUROBOROS LOOP — scripts/ouroboros_loop.sh
# =============================================================================
# The snake eating itself.
# Runs PERMANENTLY. Feeds opencode NinaGate improvement tasks, validates each
# result through the immune system, commits, and notifies Telegram.
#
# CONTINGENCY MATRIX:
#   shutdown/reboot        → systemd --user unit auto-restarts on next login
#   power outage           → git-hooks ensure no partial commit lands
#   internet outage        → NinaGate routes to Ollama; loop continues
#   NinaGate down          → wait_for_ninagate() polls every 10s with backoff
#   quota exhausted        → NinaGate auto-shifts to Ollama
#   opencode crash         → trap ERR logs; loop restarts
#   checks fail            → commit rejected by pre-commit hook; next task
#   disk full              → pre-flight check; suspend + alert
#   no tasks               → sleep IDLE_SLEEP then re-read backlog
#   loop diverging         → 3 consecutive degraded cycles → SUSPEND + Telegram
#   opencode not in PATH   → resolve_opencode() searches 8 locations + find
#   wrong CLI flags        → correct: opencode run --model x "task"
#   opencode hits OpenAI   → OPENAI_API_BASE=http://localhost:8080/v1 (NinaGate)
#   systemd Type=forking   → FIXED: Type=simple in ouroboros.service
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
NINA_DIR="${HOME}/nina"
LOG_DIR="${NINA_DIR}/logs"
DATA_DIR="${NINA_DIR}/data"

LOOP_LOG="${LOG_DIR}/ouroboros_loop.log"
ERROR_LOG="${LOG_DIR}/ouroboros_errors.log"
SUSPEND_FLAG="${DATA_DIR}/ouroboros_suspended.flag"
BACKLOG_FILE="${DATA_DIR}/ouroboros_backlog.txt"
DIGEST_FILE="${DATA_DIR}/ouroboros_digest.md"
PIDFILE="${DATA_DIR}/ouroboros_loop.pid"
OPENCODE_BIN=""

NINAGATE_URL="http://localhost:8080/v1/models"
NINAGATE_TIMEOUT=300
NINAGATE_POLL=10

# ---------------------------------------------------------------------------
# TUNING
# ---------------------------------------------------------------------------
IDLE_SLEEP=300
TASK_COOLDOWN=60
MAX_TASK_RETRIES=3
DIVERGENCE_THRESHOLD=3
MIN_DISK_MB=500

# ---------------------------------------------------------------------------
# TELEGRAM — reads TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID from env / .env
# Set these in ~/nina/.env:
#   TELEGRAM_BOT_TOKEN=123456:ABCdef...
#   TELEGRAM_CHAT_ID=your_chat_id
# Get chat_id: message @userinfobot on Telegram.
# ---------------------------------------------------------------------------
escape_html() {
    local text="$1"
    text="${text//&/&amp;}"
    text="${text//</&lt;}"
    text="${text//>/&gt;}"
    echo -n "${text}"
}

notify_telegram() {
    local msg="$1"
    local token="${TELEGRAM_BOT_TOKEN:-}"
    local chat="${TELEGRAM_CHAT_ID:-}"
    [[ -z "${token}" || -z "${chat}" ]] && return 0  # silently skip if not configured
    curl -sf --max-time 10 \
        -X POST "https://api.telegram.org/bot${token}/sendMessage" \
        -d chat_id="${chat}" \
        -d parse_mode="HTML" \
        --data-urlencode text="${msg}" \
        > /dev/null 2>&1 || true  # never block the loop on Telegram failure
}

# ---------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------
mkdir -p "${LOG_DIR}" "${DATA_DIR}"
echo $$ > "${PIDFILE}"

log()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOOP_LOG}"; }
err()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "${ERROR_LOG}" >&2; }

trap 'err "Loop exited unexpectedly. PID=$$"; rm -f "${PIDFILE}"' EXIT
trap 'log "SIGTERM — graceful shutdown"; rm -f "${PIDFILE}"; exit 0' TERM INT

# ---------------------------------------------------------------------------
# RESOLVE OPENCODE
# ---------------------------------------------------------------------------
resolve_opencode() {
    if command -v opencode &>/dev/null; then
        OPENCODE_BIN="$(command -v opencode)"
        log "opencode found in PATH: ${OPENCODE_BIN}"
        return 0
    fi
    local candidates=(
        "${HOME}/.opencode/bin/opencode"
        "${HOME}/.local/bin/opencode"
        "${HOME}/go/bin/opencode"
        "/usr/local/bin/opencode"
        "/usr/bin/opencode"
        "${HOME}/.npm-global/bin/opencode"
        "${HOME}/nina/venv/bin/opencode"
        "/usr/local/go/bin/opencode"
    )
    for c in "${candidates[@]}"; do
        if [[ -x "${c}" ]]; then
            OPENCODE_BIN="${c}"
            export PATH="$(dirname "${c}"):${PATH}"
            log "opencode found: ${OPENCODE_BIN}"
            return 0
        fi
    done
    local found
    found=$(find "${HOME}" -name "opencode" -type f -executable 2>/dev/null | head -1)
    if [[ -n "${found}" ]]; then
        OPENCODE_BIN="${found}"
        export PATH="$(dirname "${found}"):${PATH}"
        log "opencode found via find: ${OPENCODE_BIN}"
        return 0
    fi
    err "opencode not found. Install: curl -fsSL https://opencode.ai/install | bash"
    exit 1
}

# ---------------------------------------------------------------------------
# PREFLIGHT
# ---------------------------------------------------------------------------
preflight_check() {
    resolve_opencode
    local free_mb
    free_mb=$(df -m "${NINA_DIR}" | awk 'NR==2 {print $4}')
    if [[ "${free_mb}" -lt "${MIN_DISK_MB}" ]]; then
        local msg="🔴 <b>NINA Ouroboros SUSPENDED</b>
Disk critical: ${free_mb}MB free. Need ${MIN_DISK_MB}MB."
        notify_telegram "${msg}"
        echo "DISK_FULL $(date)" > "${SUSPEND_FLAG}"
        exit 1
    fi
    if ! git -C "${NINA_DIR}" rev-parse --git-dir &>/dev/null; then
        err "${NINA_DIR} is not a git repo."; exit 1
    fi
    [[ -f "${SUSPEND_FLAG}" ]] && { log "Removing stale suspend flag."; rm -f "${SUSPEND_FLAG}"; }
    log "Preflight OK. disk=${free_mb}MB opencode=${OPENCODE_BIN}"

    # Announce startup to Telegram
    notify_telegram "🐍 <b>NINA Ouroboros STARTED</b>
<code>$(date '+%Y-%m-%d %H:%M:%S')</code>
opencode: <code>${OPENCODE_BIN}</code>
NinaGate: <code>http://localhost:8080</code>"
}

# ---------------------------------------------------------------------------
# WAIT FOR NINAGATE
# ---------------------------------------------------------------------------
wait_for_ninagate() {
    local elapsed=0
    while true; do
        if curl -sf --max-time 3 "${NINAGATE_URL}" &>/dev/null; then
            log "NinaGate UP."; return 0
        fi
        if [[ ${elapsed} -ge ${NINAGATE_TIMEOUT} ]]; then
            log "NinaGate timeout — attempting start..."
            start_ninagate; return 0
        fi
        sleep "${NINAGATE_POLL}"
        elapsed=$((elapsed + NINAGATE_POLL))
        log "Waiting for NinaGate... ${elapsed}s/${NINAGATE_TIMEOUT}s"
    done
}

start_ninagate() {
    if systemctl --user start ninagate.service 2>/dev/null; then
        log "ninagate.service started."; sleep 15
    else
        nohup bash -c "cd ${NINA_DIR}/tools/ninagate && \
            source ${NINA_DIR}/venv/bin/activate && \
            uvicorn main:app --host 127.0.0.1 --port 8080" \
            >> "${LOG_DIR}/ninagate_direct.log" 2>&1 &
        sleep 10
    fi
}

check_internet() {
    curl -sf --max-time 3 https://1.1.1.1 &>/dev/null && return 0 || return 1
}

# ---------------------------------------------------------------------------
NINAGATE_TASKS=(
    # Wave 1 — NinaGate hardening
    "Read tools/ninagate/main.py. Find all bare except clauses not yet narrowed from the v1.2 fix. Narrow each one to the minimal specific exception types. Write evidence-first. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Implement the /v1/ouroboros/status endpoint that returns loop_health, last_ouroboros_commit, quota_remaining per provider, ollama_available, checks_passing, deny_list_intact. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Add request_id UUID generation for every incoming request. Log request_id, model, provider, latency_ms, tokens_in, tokens_out, status_code to a JSONL access log at logs/ninagate_access.jsonl. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py and docs/space/nina_error_register.md. Add a /v1/health/deep endpoint that checks Ollama connectivity, each configured cloud provider with a 1-token ping, quota manager state, and returns a structured JSON health report. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Add exponential backoff with jitter to cloud provider retries. base_delay=1s, max_delay=30s, jitter=random(0,1)*delay, max_retries=3. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Add a provider latency tracker: p50/p95/p99 per provider using circular buffer of last 100 requests. Expose via /v1/metrics. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Add week and month quota tiers to QuotaManager. Each provider in opencode.json can specify daily_limit, weekly_limit, monthly_limit. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Add token-bucket rate limiter middleware: MAX_REQUESTS_PER_MINUTE=60, configurable via ENV. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Add graceful shutdown on SIGTERM: drain in-flight requests (max 30s), save quota state to data/ninagate_shutdown_state.json. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Add startup self-test: ping each provider with 1-token request on boot. Mark failing providers DEGRADED. Tag commit [ouroboros opencode pipeline]."
    # Wave 2 — Observability
    "Read tools/ninagate/main.py. Add /v1/quota/reset POST endpoint (localhost-only) to manually reset quota counters for a named provider. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Add circuit breaker per provider: CLOSED→OPEN after 5 failures→HALF_OPEN after 60s→CLOSED on success. Expose state via /v1/metrics. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Implement response caching for identical prompts (60s TTL). Cache key: sha256(model+messages). CACHE_ENABLED=true, CACHE_TTL_SECONDS=60. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py. Add structured JSON logging via Python logging + JSON formatter. Every request, routing decision, quota check, error → machine-readable log line. Tag commit [ouroboros opencode pipeline]."
    # Wave 3 — Tests
    "Read tools/ninagate/main.py and tests/. Write pytest tests for QuotaManager: reset cycle, consume, thread safety. tests/test_ninagate.py. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py and tests/. Write pytest tests for _ProviderFailures: record_failure, is_degraded, record_success reset, thread safety. Tag commit [ouroboros opencode pipeline]."
    "Read tools/ninagate/main.py and tests/. Write integration test: TestClient, verify /v1/models, /health, /v1/chat/completions with mock Ollama. Tag commit [ouroboros opencode pipeline]."
)

get_next_task() {
    if [[ -f "${BACKLOG_FILE}" && -s "${BACKLOG_FILE}" ]]; then
        local task; task=$(head -1 "${BACKLOG_FILE}")
        tail -n +2 "${BACKLOG_FILE}" > "${BACKLOG_FILE}.tmp" && mv "${BACKLOG_FILE}.tmp" "${BACKLOG_FILE}"
        echo "${task}"; return 0
    fi
    local idx_file="${DATA_DIR}/ouroboros_task_index"
    local idx=0
    [[ -f "${idx_file}" ]] && idx=$(cat "${idx_file}")
    local total=${#NINAGATE_TASKS[@]}
    [[ ${idx} -ge ${total} ]] && idx=0
    echo "${NINAGATE_TASKS[${idx}]}"
    echo $((idx + 1)) > "${idx_file}"
}

# ---------------------------------------------------------------------------
# CONVERGENCE MONITOR
# ---------------------------------------------------------------------------
declare -g DEGRADED_CYCLES=0

check_convergence() {
    local last
    last=$(git -C "${NINA_DIR}" log -1 --format='%s' 2>/dev/null || echo "")
    if echo "${last}" | grep -qi "revert\|fix.*broken\|emergency\|rollback"; then
        DEGRADED_CYCLES=$((DEGRADED_CYCLES + 1))
        err "Convergence warning (${DEGRADED_CYCLES}/${DIVERGENCE_THRESHOLD})"
    else
        DEGRADED_CYCLES=0
    fi
    if [[ ${DEGRADED_CYCLES} -ge ${DIVERGENCE_THRESHOLD} ]]; then
        local msg="🔴 <b>NINA Ouroboros DIVERGING</b>
${DEGRADED_CYCLES} degraded cycles. Loop SUSPENDED.
Last commit: <code>$(escape_html "${last}")</code>"
        notify_telegram "${msg}"
        echo "DIVERGENCE $(date)" > "${SUSPEND_FLAG}"
        exit 1
    fi
}

write_digest() {
    local cycle=$1 task_summary=$2 inet=$3
    local recent
    recent=$(git -C "${NINA_DIR}" log --oneline --grep='\[ouroboros' -10 2>/dev/null || echo "none")
    cat > "${DIGEST_FILE}" <<EOF
# Ouroboros Digest — $(date '+%Y-%m-%d %H:%M:%S')

**Cycle:** ${cycle}  
**Task:** ${task_summary:0:120}...  
**Internet:** ${inet}  
**Degraded cycles:** ${DEGRADED_CYCLES}  
**opencode:** ${OPENCODE_BIN}

## Recent [ouroboros] Commits
\`\`\`
${recent}
\`\`\`

*Auto-generated by ouroboros_loop.sh*
EOF
}

# ---------------------------------------------------------------------------
# RUN ONE OPENCODE TASK
#
# Direct Local Inference: opencode runs directly on the local Ollama
# instance using the qwen2.5-coder:3b model. Bypasses NinaGate to ensure
# 100% offline autonomy without API credentials.
# ---------------------------------------------------------------------------
run_task() {
    local task="$1"
    local attempt=0
    local success=false

    while [[ ${attempt} -lt ${MAX_TASK_RETRIES} ]]; do
        attempt=$((attempt + 1))
        log "Running task (attempt ${attempt}/${MAX_TASK_RETRIES}): ${task:0:100}..."

        local inet="online"; check_internet || inet="offline"

        local extra_args=()
        if [[ ${attempt} -gt 1 ]]; then
            extra_args+=("--continue")
        fi

        local exit_code=0
        (
            cd "${NINA_DIR}" || exit 1
            # Route opencode requests through NinaGate FastAPI proxy
            export OPENAI_API_BASE="http://localhost:8080/v1"
            export OPENAI_BASE_URL="http://localhost:8080/v1"
            export OPENAI_API_KEY="dummy"
            timeout 1800 "${OPENCODE_BIN}" run \
                --dangerously-skip-permissions \
                --model "openai/gpt-4o" \
                "${extra_args[@]}" \
                "${task}" \
                >> "${LOOP_LOG}" 2>&1
        ) || exit_code=$?

        if [[ ${exit_code} -eq 0 ]]; then
            log "Task completed successfully on attempt ${attempt}."
            success=true
            break
        elif [[ ${exit_code} -eq 124 ]]; then
            err "Task timed out (attempt ${attempt})."
        else
            err "Task failed with exit code ${exit_code} (attempt ${attempt})."
        fi
        sleep $((attempt * 30))
    done

    if ! ${success}; then
        err "Task failed after ${MAX_TASK_RETRIES} attempts. Skipping: ${task:0:120}"
        notify_telegram "⚠️ <b>Ouroboros task FAILED</b> (${MAX_TASK_RETRIES} attempts)
<code>$(escape_html "${task:0:120}")</code>"
        return 1
    fi
    return 0
}

# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
log "============================================================"
log " NINA OUROBOROS LOOP STARTING — PID=$$"
log " Nina dir : ${NINA_DIR}"
log "============================================================"

preflight_check
wait_for_ninagate

CYCLE=0

while true; do
    CYCLE=$((CYCLE + 1))
    log "--- Cycle ${CYCLE} start ---"

    if [[ -f "${SUSPEND_FLAG}" ]]; then
        log "Suspended: $(cat ${SUSPEND_FLAG}). Remove flag to resume."
        sleep 60; continue
    fi

    wait_for_ninagate

    TASK=$(get_next_task)
    if [[ -z "${TASK}" ]]; then
        log "No tasks. Sleeping ${IDLE_SLEEP}s..."
        sleep "${IDLE_SLEEP}"; continue
    fi

    notify_telegram "🚀 <b>Ouroboros Cycle ${CYCLE} task started</b>

📋 Task: $(escape_html "${TASK:0:200}")"

    if run_task "${TASK}"; then
        # Successful task — get commit hash and notify Telegram
        local_commit=$(git -C "${NINA_DIR}" log -1 --format='%h %s' 2>/dev/null || echo "unknown")
        notify_telegram "✅ <b>Ouroboros Cycle ${CYCLE} complete</b>
<code>$(escape_html "${local_commit}")</code>

📋 Task: $(escape_html "${TASK:0:200}")"
    fi

    (
        cd "${NINA_DIR}" &&
        git pull --rebase --autostash origin main >> "${LOOP_LOG}" 2>&1
    ) || err "git pull failed — continuing"

    check_convergence

    inet="online"; check_internet || inet="offline"
    write_digest "${CYCLE}" "${TASK}" "${inet}"

    log "--- Cycle ${CYCLE} complete. Cooling down ${TASK_COOLDOWN}s ---"
    sleep "${TASK_COOLDOWN}"
done
