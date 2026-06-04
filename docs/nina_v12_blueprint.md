# NINA Architecture Blueprint
**Version:** 12.2
**Type:** Architecture & Design Reference
**Status:** Active — Phase 1
**Owner:** M. Baizid Alam — BASIC Bank, Dhaka
**Last Updated:** 2026-06-04

> This is the **public-safe** architecture document for NINA.
> It describes structure, design decisions, and component roles.
> It does NOT contain the system prompt, personality rules, or operator instructions.
> Those are kept in a private, secured location.

---

## What Is NINA?

NINA (Neural Intelligence Notification Agent) is a self-hosted, Telegram-based personal AI assistant that runs entirely on your own hardware. It routes tasks intelligently across 20+ free and paid AI providers, manages your email, monitors system health, and acts as a proactive personal operator — not just a chatbot.

NINA's core thesis: **the same capabilities that cost $20–$200/month from OpenAI, Anthropic, or Google can be built locally, privately, and for free — and can do things those platforms structurally cannot.**

---

## Structural Advantage

| Platform | What They Offer | What They Cannot Do |
|----------|----------------|---------------------|
| OpenAI Operator | Browser-based task automation ($200/mo) | Touch local files, terminal, desktop, private data |
| Claude Opus | Multi-step reasoning, 1M context ($20/mo) | Access local email, bank data, personal environment |
| Gemini AI Pro | Deep Research, Workspace integration ($20/mo) | Run locally, stay private, work without latency |
| **NINA** | All of the above, locally | Nothing — it runs on YOUR machine |

---

## System Architecture

```
Telegram Interface
      │
      ▼
┌─────────────────────────────────────────┐
│              NINA Core                  │
│                                         │
│  ┌──────────┐    ┌──────────────────┐  │
│  │  Router  │───▶│  Agent Loop      │  │
│  │ (Stage 2)│    │  (Stage 3)       │  │
│  └──────────┘    └────────┬─────────┘  │
│       │                   │            │
│  ┌────▼────┐    ┌─────────▼────────┐  │
│  │ Memory  │    │     Tools        │  │
│  │(Stage 4)│    │  browser/shell   │  │
│  └─────────┘    │  email/finance   │  │
│                 └──────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │     Guardian (Watchdog)          │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
      │
      ▼
 20+ AI Providers (Groq, Gemini, DeepSeek, etc.)
```

---

## Stage Map

| Stage | Component | File | Role |
|-------|-----------|------|------|
| 0 | Config & Constants | `core/config.py` | NinaConfig, rate limits, thresholds |
| 1 | Startup & Health | `core/nina.py` | Boot sequence, system checks, startup message |
| 2 | Provider Router | `core/router.py` | Multi-provider routing, rate-limit tracking, cost |
| 3 | Agent Loop | `core/agent.py` | Multi-step reasoning, tool grammar, session state |
| 4 | Memory | `core/memory.py` | Semantic recall, facts.json, personal context |
| 5 | Scheduler | `crons/manager.py` | 10 scheduled jobs, heartbeat, morning report |
| 6 | Self-Management | `core/capabilities.py`, `core/hotreload.py` | Capability registry, live config reload |
| 7 | Interfaces | `interfaces/` | Telegram bot, FastAPI REST |
| 8 | Tools | `tools/` | Browser, shell, files, email, system, GPU |
| 9 | Guardian | `guardian` | Watchdog, auto-restart, backup, health probe |

---

## Provider Routing Logic

NINA selects providers using a normalized score:

```
score = (quality_weight × quality) + (speed_weight × speed) - (latency_term)
```

Routing tiers:
- **LOCALHEAVY** — Ollama local large model (private, sensitive tasks)
- **LOCALFAST** — Ollama local fast model (self-check, quick queries)
- **CLOUD_FREE** — Groq, Gemini, Cerebras, DeepSeek, Mistral, etc.
- **CLOUD_PAID** — OpenAI, xAI (only when key present and task is non-sensitive)

Thermal guard overrides:
- CPU ≥ 90°C or GPU ≥ 85°C → ban LOCALHEAVY, force LOCALFAST/cloud
- CPU ≥ 95°C or GPU ≥ 90°C → abort agent loop entirely

---

## Memory System

```
facts.json
├── personal_context/     ← occupation, employer, priorities, habits, goals
├── semantic_memory/      ← recalled facts from past sessions
└── reminders/            ← scheduled nudges

data/
├── expenses.json         ← expenditure tracker (Phase 1)
├── capabilities.json     ← tool health registry
└── jobs.sqlite           ← cost tracker persistence
```

---

## Tool Registry

| Tool | File | Capability |
|------|------|-----------|
| Browser | `tools/browser.py` | Web browsing, page reading |
| Search | `tools/search.py` | Web search queries |
| Shell | `tools/shell.py` | Shell command execution (allowlisted) |
| Files | `tools/files.py` | File read/write operations |
| System | `tools/system.py` | CPU/RAM/disk/thermal monitoring |
| GPU Tuner | `tools/gpu-tuner.py` | Dynamic GPU management |
| Office Mail | `tools/office-mail.py` | EWS/NTLM Exchange email access |
| Finance | `tools/finance.py` | Expenditure tracker (Phase 1) |
| Market | `tools/market.py` | DSE/CSE share alerts (Phase 1) |
| Upgrade Pipeline | `tools/upgrade-pipeline.py` | Structured self-upgrade system |

---

## Guardian Watchdog

Guardian is the reliability backbone of NINA. It:
- Auto-restarts NINA on failure
- Runs preflight health checks (RAM, disk, thermal)
- Creates backup snapshots before risky operations
- Classifies warnings as `ACCEPTED-NOW`, `FIX-NEXT`, or `BLOCK-RELEASE`
- Logs all incidents to `guardian.log`

Guardian must pass before any deployment. See `NINA-Development-Policy.md` for rules.

---

## Scheduled Jobs (10 Core Jobs)

| # | Job | Frequency | Purpose |
|---|-----|-----------|---------|
| 1 | Morning report | Daily 07:00 | Email triage + market summary |
| 2 | Heartbeat | Every 5 min | Health check + Telegram alive signal |
| 3 | Thermal health | Every 5 min | CPU/GPU temperature monitoring |
| 4 | Memory backup | Daily 02:00 | Backup facts.json and memory |
| 5 | Reminder check | Every 15 min | Fire pending Telegram reminders |
| 6 | Market monitor | Every 2 hr (10:00–14:30) | DSE/CSE alert if index moves ≥1% |
| 7 | Idle loop | On idle | Background self-improvement proposals |
| 8 | Provider hunter | Daily 02:00 | Discover new free AI providers |
| 9 | Cost tracker | On each call | Log provider cost/latency to jobs.sqlite |
| 10 | Config hot reload | Every 60 sec | Apply .env changes without restart |

---

## Phase 1 Targets

| ID | Target | Status |
|----|--------|--------|
| T-1 | Personal expenditure tracker | 🔨 In progress |
| T-2 | Email intelligence & triage | 🔨 In progress |
| T-3 | DSE/CSE share market alerts | 📋 Planned |
| T-4 | Proactive reminder engine | 📋 Planned |
| T-5 | Personal context memory | 🔨 In progress |

---

## File Naming Convention

All files in this repository follow `kebab-case` lowercase naming:

| Type | Convention | Example |
|------|-----------|---------|
| Documentation | `UPPER-KEBAB.md` for root docs | `README.md`, `CHANGELOG.md` |
| Architecture docs | `kebab-case.md` in `docs/` | `docs/blueprint.md` |
| Python source | `kebab-case.py` | `core/router.py` |
| Shell scripts | `kebab-case.sh` | `guardian.sh` |
| Config/env | `UPPER_SNAKE` keys in `.env` | `GROQ_API_KEY` |

---

## Repository Structure

```
nina/
├── README.md                    ← Project overview
├── CHANGELOG.md                 ← Version history
├── CONTRIBUTING.md              ← How to contribute
├── SECURITY.md                  ← Security policy
├── LICENSE                      ← MIT License
├── .env.example                 ← Environment template
├── requirements.txt
├── main.py
├── guardian                     ← Guardian watchdog
├── guardian-engine.py
├── nina.service                 ← systemd unit
│
├── core/
│   ├── agent.py
│   ├── config.py
│   ├── memory.py
│   ├── nina.py
│   ├── router.py
│   ├── capabilities.py
│   └── hotreload.py
│
├── tools/
│   ├── browser.py
│   ├── files.py
│   ├── finance.py               ← Phase 1
│   ├── gpu-tuner.py
│   ├── market.py                ← Phase 1
│   ├── office-mail.py
│   ├── search.py
│   ├── shell.py
│   ├── system.py
│   └── upgrade-pipeline.py
│
├── interfaces/
│   ├── api.py
│   └── telegram-interface.py
│
├── crons/
│   ├── manager.py
│   └── backup-jobs.py
│
├── dashboard/
│   └── nina-guardian.html
│
├── data/                        ← Runtime data (gitignored)
│   ├── facts.json
│   ├── expenses.json
│   ├── reminders.json
│   └── jobs.sqlite
│
└── docs/
    ├── blueprint.md             ← This file
    ├── update-log.md
    ├── problem-log.md
    ├── phase1-trajectory.md
    └── vision-manifesto.md
```

---

## What Is NOT in This Repository

The following are intentionally excluded from the public repo:

| File | Reason |
|------|--------|
| `master-prompt.md` | Contains NINA's system instructions — intellectual property |
| `.env` | Contains API keys and secrets |
| `data/` | Runtime personal data — gitignored |
| `nina_backup_*.md` | Large backup snapshots — stored privately |

See `SECURITY.md` for the full security policy.
