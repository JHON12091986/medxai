# NINA v11 — STAGE 0 BLUEPRINT
### Version: 11.0.0 · Last updated: 2026-05-20 10:10 +0600
### Design source of truth. Not part of the assembled runtime prompt.
### Hardware baseline: i5 8th Gen · 16GB RAM · MX150 2GB VRAM · Ubuntu 26 · Dhaka UTC+6

---

## WHY v11 EXISTS

v10 closed the reactive/preventive gap from v9 — RAM preflight guards, parallel reservation, guaranteed memory-backup on reset, defined schedule resolution order, idle proposal persistence, provider spacing, and heartbeat dead-man escalation. All of those hold.

v11 closes the operational gaps that v10 left open: the routing score formula had an unbounded latency term that could drown out reliability; the rate limit table was missing 9 of the 16+ registered providers, leaving their spacing unenforced; the morning report had no error path when market data fetch failed; the agent loop used a single MAX_STEPS constant for all task types; the upgrade pipeline's dangerous-pattern check was undefined, creating a security specification gap; the authorized-user flood case was unhandled; the shell allowlist excluded two critical hardware diagnostics; disk pressure had no preflight guard despite write-heavy operations; and the FastAPI auth token had no generation or rotation guidance.

v11 keeps every strength of v10 and closes those gaps precisely.

---

## DESIGN PRINCIPLES

**P1 — Natural language over commands**
If a request can be understood safely through NLP, no slash command is needed. Commands exist only for protocol boundaries, explicit approvals, emergency stops, and destructive actions.

**P2 — One source of truth**
Commands defined once. Providers defined once. Safety rules defined once. Other stages reference these instead of duplicating them.

**P3 — Specify real behavior, not placeholders**
If the system exposes a report, status field, queue, or prompt variable, the actual content and data source must be defined here. No fake fields.

**P4 — Design for the real machine**
Target: 16GB RAM, modest CPU, 2GB VRAM. All model choices, concurrency rules, and scheduler behavior must respect this.

**P5 — Limits are first-class**
Rate limits, RAM limits, disk limits, and time budgets shape routing and autonomy before failure, not after.

**P6 — Shortest correct implementation**
Prefer simple async Python that can be debugged under pressure.

**P7 — Security before convenience**
Sensitive banking content stays local. Keys never echoed. Protected files guarded. Approval gates mandatory. Dangerous code patterns explicitly blocked before sandbox execution.

**P8 — Recoverability over cleverness**
Any destructive action must create a recovery path first. Useful autonomous output must be preserved, not silently discarded.

**P9 — Preventive ops over reactive ops**
Prefer preflight guards, spacing, and health checks over post-failure alerts.

**P10 — Observable by default**
Every non-trivial state transition, routing decision, and autonomous action must produce a structured log entry. Silent state changes are bugs.

---

## CANONICAL MODEL DECISIONS

```
LOCAL_FAST   : qwen2.5:1.5b Q4_K_M
               RAM: ~1.0GB | GPU layers: ~28 (fully GPU-resident on MX150)
               Use: quick replies, decomposition, aggregation, intent parsing

LOCAL_HEAVY  : qwen2.5:7b Q4_K_M
               RAM: ~4.3GB | GPU layers: ~10-12 (partial offload)
               Use: deeper reasoning, coding, sensitive banking analysis

LOCAL_EMBED  : nomic-embed-text
               Use: memory embeddings only

Expected local steady-state RAM: ~5.5GB to 6.2GB
Operational soft ceiling: 12GB
Preflight guard threshold: 10.5GB (before heavy autonomy)
Alert threshold: 11GB
Critical threshold: 12GB
```

---

## CANONICAL COMMAND SET (20 commands only)

```
IDENTITY & CONTROL
  /start              Reset session and show help
  /reset              Destructive reinitialization with mandatory backup
  /abort              Kill active agent loop immediately
  /help               Show commands and NLP examples

CORE TASKS
  /task <goal>        Explicit multi-step agent loop trigger
  /ask <question>     Single-turn, bypassing agent loop
  /email              Fetch and analyze both mailboxes
  /shell <command>    Allowlisted shell command only

MEMORY
  /remember <text>    Write to permanent memory
  /forget <key>       Delete one saved fact

UPGRADES
  /patch <file/url>   Submit a Python upgrade package
  /generate <f> <d>   AI-generate a module upgrade proposal
  /approve            Approve pending upgrade
  /reject             Reject pending upgrade
  /rollback <file>    Restore a Python backup

PROVIDERS
  /addkey <P> <key>   Store key and activate provider
  /addkey list        Show provider status and signup links

STATUS
  /status             Full health snapshot
  /router             Provider routing table and limits
  /logs               Last 50 lines of nina.log
```

NLP handles (no command needed):
```
"check my email"              → email fetch
"hunt for new providers"      → provider hunt
"what providers am I missing" → provider status
"show upgrade history"        → upgrade log
"diagnose errors"             → auto-diagnose
"run the morning report now"  → run scheduled job
"how much did I spend today"  → cost report
"roll back web.py"            → rollback
"set EWS emails to 25"        → config update
"show idle queue"             → idle proposal list
"what's using the most RAM"   → status
"clear my session"            → clear session
```

---

## SYSTEM PROMPT SOURCE TEXT

Injected into every LLM request at runtime.

```
You are NINA — Neural Intelligent Network Assistant.
You run continuously on a local laptop in Dhaka, Bangladesh for M. Baizid Alam,
Senior Banker at BASIC Bank.

You are a disciplined peer operator — direct, calm, professional, and useful.
You are context-aware: you know the current time, the user's banking role,
and the active memory context. You adapt tone to task urgency.
You do not perform for approval. You do not over-explain routine steps.

Current date and time: {current_datetime_dhaka}

Your behavior:
- Be concise by default; expand only when depth is genuinely useful.
- For non-trivial tasks, reason step by step before finalizing.
- State uncertainty plainly. Never present guesses as facts.
- Proactively flag operational, security, financial, or technical risk.
- Prefer the simplest correct path over unnecessary complexity.
- When responding in Bangla or mixed Bangla-English, match the user's language register.

Your expertise:
- SWIFT, ISO 20022, MT103, MT202, MT700, trade finance, LC workflows,
  BGs, discrepancies, amendments, banking operations, Bangladesh Bank compliance.
- Python 3.11+, asyncio, Linux, systemd, Ollama, local inference routing.
- Exchange EWS, NTLM authentication, mailbox triage, and local automation.
- Running AI systems safely on constrained consumer hardware.

Hard constraints:
- Banking data, account numbers, SWIFT references, secrets, and credentials
  must never be sent to any cloud provider.
- If a task is sensitive or ambiguous, prefer local execution.
- Never invent provider status, market data, or scheduler content.
- Never bypass an approval gate for code deployment.
- Never hide failure; report it plainly and suggest the next best action.

Current context:
{memory_context}
```

`{memory_context}` is generated at runtime by `MemorySystem.build_context()`.
`{current_datetime_dhaka}` is injected at request build time as ISO 8601 in UTC+6.

---

## MORNING REPORT CONTENT

Scheduled daily at 09:00 Dhaka. Every field must have a real data source.

```
🌅 NINA Morning Report — {date} {day_of_week}

MARKET
  USD/BDT   : {usd_bdt_rate}
  SOFR      : {sofr_rate}
  BB Repo   : {bb_repo_rate}

EMAIL SUMMARY
  Personal  : {personal_unread} unread {personal_urgent_flag}
  BasicID   : {shared_unread} unread {shared_urgent_flag}
  {top_urgent_subjects_if_any}

SCHEDULE TODAY
  {today_schedule_lines}

SYSTEM
  Uptime        : {uptime}
  RAM           : {ram_used}GB / 16GB
  Disk          : {disk_used_pct}%
  Providers     : {healthy}/{total} healthy
  Cost yesterday: ${cost_yesterday:.4f}

{urgent_preview_if_any}
```

Data sources:
- Market: web search or Perplexity cache, TTL 1 hour
- Email: EWS summary fetch
- System: psutil + router snapshot
- Cost: router daily token/cost tracker
- Schedule Today — resolved in this exact order:
  1. data/schedule_today.json if present (key = YYYY-MM-DD)
  2. same-day scheduler jobs from data/jobs.sqlite
  3. reserved keys in memory/facts.json: today_schedule, meeting_today, deadline_today
  4. mandatory fallback if all empty: "No scheduled items recorded."

Blank schedule output is forbidden.

### Market data failure handling
If web search or Perplexity cache fails for any market field:
- Show: "Unavailable (retry at next report)" for that field only
- Do not block or delay report delivery
- Log failure to logs/error.log with tag: morning_report_market_fetch_failed
- Other report sections render normally

---

## RATE LIMIT POLICY

Rate limits shape routing before dispatch, not after failure.

```python
RATE_LIMITS = {
    # Tier 1 — keyless
    "GROQ":         {"rpm": 30,  "tpd": 14_400,    "rpd": 14_400, "min_spacing_s": 2},
    "CEREBRAS":     {"rpm": 30,  "tpd": 100_000,   "rpd": None,   "min_spacing_s": 2},
    "GEMINI":       {"rpm": 15,  "tpd": 1_500_000, "rpd": 1_500,  "min_spacing_s": 4},
    "MISTRAL":      {"rpm": 1,   "tpd": None,       "rpd": None,  "min_spacing_s": 61},
    "POLLINATIONS": {"rpm": 5,   "tpd": None,       "rpd": None,  "min_spacing_s": 12},
    "CHUTES":       {"rpm": 3,   "tpd": None,       "rpd": None,  "min_spacing_s": 20},
    "HF_PUBLIC":    {"rpm": 10,  "tpd": None,       "rpd": None,  "min_spacing_s": 6},

    # Tier 2 — free key (v11: previously missing, now defined)
    "DEEPSEEK":     {"rpm": 60,  "tpd": 500_000,   "rpd": None,   "min_spacing_s": 1},
    "TOGETHER":     {"rpm": 60,  "tpd": None,       "rpd": None,  "min_spacing_s": 1},
    "COHERE":       {"rpm": 20,  "tpd": None,       "rpd": 1_000, "min_spacing_s": 3},
    "FIREWORKS":    {"rpm": 30,  "tpd": None,       "rpd": None,  "min_spacing_s": 2},
    "XAI":          {"rpm": 60,  "tpd": None,       "rpd": None,  "min_spacing_s": 1},
    "SAMBANOVA":    {"rpm": 30,  "tpd": 100_000,   "rpd": None,   "min_spacing_s": 2},
    "HYPERBOLIC":   {"rpm": 60,  "tpd": None,       "rpd": None,  "min_spacing_s": 1},
    "NOVITA":       {"rpm": 30,  "tpd": None,       "rpd": None,  "min_spacing_s": 2},
    "PERPLEXITY":   {"rpm": 50,  "tpd": None,       "rpd": None,  "min_spacing_s": 2},
    "OPENAI":       {"rpm": 500, "tpd": None,       "rpd": None,  "min_spacing_s": 0},
    "ONEBRAIN":     {"rpm": 20,  "tpd": None,       "rpd": None,  "min_spacing_s": 3},
}
```

Rules:
- At 80% of known daily limit: deprioritize
- At 100%: mark exhausted until midnight UTC
- Always enforce min_spacing_s before dispatch
- In parallel mode: reserve slots before asyncio.gather() starts
- After parallel completion: reconcile counters immediately before another fan-out
- Providers absent from RATE_LIMITS use conservative defaults: rpm=10, min_spacing_s=6

---

## ROUTING SCORE FORMULA

The composite routing score must use a normalized latency term to prevent unbounded values:

```
score = (success_rate × 0.4)
      + (1 - clamp(avg_latency_ms / 5000, 0.0, 1.0)) × 0.4
      + (not near_limit × 0.2)
```

`clamp(avg_latency_ms / 5000, 0, 1)` maps 0ms→0.0 (best) and 5000ms+→1.0 (worst),
contributing 0.4 at best and 0.0 at worst. This prevents a 1ms provider from achieving
an infinite composite score and keeps all three terms on the same 0–1 scale.

---

## STEP BUDGET BY TASK TYPE

The agent loop must use a per-task-type step budget rather than a single global constant:

```python
STEP_BUDGETS = {
    "quick":       3,
    "general":     5,
    "multilingual":5,
    "math":        6,
    "coding":      8,
    "document":    8,
    "research":   10,
    "sensitive":   5,   # local-only; conservative
}
# Fallback for unknown task types
DEFAULT_MAX_STEPS = 5
```

`max_steps = STEP_BUDGETS.get(task_type, DEFAULT_MAX_STEPS)`

---

## UPGRADE PIPELINE DANGEROUS PATTERN BLOCKLIST

The static analysis stage must scan uploaded .py files for the following patterns before sandbox execution. Any match rejects the upgrade with a specific message.

```python
DANGEROUS_PATTERNS = [
    # Shell injection
    (r"os\.system\s*\(", "os.system() — use subprocess with shell=False"),
    (r"subprocess\.(Popen|call|run).*shell\s*=\s*True", "subprocess shell=True — remove shell=True"),

    # Dynamic code execution
    (r"\beval\s*\((?!.*repr)", "eval() on non-literal — forbidden"),
    (r"\bexec\s*\((?!.*compile)", "exec() on non-literal — forbidden"),
    (r"__import__\s*\(", "__import__() dynamic import — forbidden"),
    (r"importlib\.import_module\s*\([^'\"]", "importlib dynamic import — forbidden"),

    # File system escape
    (r"open\s*\(.*\.\./", "path traversal in open() — workspace only"),
    (r"pathlib\.Path\s*\(.*\.\./", "path traversal via pathlib — workspace only"),

    # Network to unapproved hosts
    (r"socket\.connect\s*\(", "raw socket.connect() — forbidden"),
    (r"requests\.get\s*\(['\"](?!https?://)", "requests to non-http target — forbidden"),

    # Protected file modification
    (r"['\"]core/(nina|router|config)\.py['\"]", "write to protected core/ file — forbidden"),
    (r"['\"]interfaces/telegram_interface\.py['\"]", "write to protected interface — forbidden"),
    (r"['\"]\.env['\"].*[wW]", "write access to .env — forbidden"),
    (r"['\"]nina\.service['\"].*[wW]", "write to systemd unit — forbidden"),
]
```

Each match produces: `❌ Upgrade rejected: {reason}. Fix and resubmit.`
The file is not entered into sandbox. The rejection is logged to logs/upgrade.log.

---

## SAFETY OPERATIONS RULES

**RAM preflight guard**
Before starting agent/loop.py:
- if RAM > ram_guard_gb (10.5GB): skip heavy autonomy
- downgrade to single-turn /ask path
- notify: "⚠️ RAM at {n}GB — running in lean mode (agent loop skipped)"

**Disk preflight guard**
Before any write-heavy operation (upgrade deploy, memory backup, workspace file write):
```python
disk_used_pct = psutil.disk_usage("/").percent
if disk_used_pct > 90:
    await notify_telegram(f"⚠️ Disk {disk_used_pct:.0f}% full — write skipped.")
    logger.warning(f"Write skipped: disk at {disk_used_pct:.0f}%", extra={"log": "error.log"})
    return
```

**Reset backup rule**
/reset must first:
1. snapshot memory/facts.json
2. export ChromaDB collection metadata
3. store both in upgrades/backups/memory_YYYYMMDDHHMMSS/
4. wipe and rebuild only after backup confirms success
5. report backup path in confirmation message

**Idle proposal persistence**
When an idle upgrade proposal expires without approval:
- move to data/idle_queue.json, state: expired_pending_review
- preserve summary, diff metadata, expired_at
- notify: "⏳ Upgrade for {filename} expired — saved to idle queue"

**Heartbeat dead-man**
Hourly heartbeat must also ping deadman_ping_url if configured.
External service alerts if no ping within 65 minutes.
Recommended service: healthchecks.io free tier.

**Authorized-user flood protection**
Even the authorized user is rate-limited to prevent accidental loops:
- Max 10 messages per 30-second window
- On breach: queue the message and reply "⏳ Slow down — {n} message(s) queued."
- Reset counter on window expiry
- Log flood events to logs/security.log with tag: authorized_user_flood

---

## FASTAPI AUTH TOKEN

API_SECRET_KEY in .env — generate once on first run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste output as API_SECRET_KEY in .env. Rotate manually only (never auto-rotate —
this would invalidate external monitoring integrations). Never log the token value.

---

## STAGE MAP

```
STAGE 0  [THIS FILE]   Blueprint, principles, models, commands, system prompt,
                       morning report (with market error path), rate limits
                       (all 16+ providers), routing score formula, step budgets,
                       dangerous pattern blocklist, safety rules, API auth,
                       stage map, cross-cutting rules.

STAGE 1  Core          NinaConfig, .env, directory structure, NinaOS,
                       startup sequence, startup message, shutdown.

STAGE 2  Router V4     Provider registry, task classifier, ProviderHealth,
                       routing priority (normalized score), sequential, parallel,
                       idle monitor, cache, cost tracking, get_status().

STAGE 3  Telegram      Command handler, NLP fallback, security gate
                       (with flood protection), /help output, streaming,
                       reset UX, error format.

STAGE 4  Tools         shell (updated allowlist), web, browser, file,
                       system (disk guard), email, gpu_tuner.

STAGE 5  Agent+Memory  Agent loop (variable step budget), MemorySystem,
                       Scheduler (8 jobs), morning report implementation,
                       heartbeat with dead-man ping.

STAGE 6  Upgrades+     UpgradePipeline (with defined pattern blocklist),
         Providers     idle loop persistence, ConfigHotReload,
                       ABShadowTester, CapabilityRegistry, ProviderHunter,
                       /addkey flow, OpenRouter free model scanner.

STAGE 7  Ops           Logging (8 files), FastAPI (with auth token gen),
                       systemd, requirements.txt, safety boundaries,
                       final directive.
```

---

## CROSS-CUTTING RULES

```
1.  asyncio everywhere unless a library forces otherwise
2.  pydantic for all config validation — fail at startup on bad config
3.  try/except on every external call — catch, log, continue, never crash
4.  all paths via pathlib.Path — no hardcoded strings
5.  never log secret values — only key names or masked status
6.  stream=True on every LLM call
7.  protected files: core/nina.py, core/router.py, core/config.py,
    interfaces/telegram_interface.py, .env, nina.service
8.  upgrade pipeline writable scope: tools/, crons/, agent/, tests/
9.  browser automation always uses --disable-gpu --no-sandbox
10. GPU reserved for Ollama only
11. destructive actions require backup or rollback path first
12. no status line may show guessed or undefined data
13. autonomous work must preserve useful outputs instead of silently discarding them
14. provider dispatch must honor both health state and per-provider spacing
15. every non-trivial state transition produces a structured log entry (P10)
16. routing score must use normalized latency term (see ROUTING SCORE FORMULA)
17. dangerous patterns must be scanned before sandbox execution (see BLOCKLIST)
18. disk must be checked before any write-heavy operation (see DISK PREFLIGHT GUARD)
```

---

## DELIBERATE EXCLUSIONS

Still excluded (they belong in code, not the spec):
- Full implementation code for every function
- Synthetic test fixtures
- Repeated command tables across stages
- Duplicated provider registries
- Verbose A/B scoring formulas
