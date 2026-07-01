# NINA agy Batch 02 — Memory + Context Quality
> Execute every ═══ block sequentially. One file at a time.
> After ALL specs: cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh
> Then run: bash ~/nina/docs/agyspec/run_batch.sh (to get next batch)

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-01 | fix(memory): cap build_context char_budget to prevent O(n²) growth
ID: MEM-CTX-01 | Type: perf | Risk: MEDIUM | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/memory.py fully before making any changes.

FIND the `build_context` method signature:
```python
async def build_context(self, query: str, n: int = ..., char_budget: int = ...) -> str:
```

FIND the loop inside `build_context` that accumulates document text.
It likely looks like:
```python
for doc in docs:
    context += doc  # or context = context + text
```
or uses a list join. The bug: if caller passes char_budget but the loop
does not enforce it per-iteration, the final string can exceed 3× the budget.

FIND the point where accumulated text is assembled. ENSURE this guard exists
IMMEDIATELY before or inside the accumulation loop:
```python
        # MEM-CTX-01: hard char_budget enforcement per-chunk
        _remaining = char_budget - len(accumulated)
        if _remaining <= 0:
            break
        chunk = text[:_remaining]
        accumulated += chunk
```
where `accumulated` and `text` are the actual variable names in the method.
If a guard already exists but uses `>` instead of `>=`, change it to `>= char_budget`.

ALSO FIND any place where `n` (number of docs) is used as the ChromaDB `n_results`
parameter. Ensure there is a cap:
```python
        n = min(n, 50)  # MEM-CTX-01: never query more than 50 docs regardless of caller
```
Insert this line at the START of `build_context` body, before any DB call.

DO NOT TOUCH: kb_add_entry, kb_search, save_reflection, episodic_search, .env

After editing: python3 -m py_compile core/memory.py
Commit: perf(memory): enforce char_budget per-chunk and cap n_results at 50 (MEM-CTX-01) | Batch 02

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-02 | fix(memory): deduplicate context chunks before assembling
ID: MEM-DEDUP-01 | Type: quality | Risk: LOW | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/memory.py fully before making any changes.

FIND `build_context`. Identify where retrieved document texts are collected
into a list before joining/concatenating.

BEFORE the join/concatenation, insert a dedup pass:
```python
        # MEM-DEDUP-01: deduplicate by 64-char fingerprint — prevents repeated
        # facts from flooding the context window when ChromaDB returns overlapping chunks
        _seen_fps = set()
        _deduped = []
        for _chunk in _chunks:  # substitute real list variable name
            _fp = _chunk[:64].strip()
            if _fp not in _seen_fps:
                _seen_fps.add(_fp)
                _deduped.append(_chunk)
        _chunks = _deduped  # substitute real list variable name
```
Substitute `_chunks` with the actual list variable name holding the text chunks.

DO NOT TOUCH: kb_add_entry, save_reflection, episodic_search, ChromaDB collection setup, .env

After editing: python3 -m py_compile core/memory.py
Commit: fix(memory): deduplicate context chunks by 64-char fingerprint (MEM-DEDUP-01) | Batch 02

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-03 | fix(memory): add fallback when ChromaDB collection is empty
ID: MEM-EMPTY-01 | Type: bug | Risk: LOW | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/memory.py fully before making any changes.

FIND `build_context`. Locate the ChromaDB `.query()` or `.get()` call.
If it is NOT wrapped in try/except, wrap it:
```python
        try:
            _results = self._collection.query(  # use real method + args
                query_texts=[query],
                n_results=n,
            )
        except Exception as _ce:
            logger.warning(f"memory_query_failed: {_ce}")
            return ""  # MEM-EMPTY-01: return empty string — never crash the agent loop
```

ALSO FIND the section that reads `_results["documents"]` or similar.
Add a None/empty guard:
```python
        _docs = (_results or {}).get("documents", [[]])
        if not _docs or not _docs[0]:
            return ""  # MEM-EMPTY-01: empty collection — agent will work without memory context
```

DO NOT TOUCH: kb_add_entry, save_reflection, episodic_search, .env

After editing: python3 -m py_compile core/memory.py
Commit: fix(memory): safe fallback when ChromaDB collection empty or query fails (MEM-EMPTY-01) | Batch 02

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-04 | fix(task_store): add file-lock timeout to prevent deadlock
ID: TASK-LOCK-01 | Type: bug | Risk: MEDIUM | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/task_store.py fully before making any changes.

FIND any `filelock`, `FileLock`, `fcntl.flock`, or `threading.Lock` usage.
Locate the `.acquire()` call or context manager `with lock:`.

IF using filelock library:
  FIND: `FileLock(path)` or `FileLock(path, timeout=...)`
  REPLACE with: `FileLock(path, timeout=5)`  # 5s max wait — TASK-LOCK-01

IF using fcntl:
  FIND the `fcntl.flock(fd, fcntl.LOCK_EX)` call
  REPLACE with a timeout wrapper:
  ```python
        import signal as _signal
        def _lock_timeout(signum, frame): raise TimeoutError("file lock timeout")
        _old = _signal.signal(_signal.SIGALRM, _lock_timeout)
        _signal.alarm(5)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
        except TimeoutError:
            logger.warning("task_store: file lock timeout after 5s — proceeding unlocked")
        finally:
            _signal.alarm(0)
            _signal.signal(_signal.SIGALRM, _old)
  ```

IF no locking exists at all:
  ADD at the top of the write method:
  ```python
        # TASK-LOCK-01: lightweight in-process lock for concurrent task writes
        import threading as _threading
        if not hasattr(self, '_write_lock'):
            self._write_lock = _threading.Lock()
        with self._write_lock:
  ```
  and indent the existing write body under this context manager.

DO NOT TOUCH: task schema, read methods, .env

After editing: python3 -m py_compile core/task_store.py
Commit: fix(task_store): add 5s file-lock timeout to prevent deadlock (TASK-LOCK-01) | Batch 02

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-05 | fix(crons): add missed-run recovery to APScheduler jobs
ID: CRON-MISS-01 | Type: reliability | Risk: LOW | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read crons/manager.py fully before making any changes.

FIND the APScheduler `AsyncIOScheduler` or `BackgroundScheduler` instantiation.
It will look like:
```python
scheduler = AsyncIOScheduler()
```
or
```python
scheduler = BackgroundScheduler()
```

REPLACE with:
```python
scheduler = AsyncIOScheduler(
    job_defaults={
        'coalesce': True,          # CRON-MISS-01: merge missed runs into one
        'max_instances': 1,        # prevent overlapping executions
        'misfire_grace_time': 300, # 5min grace — don't skip if late by <5min
    }
)
```
If it already has `job_defaults`, MERGE these three keys into the existing dict
without removing other keys.

DO NOT TOUCH: job definitions, reminder logic, daily_report, .env

After editing: python3 -m py_compile crons/manager.py
Commit: fix(crons): add coalesce+misfire_grace to APScheduler job_defaults (CRON-MISS-01) | Batch 02

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-06 | fix(browser): add SSRF allowlist guard — S-01
ID: S-01 | Type: security | Risk: HIGH | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read tools/browser.py fully before making any changes.

FIND the `run` or `fetch` method that accepts a URL string.
FIND the point where the URL is used in an HTTP request (requests.get, aiohttp, httpx).

IMMEDIATELY BEFORE the HTTP call, insert:
```python
        # S-01: SSRF allowlist — block internal/metadata URLs
        import ipaddress as _ip
        from urllib.parse import urlparse as _up
        _parsed = _up(str(url))
        _BLOCKED_HOSTS = {
            "169.254.169.254",  # AWS/GCP metadata
            "metadata.google.internal",
            "169.254.170.2",    # ECS metadata
        }
        _BLOCKED_SCHEMES = {"file", "ftp", "gopher", "data"}
        if _parsed.scheme in _BLOCKED_SCHEMES:
            return f"[BROWSER BLOCKED] scheme '{_parsed.scheme}' not permitted (S-01)"
        if _parsed.hostname in _BLOCKED_HOSTS:
            return "[BROWSER BLOCKED] metadata endpoint not permitted (S-01)"
        try:
            _addr = _ip.ip_address(_parsed.hostname or "")
            if _addr.is_private or _addr.is_loopback or _addr.is_link_local:
                return "[BROWSER BLOCKED] private/loopback IP not permitted (S-01)"
        except ValueError:
            pass  # not an IP address — hostname, allow through
```

DO NOT TOUCH: response parsing, timeout settings, .env

After editing: python3 -m py_compile tools/browser.py
Commit: fix(browser): add SSRF allowlist guard for private IPs and metadata (S-01) | Batch 02

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-07 | fix(config): add validation for required env vars at startup
ID: CFG-VALIDATE-01 | Type: reliability | Risk: LOW | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/config.py fully before making any changes.

FIND the `NinaConfig` class `__init__` or the module-level config loading block.
Locate where env vars are read (os.getenv / os.environ).

AFTER all env var assignments, ADD a validation block:
```python
        # CFG-VALIDATE-01: warn on missing critical env vars at startup
        _REQUIRED_VARS = [
            "TELEGRAM_BOT_TOKEN",
            "AUTHORIZED_USER_ID",
        ]
        _OPTIONAL_WARN = [
            "GROQ_API_KEY",
            "GEMINI_API_KEY",
        ]
        import logging as _logging
        _cfg_log = _logging.getLogger("nina.config")
        for _v in _REQUIRED_VARS:
            if not os.getenv(_v):
                _cfg_log.critical(f"MISSING REQUIRED ENV VAR: {_v} — nina will not start correctly")
        for _v in _OPTIONAL_WARN:
            if not os.getenv(_v):
                _cfg_log.warning(f"optional env var not set: {_v} — some providers unavailable")
```

DO NOT TOUCH: any existing config values, rate limits, provider lists, .env

After editing: python3 -m py_compile core/config.py
Commit: fix(config): validate required env vars at startup with log warnings (CFG-VALIDATE-01) | Batch 02

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-08 | feat(tools): create read_file tool to replace cat shell usage
ID: RFILE-01 | Type: feature | Risk: LOW | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read tools/ directory listing before making changes. Do NOT read shell.py.

FIND if tools/read_file.py already exists. If it does, skip this spec.

IF it does NOT exist, CREATE tools/read_file.py with this content:
```python
"""read_file tool — safe file reader for AgentLoop.
Replaces 'cat' which was removed from shell allowlist (O-06).
Allowlist: ~/nina/ tree only. Blocks .env and secrets."""
import logging
from pathlib import Path

logger = logging.getLogger("nina.tools.read_file")

_BLOCKED_NAMES = {".env", ".env.local", ".env.production", "secrets.json",
                  "credentials.json", ".netrc", "id_rsa", "id_ed25519"}
_ALLOWED_BASE = Path.home() / "nina"
_MAX_BYTES = 32_000

class ReadFileTool:
    name = "read_file"
    description = "Read a file from the nina project tree (max 32KB). Blocks .env and secret files."

    async def run(self, path_str: str) -> str:
        try:
            p = Path(path_str).expanduser().resolve()
            if p.name in _BLOCKED_NAMES:
                return f"[READ_FILE BLOCKED] '{p.name}' is a protected file."
            try:
                p.relative_to(_ALLOWED_BASE)
            except ValueError:
                return f"[READ_FILE BLOCKED] path outside ~/nina tree: {p}"
            if not p.exists():
                return f"[READ_FILE] File not found: {p}"
            if not p.is_file():
                return f"[READ_FILE] Not a file: {p}"
            content = p.read_text(encoding="utf-8", errors="replace")[:_MAX_BYTES]
            logger.info(f"read_file: {p} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.warning(f"read_file failed: {e}")
            return f"[READ_FILE ERROR] {e}"
```

THEN open core/nina.py or wherever tools are registered (look for a dict like
`tools = {"shell": ShellTool(), ...}`) and ADD:
```python
    from tools.read_file import ReadFileTool
    tools["read_file"] = ReadFileTool()
```
Insert this after the existing tool registrations.

DO NOT TOUCH: shell.py, core/agent.py tool dispatch, .env

After editing: python3 -m py_compile tools/read_file.py
Commit: feat(tools): add read_file tool to replace cat (RFILE-01) | Batch 02

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-09 | fix(guardian): ensure --mode flag accepted without crashing
ID: GUARD-MODE-01 | Type: bug | Risk: LOW | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read guardian_engine.py fully before making any changes.

FIND the argparse setup. Look for `ArgumentParser` and `.add_argument`.
Verify that `--mode` argument exists with choices `["hook", "report", "full"]`.

IF `--mode` is missing:
  ADD inside the argparse block:
  ```python
    parser.add_argument(
        "--mode",
        choices=["hook", "report", "full"],
        default="report",
        help="hook=fast pre-commit scan, report=full report, full=report+AST"
    )
  ```

FIND the main execution block that uses `args.mode`.
IF it uses `args.mode` without a default guard, add:
```python
    _mode = getattr(args, "mode", "report")  # GUARD-MODE-01: safe default
```
and replace subsequent `args.mode` references with `_mode`.

FIND any `sys.exit(1)` in the guardian that fires on non-critical findings
(warnings, style issues). Change those to `sys.exit(0)` — only true security
violations should fail the pre-commit hook.

DO NOT TOUCH: AST scan logic, baseline comparison, critical violation detection, .env

After editing: python3 -m py_compile guardian_engine.py
Commit: fix(guardian): ensure --mode flag accepted with safe default (GUARD-MODE-01) | Batch 02

═══════════════════════════════════════════════════════════════════════════════
SPEC-B02-10 | fix(nina_sync): add exit-code alarm on nina_sync.sh completion
ID: SYNC-EXIT-01 | Type: reliability | Risk: LOW | Batch 02
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read nina_sync.sh fully before making any changes.

FIND the very END of nina_sync.sh — the final echo block:
```bash
echo "  ✅ All sync steps completed successfully"
```

REPLACE the final exit status block (from `_sync_exit_code=$?` to end of file) with:
```bash
# SYNC-EXIT-01: explicit exit code + final status Telegram
if git diff --quiet HEAD 2>/dev/null; then
  echo "  = git tree clean after sync"
else
  echo "  ⚠  uncommitted changes remain after sync — check manually"
  _tg_notify "⚠️ NINA sync [$TS] — uncommitted changes remain after sync"
fi

echo ""
echo "================================================"
echo "  SYNC COMPLETE  $TS"
echo "================================================"
exit 0
```

DO NOT TOUCH: [1/8] through [8/8] blocks, compact_exporter.py call, rclone calls, .env

After editing: bash -n nina_sync.sh
Commit: fix(sync): explicit exit 0 and uncommitted-change warning at end (SYNC-EXIT-01) | Batch 02
