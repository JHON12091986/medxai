_Last updated: 2026-06-12_

## Identity
- **Project Name:** NINA (Neural Intelligent Network Assistant)
- **Version:** v14.2 (Lightning Sync Release)
- **Owner:** M. Baizid Alam — AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **Deployment Machine:** ASUS VivoBook X530FN — Ubuntu 26.04 LTS — Python 3.14.4 — User: aibony
- **Service Name:** systemd `nina.service` (Agent) + `nina-dashboard.service` (Architect)

NINA IDENTITY DIRECTIVE (canonical, applies everywhere):
NINA is a personal autonomous AI agent — NOT a chatbot. She acts, she does not describe. She completes tasks end-to-end using free-tier AI routing (Pollinations, Chutes, Groq, Gemini, Cerebras, DeepSeek and others) without requiring paid AI subscriptions for agentic capability. Her agency comes from her tools, her memory, and her routing intelligence. v14.2 introduces high-concurrency "Wide-Path" execution and zero-defect autonomous deployments.

## Architecture & Stack
- **Core Modules**: 
  - `core/nina.py` (Orchestrator)
  - `core/router.py` (HybridRouter V4 + Quota Gate)
  - `core/config.py` (NinaConfig)
  - `core/agent.py` (AgentLoop + Guardian Self-Fix)
  - `core/agent_loop.py` (Parallel Tool Hub + Scout Pattern)
  - `core/memory.py` (MemorySystem + ChromaDB RAG)
  - `core/capabilities.py` (CapabilityRegistry)
- **Interfaces**:
  - `interfaces/telegram_interface.py` (Telegram bot / security gate)
  - `interfaces/cli_interface.py` (Local CLI)
- **Guardian Engine**:
  - `guardian_engine.py` (Forensic AST checks)
  - `guardian` (System watchdog)
- **Dashboard & Monitoring**:
  - `tools/nina_dashboard.py` (Flask server)
  - `tools/live_monitor.py` (Real-time resource UI)
  - `dashboard/ninaui.html` (Visual Telemetry)
- **Key Files**:
  - `main.py` (Entry point)
  - `data/memory/facts.json` (Personal context facts)
  - `AGENTS.md` (Unified Tool Mandate - RULE 0)

## AI Providers & Quota
- **Optimization Offensive:** 95% token reduction target achieved via NinaFlash/NinaGate.
- **Provider Tiers:**
  - **Tier 1 (Keyless):** POLLINATIONS, CHUTES, HFPUBLIC
  - **Tier 2 (Keyed):** CEREBRAS, GROQ, GEMINI (3.0 Flash Preview), MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini)
  - **Local (Ollama):** LOCALFAST (qwen2.5:1.5b), LOCALHEAVY (qwen2.5:7b)
- **Quota Gate:** Forced local fallback when Gemini limits (>900 req/day) are reached.
- **Circuit Breaker:** CLOSED → OPEN (3 failures/5min) → HALF-OPEN (probe after 1800s)

## Current Phase & Status
- **Current Stage:** Stage M — High-Throughput / Lightning Sync ✅
- **Status:** v14.2 Stable. Unified 10 major feature PRs.
- **Key Achievements:**
  - **Parallelism:** Concurrent tool execution via `asyncio.gather` (Wide-Path).
  - **Guardian Self-Fix:** Autonomous syntax repair loop for surgical edits.
  - **Lightning Sync:** Incremental backup system reducing sync latency by 60%.
  - **Visual Telemetry:** Real-time CPU/GPU pulse monitoring.

## Completed Milestones (v14.2 Release)
- **MT-05 Lightning Sync**: Anchor-based incremental backups and benchmark harnesses. (DONE)
- **MT-07 Guardian Hardening**: Integrated self-fix loop in AgentLoop for zero-bug deployments. (DONE)
- **MT-08 Glass Box**: Live visual dashboard for resource "bump" monitoring. (DONE)
- **MT-09 Speculative Pipeline**: Scout pattern for overlapped local/cloud execution. (DONE)
- **MT-10 Sovereign NINA**: Total autonomous self-maintenance and log rotation. (DONE)
- **RULE0 Recovery**: Fixed `is_command_safe` import regression in `ninaflash.py`. (DONE)

## Actions & Next Tasks
- **Verification Pulse**: Verify long-term stability of parallel execution under high load.
- **Capability Expansion**: Extend local RAG capabilities for complex architectural reasoning.
- **Refreshed Board Priority:** v14.2 stability and throughput validation.

## Key File Paths
- **Repository:** `/home/aibony/nina`
- **Virtual Environment:** `.venv` (Python 3.14)
- **Systemd Services:** `nina.service`, `ninagate.service`, `nina-dashboard.service`
- **Logs:** `/home/aibony/nina/logs/` (router.log, ninaflash.log, agent.log)
- **Exports:** `/home/aibony/nina/docs/space/` (claude_feed.md, nina_latest.md)

## NINA Tool Routing Policy (RULE 0)
**Principle:** USE LOCAL FIRST. All mechanical tasks (read, grep, git, format) MUST use `nf` tools to bypass cloud cost and latency.
- **Mandate:** Consult `AGENTS.md` before every tool call.
- **Efficiency:** 95% of tool turns offloaded to local CPU.
- **Compliance:** Self-audit required at end of every session.
