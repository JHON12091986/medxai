#!/usr/bin/env bash
# =============================================================================
# NINA OUROBOROS STATUS — scripts/ouroboros_status.sh
# =============================================================================
# Quick status check. Run at any time to see loop health.
# Usage: bash ~/nina/scripts/ouroboros_status.sh
# =============================================================================

NINA_DIR="${HOME}/nina"
DATA_DIR="${NINA_DIR}/data"
LOG_DIR="${NINA_DIR}/logs"

PIDFILE="${DATA_DIR}/ouroboros_loop.pid"
SUSPEND_FLAG="${DATA_DIR}/ouroboros_suspended.flag"
DIGEST_FILE="${DATA_DIR}/ouroboros_digest.md"
IDX_FILE="${DATA_DIR}/ouroboros_task_index"

echo "=================================================================="
echo " NINA OUROBOROS STATUS — $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================================="

# Service
echo ""
echo "--- systemd unit ---"
systemctl --user status nina-ouroboros.service --no-pager 2>/dev/null || echo "Service not installed."

# Loop process
echo ""
echo "--- Loop process ---"
if [[ -f "${PIDFILE}" ]]; then
    PID=$(cat "${PIDFILE}")
    if kill -0 "${PID}" 2>/dev/null; then
        echo "ALIVE  PID=${PID}"
    else
        echo "DEAD   (stale PID=${PID})"
    fi
else
    echo "UNKNOWN (no PID file)"
fi

# Suspend flag
echo ""
echo "--- Suspend status ---"
if [[ -f "${SUSPEND_FLAG}" ]]; then
    echo "SUSPENDED: $(cat ${SUSPEND_FLAG})"
else
    echo "NOT SUSPENDED — loop is running"
fi

# Task index
echo ""
echo "--- Task index ---"
if [[ -f "${IDX_FILE}" ]]; then
    echo "Next task index: $(cat ${IDX_FILE}) / 17 built-in tasks"
fi

# Recent [ouroboros] commits
echo ""
echo "--- Recent [ouroboros] commits ---"
git -C "${NINA_DIR}" log --oneline --grep='\[ouroboros\]' -10 2>/dev/null || echo "none"

# NinaGate health
echo ""
echo "--- NinaGate ---"
curl -sf --max-time 3 http://localhost:8080/v1/models > /dev/null 2>&1 && \
    echo "UP   http://localhost:8080" || echo "DOWN http://localhost:8080"

# Last digest
echo ""
echo "--- Last digest ---"
if [[ -f "${DIGEST_FILE}" ]]; then
    head -10 "${DIGEST_FILE}"
else
    echo "No digest yet."
fi

# Recent errors
echo ""
echo "--- Recent errors (last 5) ---"
ERR_LOG="${LOG_DIR}/ouroboros_errors.log"
if [[ -f "${ERR_LOG}" ]]; then
    tail -5 "${ERR_LOG}"
else
    echo "No errors logged."
fi

echo ""
echo "=================================================================="
