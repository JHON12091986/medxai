# NINA v12 — Architecture Blueprint

**Version:** 12.2
**Updated:** 2026-06-05
**Machine:** ASUS VivoBook X530FN · i5 8th Gen · 16GB RAM · MX150 2GB VRAM
**OS:** Ubuntu 26.04 LTS · Python 3.14
**Status:** Operational · R-01→R-67 resolved · 4 open issues (O-01, O-02, O-04, O-05)

---

## Overview

NINA is a self-hosted, always-on personal AI assistant running as a systemd service on a local laptop in Dhaka, Bangladesh. It exposes a Telegram bot as the sole user interface. All routing, scheduling, memory, and upgrade logic is embedded in a single Python process (`main.py`) started via `NinaOS.start()`.

```
User (Telegram) ──► TelegramInterface ──► NinaOS ──► AgentLoop ──► HybridRouter ──► Providers
                                              │
                          ┌───────────────────┼────────────────────┐
                          ▼                   ▼                    ▼
                    MemorySystem        TaskScheduler        UpgradePipeline
                    (ChromaDB +         (APScheduler)        (patch, test,
                     facts.json)                              deploy)
```

---

## Repository Structure

```
nina/
├── main.py                          # Entry point — starts NinaOS
├── idleloop.py                      # IdleProposalLoop — background self-improvement
├── guardian_engine.py               # Guardian health engine (1778 lines)
├── healthcheck.py                   # Health check utilities (666 lines)
├── nina_export.sh                   # Backup/export helper script
│
├── core/
│   ├── nina.py                      # NinaOS orchestrator — wires all components
│   ├── router.py                    # HybridRouter V4 — provider routing + fallback
│   ├── agent.py                     # AgentLoop — THINK→PLAN→ACT→OBSERVE→ADAPT
│   ├── config.py                    # NinaConfig (Pydantic) + RATELIMITS + load_config()
│   ├── memory.py                    # MemorySystem — ChromaDB + facts.json
│   ├── capabilities.py              # CapabilityRegistry — tool health tracking
│   ├── hotreload.py                 # ConfigHotReload — .env watcher (60s interval)
│   └── logger.py                    # DEPRECATED — logging now in core/nina.py
│
├── interfaces/
│   ├── telegram_interface.py        # TelegramInterface — PTB 21.9 bot handler
│   └── api.py                       # FastAPI REST — NOT IMPLEMENTED (O-05)
│
├── tools/
│   ├── __init__.py                  # Tool exports
│   ├── shell.py                     # Shell exec — allowlist + injection guard
│   ├── browser.py                   # URL fetch — SSRF-protected (ipaddress module)
│   ├── search.py                    # Web search — Tavily + Serper + DDG
│   ├── searchtool.py                # Thin wrapper around search.py
│   ├── system.py                    # System status — RAM, temp, disk
│   ├── officemail.py                # EWS email (BLOCKED — O-02)
│   ├── files.py                     # File read/write helpers
│   ├── web.py                       # HTTP fetch helpers
│   ├── gputuner.py                  # GPU tuning helpers
│   ├── providerhunter.py            # Hunts free provider keys
│   └── upgradepipeline.py           # Patch submit → test → deploy pipeline
│
├── crons/
│   ├── manager.py                   # TaskScheduler — APScheduler 10-job schedule
│   └── backup_jobs.py               # Memory + .py zip backup jobs
│
├── agent/
│   ├── context.py                   # EMPTY — placeholder
│   └── __init__.py
│
├── data/
│   ├── nina.lock                    # Single-instance fcntl lock
│   ├── capabilities.json            # Tool health state
│   ├── proposal_index.txt           # Idle loop topic rotation index
│   ├── memory/
│   │   ├── facts.json               # Durable key-value facts
│   │   └── chromadb/                # Persistent vector store
│   └── workspace/                   # Agent working directory
│
├── logs/
│   ├── nina.log                     # Main log (TimedRotating, 7-day)
│   ├── router.log                   # Per-request JSON routing log
│   ├── agent.log                    # AgentLoop step log
│   ├── tools.log                    # Tool execution log
│   ├── upgrade.log                  # Pipeline log
│   ├── error.log                    # ERROR+ only
│   ├── security.log                 # Key activation, auth events
│   └── emailaccess.log              # EWS access log
│
└── upgrades/
    └── backups/                     # Timestamped .zip + memory snapshots
```

---

## Core Components

### `core/nina.py` — NinaOS Orchestrator

Top-level class that starts and wires all subsystems. Single-instance via `fcntl` lock on `data/nina.lock`.

**Startup sequence:**
1. Acquire `fcntl` lock
2. Set up `TimedRotatingFileHandler` for 8 log streams
3. `memory.initialize()` — load ChromaDB + facts.json
4. `router.initialize()` — discover Ollama models + start idle monitor
5. `pipeline.initialize()` — init upgrade pipeline
6. `AgentLoop`, `TelegramInterface`, `TaskScheduler` wired
7. `IdleUpgradeLoop.initialize()`
8. `ConfigHotReload.initialize()` — start .env watcher
9. Send startup message to Telegram

**Key NinaOS methods (cron targets):**

| Method | Cron | Purpose |
|--------|------|---------|
| `run_morning_report` | 09:00 Dhaka | USD/BDT rate + EWS emails + system status + daily cost |
| `run_heartbeat` | Every 1h | Log heartbeat + dead-man ping |
| `run_cost_report` | 23:00 Dhaka | Daily cost summary |
| `run_idle_summary` | (idle loop) | Report idle queue count; auto-deploy if IDLE_AUTO_APPROVE=true |
| `run_provider_hunter` | (scheduled) | Hunt free provider keys |
| `run_thermal_health` | (scheduled) | Warn if CPU/GPU temp exceeds threshold |

---

### `core/router.py` — HybridRouter V4

Handles all LLM calls. Implements provider tiering, circuit breakers, rate limiting, response caching, and cost tracking.

**Provider tiers:**

| Tier | Providers | Key required |
|------|-----------|-------------|
| Tier 1 (free) | POLLINATIONS, CHUTES, HFPUBLIC | No |
| Tier 2 (paid) | CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI, ONEBRAIN | Yes |
| Tier 3 (fallback) | OPENROUTER | Yes |
| Local | LOCALFAST (qwen2.5:1.5b), LOCALHEAVY (qwen2.5:7b) | Ollama |

**Routing logic (`_ordered_providers`):**
- Sensitive tasks / force_local=True → local only
- All others: available providers sorted by composite score (success_rate×0.4 + latency×0.4 + headroom×0.2), degraded last, local as final fallback
- ONEBRAIN always last among cloud providers

**CircuitBreaker states:** CLOSED → OPEN (3 failures in 120s) → HALF_OPEN → CLOSED

**Task types and step budgets:**

| Task type | Max steps | Cache TTL |
|-----------|-----------|-----------|
| quick | 3 | 1h |
| general | 5 | 2h |
| multilingual | 5 | 2h |
| math | 6 | 6h |
| coding | 8 | 6h |
| document | 8 | 4h |
| research | 10 | 30m |
| sensitive | 5 | 0 (no cache) |

---

### `core/agent.py` — AgentLoop

Implements THINK → PLAN → ACT → OBSERVE → ADAPT loop.

**Preflight checks (in order):**
1. RAM guard — if RAM >= ram_guard_gb (10.5GB), skip loop → single_turn
2. Thermal critical — abort if CPU >= 95C or GPU >= 90C
3. Thermal guard — force_local=True if CPU >= 90C or GPU >= 85C

**Loop mechanics:**
- System frame built once before loop (goal + memory context + tool instructions)
- Each step appends only last 3 scratchpad lines (prevents quadratic growth — R-38)
- Tool calls: TOOL:web INPUT:query | TOOL:browser INPUT:url | TOOL:shell INPUT:cmd | TOOL:system INPUT:status
- Loop exits on FINAL: prefix in response
- Self-check applied for: coding, research, sensitive, analysis, document, math

**Global timeout:** agent_timeout_s (default 300s), wrapped in asyncio.wait_for.

---

### `core/memory.py` — MemorySystem

Two-layer memory:

| Layer | Storage | Contents |
|-------|---------|----------|
| Vector | ChromaDB (data/memory/chromadb/) | Conversation turns, semantic search via nomic-embed-text |
| Facts | data/memory/facts.json | Key-value pairs with timestamps |

**`build_context(query)`** returns top-5 semantically relevant turns + durable prefs + 7 most recent facts sorted by recency.

**Pref keys** (always included): name, language, timezone, bank, email, role, style.

---

### `core/config.py` — NinaConfig

Pydantic model loaded from .env. Key thresholds:

| Field | Default | Notes |
|-------|---------|-------|
| ram_guard_gb | 10.5 | AgentLoop skip threshold |
| thermal_warn_cpu/gpu | 80C | Log warn only |
| thermal_guard_cpu/gpu | 90C / 85C | Force local routing |
| thermal_critical_cpu/gpu | 95C / 90C | Abort agent loop |
| agent_timeout_s | 300 | Global loop timeout |
| session_max_turns | 20 | Telegram history |
| flood_window_s | 30 | Anti-flood window |
| flood_max_messages | 10 | Max in window |
| idle_auto_approve | False | Auto-deploy idle proposals |

**Hot-reloadable** (ConfigHotReload watches every 60s): ews_max_emails, ews_keywords, idle_threshold_min, idle_report_min, idle_auto_approve, flood_window_s, flood_max_messages, session_max_turns, agent_timeout_s, api_rate_limit_rpm, dead_man_ping_url, log_level, all 6 thermal thresholds.

---

### `interfaces/telegram_interface.py` — TelegramInterface

PTB 21.9. Single authorised user. Key handlers:

| Input | Action |
|-------|--------|
| /start | Welcome + capabilities |
| status | System + router status |
| approve | Deploy pending upgrade |
| reject | Reject pending upgrade |
| addkey PROVIDER key | Activate key (masked, message deleted) |
| .py file upload | Stage as upgrade candidate |
| Any text | Route through AgentLoop |

Anti-flood: flood_window_s / flood_max_messages. Document handler fires before empty-text guard (R-66). Keys masked on echo (R-67).

---

### `tools/upgradepipeline.py` — UpgradePipeline

Self-upgrade flow: submit → scan → test → stage → approve → deploy.

**Security guards:**
- Domain allowlist (HTTPS only): github.com, raw.githubusercontent.com, gist.githubusercontent.com, pastebin.com
- Content-type: text/plain required; max 100KB
- Pattern scanner: blocks eval, exec, compile, subprocess shell injection (word-boundary regex)
- Single pending slot — only one upgrade at a time (R-52)

**Idle queue:** data/idle_queue.json — proposals from IdleProposalLoop. Auto-deployed when idle_auto_approve=true.

---

### `idleloop.py` — IdleUpgradeLoop

Background loop generating self-improvement proposals. 7-topic rotation, index persisted to data/proposal_index.txt (R-57).

Topics: tool error handling, memory retrieval, router scoring, cron reliability, security hardening, logging quality, agent prompt clarity.

Real file tree injected into every prompt to prevent hallucinated filenames (R-42, R-51).

---

### `crons/manager.py` — TaskScheduler

APScheduler (AsyncIOScheduler, Asia/Dhaka). 10 registered jobs. Uses functools.partial — not lambda — for async handlers (R-62).

| Job ID | Trigger | Handler |
|--------|---------|---------|
| morning_report | Cron 09:00 Dhaka | run_morning_report |
| heartbeat | Interval 1h | run_heartbeat |
| cache_purge | Cron 03:05 Dhaka | router.cache.purge_expired |
| cost_report | Cron 23:00 Dhaka | run_cost_report |
| daily_reset | Cron 00:01 UTC | router.reset_daily_counters |
| memory_backup | Scheduled | run_memory_backup |
| py_backup | Scheduled | run_py_backup |
| provider_health | Scheduled | run_provider_health |
| provider_hunter | Scheduled | run_provider_hunter |
| thermal_health | Scheduled | run_thermal_health |

---

## Ollama Models

| Slot | Model | Use |
|------|-------|-----|
| LOCALFAST | qwen2.5:1.5b | Quick tasks, classification, self-check (force_local) |
| LOCALHEAVY | qwen2.5:7b | Heavy local tasks |
| Embedding | nomic-embed-text | ChromaDB semantic search |

Auto-discovered on startup via GET /api/tags. Size-ranked: smallest → LOCALFAST, largest → LOCALHEAVY.

---

## Logging Architecture

| Log file | Logger name | Level | Contents |
|----------|-------------|-------|----------|
| nina.log | nina | DEBUG | General + scheduler |
| router.log | nina.router_log | DEBUG | Per-request JSON (no console propagation) |
| agent.log | nina.agent | DEBUG | AgentLoop steps |
| tools.log | nina.tools | DEBUG | Tool calls |
| upgrade.log | nina.upgrade | DEBUG | Pipeline events |
| error.log | nina.error | ERROR | Errors only |
| security.log | nina.security | DEBUG | Key activation, auth |
| emailaccess.log | nina.email_access | DEBUG | EWS access |

All: TimedRotatingFileHandler (midnight rotation, 7-day retention).

---

## Security Constraints

- Sensitive tasks always routed local — never to cloud
- Shell allowlist — limited commands; cat removed (R-48); shlex.split injection guard (R-40)
- SSRF protection — ipaddress module covers RFC-1918, loopback, link-local, cloud metadata (R-56, R-64)
- SSL verification enabled on EWS (R-49)
- API keys masked in all replies and logs (R-67)
- Single pending upgrade slot (R-52)

---

## Open Issues

| ID | Description | Priority |
|----|-------------|----------|
| O-01 | Browser — Playwright blocked, httpx fallback active | LOW |
| O-02 | EWS email password not set — tool non-functional | MEDIUM |
| O-04 | memory_context in system prompt not refreshed per session turn | LOW |
| O-05 | FastAPI REST endpoints (interfaces/api.py) not implemented | LOW |

---

## Environment Variables (`.env`)

| Key | Required | Notes |
|-----|----------|-------|
| TELEGRAMBOTTOKEN | YES | Bot token |
| AUTHORIZEDUSERID | YES | Telegram user ID |
| OLLAMAHOST | — | Default: http://localhost:11434 |
| CEREBRASAPIKEY | — | Tier 2 |
| GROQAPIKEY | — | Tier 2 |
| GEMINIAPIKEY | — | Tier 2 |
| MISTRALAPIKEY | — | Tier 2 |
| DEEPSEEKAPIKEY | — | Tier 2 |
| OPENROUTERAPIKEY | — | Tier 3 fallback |
| EWSPASSWORD | — | Office email (O-02) |
| IDLE_AUTO_APPROVE | — | true/false, hot-reloadable |
| IDLE_THRESHOLD_MIN | — | Default 15 |
| DEADMANPINGURL | — | Heartbeat ping URL |

---

## Session Workflow

1. Run `./guardian` before any code change
2. Make changes; test with `python3 -m py_compile <file>`
3. Submit via `patch` command or Telegram document upload
4. `approve` / `reject` in Telegram
5. Run `./nina_sync.sh` at session end — no exceptions
