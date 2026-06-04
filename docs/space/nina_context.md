---
# NINA Context — Attach to every new Perplexity/Claude thread about NINA
# Version: 12.2 | Updated: 2026-06-04 | Stage: A✅ B(partial) C(queued)
---

## Owner Profile
- **Name:** M. Baizid Alam — AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **Personal email:** onlybony@gmail.com | **Work:** alam.b@basicbanklimited.com | Shared: basicid@basicbanklimited.com
- **LinkedIn:** linkedin.com/in/mba2009 | **GitHub:** github.com/aibony
- **Background:** 16 yrs banking — SWIFT/MT103/MT202/MT700, LC, BG, BB compliance, ISO 27001 Lead Auditor, BSc Engg + MBA
- **Language:** English and Bangla — match the register used
- **Style:** Direct, peer-level, no fluff. Flag risks first. Concise only.
- **Domains:** SWIFT, MT103, LC, BG, Bangladesh Bank compliance, ISO 27001

## What NINA Is
Local-first autonomous AI operator — not a chatbot. Runs 24/7 on owner's laptop in Dhaka.
Acts inside the real environment: reads BASIC Bank Exchange mailbox (EWS/NTLM), runs shell commands,
monitors markets, tracks expenses, pushes proactive Telegram alerts, self-upgrades with human approval.
Never sends sensitive/banking data to cloud providers.

**One-line test for every feature:** "Does this make NINA more like an extension of me, or just more like a chatbot?"
If it passes, build it. If not, defer it.

**Repo:** github.com/aibony/nina | Public, MIT, v12.2 released 2026-06-01
**Portfolio:** aibony.github.io | **Grant target:** Anthropic Claude $1,200 OSS grant

## Environment
- **Machine:** ASUS VivoBook X530FN | Ubuntu 26.04 LTS | Python 3.14.4 | User: aibony
- **GPU:** MX150 2GB VRAM | **RAM:** 16GB
- **Repo:** ~/nina/ | **Venv:** ~/nina/venv
- **Service:** systemd nina.service (Restart=always, depends on ollama.service)
- **Local models (Ollama):** qwen2.5:1.5b (LOCALFAST), qwen2.5:7b (LOCALHEAVY), nomic-embed-text (embeddings)
- **EWS:** webmail.basicbanklimited.com | Auth: NTLM | Domain: basic.bank

## Quick Commands

    # Start / Stop / Restart
    cd ~/nina && ./guardian          # Recommended — full health check + start
    sudo systemctl start nina        # Direct systemd
    sudo systemctl stop nina
    sudo systemctl restart nina
    sudo systemctl status nina

    # Logs
    journalctl -u nina -f            # Live
    journalctl -u nina -n 50         # Last 50 lines
    cat ~/nina/nina_update_log.md    # Change history
    cat ~/nina/nina_problem_log.md   # Bug/fix history

    # Guardian (MUST run before AND after every patch)
    cd ~/nina && ./guardian

    # Git workflow
    git status
    git add <specific files>         # NEVER git add .
    git commit -m "type: description (ID)"
    git push origin main
    # Never commit: .env, data/memory, logs, *.bak, *.save, *.fix

## .env Key Variables

    TELEGRAM_BOT_TOKEN=
    AUTHORIZED_USER_ID=
    GROQ_API_KEY=          # Free tier — recommended default
    GEMINI_API_KEY=
    OPENAI_API_KEY=        # Paid — use sparingly
    EWS_USERNAME=          # BASIC Bank Exchange
    EWS_PASSWORD=          # SET THIS → activates email triage, morning report, urgency nudge. ZERO code required.
    EWS_MY_EMAIL=
    EWS_SHARED_EMAIL=
    RAM_GUARD_GB=
    IDLE_AUTO_APPROVE=
    API_SECRET_KEY=

## Provider Architecture (17 providers)
- **TIER 1 keyless:** POLLINATIONS, CHUTES, HF_PUBLIC
- **TIER 2 keyed:** CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini), ONEBRAIN
- **TIER 3:** OPENROUTER
- **LOCAL:** LOCALFAST (qwen2.5:1.5b), LOCALHEAVY (qwen2.5:7b)
- **Priority (free first):** Groq → Gemini → Cerebras → DeepSeek → Mistral → Together → Cohere → Fireworks → Perplexity → SambaNova → OpenRouter → xAI → OpenAI (paid, last resort)
- **Routing score:** success_rate×0.4 + (1−latency/5000)×0.4 + not_near_limit×0.2
- **CircuitBreaker:** CLOSED → OPEN (3 failures/5min) → HALF-OPEN (probe after 1800s)
- **Sensitive tasks:** LOCAL only, no exceptions
- **Task types:** sensitive, coding, research, math, multilingual, document, vision, quick, general
- **Step budgets:** quick=3, general=5, math=6, coding=8, document=8, research=10, sensitive=5

## Thermal Guard
| Tier | CPU | GPU | Action |
|------|-----|-----|--------|
| WARN | 80°C | 80°C | Log warning only |
| GUARD | 90°C | 85°C | Force LOCALFAST, ban LOCALHEAVY |
| CRITICAL | 95°C | 90°C | Abort agent loop, notify Telegram |
None = sensor readings silently skipped — no false aborts.

## Codebase Structure

    nina/
      core/
        nina.py          NinaOS orchestrator, startup/shutdown, morning report
        router.py        HybridRouter V4 — CircuitBreaker, composite scoring, parallel fan-out
        config.py        NinaConfig (Pydantic), RATE_LIMITS, load_config
        agent.py         AgentLoop — THINK→PLAN→ACT, thermal preflight, self-check pass
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
        providerhunter.py Auto-discovers new free AI provider endpoints
        upgradepipeline.py Gated patch: scan→sandbox→diff→approve→deploy, 14 danger patterns
      interfaces/
        telegraminterface.py  Security gate, 20 commands, NLP, streaming, flood control
        api.py           STUB (0 lines) — deferred to Phase 2
      crons/
        manager.py       APScheduler — 13 jobs: morning report, heartbeat, thermal, backups, etc.
      guardianengine.py  Forensic engine — AST scan, baseline drift, service health
      healthcheck.py     Test suite — import isolation, structural regression
      idleloop.py        Idle upgrade proposal loop, 7-topic rotation, pings Telegram
      main.py            Entry point, asyncio event loop, SIGTERM/SIGINT shutdown
      data/memory/facts.json   Persistent key-value personal facts store (F-02 populated)
      logs/              8 rotating log files, 7-day retention
      .env               Secrets — NEVER commit, NEVER send to cloud
      guardian.sh        Shell verification script — run after EVERY patch

## Telegram Commands
| Command | Action |
|---------|--------|
| /status | RAM, VRAM, CPU, thermal, provider health |
| /router | Provider scores, latency, token counts |
| /logs | Last 20 lines nina.log |
| /reset | Clear session cache |
| /memory | Show facts.json |
| /email | Fetch BASIC Bank mailbox summary |
| /patch [url] | Submit upgrade patch for review |
| /approve | Deploy approved patch |
| /rollback | Restore last backup |

## Coding Conventions
- `task.task_type` not `task_type` alone
- `STEP_BUDGETS`, `DEFAULT_MAX_STEPS` imported from `core/router.py`
- All patches: `python3 -m py_compile file` then `./guardian` before declaring done
- router.log format: JSON-lines `{ts, provider, task_type, input_tokens, output_tokens, cost_usd, ttf_ms, total_ms, parallel, cached, status, error}`
- Tool protocol: `[TOOL:web] INPUT:query … [FINAL]answer` — text-based, fallback exists

## Rollback Commands

    cp ~/nina/upgrades/backups/backup_TIMESTAMP/core/memory.py ~/nina/core/memory.py
    sudo systemctl restart nina
    # Or named backup:
    cp ~/nina/upgrades/backups/core-cleanup-memory.py.bak ~/nina/core/memory.py

## Guardian Pass Criteria
1. venv active, Python 3.14, all required packages present
2. .env validation passed (TELEGRAM_CHAT_ID warning acceptable)
3. Syntax check — all tracked files OK
4. pyflakes — no issues
5. mypy — warnings non-blocking
6. nina.service active, no crash pattern
7. Telegram polling confirmed
8. APScheduler started — 13 jobs

## Guardian Notes
- Health score 5.8/10 is driven by stale journal signature matches — not live issues
- Blocker signatures (AttributeError, ConflictingIdError, BlockingIOError) are historical journal echoes
- Baseline will reset to PASS once a clean run clears the incident history
- mypy 22 advisory findings are non-blocking (core/config.py NinaConfig kwargs, tools/system.py)

## Development Policy (Summary — see nina_dev_policy.md for full rules)
1. One change per session. Never stack fixes.
2. Run `./guardian` before AND after every patch to core/, tools/, or interfaces/
3. Every patch needs a runtime proof — not just no import error
4. If Guardian shows a new BLOCKER after your patch → rollback first, investigate second
5. Log the ID, file, and outcome same day in nina_update_log.md + nina_problem_log.md
6. New capability = new tool file. Never add capability logic to core/nina.py
7. Protected files — extra caution: interfaces/telegraminterface.py, .env, core/router.py
8. Sensitive task = local model only. No exceptions.

## Phase 1 Status

### Stage A — Stop Active Failures ✅ COMPLETE (v12.2)
- R-01→R-78 — 65 issues resolved, crashes stopped

### Stage B — Make NINA Smarter (PARTIAL)
- B-1 F-01 Self-check pass in core/agent.py — ✅ DONE
- B-2 F-02 Personal context injection — ✅ DONE 2026-06-04
  - data/memory/facts.json populated (name, role, bank, language, timezone, domains, style, github, project)
  - core/memory.py patched — Owner block injected at top of build_context() before semantic recall
  - Rollback: upgrades/backups/memory.py.bak.20260604
- B-3 F-03 System prompt rewrite — remove duplicate `Available tools:` line in core/nina.py, add tone calibration — **NOT DONE**

### Stage C — New Capabilities (NOT STARTED)
- C-1 F-04 tools/finance.py — SQLite ledger, NLP entry, weekly summary, threshold alert
- C-2 F-05 tools/market.py — cron DSE/CSE, 2h polling 10:00–14:30 Dhaka, 1% threshold Telegram alert
- C-3 F-06 Reminder engine — data/reminders.json, heartbeat cron checks every 15min
- C-4 F-07 Email triage — structured sender/subject/received/urgency_flag output, keywords: LC, SWIFT, MT103, urgent, deadline, Bangladesh Bank
- C-5 F-08 /remember /recall — auto-inject recalled facts by topic

### Stage D — Hardening (parallel with C, one per session)
- S-01 SSRF fix — replace substring check with ipaddress module in tools/browser.py
- S-02 Async memory IO — wrapped in F-02 patch
- S-04 Model version override dict in NinaConfig — core/config.py

## Open Issues
| ID | File | Issue | Blocking? |
|----|------|-------|-----------|
| O-02 | core/nina.py | Duplicate `Available tools:` line in prompt | Degrades LLM |
| O-03 | tools/browser.py | SSRF substring guard — verify R-64 closed this | Security debt |
| O-06 | tools/shell.py | `cat` in ALLOWED_BASES — path traversal risk | CRITICAL — R-48 removed it, verify |

**Single most valuable unlock:** Set `EWS_PASSWORD` in `.env` → email triage, morning report email section, and urgency nudge all activate. Zero code required.

## Next Steps (Priority Order)
1. B-3 F-03 — System prompt rewrite, remove duplicate `Available tools:` line, add tone calibration
2. Set `EWS_PASSWORD` in `.env` — activate email features (zero code, instant unlock)
3. Verify O-06 (cat/shell) and O-03 (SSRF) are actually closed by R-48 and R-64
4. C-1 F-04 — finance.py expenditure tracker (Stage C start)
5. Submit Anthropic Claude $1,200 OSS grant application

## Version History
- v12.2.0 — 2026-06-01 — Public release, EWS creds to .env, .gitignore, .env.example, MIT, README
- v12.1.0 — 2026-05-23 — 10-fix external audit sweep, router snake_case regression, guardian mypy
- v12.0.0 — 2026-05-22 — Agent timeout, FastAPI rate limiting, ABShadowTester, 29 bug fixes
