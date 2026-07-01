#!/usr/bin/env bash
# ============================================================
# NINA ONE-CLICK FIX  — aibony/nina
# Fixes: duplicate processes, missing core/scheduler.py,
#        stale lock/pid files, .env missing keys
# Run: cd ~/nina && bash nina_fix.sh
# ============================================================
set -euo pipefail
NINA_DIR="$HOME/nina"
cd "$NINA_DIR"

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "${GRN}  ✓  $*${NC}"; }
warn() { echo -e "${YLW}  ⚠  $*${NC}"; }
err()  { echo -e "${RED}  ✗  $*${NC}"; }
step() { echo -e "\n${BLU}══ $* ${NC}"; }

echo -e "${CYN}"
echo "╔══════════════════════════════════════════════╗"
echo "║     NINA ONE-CLICK FIX — $(date '+%H:%M:%S')      ║"
echo "╚══════════════════════════════════════════════╝${NC}"

# ── 1. Stop service ─────────────────────────────────────────
step "1/6  STOP NINA SERVICE"
systemctl --user stop nina.service 2>/dev/null && ok "Stopped" || warn "Was not running"

# ── 2. Kill duplicate processes ─────────────────────────────
step "2/6  KILL DUPLICATE PROCESSES"
PIDS=$(pgrep -f "python.*main\.py" 2>/dev/null || true)
if [[ -n "$PIDS" ]]; then
    echo "$PIDS" | xargs kill -9 2>/dev/null; sleep 1
    ok "Killed PIDs: $PIDS"
else
    ok "No stray processes"
fi

# ── 3. Clean stale lock/pid ──────────────────────────────────
step "3/6  CLEAN STALE LOCK / PID FILES"
rm -f data/nina.pid data/nina.lock && ok "Cleaned data/nina.pid + data/nina.lock"

# ── 4. Create core/scheduler.py stub ────────────────────────
step "4/6  CREATE core/scheduler.py STUB"
if [[ -f core/scheduler.py ]]; then
    ok "Already exists — skipping"
else
python3 - << 'PYEOF'
stub = '''"""
core/scheduler.py — NinaScheduler stub.
Auto-created by nina_fix.sh. Replace with full impl when ready.
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger("nina.scheduler")


class NinaScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Dhaka")
        self._jobs: dict = {}
        logger.info("NinaScheduler initialised (stub)")

    async def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("NinaScheduler started")

    async def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("NinaScheduler stopped")

    def add_job(self, func, trigger, job_id: str = None, **kwargs):
        job = self.scheduler.add_job(func, trigger, id=job_id, **kwargs)
        if job_id:
            self._jobs[job_id] = job
        return job

    def remove_job(self, job_id: str) -> None:
        try:
            self.scheduler.remove_job(job_id)
            self._jobs.pop(job_id, None)
        except Exception as e:
            logger.warning("remove_job(%s): %s", job_id, e)

    @property
    def running(self) -> bool:
        return self.scheduler.running
'''
with open("core/scheduler.py", "w") as f:
    f.write(stub)
print("  ✓  core/scheduler.py stub written")
PYEOF
fi

# ── 5. .env key audit ────────────────────────────────────────
step "5/6  .ENV KEY AUDIT"
MISSING=()
for key in TELEGRAM_BOT_TOKEN TELEGRAMBOTTOKEN TELEGRAM_CHAT_ID \
           TELEGRAMCHATID ALLOWED_USERS ANTHROPIC_API_KEY; do
    val=$(grep -E "^${key}=" .env 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'" | xargs 2>/dev/null || true)
    if [[ -z "$val" ]]; then MISSING+=("$key"); warn "$key → EMPTY"
    else ok "$key = SET"; fi
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo ""
    warn "Fill missing keys in ~/nina/.env, then restart:"
    warn "  systemctl --user restart nina.service"
fi

# ── 6. Import check + restart ────────────────────────────────
step "6/6  VERIFY IMPORTS + RESTART"
PYTHON=""
for p in "$NINA_DIR/.venv/bin/python3" "$NINA_DIR/venv/bin/python3"; do
    [[ -x "$p" ]] && PYTHON="$p" && break
done
[[ -z "$PYTHON" ]] && { err "No venv python found"; exit 1; }
ok "venv: $PYTHON"

IMPORT_OK=true
for mod in core.nina core.scheduler core.router core.memory crons.manager; do
    if "$PYTHON" -c "import sys,os; sys.path.insert(0,os.getcwd()); __import__('$mod')" 2>/dev/null; then
        ok "import $mod"
    else
        err "import $mod  FAILED"
        IMPORT_OK=false
    fi
done

if $IMPORT_OK; then
    ok "All imports clean — restarting"
    systemctl --user daemon-reload
    systemctl --user restart nina.service
    sleep 3
    STATUS=$(systemctl --user is-active nina.service 2>/dev/null || echo "unknown")
    if [[ "$STATUS" == "active" ]]; then
        ok "nina.service ACTIVE ✓"
        systemctl --user status nina.service --no-pager -l | tail -6
    else
        err "nina.service: $STATUS"
        systemctl --user status nina.service --no-pager -l | tail -12
    fi
else
    warn "Import errors remain — service NOT restarted. Fix errors and re-run."
fi

echo -e "\n${CYN}══ DONE $(date '+%H:%M:%S') ══${NC}"
