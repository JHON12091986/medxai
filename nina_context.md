---
title: NINA Context
version: 14.2
updated: 2026-06-16
stage: "A✅ B✅ C✅ M🚀 IN_PROGRESS"
---

# NINA Context — Attach to Every New Thread

## Overview
A comprehensive state-of-the-union document for NINA, mapping her identity, environment, and development status. This is the canonical source for new agent threads to understand their context.

## 2026-06-16 Update: Pre-Grant Housekeeping Sprint
NINA is in a **documentation and hygiene freeze** ahead of the Anthropic OSS grant application on **June 20, 2026**. No new features are being added. Focus is on repo coherence, audit passes, and documentation quality. Development resumes post-June 20.

Key changes since 2026-06-12:
- `idleloop.py` — quota-awareness guard added (`_is_quota_safe()`)
- `nina_cleanup.sh` — `--purge-oneshots` flag added
- `agy_prompt.md` — expanded with full rules + task template
- `bench_report.md` — upgraded to table format with provider cascade notes
- `WORKFLOW.md` — agy decision tree section added

## 2026-06-12 Update: Lightning Sync Release (v14.2)
NINA has entered the "Lightning Sync" phase. All agents now operate under **NINA-OPT-001**, prioritizing local CPU/GPU execution (NinaFlash/NinaGate) to reduce cloud token costs by 95%. This version integrates Parallel Tool execution (Wide-Path) and the Guardian Self-Fix loop for zero-defect autonomous deployments.

## Purpose
To provide instant alignment for AI agents (Jules, Perplexity, ninaflash) on project architecture, owner preferences, and the current phase of autonomous development.

## Usage
Attach this file to the beginning of every new conversation with a NINA-aligned agent to ensure continuity and prevent architectural drift.

## Owner Profile

- **Name:** M. Baizid Alam — AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **Personal email:** onlybony@gmail.com | **Work:** alam.b@basicbanklimited.com | **Shared:** basicid@basicbanklimited.com
- **LinkedIn:** linkedin.com/in/mba2009 | **GitHub:** github.com/aibony
- **Background:** 16 yrs banking — SWIFT/MT103/MT202/MT700, LC, BG, BB compliance, ISO 27001 Lead Auditor, BSc Engg + MBA
- **Language:** English and Bangla — match the register used
- **Style:** Direct, peer-level, no fluff. Flag risks first. Concise only.
- **Domains:** SWIFT, MT103, LC, BG, Bangladesh Bank compliance, ISO 27001

## What NINA Is

Local-first autonomous AI operator — not a chatbot. Runs 24/7 on owner's laptop in Dhaka. Acts inside the real environment: reads BASIC Bank Exchange mailbox (EWS/NTLM), runs shell commands, monitors markets, tracks expenses, pushes proactive Telegram alerts, self-upgrades with human approval. Never sends sensitive/banking data to cloud providers.

**PRIME DIRECTIVE:** Reduce cloud token usage by 95%, accelerate feature delivery by 10x, and maximize local autonomous throughput.

**One-line test for every feature:** *Does this make NINA more like an extension of me, or just more like a chatbot?* If it passes, build it. If not, defer it.

- **Repo:** github.com/aibony/nina — Public, MIT, v14.2 released 2026-06-12
- **Portfolio:** aibony.github.io
- **Grant target:** Anthropic Claude OSS grant — applying June 20, 2026

## Environment

- **Machine:** ASUS VivoBook X530FN — Ubuntu 26.04 LTS — Python 3.14.4 — User: aibony
- **GPU:** MX150 2GB VRAM | **RAM:** 16GB
- **Repo/Venv:** `nina` / `venv`
- **Service:** systemd `nina.service` — Restart=always, depends on `ollama.service`, `ninagate.service`
- **Local models:** Ollama — `qwen2.5-coder:1.5b` (LOCALFAST), `qwen2.5-coder:7b` (LOCALHEAVY), `deepseek-coder:1.3b`
- **EWS:** webmail.basicbanklimited.com — Auth: NTLM — Domain: basic.bank
- **NinaGate:** OpenAI-compatible proxy at `http://localhost:8080`

## Start / Stop / Restart

```bash
cd nina && ./guardian          # Recommended — full health check before start
sudo systemctl start nina      # Direct systemd
sudo systemctl stop nina
sudo systemctl restart nina
sudo systemctl status nina
```

## Logs

```bash
journalctl -u nina -f          # Live
journalctl -u nina -n 50       # Last 50 lines
cat nina/nina_update_log.md    # Change history
cat nina/nina_problem_log.md   # Bug/fix history
```

## Guardian — MUST run before AND after every patch

```bash
cd nina && ./guardian
```

## Git Workflow

```bash
git status
git add <specific files>       # NEVER git add .
git commit -m "type: description (ID)"
git push origin main
```

## .env Key Variables

| Key | Required | Notes |
|-----|----------|-------|
| `TELEGRAM_BOT_TOKEN` | BLOCKER | Bot token from @BotFather |
| `AUTHORIZED_USER_ID` | BLOCKER | Your Telegram user ID |
| `JULES_API_KEY` | BLOCKER | Async builder access |
| `GROQ_API_KEY` | Recommended | Free tier, default cloud provider |
| `GEMINI_API_KEY` | Recommended | Free tier fallback |
| `EWS_PASSWORD` | **SET THIS** | Activates email triage, morning report, urgency nudge |
| `RAM_GUARD_GB` | Optional | Default 10.5 |
| `API_SECRET_KEY` | BLOCKER | API security |

## Provider Architecture — 19 Providers + 2 Local

**Priority:** Free first → Groq → Gemini → Cerebras → DeepSeek → Mistral → Together → Cohere → Fireworks → Perplexity → SambaNova → OpenRouter → xAI → OpenAI (paid, last resort)

| Tier | Providers |
|------|-----------|
| TIER 1 (keyless) | POLLINATIONS, CHUTES, HFPUBLIC |
| TIER 2 (keyed) | CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini), ONEBRAIN |
| TIER 3 | OPENROUTER |
| LOCAL | LOCALFAST (qwen2.5:1.5b), LOCALHEAVY (qwen2.5:7b) |

- **Routing score:** `success_rate×0.4 + (1−latency/5000)×0.4 + not_near_limit×0.2`
- **CircuitBreaker:** CLOSED → OPEN (3 failures/120s) → HALF-OPEN (probe after 60s)
- **Sensitive tasks:** LOCAL only, no exceptions

## Thermal Guard

| Tier | CPU | GPU | Action |
|------|-----|-----|--------|
| WARN | 80°C | 80°C | Log warning only |
| GUARD | 90°C | 85°C | Force LOCALFAST, ban LOCALHEAVY |
| CRITICAL | 95°C | 90°C | Abort agent loop, notify Telegram |

## Codebase Structure

```
core/
  nina.py          NinaOS — orchestrator, startup/shutdown, morning report
  router.py        HybridRouter V4 — CircuitBreaker, composite scoring, parallel fan-out
  config.py        NinaConfig (Pydantic), RATELIMITS, load_config
  agent.py         AgentLoop — THINK-PLAN-ACT, thermal preflight, self-check pass
  memory.py        MemorySystem — ChromaDB + facts.json, build_context, remember/forget
  capabilities.py  CapabilityRegistry — per-tool health tracking
  hotreload.py     ConfigHotReload — watches .env every 60s, 18 reloadable fields

tools/
  ninaflash.py     Universe-Mode kernel — Nucleus with 100+ functions, local research/triage
  jules_api.py     Jules REST API — task dispatch (14 concurrent max)
  shell.py         Allowlist-gated shell, 10s timeout, 2000 char truncation
  web.py           DuckDuckGo search, user-agent rotation, exponential backoff
  browser.py       Playwright headless, text-only, 5000 char, SSRF-protected
  system.py        RAM/VRAM/CPU/disk/thermal, get_temps, get_ram_used_gb
  files.py         Workspace-scoped file ops, path traversal check on every call
  officemail.py    EWS/NTLM email fetch, urgency keyword scan, emailaccess.log
  search.py        Tavily → Serper → DuckDuckGo fallback chain
  gputuner.py      Dynamic GPU memory management, VRAM headroom adjustment
  upgradepipeline.py Gated patch — scan→sandbox→diff→approve→deploy

ninagate/
  main.py          API Proxy — routes requests through priority cascade, port 8080

interfaces/
  telegram_interface.py  Security gate, 20 commands, NLP, streaming, flood control
  api.py                REST API

crons/
  manager.py       APScheduler — 13 jobs (morning report, heartbeat, thermal, backups, etc.)

guardian_engine.py  Forensic engine — AST scan, baseline drift, service health
healthcheck.py      Test suite — import isolation, structural regression
idleloop.py         Idle proposal loop, 7-topic rotation, quota guard, pings Telegram

main.py                   Entry point, asyncio event loop, SIGTERM/SIGINT shutdown
data/memory/facts.json    Persistent key-value personal facts store
AGENTS.md                 Agent operating law (canonical) — MANDATORY READ
docs/space/jules_backlog.md  Task registry
```

## Phase 1 Status

### Stage A — Stop Active Failures COMPLETE (v12.2)

### Stage B — Make NINA Smarter COMPLETE (v13.0)

### Stage C — New Capabilities COMPLETE

### Stage M — Optimization Offensive 🚀 IN_PROGRESS

- M-1 🚀 MEGA-TASK: Throughput Maximizer (v2.0) — IN_PROGRESS
- M-2 📉 MEGA-TASK: Token-Surgical Architecture (v2.1) — IN_PROGRESS
- M-3 to M-12: Token-saving infrastructure — IN_PROGRESS
- N to T: 71 Advanced optimization tasks — READY

## Grant Freeze (until 2026-06-20)

No new features or architecture changes until after Anthropic OSS grant application is submitted on June 20, 2026. Only housekeeping, docs, and hygiene commits are permitted.

---

*Last updated: 2026-06-16 — v14.2 housekeeping sprint, grant freeze active*
