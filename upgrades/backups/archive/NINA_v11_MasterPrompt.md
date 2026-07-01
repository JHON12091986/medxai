# NINA v11 — MASTER PROMPT
### Version: 11.0.0 · Last updated: 2026-05-20 10:10 +0600
### Runtime specification, Stages 1–7.
### Design source of truth: Stage 0 Blueprint.

---

# STAGE 1: CORE

## 1.1 IDENTITY

**NINA** — Neural Intelligent Network Assistant.
Persistent local-first autonomous agent for M. Baizid Alam, Senior Banker, BASIC Bank, Dhaka.
Runs continuously on a consumer laptop. Telegram is the primary interface. Python 3.11+.

NINA is not a generic chatbot. It is a disciplined operating agent that can think, route, act, remember, monitor itself, and propose improvements — while keeping sensitive banking work on local models only.

---

## 1.2 DIRECTORY STRUCTURE

```
nina/
├── core/
│   ├── nina.py          # NinaOS — orchestration
│   ├── router.py        # HybridRouter V4
│   └── config.py        # NinaConfig pydantic model
├── agent/
│   ├── loop.py          # Autonomous agent loop
│   ├── idle_loop.py     # Idle improvement loop
│   ├── planner.py       # Goal decomposition
│   └── memory.py        # ChromaDB + facts.json
├── tools/
│   ├── shell.py
│   ├── web.py
│   ├── browser.py
│   ├── files.py
│   ├── system.py
│   ├── office_mail.py
│   ├── gpu_tuner.py
│   ├── provider_hunter.py
│   └── upgrade_pipeline.py
├── interfaces/
│   ├── telegram_interface.py
│   └── api.py
├── crons/
│   └── manager.py
├── data/
│   ├── workspace/
│   ├── model_discovery.json
│   ├── gpu_config.json
│   ├── capabilities.json
│   ├── discovered_providers.json
│   ├── idle_queue.json
│   ├── schedule_today.json
│   └── jobs.sqlite
├── memory/
│   ├── chromadb/
│   └── facts.json
├── upgrades/
│   └── backups/
├── logs/
├── tests/
├── main.py
├── .env
├── requirements.txt
├── start.sh
└── nina.service
```

---

## 1.3 NINACONFIG (`core/config.py`)

```python
class NinaConfig(BaseModel):
    # Required
    telegram_bot_token: str
    authorized_user_id: str

    # Local inference
    ollama_host: str = "http://localhost:11434"

    # Cloud providers — all optional
    cerebras_api_key:    str | None = None
    groq_api_key:        str | None = None
    gemini_api_key:      str | None = None
    mistral_api_key:     str | None = None
    openrouter_api_key:  str | None = None
    openai_api_key:      str | None = None
    deepseek_api_key:    str | None = None
    perplexity_api_key:  str | None = None
    together_api_key:    str | None = None
    cohere_api_key:      str | None = None
    fireworks_api_key:   str | None = None
    xai_api_key:         str | None = None
    sambanova_api_key:   str | None = None
    hyperbolic_api_key:  str | None = None
    novita_api_key:      str | None = None
    onebrain_api_key:    str | None = None
    onebrain_api_base:   str | None = None

    # FastAPI auth
    api_secret_key:      str | None = None   # generate: python -c "import secrets; print(secrets.token_hex(32))"

    # Exchange EWS
    ews_server:       str = "webmail.basicbanklimited.com"
    ews_domain:       str = "basic.bank"
    ews_username:     str = "alamba"
    ews_password:     str | None = None
    ews_auth_type:    str = "NTLM"
    ews_my_email:     str = "alamba@basicbanklimited.com"
    ews_shared_email: str = "basicid@basicbanklimited.com"
    ews_max_emails:   int = 10
    ews_keywords:     str = "SWIFT,LC,MT103,MT202,MT700,discrepancy,amendment,BG,overdue,urgent"

    # System
    log_level:          str = "INFO"
    workspace_dir:      Path = Path("./data/workspace")
    max_ram_gb:         float = 12.0
    ram_guard_gb:       float = 10.5
    disk_guard_pct:     float = 90.0        # NEW v11: disk preflight threshold
    idle_threshold_min: int = 15
    idle_report_min:    int = 30
    idle_auto_approve:  bool = False

    # Authorized-user flood protection
    flood_window_s:     int = 30            # NEW v11
    flood_max_messages: int = 10            # NEW v11

    # Heartbeat dead-man
    deadman_ping_url:          str | None = None
    deadman_max_interval_min:  int = 65
```

`load_config()` reads `.env`, builds NinaConfig, exits with a clear error if Telegram credentials are missing.

---

## 1.4 .ENV TEMPLATE

```
# Required
TELEGRAM_BOT_TOKEN=
AUTHORIZED_USER_ID=

# Local
OLLAMA_HOST=http://localhost:11434

# Cloud — add keys as you acquire them
CEREBRAS_API_KEY=
GROQ_API_KEY=
GEMINI_API_KEY=
MISTRAL_API_KEY=
OPENROUTER_API_KEY=
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
PERPLEXITY_API_KEY=
TOGETHER_API_KEY=
COHERE_API_KEY=
FIREWORKS_API_KEY=
XAI_API_KEY=
SAMBANOVA_API_KEY=
HYPERBOLIC_API_KEY=
NOVITA_API_KEY=
ONEBRAIN_API_KEY=
ONEBRAIN_API_BASE=

# FastAPI auth — generate: python -c "import secrets; print(secrets.token_hex(32))"
API_SECRET_KEY=

# EWS
EWS_SERVER=webmail.basicbanklimited.com
EWS_DOMAIN=basic.bank
EWS_USERNAME=alamba
EWS_PASSWORD=
EWS_AUTH_TYPE=NTLM
EWS_MY_EMAIL=alamba@basicbanklimited.com
EWS_SHARED_EMAIL=basicid@basicbanklimited.com
EWS_MAX_EMAILS=10
EWS_KEYWORDS=SWIFT,LC,MT103,MT202,MT700,discrepancy,amendment,BG,overdue,urgent

# System
LOG_LEVEL=INFO

# Heartbeat dead-man (optional — recommended: healthchecks.io free tier)
DEADMAN_PING_URL=
DEADMAN_MAX_INTERVAL_MIN=65
```

---

## 1.5 NINAOS CLASS (`core/nina.py`)

```python
class NinaOS:
    config:    NinaConfig
    router:    HybridRouter
    memory:    MemorySystem
    telegram:  TelegramInterface
    scheduler: TaskScheduler
    pipeline:  UpgradePipeline
    idle_loop: IdleUpgradeLoop
    system_prompt: str
```

---

## 1.6 STARTUP SEQUENCE

```
1.  load_config()
2.  fcntl single-instance lock at data/nina.lock
3.  configure logging (8 handlers)
4.  build system_prompt from Stage 0 source text (inject current_datetime_dhaka)
5.  MemorySystem.initialize()
6.  HybridRouter.initialize()
7.  TaskScheduler.start()
8.  UpgradePipeline.initialize()
9.  IdleUpgradeLoop.initialize() — loads idle_queue.json
10. TelegramInterface.start()
11. asyncio.create_task(router.run_idle_monitor())
12. FastAPI start in background thread (optional)
13. send startup Telegram message
```

---

## 1.7 STARTUP MESSAGE

```
● NINA v11 ONLINE — {datetime}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Local    : qwen2.5:1.5b · qwen2.5:7b
           GPU layers: {fast_layers}/{heavy_layers}
Keyless  : {keyless_providers}
Cloud    : {n_cloud_active} active · {n_missing} missing keys
Memory   : {n_conversations} conversations · {n_facts} facts
Scheduler: {n_jobs} jobs · next morning report {next_report_time}
Idle Loop: active · threshold {idle_threshold_min}min
Queue    : {idle_queue_count} proposals pending review
RAM      : {ram_used}GB / 16GB  |  VRAM: {vram_used}MB / 2048MB
Disk     : {disk_used_pct}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready.
```

All values filled at runtime. No hardcoded counts.

---

## 1.8 GRACEFUL SHUTDOWN

```
1. TelegramInterface.stop()
2. TaskScheduler.shutdown(wait=False)
3. HybridRouter.close()
4. MemorySystem.close()
5. release fcntl lock
6. log "NINA shutdown complete" to nina.log
```

Send shutdown Telegram message only if uptime > 1 hour.

---

# STAGE 2: ROUTER V4

## 2.1 PROVIDER REGISTRY

### Tier 1 — keyless (auto-active on startup)
| ID | Model | Base URL |
|----|-------|----------|
| LOCAL_FAST | qwen2.5:1.5b | http://localhost:11434 |
| LOCAL_HEAVY | qwen2.5:7b | http://localhost:11434 |
| POLLINATIONS | mistral | https://text.pollinations.ai/openai |
| CHUTES | deepseek-r1 | https://llm.chutes.ai/v1 |
| HF_PUBLIC | various | https://api-inference.huggingface.co |

### Tier 2 — free key (activated via /addkey)
| ID | Env Key | Model |
|----|---------|-------|
| CEREBRAS | CEREBRAS_API_KEY | llama-3.3-70b |
| GROQ | GROQ_API_KEY | llama-3.3-70b-versatile |
| MISTRAL | MISTRAL_API_KEY | mistral-large-latest |
| DEEPSEEK | DEEPSEEK_API_KEY | deepseek-chat |
| GEMINI | GEMINI_API_KEY | gemini-1.5-pro |
| TOGETHER | TOGETHER_API_KEY | llama-3.1-405b |
| COHERE | COHERE_API_KEY | command-r-plus |
| FIREWORKS | FIREWORKS_API_KEY | llama-v3p1-405b |
| XAI | XAI_API_KEY | grok-beta |
| PERPLEXITY | PERPLEXITY_API_KEY | sonar-pro |
| SAMBANOVA | SAMBANOVA_API_KEY | Meta-Llama-3.1-405B |
| HYPERBOLIC | HYPERBOLIC_API_KEY | llama-3.1-405b |
| NOVITA | NOVITA_API_KEY | llama-3.1-70b |
| ONEBRAIN | ONEBRAIN_API_KEY | default |

### Tier 3 — meta-provider
- OPENROUTER: on /addkey, scans /v1/models, registers all price==0 models as sub-providers.

---

## 2.2 TASK CLASSIFIER

Types: sensitive · coding · research · math · multilingual · document · vision · quick · general

Classifier outputs: task_type, estimated_tokens, is_parallel_candidate, is_sensitive.

Sensitive tasks route to local-only. No exceptions.

---

## 2.3 PROVIDERHEALTH

Per-provider fields:
```
success_count         int
failure_count         int
latencies             deque(maxlen=20)
requests_today        int
tokens_today          int
cooldown_until        float
degraded_until        float
last_used             float
last_request_ts       float    ← epoch of last dispatched request
reserved_requests     int      ← parallel reservation counter
reserved_tokens       int      ← parallel token reservation
```

Derived states:
```
is_available    → time.time() >= cooldown_until AND key exists
is_degraded     → time.time() < degraded_until
near_limit      → tokens_today >= 0.8 * RATE_LIMITS[id]["tpd"]
exhausted       → tokens_today >= RATE_LIMITS[id]["tpd"]
spacing_blocked → RATE_LIMITS[id]["min_spacing_s"] is set AND
                  (time.time() - last_request_ts) < RATE_LIMITS[id]["min_spacing_s"]
```

State transitions:
```
failure               → cooldown 5 min
3 failures in 1h      → cooldown 30 min
quality probe fail    → degraded 30 min + Telegram alert
exhausted             → blocked until midnight UTC + Telegram alert
spacing_blocked       → skipped silently — no failure recorded, no cooldown
```

---

## 2.4 ROUTING PRIORITY

```
1. Filter: is_available AND has_key AND not exhausted
           AND not spacing_blocked AND task compatible
2. Sensitive → LOCAL only. Never reaches cloud sort.
3. Sort composite score (normalized — v11):
   score = (success_rate × 0.4)
         + (1 - clamp(avg_latency_ms / 5000, 0.0, 1.0)) × 0.4
         + (not near_limit × 0.2)
4. Degraded providers appended at end
5. ONEBRAIN always last regardless of score
6. LOCAL_FAST / LOCAL_HEAVY: always available, used as fallback only when all cloud fails
```

---

## 2.5 SEQUENTIAL EXECUTION

```
providers = _ordered_providers(task)
for provider in providers:
    enforce min_spacing_s
    try:
        response = await _call(provider, messages, timeout=60s)
        record_success(provider, latency, tokens)
        update_cost_tracker(provider, tokens)
        return response
    except TimeoutError:
        record_failure(provider); continue
    except RateLimitError:
        mark_exhausted(provider); continue
    except Exception:
        record_failure(provider); continue
raise RuntimeError("All providers failed")
→ notify Telegram: "⚠️ All providers failed for this request"
```

---

## 2.6 PARALLEL EXECUTION

Conditions: is_parallel_candidate AND ≥2 healthy non-local providers AND RAM < ram_guard_gb.

```
Step 1 — Decompose
  LOCAL_FAST splits prompt into N independent sub-questions (N = min(3, available_providers))

Step 2 — Reserve
  Before asyncio.gather():
  For each chosen provider: increment reserved_requests, increment reserved_tokens estimate.

Step 3 — Fan-out
  asyncio.gather() with 45s per-provider timeout.

Step 4 — Reconcile
  Immediately after gather() completes:
  Update requests_today and tokens_today for all providers used.
  Clear reserved_requests and reserved_tokens.
  No second fan-out starts until this step completes.

Step 5 — Aggregate
  LOCAL_FAST synthesizes all returned parts.
  If 0 parts returned → fall through to sequential.
```

---

## 2.7 IDLE MONITOR

Runs every 300s. Max 3 concurrent tasks. Local models excluded.
Stops immediately under RAM pressure.

Task types: benchmark · warmup_ping · speculative_prefetch · cache_prefill · quality_probe

Quality probe failure → mark DEGRADED, send Telegram alert.

---

## 2.8 CACHE

Table: cache(prompt_hash, response, provider, task_type, timestamp, ttl_seconds)
Key: SHA-256 of normalized prompt.

TTLs:
```
sensitive    → NO CACHE (never)
quick        → 3600s
research     → 1800s
coding       → 21600s
document     → 14400s
general      → 7200s
math         → 21600s
multilingual → 7200s
```

Daily purge at 03:05 Dhaka.

---

## 2.9 COST TRACKING

Every successful request logged:
{provider, task_type, input_tokens, output_tokens, cost_usd, ttft_ms, total_ms, parallel, cached}

Daily cost report at 23:00 Dhaka.

---

## 2.10 get_status() FORMAT

`/router` shows per-provider readiness, latency, success rate, live usage vs daily limit, spacing state, and parallel mode availability.

---

# STAGE 3: TELEGRAM INTERFACE

## 3.1 SECURITY GATE

On every update:
1. if user_id ≠ authorized_user_id → ignore silently + security log
2. if empty → ignore
3. **flood check** (v11): if authorized user sent > flood_max_messages in flood_window_s:
   queue message, reply "⏳ Slow down — {n} message(s) queued."
   log to security.log with tag: authorized_user_flood
4. if .py document → route to upgrade pipeline
5. else → dispatch

---

## 3.2 COMMAND HANDLER

All 20 commands from Stage 0. Unknown command → "Unknown command. /help for the list."

---

## 3.3 NLP HANDLER

Intent classification via LOCAL_FAST. Intents:
```
email_fetch, provider_hunt, provider_status, config_update,
rollback_request, upgrade_history, cost_report, diagnose,
run_schedule, gpu_config, clear_session, show_idle_queue, general_task
```

On classification failure → fall through to general_task.

---

## 3.4 /help OUTPUT

```
NINA v11 — Commands

/task <goal>       Multi-step autonomous task
/ask <question>    Quick single-turn question
/email             Fetch + analyze both mailboxes
/shell <cmd>       Allowlisted system command
/remember <text>   Save to permanent memory
/forget <key>      Delete a saved fact
/patch <file/url>  Deploy a Python module upgrade
/generate <f> <d>  AI-generate a module upgrade
/approve           Confirm pending upgrade
/reject            Discard pending upgrade
/rollback <file>   Restore previous version
/addkey <P> <key>  Add a provider API key
/addkey list       Show provider status + signup links
/status            System health snapshot
/router            Provider routing table
/logs              Last 50 lines of nina.log
/abort             Kill active task immediately
/start             Reset session
/reset             Full reinitialization (backs up memory first)

You can also just talk:
  "check my email"
  "hunt for new providers"
  "show idle queue"
  "diagnose errors"
  "run the morning report now"
  "how much did I spend today"
  "set EWS emails to 25"
  "roll back web.py"
  "what's using the most RAM"
```

---

## 3.5 FILE UPLOAD HANDLER

.py files only → upgrade pipeline.
Non-.py → "NINA only accepts .py files for upgrades."
> 100KB → "File too large. Max 100KB."
Delete original upload message after routing (chat hygiene).

---

## 3.6 STREAMING

stream=True for all LLM responses.
Edit interval: 400ms or 200 chars (safe for Telegram ~20 edits/min).
Split at last newline if response > 4096 chars.

---

## 3.7 RESET UX

```
1. Warn: "⚠️ /reset will wipe all session memory. Creating backup first..."
2. memory_backup_path = MemorySystem.backup()
3. MemorySystem.wipe_and_reinitialize()
4. reply: "✅ Reset complete. Memory backed up to: {memory_backup_path}"
```

---

## 3.8 ERROR FORMAT

```
❌ [what failed]: [plain-English reason]
   [fallback attempt if any]
   [what user can do next if relevant]
```

---

## 3.9 SESSION MANAGEMENT

session_history in-memory only. Max 20 turns (prune from front).
/start clears session_history only. /reset clears everything.
ChromaDB and facts.json are preserved on /start.

---

# STAGE 4: TOOLS

## 4.1 REGISTRY

```python
TOOL_REGISTRY = {
    "shell":   ShellTool,   "search":  WebSearchTool,
    "browser": BrowserTool, "file":    FileTool,
    "system":  SystemTool,  "email":   OfficeMailTool,
    "gpu":     GPUTuner,
}
```

All tools: async run(input: str) -> str. All log to logs/tools.log.

---

## 4.2 SHELL TOOL

```
ALLOWED = {df, ls, pwd, whoami, free, ps, uptime, cat, top, du, date,
           systemctl status nina,
           journalctl -n 50 -u nina,    ← v11: unit-locked (was system-wide)
           nvidia-smi,                  ← v11: added for GPU diagnostics
           ollama ps,                   ← v11: added for model state
           ollama list}                 ← v11: added for installed models
cat: workspace only
Timeout: 10s | Output truncated to 2000 chars
```

---

## 4.3 WEB TOOL

duckduckgo_search — top 5 results. Exponential backoff on 202 errors.
User-agent rotation from pool of 5. Timeout: 15s search, 30s fetch.

---

## 4.4 BROWSER TOOL

Playwright headless: --disable-gpu --no-sandbox --disable-dev-shm-usage
Text extraction only. 5000 char limit. 30s timeout.
No screenshots. No internal network targets.

---

## 4.5 FILE TOOL

Workspace-scoped. Path traversal check on every operation.
Max read: 1MB. Max write: 5MB.

Disk preflight check before every write:
```python
if psutil.disk_usage("/").percent > config.disk_guard_pct:
    raise DiskGuardError(f"Disk {pct:.0f}% — write blocked")
```

---

## 4.6 SYSTEM TOOL

Reports: RAM, VRAM, CPU, disk, uptime, top 5 processes, NINA process footprint.

Alert thresholds:
```
RAM > 11GB        → "⚠️ NINA ALERT: RAM at {n}GB/16GB"
RAM > 12GB        → "🔴 RAM critical — reduce load"
VRAM < 150MB free → "⚠️ VRAM pressure — reduce GPU layers"
Disk > 90%        → "⚠️ Disk {n}% full"
CPU > 90% for 60s → "⚠️ CPU sustained high load"
```

Provides `get_ram_used_gb()` and `get_disk_used_pct()` for preflight guards.

---

## 4.7 EMAIL TOOL

Network TCP probe first → EWS fetch → urgency scan (keywords in subject + 500 chars body)
→ AI analysis (subject + sender + 500-char excerpt only — never full body to cloud).

Logs every access to logs/email_access.log as JSON-lines.

---

## 4.8 GPU TUNER

Determines stable GPU layer counts for qwen2.5:1.5b and qwen2.5:7b on MX150.
Writes to data/gpu_config.json. NLP-triggered: "optimize GPU layers".

---

# STAGE 5: AGENT + MEMORY + SCHEDULER

## 5.1 AGENT LOOP (`agent/loop.py`)

Pattern: THINK → PLAN → ACT → OBSERVE → ADAPT

Variable step budget by task type (v11):
```python
STEP_BUDGETS = {
    "quick":       3,
    "general":     5,
    "multilingual":5,
    "math":        6,
    "coding":      8,
    "document":    8,
    "research":   10,
    "sensitive":   5,
}
DEFAULT_MAX_STEPS = 5
max_steps = STEP_BUDGETS.get(task_type, DEFAULT_MAX_STEPS)
```

/abort stops immediately regardless of step count.

### RAM guard (runs first, every invocation)
```python
ram_used = await SystemTool.get_ram_used_gb()
if ram_used > config.ram_guard_gb:
    await notify_telegram(
        f"⚠️ RAM at {ram_used:.1f}GB — running in lean mode (agent loop skipped)."
    )
    logger.warning(f"Agent loop skipped: RAM {ram_used:.1f}GB > guard {config.ram_guard_gb}GB")
    return await router.single_turn(goal, session_history)
```

---

## 5.2 MEMORY SYSTEM (`agent/memory.py`)

ChromaDB at memory/chromadb/ — collection: nina_conversations
facts.json — explicit key-value store

Reserved schedule keys: today_schedule · meeting_today · deadline_today

### Reset backup procedure
```python
async def backup() -> Path:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = Path(f"upgrades/backups/memory_{ts}")
    backup_dir.mkdir(parents=True)
    shutil.copy("memory/facts.json", backup_dir / "facts.json")
    chromadb_export(backup_dir / "chromadb_export.json")
    update_memory_index(backup_dir)
    return backup_dir
```

Wipe only after backup() succeeds.

---

## 5.3 SCHEDULER (`crons/manager.py`)

8 core jobs:
```
morning_report    09:00 Dhaka daily
heartbeat         every 1h
cache_purge       03:05 Dhaka daily
cost_report       23:00 Dhaka daily
rate_limit_reset  00:01 UTC daily
idle_summary      every 30min (if idle queue has items)
log_rotation      04:00 Dhaka daily
provider_health   every 6h (re-probe cooled-down providers)
```

---

## 5.4 MORNING REPORT IMPLEMENTATION

Schedule Today resolution:
```python
schedule_lines = []

# 1. schedule_today.json
data = load_json("data/schedule_today.json")
today = date.today().isoformat()
if data and today in data:
    schedule_lines = data[today]

# 2. jobs.sqlite
if not schedule_lines:
    schedule_lines = get_today_scheduled_jobs_from_sqlite()

# 3. facts.json reserved keys
if not schedule_lines:
    for key in ["today_schedule", "meeting_today", "deadline_today"]:
        val = facts.get(key)
        if val:
            schedule_lines.append(val)

# 4. mandatory fallback
if not schedule_lines:
    schedule_lines = ["No scheduled items recorded."]
```

Market data fetch — failure handling:
```python
async def fetch_market_field(query: str, label: str) -> str:
    try:
        result = await web_search_cached(query, ttl=3600)
        return parse_rate(result)
    except Exception as e:
        logger.warning(f"morning_report_market_fetch_failed: {label} — {e}",
                       extra={"log": "error.log"})
        return "Unavailable (retry at next report)"
```

Report delivery is never blocked by a single field failure.

---

## 5.5 HEARTBEAT JOB

```python
async def heartbeat():
    logger.info("NINA operational", extra={"log": "scheduler.log"})
    if config.deadman_ping_url:
        try:
            async with httpx.AsyncClient() as client:
                await client.get(config.deadman_ping_url, timeout=10)
        except Exception as e:
            logger.warning(f"Dead-man ping failed: {e}")
```

---

# STAGE 6: UPGRADES + PROVIDERS

## 6.1 UPGRADE PIPELINE

Gated flow:
receive → **dangerous pattern scan** → static analysis → sandbox test → diff → present to user
→ await /approve or /reject → deploy → backup old version

The dangerous pattern scan runs first. Any match immediately rejects the upgrade.
Pattern blocklist is defined in Stage 0. Match produces:
`❌ Upgrade rejected: {reason}. Fix and resubmit.`
Rejection logged to logs/upgrade.log.

Protected files: never patched autonomously.
Writable scope: tools/, crons/, agent/, tests/

---

## 6.2 ROLLBACK

/rollback <filename> → restore latest timestamped backup from upgrades/backups/.

Memory backups (memory_YYYYMMDDHHMMSS/) are listed separately via NLP:
"restore memory backup" → list available snapshots → user picks → restore.

---

## 6.3 IDLE LOOP PERSISTENCE

When a proposal expires without approval:
```python
async def on_proposal_expire(proposal: Proposal):
    proposal.status = "expired_pending_review"
    proposal.expired_at = datetime.utcnow().isoformat()
    idle_queue.append(proposal)
    save_idle_queue()
    await notify_telegram(
        f"⏳ Upgrade for {proposal.filename} expired — saved to idle queue. "
        f"Say 'show idle queue' to review."
    )
```

---

## 6.4 PROVIDER HUNTER

Discovers new free providers, validates with test prompts, writes to data/discovered_providers.json.
New providers remain inactive until health check passes.

---

## 6.5 ADDKEY FLOW

```
/addkey GROQ sk-xxxx
→ validate format
→ store in .env
→ probe with lightweight request
→ if healthy: activate in router
   reply: "✅ GROQ activated — llama-3.3-70b-versatile ready"
→ if unhealthy: store key, mark inactive
   reply: "⚠️ GROQ key stored but probe failed: {reason}"
```

---

# STAGE 7: OPS

## 7.1 LOGGING (8 files)

```
logs/nina.log           Main runtime log
logs/router.log         Every request: provider, latency, tokens, cost (JSON-lines)
logs/agent.log          Agent reasoning — append only, never truncated
logs/tools.log          Tool calls: input preview, output preview, duration, outcome
logs/email_access.log   EWS fetches (JSON-lines)
logs/upgrade.log        Full upgrade and rollback history (includes pattern-scan rejections)
logs/error.log          Exceptions only (includes market fetch failures, disk guard events)
logs/security.log       Unauthorized access attempts + authorized-user flood events
```

Rotation: TimedRotatingFileHandler, 7-day retention per log file.

---

## 7.2 FASTAPI (optional, port 8000)

```
GET  /health           {status, uptime, version}
GET  /status           full NinaOS snapshot
GET  /router           router.get_status()
GET  /logs?n=50        last n lines of nina.log
GET  /memory/stats     conversation count, fact count
GET  /upgrades/queue   pending and idle queue items
```

Authentication: Bearer token from API_SECRET_KEY in .env.
Generate token once: `python -c "import secrets; print(secrets.token_hex(32))"`
Never auto-rotate. Never log token value.

---

## 7.3 SYSTEMD UNIT (`nina.service`)

```ini
[Unit]
Description=NINA Autonomous Agent
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/nina
ExecStart=/home/user/nina/start.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 7.4 FINAL DIRECTIVE

NINA must be honest, local-first, recoverable, and calm under resource pressure.
It must not silently lose memory, silently discard useful autonomous work, or display undefined data as if it were real.
It must not dispatch code to sandbox without running the dangerous pattern scan first.
It must not let routing scores be distorted by unbounded latency arithmetic.
It must not block the morning report because a single market data source failed.
When uncertain: say so. When under pressure: degrade gracefully. When something fails: report it and recover.
