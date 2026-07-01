# NINA v12.1 — Perplexity Implementation Prompts
### Paste one prompt per session. Upload both spec files to your NINA Dev Space first.

---

## BEFORE YOU START

1. Create a Perplexity Space: "NINA Dev"
2. Upload `nina_v12_blueprint.md` and `nina_v12_master_prompt.md` to the Space
3. Use **Comet Agent** (not regular chat) for every prompt below — it writes files
4. Work in order: Stage 1 → 2 → 3 → 4 → 5 → 6 → 7
5. After each stage: test before moving on

---

## PROMPT 0 — Project Scaffold

```
You are implementing NINA v12, a local-first autonomous AI agent.
The full spec is in the uploaded blueprint and master prompt files.

Task: Create the complete project scaffold. No implementation logic yet — 
just the directory structure, empty files, and the requirements.txt.

Create this exact structure under /home/user/nina/:

nina/
├── core/           nina.py  router.py  config.py
├── agent/          loop.py  idle_loop.py  planner.py  memory.py
├── tools/          shell.py  web.py  browser.py  files.py
│                   system.py  office_mail.py  gpu_tuner.py
│                   provider_hunter.py  upgrade_pipeline.py
├── interfaces/     telegram_interface.py  api.py
├── crons/          manager.py
├── data/           workspace/  (create empty JSON stubs:
│                   model_discovery.json  gpu_config.json
│                   capabilities.json  discovered_providers.json
│                   idle_queue.json  schedule_today.json)
├── memory/         chromadb/  facts.json (empty {})
├── upgrades/       backups/
├── logs/           (create 8 empty log files:
│                   nina.log  router.log  agent.log  tools.log
│                   email_access.log  upgrade.log  error.log  security.log)
├── tests/
├── main.py
├── .env            (use the exact .env template from Stage 1.4 of the master prompt)
├── requirements.txt
├── start.sh
└── nina.service    (use the exact systemd unit from Stage 7.3)

requirements.txt must include:
python-telegram-bot>=20.0, httpx, pydantic>=2.0, psutil, chromadb,
python-dotenv, duckduckgo-search, playwright, exchangelib,
apscheduler, fastapi, uvicorn, ollama, aiofiles, pathlib

After creating all files, run:
  find /home/user/nina -type f | sort
to confirm the structure, and show me the output.
```

---

## PROMPT 1 — Stage 1: Core (Config + NinaOS)

```
You are implementing NINA v12. The full spec is in the uploaded files.
Implement Stage 1 exactly. Create or overwrite these files:

FILE: core/config.py
- Implement NinaConfig as the pydantic BaseModel defined in Stage 1.3
- Include every field exactly as specified including all v12 additions:
  api_rate_limit_rpm, session_max_turns, agent_timeout_s
- Include all 6 v12.1 thermal threshold fields:
  thermal_warn_cpu=80, thermal_warn_gpu=80,
  thermal_guard_cpu=90, thermal_guard_gpu=85,
  thermal_critical_cpu=95, thermal_critical_gpu=90
- Implement load_config(): reads .env via python-dotenv, builds NinaConfig,
  exits with a clear error message if TELEGRAM_BOT_TOKEN or
  AUTHORIZED_USER_ID is missing

FILE: core/nina.py
- Implement NinaOS class with the 8 attributes from Stage 1.5
- Implement startup_sequence() following the 13 steps in Stage 1.6 exactly
- Implement shutdown() following the 6 steps in Stage 1.8
- Build system_prompt by reading the source text from Stage 0 of the blueprint
  and injecting current_datetime_dhaka as ISO 8601 UTC+6
- Send the startup message (Stage 1.7) via Telegram after step 13
  All fields in the startup message must be real runtime values
  Include the thermal line: "Thermal: CPU {n}°C {status}  GPU {n}°C {status}"
  (call SystemTool.get_temps() during startup; show N/A if sensor unavailable)
- Send shutdown message only if uptime > 1 hour

FILE: main.py
- Create NinaOS, call startup_sequence(), run asyncio event loop,
  handle SIGTERM/SIGINT for graceful shutdown

After writing the files, run:
  cd /home/user/nina && python -c "from core.config import load_config; print(load_config())"
and show me the output (it will error on missing .env values — that is expected).
```

---

## PROMPT 2 — Stage 2: HybridRouter V4

```
You are implementing NINA v12. The full spec is in the uploaded files.
Implement Stage 2 exactly. Create or overwrite: core/router.py

Requirements:
- Implement the full provider registry from Stage 2.1:
  Tier 1 (5 keyless), Tier 2 (15 keyed including OPENAI), 
  Tier 3 OPENROUTER with sub-provider scanning
- Implement ProviderHealth dataclass with all fields from Stage 2.3
  including last_request_ts, reserved_requests, reserved_tokens
- Implement all 5 derived state properties: is_available, is_degraded,
  near_limit, exhausted, spacing_blocked
- Implement all 5 state transitions from Stage 2.3
- Implement RATE_LIMITS dict from Stage 0 of blueprint — all 18 entries
  including OPENROUTER
- Implement routing score formula exactly:
  score = (success_rate × 0.4)
        + (1 - clamp(avg_latency_ms / 5000, 0.0, 1.0)) × 0.4
        + (not near_limit × 0.2)
- Implement routing priority from Stage 2.4 (filter → sensitive check →
  score sort → degraded append → ONEBRAIN last)
- Implement sequential execution (Stage 2.5) with TimeoutError,
  RateLimitError, and generic Exception handling
- Implement parallel execution (Stage 2.6) all 5 steps including
  reservation before gather and reconciliation after
- Implement idle monitor (Stage 2.7): runs every 300s, max 3 tasks,
  stops under RAM pressure, 5 task types
- Implement cache (Stage 2.8): SQLite table, SHA-256 key, per-type TTLs,
  sensitive tasks never cached, cleared on reset
- Implement cost tracking (Stage 2.9): persist to data/jobs.sqlite
- Implement get_status() for /router command (Stage 2.10)
- All router.log entries must follow the JSON schema from Stage 0:
  ts, provider, task_type, input_tokens, output_tokens, cost_usd,
  ttft_ms, total_ms, parallel, cached, status, error

After writing, run:
  cd /home/user/nina && python -c "from core.router import HybridRouter; print('Router OK')"
```

---

## PROMPT 3 — Stage 3: Telegram Interface

```
You are implementing NINA v12. The full spec is in the uploaded files.
Implement Stage 3 exactly. Create or overwrite: interfaces/telegram_interface.py

Requirements:
- Implement security gate (Stage 3.1) in exact order:
  1. unknown user_id → ignore + log to security.log
  2. empty message → ignore
  3. flood check: > flood_max_messages in flood_window_s → queue +
     reply "⏳ Slow down — {n} message(s) queued."
     log to security.log tag: authorized_user_flood
  4. .py document → upgrade pipeline
  5. else → dispatch
- Implement all 20 commands from Stage 0 command set (Stage 3.2)
  Unknown command → "Unknown command. /help for the list."
- Implement NLP handler (Stage 3.3) with all 13 intents via LOCAL_FAST
  On classification failure: fall through to general_task AND log warning
  to nina.log with tag nlp_classification_failed and first 80 chars of input
- Implement /help output exactly as shown in Stage 3.4
- Implement file upload handler (Stage 3.5):
  .py only, max 100KB, delete original after routing
- Implement streaming (Stage 3.6):
  stream=True, edit interval 400ms or 200 chars, split at 4096 chars
- Implement reset UX (Stage 3.7) including cache clear step (v12)
- Implement error format (Stage 3.8)
- Implement session management (Stage 3.9):
  max session_max_turns turns (from config), prune from front
  /start clears session_history only
  /reset clears everything including cache

After writing, run:
  cd /home/user/nina && python -c "from interfaces.telegram_interface import TelegramInterface; print('Telegram OK')"
```

---

## PROMPT 4 — Stage 4: Tools

```
You are implementing NINA v12. The full spec is in the uploaded files.
Implement Stage 4 exactly. Create or overwrite these files in tools/:

tools/shell.py
- Allowlist exactly as in Stage 4.2 including v11 additions:
  journalctl -n 50 -u nina (unit-locked), nvidia-smi, ollama ps, ollama list
- cat restricted to workspace only
- 10s timeout, output truncated to 2000 chars
- Log every call to tools.log

tools/web.py
- duckduckgo_search, top 5 results
- Exponential backoff on 202 errors
- User-agent rotation from pool of 5
- 15s search timeout, 30s fetch timeout

tools/browser.py
- Playwright headless with flags: --disable-gpu --no-sandbox
  --disable-dev-shm-usage  (all three required — Stage 0 cross-cutting rule #9)
- Text extraction only, 5000 char limit, 30s timeout
- No screenshots, no internal network targets

tools/files.py
- Workspace-scoped with path traversal check on every operation
- Max read 1MB, max write 5MB
- Disk preflight guard before every write:
  if psutil.disk_usage("/").percent > config.disk_guard_pct: raise DiskGuardError

tools/system.py
- Reports: RAM, VRAM, CPU, disk, uptime, top 5 processes, NINA footprint, thermal state
- Alert thresholds exactly as in Stage 4.6 including v12.1 thermal alerts:
  CPU temp >= thermal_warn_cpu → "🌡️ CPU temp warning: {n}°C"
  GPU temp >= thermal_warn_gpu → "🌡️ GPU temp warning: {n}°C"
- Implement get_temps() exactly as in Stage 4.6:
  CPU via psutil.sensors_temperatures() (try coretemp, k10temp, cpu_thermal in order)
  GPU via subprocess nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader
  timeout=5s. On any exception: set that sensor to None — never raise.
  Return {"cpu": float|None, "gpu": float|None}
- Implement get_status() thermal section:
  {"cpu_c": n, "gpu_c": n, "cpu_status": "OK"|"WARN", "gpu_status": "OK"|"WARN"}
  WARN if temp >= thermal_warn_* threshold; None sensors show as "N/A"
- Exposes get_ram_used_gb(), get_disk_used_pct(), and get_temps() for preflight guards

tools/office_mail.py
- Network TCP probe first, then EWS fetch via exchangelib + NTLM
- Urgency scan: keywords in subject + first 500 chars of body
- AI analysis uses subject + sender + 500-char excerpt only
  Never send full email body to any cloud provider
- Log every access to email_access.log as JSON-lines

tools/gpu_tuner.py
- Determine stable GPU layer counts for qwen2.5:1.5b and qwen2.5:7b
- Write results to data/gpu_config.json

All tools must implement: async run(input: str) -> str
All tools must log to logs/tools.log

After writing, run:
  cd /home/user/nina && python -c "
from tools.shell import ShellTool
from tools.system import SystemTool
from tools.files import FileTool
print('Tools OK')
"
```

---

## PROMPT 5 — Stage 5: Agent + Memory + Scheduler

```
You are implementing NINA v12. The full spec is in the uploaded files.
Implement Stage 5 exactly.

FILE: agent/loop.py
- Pattern: THINK → PLAN → ACT → OBSERVE → ADAPT
- Implement STEP_BUDGETS dict and DEFAULT_MAX_STEPS from Stage 5.1
- Run preflight guards in this exact order before the step loop:
  1. RAM guard (Stage 5.1) — if RAM > ram_guard_gb: downgrade to single-turn
  2. Thermal guard (Stage 5.1, v12.1) — three tiers:
     a. CRITICAL (cpu >= thermal_critical_cpu OR gpu >= thermal_critical_gpu):
        notify Telegram, log to agent.log tag agent_loop_aborted_thermal, return abort message
     b. GUARD (cpu >= thermal_guard_cpu OR gpu >= thermal_guard_gpu):
        notify Telegram, set force_local_fast=True (ban LOCAL_HEAVY this invocation)
     c. WARN (cpu >= thermal_warn_cpu OR gpu >= thermal_warn_gpu):
        log warning to nina.log only
     If sensor returns None: skip that tier silently — no false aborts
- Global timeout guard using asyncio.wait_for with config.agent_timeout_s
  On timeout: log to agent.log tag agent_loop_timeout, return partial result
  with notice "⚠️ Task timed out after {n}s."
- /abort stops immediately regardless of step count

FILE: agent/memory.py
- ChromaDB at memory/chromadb/, collection: nina_conversations
- facts.json for explicit key-value store
- Reserved keys: today_schedule, meeting_today, deadline_today
- Implement backup() exactly as in Stage 5.2 — wipe only after backup() succeeds
- Implement build_context() for system prompt injection

FILE: crons/manager.py
- Implement all 10 scheduler jobs from Stage 5.3 (APScheduler):
  morning_report     09:00 Dhaka daily
  heartbeat          every 1h
  cache_purge        03:05 Dhaka daily
  cost_report        23:00 Dhaka daily
  rate_limit_reset   00:01 UTC daily
  idle_summary       every 30min (only if idle queue has items)
  log_rotation       04:00 Dhaka daily
  provider_health    every 6h
  provider_hunter    02:00 Dhaka daily  ← v12
  thermal_health     every 5min         ← v12.1

- Implement morning report (Stage 5.4):
  Schedule Today resolution: 4-step fallback (blank output forbidden)
  fetch_market_field(): on failure return "Unavailable (retry at next report)"
    log to error.log tag morning_report_market_fetch_failed
  fetch_mailbox_summary(): on EWS failure return
    "Unavailable (EWS unreachable — retry at next report)"
    log to error.log tag morning_report_ews_fetch_failed
  Report delivery never blocked by any single field failure

- Implement heartbeat (Stage 5.5) with dead-man ping to deadman_ping_url

- Implement thermal_health_check (Stage 5.6):
  Call SystemTool.get_temps() every 5 minutes
  If cpu temp >= thermal_warn_cpu: log warning to nina.log AND notify Telegram
  If gpu temp >= thermal_warn_gpu: log warning to nina.log AND notify Telegram
  None sensors: skip silently — no LLM call involved

After writing, run:
  cd /home/user/nina && python -c "
from agent.memory import MemorySystem
from agent.loop import run_agent_loop
from crons.manager import TaskScheduler
print('Agent + Memory + Scheduler OK')
"
```

---

## PROMPT 6 — Stage 6: Upgrades + Providers

```
You are implementing NINA v12. The full spec is in the uploaded files.
Implement Stage 6 exactly.

FILE: tools/upgrade_pipeline.py
- Implement gated flow: receive → pattern scan → static analysis →
  sandbox test → diff → present → await /approve or /reject →
  deploy → backup old version
- Implement DANGEROUS_PATTERNS list from Stage 0 (all 14 patterns)
  Pattern scan runs FIRST — any match rejects immediately
  Rejection message: "❌ Upgrade rejected: {reason}. Fix and resubmit."
  Log rejection to upgrade.log
- Protected files: never patched (core/nina.py, core/router.py,
  core/config.py, interfaces/telegram_interface.py, .env, nina.service)
- Writable scope: tools/, crons/, agent/, tests/ only
- Implement rollback (Stage 6.2): restore latest timestamped backup
  Memory backup restore via NLP "restore memory backup" → list → pick

- Implement idle loop persistence (Stage 6.3):
  on_proposal_expire(): set status expired_pending_review,
  save to data/idle_queue.json, notify Telegram

- Implement ABShadowTester (Stage 6.7):
  shadow_n=20 requests alongside production
  After shadow_n: present match rate summary, await /approve or /reject
  On /reject: discard candidate, restore production
  Opt-in only

FILE: tools/provider_hunter.py
- Discover new free providers, validate with test prompts
- Write to data/discovered_providers.json
- New providers inactive until health check passes

- Implement /addkey flow (Stage 6.5):
  validate format → store in .env → probe → activate or store-inactive

FILE: core/config.py — add ConfigHotReload (Stage 6.6):
- Watch .env every 60s via mtime check
- Reloadable fields: ews_max_emails, ews_keywords, idle_threshold_min,
  idle_report_min, idle_auto_approve, flood_window_s, flood_max_messages,
  session_max_turns, agent_timeout_s, api_rate_limit_rpm,
  deadman_ping_url, log_level,
  thermal_warn_cpu, thermal_warn_gpu, thermal_guard_cpu,
  thermal_guard_gpu, thermal_critical_cpu, thermal_critical_gpu   ← v12.1
- On reload success: log to nina.log tag config_hot_reload, list changed fields
- On validation failure: keep old config, log error, notify Telegram

- Implement CapabilityRegistry (Stage 6.8):
  JSON at data/capabilities.json: loaded, healthy, last_checked, error per tool
  Updated on startup and after every tool health probe
  Agent loop skips unhealthy tools and logs warning — never crashes

After writing, run:
  cd /home/user/nina && python -c "
from tools.upgrade_pipeline import UpgradePipeline, ABShadowTester
from tools.provider_hunter import ProviderHunter
print('Upgrades + Providers OK')
"
```

---

## PROMPT 7 — Stage 7: Ops + Integration Test

```
You are implementing NINA v12. The full spec is in the uploaded files.
Implement Stage 7 and run a full integration test.

FILE: interfaces/api.py
- FastAPI app on port 8000 (optional, started in background thread)
- Implement all 6 endpoints from Stage 7.2:
  GET /health  GET /status  GET /router  GET /logs?n=50
  GET /memory/stats  GET /upgrades/queue
- Authentication: Bearer token from API_SECRET_KEY in .env
- Rate limiting: api_rate_limit_rpm requests/min per source IP
  On breach: HTTP 429 with Retry-After header
  Log to security.log tag: api_rate_limit_breach

FILE: configure logging (in core/nina.py startup):
- 8 TimedRotatingFileHandler instances, 7-day retention:
  nina.log  router.log  agent.log  tools.log
  email_access.log  upgrade.log  error.log  security.log
- router.log entries must follow the JSON schema from Stage 0:
  {ts, provider, task_type, input_tokens, output_tokens, cost_usd,
   ttft_ms, total_ms, parallel, cached, status, error}

Then run this integration checklist. For each item report PASS or FAIL:

1. python -c "from core.config import load_config" → should exit cleanly
2. python -c "from core.router import HybridRouter" → no import errors
3. python -c "from agent.memory import MemorySystem" → no import errors
4. python -c "from crons.manager import TaskScheduler" → no import errors
5. python -c "from tools.upgrade_pipeline import UpgradePipeline" → no import errors
6. python -c "from interfaces.api import app" → no import errors
7. python -c "
   from tools.upgrade_pipeline import DANGEROUS_PATTERNS
   import re
   test = 'os.system(\"rm -rf /\")'
   hits = [r for r,_ in DANGEROUS_PATTERNS if re.search(r, test)]
   assert len(hits) > 0, 'Pattern scan failed'
   print('Pattern scan: PASS')
   "
8. python -c "
   import asyncio
   from tools.system import SystemTool
   temps = asyncio.run(SystemTool.get_temps())
   assert isinstance(temps, dict) and 'cpu' in temps and 'gpu' in temps
   print(f'Thermal sensors: CPU={temps[\"cpu\"]} GPU={temps[\"gpu\"]} — PASS')
   "
9. python -c "
   from core.config import NinaConfig
   cfg = NinaConfig(telegram_bot_token='x', authorized_user_id='y')
   assert cfg.thermal_warn_cpu == 80
   assert cfg.thermal_critical_gpu == 90
   print('Thermal config defaults: PASS')
   "
10. Confirm all 8 log files exist in logs/
11. Confirm data/ JSON stubs are valid JSON
12. Confirm nina.service and start.sh exist

Report the full checklist result. List any FAILs with the error message.
If all pass, print: "NINA v12.1 ready for .env configuration and live test."
```

---

## AFTER ALL STAGES PASS

```
NINA v12.1 is scaffolded and tested. Final steps before going live:

1. Fill in .env:
   - TELEGRAM_BOT_TOKEN (from @BotFather)
   - AUTHORIZED_USER_ID (your Telegram user ID)
   - EWS_PASSWORD
   - Any cloud API keys you have (GROQ, CEREBRAS, GEMINI are free)
   - Generate API_SECRET_KEY:
     python -c "import secrets; print(secrets.token_hex(32))"

2. Pull Ollama models:
   ollama pull qwen2.5:1.5b
   ollama pull qwen2.5:7b
   ollama pull nomic-embed-text

3. Install Playwright browser:
   playwright install chromium

4. Test startup:
   cd /home/user/nina && python main.py

5. If startup message arrives in Telegram — NINA v12 is live.

6. Install as systemd service:
   sudo cp nina.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable nina
   sudo systemctl start nina
```
