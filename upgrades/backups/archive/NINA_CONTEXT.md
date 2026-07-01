# NINA — Master Context File
# Version: v12.2 | Updated: 2026-06-04
# Use: Attach to every new Perplexity/Claude thread about NINA

---

## Owner Profile
- **Name:** M. Baizid Alam | AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **Personal email:** onlybony@gmail.com
- **Work email:** alamba@basicbanklimited.com | Shared: basicid@basicbanklimited.com
- **LinkedIn:** linkedin.com/in/mba2009 | **GitHub:** github.com/aibony
- **Background:** 16+ yrs banking, SWIFT/MT103/MT202/MT700, LC, BG, BB compliance, ISO 27001 Lead Auditor, BSc Engg + MBA
- **Language:** English and Bangla — match the register used

---

## What NINA Is
Local-first autonomous AI operator — not a chatbot. Runs 24/7 on owner's laptop in Dhaka.
Acts inside the real environment: reads BASIC Bank Exchange mailbox (EWS/NTLM), runs shell
commands, monitors markets, tracks expenses, pushes proactive Telegram alerts, self-upgrades
with human approval. **Never sends sensitive/banking data to cloud providers.**

**One-line test for every feature:** Does this make NINA more like an extension of me, or just
more like a chatbot? If it passes, build it. If not, defer it.

---

## Environment
- **Machine:** ASUS VivoBook X530FN | Ubuntu 26.04 LTS | Python 3.11+
- **User:** aibony | **Repo:** ~/nina | **Venv:** ~/nina/venv
- **Local models (Ollama):** qwen2.5:1.5b (LOCALFAST), qwen2.5:7b (LOCALHEAVY), nomic-embed-text
- **GPU:** MX150 | **RAM:** 16GB
- **Service:** systemd `nina.service` (Restart=always, depends on ollama.service)
- **Start:** `./guardian` (manages full service lifecycle)
- **EWS:** webmail.basicbanklimited.com | Auth: NTLM | Domain: basic.bank

---

## Codebase Structure
```
~/nina/
├── core/
│   ├── nina.py          — NinaOS orchestrator, startup/shutdown, morning report
│   ├── router.py        — HybridRouter V4 (CircuitBreaker, composite scoring, parallel fan-out)
│   ├── config.py        — NinaConfig (Pydantic), RATE_LIMITS, load_config()
│   ├── agent.py         — AgentLoop: THINK→PLAN→ACT, thermal preflight, self-check pass
│   ├── memory.py        — MemorySystem: ChromaDB + facts.json, build_context(), remember/forget
│   ├── capabilities.py  — CapabilityRegistry: per-tool health tracking
│   └── hotreload.py     — ConfigHotReload: watches .env every 60s, 18 reloadable fields
├── tools/
│   ├── shell.py         — Allowlist-gated shell, 10s timeout, 2000 char truncation
│   ├── web.py           — DuckDuckGo search, user-agent rotation, exponential backoff
│   ├── browser.py       — Playwright headless, text-only, 5000 char, SSRF-protected
│   ├── system.py        — RAM/VRAM/CPU/disk/thermal, get_temps(), get_ram_used_gb()
│   ├── files.py         — Workspace-scoped file ops, path traversal check on every call
│   ├── officemail.py    — EWS/NTLM email fetch, urgency keyword scan, emailaccess.log
│   ├── search.py        — Tavily → Serper → DuckDuckGo fallback chain
│   ├── gputuner.py      — Dynamic GPU memory management, VRAM headroom adjustment
│   ├── providerhunter.py — Auto-discovers new free AI provider endpoints
│   └── upgrade_pipeline.py — Gated patch: scan→sandbox→diff→approve→deploy, 14 danger patterns
├── interfaces/
│   ├── telegram_interface.py — Security gate, 20 commands, NLP, streaming, flood control
│   └── api.py           — STUB (0 lines) — deferred to Phase 2
├── crons/manager.py     — APScheduler: 13 jobs (morning report, heartbeat, thermal, backups, etc.)
├── guardian_engine.py   — Forensic engine: AST scan, baseline drift, service health
├── healthcheck.py       — Test suite: import isolation, structural regression
├── idleloop.py          — Idle upgrade proposal loop, 7-topic rotation, pings Telegram
├── main.py              — Entry point, asyncio event loop, SIGTERM/SIGINT shutdown
├── data/memory/facts.json — Persistent key-value personal facts store
├── logs/                — 8 rotating log files, 7-day retention
├── .env                 — Secrets (NEVER commit, NEVER send to cloud)
└── guardian.sh          — Shell verification script — run after EVERY patch
```

---

## Provider Architecture (17 providers)
```
TIER 1 (keyless): POLLINATIONS, CHUTES, HF_PUBLIC
TIER 2 (keyed):   CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER,
                  COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA,
                  HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini), ONEBRAIN
TIER 3:           OPENROUTER
LOCAL:            LOCALFAST (qwen2.5:1.5b), LOCALHEAVY (qwen2.5:7b)
```
- **Routing score:** `success_rate×0.4 + (1−latency/5000)×0.4 + not_near_limit×0.2`
- **CircuitBreaker:** CLOSED → OPEN (3 failures/5min) → HALF_OPEN (probe after 1800s)
- **Sensitive tasks:** LOCAL only, no exceptions
- **Task types:** sensitive, coding, research, math, multilingual, document, vision, quick, general
- **Step budgets:** quick:3, general:5, math:6, coding:8, document:8, research:10, sensitive:5

---

## Thermal Guard (3 tiers)
| Tier     | CPU   | GPU   | Action                              |
|----------|-------|-------|-------------------------------------|
| WARN     | >80°C | >80°C | Log warning only                    |
| GUARD    | >90°C | >85°C | Force LOCALFAST, ban LOCALHEAVY     |
| CRITICAL | >95°C | >90°C | Abort agent loop, notify Telegram   |
None sensor readings silently skipped — no false aborts.

---

## Telegram Commands
```
/status   — RAM, VRAM, CPU, thermal, provider health
/router   — Provider scores, latency, token counts
/logs     — Last 20 lines nina.log
/reset    — Clear session + cache
/memory   — Show facts.json
/email    — Fetch BASIC Bank mailbox summary
patch <url> — Submit upgrade patch for review
approve   — Deploy approved patch
rollback  — Restore last backup
```

---

## Development Policy (Never Violate)
1. One change per session. Never stack fixes.
2. Run `guardian.sh` before AND after every patch to core/, tools/, or interfaces/.
3. Every patch needs a **runtime proof** — not just "no import error."
4. If Guardian shows a new BLOCKER after your patch — **rollback first**, investigate second.
5. Log the ID, file, and outcome **same day** in problem_log.md and CHANGELOG.md.
6. New capability = new tool file. Never add capability logic to core/nina.py.
7. Patches go through upgrade_pipeline — never direct file edits on the running service.
8. **Protected files (never patch directly):** core/nina.py, core/router.py, core/config.py,
   interfaces/telegram_interface.py, .env, nina.service
9. Sensitive task = local model only. No exceptions.
10. Rollback: `cp $(ls -t upgrades/backups/core_agent.py.bak.* | head -1) core/agent.py`
11. No REST API, no dashboards, no test suite, no Prometheus — not in Phase 1.
12. Definition of done: ID assigned + Guardian PASS + runtime proof + log updated.

---

## Phase 1 Trajectory
### Stage A — Stop Crashes ✅ COMPLETE (v12.2)
- ~~A-1 R-77: parallel_route RAM guard crash fixed~~
- ~~A-2 D-01: core/logger.py deleted~~
- ~~A-3 R-78: tool parse fallback added~~

### Stage B — Smarter Reasoning (PARTIAL)
- ~~B-1 F-01: Self-check pass~~ ✅ in core/agent.py
- **B-2 F-02: Personal context injection** — add `personal_context` block to facts.json,
  inject as fixed top section in build_context() BEFORE semantic recall. **NOT DONE.**
- **B-3 F-03: System prompt rewrite** — remove duplicate `Available tools:` line,
  add tone calibration (direct, peer-level, Bangla/English register). **NOT DONE.**

### Stage C — New Capabilities (NOT STARTED)
- C-1 F-04: `tools/finance.py` — SQLite expense ledger, NLP entry, weekly summary, threshold alert
- C-2 F-05: `tools/market.py` + cron — DSE/CSE alerts, 2h polling 1000–1430 Dhaka, 1% threshold
- C-3 F-06: Reminder engine — data/reminders.json, heartbeat cron checks every 15min, Telegram push
- C-4 F-07: Structured email triage — sender/subject/received/urgency_flag, keywords:
  LC, SWIFT, MT103, urgent, deadline, Bangladesh Bank
- C-5 F-08: /remember /recall — auto-inject recalled facts by topic

### Stage D — Hardening (parallel with C, one per session)
- S-01: SSRF — replace substring check with ipaddress module (tools/browser.py)
- S-02: Async memory I/O — wrap FACTS_FILE.read_text() in asyncio.to_thread (core/memory.py)
- S-04: Model version override dict in NinaConfig (core/config.py)

---

## Open Issues
| ID   | File                          | Issue                                           | Blocking?     |
|------|-------------------------------|-------------------------------------------------|---------------|
| O-06 | tools/shell.py                | `cat` in ALLOWED_BASES — path traversal risk    | **CRITICAL**  |
| O-02 | core/nina.py                  | Duplicate `Available tools:` line in prompt     | Degrades LLM  |
| O-03 | tools/browser.py              | SSRF substring guard — needs ipaddress module   | Security debt |
| O-04 | core/memory.py                | Sync file I/O in async path                     | Performance   |
| O-05 | interfaces/api.py             | FastAPI REST not implemented                    | Deferred Ph2  |

**Single most valuable unlock:** Set `EWS_PASSWORD` in `.env` → email triage, morning report
email section, and urgency nudge all activate. Zero code required.

---

## Coding Conventions
- `task.task_type` not `task_type` alone
- `STEP_BUDGETS`, `DEFAULT_MAX_STEPS` imported from `core/router.py`
- All patches: `python3 -m py_compile <file>` then `guardian.sh` before declaring done
- router.log format: JSON-lines `{ts, provider, task_type, input_tokens, output_tokens, cost_usd, ttf_ms, total_ms, parallel, cached, status, error}`
- Tool protocol: `TOOL:web INPUT:query` ... `FINAL:answer` (text-based, fallback exists)

---

## Version History (Windows → Linux migration)
- v1.0.0  (2026-02-01): Windows — ReAct agent, single Ollama router, tools scaffold
- v2.0.0  (2026-02-10): HybridRouter v4, 17 providers, ResponseCache, memory.py
- v3.0.0  (2026-02-20): Telegram interface, FastAPI, flood protection, NLP intent (15+ categories)
- v4.0.0  (2026-03-01): Tools layer — gputuner, system, browser, officemail, providerhunter
- v5.0.0  (2026-03-10): APScheduler (13 jobs), morning report (weather+FX+email)
- v6.0.0  (2026-03-20): ConfigHotReload, CapabilityRegistry, NLP config commands
- v7.0.0  (2026-04-01): Guardian watchdog, healthcheck.py, browser dashboard, systemd unit
- v8.0.0  (2026-04-10): UpgradePipeline (submit/approve/reject/patch via Telegram), 14-pattern scanner
- v9.0.0  (2026-04-20): **Linux port** (Ubuntu 26.04), IdleProposalLoop (7-topic rotation)
- v10.0.0 (2026-05-01): RAM/disk guards, parallel slots, idle persistence, heartbeat escalation
- v11.0.0 (2026-05-10): 3-tier thermal guard (CPU/GPU), normalized routing score, full RATE_LIMITS table
- v12.0.0 (2026-05-22): Agent timeout, FastAPI rate limiting, ABShadowTester, 29 bug fixes (R-29–R-57)
- v12.1.0 (2026-05-23): 10-fix external audit sweep + router snake_case regression + guardian mypy
- v12.2.0 (2026-06-01): Public release — EWS creds to .env, .gitignore, .env.example, MIT, README

---

## Key Security Fixes (v12.1 Audit)
- `purge_expired` dict mutation during iteration → collect keys first
- APScheduler lambda → unawaited coroutine → functools.partial (backups were silently not running)
- SSRF substring match → ipaddress module range validation
- API keys echoed in Telegram → delete message + masked reply + log provider name only
- `self._http` vs `self.http` mismatch → **ROOT CAUSE** of "all providers unavailable"
- `cat` removed from shell allowlist; SSL restored on EWS; `pkill -f` → PID-file SIGTERM

---

## GitHub & Public Profile
- **Repo:** github.com/aibony/nina (public, MIT, v12.2 released 2026-06-01)
- **SSH remote:** git@github.com:aibony/nina.git
- **SSH key:** ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMLscCqysdJWcgitU7REXEwWvSL1Mhb7SVZHOe/Jgf9r
- **PAT fallback:** `git remote set-url origin https://TOKEN@github.com/aibony/nina.git`
- **GitHub profile website:** https://linkedin.com/in/mba2009
- **Personal portfolio:** aibony.github.io (single-page, dark mode, built Jun 2026)
- **Grant target:** Anthropic Claude $1,200 OSS grant — angle: privacy-first AI for regulated industries

---

## Completed (This Session)
- [x] CHANGELOG.md — v1.0→v12.2 with Windows→Linux narrative, spread dates Feb–Jun 2026
- [x] README.md — Platform History section added
- [x] v12.2 GitHub Release published
- [x] SSH key generated on VivoBook
- [x] GitHub profile configured (LinkedIn in website field)
- [x] Personal portfolio page (aibony.github.io) built

## Next Steps (Pending)
- [ ] Submit Claude $1,200 OSS grant application
- [ ] Grant 500-word application draft
- [ ] B-2 F-02: Personal context injection (next dev session)
- [ ] B-3 F-03: System prompt rewrite (next dev session)
- [ ] Fix O-06: remove `cat` from shell allowlist (CRITICAL)
- [ ] Set EWS_PASSWORD in .env to activate email features

---
# HOW TO USE THIS FILE
# 1. Save to ~/nina/NINA_CONTEXT.md
# 2. In any new Perplexity thread, attach this file and start with:
#    "Continuing NINA work. Context in attached file. Today: [goal]"
