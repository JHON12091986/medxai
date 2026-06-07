# healthcheck.py
"""
NINA Guardian 2.0 — Startup Safety Assertions
Invoked by the `guardian` bash entry point before every deploy.
Catches import-time errors, validates env keys, checks package presence,
and emits a structured pass/fail report.
Exit 0 = all BLOCKER checks passed (advisory warnings may still be present).
Exit 1 = at least one BLOCKER check failed — deploy must be halted.
"""

import ast
import importlib
import importlib.util
import json
import os
import sys
import re
import subprocess
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
NINA_DIR    = Path(__file__).parent.resolve()
ENV_FILE    = NINA_DIR / ".env"
VENV_DIR    = NINA_DIR / "venv"

# ── Output mode ───────────────────────────────────────────────────────────────
JSON_MODE = "--json" in sys.argv
METRICS_MODE = "--metrics" in sys.argv

# ── Result accumulator ────────────────────────────────────────────────────────
results = []
blocker_count = 0
warn_count    = 0

def record(level, check_id, title, detail="", fix=""):
    global blocker_count, warn_count
    entry = {
        "level":    level,
        "check_id": check_id,
        "title":    title,
        "detail":   detail,
        "fix":      fix,
    }
    results.append(entry)
    if level == "BLOCKER":
        blocker_count += 1
    elif level == "WARN":
        warn_count += 1
    if not JSON_MODE:
        prefix = {
            "BLOCKER": "[BLOCKER] ✖",
            "WARN":    "[WARN]    ⚠",
            "PASS":    "[PASS]    ✔",
            "INFO":    "[INFO]    ℹ",
        }.get(level, "[???]")
        print(f"  {prefix}  {title}")
        if detail and level in ("BLOCKER", "WARN"):
            for line in detail.splitlines()[:3]:
                print(f"             {line}")

# ── §1 · Env file presence ────────────────────────────────────────────────────
def check_env_file():
    if ENV_FILE.exists():
        record("PASS", "env.file_present", ".env file present")
    else:
        record(
            "BLOCKER", "env.file_missing",
            ".env file missing",
            detail=f"Expected at: {ENV_FILE}",
            fix="Create ~/nina/.env with required keys. See nina_problem_log.md §R-10.",
        )

# ── §2 · Env key validation ───────────────────────────────────────────────────
def load_env():
    env = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env

def check_env_keys(env):
    BLOCKER_KEYS = [
        ("TELEGRAMBOTTOKEN",  "config.missing_env.telegrambottoken"),
        ("AUTHORIZEDUSERID",  "config.missing_env.authorizeduserid"),
        ("APISECRETKEY",        "config.missing_env.apisecretkey"),
    ]
    ADVISORY_KEYS = [
        ("TELEGRAMCHATID",    "config.missing_env.telegramchatid"),
    ]

    for key, sig_id in BLOCKER_KEYS:
        val = env.get(key, "").strip()
        if val:
            record("PASS", f"env.{key.lower()}", f"Env key present: {key}")
        else:
            record(
                "BLOCKER", sig_id,
                f"Env key MISSING or EMPTY: {key}",
                detail=f"Key '{key}' is required for NINA to start.",
                fix=f"Add {key}=<value> to ~/nina/.env and re-run guardian.",
            )

    for key, sig_id in ADVISORY_KEYS:
        val = env.get(key, "").strip()
        if val:
            record("PASS", f"env.{key.lower()}", f"Env key present: {key}")
        else:
            record(
                "INFO", sig_id,
                f"Env key missing (non-blocking): {key}",
                detail="TELEGRAMCHATID enables proactive notifications. Not required for startup.",
                fix=f"Optionally add {key}=<your_chat_id> to ~/nina/.env.",
            )

# ── §3 · Package presence ─────────────────────────────────────────────────────
REQUIRED_PACKAGES = [
    ("telegram",    "python-telegram-bot",  "BLOCKER"),
    ("apscheduler", "APScheduler",          "BLOCKER"),
    ("pydantic",    "pydantic",             "BLOCKER"),
    ("dotenv",      "python-dotenv",        "BLOCKER"),
    ("aiohttp",     "aiohttp",              "BLOCKER"),
    ("aiofiles",    "aiofiles",             "BLOCKER"),
    ("psutil",      "psutil",               "BLOCKER"),
    ("numpy",       "numpy",                "BLOCKER"),
    ("pyflakes",    "pyflakes",             "WARN"),
    ("mypy",        "mypy",                 "WARN"),
]

def check_packages():
    for import_name, pip_name, level in REQUIRED_PACKAGES:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            record("PASS", f"pkg.{import_name}", f"Package present: {import_name}")
        else:
            record(
                level, f"pkg.{import_name}_missing",
                f"Package missing: {import_name} ({pip_name})",
                detail=f"import {import_name} failed — module not found in current Python path.",
                fix=f"Run: source ~/nina/venv/bin/activate && pip install {pip_name}",
            )

# ── §4 · Syntax validation (ast.parse) ───────────────────────────────────────
SYNTAX_CHECK_FILES = [
    "main.py",
    "core/config.py",
    "core/router.py",
    "core/nina.py",
    "core/agent.py",
    "core/memory.py",
    "core/logger.py",
    "core/hotreload.py",
    "core/capabilities.py",
    "interfaces/telegram_interface.py",
    "tools/shell.py",
    "tools/browser.py",
    "tools/upgradepipeline.py",
    "tools/officemail.py",
    "tools/system.py",
    "crons/manager.py",
    "idleloop.py",
]

def check_syntax():
    for rel in SYNTAX_CHECK_FILES:
        full = NINA_DIR / rel
        if not full.exists():
            record("INFO", f"syntax.missing.{rel.replace('/','.')}", f"File not found: {rel}")
            continue
        try:
            source = full.read_text(errors="replace")
            ast.parse(source, filename=rel)
            record("PASS", f"syntax.{rel.replace('/','.')}", f"Syntax OK: {rel}")
        except SyntaxError as e:
            record(
                "BLOCKER", "startup.syntaxError",
                f"SyntaxError in {rel}: {e.msg} (line {e.lineno})",
                detail=f"File: {rel}\nLine: {e.lineno}\nMessage: {e.msg}\nText: {e.text or ''}",
                fix=f"Open ~/nina/{rel} at line {e.lineno} and fix the syntax error.",
            )
        except Exception as e:
            record(
                "WARN", f"syntax.parse_error.{rel.replace('/','.')}",
                f"Parse error in {rel}: {e}",
                detail=str(e),
                fix=f"Inspect ~/nina/{rel} for encoding or unusual syntax issues.",
            )

# ── §5 · Core module import assertions ───────────────────────────────────────
CORE_MODULES = [
    ("core.config",       "core/config.py"),
    ("core.logger",       "core/logger.py"),
    ("core.capabilities", "core/capabilities.py"),
    ("core.memory",       "core/memory.py"),
    ("core.router",       "core/router.py"),
    ("core.agent",        "core/agent.py"),
    ("core.nina",         "core/nina.py"),
    ("core.hotreload",    "core/hotreload.py"),
]

# Error classes that are always BLOCKER regardless of module
BLOCKER_EXCEPTIONS = (NameError, TypeError, AttributeError, ImportError, SyntaxError)

def check_core_imports():
    # Ensure nina dir is on sys.path
    nina_str = str(NINA_DIR)
    if nina_str not in sys.path:
        sys.path.insert(0, nina_str)

    for mod_name, rel_path in CORE_MODULES:
        full_path = NINA_DIR / rel_path
        if not full_path.exists():
            record(
                "INFO", f"import.missing.{mod_name.replace('.','_')}",
                f"Module file not found: {rel_path} — skipping import check",
            )
            continue
        try:
            # Use importlib to attempt the import in isolation
            spec = importlib.util.spec_from_file_location(mod_name, full_path)
            if spec is None or spec.loader is None:
                record("WARN", f"import.spec_none.{mod_name.replace('.','_')}",
                       f"Could not build import spec for {mod_name}")
                continue
            module = importlib.util.module_from_spec(spec)
            # Temporarily add to sys.modules to allow relative imports
            sys.modules[mod_name] = module
            try:
                spec.loader.exec_module(module)
                record("PASS", f"import.{mod_name.replace('.','_')}", f"Import OK: {mod_name}")
            except BLOCKER_EXCEPTIONS as e:
                exc_type = type(e).__name__
                sig_map = {
                    "NameError":      "startup.nameError",
                    "TypeError":      "startup.typeError",
                    "AttributeError": "startup.attributeError",
                    "ImportError":    "startup.importError",
                    "SyntaxError":    "startup.syntaxError",
                }
                sig_id = sig_map.get(exc_type, "startup.importError")
                record(
                    "BLOCKER", sig_id,
                    f"{exc_type} importing {mod_name}: {e}",
                    detail=(
                        f"Module: {mod_name}\n"
                        f"File:   {rel_path}\n"
                        f"Error:  {exc_type}: {e}"
                    ),
                    fix=f"Inspect ~/nina/{rel_path} for the symbol named in the error. "
                        f"Check recent patches via nina_update_log.md.",
                )
            except Exception as e:
                # Non-BLOCKER exception (e.g. missing .env at import time) — WARN only
                record(
                    "WARN", f"import.runtime_error.{mod_name.replace('.','_')}",
                    f"Runtime error importing {mod_name}: {type(e).__name__}: {e}",
                    detail=str(e),
                    fix=f"Check ~/nina/{rel_path} — may require .env to be fully populated.",
                )
            finally:
                # Remove from sys.modules to avoid polluting subsequent checks
                sys.modules.pop(mod_name, None)
        except Exception as outer:
            record(
                "WARN", f"import.outer_error.{mod_name.replace('.','_')}",
                f"Outer error testing import of {mod_name}: {outer}",
                detail=str(outer),
                fix=f"Inspect ~/nina/{rel_path} manually.",
            )

# ── §6 · Router attribute regression checks ───────────────────────────────────
# These are the exact attribute-name regressions from R-69, R-70, R-72
# that caused live outages. We scan the source text directly.
def check_router_regressions():
    router_path = NINA_DIR / "core" / "router.py"
    if not router_path.exists():
        record("INFO", "router.regression.missing", "core/router.py not found — skipping regression scan")
        return

    source = router_path.read_text(errors="replace")

    # R-72: self._http (must be self.http)
    if re.search(r"self\._http\b", source):
        record(
            "BLOCKER", "router.attr.self_http",
            "Regression: self._http found in core/router.py (should be self.http)",
            detail="Pattern: self._http — causes AttributeError at runtime on every provider call.",
            fix="Run: sed -i 's/self\\._http/self.http/g' ~/nina/core/router.py",
        )
    else:
        record("PASS", "router.attr.self_http", "Router attribute self.http — OK")

    # R-69: ordered_providers (must be _ordered_providers)
    if re.search(r"(?<!_)ordered_providers\b", source):
        record(
            "BLOCKER", "router.attr.orderedproviders",
            "Regression: ordered_providers (non-underscore) found in core/router.py",
            detail="Pattern: ordered_providers — should be _ordered_providers.",
            fix="Run: sed -i 's/\\bordered_providers\\b/_ordered_providers/g' ~/nina/core/router.py",
        )
    else:
        record("PASS", "router.attr.orderedproviders", "Router attribute _ordered_providers — OK")

    # R-70: forcelocal (must be force_local)
    if re.search(r"\bforcelocal\b", source):
        record(
            "BLOCKER", "router.attr.forcelocal",
            "Regression: forcelocal (camelCase) found in core/router.py",
            detail="Pattern: forcelocal — should be force_local.",
            fix="Run: sed -i 's/\\bforcelocal\\b/force_local/g' ~/nina/core/router.py ~/nina/core/agent.py",
        )
    else:
        record("PASS", "router.attr.forcelocal", "Router attribute force_local — OK")

    # R-58: dict mutation during iteration in purge_expired
    if re.search(r"for\s+k.*in\s+self\.s\.items\(\).*self\.s\.pop", source, re.DOTALL):
        record(
            "WARN", "router.cache.dict_mutation",
            "Potential dict mutation during iteration in ResponseCache.purge_expired",
            detail="Iterating self.s.items() while calling self.s.pop() causes RuntimeError.",
            fix="Collect dead keys into a list first, then pop in a separate loop (R-58 fix).",
        )
    else:
        record("PASS", "router.cache.dict_mutation", "ResponseCache purge_expired — OK")

# ── §7 · Shell allowlist regression ──────────────────────────────────────────
def check_shell_allowlist():
    shell_path = NINA_DIR / "tools" / "shell.py"
    if not shell_path.exists():
        record("INFO", "shell.allowlist.missing", "tools/shell.py not found — skipping allowlist check")
        return

    source = shell_path.read_text(errors="replace")

    # R-48: 'cat' must not be in ALLOWED
    if re.search(r"['\"]cat['\"]", source):
        record(
            "BLOCKER", "shell.allowlist.regression",
            "Security regression: 'cat' found in shell allowlist (tools/shell.py)",
            detail="'cat' in ALLOWED enables unrestricted file reads including .env and SSH keys.",
            fix="Remove 'cat' from the ALLOWED set in ~/nina/tools/shell.py (R-48 fix).",
        )
    else:
        record("PASS", "shell.allowlist.regression", "Shell allowlist — 'cat' not present — OK")

    # Check for shell=True without injection protection
    if re.search(r"shell\s*=\s*True", source) and not re.search(r"shlex\.split", source):
        record(
            "WARN", "shell.injection_risk",
            "tools/shell.py uses shell=True without shlex.split — injection risk",
            detail="shell=True without tokenisation can allow command injection.",
            fix="Add shlex.split() and a shell operator blocklist (R-40 fix).",
        )
    else:
        record("PASS", "shell.injection_risk", "Shell injection protection — OK")

# ── §8 · SSRF guard regression ────────────────────────────────────────────────
def check_ssrf_guard():
    browser_path = NINA_DIR / "tools" / "browser.py"
    if not browser_path.exists():
        record("INFO", "browser.ssrf.missing", "tools/browser.py not found — skipping SSRF check")
        return

    source = browser_path.read_text(errors="replace")

    # R-64: substring SSRF checks are bad — ipaddress module must be used
    substring_ssrf = re.search(r'"10\." in url|"192\.168" in url|"172\." in url', source)
    ipaddress_used = re.search(r"import ipaddress|from ipaddress", source)

    if substring_ssrf and not ipaddress_used:
        record(
            "DEBT", "browser.ssrf.guard_regression",
            "SSRF guard uses substring matching — ipaddress module not used",
            detail="Substring SSRF checks are bypassable. Use ipaddress.ip_address() (R-64 fix).",
            fix="Replace substring checks with ipaddress.ip_address() range validation in tools/browser.py.",
        )
    else:
        record("PASS", "browser.ssrf.guard_regression", "SSRF guard — ipaddress module in use — OK")

# ── §9 · Duplicate cron ID check ─────────────────────────────────────────────
def check_cron_ids():
    mgr_path = NINA_DIR / "crons" / "manager.py"
    if not mgr_path.exists():
        record("INFO", "cron.manager.missing", "crons/manager.py not found — skipping cron ID check")
        return

    source = mgr_path.read_text(errors="replace")
    ids_found = re.findall(r"id\s*=\s*['\"]([^'\"]+)['\"]", source)
    seen = {}
    duplicates = []
    for job_id in ids_found:
        seen[job_id] = seen.get(job_id, 0) + 1
    for job_id, count in seen.items():
        if count > 1:
            duplicates.append(job_id)

    if duplicates:
        record(
            "BLOCKER", "cron.conflicting_id",
            f"Duplicate APScheduler job ID(s) found: {', '.join(duplicates)}",
            detail=f"Duplicate IDs in crons/manager.py: {duplicates}. Causes ConflictingIdError on startup.",
            fix="Remove or rename duplicate job registrations in ~/nina/crons/manager.py (R-23 fix).",
        )
    else:
        record("PASS", "cron.conflicting_id", "APScheduler job IDs — no duplicates — OK")

    # R-62: lambda coroutine drop
    if re.search(r"lambda\s*:\s*\w+\(", source) and not re.search(r"functools\.partial", source):
        record(
            "WARN", "cron.lambda_coroutine_drop",
            "APScheduler jobs may use lambda instead of functools.partial",
            detail="lambda: coroutine_fn(n) is sync; APScheduler will call it without awaiting.",
            fix="Replace lambda: fn(n) with functools.partial(fn, n) in crons/manager.py (R-62 fix).",
        )
    else:
        record("PASS", "cron.lambda_coroutine_drop", "APScheduler job callables — functools.partial in use — OK")

# ── §10 · Idle queue path consistency ─────────────────────────────────────────
def check_idle_queue_path():
    nina_path     = NINA_DIR / "core" / "nina.py"
    pipeline_path = NINA_DIR / "tools" / "upgradepipeline.py"

    if not nina_path.exists() or not pipeline_path.exists():
        record("INFO", "queue.path_mismatch.missing", "core/nina.py or tools/upgradepipeline.py not found — skipping")
        return

    nina_src     = nina_path.read_text(errors="replace")

    # R-61: idlequeue.json is the wrong path
    if re.search(r"idlequeue\.json", nina_src) and not re.search(r"IDLE_QUEUE", nina_src):
        record(
            "WARN", "queue.path_mismatch",
            "core/nina.py uses hardcoded 'idlequeue.json' instead of importing IDLE_QUEUE",
            detail="Should import IDLE_QUEUE from tools/upgradepipeline.py (single source of truth).",
            fix="Add: from tools.upgradepipeline import IDLE_QUEUE and use it in run_idle_summary (R-61).",
        )
    else:
        record("PASS", "queue.path_mismatch", "Idle queue path — IDLE_QUEUE imported correctly — OK")

# ── §11 · Duplicate log handler check ────────────────────────────────────────
def check_duplicate_log_handler():
    nina_path = NINA_DIR / "core" / "nina.py"
    if not nina_path.exists():
        record("INFO", "logger.duplicate_handler.missing", "core/nina.py not found — skipping handler check")
        return

    source = nina_path.read_text(errors="replace")

    handler_guard_count = len(re.findall(r"if not root\.handlers", source))
    add_handler_count   = len(re.findall(r"root\.addHandler", source))

    if handler_guard_count == 0 and add_handler_count > 0:
        record(
            "WARN", "logger.duplicate_handler",
            "root.addHandler called without 'if not root.handlers' guard in core/nina.py",
            detail="Duplicate handlers added on every restart → duplicate log lines.",
            fix="Wrap root.addHandler(ch) inside a single 'if not root.handlers:' guard (R-65 fix).",
        )
    elif add_handler_count > handler_guard_count + 1:
        record(
            "WARN", "logger.duplicate_handler",
            f"Multiple addHandler calls ({add_handler_count}) vs guard blocks ({handler_guard_count}) in core/nina.py",
            detail="Some addHandler calls may be outside the guard, causing duplicate log lines.",
            fix="Ensure every root.addHandler(ch) is inside a single guard (R-65 fix).",
        )
    else:
        record("PASS", "logger.duplicate_handler", "Log handler guard — OK")

# ── §12 · Upgrade pipeline security checks ───────────────────────────────────
def check_pipeline_security():
    pipeline_path = NINA_DIR / "tools" / "upgradepipeline.py"
    if not pipeline_path.exists():
        record("INFO", "pipeline.missing", "tools/upgradepipeline.py not found — skipping pipeline checks")
        return

    source = pipeline_path.read_text(errors="replace")

    # R-54: weak eval/exec regex (no word boundaries)
    has_word_boundary = re.search(r"\\b(eval|exec|compile)\\b", source)
    has_eval_pattern  = re.search(r"eval|exec|compile", source)
    if has_eval_pattern and not has_word_boundary:
        record(
            "DEBT", "pipeline.eval_regex_weak",
            "Upgrade pipeline eval/exec pattern may lack \\b word boundaries",
            detail="Without word boundaries, 'evaluate' or 'executor' could be falsely flagged.",
            fix="Use re.compile(r'\\b(eval|exec|compile)\\b') in tools/upgradepipeline.py (R-54 fix).",
        )
    else:
        record("PASS", "pipeline.eval_regex_weak", "Pipeline eval/exec regex — OK")

    # R-63: content-type and size guard
    has_content_type = re.search(r"content.type|Content-Type", source, re.IGNORECASE)
    has_size_guard   = re.search(r"100.*1024|max.*size|content.*length", source, re.IGNORECASE)
    if not has_content_type or not has_size_guard:
        record(
            "DEBT", "pipeline.no_content_type_guard",
            "Upgrade pipeline may be missing Content-Type or size guard on remote fetch",
            detail="Fetching patches without Content-Type/size guard allows binary or oversized data.",
            fix="Enforce text/plain + 100KB max on all patch downloads (R-63 fix).",
        )
    else:
        record("PASS", "pipeline.no_content_type_guard", "Pipeline content-type + size guard — OK")

# ── §13 · Data directory and lock file ───────────────────────────────────────
def check_data_dir():
    data_dir  = NINA_DIR / "data"
    lock_file = data_dir / "nina.lock"

    if not data_dir.exists():
        record(
            "WARN", "data_dir.missing",
            "data/ directory not found — will be created at startup",
            fix="Run: mkdir -p ~/nina/data",
        )
    else:
        record("PASS", "data_dir.present", "data/ directory present")

    if lock_file.exists():
        record(
            "INFO", "process.lock_file_present",
            "nina.lock file exists — normal if service is running",
        )

    pid_file = data_dir / "nina.pid"
    if pid_file.exists():
        pid_content = pid_file.read_text(errors="replace").strip()
        record("INFO", "process.pid_file", f"nina.pid contains: {pid_content}")

# ── §14 · Log directory writable ─────────────────────────────────────────────
def check_log_dir():
    logs_dir = NINA_DIR / "logs"
    if not logs_dir.exists():
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            record("PASS", "logs_dir.created", "logs/ directory created")
        except Exception as e:
            record(
                "WARN", "logs_dir.create_fail",
                f"Could not create logs/ directory: {e}",
                fix="Run: mkdir -p ~/nina/logs && chmod 755 ~/nina/logs",
            )
    elif os.access(logs_dir, os.W_OK):
        record("PASS", "logs_dir.writable", "logs/ directory writable")
    else:
        record(
            "WARN", "logs_dir.not_writable",
            f"logs/ directory is not writable: {logs_dir}",
            fix="Run: chmod 755 ~/nina/logs",
        )

# ── §15 · Python version check ───────────────────────────────────────────────
def check_python_version():
    major = sys.version_info.major
    minor = sys.version_info.minor
    version_str = f"{major}.{minor}.{sys.version_info.micro}"

    if major < 3 or (major == 3 and minor < 10):
        record(
            "BLOCKER", "python.version_too_old",
            f"Python {version_str} is too old — NINA requires Python 3.10+",
            detail=f"Current: {sys.version}",
            fix="Activate the correct venv: source ~/nina/venv/bin/activate",
        )
    elif major == 3 and minor >= 14:
        record(
            "PASS", "python.version",
            f"Python {version_str} — meets requirement (3.14 confirmed compatible)",
        )
    else:
        record(
            "PASS", "python.version",
            f"Python {version_str} — OK",
        )

# ── §16 · Ollama availability (advisory) ─────────────────────────────────────
def check_ollama():
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "3", "http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and "models" in result.stdout.lower():
            record("PASS", "ollama.responding", "Ollama local inference responding")
        else:
            record(
                "INFO", "ollama.not_responding",
                "Ollama not responding at localhost:11434 (non-blocking — cloud fallback available)",
                fix="Run: sudo systemctl start ollama",
            )
    except Exception as e:
        record(
            "INFO", "ollama.check_error",
            f"Ollama check failed: {e} (non-blocking)",
        )

# ── Run all checks ────────────────────────────────────────────────────────────
if METRICS_MODE:
    # Do not print standard outputs, jump straight to the server block later.
    pass
elif not JSON_MODE:
    print("\n  NINA Guardian 2.0 — Startup Safety Assertions")
    print("  " + "─" * 52)

if not METRICS_MODE:
    check_python_version()
    check_env_file()
    env_data = load_env()
    check_env_keys(env_data)
    check_packages()
    check_syntax()
    check_core_imports()
    check_router_regressions()
    check_shell_allowlist()
    check_ssrf_guard()
    check_cron_ids()
    check_idle_queue_path()
    check_duplicate_log_handler()
    check_pipeline_security()
    check_data_dir()
    check_log_dir()
    check_ollama()
# ── Final report ──────────────────────────────────────────────────────────────
total  = len(results)
passed = sum(1 for r in results if r["level"] == "PASS")

if METRICS_MODE:
    pass
elif JSON_MODE:
    output = {
        "healthcheck_version": "2.0",
        "timestamp": __import__("datetime").datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "python": sys.version,
        "blocker_count": blocker_count,
        "warn_count": warn_count,
        "pass_count": passed,
        "total_checks": total,
        "overall": "FAIL" if blocker_count > 0 else ("WARN" if warn_count > 0 else "PASS"),
        "results": results,
    }
    print(json.dumps(output, indent=2))
else:
    print("")
    print("  " + "─" * 52)
    print(f"  Checks run  : {total}")
    print(f"  PASS        : {passed}")
    print(f"  WARN        : {warn_count}")
    print(f"  BLOCKER     : {blocker_count}")
    print("  " + "─" * 52)

    if blocker_count == 0:
        print("  ✔  PASS — all BLOCKER checks clear")
    else:
        print(f"  ✖  FAIL — {blocker_count} BLOCKER(s) must be resolved before deploy")
        print("")
        print("  Fixes required:")
        for r in results:
            if r["level"] == "BLOCKER":
                print(f"    → [{r['check_id']}] {r['fix']}")

    print("")

# ── Metrics server ────────────────────────────────────────────────────────────
def get_prometheus_metrics():
    """Generates Prometheus-style plain-text metrics."""
    lines = []

    # 1. nina_service_active
    pid_file = NINA_DIR / "data" / "nina.pid"
    service_active = 0
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text(errors="replace").strip())
            if os.path.exists(f"/proc/{pid}"):
                service_active = 1
        except (ValueError, OSError):
            pass
    lines.append("# HELP nina_service_active NINA main service running status")
    lines.append("# TYPE nina_service_active gauge")
    lines.append(f"nina_service_active {service_active}")

    # 2. nina_provider_health
    prov_file = NINA_DIR / "data" / "discoveredproviders.json"
    if prov_file.exists():
        try:
            providers = json.loads(prov_file.read_text(errors="replace"))
            lines.append("# HELP nina_provider_health Health status of AI providers")
            lines.append("# TYPE nina_provider_health gauge")
            for p in providers:
                pid_str = p.get("id", "UNKNOWN")
                healthy = 1 if p.get("healthy") else 0
                lines.append(f'nina_provider_health{{provider="{pid_str}"}} {healthy}')
        except Exception:
            pass

    # 3. cron job status
    mgr_path = NINA_DIR / "crons" / "manager.py"
    if mgr_path.exists():
        try:
            source = mgr_path.read_text(errors="replace")
            ids_found = re.findall(r"id\s*=\s*['\"]([^'\"]+)['\"]", source)
            lines.append("# HELP nina_cron_job_status Count of defined cron jobs")
            lines.append("# TYPE nina_cron_job_status gauge")
            lines.append(f'nina_cron_job_status{{status="defined"}} {len(ids_found)}')
        except Exception:
            pass

    return "\n".join(lines) + "\n"

def run_metrics_server(port=8000):
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class MetricsHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/metrics':
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; version=0.0.4')
                self.end_headers()
                metrics = get_prometheus_metrics()
                self.wfile.write(metrics.encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not Found")

        def log_message(self, format, *args):
            # Suppress default HTTP logging to keep stdout clean
            pass

    server = HTTPServer(('0.0.0.0', port), MetricsHandler)
    print(f"Serving Prometheus metrics on port {port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

# ── Run Metrics Server ────────────────────────────────────────────────────────
if METRICS_MODE:
    run_metrics_server()
    sys.exit(0)

# ── Exit code ─────────────────────────────────────────────────────────────────
# Exit 0 = BLOCKER-free (warnings/advisory do not block)
# Exit 1 = at least one BLOCKER present
if not METRICS_MODE:
    sys.exit(0 if blocker_count == 0 else 1)
