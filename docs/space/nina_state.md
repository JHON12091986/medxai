# NINA State — Single Source of Truth
_Last updated: 2026-06-08_

## Identity
- **Project Name:** NINA
- **Owner:** M. Baizid Alam — AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **Deployment Machine:** ASUS VivoBook X530FN — Ubuntu 26.04 LTS — Python 3.14.4 — User: aibony
- **Service Name:** systemd `nina.service` (Agent) + `nina-dashboard.service` (Architect)

NINA IDENTITY DIRECTIVE (canonical, applies everywhere):
NINA is a personal autonomous AI agent — NOT a chatbot. She acts, she does not describe. She completes tasks end-to-end using free-tier AI routing (Pollinations, Chutes, Groq, Gemini, Cerebras, DeepSeek and others) without requiring paid AI subscriptions for agentic capability. Her agency comes from her tools, her memory, and her routing intelligence. Every session, every feature, and every spec must serve this mission.

## Architecture & Stack
- **Core Modules**: 
  - `core/nina.py` (Orchestrator)
  - `core/router.py` (HybridRouter V4)
  - `core/config.py` (NinaConfig)
  - `core/agent.py` (AgentLoop)
  - `core/memory.py` (MemorySystem)
  - `core/capabilities.py` (CapabilityRegistry)
  - `core/hotreload.py` (ConfigHotReload)
- **Interfaces**:
  - `interfaces/telegraminterface.py` (Telegram bot / security gate)
- **Guardian Engine**:
  - `guardianengine.py` (Forensic checks)
- **Dashboard & Architect**:
  - `tools/nina_dashboard.py` (Flask server)
  - `dashboard/puter_architect.html` (Puter.js Dev Console)
- **Key Files**:
  - `main.py` (Entry point)
  - `data/memory/facts.json` (Personal context facts)
  - `guardian.sh` (Shell validation script)

## AI Providers & Quota
- **Priority Priority List:** Free first → Groq → Gemini → Cerebras → DeepSeek → Mistral → Together → Cohere → Fireworks → Perplexity → SambaNova → OpenRouter → xAI → OpenAI (paid, last resort)
- **Provider Tiers:**
  - **Tier 1 (Keyless):** POLLINATIONS, CHUTES, HFPUBLIC
  - **Tier 2 (Keyed):** CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini), ONEBRAIN
  - **Tier 3:** OPENROUTER
  - **Local:** LOCALFAST (qwen2.5:1.5b), LOCALHEAVY (qwen2.5:7b)
- **Routing Score Algorithm:** `success_rate × 0.4 + (1 - latency / 5000) × 0.4 + not_near_limit × 0.2`
- **Circuit Breaker state:** CLOSED → OPEN (3 failures/5min) → HALF-OPEN (probe after 1800s)

## Current Phase & Next Task
- **Current Stage:** Stage B — Make NINA Smarter (PARTIAL)
- **What is done:**
  - B-1 F-01 Self-check pass in `core/agent.py` (DONE)
  - B-2 F-02 Personal context injection in `core/memory.py` and `data/memory/facts.json` (DONE)
- **What is next:**
  - B-3 F-03 Response tone calibration in system prompt (`core/nina.py` SYSTEM_PROMPT_TEMPLATE)

## Open Milestones
- **B-3 F-03**: Response tone calibration in system prompt (`core/nina.py` SYSTEM_PROMPT_TEMPLATE)
- **C-1 F-04**: Expenditure tracker tool (`tools/finance.py`)
- **C-2 F-05**: Share market monitor (`tools/market.py`) + `crons/manager.py`
- **C-3 F-06**: Proactive reminder engine (`core/nina.py` + `data/reminders.json`)
- **C-4 F-07**: Email triage improvement (`tools/office_mail.py`)
- **C-5 F-08**: Personal knowledge base (`core/memory.py` + Telegram command handler)
## Completed Milestones
- **S-01**: Fix SSRF substring → `ipaddress` module (`tools/browser.py`) (DONE)
- **S-02**: Wrap memory file I/O in `asyncio.to_thread` (`core/memory.py`) (DONE)
- **S-03**: Fix `ResponseCache.purge_expired` dict mutation (`core/router.py`) (DONE)
- **S-04**: Add model version override dict to `NinaConfig` (`core/config.py`) (DONE)
- **S-05**: Add `if not root.handlers` guard in logger setup (`core/nina.py`) (DONE)

## Action Board Confidence
- **Revalidation Pass:** Conducted on 2026-06-06 against live code and guardian evidence.
- **Historical Blocker & Warning Signatures (Confirmed Stale/FIXED):**
  - Router attribute issues (`router.attr.forcelocal`, `router.attr.orderedproviders`, `router.attr.selfhttp`) are verified as resolved.
  - Startup issues (`startup.nameError`, `startup.syntaxError`, etc.) are resolved; `guardian` now returns `Status: PASS` cleanly.
  - Hot-reload environment reverts (`hotreload.deletedkeyrevert`) and SSRF guard regressions (`browser.ssrf.guardregression`) are fixed in live source code.
  - Env variables (`apisecretkey`, `authorizeduserid`, `telegrambottoken`) are populated and loaded properly at runtime.
  - Conflicting scheduler ID issues (`cron.conflictingid`) are resolved.
  - Telegram interface issues (`telegram.document.handler_order` via dedicated handler, `telegram.key.echoed_in_chat` via centralized mask helper, and `telegram.parsemode.badrequest` via safe defaults) are resolved.
  - Logging handler duplication check (`logger.duplicate_handler`) is resolved via a root.handlers guard.
- **Genuinely Unresolved Items (Confirmed OPEN):**
  - None (all warning items from the register are resolved).
- **Refreshed Board Priority:** Action priority must now follow the refreshed error register board.

## Capabilities
- **shell**: loaded=true, healthy=true
- **web**: loaded=true, healthy=true
- **browser**: loaded=true, healthy=true
- **file**: loaded=true, healthy=true
- **system**: loaded=true, healthy=true
- **email**: loaded=true, healthy=true
- **gpu**: loaded=true, healthy=true

## Memory Facts
- **name**: M. Baizid Alam
- **role**: AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **language**: English and Bangla — match the register used
- **timezone**: UTC+6 (Dhaka)
- **domains**: SWIFT, MT103, MT202, MT700, LC, BG, BB compliance, ISO 27001 Lead Auditor
- **style**: Direct, peer-level, no fluff. Concise. Flag risks proactively.
- **github**: github.com/aibony
- **project**: NINA — local-first autonomous AI operator, self-hosted on VivoBook Ubuntu

## Key File Paths
- **Repository:** `/home/aibony/nina`
- **Virtual Environment:** `/home/aibony/nina/ninavenv` (or `.venv`)
- **Systemd Service:** `/etc/systemd/system/nina.service`
- **Rotating Logs Directory:** `/home/aibony/nina/logs/`
- **Exports Directory:** `/home/aibony/nina/exports/`

## NINA Tool Routing Policy v2 Summary

**Principle:** Perplexity plans, the local executor stabilizes, Jules builds — running IN PARALLEL.

### Four-Tool Parallel Model

| Tool | Role | Execution Mode |
|------|------|---------------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Active throughout — specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| Local Executor (ninaflash, Cursor, Claude Code, Cline, aider) | LOCAL MUSCLE | Sync local executor — edits, merges Jules PRs, deploys to service |
| aider-chat (./nina-aider.sh) | INTERACTIVE LOCAL CODER — interactive multi-file editing with full repo context via OpenRouter. Use when iterating live with direct file edits and needing conversational pair-programming. Requires terminal presence. | Interactive sync |

### The Full Parallel Loop
1. Perplexity diagnoses + writes precise spec
2. Jules receives spec → builds in cloud async (no interaction after submit)
3. The local executor handles any urgent local fixes in parallel on its own worktree
4. Jules opens PR when done
5. The local executor reviews Jules PR diff, runs lint/compile checks, merges to main
6. The local executor runs `./nina_sync.sh` to deploy and export
7. Perplexity reviews result (attach `nina_latest.md` to new thread)

### Local Executor as Merge Executor (Mandatory)
- The local executor performs ALL Jules PR merges — never auto-merge via GitHub UI
- Before merge: `python3 -m py_compile` + `pyflakes` on changed files, check `jules_lock.txt`
- After merge: `./nina_sync.sh` — no exceptions
- Merge conflict → stop, escalate to Perplexity for re-spec

### Key Rules
- Check `jules_lock.txt` before starting any task.
- High-risk files (`main.py`, `router.py`, `telegram_interface.py`, `guardian_engine.py`, `shell.py`, `.env`) default to local executor / manual local only.
- Perplexity requires exact source attachments for code edits; `nina_latest.md` is for snapshot awareness only.
- Sensitive paths remain LOCAL only — never cloud.
