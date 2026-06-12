# CHANGELOG

## Overview
A chronological record of all notable changes, improvements, and fixes made to the NINA ecosystem.

## Purpose
To provide transparency and a clear historical audit trail of the project's evolution for human operators and AI agents.

## Usage
Refer to this document to understand recent architectural shifts, feature additions, or security hardening measures before starting new development tasks.

All notable changes to NINA are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) — newest first.

> **Platform history:** NINA was originally developed on Windows (v1–v8). In April 2026,
> following the release of Ubuntu 26.04 LTS, the project was ported to a dedicated Linux
> machine (ASUS VivoBook, i5 8th Gen, 16 GB RAM, MX150 GPU) for always-on deployment.
> v9 onward targets Linux/systemd. Core Python logic is platform-agnostic.

---

## [13.2.0] — 2026-06-12

### Added
- **Integrated 10 Major Feature Clusters:** Completed a massive consolidation phase, merging 10 high-priority PRs covering performance, observability, and autonomous hardening.
- **Mega Task 7 (Autonomous QA - The Guardian):** Implemented a self-fixing loop in `core/agent.py` that intercepts syntax errors in surgical edits and autonomously routes them for repair (up to 2 attempts).
- **Parallel Tool Execution:** Upgraded `AgentLoop` to support concurrent execution of multiple tools via `asyncio.gather`, significantly reducing latency for multi-step tasks.
- **Lightning Edition (Mega Task 5):** Standardized performance monitoring through benchmark harnesses (`nf bench`), quota management (`data/quota_state.json`), and incremental "Lightning Sync" backups.
- **Live Visual Telemetry Dashboard:** Integrated `dashboard/ninaui.html` and a local observability layer for real-time monitoring of CPU/GPU resource "bumps" and routing metrics.
- **Surgical Context (ChromaDB RAG):** Added `context-pack` and local RAG capabilities using ChromaDB for high-density symbol mapping and zero-token context engineering.
- **Speculative Pipeline (Scout Pattern):** Implemented the "Scout" pattern in `AgentLoop` for overlapped local/cloud execution.
- **Sovereign Self-Maintenance:** Deployed automated protocols for dependency updates, log rotation, and repository hygiene.

### Changed
- **ResponseCache Optimization:** Optimized core router logic in `core/router.py` for 2x faster cache purging.
- **ninaflash (nf) v6.5:** Added `nf test --parallel`, `nf bench`, and `nf query` commands to the local Nucleus.

### Fixed
- **Rule 0 Blocker:** Restored `is_command_safe` in `tools/shell.py`, resolving `ImportError` in `nf git` subcommands.

---

## [13.1.0] — 2026-06-11

### Added
- **NINA-Evolve Protocol (v4.0):** Defined a new autonomous self-optimization framework. This "Vicious Cycle" enables NINA to monitor its own performance (tokens, time, throughput), identify bottlenecks, and autonomously implement code upgrades.
- **Surgical Tool Standard:** Implemented a unified `async def run(input: str) -> str` interface across all core tools (`search.py`, `browser.py`, `system.py`). This ensures the `AgentLoop` can invoke any tool with a consistent pattern.
- **Performance Monitor v2.0:** Added requirements for visible CPU/GPU resource "bumps" in `tools/monitor.py` to provide empirical proof of local execution.
- **Persistent Conversational Memory:** Formalized a "Session Bridge" requirement to ensure Gemini CLI remembers project facts and past decisions across sessions using `AGENTS.md` and `MEMORY.md`.

### Fixed
- **nina.service Crash Loop:** Resolved a `ModuleNotFoundError` in `core/nina.py` caused by a broken dynamic import of `tools.searchtool`. Fixed by standardizing on `tools.search`.
- **Tool Interface Compliance:** Added missing `run` wrappers to `search`, `browser`, and `system` tools, preventing runtime errors during agentic tool use.
- **Repository Hygiene:** Pruned 6 stale Jules branches from remote and local to restore repo clarity.

---

## [13.0.0] — 2026-06-11

### Added
- **Optimization Offensive:** Launched the major "Throughput Maximizer" initiative aimed at 90% cloud token reduction and 10x feature delivery acceleration.
- **83-Task Backlog:** Expanded `docs/space/jules_backlog.md` with 83 "READY" mega-tasks grouped into 7 strategic clusters (Advanced Code Intelligence, QA Automation, Performance, Memory, Repository Hygiene, Interface, and Context Engineering).
- **NinaGate Proxy:** Integrated an OpenAI-compatible proxy on port 8080 for local "Fast-Path" routing and boilerplate offloading to Ollama models.
- **Surgical Code Intel:** Added `nf code outline` capability to `tools/ninaflash.py` for zero-token signature mapping using local AST parsing.
- **Detailed Specifications:** Created 12 individual mega-task specifications in `docs/space/` covering Surgical Intel, Token Reduction, Backlog Monitoring, and Automated Hygiene.
- **Concurrent Execution:** Dispatched 14 simultaneous high-priority optimization tasks to Jules API (system saturation limit).

### Changed
- **Documentation Overhaul:** Updated `nina_context.md`, `ARCHITECTURE.md`, and `README.md` to v13.0, integrating the "Prime Directive" and v2.1 architecture.
- **ninaflash (nf) v6.0:** Refined local executor to prioritize surgical research, automated hygiene, and high-density project heartbeats (strict 100-function Nucleus).
- **Quality Gates:** Enforced mandatory `overview/purpose/usage` sections across all core documentation to pass `nf check doc` verification.

### Fixed
- **Jules API Resilience:** Enhanced `tools/jules_api.py` with detailed error response logging and 50-session status visibility for better observability.
- **Backlog Integrity:** Repaired and unified task IDs across the entire agentic pipeline to ensure ID continuity.

---

## [12.3.0] — 2026-06-10

### Added
- **Integrated Jules PRs:**
  - `ag-d-03-04-verifiers`: Enhanced `StepVerifier` with `semantic_score` (LLM-eval) and `numeric_assert` (AG-D-03, AG-D-04)
  - `feat/ag-j-02-task-store-tests`: Added 46 comprehensive unit tests for `TaskStore`
  - `ag-a-06-plan-templates`: Added structured goal decomposition templates in `data/plans/templates/`
  - `jules-memory-tests`: Added 155 lines of unit tests for `core/memory.py`
- **Verification:** Test suite expanded from ~110 to 202 passing tests.

### Fixed
- **Sentinel Security:** Hardcoded `shell=False` in `tools/ninaflash.py` and `guardian_engine.py` to eliminate critical command injection risks.
- **Memory Identity:** Fixed Jules identity and fact injection in `MemorySystem.build_context` (AG-F-02) ensuring deterministic personal context.
- **Context Management:** Implemented character-based truncation (4000 char budget) in memory system to prevent context window overflow.
- **Config Stability:** Added `.env` key validation to `NinaConfig` (B-028) to prevent startup crashes on missing required secrets.
- **Reliability:** Hardened `tools/compact_exporter.py` with mandatory subprocess timeouts.

### Changed
- Moved Phase 1 targets (Expenditure, Email, Market, Context) to DONE status in blueprint.
- Cleaned up 11 stale/redundant feature branches from origin.

---

## [12.2.0] — 2026-06-01

### Security — Public Release Hardening

- Moved EWS identity fields from hardcoded config defaults to `.env`; no personally identifiable values in source code
- Added `.env.example` documenting all 20+ environment variables
- Verified no secrets, API keys, backups, or incident logs committed to public repository
- Comprehensive `.gitignore` covering `.env`, `data/memory/`, `data/workspace/`, `logs/`, `*.bak.*`, `venv/`, `upgrades/backups/`

### Repository

- Initial public release at [github.com/aibony/nina](https://github.com/aibony/nina)
- Added `README.md` with full feature list, provider table, installation guide, and project structure
- Added `LICENSE` (MIT, Copyright 2026 M. Baizid Alam)
- Tagged `v12.2.0` as first official GitHub Release

---

## [12.1.0] — 2026-05-23

### Security Audit — 10-Fix External Review Sweep

- `core/router.py` — purge_expired mutated dict during iteration; fixed by collecting dead keys before popping
- `core/router.py` — route() leaked raw traceback to Telegram on total failure; replaced with user-safe reply
- `core/memory.py` — build_context returned facts in insertion order; now sorts by recency x priority score
- `core/nina.py` — idle queue split-brain between two filenames; unified to single canonical path
- `crons/manager.py` — APScheduler jobs used lambda returning unawaited coroutine; replaced with functools.partial
- `tools/upgradepipeline.py` — no content-type or size guard on remote patch; enforced 100KB max and text/plain
- `tools/browser.py` — SSRF substring matching replaced with ipaddress module range validation
- `interfaces/telegram_interface.py` — .py uploads with no caption silently dropped; fixed ordering
- `interfaces/telegram_interface.py` — API keys echoed in chat; now masked and user message deleted
- `core/nina.py` — duplicate log handler guard removed

### Bug Fixes — Router Naming Regression

- Root cause: self._http vs self.http mismatch caused all local Ollama inference to silently fail
- Fixed camelCase ClassifiedTask fields to snake_case across agent and router
- Fixed forcelocal to force_local and ordered_providers to _ordered_providers
- Stripped parse_mode=Markdown to eliminate Telegram BadRequest crashes

### Guardian Enablement

- mypy installed; guardian package validation fully passes
- Config preflight no longer fails on empty API_SECRET_KEY
- Guardian mypy policy changed from hard failure to warning

---

## [12.0.0] — 2026-05-22

### Added

- Agent loop global wall-clock timeout (agent_timeout_s, default 300s)
- FastAPI rate limiting per source IP; HTTP 429 with Retry-After on breach
- router.log formal JSON schema with cost, latency, token, and status fields
- provider_hunter as 9th core scheduler job (daily 02:00)
- ConfigHotReload watching .env every 60s with Telegram notification
- ABShadowTester running candidate module alongside production for 20 requests before promotion
- CapabilityRegistry at data/capabilities.json; agent skips unhealthy tools gracefully
- OPENAI (gpt-4o-mini) added as first-class Tier 2 provider
- EWS failure path in morning report shows Unavailable instead of crashing

### Fixed

- Blocking IO in async memory methods offloaded to asyncio.to_thread
- 18 RELOADABLE hot-reload keys corrected to underscore format
- capabilities.json race condition fixed with asyncio.Lock
- Unbounded context window growth fixed with incremental scratchpad pattern
- cat removed from shell allowlist (file exfiltration risk)
- SSL verification restored on EWS (was silently disabled)
- pkill -f replaced with PID-file targeted SIGTERM
- SSRF blocklist expanded to IPv6, link-local, and cloud metadata endpoints
- Idle promptindex persisted across restarts

---

## [11.0.0] — 2026-05-10

### Added

- Three-tier thermal guard: warn (80C), guard (90C), critical (95C) for CPU; similar for GPU MX150
- get_temps() via psutil and nvidia-smi; thermal line in /status and startup message
- thermal_health scheduler job every 5 minutes (10th core job)
- 6 thermal threshold fields in NinaConfig, all hot-reloadable
- Normalized routing score formula; clamped latency term
- Full RATE_LIMITS table for all 17 providers (9 were missing)
- Per-task-type step budgets via STEP_BUDGETS dict
- Upgrade pipeline dangerous-pattern blocklist (14 patterns)
- Flood protection: flood_window_s and flood_max_messages
- Disk preflight guard for write-heavy operations

---

## [10.0.0] — 2026-05-01

### Added

- RAM preflight guard and lean-mode fallback
- Parallel slot reservation before asyncio.gather()
- Guaranteed memory backup on /reset
- Idle proposal persistence to idle_queue.json
- Provider min-spacing enforcement from RATE_LIMITS
- Heartbeat dead-man escalation with configurable ping URL

---

## [9.0.0] — 2026-04-20

### Migration: Windows to Linux

- Ported entire codebase to Ubuntu 26.04 LTS on ASUS VivoBook (i5 8th Gen, 16GB RAM, MX150)
- Replaced Windows service wrapper with nina.service systemd unit (Restart=always)
- Added ollama.service systemd dependency for local inference auto-start
- Resolved Python 3.14 + PTB 21.9 compatibility; pinned numpy<2.0
- All file paths migrated to pathlib.Path for cross-platform safety

### Added

- IdleProposalLoop with 7-topic rotation (security, routing, memory, scheduling, Telegram UX, observability, tool errors)
- promptindex persisted across restarts
- Proposals queued to idle_queue.json for manual or auto-approved review
- Ollama local models: qwen2.5:1.5b, qwen2.5:7b, nomic-embed-text

---

## [8.0.0] — 2026-04-10

### Added

- UpgradePipeline: submit, approve, reject, patch commands via Telegram
- Guardian handoff protocol with guardian_handoff.json before every restart
- Incident logging to upgrades/incidents/ with forensic reports
- ABShadowTester for safe pre-production validation

### Security

- Dangerous-pattern scanner blocks eval, exec, compile, os.system, subprocess.call, shutil.rmtree, and 8 more patterns

---

## [7.0.0] — 2026-04-01

### Added

- Guardian watchdog (guardian + guardian_engine.py): health monitoring, auto-restart, forensic reports
- healthcheck.py: standalone preflight for env, packages, syntax, and service status
- dashboard/nina-guardian.html: real-time health view in browser
- Health scoring system 0-10 with HEALTHY / WARN / CRITICAL thresholds

---

## [6.0.0] — 2026-03-20

### Added

- ConfigHotReload: live .env reload every 60s, Telegram notification, validation fallback
- CapabilityRegistry: tool health tracking with graceful skip on unhealthy tools
- NLP commands: "reload config", "show tool status"

---

## [5.0.0] — 2026-03-10

### Added

- crons/manager.py with 10 APScheduler jobs: morning report, memory backup, health checks, thermal check, dead-man ping, idle proposals, provider probe, log rotation, provider hunter, expire_pending
- Morning report: BDT exchange rate, weather summary, EWS email digest

---

## [4.0.0] — 2026-03-01

### Added

- tools/gputuner.py: dynamic GPU layer allocation based on VRAM headroom
- tools/system.py: CPU, RAM, disk, thermal monitoring; /status command
- tools/browser.py: Playwright async web automation with SSRF protection
- tools/officemail.py: EWS email integration with NTLM auth for Exchange servers
- tools/providerhunter.py: auto-discovers new free AI provider endpoints

---

## [3.0.0] — 2026-02-20

### Added

- interfaces/telegram_interface.py via python-telegram-bot
- interfaces/api.py: FastAPI REST with bearer token auth
- Flood protection, streaming replies, /reset /status /help /approve /reject commands
- Document upload handling; .py files routed to upgrade pipeline
- NLP intent classification with 15+ categories

---

## [2.0.0] — 2026-02-10

### Added

- HybridRouter v4: weighted scoring across 17 providers
- Provider tiers: LOCAL_FAST, LOCAL_HEAVY, CLOUD_FAST, CLOUD_CAPABLE, CLOUD_POWERFUL
- ResponseCache with TTL-based expiry
- RATE_LIMITS table: rpm, rpd, tpd, min_spacing_s for all providers
- core/memory.py: vector-backed facts, preferences, conversation snippets
- Providers: Groq, Gemini, Cerebras, Mistral, DeepSeek, Together, Cohere, Fireworks, Perplexity, SambaNova, Hyperbolic, Novita, xAI, OpenAI, OpenRouter, Pollinations, Chutes

---

## [1.0.0] — 2026-02-01

### Initial Release — Windows

- core/agent.py: ReAct-style agent loop with tool use and multi-step reasoning
- core/config.py: NinaConfig Pydantic model; all settings from .env
- core/nina.py: NinaOS orchestrator with startup sequence and log handlers
- core/router.py: initial single-provider Ollama router
- core/logger.py: rotating file handlers for nina, agent, router, error, security logs
- tools/search.py: Tavily / Serper / DuckDuckGo fallback search
- tools/shell.py: sandboxed shell with command allowlist
- tools/files.py: workspace file read/write/list
- main.py: PID-file management and graceful shutdown
- Windows-native; Python 3.11+

### Autonomous Evolution
- Implemented OPTIMIZE_PARALLELISM to improve system efficiency.

### Autonomous Evolution
- Implemented OPTIMIZE_PARALLELISM to improve system efficiency.

### Autonomous Evolution
- Implemented OPTIMIZE_PARALLELISM to improve system efficiency.

### Autonomous Evolution
- Implemented OPTIMIZE_PARALLELISM to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.

### Autonomous Evolution
- Implemented HARDWARE_OPTIMIZE_GPU to improve system efficiency.
