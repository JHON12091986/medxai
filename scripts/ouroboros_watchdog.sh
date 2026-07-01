#!/usr/bin/env bash
# =============================================================================
# NINA OUROBOROS WATCHDOG — scripts/ouroboros_watchdog.sh
# =============================================================================
# Monitors ouroboros_loop.sh and restarts it if it dies.
# Runs as a companion process, launched by ouroboros.service.
#
# CONTINGENCIES:
#   loop process dies        → detect via PID file + process check → restart
#   loop is suspended        → watchdog does NOT override suspend flag
#                              (suspend = intentional stop by immune system)
#   watchdog itself crashes  → systemd --user auto-restarts the service unit
#   double-start guard       → checks PIDFILE before launching new instance
# =============================================================================

set -euo pipefail

NINA_DIR="${HOME}/nina"
DATA_DIR="${NINA_DIR}/data"
LOG_DIR="${NINA_DIR}/logs"

PIDFILE="${DATA_DIR}/ouroboros_loop.pid"
SUSPEND_FLAG="${DATA_DIR}/ouroboros_suspended.flag"
WATCHDOG_LOG="${LOG_DIR}/ouroboros_watchdog.log"
LOOP_SCRIPT="${NINA_DIR}/scripts/ouroboros_loop.sh"

CHECK_INTERVAL=30   # seconds between liveness checks
RESTART_DELAY=10    # seconds to wait before restarting

mkdir -p "${LOG_DIR}" "${DATA_DIR}"

wlog() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] WATCHDOG: $*" | tee -a "${WATCHDOG_LOG}"; }

trap 'wlog "Watchdog stopping (SIGTERM/INT)."; exit 0' TERM INT

wlog "Watchdog started. Monitoring ouroboros_loop.sh every ${CHECK_INTERVAL}s."

while true; do
    sleep "${CHECK_INTERVAL}"

    # Do not restart if loop is intentionally suspended
    if [[ -f "${SUSPEND_FLAG}" ]]; then
        wlog "Suspend flag present — not restarting loop: $(cat ${SUSPEND_FLAG})"
        continue
    fi

    # Check if loop process is alive
    LOOP_ALIVE=false
    if [[ -f "${PIDFILE}" ]]; then
        LOOP_PID=$(cat "${PIDFILE}" 2>/dev/null || echo "")
        if [[ -n "${LOOP_PID}" ]] && kill -0 "${LOOP_PID}" 2>/dev/null; then
            LOOP_ALIVE=true
        fi
    fi

    if ! ${LOOP_ALIVE}; then
        wlog "Loop process not running. Restarting in ${RESTART_DELAY}s..."
        sleep "${RESTART_DELAY}"

        # Double-check — avoid race with a loop that just started
        if [[ -f "${PIDFILE}" ]]; then
            LOOP_PID=$(cat "${PIDFILE}" 2>/dev/null || echo "")
            if [[ -n "${LOOP_PID}" ]] && kill -0 "${LOOP_PID}" 2>/dev/null; then
                wlog "Loop came back on its own. Not launching another."
                continue
            fi
        fi

        wlog "Launching ouroboros_loop.sh..."
        bash "${LOOP_SCRIPT}" >> "${LOG_DIR}/ouroboros_loop.log" 2>&1 &
        wlog "Loop relaunched with PID $!."
    fi
done
