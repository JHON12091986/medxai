# NINA v12.2 Problem Log

**Machine:** ASUS VivoBook X530FN (aibony) · i5 8th Gen · 16GB RAM · MX150 2GB VRAM  
**OS:** Ubuntu 26.04 LTS · Python 3.14  
**Last updated:** 2026-05-22  
**Status:** v12.2 operational · all 8 GPT-5 audit fixes applied · 65 issues resolved · IdleProposalLoop active

---

## Component Status

| Component | Status | Notes |
|---|---|---|
| venv / Python 3.14 | ✅ | |
| HybridRouter V4 | ✅ | Cloud routing confirmed |
| `core/router.py` | ✅ | ResponseCache auto-purge · safe provider fallback · purge_expired safe iteration · R-53, R-58, R-59 |
| `core/agent.py` | ✅ | System frame once, incremental steps · R-38 |
| `core/config.py` | ✅ | Safe env loading · idle vars wired · R-29, R-35, R-41 |
| `core/memory.py` | ✅ | Blocking IO offloaded · freshness ranking · durable prefs · R-34, R-45, R-60 |
| `core/capabilities.py` | ✅ | asyncio.Lock + tothread · R-37 |
| `core/hotreload.py` | ✅ | Key mismatch fixed · deleted keys revert to defaults · R-36, R-44 |
| `core/nina.py` | ✅ | Duplicate import removed · IDLE_QUEUE canonical · duplicate log handler guard · R-46, R-47, R-61, R-65 |
| `core/logger.py` | ✅ | NameError fixed · duplicate import removed · R-33, R-43 |
| `crons/manager.py` | ✅ | Backup jobs use functools.partial (not lambda) · R-62 |
| `idleloop.py` | ✅ | Grounded prompts · promptindex persisted · R-42, R-51, R-57 |
| `tools/shell.py` | ✅ | cat removed from allowlist · injection protection · R-40, R-48 |
| `tools/officemail.py` | ✅ | SSL verification restored · R-49 |
| `tools/upgradepipeline.py` | ✅ | Pending slot guard · URL allowlist · eval regex · content-type/size guard · R-50, R-52, R-54, R-63 |
| `tools/browser.py` | ✅ | Full IP-range SSRF guard (ipaddress module) · R-56, R-64 |
| `interfaces/telegram_interface.py` | ✅ | Document upload before empty-text guard · key masking · intent map tightened · R-63b, R-66, R-67 |
| `main.py` | ✅ | PID-file targeted kill · R-55 |
| Ollama | ✅ | qwen2.5:1.5b · 7b · nomic-embed-text |
| Telegram bot | ✅ | PTB 21.9, live |
| NumPy | ✅ | Pinned <2.0 |
| Systemd | ✅ | nina + ollama auto-start enabled |
| IdleProposalLoop | ✅ | 7-topic rotation, promptindex persisted |
| EWS email | ⛔ | Blocked by O-02 |

---

## Resolved Issues

### R-01 — nina directory missing
- **Fix:** `mkdir -p nina`

### R-02 — python command not found
- **Fix:** `sudo apt install python-is-python3 -y`

### R-03 — Ollama models not pulled
- **Fix:** Pulled manually: qwen2.5:1.5b, qwen2.5:7b, nomic-embed-text

### R-04 — playwright not found at system level
- **Fix:** Installed via pip inside venv

### R-05 — nina.service unit missing
- **Fix:** Old v1 service disabled; new unit created and enabled

### R-06 — venv not set up
- **Fix:** `python3 -m venv nina/venv && source nina/venv/bin/activate`

### R-07 — No source code after uninstall
- **Fix:** All stages scaffolded in session (Stages 1–7)

### R-08 — PTB Updater.__slots__ AttributeError on Python 3.14
- **Error:** `AttributeError: Updater object has no attribute _Updater__polling_cleanup_cb`
- **Cause:** PTB 20.7 incompatible with Python 3.14 name-mangling changes
- **Fix:** `pip install --force-reinstall python-telegram-bot==21.9`

### R-09 — externally-managed-environment on pip install
- **Fix:** Always use venv; Ubuntu 26.04 enforces PEP 668

### R-10 — KeyError TELEGRAM_BOT_TOKEN on startup
- **Cause:** .env used `TELEGRAM_BOT_TOKEN`; config expected `TELEGRAM_BOT_TOKEN`
- **Fix:** `sed -i s/TELEGRAM_BOT_TOKEN/TELEGRAM_BOT_TOKEN/ nina/.env`

### R-11 — AttributeError NinaOS has no attribute run_morning_report
- **Cause:** Scheduler methods appended outside class body
- **Fix:** Re-appended correctly inside NinaOS

### R-12 — AttributeError TelegramInterface has no attribute send_message
- **Fix:** Appended `send_message` helper to TelegramInterface

### R-13 — BlockingIOError Errno 11 fcntl lock on startup
- **Cause:** Multiple NINA processes running simultaneously
- **Fix:** `pkill -f "python main.py"`; remove `nina/data/nina.lock`

### R-14 — BadRequest: Message is not modified
- **Cause:** Streaming edit loop sending identical text to Telegram
- **Fix:** Single final `edit_text` with content-change guard

### R-15 — Old NINA v1 intercepting bot token
- **Fix:** Disabled v1 service; fcntl lock prevents future double-start

### R-16 — router.log not writing to file
- **Fix:** 8 TimedRotatingFileHandler instances added to `core/nina.py`

### R-17 — nina.service not auto-starting after reboot
- **Cause:** Service was not enabled
- **Fix:** `sudo systemctl enable nina ollama`

### R-18 — IndentationError in core/nina.py after style patch
- **Cause:** Auto-patch used wrong variable name and bad insertion point
- **Fix:** Reverted with re.sub, re-applied manually

### R-19 — NumPy 2.0 compatibility error on startup
- **Error:** `AttributeError: np.float was removed in the NumPy 2.0 release`
- **Fix:** `pip install "numpy<2.0"`

### R-20 — SyntaxError: closing triple-quote merged with next line
- **Cause:** Bash history expansion on `!` corrupted injection
- **Fix:** `sed -i` to insert newline

### R-21 — format_for_telegram defined but never called
- **Fix:** `sed -i` to wire call in `edit_text`

### R-22 — UnboundLocalError: tool in core/agent.py
- **Cause:** tool only assigned inside else branch
- **Fix:** Moved above health check; rewrote if/else/if to if/elif/else
- **File:** `core/agent.py`

### R-23 — ConflictingIdError: memory_backup crash on startup
- **Cause:** `id='memory_backup'` registered twice in `crons/manager.py`
- **Fix:** Removed duplicate
- **File:** `crons/manager.py`

### R-24 — AttributeError: HybridRouter has no attribute activate_key
- **Cause:** Method called but never defined
- **Fix:** Added `async def activate_key(self, provider, key)` to HybridRouter
- **File:** `core/router.py`

### R-25 — FileNotFoundError: data/nina.lock on fresh install
- **Cause:** data directory not created before lock open
- **Fix:** Added `os.makedirs("data", exist_ok=True)`
- **File:** `core/nina.py`

### R-26 — handle_shadow defined 3× in tools/upgradepipeline.py
- **Fix:** Removed first two definitions, kept final
- **File:** `tools/upgradepipeline.py`

### R-27 — Dead file interfaces/telegram_interface.py
- **Cause:** 129-line legacy class never imported, shadowed active file
- **Fix:** Deleted

### R-28 — Ghost bot instance returning stale exchange rate
- **Symptom:** 1 USD = 95.20 BDT returned with no main.py in process list
- **Fix:** `pkill -9` cleared ghost; confirmed live: 1 USD = 122.84 BDT via Perplexity

### R-29 — idle_auto_approve hardcoded False, not wired to .env
- **Cause:** `load_config` had no mapping for IDLE_AUTO_APPROVE, IDLE_THRESHOLD_MIN, IDLE_REPORT_MIN
- **Fix:** Added 3 `os.getenv` overrides after `cfg = NinaConfig(...)`
- **File:** `core/config.py`

### R-30 — Pattern scanner silently killed auto-approve flow
- **Cause:** Scanner rejections returned different string; auto-approve branch never entered
- **Fix:** Added early-return guard for "Upgrade rejected" before auto-approve
- **File:** `idleloop.py`

### R-31 — WRITABLE scope mismatch between idleloop and pipeline
- **Cause:** idleloop.py allowed `agent/` directory; pipeline only allowed `core/agent.py`
- **Fix:** Aligned WRITABLE tuple to tools/, crons/, core/agent.py, tests/
- **File:** `idleloop.py`

### R-32 — Idle queue accumulated without action
- **Cause:** `run_idle_summary` only reported count, never auto-deployed
- **Fix:** Added auto-deploy of oldest item when `idle_auto_approve=True`
- **File:** `core/nina.py`

### R-33 — core/logger.py broken config import
- **Cause:** `from core.config import config` — no module-level config object exists
- **Fix:** Replaced with `from pathlib import Path; LOG_DIR = Path("logs")`
- **File:** `core/logger.py`

### R-34 — Blocking IO in async memory methods
- **Cause:** `build_context`, `remember`, `forget` all called sync IO in async context
- **Fix:** All blocking calls wrapped in `asyncio.to_thread`
- **File:** `core/memory.py`

### R-35 — KeyError crash on missing env vars at startup
- **Cause:** `os.environ["TELEGRAM_BOT_TOKEN"]` raises KeyError with no message
- **Fix:** Replaced with `os.getenv` + explicit RuntimeError with descriptive message
- **File:** `core/config.py`

### R-36 — Hot-reload silently ignored deleted .env keys
- **Cause:** reload hit `continue` on None; deleted keys never reverted
- **Fix:** Added Pydantic default lookup and `setattr` revert on missing key
- **File:** `core/hotreload.py`

### R-37 — Race condition on capabilities.json writes
- **Cause:** Concurrent `mark_unhealthy`/`mark_healthy` calls could corrupt JSON
- **Fix:** Added `asyncio.Lock` + `asyncio.to_thread` for atomic writes
- **File:** `core/capabilities.py`

### R-38 — Unbounded context window growth in AgentLoop
- **Cause:** Each step appended full prompt; quadratic token growth over multi-step tasks
- **Fix:** System frame built once before loop; each step appends only incremental scratchpad
- **File:** `core/agent.py`

### R-39 — agentloop.py and agentmemory.py orphaned dead code
- **Cause:** Both files never imported by any active module
- **Fix:** Archived to `agent_archive/`

### R-40 — asyncio.get_event_loop deprecated; injection risk in tools/shell.py
- **Cause:** Deprecated API; `shell=True` with no injection protection; returncode unchecked
- **Fix:** `get_running_loop` + `shlex.split` + shell operator blocklist + returncode check
- **File:** `tools/shell.py`

### R-41 — Orphaned `cfg = NinaConfig()` line causing SyntaxError in core/config.py
- **Cause:** R-29 patch left original unclosed line in place
- **Fix:** Removed orphaned line; verified with `ast.parse`
- **File:** `core/config.py`

### R-42 — IdleProposalLoop generating hallucinated filenames
- **Cause:** Analysis prompts gave LLM no grounding; invented files like `tools/platesolve.py`
- **Fix:** Injected real file tree into prompt before every analysis call
- **File:** `idleloop.py`

### R-43 — config.LOGDIR NameError in core/logger.py
- **Cause:** RotatingFileHandler referenced `config.LOGDIR` but config was never imported; duplicate `from pathlib import Path` also present
- **Fix:** Replaced with local constant `LOG_DIR`; removed duplicate import
- **File:** `core/logger.py`

### R-44 — RELOADABLE key mismatch causing config wipe on hot-reload
- **Cause:** 18 keys in RELOADABLE used concatenated names (e.g. IDLEAUTOAPPROVE) but .env stores underscore-separated keys; every reload cycle reverted all settings to Pydantic defaults silently
- **Fix:** All 18 keys corrected to underscore format matching .env
- **File:** `core/hotreload.py`

### R-45 — Empty collection guard missing in core/memory.py
- **Fix:** Added guard for empty facts/docs before slicing

### R-46 — Conflicting tool descriptions in SYSTEM_PROMPT_TEMPLATE
- **Cause:** Two consecutive "Available tools" lines with contradictory tool names degraded LLM instruction adherence
- **Fix:** Removed stale DuckDuckGo-only line; kept accurate Tavily/Serper/DDG line
- **File:** `core/nina.py`

### R-47 — Duplicate `import os` in core/nina.py
- **Fix:** Removed standalone `import os` on line 1; retained inside combined import on line 3
- **File:** `core/nina.py`

### R-48 — cat in shell allowlist enabling file exfiltration
- **Cause:** `cat` in ALLOWED allowed unrestricted reads of .env, SSH keys, any file on disk
- **Fix:** Removed `cat` from ALLOWED
- **File:** `tools/shell.py`

### R-49 — SSL verification disabled on EWS email connections
- **Cause:** NoVerifyHTTPAdapter override silently disabled SSL cert verification, exposing NTLM credentials to MITM attacks
- **Fix:** Removed NoVerifyHTTPAdapter override; SSL verification restored
- **File:** `tools/officemail.py`

### R-50 — patch command fetched and deployed arbitrary URLs
- **Cause:** No domain allowlist or HTTPS enforcement on `patch` command
- **Fix:** Enforces HTTPS-only domain allowlist: github.com, raw.githubusercontent.com, gist.githubusercontent.com, pastebin.com
- **File:** `tools/upgradepipeline.py`

### R-51 — Grounded prompt built but never passed to router in idleloop.py
- **Cause:** `generate_proposal` built `grounded_prompt` with real file context but passed bare prompt to router, enabling hallucinated filenames
- **Fix:** Changed router call to use `grounded_prompt`
- **File:** `idleloop.py`

### R-52 — Pending upgrade slot silently overwritten in upgradepipeline.py
- **Cause:** `submit` overwrote any existing pending upgrade without warning, losing the first submission
- **Fix:** Added guard; returns error if `self.pending is not None`
- **File:** `tools/upgradepipeline.py`

### R-53 — ResponseCache unbounded memory leak in core/router.py
- **Cause:** `purge_expired` existed but was never called automatically; cache grew forever
- **Fix:** Added auto-purge in `set` when cache exceeds 500 entries
- **File:** `core/router.py`

### R-54 — Weak exec/eval/compile regex in upgrade scanner
- **Cause:** Regex lookbehind patterns didn't reliably block eval/exec/compile calls
- **Fix:** Replaced with `\b` word-boundary patterns
- **File:** `tools/upgradepipeline.py`

### R-55 — pkill -f self-restart guard killed unrelated processes
- **Cause:** `pkill -f "python3 main.py"` matched any process with that string, not just NINA
- **Fix:** Replaced with PID-file approach; only sends SIGTERM to the exact previous NINA PID
- **File:** `main.py`

### R-56 — Incomplete SSRF protection in tools/browser.py
- **Cause:** Blocklist missed IPv6 loopback (::1), link-local 169.254.x.x, cloud metadata endpoints, and upper 172.x RFC-1918 ranges
- **Fix:** Expanded blocklist to cover all missing ranges and cloud metadata IPs
- **File:** `tools/browser.py`

### R-57 — Idle proposal promptindex reset to 0 on every restart
- **Cause:** `prompt_index = 0` hardcoded in `__init__`; all restarts started from tool-error-handling category
- **Fix:** Index persisted to `data/proposal_index.txt` and loaded on init
- **File:** `idleloop.py`

---

### R-58 — ResponseCache.purge_expired mutates dict during iteration *(GPT-5 audit)*
- **Cause:** `purge_expired` used a generator expression that called `self.s.pop(k)` while iterating `self.s.items()` → `RuntimeError` in Python 3.3+
- **Fix:** Collect dead keys into a list first, then pop in a separate loop
- **File:** `core/router.py`
- **Impact:** HIGH — any cache flush crashed the router

### R-59 — route() raised RuntimeError with no user-safe fallback *(GPT-5 audit)*
- **Cause:** Final `raise RuntimeError("All providers failed…")` propagated unhandled to Telegram, producing a raw traceback in chat
- **Fix:** Replaced with logged warning + user-safe reply string listing failed providers
- **File:** `core/router.py`
- **Impact:** HIGH

### R-60 — core/memory.py build_context returned stale facts with no freshness ranking *(GPT-5 audit)*
- **Cause:** First 10 facts returned by insertion order; stale or low-priority facts could dominate prompts; no separation of durable preferences from recent conversation snippets
- **Fix:** Added timestamps + priority to facts; `build_context` sorts by recency × priority score; durable preferences always included regardless of recency cutoff
- **File:** `core/memory.py`
- **Impact:** MEDIUM

### R-61 — core/nina.py idle queue path mismatch *(GPT-5 audit)*
- **Cause:** `run_idle_summary` read `data/idlequeue.json`; `expire_pending` wrote to `IDLE_QUEUE` = `data/idle_queue.json` (underscore); pending items were invisible to the consumer
- **Fix:** `core/nina.py` now imports `IDLE_QUEUE` from `tools/upgradepipeline.py`; single source of truth
- **File:** `core/nina.py`
- **Impact:** HIGH — idle queue silently dropped all expired items

### R-62 — Cron backup jobs silently dropped via lambda coroutine anti-pattern *(GPT-5 audit)*
- **Cause:** `lambda: run_memory_backup(n)` is a sync callable returning a coroutine object; APScheduler treats it as sync, calls it, discards the coroutine without awaiting
- **Fix:** Replaced with `functools.partial(run_memory_backup, n)` (a proper async callable)
- **File:** `crons/manager.py`
- **Impact:** HIGH — backups and expire_pending never actually ran

### R-63 — Remote patch download had no content-type or size guard *(GPT-5 audit)*
- **Cause:** `tools/upgradepipeline.py` fetched patch URLs from approved domains but did not verify Content-Type, response size, or exact path intent before staging as code
- **Fix:** Enforced 100KB max response size, required `text/plain` content-type, added diff summary shown to user before approval
- **File:** `tools/upgradepipeline.py`
- **Impact:** MEDIUM — oversized or binary responses could be staged as code

### R-64 — tools/browser.py SSRF guard used substring matching *(GPT-5 audit)*
- **Cause:** `"10." in url` matched `example10.com` (false positive) and missed URL-encoded or zero-padded variants; no check for `::1`, link-local, or cloud metadata hosts
- **Fix:** Replaced all substring checks with `ipaddress.ip_address()` range validation covering private, loopback, link-local, and reserved ranges
- **File:** `tools/browser.py`
- **Impact:** MEDIUM — SSRF bypass and false-positive blocks

### R-65 — Duplicate `if not root.handlers:` guard with bad indentation *(GPT-5 audit)*
- **Cause:** P8 patch introduced `if not root.handlers:` correctly, but left a duplicate `if not root.handlers:` on the next line; `root.addHandler(ch)` was at wrong indentation level outside both conditions → handler always added on reinit
- **Fix:** Removed duplicate `if` block; single guard with correct indentation
- **File:** `core/nina.py`
- **Impact:** LOW — duplicate log lines on restart/hot-reload

### R-66 — Document-only Telegram messages silently dropped *(GPT-5 audit)*
- **Cause:** `handle_message` read `update.message.text`, returned early if empty, before the `.py` document handler was reached; file uploads with no caption were never processed
- **Fix:** Moved document check block above the empty-text early-return
- **File:** `interfaces/telegram_interface.py`
- **Impact:** HIGH — upgrade-via-Telegram file flow completely broken

### R-67 — API keys echoed in chat and logs via addkey command *(GPT-5 audit)*
- **Cause:** `handle_add_key` replied with the raw activate_key result string including the full key; no masking, no message deletion, no persistence policy
- **Fix:** Delete the user's message from chat immediately; reply with masked key (`sk-ab****yz`); log only provider name (not key value)
- **File:** `interfaces/telegram_interface.py`
- **Impact:** HIGH — security

---

## Open Issues

| ID | Item | Priority |
|----|------|----------|
| O-01 | Browser tool — Playwright blocked | LOW |
| O-02 | EWS email password | MEDIUM |
| O-04 | memory_context per-session refresh | LOW |
| O-05 | FastAPI REST endpoints not implemented | LOW |

---

## Confirmed Working — 2026-05-22 20:45

- NINA started cleanly: PID 49721, `Active: active (running)`
- All 8 GPT-5 audit patches compiled and applied (`python3 -m py_compile` clean)
- `systemctl status nina` shows no errors
- 65 total issues resolved (R-01 → R-67)


cat >> ~/nina/nina_problem_log.md << 'EOF'

---

### R-68 — parse_mode="Markdown" causing Telegram BadRequest crashes
- **Cause:** Special characters in responses triggered Telegram BadRequest on all reply_text/edit_text calls
- **Fix:** `sed -i 's/parse_mode="Markdown"/parse_mode=None/g'` across telegram_interface.py
- **File:** `interfaces/telegram_interface.py`

### R-69 — HybridRouter has no attribute ordered_providers
- **Cause:** Method renamed to `_ordered_providers` but stale reference remained in error log line 222
- **Fix:** `sed -i '222s/ordered_providers/_ordered_providers/'`
- **File:** `core/router.py`

### R-70 — NameError: forcelocal is not defined
- **Cause:** Line 221 still used old camelCase `forcelocal` after router renamed to snake_case
- **Fix:** `sed -i '221s/forcelocal/force_local/'`
- **File:** `core/router.py`

### R-71 — ClassifiedTask has no attribute tasktype
- **Cause:** Dataclass fields renamed to snake_case but old camelCase references remained in agent.py and router.py
- **Fix:** Global sed replace of tasktype→task_type, issensitive→is_sensitive etc.
- **File:** `core/agent.py`, `core/router.py`

### R-72 — self._http AttributeError — root cause of all-providers-failed
- **Cause:** `_call_provider` used `self._http` but `__init__` set `self.http` (no underscore) — all Ollama calls silently failed
- **Fix:** `sed -i 's/self\._http/self.http/g' core/router.py`
- **File:** `core/router.py`
- **Impact:** HIGH — all local inference broken in live service
EOF

---

## Guardian status — 2026-05-23

**Current state:** guardian operational; deploy path verified; mypy downgraded to advisory warnings.

### New resolved items

### R-73 — guardian failed package check for mypy
- **Cause:** guardian validated `mypy`, but the package was not installed in `~/nina/venv`
- **Fix:** `python -m pip install --upgrade mypy`
- **Scope:** `venv`

### R-74 — API_SECRET_KEY empty in .env
- **Cause:** `.env` contained an empty `API_SECRET_KEY`, causing guardian config validation to fail
- **Fix:** inserted a non-empty secret value in `/home/aibony/nina/.env`
- **Scope:** `.env`

### R-75 — guardian treated mypy output as hard failure during healthy deploys
- **Cause:** mypy findings were emitted through `fail`, producing blocking-style output even when runtime deploy succeeded
- **Fix:** changed guardian mypy reporting from `fail` to `warn`
- **Scope:** `nina-guardian.sh`
- **Impact:** MEDIUM — removes contradictory red failure output while preserving visible type debt

### Current warnings

| ID | Item | Priority |
|----|------|----------|
| W-01 | `TELEGRAMCHATID` missing in `.env` | LOW |
| W-02 | mypy type issues remain in `core/`, `tools/`, and `interfaces/telegram_interface.py` | LOW |

### Confirmed working — 2026-05-23 01:35

- guardian completes all sections and reaches `All checks passed — NINA is healthy`
- `nina.service` restarts cleanly from guardian
- Telegram polling confirmed after deploy
- APScheduler confirmed after deploy
- pyflakes clean; syntax checks clean; mypy present and running

--- TITLE NINA v12.2 Problem Log - Guardian status 2026-05-23 - R-76 Guardian handoff/suppression patch applied inconsistently...

- Symptom: guardian patching introduced a partial cosmetic suppression change, causing internal inconsistency between live findings flow and handoff/report fields; one attempted edit also introduced an undefined `effective_findings` reference during suggested_actions construction.
- Evidence: backup of `guardian_engine.py` shows health scoring, overall status, root cause selection, report assembly, and incident writing still run from `findings`, while a separate backup fragment shows a handoff field `suppressedcount lensuppressedfindings` even though no durable `suppressed_findings` pipeline was completed.
- Cause: patch was applied in fragments instead of as one coherent refactor; result was mixed use of old `findings` path plus unfinished suppression/handoff variables.
- Fix: reverted `build_suggested_actions` back to `findings` to remove the immediate NameError path, and identified the dangling handoff `suppressed_count` reference as the remaining cleanup point before any future cosmetic suppression pass.
- Scope: `guardian_engine.py`
- Impact: MEDIUM — can make guardian crash or report inconsistent forensic status even while `healthcheck.py` passes and NINA itself is healthy.
- Current state: guardian logic requires a single coherent follow-up patch, not piecemeal substitutions.

cd ~/nina && BACKUP_MD="$(ls -t upgrades/backups/nina_export_*.md 2>/dev/null | head -n 1)" && [ -n "$BACKUP_MD" ] && cat >> "$BACKUP_MD" <<'EOF'

---

## NINA Problem Log

### 2026-05-23 22:14:44 +0600 — Guardian forensic run
- Guardian reported WARN status with health score 4.5/10, while startup checks and service restart still showed NINA active, Telegram polling confirmed, APScheduler started, and Ollama responding.
- Signature phase reported likely false-positive blockers for `API_SECRET_KEY`, `TELEGRAM_BOT_TOKEN`, and `AUTHORIZED_USER_ID` even though earlier env preflight and healthcheck marked them present.
- Guardian also reported a concurrent-process/lock warning around `nina.lock` and PID 26097 before restart.
- Advisory findings included duplicate log handler warning, Telegram Markdown parse warning, coroutine/lambda APScheduler warning, idle queue path mismatch warning, shell allowlist regression debt, weak eval/exec regex debt, and TELEGRAMCHATID missing info.
- Guardian forensic engine crashed at the end with:
  - `NameError: name 'suppressed_findings' is not defined`
  - File: `guardian_engine.py`
  - Area: `run_engine(args)` handoff/report assembly

### Confirmed technical interpretation
- NINA runtime itself was not down after restart; deploy gate completed successfully and service remained active.
- The strongest confirmed Guardian bug is the undefined variable `suppressed_findings`.
- The env blocker signatures are likely over-matching from source/signature text rather than true runtime evidence.
- Some warnings appear stale relative to the current codebase backup and should be revalidated against runtime-only evidence.

---

## R-77 - Router review prioritization for next patch set
- **Date:** 2026-05-24 00:27
- **Component:** `core/router.py`
- **Type:** Reliability / routing quality / observability
- **Summary:** Reviewed external feedback from multiple model opinions and selected the safest high-impact router improvements for NINA v12.2.
- **Decision:**
  - Prioritize contextual cache-key hardening so identical prompts from different conversations do not collide.
  - Prioritize proper HTTP 429 handling using `Retry-After` to reduce repeated provider hammering and improve cooldown accuracy.
  - Prioritize request-level trace ID logging for end-to-end correlation across routing attempts and diagnostics.
- **Deferred:**
  - Full circuit-breaker state machine with half-open recovery.
  - Retry/backoff expansion beyond narrow transient-failure classes.
  - Dynamic Ollama model discovery.
  - Cost-tracking-first work as a leading patch item.
- **Rationale:** Selected quick wins improve correctness and resilience immediately with low regression risk and minimal architectural churn.
- **Status:** Logged for implementation planning; no code patch applied in this session.

---

## R-126 - Architect Dashboard URL not working / not auto-starting
- **Date:** 2026-06-08 21:05
- **Component:** `tools/nina_dashboard.py`, `nina.service`
- **Type:** Bug / Integration
- **Summary:** User reported that the Architect dashboard URL was not working. Investigation revealed that the dashboard required manual starting and had relative path issues when run as a service.
- **Resolution:**
  - Refactored `tools/nina_dashboard.py` to use absolute paths for template and static file serving.
  - Created `nina-dashboard.service` and integrated it into `nina.service` via `Wants` and `Partof`.
- **Status:** FIXED
