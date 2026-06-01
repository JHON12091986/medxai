# CHANGELOG

All notable changes to NINA are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) — newest first.

---

## [12.2.0] — 2026-06-01

### Security — Public Release Hardening

- Moved EWS identity fields (`EWS_USERNAME`, `EWS_MY_EMAIL`, `EWS_SHARED_EMAIL`) from hardcoded config defaults to `.env`; no personally identifiable values in source code
- Added `.env.example` template documenting all 20+ environment variables
- Verified no secrets, API keys, backups, or incident logs committed to public repository
- Comprehensive `.gitignore` covering `.env`, `data/memory/`, `data/workspace/`, `logs/`, `*.bak.*`, `venv/`, `upgrades/backups/`

### Repository

- Initial public release at [github.com/aibony/nina](https://github.com/aibony/nina)
- Added `README.md` with full feature list, provider table, installation guide, and project structure
- Added `LICENSE` (MIT, Copyright 2026 M. Baizid Alam)
- Added `.env.example` for clean onboarding
- Tagged `v12.2` as first official GitHub Release

---

## [12.1.0] — 2026-05-23

### Security Audit — 10-Fix External Review Sweep

- **`core/router.py`** — `purge_expired` mutated dict during iteration causing `RuntimeError` on cache flush; fixed by collecting dead keys before popping
- **`core/router.py`** — `route()` raised bare `RuntimeError` on total provider failure, leaking traceback to Telegram; replaced with structured log and user-safe reply
- **`core/memory.py`** — `build_context` returned facts in insertion order; added `timestamp` and `priority`; sorts by recency x priority; durable preferences always included
- **`core/nina.py`** — Idle queue split-brain between two filenames; unified to single canonical path
- **`crons/manager.py`** — APScheduler backup jobs used lambda returning unawaited coroutine; replaced with `functools.partial`; backups now actually run
- **`tools/upgradepipeline.py`** — Remote patch had no content-type or size guard; enforced 100KB max, text/plain required, diff preview before approval
- **`tools/browser.py`** — SSRF guard used substring matching; replaced with `ipaddress.ip_address()` range validation covering all private/loopback/link-local/cloud metadata ranges
- **`interfaces/telegram_interface.py`** — .py uploads with no caption silently dropped; document check moved above empty-text early-return
- **`interfaces/telegram_interface.py`** — API keys echoed in chat; now deletes user message, replies with masked key only, logs provider name only
- **`core/nina.py`** — Duplicate log handler guard removed; handler no longer appended on every restart

### Bug Fixes — Router Naming Regression

- Stripped all parse_mode="Markdown" to eliminate Telegram BadRequest crashes
- Fixed ordered_providers stale reference to _ordered_providers
- Fixed camelCase forcelocal to force_local
- Fixed camelCase ClassifiedTask fields to snake_case across agent and router
- Root cause: self._http vs self.http mismatch — all local Ollama inference silently failed

### Guardian Watchdog Enablement

- Installed mypy into venv; guardian package validation fully passes
- Config validation no longer fails at preflight on empty API_SECRET_KEY
- Guardian mypy policy changed from hard failure to warning

---

## [12.0.0] — 2026-05-22

### Added

- Agent loop global wall-clock timeout (agent_timeout_s, default 300s)
- FastAPI rate limiting per source IP; breaches return HTTP 429 with Retry-After
- router.log formal JSON schema: ts, provider, task_type, input_tokens, output_tokens, cost_usd, ttft_ms, total_ms, cached, status, error
- provider_hunter as 9th core scheduler job, runs daily at 02:00 local time
- ConfigHotReload — watches .env every 60s; falls back to old config on failure; notifies Telegram
- ABShadowTester — runs candidate module alongside production for 20 live requests before promotion
- CapabilityRegistry — JSON registry at data/capabilities.json; agent skips unhealthy tools with warning
- session_max_turns moved from hardcoded 20 to NinaConfig field
- OPENAI (gpt-4o-mini) added as first-class Tier 2 provider
- EWS failure path in morning report — failed mailbox shows Unavailable instead of crashing report
- Cache cleared on /reset alongside memory wipe

### Fixed

- Idle loop IDLE_AUTO_APPROVE wired to .env; auto-deploy added to idle summary
- Blocking IO in async memory methods offloaded to asyncio.to_thread
- KeyError on missing env vars replaced with descriptive RuntimeError
- Hot-reload deleted-key revert fixed; 18 RELOADABLE keys corrected
- capabilities.json race condition fixed with asyncio.Lock
- Unbounded context window growth fixed — system frame once; incremental scratchpad per step
- cat removed from shell allowlist (file exfiltration risk)
- SSL verification restored on EWS email connections
- patch restricted to HTTPS domain allowlist
- ResponseCache auto-purge at 500 entries
- Weak eval/exec regex replaced with word-boundary patterns
- pkill -f replaced with PID-file targeted SIGTERM
- SSRF blocklist expanded to IPv6, link-local, and cloud metadata endpoints
- Idle promptindex persisted across restarts

---

## [11.0.0] — 2026-05-20

### Added

- Three-tier thermal guard alongside RAM and disk guards
  - warn (CPU 80C / GPU 80C) — log and notify Telegram, no routing change
  - guard (CPU 90C / GPU 85C) — ban LOCAL_HEAVY, force cloud routing
  - critical (CPU 95C / GPU 90C) — abort agent loop entirely
  - Unavailable sensors silently skipped — no false aborts
- get_temps() in SystemTool — CPU via psutil, GPU via nvidia-smi
- Thermal line in /status output and startup message
- thermal_health scheduler job — 10th core job, runs every 5 minutes
- 6 thermal threshold fields in NinaConfig — all hot-reloadable without restart
- Normalized routing score formula — clamped latency term prevents unbounded scores
- Full rate-limit table covering all 17 registered providers (9 were missing)
- Per-task-type step budgets (STEP_BUDGETS dict + DEFAULT_MAX_STEPS fallback)
- Upgrade pipeline dangerous-pattern blocklist — 14 patterns
- Authorized-user flood protection (flood_window_s, flood_max_messages)
- Disk preflight guard for write-heavy operations

---

## [10.0.0] — 2026-05-19

### Added

- RAM preflight guard and lean-mode fallback
- Parallel slot reservation before asyncio.gather()
- Guaranteed memory backup on /reset
- Idle proposal persistence to idle_queue.json
- Provider min-spacing enforcement
- Heartbeat dead-man escalation with configurable ping URL

---

## [9.0.0] — 2026-05-17

### Added

- IdleProposalLoop — 7-topic rotation generating self-improvement proposals during inactivity
- promptindex rotation across tool-error-handling, security, routing, memory, scheduling, Telegram UX, and observability topics
- Proposals queued to idle_queue.json for manual or auto review
- Idle threshold and report interval configurable via NinaConfig

### Changed

- Agent loop restructured to support background idle tasks without blocking Telegram polling

---

## [8.0.0] — 2026-05-15

### Added

- UpgradePipeline — full self-upgrade system: submit, approve, reject, patch commands via Telegram
- Guardian handoff protocol — structured guardian_handoff.json written before any service restart
- Incident logging to upgrades/incidents/ with full forensic report on guardian intervention
- ABShadowTester scaffolded for safe pre-production validation of candidate modules

### Security

- Dangerous-pattern scanner blocks eval, exec, compile, os.system, subprocess.call, shutil.rmtree, and 8 additional patterns before any patch is staged

---

## [7.0.0] — 2026-05-13

### Added

- Guardian watchdog process (guardian + guardian_engine.py) — monitors NINA health, auto-restarts on crash, writes forensic incident reports
- healthcheck.py — standalone preflight checks for env, packages, syntax, and service status
- Dashboard at dashboard/nina-guardian.html — real-time health view via browser
- nina.service systemd unit with Restart=always and ollama.service dependency

### Changed

- NINA now starts via ./guardian; guardian manages the full service lifecycle

---

## [6.0.0] — 2026-05-11

### Added

- ConfigHotReload — live .env reload every 60s without service restart; Telegram notification on change
- CapabilityRegistry — tracks tool health state; agent skips unhealthy tools gracefully
- NLP-triggered config reload: "reload config" command
- NLP-triggered tool status: "show tool status" command

### Changed

- All 6 thermal thresholds, idle settings, and flood controls added to hot-reloadable field list

---

## [5.0.0] — 2026-05-09

### Added

- crons/manager.py — APScheduler-based job manager with 10 core scheduled jobs:
  1. Morning report (08:00) — weather, exchange rate, email summary
  2. Memory backup (every 6h)
  3. System health check (every 15m)
  4. Thermal health check (every 5m)
  5. Dead-man heartbeat ping (every 60m)
  6. Idle proposal generation (on idle threshold)
  7. Provider health probe (every 30m)
  8. Log rotation trigger (daily 00:00)
  9. Provider hunter (daily 02:00)
  10. expire_pending cleanup (every 1h)
- crons/backup_jobs.py — memory and workspace backup routines
- Morning report includes live exchange rate, weather summary, and EWS email digest

---

## [4.0.0] — 2026-05-07

### Added

- tools/gputuner.py — dynamic GPU memory management; adjusts layer allocation based on VRAM headroom
- tools/system.py — CPU, RAM, disk, and thermal monitoring; /status Telegram command
- tools/browser.py — Playwright-based async web automation with SSRF protection
- tools/upgradepipeline.py — scaffolded self-upgrade pipeline with approval flow
- tools/providerhunter.py — auto-discovers new free AI provider endpoints
- tools/officemail.py — EWS email integration with NTLM auth for Exchange servers

### Security

- SSRF protection on browser tool blocking private IP ranges
- Shell allowlist limiting executable commands to safe set
- nvidia-smi, ollama ps, ollama list added to shell allowlist

---

## [3.0.0] — 2026-05-05

### Added

- interfaces/telegram_interface.py — full Telegram bot interface via python-telegram-bot 21.9
- interfaces/api.py — FastAPI REST API with bearer token auth
- Flood protection — configurable window and max messages per authorized user
- Streaming replies — progressive edit_text updates during long agent responses
- /reset, /status, /help, /approve, /reject commands
- Document upload handling — .py files routed directly to upgrade pipeline
- NLP intent classification with 15+ intent categories

---

## [2.0.0] — 2026-05-03

### Added

- HybridRouter v4 — intelligent provider routing across 17 providers with weighted scoring
- Routing score formula: latency weight + cost weight + reliability weight (normalized, clamped)
- ResponseCache — LRU cache for identical prompts with TTL-based expiry
- Provider tier system: LOCAL_FAST, LOCAL_HEAVY, CLOUD_FAST, CLOUD_CAPABLE, CLOUD_POWERFUL
- Sensitive task routing — sensitive classifications route local-only regardless of load
- RATE_LIMITS table covering all 17 providers with rpm, rpd, tpd, min_spacing_s
- core/memory.py — vector-backed memory with facts, preferences, and conversation snippets
- core/capabilities.py — tool registry with health tracking
- core/hotreload.py — .env watcher scaffolded
- Providers: Groq, Gemini, Cerebras, Mistral, DeepSeek, Together, Cohere, Fireworks, Perplexity, SambaNova, Hyperbolic, Novita, xAI, OpenAI, OpenRouter, Pollinations, Chutes

---

## [1.0.0] — 2026-05-01

### Initial Release

- core/agent.py — ReAct-style agent loop with tool use and multi-step reasoning
- core/config.py — NinaConfig Pydantic model; all settings loaded from .env
- core/nina.py — NinaOS orchestrator; startup sequence, log handlers, scheduler integration
- core/router.py — initial single-provider Ollama router
- core/logger.py — rotating file handlers for nina.log, agent.log, router.log, error.log, security.log
- tools/search.py — web search via Tavily / Serper / DuckDuckGo fallback chain
- tools/shell.py — sandboxed shell execution with command allowlist
- tools/files.py — file read/write/list within workspace directory
- tools/web.py — lightweight HTTP fetch for plain-text URLs
- main.py — entry point with PID-file management and graceful shutdown
- Ollama local inference: qwen2.5:1.5b, qwen2.5:7b, nomic-embed-text
- nina.service systemd unit for auto-start on boot
- Ubuntu 26.04 + Python 3.14 + PTB 21.9 compatibility confirmed
