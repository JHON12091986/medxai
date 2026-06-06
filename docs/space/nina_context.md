---
title: NINA Context
version: 12.2
updated: 2026-06-05
stage: "A✅ B(partial) C(queued)"
---

# NINA Context — Attach to Every New Thread

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

**One-line test for every feature:** *Does this make NINA more like an extension of me, or just more like a chatbot?* If it passes, build it. If not, defer it.

- **Repo:** github.com/aibony/nina — Public, MIT, v12.2 released 2026-06-01
- **Portfolio:** aibony.github.io
- **Grant target:** Anthropic Claude $1,200 OSS grant

## Environment

- **Machine:** ASUS VivoBook X530FN — Ubuntu 26.04 LTS — Python 3.14.4 — User: aibony
- **GPU:** MX150 2GB VRAM | **RAM:** 16GB
- **Repo/Venv:** `nina` / `ninavenv`
- **Service:** systemd `nina.service` — Restart=always, depends on `ollama.service`
- **Local models:** Ollama — `qwen2.5:1.5b` (LOCALFAST), `qwen2.5:7b` (LOCALHEAVY), `nomic-embed-text` (embeddings)
- **EWS:** webmail.basicbanklimited.com — Auth: NTLM — Domain: basic.bank

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
| `GROQ_API_KEY` | Recommended | Free tier, default cloud provider |
| `GEMINI_API_KEY` | Recommended | Free tier fallback |
| `OPENAI_API_KEY` | Optional | Paid — use sparingly |
| `EWS_USERNAME` | Optional | BASIC Bank Exchange |
| `EWS_PASSWORD` | **SET THIS** | Activates email triage, morning report, urgency nudge — zero code required |
| `EWS_MY_EMAIL` | Optional | Your Exchange email |
| `EWS_SHARED_EMAIL` | Optional | Shared mailbox |
| `RAM_GUARD_GB` | Optional | Default 10.5 |
| `IDLE_AUTO_APPROVE` | Optional | Auto-deploy idle queue patches |
| `API_SECRET_KEY` | BLOCKER | API security |

## Provider Architecture — 19 Providers + 2 Local

**Priority:** Free first → Groq → Gemini → Cerebras → DeepSeek → Mistral → Together → Cohere → Fireworks → Perplexity → SambaNova → OpenRouter → xAI → OpenAI (paid, last resort)

### Provider Registry and Cost Profiles

| Tier | Provider | Cost Profile | Typical Use Case | Sensitivity Rule |
|------|----------|--------------|------------------|------------------|
| TIER 1 | POLLINATIONS | Free (Keyless) | General fast tasks, fallback | Public data only |
| TIER 1 | CHUTES | Free (Keyless) | Reason-heavy (DeepSeek R1) | Public data only |
| TIER 1 | HFPUBLIC | Free (Keyless) | Miscellaneous small tasks | Public data only |
| TIER 2 | CEREBRAS | Free tier / Keyed | Fast general execution | Public data only |
| TIER 2 | GROQ | Free tier / Keyed | Ultra-fast execution | Public data only |
| TIER 2 | GEMINI | Free tier / Keyed | Multilingual (Bangla), Vision | Public data only |
| TIER 2 | MISTRAL | Paid / Keyed | Complex logic, reasoning | Public data only |
| TIER 2 | DEEPSEEK | Paid / Keyed | Coding, deep reasoning | Public data only |
| TIER 2 | TOGETHER | Paid / Keyed | Heavy inference (Llama 405B) | Public data only |
| TIER 2 | COHERE | Paid / Keyed | Document heavy, command | Public data only |
| TIER 2 | FIREWORKS | Paid / Keyed | Heavy inference (Llama 405B) | Public data only |
| TIER 2 | XAI | Paid / Keyed | General coding, fallback | Public data only |
| TIER 2 | PERPLEXITY | Paid / Keyed | Research, search-heavy | Public data only |
| TIER 2 | SAMBANOVA | Free tier / Keyed | Heavy inference | Public data only |
| TIER 2 | HYPERBOLIC | Free tier / Keyed | Heavy inference | Public data only |
| TIER 2 | NOVITA | Paid / Keyed | Fast inference | Public data only |
| TIER 2 | OPENAI | Paid / Keyed | Reliable fallback, formatting | Public data only |
| TIER 2 | ONEBRAIN | Custom / Keyed | Custom local/remote proxy | Public data only |
| TIER 3 | OPENROUTER | Paid / Keyed | Universal fallback | Public data only |
| LOCAL | LOCALFAST | Free (Local) | Quick commands, sensor checks | Sensitive / Private |
| LOCAL | LOCALHEAVY | Free (Local) | Local coding, sensitive docs | Sensitive / Private |

### Routing and Circuit Breaker Behavior

- **Task Classification:** Tasks are mapped to types (`sensitive`, `coding`, `research`, `math`, `multilingual`, `document`, `vision`, `quick`, `general`).
- **Sensitive Routing:** If a task is flagged as `sensitive` (e.g. banking info, private mail, personal data), it completely bypasses the cloud tiers. **It is strictly routed to LOCALFAST or LOCALHEAVY. No exceptions.**
- **Bangla Routing:** Queries containing Bangla text (`U+0980–U+09FF`) prioritize specific multilingual providers (GEMINI, OPENAI, MISTRAL, CEREBRAS, GROQ, PERPLEXITY) first.
- **Dynamic Scoring:** For cloud tasks, providers are scored via `composite_score`:
  `success_rate×0.4 + (1−latency/5000)×0.4 + not_near_limit×0.2`.
  Higher score wins.
- **Circuit Breaker:**
  - **CLOSED:** Normal operation.
  - **OPEN:** After 3 consecutive failures within 5 minutes (120s rolling window). Traffic is hard-blocked to this provider.
  - **HALF-OPEN:** After a 60s cooldown, exactly one probe request is allowed to test recovery. If it succeeds, the breaker closes; if it fails, it re-opens and waits again.

## Thermal Guard

| Tier | CPU | GPU | Action |
|------|-----|-----|--------|
| WARN | 80°C | 80°C | Log warning only |
| GUARD | 90°C | 85°C | Force LOCALFAST, ban LOCALHEAVY |
| CRITICAL | 95°C | 90°C | Abort agent loop, notify Telegram |

None = sensor readings silently skipped (no false aborts)

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
  shell.py         Allowlist-gated shell, 10s timeout, 2000 char truncation
  web.py           DuckDuckGo search, user-agent rotation, exponential backoff
  browser.py       Playwright headless, text-only, 5000 char, SSRF-protected
  system.py        RAM/VRAM/CPU/disk/thermal, get_temps, get_ram_used_gb
  files.py         Workspace-scoped file ops, path traversal check on every call
  officemail.py    EWS/NTLM email fetch, urgency keyword scan, emailaccess.log
  search.py        Tavily → Serper → DuckDuckGo fallback chain
  gputuner.py      Dynamic GPU memory management, VRAM headroom adjustment
  providerhunter.py  Auto-discovers new free AI provider endpoints
  upgradepipeline.py Gated patch — scan→sandbox→diff→approve→deploy, 14 danger patterns

interfaces/
  telegraminterface.py  Security gate, 20 commands, NLP, streaming, flood control
  api.py                STUB (0 lines) — deferred to Phase 2

crons/
  manager.py       APScheduler — 13 jobs (morning report, heartbeat, thermal, backups, etc.)

guardianengine.py  Forensic engine — AST scan, baseline drift, service health
healthcheck.py     Test suite — import isolation, structural regression
idleloop.py        Idle upgrade proposal loop, 7-topic rotation, pings Telegram

main.py                   Entry point, asyncio event loop, SIGTERM/SIGINT shutdown
data/memory/facts.json    Persistent key-value personal facts store (F-02 populated)
logs/                     8 rotating log files, 7-day retention
.env                      Secrets — NEVER commit, NEVER send to cloud
guardian.sh               Shell verification script — run after EVERY patch
```

> **Note:** `core/logger.py` DELETED in R-101 (DEV 5.8, 2026-06-06).

## Telegram Commands

| Command | Action |
|---------|--------|
| `/status` | RAM, VRAM, CPU, thermal, provider health |
| `/router` | Provider scores, latency, token counts |
| `/logs` | Last 20 lines nina.log |
| `/reset` | Clear session cache + memory |
| `/email` | Fetch BASIC Bank mailbox summary |
| `/patch <url>` | Submit upgrade patch for review |
| `/approve` | Deploy approved patch |
| `/rollback` | Restore last backup |

## Task Types & Step Budgets

| Task Type | Max Steps | Cache TTL |
|-----------|-----------|-----------|
| quick | 3 | 3600s |
| general | 5 | 7200s |
| multilingual | 5 | 7200s |
| math | 6 | 21600s |
| coding | 8 | 21600s |
| document | 8 | 14400s |
| research | 10 | 1800s |
| sensitive | 5 | 0 (no cache) |

## Coding Conventions

- Use `task.task_type`, not `tasktype` alone
- `STEP_BUDGETS`, `DEFAULT_MAX_STEPS` imported from `core/router.py`
- All patches: `python3 -m py_compile <file>` then `./guardian` before declaring done
- `router.log` format: JSON-lines — `ts, provider, task_type, input_tokens, output_tokens, cost_usd, ttf_ms, total_ms, parallel, cached, status, error`
- Tool protocol: `TOOL:web INPUT:query` → `FINAL:answer` — text-based, fallback exists

## Rollback Commands

```bash
cp nina/upgrades/backups/backup-TIMESTAMP/core/memory.py nina/core/memory.py
sudo systemctl restart nina
# Or named backup:
cp nina/upgrades/backups/core-cleanup-memory.py.bak nina/core/memory.py
```

## Guardian Pass Criteria

1. venv active, Python 3.14, all required packages present
2. .env validation passed (TELEGRAM_CHAT_ID warning: acceptable)
3. Syntax check — all tracked files OK
4. pyflakes — no issues
5. mypy — warnings non-blocking
6. nina.service active, no crash pattern
7. Telegram polling confirmed
8. APScheduler started (13 jobs)

### Guardian Notes (Ongoing)

- Health score 5.8/10 is driven by stale journal signature matches — not live issues
- Blocker signatures (AttributeError, ConflictingIdError, BlockingIOError) are historical journal echoes
- Baseline will reset to PASS once a clean run clears the incident history
- mypy 22 advisory findings are non-blocking — core/config.py NinaConfig kwargs, tools/system.py

## Development Policy Summary (see nina_dev_policy.md for full rules)

1. Every change has an ID — no anonymous fixes
2. One purpose per patch — never bundle unrelated changes
3. Guardian runs before AND after every change to core, tools, interfaces, main.py, .env, or service files
4. Every risky change must be recoverable — guardian snapshot, git commit, or manual backup first
5. Runtime proof required — nina.service active, Telegram responding, target behaviour confirmed
6. Logs updated same day — nina_update_log.md + nina_problem_log.md
7. Production fixes beat cleanup priority
8. No blind AI patching — read target files, confirm paths are real, confirm names match current code
9. Protect interfaces and secrets — interfaces/telegraminterface.py, .env, router are high-risk
10. Warnings must be managed — ACCEPTED-NOW / FIX-NEXT / BLOCK-RELEASE
11. Small changes win — prefer one-line fixes over rewrites
12. Done = ID assigned, one purpose, guardian ran, runtime verified, rollback exists, logs updated

## Phase 1 Status

### Stage A — Stop Active Failures COMPLETE (v12.2)

R-01 to R-78: 65 issues resolved, crashes stopped.

### Stage B — Make NINA Smarter (PARTIAL)

- B-1 F-01 Self-check pass in core/agent.py — DONE
- B-2 F-02 Personal context injection — DONE (2026-06-04)
  - data/memory/facts.json populated: name, role, bank, language, timezone, domains, style, github, project
  - core/memory.py patched — Owner block injected at top of build_context before semantic recall
  - Rollback: upgrades/backups/memory.py.bak.20260604
- B-3 F-03 System prompt rewrite — remove duplicate "Available tools" line in core/nina.py, add tone calibration — NOT DONE

### Stage C — New Capabilities (NOT STARTED)

- C-1 F-04 tools/finance.py — SQLite ledger, NLP entry, weekly summary, threshold alert
- C-2 F-05 tools/market.py — cron DSE/CSE, 2h polling 10:00-14:30 Dhaka, 1% threshold Telegram alert
- C-3 F-06 Reminder engine — data/reminders.json, heartbeat cron checks every 15min
- C-4 F-07 Email triage — structured sender/subject/received/urgency/flag output, keywords: LC, SWIFT, MT103, urgent, deadline, Bangladesh Bank
- C-5 F-08 remember/recall — auto-inject recalled facts by topic

### Stage D — Hardening (parallel with C, one per session)

- S-01 SSRF fix — replace substring check with ipaddress module in tools/browser.py
- S-02 Async memory IO — wrapped in F-02 patch
- S-04 Model version override dict in NinaConfig (core/config.py)

## Open Issues

| ID | File | Issue | Blocking? |
|----|------|-------|-----------|
| O-02 | core/nina.py | Duplicate "Available tools" line in prompt | Degrades LLM |
| O-03 | tools/browser.py | SSRF substring guard — verify R-64 closed this | Security debt |
| O-06 | tools/shell.py | cat in ALLOWED_BASES — path traversal risk | CRITICAL |

Single most valuable unlock: Set EWS_PASSWORD in .env — email triage, morning report email section,
and urgency nudge all activate. Zero code required.

## Next Steps — Priority Order

1. F-03 DONE (Entry 027)
2. Set EWS_PASSWORD in .env — activate email features, zero code, instant unlock
3. O-06 DONE (R-97), O-03 DONE (R-98), both confirmed in R-90–R-101 PR
4. C-1 F-04 — finance.py expenditure tracker (Stage C start)
5. Submit Anthropic Claude $1,200 OSS grant application

## Version History

| Version | Date | Summary |
|---------|------|---------|
| v12.2.0 | 2026-06-01 | Public release, EWS creds to .env, .gitignore, .env.example, MIT, README |
| v12.1.0 | 2026-05-23 | 10-fix external audit sweep, router snake_case regression, guardian mypy |
| v12.0.0 | 2026-05-22 | Agent timeout, FastAPI rate limiting, ABShadowTester, 29 bug fixes |

---

*Last updated: 2026-06-05 — Blueprint updated, Space Instructions rewritten (snake_case enforcement, nina_sync.sh correction)*
