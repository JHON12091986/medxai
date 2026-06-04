---
Version: 12.2
Type: Architecture & Design Reference
Status: Active — Phase 1
Owner: M. Baizid Alam, BASIC Bank, Dhaka
Last Updated: 2026-06-04
Note: Public-safe architecture document. Does NOT contain system prompt, personality rules, or operator instructions.
---

# NINA Architecture Blueprint

## What Is NINA?
NINA (Neural Intelligence Notification Agent) is a self-hosted, Telegram-based personal AI assistant
that runs entirely on your own hardware. It routes tasks intelligently across 20 free and paid AI
providers, manages your email, monitors system health, and acts as a proactive personal operator
— not just a chatbot.

**Core thesis:** The same capabilities that cost $20-$200/month from OpenAI, Anthropic, or Google
can be built locally, privately, and for free — and can do things those platforms structurally cannot.

## Structural Advantage
| Platform | What They Offer | What They Cannot Do |
|----------|----------------|---------------------|
| OpenAI Operator | Browser-based task automation ($200/mo) | Touch local files, terminal, private data |
| Claude Opus | Multi-step reasoning, 1M context ($20/mo) | Access local email, bank data, personal environment |
| Gemini AI Pro | Deep Research, Workspace integration ($20/mo) | Run locally, stay private, work without latency |
| NINA | All of the above, locally | Nothing — it runs on YOUR machine |

## System Architecture
    Telegram Interface
         |
    NINA Core (nina.py)
         |
    Router (router.py)  <-->  Agent Loop (agent.py)
         |                         |
    Memory (memory.py)         Tools (browser/shell/email/finance)
         |
    Guardian Watchdog
         |
    20 AI Providers (Groq, Gemini, DeepSeek, etc.)

## Stage Map
| Stage | Component | File | Role |
|-------|-----------|------|------|
| 0 | Config & Constants | core/config.py | NinaConfig, rate limits, thresholds |
| 1 | Startup & Health | core/nina.py | Boot sequence, system checks, startup message |
| 2 | Provider Router | core/router.py | Multi-provider routing, rate-limit tracking, cost |
| 3 | Agent Loop | core/agent.py | Multi-step reasoning, tool grammar, session state |
| 4 | Memory | core/memory.py | Semantic recall, facts.json, personal context |
| 5 | Scheduler | crons/manager.py | 13 scheduled jobs, heartbeat, morning report |
| 6 | Self-Management | core/capabilities.py, core/hotreload.py | Capability registry, live config reload |
| 7 | Interfaces | interfaces/ | Telegram bot, FastAPI REST (stub) |
| 8 | Tools | tools/ | Browser, shell, files, email, system, GPU |
| 9 | Guardian | guardian/ | Watchdog, auto-restart, backup, health probe |

## Provider Routing Logic
NINA selects providers using a normalized score:
    score = quality_weight * quality + speed_weight * speed - latency_term

Routing tiers:
- LOCALHEAVY — Ollama local large model (private, sensitive tasks)
- LOCALFAST — Ollama local fast model (self-check, quick queries)
- CLOUDFREE — Groq, Gemini, Cerebras, DeepSeek, Mistral, etc.
- CLOUDPAID — OpenAI, xAI (only when key present and task is non-sensitive)

Thermal guard overrides:
- CPU >= 90C or GPU >= 85C: ban LOCALHEAVY, force LOCALFAST/cloud
- CPU >= 95C or GPU >= 90C: abort agent loop entirely

## Memory System
    data/memory/facts.json       personal_context — occupation, employer, priorities, habits, goals
                                 semantic_memory  — recalled facts from past sessions
                                 reminders        — scheduled nudges
    data/expenses.json           expenditure tracker (Phase 1)
    capabilities.json            tool health registry
    jobs.sqlite                  cost tracker persistence

## Tool Registry
| Tool | File | Capability |
|------|------|------------|
| Browser | tools/browser.py | Web browsing, page reading |
| Search | tools/search.py | Web search queries |
| Shell | tools/shell.py | Shell command execution (allowlisted) |
| Files | tools/files.py | File read/write operations |
| System | tools/system.py | CPU/RAM/disk/thermal monitoring |
| GPU Tuner | tools/gpu-tuner.py | Dynamic GPU management |
| Office Mail | tools/office-mail.py | EWS/NTLM Exchange email access |
| Finance | tools/finance.py | Expenditure tracker (Phase 1) |
| Market | tools/market.py | DSE/CSE share alerts (Phase 1) |
| Upgrade Pipeline | tools/upgrade-pipeline.py | Structured self-upgrade system |

## Guardian Watchdog
Guardian is the reliability backbone of NINA. It:
- Auto-restarts NINA on failure
- Runs preflight health checks (RAM, disk, thermal)
- Creates backup snapshots before risky operations
- Classifies warnings as ACCEPTED-NOW, FIX-NEXT, or BLOCK-RELEASE
- Logs all incidents to guardian.log

Guardian MUST pass before any deployment.

## Scheduled Jobs (13 Core Jobs)
| Job | Frequency | Purpose |
|-----|-----------|---------|
| Morning report | Daily 07:00 | Email triage + market summary |
| Heartbeat | Every 5 min | Health check + Telegram alive signal |
| Thermal health | Every 5 min | CPU/GPU temperature monitoring |
| Memory backup | Daily 02:00 | Backup facts.json and memory |
| Reminder check | Every 15 min | Fire pending Telegram reminders |
| Market monitor | Every 2hr 10:00-14:30 | DSE/CSE alert if index moves 1% |
| Idle loop | On idle | Background self-improvement proposals |
| Provider hunter | Daily 02:00 | Discover new free AI providers |
| Cost tracker | On each call | Log provider cost/latency to jobs.sqlite |
| Config hot reload | Every 60 sec | Apply .env changes without restart |

## Phase 1 Targets
| ID | Target | Status |
|----|--------|--------|
| T-1 | Personal expenditure tracker | In progress |
| T-2 | Email intelligence triage | In progress |
| T-3 | DSE/CSE share market alerts | Planned |
| T-4 | Proactive reminder engine | Planned |
| T-5 | Personal context memory | DONE (F-02) |

## File Naming Convention
| Type | Convention | Example |
|------|-----------|---------|
| Documentation | UPPER-KEBAB.md for root docs | README.md, CHANGELOG.md |
| Architecture docs | kebab-case.md in docs/ | docs/blueprint.md |
| Python source | kebab-case.py | core/router.py |
| Shell scripts | kebab-case.sh | guardian.sh |
| Config/.env | UPPER_SNAKE keys | GROQ_API_KEY |

## Repository Structure
    nina/
      README.md, CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, LICENSE (MIT)
      .env.example, requirements.txt, main.py, guardian.sh, nina.service
      core/     agent.py, config.py, memory.py, nina.py, router.py, capabilities.py, hotreload.py
      tools/    browser.py, files.py, finance.py, gpu-tuner.py, market.py,
                office-mail.py, search.py, shell.py, system.py, upgrade-pipeline.py
      interfaces/   api.py, telegram-interface.py
      crons/        manager.py, backup-jobs.py
      data/         facts.json, expenses.json, reminders.json, jobs.sqlite (all gitignored)
      docs/         blueprint.md, update-log.md, problem-log.md, phase1-trajectory.md

## What Is NOT in the Public Repo
| File | Reason |
|------|--------|
| master-prompt.md | Contains NINA's system instructions — intellectual property |
| .env | Contains API keys and secrets |
| data/ | Runtime personal data — gitignored |
| nina_backup*.md | Large backup snapshots — stored privately |
