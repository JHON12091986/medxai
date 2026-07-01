#!/usr/bin/env bash
# ============================================================
# nina_boot_fix.sh — 1-click post-reboot NINA recovery
# Usage: bash ~/nina/scripts/nina_boot_fix.sh
# Fixes: sentence_transformers missing, ghost procs, service
#        restart, ninagate restart, final health probe.
# ============================================================
set -euo pipefail

NINA_DIR="$HOME/nina"
VENV="$NINA_DIR/.venv"
PY="$VENV/bin/python3"
PIP="$VENV/bin/pip"

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'
CYN='\033[0;36m'; BLD='\033[1m'; RST='\033[0m'

step() { echo -e "\n${CYN}${BLD}── $1 ──${RST}"; }
ok()   { echo -e "  ${GRN}✓ $1${RST}"; }
warn() { echo -e "  ${YLW}⚠ $1${RST}"; }
fail() { echo -e "  ${RED}✗ $1${RST}"; }

echo -e "${BLD}╔══════════════════════════════════════════╗"
echo -e "║   NINA BOOT FIX  •  $(date '+%Y-%m-%d %H:%M:%S')   ║"
echo -e "╚══════════════════════════════════════════╝${RST}"

cd "$NINA_DIR"

# ── 1. Kill ghost main.py processes ──────────────────────────
step "1/6  Kill ghost processes"
GHOSTS=$(pgrep -f 'python.*main\.py' 2>/dev/null || true)
if [[ -n "$GHOSTS" ]]; then
    pkill -f 'python.*main\.py' && ok "Killed ghost PIDs: $GHOSTS" || warn "pkill returned non-zero (already dead)"
    sleep 1
else
    ok "No ghost processes found"
fi

# ── 2. Install missing Python packages ───────────────────────
step "2/6  Install missing packages into .venv"
if [[ ! -x "$PIP" ]]; then
    fail ".venv not found at $VENV — run: python3 -m venv $VENV"
    exit 1
fi

PACKAGES=(sentence-transformers)
for pkg in "${PACKAGES[@]}"; do
    if "$PY" -c "import ${pkg//-/_}" 2>/dev/null; then
        ok "$pkg already installed"
    else
        warn "$pkg missing — installing..."
        "$PIP" install --quiet "$pkg" && ok "$pkg installed" || { fail "pip install $pkg FAILED"; exit 1; }
    fi
done

# ── 3. Smoke-test critical imports ───────────────────────────
step "3/6  Smoke-test core imports"
IMPORTS=(
    "from core.nina import Nina"
    "from core.router import HybridRouter"
    "from core.memory import MemorySystem"
    "from core.scheduler import NinaScheduler"
    "from core.reflexion import ReflexionEngine"
    "from core.observability import get_hub"
)
FAIL=0
for imp in "${IMPORTS[@]}"; do
    if "$PY" -c "$imp" 2>/dev/null; then
        ok "$imp"
    else
        fail "$imp"
        FAIL=$((FAIL+1))
    fi
done
if [[ $FAIL -gt 0 ]]; then
    fail "$FAIL import(s) still failing — check logs above before restarting services"
    exit 1
fi

# ── 4. Restart nina.service ───────────────────────────────────
step "4/6  Restart nina.service"
systemctl --user daemon-reload
systemctl --user restart nina.service
sleep 3
STATUS=$(systemctl --user is-active nina.service 2>/dev/null || echo "unknown")
if [[ "$STATUS" == "active" ]]; then
    ok "nina.service is ACTIVE"
else
    fail "nina.service is $STATUS — tailing last 20 lines:"
    journalctl --user -u nina.service -n 20 --no-pager || true
    exit 1
fi

# ── 5. Restart ninagate.service ───────────────────────────────
step "5/6  Restart ninagate.service"
if systemctl --user cat ninagate.service &>/dev/null; then
    systemctl --user restart ninagate.service
    sleep 3
    NG_STATUS=$(systemctl --user is-active ninagate.service 2>/dev/null || echo "unknown")
    if [[ "$NG_STATUS" == "active" ]]; then
        ok "ninagate.service is ACTIVE"
    else
        warn "ninagate.service is $NG_STATUS — check: journalctl --user -u ninagate.service -n 30 --no-pager"
    fi
else
    warn "ninagate.service unit not found — skipping (start manually if needed)"
fi

# ── 6. Health probe ───────────────────────────────────────────
step "6/6  NinaGate /health probe"
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:7860/health 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
    ok "NinaGate /health → HTTP 200 ✓"
else
    warn "NinaGate /health → HTTP $HTTP_CODE (may still be warming up)"
    warn "Retry: curl http://localhost:7860/health"
fi

# ── Final summary ─────────────────────────────────────────────
echo ""
echo -e "${BLD}${GRN}╔══════════════════════════════════════════╗"
echo -e "║          NINA BOOT FIX COMPLETE          ║"
echo -e "╚══════════════════════════════════════════╝${RST}"
echo -e "  nina.service   : $(systemctl --user is-active nina.service 2>/dev/null || echo 'unknown')"
echo -e "  ninagate       : $(systemctl --user is-active ninagate.service 2>/dev/null || echo 'unknown')"
echo -e "  NinaGate health: HTTP $HTTP_CODE"
echo -e "\n  Run diag anytime: python scripts/nina_diag.py"
echo -e "  Tail logs:        journalctl --user -u nina.service -f\n"
