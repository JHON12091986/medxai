#!/usr/bin/env python3
"""
nina_diag.py — NINA Forensic Diagnostic Tool v2  [ouroboros]
============================================================
Run from ~/nina:  python scripts/nina_diag.py [--full]

PURPOSE
-------
Surgically scan ALL logs and state files for PROBLEMS ONLY.
Output is concise, deduplicated, and paste-ready for ARCHITECT OVERWATCH.
Every ⚠ finding ends with a FIX: directive — exact command or file:line to patch.

SECTIONS
--------
 1. SERVICE STATE         — systemd health + restart count
 2. JOURNAL ERRORS        — filtered/deduped ERROR/WARN/Traceback lines only
 3. ROOT TRACEBACK        — first unhandled exception in last 200 journal lines
 4. NINAGATE LOG          — last 50 lines of ninagate.log, errors only
 5. OUROBOROS HEALTH      — loop heartbeat, divergence detection, /health probe
 6. LOCK / PID FILES      — stale lock detection
 7. IMPORT CHECK          — critical module import smoke-test
 8. ENV KEY PRESENCE      — required .env keys
 9. DUPLICATE PROCESSES   — ghost python/main.py instances
10. ERROR REGISTER        — last 5 entries from nina_error_register.md
11. RESOURCES             — disk / RAM / Python version
12. LAST 5 COMMITS        — git log oneline
──  ACTIONABLE SUMMARY    — all ⚠ findings + FIX directives, copy-paste ready

Usage:
  python scripts/nina_diag.py           # concise (errors only)
  python scripts/nina_diag.py --full    # include ✓ OK lines too
"""

import os, sys, re, json, subprocess, textwrap
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
from pathlib import Path
from datetime import datetime, timezone

try:
    from core.constants import (
        ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID,
        ENV_API_SECRET_KEY, ENV_OPENAI_API_KEY, ENV_GEMINI_API_KEY,
    )
except Exception:
    ENV_TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
    ENV_TELEGRAM_CHAT_ID   = "TELEGRAM_CHAT_ID"
    ENV_API_SECRET_KEY     = "API_SECRET_KEY"
    ENV_OPENAI_API_KEY     = "OPENAI_API_KEY"
    ENV_GEMINI_API_KEY     = "GEMINI_API_KEY"

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.parent
NINA_DIR    = ROOT
DATA_DIR    = NINA_DIR / "data"
LOGS_DIR    = NINA_DIR / "logs"
VENV_PY     = NINA_DIR / ".venv/bin/python3"
ENV_FILE    = NINA_DIR / ".env"
NINAGATE_LOG    = LOGS_DIR / "ninagate.log"
OUROBOROS_LOG   = LOGS_DIR / "ouroboros.log"
ERROR_REGISTER  = NINA_DIR / "docs/space/nina_error_register.md"
OUROBOROS_STATE = NINA_DIR / "data/ouroboros_state.json"
NINAGATE_HOST   = "http://localhost:7860"

FULL = "--full" in sys.argv

# ── Output helpers ─────────────────────────────────────────────────────────────
SEP    = "─" * 68
out    = []       # all output lines
issues = []       # (section, description, fix) tuples for summary

def section(title):    out.append(f"\n{SEP}\n## {title}\n{SEP}")
def line(k, v):        out.append(f"  {k:<30} {v}")
def emit_ok(msg):
    if FULL: out.append(f"  ✓  {msg}")
def emit_warn(msg, fix=""):
    out.append(f"  ⚠  {msg}")
    if fix:
        out.append(f"     FIX: {fix}")
        issues.append((msg, fix))
    else:
        issues.append((msg, "— see section above"))
def emit_crit(msg, fix=""):
    out.append(f"  🔴 {msg}")
    fix_str = fix or "— see section above"
    out.append(f"     FIX: {fix_str}")
    issues.append((msg, fix_str))

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return f"ERROR: {e}"

def probe_http(url, timeout=4):
    """Return (ok:bool, body:str)."""
    try:
        import urllib.request
        resp = urllib.request.urlopen(url, timeout=timeout)
        return True, resp.read().decode()[:200]
    except Exception as e:
        return False, str(e)

# ── Error keyword patterns ─────────────────────────────────────────────────────
ERROR_RX = re.compile(
    r"(error|traceback|exception|failed|critical|fatal|"
    r"signal 15|sigterm|sigabrt|conflict|cancelled|"
    r"importerror|syntaxerror|attributeerror|typeerror|"
    r"valueerror|runtimeerror|filenotfound|permissionerror|"
    r"connectionrefused|timeout|refused connection|"
    r"quota exceeded|rate.?limit|401|403|500|503)",
    re.IGNORECASE,
)

def filter_errors(lines, max_lines=60):
    """Return only lines matching ERROR_RX, deduplicated, max max_lines."""
    seen = {}
    result = []
    for ln in lines:
        if ERROR_RX.search(ln):
            key = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\s]*", "TS", ln)
            key = re.sub(r"\bpid=\d+\b", "pid=N", key)
            key = re.sub(r"\s+", " ", key).strip()[:120]
            seen[key] = seen.get(key, 0) + 1
    deduped = []
    seen2   = {}
    for ln in lines:
        if ERROR_RX.search(ln):
            key = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\s]*", "TS", ln)
            key = re.sub(r"\bpid=\d+\b", "pid=N", key)
            key = re.sub(r"\s+", " ", key).strip()[:120]
            if key not in seen2:
                seen2[key] = True
                count = seen[key]
                suffix = f"  [{count}×]" if count > 1 else ""
                deduped.append(ln[-140:] + suffix)
                if len(deduped) >= max_lines:
                    break
    return deduped


# ══════════════════════════════════════════════════════════════════════════════
# 1. SERVICE STATE
# ══════════════════════════════════════════════════════════════════════════════
section("1. SERVICE STATE  (systemd nina.service)")
svc = run(
    "systemctl --user show nina.service "
    "--property=ActiveState,SubState,Result,MainPID,NRestarts,ExecMainStatus"
)
state = {}
for l in svc.splitlines():
    if "=" in l:
        k, v = l.split("=", 1)
        state[k] = v

active  = state.get("ActiveState",    "?")
sub     = state.get("SubState",       "?")
result  = state.get("Result",         "?")
nrest   = state.get("NRestarts",      "0")
pid     = state.get("MainPID",        "0")

line("ActiveState",    active)
line("SubState",       sub)
line("Result",         result)
line("NRestarts",      nrest)
line("MainPID",        pid)

if active != "active":
    emit_crit(
        f"nina.service is {active}/{sub} (Result={result})",
        "systemctl --user restart nina.service && journalctl --user -u nina.service -n 50 --no-pager",
    )
elif int(nrest or 0) >= 3:
    emit_warn(
        f"NRestarts={nrest} — service is crash-looping",
        "journalctl --user -u nina.service -n 100 --no-pager | grep -E 'Traceback|Error'",
    )
else:
    emit_ok(f"nina.service active ({nrest} restarts)")

if pid and pid != "0":
    mem = run(f"cat /proc/{pid}/status 2>/dev/null | grep -E 'VmRSS|VmPeak'")
    for m in mem.splitlines():
        parts = m.split(":")
        if len(parts) == 2:
            line("  " + parts[0].strip(), parts[1].strip())


# ══════════════════════════════════════════════════════════════════════════════
# 2. JOURNAL ERRORS  (last 300 lines, filtered)
# ══════════════════════════════════════════════════════════════════════════════
section("2. JOURNAL ERRORS  (last 300 lines → errors/warns only, deduped)")
journal_raw = run(
    "journalctl --user -u nina.service -n 300 --no-pager --output=short-monotonic 2>/dev/null"
)
jlines = journal_raw.splitlines()
error_lines = filter_errors(jlines, max_lines=40)
if error_lines:
    for el in error_lines:
        out.append("  ⚠  " + el)
    emit_warn(
        f"{len(error_lines)} unique error pattern(s) in journal",
        "See ROOT TRACEBACK section (§3) for the full exception chain",
    )
else:
    emit_ok("No ERROR/WARN/Traceback patterns in last 300 journal lines")


# ══════════════════════════════════════════════════════════════════════════════
# 3. ROOT TRACEBACK  (first Traceback in last 300 journal lines)
# ══════════════════════════════════════════════════════════════════════════════
section("3. ROOT TRACEBACK  (first unhandled exception)")
full_j  = run("journalctl --user -u nina.service -n 300 --no-pager --output=cat 2>/dev/null")
fjlines = full_j.splitlines()
tb_start = next((i for i, l in enumerate(fjlines) if "Traceback" in l), None)
if tb_start is not None:
    tb_block = fjlines[tb_start : tb_start + 30]
    for l in tb_block:
        out.append("    " + l)
    # Extract the final "XxxError: ..." line for the fix directive
    last_err = next(
        (l for l in reversed(tb_block) if re.match(r"\s*\w+Error:", l)), ""
    ).strip()
    # Try to extract file+line reference
    file_ref = next(
        (l for l in reversed(tb_block) if 'File "' in l), ""
    ).strip()
    emit_crit(
        f"Unhandled exception: {last_err[:100]}",
        f"Check {file_ref[:80]} — fix the exception, then: systemctl --user restart nina.service",
    )
else:
    emit_ok("No Traceback found in last 300 journal lines")


# ══════════════════════════════════════════════════════════════════════════════
# 4. NINAGATE LOG  (errors only)
# ══════════════════════════════════════════════════════════════════════════════
section(f"4. NINAGATE LOG  ({NINAGATE_LOG})")
if NINAGATE_LOG.exists():
    try:
        ng_lines = NINAGATE_LOG.read_text(errors="replace").splitlines()[-200:]
        ng_errors = filter_errors(ng_lines, max_lines=25)
        if ng_errors:
            for el in ng_errors:
                out.append("  ⚠  " + el)
            emit_warn(
                f"{len(ng_errors)} ninagate error pattern(s) found",
                f"tail -100 {NINAGATE_LOG} | grep -E 'ERROR|quota|rate.?limit|500|503'",
            )
        else:
            emit_ok("ninagate.log — no errors in last 200 lines")
        # Last 3 lines regardless for context
        out.append("  [last 3 lines]")
        for l in ng_lines[-3:]:
            out.append("    " + l[-140:])
    except Exception as e:
        emit_warn(f"Cannot read ninagate.log: {e}")
else:
    emit_warn(
        "ninagate.log not found",
        f"mkdir -p {LOGS_DIR} — ninagate may not be writing logs; check LOG_FILE in ninagate_server.py",
    )

# Also check ouroboros.log
if OUROBOROS_LOG.exists():
    try:
        ob_lines = OUROBOROS_LOG.read_text(errors="replace").splitlines()[-100:]
        ob_errors = filter_errors(ob_lines, max_lines=10)
        if ob_errors:
            out.append(f"  ⚠  ouroboros.log errors ({len(ob_errors)}):")
            for el in ob_errors[:5]:
                out.append("    " + el)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# 5. OUROBOROS HEALTH
# ══════════════════════════════════════════════════════════════════════════════
section("5. OUROBOROS HEALTH  (loop heartbeat + /health probe + divergence)")

# 5a. State file heartbeat
if OUROBOROS_STATE.exists():
    try:
        st = json.loads(OUROBOROS_STATE.read_text())
        last_ts = st.get("last_cycle_ts") or st.get("last_run") or st.get("ts")
        cycles  = st.get("cycles", "?")
        consec_fail = st.get("consecutive_failures", 0)
        if last_ts:
            try:
                last_dt = datetime.fromisoformat(str(last_ts).replace("Z", "+00:00"))
                now_utc = datetime.now(timezone.utc)
                age_min = (now_utc - last_dt).total_seconds() / 60
                line("Last cycle", f"{last_ts}  ({age_min:.1f} min ago)")
                line("Total cycles", str(cycles))
                if age_min > 30:
                    emit_crit(
                        f"Ouroboros loop STALE — last cycle {age_min:.0f} min ago (>30 min)",
                        "bash scripts/ouroboros_loop.sh  OR  systemctl --user restart ouroboros.service",
                    )
                elif age_min > 10:
                    emit_warn(
                        f"Ouroboros loop SLOW — {age_min:.0f} min since last cycle",
                        "Check ouroboros.log for blocking step",
                    )
                else:
                    emit_ok(f"Ouroboros loop healthy — {age_min:.1f} min ago")
            except Exception as e:
                emit_warn(f"Cannot parse last_cycle_ts: {e}")
        else:
            emit_warn(
                "ouroboros_state.json has no timestamp key",
                "Add 'last_cycle_ts': datetime.utcnow().isoformat() write in ouroboros_loop.sh",
            )
        # Divergence check
        if isinstance(consec_fail, int) and consec_fail >= 3:
            emit_crit(
                f"DIVERGENCE: {consec_fail} consecutive ouroboros failures",
                "Manual audit required — run: python scripts/nina_diag.py --full && check jules_backlog.md",
            )
        elif isinstance(consec_fail, int) and consec_fail > 0:
            emit_warn(f"{consec_fail} consecutive failure(s) in ouroboros state")
    except Exception as e:
        emit_warn(f"Cannot parse ouroboros_state.json: {e}")
else:
    emit_warn(
        "ouroboros_state.json not found — loop may never have run",
        f"Run: bash scripts/ouroboros_loop.sh  (creates {OUROBOROS_STATE})",
    )

# 5b. NinaGate /health probe
ok_h, body_h = probe_http(f"{NINAGATE_HOST}/health")
if ok_h:
    emit_ok(f"NinaGate /health → {body_h[:60]}")
else:
    emit_crit(
        f"NinaGate /health UNREACHABLE: {body_h[:80]}",
        "systemctl --user status ninagate.service  OR  cd ~/nina && uvicorn ninagate.ninagate_server:app --port 7860",
    )

# 5c. Ouroboros systemd service (if registered)
ob_svc = run("systemctl --user is-active ouroboros.service 2>/dev/null")
if ob_svc == "active":
    emit_ok("ouroboros.service is active")
elif ob_svc not in ("", "inactive"):
    emit_warn(
        f"ouroboros.service is {ob_svc}",
        "systemctl --user restart ouroboros.service",
    )


# ══════════════════════════════════════════════════════════════════════════════
# 6. LOCK / PID FILES
# ══════════════════════════════════════════════════════════════════════════════
section("6. LOCK / PID FILES")
for fname in ["data/nina.pid", "data/nina.lock"]:
    p = NINA_DIR / fname
    if p.exists():
        try:
            content = p.read_text().strip()
        except Exception:
            content = "?"
        pid_val = content if fname.endswith(".pid") else ""
        alive   = ""
        if pid_val.isdigit():
            alive = "ALIVE" if Path(f"/proc/{pid_val}").exists() else "DEAD — stale!"
        tag = "stale" if "stale" in alive else "present"
        if "stale" in alive:
            emit_crit(
                f"Stale {fname}  pid={pid_val}",
                f"rm {NINA_DIR / fname}  && systemctl --user restart nina.service",
            )
        else:
            emit_warn(f"{fname} present  pid={pid_val}  {alive}")
    else:
        emit_ok(f"{fname} — clean (not present)")


# ══════════════════════════════════════════════════════════════════════════════
# 7. CRITICAL IMPORT CHECK
# ══════════════════════════════════════════════════════════════════════════════
section("7. CRITICAL IMPORT CHECK  (smoke-test via .venv)")
IMPORTS = [
    "from core.nina import Nina",
    "from core.router import HybridRouter",
    "from core.memory import MemorySystem",
    "from core.scheduler import NinaScheduler",
    "from core.reflexion import ReflexionEngine",
    "from core.observability import get_hub",
    "from telegram.ext import Application",
    "import fastapi",
]
import_failures = 0
for imp in IMPORTS:
    result = run(f'cd {NINA_DIR} && {VENV_PY} -c "{imp}" 2>&1', timeout=15)
    if result == "":
        emit_ok(imp)
    else:
        import_failures += 1
        first_line = result.splitlines()[0][:120] if result else "?"
        emit_crit(
            f"IMPORT FAIL: {imp}",
            f"cd ~/nina && {VENV_PY} -c \"{imp}\"  →  {first_line}",
        )
if import_failures == 0:
    emit_ok("All critical imports OK")


# ══════════════════════════════════════════════════════════════════════════════
# 8. ENV KEY PRESENCE
# ══════════════════════════════════════════════════════════════════════════════
section("8. ENV KEYS  (.env presence check — values NOT shown)")
REQUIRED_KEYS = [
    "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
    "OPENAI_API_KEY", "GEMINI_API_KEY",
    "API_SECRET_KEY",
]
OPTIONAL_KEYS = [
    "ANTHROPIC_API_KEY", "GROQ_API_KEY", "MISTRAL_API_KEY",
    "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "CEREBRAS_API_KEY",
    "ALLOWED_USERS", "OLLAMA_HOST",
]
if ENV_FILE.exists():
    env_text = ENV_FILE.read_text()
    for key in REQUIRED_KEYS:
        found = bool(re.search(rf"^{key}\s*=\s*.+", env_text, re.MULTILINE))
        if found:
            emit_ok(f"{key}: SET")
        else:
            emit_crit(f"{key}: MISSING", f"echo '{key}=YOUR_VALUE' >> {ENV_FILE}")
    for key in OPTIONAL_KEYS:
        found = bool(re.search(rf"^{key}\s*=\s*.+", env_text, re.MULTILINE))
        if found:
            emit_ok(f"{key}: SET (optional)")
        else:
            if FULL:
                out.append(f"  –  {key}: not set (optional)")
    # ALLOWED_USERS special check
    if not re.search(r"^ALLOWED_USERS\s*=\s*.+", env_text, re.MULTILINE):
        emit_warn(
            "ALLOWED_USERS not set — ALL incoming Telegram messages may be rejected",
            "echo 'ALLOWED_USERS=your_chat_id' >> .env",
        )
else:
    emit_crit(".env file NOT FOUND", f"cp {NINA_DIR}/.env.example {ENV_FILE}  (then fill in keys)")


# ══════════════════════════════════════════════════════════════════════════════
# 9. DUPLICATE PROCESSES
# ══════════════════════════════════════════════════════════════════════════════
section("9. DUPLICATE NINA PROCESSES")
procs = run("ps aux | grep -E 'python.*main\\.py' | grep -v grep | grep -v nina_diag")
if procs:
    plines = procs.splitlines()
    if len(plines) > 1:
        emit_crit(
            f"{len(plines)} python/main.py processes — likely ghost/zombie",
            "pkill -f 'python.*main.py' && systemctl --user restart nina.service",
        )
    else:
        emit_ok("Single python/main.py process (expected)")
        if FULL:
            out.append("  " + plines[0][-120:])
else:
    emit_warn("No python/main.py found — service may be down")

# Also check ninagate
ng_procs = run("ps aux | grep -E 'uvicorn.*ninagate' | grep -v grep")
if ng_procs:
    ng_count = len(ng_procs.splitlines())
    if ng_count > 1:
        emit_warn(
            f"{ng_count} uvicorn/ninagate processes",
            "pkill -f 'uvicorn.*ninagate' && systemctl --user restart ninagate.service",
        )
    else:
        emit_ok("Single uvicorn/ninagate process")
else:
    emit_warn("No uvicorn/ninagate process found — NinaGate may be down")


# ══════════════════════════════════════════════════════════════════════════════
# 10. ERROR REGISTER  (last 5 entries)
# ══════════════════════════════════════════════════════════════════════════════
section(f"10. ERROR REGISTER  ({ERROR_REGISTER.name} — last 5 entries)")
if ERROR_REGISTER.exists():
    try:
        er_text  = ERROR_REGISTER.read_text(errors="replace")
        # Find entries by ## or date-prefixed headers
        entries  = re.split(r"\n(?=##|\d{4}-\d{2}-\d{2})", er_text)
        recent   = [e.strip() for e in entries if e.strip()][-5:]
        for entry in recent:
            lines_e = entry.splitlines()
            out.append("  ──")
            for el in lines_e[:6]:
                out.append("    " + el[:120])
        if not recent:
            emit_ok("Error register is empty — no known issues")
    except Exception as e:
        emit_warn(f"Cannot read error register: {e}")
else:
    emit_warn(
        f"{ERROR_REGISTER} not found",
        f"touch {ERROR_REGISTER}",
    )


# ══════════════════════════════════════════════════════════════════════════════
# 11. RESOURCES
# ══════════════════════════════════════════════════════════════════════════════
section("11. RESOURCES")
disk_nina = run(f"du -sh {NINA_DIR} 2>/dev/null | cut -f1")
disk_free = run("df -h / | tail -1 | awk '{print $4\" free of \"$2}'")
ram_free  = run("free -h | grep Mem | awk '{print $7\" available of \"$2}'")
py_ver    = run(f"{VENV_PY} --version 2>&1")
line("Disk ~/nina",  disk_nina)
line("Disk free /",  disk_free)
line("RAM free",     ram_free)
line("Python (.venv)", py_ver)

# Warn on low disk
disk_free_gb_str = run("df --output=avail / | tail -1").strip()
try:
    avail_kb = int(disk_free_str) if (disk_free_str := disk_free_gb_str) else 0
    if avail_kb < 1_000_000:   # < 1 GB
        emit_crit(
            f"LOW DISK: only {disk_free_gb_str} KB free",
            "du -sh ~/nina/logs/* | sort -h  →  remove old logs",
        )
except Exception:
    pass


# ══════════════════════════════════════════════════════════════════════════════
# 12. LAST 5 COMMITS
# ══════════════════════════════════════════════════════════════════════════════
section("12. LAST 5 COMMITS  (git log)")
git_log = run(f"cd {NINA_DIR} && git log --oneline -5 2>/dev/null")
for gl in git_log.splitlines():
    out.append("  " + gl)


# ══════════════════════════════════════════════════════════════════════════════
# ACTIONABLE SUMMARY — all ⚠/🔴 findings + FIX directives
# ══════════════════════════════════════════════════════════════════════════════
section("ACTIONABLE SUMMARY  — paste to ARCHITECT OVERWATCH")
line("Timestamp",     datetime.now().strftime("%Y-%m-%d %H:%M:%S +06"))
line("Service",       f"{active}/{sub}  (restarts={nrest})")
line("Issues found",  str(len(issues)))

out.append("")
if issues:
    for i, (desc, fix) in enumerate(issues, 1):
        out.append(f"  [{i:02d}] {desc[:90]}")
        out.append(f"       FIX: {fix[:120]}")
        out.append("")
else:
    out.append("  🟢 ALL CLEAR — no problems detected")

out.append(SEP)
out.append("END OF NINA FORENSIC DIAGNOSTIC REPORT — nina_diag.py v2  [ouroboros]")
out.append(SEP)

print("\n".join(out))
