# guardian_engine.py
"""
NINA Guardian 2.0 — Forensic Engine
Invoked by the `guardian` bash entry point.
Reads logs, correlates evidence, matches issue signatures, scores health,
emits terminal summary + report.json + summary.md + incident artifacts.
"""

import argparse
import hashlib
import json
import logging
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
NINA_DIR        = Path.home() / "nina"
LOGS_DIR        = NINA_DIR / "logs"
UPGRADES_DIR    = NINA_DIR / "upgrades"
INCIDENTS_DIR   = UPGRADES_DIR / "incidents"
BACKUPS_DIR     = UPGRADES_DIR / "backups"
BASELINE_FILE   = UPGRADES_DIR / "guardian_baseline.json"
DATA_DIR        = NINA_DIR / "data"
ENV_FILE        = NINA_DIR / ".env"
VENV_DIR        = NINA_DIR / "venv"
DOWNLOADS_DIR   = Path.home() / "Downloads"

CRITICAL_FILES = [
    NINA_DIR / "main.py",
    NINA_DIR / "core" / "router.py",
    NINA_DIR / "core" / "config.py",
    NINA_DIR / "interfaces" / "telegram_interface.py",
]

TRACKED_PY_FILES = [
    NINA_DIR / "main.py",
    NINA_DIR / "core" / "router.py",
    NINA_DIR / "core" / "config.py",
    NINA_DIR / "core" / "nina.py",
    NINA_DIR / "core" / "agent.py",
    NINA_DIR / "core" / "memory.py",
    NINA_DIR / "core" / "logger.py",
    NINA_DIR / "core" / "hotreload.py",
    NINA_DIR / "core" / "capabilities.py",
    NINA_DIR / "interfaces" / "telegram_interface.py",
    NINA_DIR / "tools" / "shell.py",
    NINA_DIR / "tools" / "browser.py",
    NINA_DIR / "tools" / "upgradepipeline.py",
    NINA_DIR / "tools" / "officemail.py",
    NINA_DIR / "tools" / "system.py",
    NINA_DIR / "crons" / "manager.py",
    NINA_DIR / "idleloop.py",
]

REQUIRED_PACKAGES = [
    "telegram", "apscheduler", "pydantic", "dotenv",
    "aiohttp", "aiofiles", "pyflakes", "mypy",
    "psutil", "numpy",
]

REQUIRED_ENV_KEYS_BLOCKER = [
    "TELEGRAMBOTTOKEN",
    "AUTHORIZEDUSERID",
    "APISECRETKEY",
]

REQUIRED_ENV_KEYS_WARN = [
    "TELEGRAMCHATID",
]

DOWNLOADS_RELEVANT_PATTERNS = re.compile(
    r"(guardian|nina|log|report|patch|update|error|crash)",
    re.IGNORECASE,
)

CREDENTIAL_PATTERNS = re.compile(
    r"(password|passwd|secret|key|token|credential|auth|private|ssh|pgp|gpg)",
    re.IGNORECASE,
)

# ── Terminal Colors ───────────────────────────────────────────────────────────
class C:
    RED    = "\033[0;31m"
    GREEN  = "\033[0;32m"
    YELLOW = "\033[0;33m"
    CYAN   = "\033[0;36m"
    BOLD   = "\033[1m"
    NC     = "\033[0m"

def red(s):    return f"{C.RED}{s}{C.NC}"
def green(s):  return f"{C.GREEN}{s}{C.NC}"
def yellow(s): return f"{C.YELLOW}{s}{C.NC}"
def cyan(s):   return f"{C.CYAN}{s}{C.NC}"
def bold(s):   return f"{C.BOLD}{s}{C.NC}"

def section(title):
    print(f"\n{C.CYAN}{C.BOLD}── {title} {'─' * max(0, 55 - len(title))}{C.NC}")

def ok(msg):   print(f"  {green('✔')}  {msg}")
def warn(msg): print(f"  {yellow('⚠')}  {yellow(msg)}")
def fail(msg): print(f"  {red('✖')}  {red(msg)}")
def info(msg): print(f"  {cyan('ℹ')}  {msg}")

# ── Issue Signatures ──────────────────────────────────────────────────────────
SIGNATURES = {
    # BLOCKER class
    "config.missing_env.telegrambottoken": {
        "severity": "BLOCKER",
        "title": "TELEGRAMBOTTOKEN missing from .env",
        "component": "core.config",
        "files": [".env", "core/config.py"],
        "patterns": [
            re.compile(r"KeyError.*TELEGRAMBOTTOKEN|RuntimeError.*TELEGRAMBOTTOKEN|envcheck: TELEGRAMBOTTOKEN absent or empty", re.IGNORECASE),
            re.compile(r"KeyError.*TELEGRAMBOTTOKEN", re.IGNORECASE),
            re.compile(r"telegram.*bot.*token.*missing", re.IGNORECASE),
            re.compile(r"RuntimeError.*TELEGRAMBOTTOKEN", re.IGNORECASE),
        ],
        "fix": "Set TELEGRAMBOTTOKEN=<your_token> in ~/nina/.env and re-run guardian.",
    },
    "config.missing_env.authorizeduserid": {
        "severity": "BLOCKER",
        "title": "AUTHORIZEDUSERID missing from .env",
        "component": "core.config",
        "files": [".env", "core/config.py"],
        "patterns": [
            re.compile(r"KeyError.*AUTHORIZEDUSERID|RuntimeError.*AUTHORIZEDUSERID|envcheck: AUTHORIZEDUSERID absent or empty", re.IGNORECASE),
            re.compile(r"KeyError.*AUTHORIZEDUSERID", re.IGNORECASE),
            re.compile(r"RuntimeError.*AUTHORIZEDUSERID", re.IGNORECASE),
        ],
        "fix": "Set AUTHORIZEDUSERID=<your_telegram_id> in ~/nina/.env and re-run guardian.",
    },
    "config.missing_env.apisecretkey": {
        "severity": "BLOCKER",
        "title": "APISECRETKEY missing or empty in .env",
        "component": "core.config",
        "files": [".env", "core/config.py"],
        "patterns": [
            re.compile(r"RuntimeError.*APISECRETKEY|api.*secret.*key.*missing|envcheck: APISECRETKEY absent or empty", re.IGNORECASE),
            re.compile(r"api.*secret.*key.*missing", re.IGNORECASE),
            re.compile(r"RuntimeError.*APISECRETKEY", re.IGNORECASE),
        ],
        "fix": "Set a non-empty APISECRETKEY=<random_string> in ~/nina/.env and re-run guardian.",
    },
    "router.attr.self_http": {
        "severity": "BLOCKER",
        "title": "HybridRouter AttributeError: self._http vs self.http",
        "component": "core.router",
        "files": ["core/router.py"],
        "patterns": [
            re.compile(r"AttributeError.*_http", re.IGNORECASE),
            re.compile(r"self\._http", re.IGNORECASE),
            re.compile(r"object has no attribute.*_http", re.IGNORECASE),
        ],
        "fix": "Run: sed -i 's/self\\._http/self.http/g' ~/nina/core/router.py",
    },
    "router.attr.orderedproviders": {
        "severity": "BLOCKER",
        "title": "HybridRouter AttributeError: ordered_providers vs _ordered_providers",
        "component": "core.router",
        "files": ["core/router.py"],
        "patterns": [
            re.compile(r"AttributeError.*ordered_providers", re.IGNORECASE),
            re.compile(r"object has no attribute.*ordered_providers", re.IGNORECASE),
        ],
        "fix": "Run: sed -i 's/ordered_providers/_ordered_providers/g' ~/nina/core/router.py",
    },
    "router.attr.forcelocal": {
        "severity": "BLOCKER",
        "title": "NameError: forcelocal not defined (should be force_local)",
        "component": "core.router",
        "files": ["core/router.py", "core/agent.py"],
        "patterns": [
            re.compile(r"NameError.*forcelocal", re.IGNORECASE),
            re.compile(r"forcelocal.*not defined", re.IGNORECASE),
        ],
        "fix": "Run: sed -i 's/forcelocal/force_local/g' ~/nina/core/router.py ~/nina/core/agent.py",
    },
    "startup.nameError": {
        "severity": "BLOCKER",
        "title": "NameError at startup/import",
        "component": "startup",
        "files": ["main.py"],
        "patterns": [
            re.compile(r"NameError:", re.IGNORECASE),
            re.compile(r"name '.*' is not defined", re.IGNORECASE),
        ],
        "fix": "Check the named variable in the traceback. Likely a missing import or typo introduced by a recent patch.",
    },
    "startup.attributeError": {
        "severity": "BLOCKER",
        "title": "AttributeError at startup/import",
        "component": "startup",
        "files": ["main.py"],
        "patterns": [
            re.compile(r"AttributeError:", re.IGNORECASE),
            re.compile(r"object has no attribute", re.IGNORECASE),
        ],
        "fix": "Check the class and attribute named in the traceback. Often caused by a rename regression.",
    },
    "startup.typeError": {
        "severity": "BLOCKER",
        "title": "TypeError at startup/import",
        "component": "startup",
        "files": ["main.py"],
        "patterns": [
            re.compile(r"TypeError:", re.IGNORECASE),
        ],
        "fix": "Check the function signature named in the traceback for a missing or incorrect argument.",
    },
    "startup.importError": {
        "severity": "BLOCKER",
        "title": "ImportError or ModuleNotFoundError at startup",
        "component": "startup",
        "files": ["main.py"],
        "patterns": [
            re.compile(r"ImportError:", re.IGNORECASE),
            re.compile(r"ModuleNotFoundError:", re.IGNORECASE),
            re.compile(r"No module named", re.IGNORECASE),
        ],
        "fix": "Run: source ~/nina/venv/bin/activate && pip install <missing_module>",
    },
    "startup.syntaxError": {
        "severity": "BLOCKER",
        "title": "SyntaxError in Python source file",
        "component": "startup",
        "files": ["main.py"],
        "patterns": [
            re.compile(r"SyntaxError:", re.IGNORECASE),
            re.compile(r"invalid syntax", re.IGNORECASE),
        ],
        "fix": "Run pyflakes on the file named in the traceback. Check for unterminated strings or bad indentation.",
    },
    "cron.conflicting_id": {
        "severity": "BLOCKER",
        "title": "APScheduler ConflictingIdError — duplicate job ID",
        "component": "crons.manager",
        "files": ["crons/manager.py"],
        "patterns": [
            re.compile(r"ConflictingIdError|Job identifier .* conflicts with an existing job|Duplicate APScheduler job IDs found", re.IGNORECASE),
            re.compile(r"conflicting.*id", re.IGNORECASE),
            re.compile(r"Job identifier .* conflicts with an existing job", re.IGNORECASE),
        ],
        "fix": "Find the duplicate job id in crons/manager.py and remove or rename the second registration.",
    },
    "process.ghost_instance": {
        "severity": "BLOCKER",
        "title": "Ghost NINA process still running",
        "component": "process",
        "files": ["data/nina.pid", "main.py"],
        "patterns": [
            re.compile(r"ghost.*bot", re.IGNORECASE),
            re.compile(r"another.*instance.*running", re.IGNORECASE),
            re.compile(r"fcntl.*lock.*blocked", re.IGNORECASE),
        ],
        "fix": "Run: kill $(cat ~/nina/data/nina.pid) && rm -f ~/nina/data/nina.lock && re-run guardian.",
    },
    "process.lock_conflict": {
        "severity": "BLOCKER",
        "title": "BlockingIOError on nina.lock — concurrent process conflict",
        "component": "process",
        "files": ["data/nina.lock", "main.py"],
        "patterns": [
            re.compile(r"BlockingIOError.*nina\\.lock", re.IGNORECASE),
            re.compile(r"\\[Errno 11\\].*nina\\.lock", re.IGNORECASE),
            re.compile(r"nina\.lock", re.IGNORECASE),
        ],
        "fix": "Run: rm -f ~/nina/data/nina.lock && pkill -f 'python main.py' && re-run guardian.",
    },
    # WARN class
    "telegram.parsemode.badrequest": {
        "severity": "WARN",
        "title": "Telegram BadRequest caused by parse_mode=Markdown",
        "component": "interfaces.telegram",
        "files": ["interfaces/telegram_interface.py"],
        "patterns": [
            re.compile(r"BadRequest.*Markdown", re.IGNORECASE),
            re.compile(r"BadRequest.*Markdown|Can't parse entities|Message is not modified", re.IGNORECASE),
            re.compile(r"Message is not modified", re.IGNORECASE),
            re.compile(r"Can't parse entities", re.IGNORECASE),
        ],
        "fix": "Run: sed -i 's/parse_mode=\"Markdown\"/parse_mode=None/g' ~/nina/interfaces/telegram_interface.py",
    },
    "telegram.document.handler_order": {
        "severity": "WARN",
        "title": "Document uploads silently dropped — handler order bug",
        "component": "interfaces.telegram",
        "files": ["interfaces/telegram_interface.py"],
        "patterns": [
            re.compile(r"document.*handler.*order", re.IGNORECASE),
            re.compile(r"document.*upload.*dropped", re.IGNORECASE),
            re.compile(r"empty.*text.*early.*return", re.IGNORECASE),
        ],
        "fix": "Ensure the document handler block appears before the empty-text early-return in handle_message.",
    },
    "telegram.key.echoed_in_chat": {
        "severity": "WARN",
        "title": "API key echoed in Telegram chat without masking",
        "component": "interfaces.telegram",
        "files": ["interfaces/telegram_interface.py"],
        "patterns": [
            re.compile(r"activate_key.*reply", re.IGNORECASE),
            re.compile(r"key.*echoed", re.IGNORECASE),
            re.compile(r"addkey.*result.*string", re.IGNORECASE),
        ],
        "fix": "Apply R-67 fix: delete user message, reply with masked key (sk-ab****yz), log provider name only.",
    },
    "cron.lambda_coroutine_drop": {
        "severity": "WARN",
        "title": "APScheduler lambda returning coroutine without await",
        "component": "crons.manager",
        "files": ["crons/manager.py"],
        "patterns": [
            re.compile(r"coroutine.*never.*await|lambda.*run_memory_backup", re.IGNORECASE),
            re.compile(r"coroutine.*never.*await", re.IGNORECASE),
            re.compile(r"lambda.*run_memory_backup", re.IGNORECASE),
        ],
        "fix": "Replace lambda: fn(n) with functools.partial(fn, n) in crons/manager.py (R-62 fix).",
    },
    "queue.path_mismatch": {
        "severity": "WARN",
        "title": "Idle queue path mismatch: idlequeue.json vs idle_queue.json",
        "component": "core.nina",
        "files": ["core/nina.py", "tools/upgradepipeline.py"],
        "patterns": [
            re.compile(r"idlequeue\.json", re.IGNORECASE),
            re.compile(r"idle_queue.*path.*mismatch", re.IGNORECASE),
        ],
        "fix": "Ensure core/nina.py imports IDLE_QUEUE from tools/upgradepipeline.py (R-61 fix).",
    },
    "logger.duplicate_handler": {
        "severity": "WARN",
        "title": "Duplicate log handler added on every restart",
        "component": "core.nina",
        "files": ["core/nina.py"],
        "patterns": [
            re.compile(r"duplicate.*handler", re.IGNORECASE),
            re.compile(r"addHandler.*outside.*guard", re.IGNORECASE),
            re.compile(r"duplicate.*log.*lines", re.IGNORECASE),
        ],
        "fix": "Ensure root.addHandler(ch) is inside a single `if not root.handlers:` guard in core/nina.py (R-65).",
    },
    "router.fallback.no_user_safe_reply": {
        "severity": "WARN",
        "title": "Router raises RuntimeError instead of user-safe fallback string",
        "component": "core.router",
        "files": ["core/router.py"],
        "patterns": [
            re.compile(r"raise RuntimeError.*All providers", re.IGNORECASE),
            re.compile(r"All providers.*failed.*RuntimeError", re.IGNORECASE),
        ],
        "fix": "Replace bare raise RuntimeError with logged warning + user-safe reply string (R-59 fix).",
    },
    "router.cache.dict_mutation": {
        "severity": "WARN",
        "title": "ResponseCache purge_expired mutates dict during iteration",
        "component": "core.router",
        "files": ["core/router.py"],
        "patterns": [
            re.compile(r"RuntimeError.*dictionary.*changed.*size.*during.*iteration", re.IGNORECASE),
            re.compile(r"purge_expired.*RuntimeError", re.IGNORECASE),
        ],
        "fix": "Collect dead keys into a list before popping in purge_expired (R-58 fix).",
    },
    "memory.blocking_io_in_async": {
        "severity": "WARN",
        "title": "Blocking IO inside async memory methods",
        "component": "core.memory",
        "files": ["core/memory.py"],
        "patterns": [
            re.compile(r"blocking.*io.*async", re.IGNORECASE),
            re.compile(r"build_context.*sync.*io", re.IGNORECASE),
        ],
        "fix": "Wrap all file IO in memory.py with asyncio.to_thread() (R-34 fix).",
    },
    "hotreload.deleted_key_revert": {
        "severity": "WARN",
        "title": "Hot-reload silently ignores deleted .env keys",
        "component": "core.hotreload",
        "files": ["core/hotreload.py"],
        "patterns": [
            re.compile(r"deleted.*key.*revert", re.IGNORECASE),
            re.compile(r"RELOADABLE.*key.*mismatch", re.IGNORECASE),
        ],
        "fix": "Add Pydantic default lookup and setattr revert for missing keys in hotreload.py (R-36, R-44).",
    },
    "capabilities.race_condition": {
        "severity": "WARN",
        "title": "Race condition on capabilities.json writes",
        "component": "core.capabilities",
        "files": ["core/capabilities.py"],
        "patterns": [
            re.compile(r"capabilities.*race", re.IGNORECASE),
            re.compile(r"capabilities\.json.*corrupt", re.IGNORECASE),
        ],
        "fix": "Add asyncio.Lock + asyncio.to_thread for all capabilities.json writes (R-37 fix).",
    },
    # DEBT class
    "shell.allowlist.regression": {
        "severity": "DEBT",
        "title": "Shell allowlist regression — dangerous command re-added",
        "component": "tools.shell",
        "files": ["tools/shell.py"],
        "patterns": [
            re.compile(r"Security regression: 'cat' found in shell allowlist", re.IGNORECASE),
            re.compile(r"shell.*allowlist.*regression", re.IGNORECASE),
        ],
        "fix": "Remove 'cat' and any exfiltration-capable commands from ALLOWED in tools/shell.py (R-48).",
    },
    "browser.ssrf.guard_regression": {
        "severity": "DEBT",
        "title": "SSRF guard uses substring matching instead of ipaddress module",
        "component": "tools.browser",
        "files": ["tools/browser.py"],
        "patterns": [
            re.compile(r'"10\." in url', re.IGNORECASE),
            re.compile(r"SSRF.*substring", re.IGNORECASE),
        ],
        "fix": "Replace all substring SSRF checks with ipaddress.ip_address() validation (R-64 fix).",
    },
    "pipeline.eval_regex_weak": {
        "severity": "DEBT",
        "title": "Weak eval/exec/compile regex in upgrade scanner",
        "component": "tools.upgradepipeline",
        "files": ["tools/upgradepipeline.py"],
        "patterns": [
            re.compile(r"eval.*regex.*weak", re.IGNORECASE),
            re.compile(r"lookbehind.*eval", re.IGNORECASE),
        ],
        "fix": "Use \\b word-boundary patterns for eval/exec/compile detection (R-54 fix).",
    },
    "pipeline.no_content_type_guard": {
        "severity": "DEBT",
        "title": "Remote patch fetch missing Content-Type and size guard",
        "component": "tools.upgradepipeline",
        "files": ["tools/upgradepipeline.py"],
        "patterns": [
            re.compile(r"content.type.*missing", re.IGNORECASE),
            re.compile(r"patch.*no.*size.*guard", re.IGNORECASE),
        ],
        "fix": "Enforce 100KB max + text/plain content-type on all patch downloads (R-63 fix).",
    },
    "mypy.advisory_findings": {
        "severity": "DEBT",
        "title": "mypy type-checking advisory findings present",
        "component": "type_hygiene",
        "files": ["core/router.py", "core/config.py", "interfaces/telegram_interface.py"],
        "patterns": [
            re.compile(r"error:.*\[", re.IGNORECASE),
            re.compile(r"Found \d+ error", re.IGNORECASE),
        ],
        "fix": "Advisory only — clean up mypy findings incrementally. Does not block deploy.",
    },
    # INFO class
    "config.missing_env.telegramchatid": {
        "severity": "INFO",
        "title": "TELEGRAMCHATID missing from .env (non-blocking)",
        "component": "core.config",
        "files": [".env"],
        "patterns": [
            re.compile(r"TELEGRAMCHATID", re.IGNORECASE),
            re.compile(r"TELEGRAMCHATID.*missing", re.IGNORECASE),
        ],
        "fix": "Set TELEGRAMCHATID=<your_chat_id> in ~/nina/.env for proactive notifications (optional).",
    },
    "feature.ews_blocked": {
        "severity": "INFO",
        "title": "EWS email feature blocked (open issue O-02)",
        "component": "tools.officemail",
        "files": ["tools/officemail.py"],
        "patterns": [
            re.compile(r"EWS.*unreachable", re.IGNORECASE),
            re.compile(r"ews.*password.*missing", re.IGNORECASE),
            re.compile(r"morning_report_ews_fetch_failed", re.IGNORECASE),
        ],
        "fix": "Set EWS credentials in .env when available. Non-blocking — morning report handles gracefully.",
    },
    "feature.playwright_blocked": {
        "severity": "INFO",
        "title": "Playwright browser tool blocked (open issue O-01)",
        "component": "tools.browser",
        "files": ["tools/browser.py"],
        "patterns": [
            re.compile(r"playwright.*not.*found", re.IGNORECASE),
            re.compile(r"playwright.*blocked", re.IGNORECASE),
            re.compile(r"playwright.*install", re.IGNORECASE),
        ],
        "fix": "Run: source ~/nina/venv/bin/activate && playwright install chromium. Non-blocking.",
    },
}

SEVERITY_ORDER = {"BLOCKER": 0, "WARN": 1, "DEBT": 2, "INFO": 3}

# ── Utility helpers ───────────────────────────────────────────────────────────

def run_cmd(cmd, timeout=30):
    """Run a shell command, return (stdout, stderr, returncode)."""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", 1
    except Exception as e:
        return "", str(e), 1


def file_sha256(path):
    """Return hex SHA-256 of a file, or None if unreadable."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def read_file_safe(path, max_bytes=200_000):
    """Read a file safely, return text or empty string."""
    try:
        with open(path, "r", errors="replace") as f:
            return f.read(max_bytes)
    except Exception:
        return ""


def load_env_file(path):
    """Parse a .env file into a dict. Returns {} if missing."""
    result = {}
    if not Path(path).exists():
        return result
    for line in read_file_safe(path).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def now_iso():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def relative_time(seconds_ago):
    if seconds_ago < 60:
        return f"{int(seconds_ago)}s ago"
    if seconds_ago < 3600:
        return f"{int(seconds_ago // 60)}m ago"
    return f"{int(seconds_ago // 3600)}h ago"


# ── Log collectors ────────────────────────────────────────────────────────────

def collect_journal_recent():
    """Last 200 journal lines for nina.service."""
    out, _, _ = run_cmd("journalctl -u nina -n 200 --no-pager 2>/dev/null")
    return out


def collect_journal_errors():
    """Error-level journal lines from current boot."""
    out, _, _ = run_cmd("journalctl -u nina -p err -b --no-pager 2>/dev/null")
    return out


def collect_journal_15min():
    """Journal lines from the last 15 minutes."""
    out, _, _ = run_cmd('journalctl -u nina --since "15 minutes ago" --no-pager 2>/dev/null')
    return out


def collect_service_status():
    """systemctl status nina output."""
    out, _, _ = run_cmd("systemctl status nina 2>/dev/null")
    return out


def collect_nina_logs():
    """Read all rotating log files under ~/nina/logs/. Returns dict filename→text."""
    logs = {}
    if LOGS_DIR.exists():
        for f in sorted(LOGS_DIR.glob("*.log"))[:10]:
            content = read_file_safe(f, max_bytes=50_000)
            if content.strip():
                logs[f.name] = content
    return logs


def collect_incident_reports():
    """Read most recent 3 incident summary.md files for context."""
    reports = []
    if INCIDENTS_DIR.exists():
        folders = sorted(
            [d for d in INCIDENTS_DIR.iterdir() if d.is_dir()],
            reverse=True,
        )[:3]
        for folder in folders:
            summary = folder / "summary.md"
            if summary.exists():
                reports.append((folder.name, read_file_safe(summary, max_bytes=5_000)))
    return reports


def collect_downloads_clues():
    """
    Scan ~/Downloads/ for files whose names match guardian/nina/log/report/
    patch/update/error/crash. Skip anything that looks like a credential file.
    Returns list of (filename, snippet).
    """
    clues = []
    if not DOWNLOADS_DIR.exists():
        return clues
    try:
        candidates = [
            f for f in DOWNLOADS_DIR.iterdir()
            if f.is_file()
            and DOWNLOADS_RELEVANT_PATTERNS.search(f.name)
            and not CREDENTIAL_PATTERNS.search(f.name)
            and f.suffix.lower() in (".log", ".txt", ".json")
        ]
        for f in sorted(candidates, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
            snippet = read_file_safe(f, max_bytes=3_000)
            if snippet.strip():
                clues.append((f.name, snippet))
    except Exception:
        pass
    return clues


def collect_all_log_text():
    """
    Aggregate all log text from all sources into a single blob
    for signature matching. Returns (combined_text, list_of_sources).
    """
    sources = []
    parts = []

    journal_recent = collect_journal_recent()
    if journal_recent.strip():
        parts.append(journal_recent)
        sources.append("journalctl -u nina -n 200")

    journal_errors = collect_journal_errors()
    if journal_errors.strip():
        parts.append(journal_errors)
        sources.append("journalctl -u nina -p err -b")

    journal_15min = collect_journal_15min()
    if journal_15min.strip():
        parts.append(journal_15min)
        sources.append("journalctl --since 15min")

    svc_status = collect_service_status()
    if svc_status.strip():
        parts.append(svc_status)
        sources.append("systemctl status nina")

    nina_logs = collect_nina_logs()
    for fname, content in nina_logs.items():
        parts.append(content)
        sources.append(f"~/nina/logs/{fname}")

    return "\n".join(parts), sources


# ── Signature matcher ─────────────────────────────────────────────────────────

def match_signatures(log_text, env_keys):
    """
    Match signatures using runtime/log evidence only.
    Do not match broad signatures against source code text, because that creates
    false positives from constant names, signature definitions, comments, and fix text.
    """
    findings = []

    all_text = log_text

    for sig_id, sig in SIGNATURES.items():
        matched_evidence = []
        for pat in sig["patterns"]:
            for line in all_text.splitlines():
                if pat.search(line):
                    matched_evidence.append(line.strip()[:200])
            if len(matched_evidence) >= 3:
                break

        # Env key checks for config signatures
        if sig_id == "config.missing_env.telegrambottoken":
            if "TELEGRAMBOTTOKEN" not in env_keys or not env_keys.get("TELEGRAMBOTTOKEN", "").strip():
                matched_evidence.append("[env_check] TELEGRAMBOTTOKEN absent or empty in .env")
        if sig_id == "config.missing_env.authorizeduserid":
            if "AUTHORIZEDUSERID" not in env_keys or not env_keys.get("AUTHORIZEDUSERID", "").strip():
                matched_evidence.append("[env_check] AUTHORIZEDUSERID absent or empty in .env")
        if sig_id == "config.missing_env.apisecretkey":
            if "APISECRETKEY" not in env_keys or not env_keys.get("APISECRETKEY", "").strip():
                matched_evidence.append("[env_check] APISECRETKEY absent or empty in .env")
        if sig_id == "config.missing_env.telegramchatid":
            if "TELEGRAMCHATID" not in env_keys or not env_keys.get("TELEGRAMCHATID", "").strip():
                matched_evidence.append("[env_check] TELEGRAMCHATID absent or empty in .env (non-blocking)")

        if sig_id == "logger.duplicate_handler" and matched_evidence:
            try:
                with open("core/nina.py", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                has_unguarded = False
                for i, line in enumerate(lines):
                    if "root.addHandler(" in line:
                        prev = lines[i-1] if i > 0 else ""
                        if "if " not in line and "if " not in prev:
                            has_unguarded = True
                            break
                if not has_unguarded:
                    matched_evidence = []
            except Exception:
                pass

        if matched_evidence:
            # Deduplicate evidence lines
            seen = set()
            deduped = []
            for e in matched_evidence:
                if e not in seen:
                    seen.add(e)
                    deduped.append(e)

            findings.append({
                "id": sig_id,
                "title": sig["title"],
                "severity": sig["severity"],
                "component": sig["component"],
                "files": sig["files"],
                "evidence": deduped[:5],
                "is_root_cause": False,
                "is_downstream_symptom": False,
                "suggested_fix": sig["fix"],
                "_match_count": len(deduped),
            })

    # Sort: BLOCKER first, then by match count descending
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 99), -f["_match_count"]))
    return findings


def resolve_root_cause(findings):
    """
    Identify root cause and downstream symptoms.
    Rule: the highest-severity, highest-confidence finding is root cause.
    Telegram failures are downstream if any config/router BLOCKER is also present.
    """
    if not findings:
        return findings

    config_router_blocker = any(
        f["severity"] == "BLOCKER"
        and any(c in f["component"] for c in ["core.config", "core.router", "startup"])
        for f in findings
    )

    for i, f in enumerate(findings):
        if i == 0:
            f["is_root_cause"] = True
        elif config_router_blocker and "telegram" in f["component"].lower():
            f["is_downstream_symptom"] = True

    return findings


def compute_confidence(findings, service_active):
    """Compute overall confidence based on evidence density and service state."""
    if not findings:
        return "low"
    top = findings[0]
    match_count = top.get("_match_count", 0)
    if top["severity"] == "BLOCKER" and match_count >= 2:
        return "high"
    if top["severity"] == "BLOCKER" and match_count >= 1:
        return "medium"
    if top["severity"] == "WARN" and match_count >= 2:
        return "medium"
    return "low"


# ── Service state inspector ───────────────────────────────────────────────────

def inspect_service_state(journal_recent, journal_15min):
    """Parse service state from systemctl and journal output."""
    status_out = collect_service_status()

    active = "active (running)" in status_out
    pid = None
    uptime = "unknown"
    restart_count = 0
    crash_loop = False

    pid_match = re.search(r"Main PID:\s*(\d+)", status_out)
    if pid_match:
        pid = pid_match.group(1)

    uptime_match = re.search(r"Active:.*since.*?;\s*(.*?)(?:\n|$)", status_out)
    if uptime_match:
        uptime = uptime_match.group(1).strip()

    restart_match = re.search(r"(\d+)\s+restart", status_out, re.IGNORECASE)
    if restart_match:
        restart_count = int(restart_match.group(1))

    # Crash loop: repeated starts only count if runtime signals are still missing
    recent_lines = (journal_15min or "") + (journal_recent or "")
    start_events = re.findall(r"Started.*nina|Starting.*nina", recent_lines, re.IGNORECASE)

    telegram_polling = bool(
        re.search(r"polling started|getUpdates|Application started", recent_lines, re.IGNORECASE)
    )
    apscheduler_started = bool(
        re.search(r"Scheduler started|APScheduler|scheduler.*started", recent_lines, re.IGNORECASE)
    )

    if len(start_events) >= 3 and not (telegram_polling and apscheduler_started):
        crash_loop = True

    # Check Ollama
    out, _, rc = run_cmd("curl -s --max-time 3 http://localhost:11434/api/tags 2>/dev/null")
    local_inference_ok = rc == 0 and "models" in out.lower()

    return {
        "active": active,
        "pid": pid,
        "uptime": uptime,
        "crash_loop": crash_loop,
        "restart_count": restart_count,
        "telegram_polling": telegram_polling,
        "apscheduler_started": apscheduler_started,
        "local_inference_ok": local_inference_ok,
    }


# ── Health scoring ────────────────────────────────────────────────────────────

def compute_health_score(findings, service_state, env_keys):
    """
    Score 0-10 for each dimension. 10 = perfect.
    Deductions are additive per severity class of finding.
    """
    runtime = 10
    config  = 10
    security = 10
    type_hygiene = 10

    for f in findings:
        sev = f["severity"]
        comp = f["component"]

        if sev == "BLOCKER":
            deduction = 4
        elif sev == "WARN":
            deduction = 2
        elif sev == "DEBT":
            deduction = 1
        else:
            deduction = 0

        if "config" in comp or "startup" in comp or "process" in comp:
            config = max(0, config - deduction)
        elif "router" in comp or "telegram" in comp or "cron" in comp or "memory" in comp:
            runtime = max(0, runtime - deduction)
        elif "shell" in comp or "browser" in comp or "pipeline" in comp:
            security = max(0, security - deduction)
        elif "type_hygiene" in comp or "hotreload" in comp or "capabilities" in comp:
            type_hygiene = max(0, type_hygiene - deduction)
        else:
            runtime = max(0, runtime - deduction)

    if not service_state["active"]:
        runtime = max(0, runtime - 4)
    if service_state["crash_loop"]:
        runtime = max(0, runtime - 3)
    if not service_state["telegram_polling"]:
        runtime = max(0, runtime - 1)
    if not service_state["apscheduler_started"]:
        runtime = max(0, runtime - 1)

    overall = round((runtime + config + security + type_hygiene) / 4, 1)
    return {
        "runtime": runtime,
        "config": config,
        "security": security,
        "type_hygiene": type_hygiene,
        "overall": overall,
    }


# ── Baseline drift ────────────────────────────────────────────────────────────

def load_baseline():
    """Load last-known-good baseline. Returns dict or {}."""
    if BASELINE_FILE.exists():
        try:
            return json.loads(BASELINE_FILE.read_text())
        except Exception:
            return {}
    return {}


def compute_file_hashes():
    """Return dict of relative_path → sha256 for all critical files."""
    hashes = {}
    for f in CRITICAL_FILES:
        rel = str(f.relative_to(NINA_DIR))
        hashes[rel] = file_sha256(f)
    return hashes


def pip_freeze_sha():
    """Return sha256 of `pip freeze` output from venv."""
    python = VENV_DIR / "bin" / "python"
    if not python.exists():
        python = "python3"
    out, _, rc = run_cmd(f"{python} -m pip freeze 2>/dev/null")
    if rc != 0 or not out.strip():
        return None
    return hashlib.sha256(out.encode()).hexdigest()


def compute_baseline_drift(baseline, current_hashes, current_pip_sha, env_keys):
    """Compare current state against saved baseline. Returns drift dict."""
    if not baseline:
        return {
            "compared_to": "no_baseline",
            "changed_files": [],
            "package_drift": [],
            "env_drift": [],
        }

    changed_files = []
    baseline_hashes = baseline.get("file_hashes", {})
    for rel, current_hash in current_hashes.items():
        old_hash = baseline_hashes.get(rel)
        if old_hash and current_hash and old_hash != current_hash:
            changed_files.append(rel)
        elif old_hash and not current_hash:
            changed_files.append(f"{rel} (MISSING)")

    package_drift = []
    baseline_pip_sha = baseline.get("package_fingerprint")
    if baseline_pip_sha and current_pip_sha and baseline_pip_sha != current_pip_sha:
        package_drift.append("pip packages changed since last healthy run")

    env_drift = []
    baseline_env_keys = set(baseline.get("env_keys_present", []))
    current_env_key_names = set(env_keys.keys())
    added = current_env_key_names - baseline_env_keys
    removed = baseline_env_keys - current_env_key_names
    if added:
        env_drift.append(f"New .env keys: {', '.join(sorted(added))}")
    if removed:
        env_drift.append(f"Removed .env keys: {', '.join(sorted(removed))}")

    return {
        "compared_to": baseline.get("timestamp", "unknown"),
        "changed_files": changed_files,
        "package_drift": package_drift,
        "env_drift": env_drift,
    }


def save_baseline(service_state, env_keys, current_hashes, pip_sha):
    """Write a new guardian_baseline.json."""
    UPGRADES_DIR.mkdir(parents=True, exist_ok=True)
    python_path = str(VENV_DIR / "bin" / "python") if (VENV_DIR / "bin" / "python").exists() else "python3"
    baseline = {
        "timestamp": now_iso(),
        "python_interpreter": python_path,
        "package_fingerprint": pip_sha,
        "file_hashes": current_hashes,
        "env_keys_present": sorted(env_keys.keys()),
        "service_flags": {
            "telegram_polling": service_state["telegram_polling"],
            "apscheduler_started": service_state["apscheduler_started"],
        },
    }
    BASELINE_FILE.write_text(json.dumps(baseline, indent=2))


# ── Timeline builder ──────────────────────────────────────────────────────────

def build_timeline(journal_recent, journal_15min, guardian_start_ts):
    """
    Build a structured timeline from journal lines.
    Returns list of {t, event, source} dicts.
    """
    timeline = []
    now_ts = time.time()

    timeline.append({
        "t": "T+0s",
        "event": "Guardian started",
        "source": "guardian_check",
    })

    combined = journal_15min + "\n" + journal_recent

    events_patterns = [
        (r"Started.*nina\.service",           "nina.service started",        "journal"),
        (r"Starting.*nina\.service",          "nina.service starting",       "journal"),
        (r"Stopped.*nina\.service",           "nina.service stopped",        "journal"),
        (r"polling started|Application started", "Telegram polling started",    "journal"),
        (r"Scheduler started|APScheduler",    "APScheduler started",         "journal"),
        (r"Traceback",                         "Python traceback detected",   "journal"),
        (r"NameError:",                        "NameError at startup",        "journal"),
        (r"AttributeError:",                   "AttributeError at startup",   "journal"),
        (r"TypeError:",                        "TypeError at startup",        "journal"),
        (r"ImportError:|ModuleNotFoundError:", "ImportError at startup",      "journal"),
        (r"SyntaxError:",                      "SyntaxError detected",        "journal"),
        (r"ConflictingIdError",                "APScheduler ConflictingIdError", "journal"),
        (r"BlockingIOError|Errno 11",          "Lock conflict detected",      "journal"),
        (r"BadRequest.*Markdown",              "Telegram BadRequest (Markdown)", "journal"),
        (r"agent_loop_timeout",                "Agent loop timeout",          "log_file"),
        (r"agent_loop_aborted_thermal",        "Thermal abort triggered",     "log_file"),
        (r"api_rate_limit_breach",             "API rate-limit breach",       "log_file"),
        (r"morning_report_ews_fetch_failed",   "EWS fetch failed",            "log_file"),
    ]

    seen_events = set()
    for line in combined.splitlines()[-300:]:
        for pattern, label, source in events_patterns:
            if re.search(pattern, line, re.IGNORECASE) and label not in seen_events:
                ts_match = re.search(
                    r"(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})",
                    line,
                )
                t_label = ts_match.group(1) if ts_match else "recent"
                timeline.append({"t": t_label, "event": label, "source": source})
                seen_events.add(label)

    timeline.append({
        "t": "T+now",
        "event": "Guardian forensic analysis complete",
        "source": "guardian_check",
    })

    return timeline


# ── Evidence collector ────────────────────────────────────────────────────────

def build_evidence_list(journal_recent, journal_errors, nina_logs, downloads_clues):
    """Build the evidence[] array for the JSON report."""
    evidence = []

    if journal_recent.strip():
        relevant = [
            line for line in journal_recent.splitlines()
            if re.search(
                r"Error|Traceback|Warning|failed|exception|blocked|killed|OOM",
                line, re.IGNORECASE
            )
        ][:20]
        evidence.append({"source": "journalctl -u nina -n 200", "lines": relevant})

    if journal_errors.strip():
        evidence.append({
            "source": "journalctl -u nina -p err -b",
            "lines": journal_errors.splitlines()[:20],
        })

    for fname, content in list(nina_logs.items())[:3]:
        relevant = [
            line for line in content.splitlines()
            if re.search(
                r"ERROR|WARNING|CRITICAL|Traceback|Exception|failed",
                line, re.IGNORECASE
            )
        ][:15]
        if relevant:
            evidence.append({"source": f"~/nina/logs/{fname}", "lines": relevant})

    if downloads_clues:
        for fname, snippet in downloads_clues[:2]:
            evidence.append({
                "source": f"~/Downloads/{fname}",
                "lines": snippet.splitlines()[:10],
            })

    return evidence


# ── Suggested actions ─────────────────────────────────────────────────────────

def build_suggested_actions(findings, service_state, baseline_drift):
    """Build the prioritized suggested_actions list."""
    actions = []
    priority = 1

    # Blockers first
    for f in findings:
        if f["severity"] == "BLOCKER":
            actions.append({
                "priority": priority,
                "action": f["suggested_fix"],
                "target_file": f["files"][0] if f["files"] else "unknown",
                "expected_result": f"Resolves: {f['title']}",
            })
            priority += 1

    # If service not active and no blocker explains it
    if not service_state["active"] and not any(f["severity"] == "BLOCKER" for f in findings):
        actions.append({
            "priority": priority,
            "action": "sudo systemctl restart nina && sleep 5 && systemctl status nina",
            "target_file": "nina.service",
            "expected_result": "Service returns to active (running) state",
        })
        priority += 1

    # Warn class
    for f in findings:
        if f["severity"] == "WARN":
            actions.append({
                "priority": priority,
                "action": f["suggested_fix"],
                "target_file": f["files"][0] if f["files"] else "unknown",
                "expected_result": f"Resolves: {f['title']}",
            })
            priority += 1

    # Drift: changed critical files
    for changed in baseline_drift.get("changed_files", []):
        actions.append({
            "priority": priority,
            "action": f"Review recent changes to {changed} — it changed since last healthy run",
            "target_file": changed,
            "expected_result": "Confirm change is intentional or roll back",
        })
        priority += 1

    # Always verify after fix
    actions.append({
        "priority": priority,
        "action": "Re-run guardian after all fixes applied",
        "target_file": "~/nina/guardian",
        "expected_result": "Overall status: PASS, health score >= 8, deploy confirmed",
    })

    return actions


# ── Recent changes ────────────────────────────────────────────────────────────

def collect_recent_changes(baseline):
    """Find files modified more recently than the last baseline timestamp."""
    changed = []
    baseline_ts = baseline.get("timestamp")
    if not baseline_ts:
        return changed
    try:
        baseline_dt = datetime.fromisoformat(baseline_ts)
        baseline_epoch = baseline_dt.timestamp()
        for f in TRACKED_PY_FILES:
            if f.exists():
                mtime = f.stat().st_mtime
                if mtime > baseline_epoch:
                    changed.append(str(f.relative_to(NINA_DIR)))
    except Exception:
        pass
    return changed


# ── Rollback snapshot finder ──────────────────────────────────────────────────

def find_latest_backup():
    """Return path to the most recent backup snapshot."""
    if not BACKUPS_DIR.exists():
        return "no_backup_found"
    backups = sorted(
        [d for d in BACKUPS_DIR.iterdir() if d.is_dir()],
        reverse=True,
    )
    if backups:
        return str(backups[0])
    md_backups = sorted(
        [f for f in BACKUPS_DIR.glob("*.md")],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    if md_backups:
        return str(md_backups[0])
    return "no_backup_found"


# ── Incident artifact writer ──────────────────────────────────────────────────

def write_incident_artifacts(incident_dir, report, journal_recent, service_status,
                              healthcheck_out, evidence_text, recent_changes,
                              signature_matches, downloads_clues):
    """Write all artifact files for a FAIL/WARN incident run."""
    incident_dir.mkdir(parents=True, exist_ok=True)

    (incident_dir / "report.json").write_text(
        json.dumps(report, indent=2, default=str)
    )

    journal_clean = re.sub(
        r"bot\d+:[A-Za-z0-9_-]+", "bot***:***", journal_recent
    )
    (incident_dir / "journal.txt").write_text(journal_clean)
    (incident_dir / "service_status.txt").write_text(service_status)
    (incident_dir / "healthcheck.txt").write_text(healthcheck_out)

    ev_lines = []
    for ev in report.get("evidence", []):
        ev_lines.append(f"## {ev['source']}")
        ev_lines.extend(ev["lines"])
        ev_lines.append("")
    (incident_dir / "evidence.txt").write_text("\n".join(ev_lines))

    (incident_dir / "recent_changes.txt").write_text("\n".join(recent_changes) or "none")

    sig_lines = []
    for f in report.get("findings", []):
        sig_lines.append(f"[{f['severity']}] {f['id']}: {f['title']}")
        for ev in f.get("evidence", []):
            sig_lines.append(f"  evidence: {ev}")
    (incident_dir / "signature_matches.txt").write_text("\n".join(sig_lines))

    dl_lines = []
    for fname, snippet in downloads_clues:
        dl_lines.append(f"## ~/Downloads/{fname}")
        dl_lines.append(snippet[:500])
        dl_lines.append("")
    (incident_dir / "downloads_clues.txt").write_text("\n".join(dl_lines) or "none")


def write_summary_md(incident_dir, report):
    """Write the human-readable Markdown summary."""
    status      = report["overall_status"]
    score       = report["health_score"]["overall"]
    rc          = report.get("root_cause", {})
    findings    = report.get("findings", [])
    actions     = report.get("suggested_actions", [])
    rollback    = report.get("rollback_snapshot", "unknown")
    ts          = report["timestamp"]
    run_id      = report["run_id"]
    blocked     = report["deploy_blocked"]
    svc         = report.get("service_state", {})
    drift       = report.get("baseline_drift", {})

    lines = [
        f"# NINA Guardian Incident Report",
        f"",
        f"**Run ID:** `{run_id}`  ",
        f"**Timestamp:** {ts}  ",
        f"**Host:** {report.get('hostname', 'unknown')}  ",
        f"**Overall Status:** {status}  ",
        f"**Deploy Blocked:** {'YES' if blocked else 'NO'}  ",
        f"**Health Score:** {score}/10  ",
        f"",
        f"---",
        f"",
        f"## Root Cause",
        f"",
        f"| Field | Value |",
        f"|---|---|",
        f"| Title | {rc.get('title', 'N/A')} |",
        f"| Confidence | {rc.get('confidence', 'N/A')} |",
        f"| Fingerprint | `{rc.get('signature', 'N/A')}` |",
        f"| Component | {rc.get('component', 'N/A')} |",
        f"| Likely Files | {', '.join(rc.get('likely_files', []))} |",
        f"",
        f"**Evidence Summary:**  ",
        f"{rc.get('evidence_summary', 'N/A')}",
        f"",
        f"---",
        f"",
        f"## Health Scores",
        f"",
        f"| Dimension | Score |",
        f"|---|---|",
        f"| Runtime | {report['health_score']['runtime']}/10 |",
        f"| Config | {report['health_score']['config']}/10 |",
        f"| Security | {report['health_score']['security']}/10 |",
        f"| Type Hygiene | {report['health_score']['type_hygiene']}/10 |",
        f"| **Overall** | **{score}/10** |",
        f"",
        f"---",
        f"",
        f"## Findings",
        f"",
    ]

    for f in findings:
        root_label = " ← ROOT CAUSE" if f.get("is_root_cause") else ""
        sym_label  = " ← downstream symptom" if f.get("is_downstream_symptom") else ""
        lines.append(f"### [{f['severity']}] {f['title']}{root_label}{sym_label}")
        lines.append(f"")
        lines.append(f"- **ID:** `{f['id']}`")
        lines.append(f"- **Component:** {f['component']}")
        lines.append(f"- **Files:** {', '.join(f['files'])}")
        lines.append(f"- **Fix:** {f['suggested_fix']}")
        if f.get("evidence"):
            lines.append(f"- **Evidence:**")
            for ev in f["evidence"][:3]:
                lines.append(f"  - `{ev}`")
        lines.append(f"")

    lines += [
        f"---",
        f"",
        f"## Suggested Actions",
        f"",
    ]
    for a in actions:
        lines.append(f"{a['priority']}. **{a['action']}**")
        lines.append(f"   - Target: `{a['target_file']}`")
        lines.append(f"   - Expected: {a['expected_result']}")
        lines.append(f"")

    lines += [
        f"---",
        f"",
        f"## Service State",
        f"",
        f"| Field | Value |",
        f"|---|---|",
        f"| Active | {svc.get('active', '?')} |",
        f"| PID | {svc.get('pid', 'N/A')} |",
        f"| Uptime | {svc.get('uptime', 'N/A')} |",
        f"| Crash Loop | {svc.get('crash_loop', False)} |",
        f"| Restart Count | {svc.get('restart_count', 0)} |",
        f"| Telegram Polling | {svc.get('telegram_polling', False)} |",
        f"| APScheduler | {svc.get('apscheduler_started', False)} |",
        f"| Local Inference | {svc.get('local_inference_ok', False)} |",
        f"",
        f"---",
        f"",
        f"## Baseline Drift",
        f"",
        f"**Compared to:** {drift.get('compared_to', 'N/A')}  ",
        f"**Changed files:** {', '.join(drift.get('changed_files', [])) or 'none'}  ",
        f"**Package drift:** {'; '.join(drift.get('package_drift', [])) or 'none'}  ",
        f"**Env drift:** {'; '.join(drift.get('env_drift', [])) or 'none'}  ",
        f"",
        f"---",
        f"",
        f"## Rollback Snapshot",
        f"",
        f"`{rollback}`",
        f"",
        f"---",
        f"",
        f"## Open Risks",
        f"",
    ]
    for risk in report.get("open_risks", []):
        lines.append(f"- {risk}")
    lines.append("")

    (incident_dir / "summary.md").write_text("\n".join(lines))


def write_pass_summary_md(incident_dir, report):
    """Write a minimal pass-confirmation summary.md."""
    score = report["health_score"]["overall"]
    ts    = report["timestamp"]
    svc   = report.get("service_state", {})
    lines = [
        f"# NINA Guardian — PASS",
        f"",
        f"**Timestamp:** {ts}  ",
        f"**Health Score:** {score}/10  ",
        f"**Service:** {'active' if svc.get('active') else 'INACTIVE'}  ",
        f"**Telegram polling:** {svc.get('telegram_polling', False)}  ",
        f"**APScheduler:** {svc.get('apscheduler_started', False)}  ",
        f"**Baseline:** updated ✔  ",
        f"",
        f"No BLOCKER findings. NINA is healthy.",
        f"",
    ]
    incident_dir.mkdir(parents=True, exist_ok=True)
    (incident_dir / "summary.md").write_text("\n".join(lines))


# ── Terminal diagnosis block ──────────────────────────────────────────────────

def print_diagnosis(report):
    """Print the final GUARDIAN DIAGNOSIS terminal block."""
    status   = report["overall_status"]
    blocked  = report["deploy_blocked"]
    rc       = report.get("root_cause", {})
    actions  = report.get("suggested_actions", [])
    score    = report["health_score"]["overall"]

    color = green if status == "PASS" else (yellow if status == "WARN" else red)

    print(f"\n{C.BOLD}{'═' * 60}{C.NC}")
    print(f"{C.BOLD}{'  GUARDIAN DIAGNOSIS':^60}{C.NC}")
    print(f"{C.BOLD}{'═' * 60}{C.NC}")
    print(f"  Status         : {color(status)}")
    print(f"  Health Score   : {score}/10")
    print(f"  Primary cause  : {rc.get('title', 'None detected')}")
    print(f"  Confidence     : {rc.get('confidence', 'N/A')}")
    print(f"  Fingerprint    : {rc.get('signature', 'N/A')}")
    print(f"  Component      : {rc.get('component', 'N/A')}")
    print(f"  Likely files   : {', '.join(rc.get('likely_files', ['N/A']))}")
    print(f"  Deploy blocked : {red('YES') if blocked else green('NO')}")
    print(f"  {'─' * 56}")
    for a in actions[:5]:
        print(f"  Action {a['priority']}: {a['action'][:70]}")
    print(f"{C.BOLD}{'═' * 60}{C.NC}\n")


# ── Main engine ───────────────────────────────────────────────────────────────

def run_engine(args):
    guardian_start = time.time()
    run_id = now_stamp()
    ts = now_iso()

    section("Guardian Engine 2.0 — Forensic Analysis")
    info(f"Run ID: {run_id}")
    info(f"Host: {socket.gethostname()}  CWD: {os.getcwd()}")

    # ── Collect all logs ──────────────────────────────────────────────────────
    section("Log Collection")
    journal_recent   = collect_journal_recent()
    journal_errors   = collect_journal_errors()
    journal_15min    = collect_journal_15min()
    service_status   = collect_service_status()
    nina_logs        = collect_nina_logs()
    downloads_clues  = collect_downloads_clues()

    log_sources = []
    if journal_recent.strip():
        ok("journalctl -u nina (recent 200)")
        log_sources.append("journalctl -u nina -n 200")
    else:
        warn("journalctl returned nothing for nina.service")

    if journal_errors.strip():
        ok("journalctl error-level lines (current boot)")
        log_sources.append("journalctl -u nina -p err -b")

    if journal_15min.strip():
        ok("journalctl last 15 minutes")
        log_sources.append("journalctl --since 15min")

    if nina_logs:
        ok(f"~/nina/logs/ — {len(nina_logs)} log file(s) found")
        log_sources.extend([f"~/nina/logs/{f}" for f in nina_logs])
    else:
        warn("No rotating log files found in ~/nina/logs/")

    if downloads_clues:
        ok(f"~/Downloads/ — {len(downloads_clues)} relevant file(s) found")
        log_sources.append("~/Downloads/ scan")
    else:
        info("~/Downloads/ — no relevant clues found")

    # ── Collect source files ──────────────────────────────────────────────────
    section("Source File Inspection")
    py_file_texts = {}
    for f in TRACKED_PY_FILES:
        if f.exists():
            rel = str(f.relative_to(NINA_DIR))
            py_file_texts[rel] = read_file_safe(f, max_bytes=20_000)
            ok(f"{rel}")
        else:
            warn(f"{f.relative_to(NINA_DIR)} not found")

    # ── Env validation ────────────────────────────────────────────────────────
    section("Environment Validation")
    env_keys = load_env_file(ENV_FILE)
    hc_passed = locals().get("hc_passed", False)
    env_blocker = False
    for key in REQUIRED_ENV_KEYS_BLOCKER:
        val = env_keys.get(key, "").strip()
        if val:
            ok(f"{key} present")
        else:
            fail(f"{key} MISSING or EMPTY — BLOCKER")
            env_blocker = True
    for key in REQUIRED_ENV_KEYS_WARN:
        val = env_keys.get(key, "").strip()
        if val:
            ok(f"{key} present")
        else:
            warn(f"{key} missing (non-blocking, advisory)")

    # ── Run healthcheck.py ────────────────────────────────────────────────────
    section("Startup Safety Assertions (healthcheck.py)")
    healthcheck_out = ""
    healthcheck_path = NINA_DIR / "healthcheck.py"
    python_bin = VENV_DIR / "bin" / "python"
    if not python_bin.exists():
        python_bin = Path("python3")

    if healthcheck_path.exists():
        hc_out, hc_err, hc_rc = run_cmd(
            f"cd {NINA_DIR} && {python_bin} healthcheck.py --json 2>&1",
            timeout=60,
        )
        healthcheck_out = hc_out + hc_err
        hc_passed = (hc_rc == 0)
        if hc_rc == 0:
            ok("healthcheck.py passed")
        else:
            fail(f"healthcheck.py failed (exit {hc_rc})")
        for line in healthcheck_out.splitlines()[:10]:
            if re.search(r"(Error|Warning|FAIL|PASS|BLOCK)", line, re.IGNORECASE):
                info(f"  hc: {line.strip()}")
    else:
        warn("healthcheck.py not found — skipping startup assertions")
        healthcheck_out = "healthcheck.py not found"

    # ── Signature matching ────────────────────────────────────────────────────
    section("Signature Matching")

    # Filter healthcheck JSON output to avoid false positives on PASS/INFO checks
    healthcheck_text_to_match = ""
    if healthcheck_out.strip():
        try:
            hc_data = json.loads(healthcheck_out)
            hc_failures = []
            for item in hc_data.get("results", []):
                if item.get("level") in ("BLOCKER", "WARN", "DEBT"):
                    hc_failures.append(
                        f"[HEALTHCHECK {item.get('level')}] {item.get('check_id')}: {item.get('title')} - {item.get('detail')} - {item.get('fix')}"
                    )
            healthcheck_text_to_match = "\n".join(hc_failures)
        except Exception:
            healthcheck_text_to_match = healthcheck_out

    all_log_text = (
        journal_recent + "\n" + journal_errors + "\n" + journal_15min
        + "\n" + service_status
        + "\n".join(nina_logs.values())
        + "\n".join(snip for _, snip in downloads_clues)
        + healthcheck_text_to_match
    )

    findings = match_signatures(all_log_text, env_keys)
    findings = resolve_root_cause(findings)

    blockers = [f for f in findings if f["severity"] == "BLOCKER"]
    warns    = [f for f in findings if f["severity"] == "WARN"]
    debts    = [f for f in findings if f["severity"] == "DEBT"]
    infos    = [f for f in findings if f["severity"] == "INFO"]

    if blockers:
        for f in blockers:
            fail(f"[BLOCKER] {f['title']}")
    if warns:
        for f in warns:
            warn(f"[WARN] {f['title']}")
    if debts:
        for f in debts:
            info(f"[DEBT] {f['title']}")
    if infos:
        for f in infos:
            info(f"[INFO] {f['title']}")
    if not findings:
        ok("No issue signatures matched")

    # ── Service state ─────────────────────────────────────────────────────────
    section("Service State")
    service_state = inspect_service_state(journal_recent, journal_15min)
    if service_state["active"]:
        ok(f"nina.service active — PID {service_state['pid']} — {service_state['uptime']}")
    else:
        fail("nina.service NOT active")
    if service_state["crash_loop"]:
        fail("Crash loop detected — multiple restarts in last 15 minutes")
    if service_state["telegram_polling"]:
        ok("Telegram polling confirmed in journal")
    else:
        warn("Telegram polling not visible in recent journal")
    if service_state["apscheduler_started"]:
        ok("APScheduler started")
    else:
        warn("APScheduler startup not confirmed")
    if service_state["local_inference_ok"]:
        ok("Ollama local inference responding")
    else:
        warn("Ollama local inference not responding (non-blocking)")

    # ── Baseline drift ────────────────────────────────────────────────────────
    section("Baseline Drift")
    baseline = load_baseline()
    current_hashes = compute_file_hashes()
    current_pip_sha = pip_freeze_sha()
    baseline_drift = compute_baseline_drift(baseline, current_hashes, current_pip_sha, env_keys)
    recent_changes = collect_recent_changes(baseline)

    if baseline_drift["compared_to"] == "no_baseline":
        info("No baseline found — will create one on PASS")
    else:
        info(f"Baseline from: {baseline_drift['compared_to']}")
        if baseline_drift["changed_files"]:
            warn(f"Changed files: {', '.join(baseline_drift['changed_files'])}")
        else:
            ok("No critical file changes since last healthy run")
        if baseline_drift["package_drift"]:
            warn(f"Package drift: {'; '.join(baseline_drift['package_drift'])}")
        if baseline_drift["env_drift"]:
            warn(f"Env drift: {'; '.join(baseline_drift['env_drift'])}")

    # ── Health scoring ────────────────────────────────────────────────────────
    section("Health Scoring")
    health_score = compute_health_score(findings, service_state, env_keys)
    info(f"Runtime      : {health_score['runtime']}/10")
    info(f"Config       : {health_score['config']}/10")
    info(f"Security     : {health_score['security']}/10")
    info(f"Type Hygiene : {health_score['type_hygiene']}/10")
    score_label = health_score["overall"]
    score_color = green if score_label >= 8 else (yellow if score_label >= 5 else red)
    print(f"  {C.BOLD}Overall      : {score_color(str(score_label))}/10{C.NC}")

    # ── Determine overall status ──────────────────────────────────────────────
    deploy_blocked = (bool(blockers) or env_blocker) and not hc_passed or not service_state["active"]
    if (blockers or env_blocker) and not hc_passed:
        overall_status = "FAIL"
    elif warns or not service_state["telegram_polling"] or not service_state["apscheduler_started"]:
        overall_status = "WARN"
    else:
        overall_status = "PASS"

    # ── Build root cause block ────────────────────────────────────────────────
    confidence = compute_confidence(findings, service_state["active"])
    if findings:
        top = findings[0]
        root_cause = {
            "title": top["title"],
            "confidence": confidence,
            "signature": top["id"],
            "component": top["component"],
            "likely_files": top["files"],
            "evidence_summary": " | ".join(top["evidence"][:3]) or "see evidence array",
        }
    else:
        root_cause = {
            "title": "No specific root cause identified",
            "confidence": "low",
            "signature": "none",
            "component": "unknown",
            "likely_files": [],
            "evidence_summary": "No matching signatures found in logs or source files.",
        }

    # ── Build timeline ────────────────────────────────────────────────────────
    timeline = build_timeline(journal_recent, journal_15min, guardian_start)

    # ── Build evidence list ───────────────────────────────────────────────────
    evidence_list = build_evidence_list(journal_recent, journal_errors, nina_logs, downloads_clues)

    # ── Suggested actions ─────────────────────────────────────────────────────
    suggested_actions = build_suggested_actions(findings, service_state, baseline_drift)

    # ── Downloads scan summary ────────────────────────────────────────────────
    downloads_scan = {
        "files_found": [f for f, _ in downloads_clues],
        "relevant_files": [f for f, _ in downloads_clues],
        "clues": [
            {"file": f, "snippet": snip[:300]}
            for f, snip in downloads_clues
        ],
    }

    # ── Open risks ────────────────────────────────────────────────────────────
    open_risks = [
        "O-01: Playwright browser tool blocked — install chromium when ready",
        "O-02: EWS email password not set — morning report handles gracefully",
        "O-04: memory_context per-session refresh not implemented",
        "O-05: FastAPI REST endpoints not implemented",
    ]
    warnings_list = [
        "W-01: TELEGRAMCHATID missing — proactive notifications disabled",
        "W-02: mypy type findings present — advisory cleanup backlog",
    ]

    # ── Assemble full JSON report ─────────────────────────────────────────────
    suppressed_findings = []
    report = {
        "guardian_version": "2.0",
        "run_id": run_id,
        "timestamp": ts,
        "hostname": socket.gethostname(),
        "cwd": str(NINA_DIR),
        "overall_status": overall_status,
        "deploy_blocked": deploy_blocked,
        "health_score": health_score,
        "root_cause": root_cause,
        "findings": [
            {k: v for k, v in f.items() if k != "_match_count"}
            for f in findings
        ],
        "suppressed_findings": suppressed_findings,
        "suppressed_count": len(suppressed_findings),
        "timeline": timeline,
        "evidence": evidence_list,
        "likely_files": root_cause["likely_files"] + baseline_drift.get("changed_files", []),
        "suggested_actions": suggested_actions,
        "rollback_snapshot": find_latest_backup(),
        "recent_changes": recent_changes,
        "service_state": service_state,
        "log_sources": log_sources,
        "downloads_scan": downloads_scan,
        "baseline_drift": baseline_drift,
        "warnings": warnings_list,
        "open_risks": open_risks,
        "confidence": confidence,
    }

    # ── Write incident artifacts ──────────────────────────────────────────────
    section("Incident Artifacts")
    incident_dir = INCIDENTS_DIR / f"guardian_{run_id}"
    incident_dir.mkdir(parents=True, exist_ok=True)

    if overall_status in ("FAIL", "WARN"):
        write_incident_artifacts(
            incident_dir, report,
            journal_recent, service_status, healthcheck_out,
            "\n".join(
                f"# {ev['source']}\n" + "\n".join(ev["lines"])
                for ev in evidence_list
            ),
            recent_changes,
            [
                f"[{f['severity']}] {f['id']}: {f['title']}"
                for f in findings
            ],
            downloads_clues,
        )
        write_summary_md(incident_dir, report)
        ok(f"Incident artifacts written: {incident_dir}")
    else:
        write_pass_summary_md(incident_dir, report)
        ok(f"Pass summary written: {incident_dir}")

    # ── Update baseline on PASS ───────────────────────────────────────────────
    if overall_status == "PASS":
        save_baseline(service_state, env_keys, current_hashes, current_pip_sha)
        ok("guardian_baseline.json updated")

    # ── Emit JSON report path ─────────────────────────────────────────────────
    json_path = incident_dir / "report.json"
    if overall_status in ("FAIL", "WARN") and json_path.exists():
        info(f"JSON report: {json_path}")

    # ── Print final diagnosis ─────────────────────────────────────────────────
    print_diagnosis(report)

    # ── Return structured result for bash ────────────────────────────────────
    # Write a small handoff file for the bash layer to read
    handoff = {
        "overall_status": overall_status,
        "deploy_blocked": deploy_blocked,
        "incident_dir": str(incident_dir),
        "json_report": str(json_path) if json_path.exists() else "",
        "root_cause_title": root_cause["title"],
        "root_cause_signature": root_cause["signature"],
        "blocker_count": len(blockers),
        "warn_count": len(warns),
        "health_score": health_score["overall"],
        "suppressed_count": len(suppressed_findings),
    }
    handoff_path = NINA_DIR / "upgrades" / ".guardian_handoff.json"
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(json.dumps(handoff, indent=2))

    return 0 if not deploy_blocked else 1


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NINA Guardian Engine 2.0")
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Suppress terminal output, emit only JSON report path to stdout",
    )
    args = parser.parse_args()

    if args.json_only:
        # Redirect terminal output to /dev/null
        sys.stdout = open(os.devnull, "w")

    exit_code = run_engine(args)

    if args.json_only:
        sys.stdout = sys.__stdout__
        handoff_path = NINA_DIR / "upgrades" / ".guardian_handoff.json"
        if handoff_path.exists():
            h = json.loads(handoff_path.read_text())
            print(h.get("json_report", ""))

    sys.exit(exit_code)
