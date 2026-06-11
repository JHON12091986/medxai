---
title: NINA Context
version: 14.0
updated: 2026-06-11
stage: "A✅ B✅ C✅ M(high-throughput)🚀"
---

# NINA Context — Attach to Every New Thread

## Overview
A comprehensive state-of-the-union document for NINA, mapping her identity, environment, and development status. This is the canonical source for new agent threads to understand their context.

## 2026-06-11 Update: Optimization Offensive (v14.0)
NINA has entered the "High-Throughput" phase. All agents now operate under **NINA-OPT-001**, prioritizing local CPU/GPU execution (NinaFlash/NinaGate) to reduce cloud token costs by 90%. Unified context is now maintained exclusively in `AGENTS.md`.

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

**PRIME DIRECTIVE:** Reduce cloud token usage by 90%, accelerate feature delivery by 10x, and maximize local autonomous throughput.

**One-line test for every feature:** *Does this make NINA more like an extension of me, or just more like a chatbot?* If it passes, build it. If not, defer it.

- **Repo:** github.com/aibony/nina — Public, MIT, v13.0 released 2026-06-11
- **Portfolio:** aibony.github.io
- **Grant target:** Anthropic Claude $1,200 OSS grant

## Environment

- **Machine:** ASUS VivoBook X530FN — Ubuntu 26.04 LTS — Python 3.14.4 — User: aibony
- **GPU:** MX150 2GB VRAM | **RAM:** 16GB
- **Repo/Venv:** `nina` / `venv`
- **Service:** systemd `nina.service` — Restart=always, depends on `ollama.service`, `ninagate.service`
- **Local models:** Ollama — `qwen2.5-coder:1.5b` (LOCALFAST), `qwen2.5-coder:7b` (LOCALHEAVY), `deepseek-coder:1.3b`
- **EWS:** webmail.basicbanklimited.com — Auth: NTLM — Domain: basic.bank
- **NinaGate:** OpenAI-compatible proxy at `http://localhost:8765`

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
  main.py          API Proxy — rutas requests through priority cascade, port 8765

interfaces/
  telegram_interface.py  Security gate, 20 commands, NLP, streaming, flood control
  api.py                REST API

crons/
  manager.py       APScheduler — 13 jobs (morning report, heartbeat, thermal, backups, etc.)

guardianengine.py  Forensic engine — AST scan, baseline drift, service health
healthcheck.py     Test suite — import isolation, structural regression
idleloop.py        Idle upgrade proposal loop, 7-topic rotation, pings Telegram

main.py                   Entry point, asyncio event loop, SIGTERM/SIGINT shutdown
data/memory/facts.json    Persistent key-value personal facts store
AGENTS.md                 Agent operating law (canonical) — MANDATORY READ
docs/space/jules_backlog.md  Task registry — 83 READY optimization tasks
```

## Phase 1 Status

### Stage A — Stop Active Failures COMPLETE (v12.2)

### Stage B — Make NINA Smarter COMPLETE (v13.0)

- B-1 F-01 Self-check pass in core/agent.py — DONE
- B-2 F-02 Personal context injection — DONE
- B-3 F-03 System prompt rewrite — DONE

### Stage C — New Capabilities (PARTIAL)

- C-1 F-04 tools/finance.py — DONE
- C-2 F-05 tools/market.py — DONE
- C-3 F-06 Reminder engine — DONE
- C-4 F-07 Email triage — DONE (officemail.py)
- C-5 F-08 remember/recall — DONE

### Stage M — Optimization Offensive (v2.0/v2.1) — READY🚀

- M-1 🚀 MEGA-TASK: Throughput Maximizer (v2.0) — IN_PROGRESS (Jules)
- M-2 📉 MEGA-TASK: Token-Surgical Architecture (v2.1) — IN_PROGRESS (Jules)
- M-3 to M-12: Token-saving infrastructure — IN_PROGRESS (Jules)
- N to T: 71 Advanced optimization tasks — READY

## Next Steps — Priority Order

1. **Merge Optimization Batch 1:** Integrate Jules' PRs for M-01 to M-10.
2. **Implement Local Fast-Path:** Move boilerplate generation to local Ollama models.
3. **Surgical Context:** Implement `nf code symbol` to avoid full-file reads.
4. **Instruction Compression:** Refactor `AGENTS.md` to reduce token overhead.

---

*Last updated: 2026-06-11 — Version 13.0 integrated (Optimization Offensive launched)*
