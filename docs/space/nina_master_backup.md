# NINA Master Reference Backup — 2026-06-07

> **Snapshot base:** `nina_latest.md` generated `2026-06-07 13:19:17`
> **Branch:** `main` | **Python:** 3.14.4 | **OS:** Ubuntu 26.04 LTS
> **Owner:** M. Baizid Alam, AGM, BASIC Bank Limited, Dhaka, Bangladesh
> **Deployment:** ASUS VivoBook X530FN | Service: `systemd nina.service`
> **Repo:** `github.com/aibony/nina`

---

## 1. Session Health Check (Current State)

| Metric | Value |
|---|---|
| **BLOCKER** | 0 |
| **WARN** | 0 |
| **DEBT** | 0 |
| **FEATURE_PENDING** | 11 |
| **Guardian Status** | PASS (clean) |
| **Open PRs** | 0 |
| **`juleslock.txt`** | CLEARED |
| **`nina.service`** | active |
| **agy Claude quota** | SPENT (resets ~127h from session) |
| **Jules daily quota** | 100 tasks/day (rolling 24h) |

### Today's Merged PRs (2026-06-07)

| PR | Task ID | What Was Added | Key Files |
|---|---|---|---|
| 13 | R-82 | `Makefile` dev helpers | `Makefile` |
| 14 | D-24 | Provider architecture docs | `docs/space/nina_context.md` |
| 15 | R-81 | Smoke tests for tools | `tests/test_tools_smoke.py`, `pytest.ini` |
| 16 | F-08 | KB core primitives | `core/memory.py` |
| 17 | R-80 | Structured `extra=` logging (12 files) | tools/crons |
| 18 | R-79 | `IdleProposalLoop` IMPACT briefs | `idleloop.py` |
| 19 | F-07 | Email triage refactor + compat wrapper | `tools/officemail.py` |
| 20 | F-06 | Proactive reminder engine | `core/nina.py`, `data/reminders.json` |
| 21 | F-05 | DSE/CSE market monitor | `tools/market.py`, `crons/manager.py` |
| 22 | F-04 | Expenditure tracker + tests | `tools/finance.py` |
| 23 | Bolt | `is_bangla` compiled regex (10× faster) | `core/agent.py` |
| 24 | Sentinel | `shell=True` → `shlex.split` / `shell=False` | `guardian_engine.py` |

---

## 2. Three-Tool Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  THE PARALLEL LOOP                         │
│                                                            │
│  1. Perplexity ─── diagnoses + writes precise spec        │
│         │                                                  │
│         ├──► Jules ─── async cloud VM ──► PR              │
│         │      (fire-and-forget, NO interaction)           │
│         │                                                  │
│         └──► agy ─── local executor ──► merge + deploy    │
│                (sync, single-file hotfixes in parallel)    │
│                                                            │
│  5. agy reviews Jules PR diff                             │
│  6. agy: pycompile + pyflakes → merge → .ninasync.sh      │
│  7. Perplexity reviews: attach fresh nina_latest.md        │
└────────────────────────────────────────────────────────────┘
```

### Tool Routing Table

| Tool | Model | Role | Execution | Reset |
|---|---|---|---|---|
| Perplexity Enterprise Pro | Claude Sonnet 4.6 Thinking | ARCHITECT / OVERWATCH | Active throughout | — |
| Google Jules | Gemini 3.1 Pro (built-in) | ASYNC CLOUD CODER | Fire-and-forget → PR | 100 tasks/24h |
| Antigravity CLI (`agy`) | Gemini 3.5 Flash Medium (default) | LOCAL MUSCLE | Sync executor, merge, deploy | ~5h rolling |

### agy Model Tiers

| Model | Budget | Use When |
|---|---|---|
| Gemini 3.5 Flash Medium | ~5h rolling | Default — always try first |
| Gemini 3.5 Flash High | ~5h rolling | Moderate complexity |
| Gemini 3.1 Pro High | ~5h rolling | High complexity local tasks |
| Claude Sonnet 4.6 Thinking | Weekly (~7 days) | Reserve — burns budget fast |
| Claude Opus 4.6 Thinking | Weekly (~7 days) | Last resort — same pool as Sonnet |

### agy Mandatory Rules

- **Always start every agy prompt with:** `"Use the permanent JSON approval setting — approve all steps without prompting for this task."`
- Never generate bash scripts or code — write plain-English prompts only
- Never write log entries, commits, or file edits directly — always instruct agy
- Sequential only — one task at a time, one file at a time
- agy performs **ALL** Jules PR merges — never auto-merge via GitHub UI
- Before merge: `python3 -m pycompile` + `pyflakes` on changed files + check `juleslock.txt`
- After merge: `.ninasync.sh` — no exceptions

### Jules Mandatory Rules

- `jules remote new --repo aibony/nina --task start --session "full task spec"`
- Fire-and-forget: submit and walk away — check GitHub for PR
- Jules reads `AGENTS.md` automatically — keep it updated
- Jules does **NOT** merge its own PRs — agy always does the merge
- Daily limit: 100 tasks (Pro)
- **Do NOT pause for confirmation** at any point in the Jules spec

---

## 3. Key Paths

| Item | Path |
|---|---|
| NINA repo | `~/nina` |
| venv activate | `source ~/nina/venv/bin/activate` |
| agy binary | `~/.local/bin/agy` |
| Service restart | `sudo systemctl restart nina.service` |
| Guardian run | `cd ~/nina && bash guardian.sh` |
| Post-session sync | `cd ~/nina && ./nina_sync.sh` |
| Export snapshot | `cd ~/nina && ./nina_docs_export.sh` |
| Space upload dir | `~/Downloads/nina_space_upload/` |
| Error register | `~/nina/docs/space/nina_error_register.md` |
| Canonical docs | `~/nina/docs/space/` only |
| Update log | `~/nina/nina_update_log.md` |
| Jules lock | `~/nina/juleslock.txt` |
| Workflow doc | `~/nina/WORKFLOW.md` |
| Exporter contract | `~/nina/docs/space/nina_exporter_contract.md` |

---

## 4. High-Risk Files (Strict Rules)

| File | Risk | Default Route |
|---|---|---|
| `interfaces/telegram_interface.py` | Security gate, user-facing | agy local only |
| `.env` | All secrets | NEVER cloud, NEVER commit |
| `core/router.py` | HybridRouter V4 | agy local only |
| `main.py` | Entry point, PID lock | agy local only |
| `guardian_engine.py` | Forensic engine | agy local only |
| `tools/shell.py` | Allowlist-gated shell | agy local only |

**Rule:** Jules can only touch these files if explicitly authorized in the task spec and they are **not** locked in `juleslock.txt`.

---

## 5. Core Architecture

### Module Map

| Module | File | Role |
|---|---|---|
| Orchestrator | `core/nina.py` | `NinaOS` — top-level coordinator |
| Router | `core/router.py` | `HybridRouter V4` — provider selection, circuit breaker |
| Agent | `core/agent.py` | `AgentLoop` — THINK→PLAN→ACT→OBSERVE→ADAPT (Stage 5) |
| Memory | `core/memory.py` | `MemorySystem` — conversation + facts + KB (ChromaDB) |
| Config | `core/config.py` | `NinaConfig` — Pydantic model, `.env` loading |
| Capabilities | `core/capabilities.py` | `CapabilityRegistry` |
| Hot Reload | `core/hotreload.py` | `ConfigHotReload` — watches `.env` every 60s |
| Telegram | `interfaces/telegram_interface.py` | Security gate, command handler, flood protection |
| Guardian | `guardian_engine.py` | Forensic health checks |
| Shell | `tools/shell.py` | Allowlist-gated shell execution |
| Finance | `tools/finance.py` | Expenditure tracker (F-04) |
| Market | `tools/market.py` | DSE/CSE monitor (F-05) |
| Officemail | `tools/officemail.py` | EWS email triage (F-07) |
| Upgrade Pipeline | `tools/upgrade_pipeline.py` | Pattern scan, sandbox, approve/reject |
| Crons | `crons/manager.py` | `TaskScheduler` — APScheduler jobs |
| Idle Loop | `idleloop.py` | `IdleUpgradeLoop` — IMPACT briefs |
| Entry Point | `main.py` | PID lock, asyncio bootstrap |

### Provider Routing Priority

```
Free first → Groq → Gemini → Cerebras → DeepSeek → Mistral →
Together → Cohere → Fireworks → Perplexity → SambaNova →
OpenRouter → xAI → OpenAI (paid — last resort)
```

**Tier 1 (Keyless):** POLLINATIONS, CHUTES, HFPUBLIC
**Tier 2 (Keyed):** CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini), ONEBRAIN
**Tier 3:** OPENROUTER
**Local:** LOCALFAST (qwen2.5-1.5b), LOCALHEAVY (qwen2.5-7b)

### Routing Score Algorithm

```
score = (success_rate × 0.4) + ((1 - latency/5000) × 0.4) + (not_near_limit × 0.2)
```

**Circuit Breaker:** CLOSED → OPEN (3 failures/5min) → HALF-OPEN (probe after 1800s)

---

## 6. Scheduled Jobs (crons/manager.py)

| Job ID | Trigger | Function |
|---|---|---|
| `morning_report` | Daily 09:00 Asia/Dhaka | Morning briefing |
| `heartbeat` | Every 1h | Service health ping |
| `cache_purge` | Daily 03:05 Asia/Dhaka | Cache cleanup |
| `cost_report` | Daily 23:00 Asia/Dhaka | Provider cost summary |
| `rate_limit_reset` | Daily 00:01 UTC | Provider daily counters reset |
| `idle_summary` | Every 30min | Idle session summary |
| `log_rotation` | Daily 04:00 Asia/Dhaka | Log cleanup |
| `provider_health` | Every 6h | Provider availability check |
| `provider_hunter` | Daily 02:00 Asia/Dhaka | New provider scan |
| `thermal_health` | Every 5min | CPU/GPU temperature guard |
| `memory_backup` | Daily 02:30 Asia/Dhaka | Memory system backup |
| `py_backup` | Daily 03:00 Asia/Dhaka | Python code backup |
| `reminder_check` | Every 15min | Proactive reminder engine (F-06) |
| `market_monitor` | 10:30–14:30 Asia/Dhaka | DSE/CSE alerts (F-05) |
| `expire_pending` | Every 15min | Upgrade pipeline expiry |

---

## 7. Configuration Reference (NinaConfig)

### Thermal Thresholds

| Key | Default | Description |
|---|---|---|
| `thermal_warn_cpu` | 80 | CPU warn % |
| `thermal_warn_gpu` | 80 | GPU warn % |
| `thermal_guard_cpu` | 90 | CPU throttle % |
| `thermal_guard_gpu` | 85 | GPU throttle % |
| `thermal_critical_cpu` | 95 | CPU critical % |
| `thermal_critical_gpu` | 90 | GPU critical % |

### Resource Limits

| Key | Default | Description |
|---|---|---|
| `max_ram_gb` | 12.0 | Max RAM before guard |
| `ram_guard_gb` | 10.5 | RAM guard threshold |
| `disk_guard_pct` | 90.0 | Disk usage guard % |

### Agent Behaviour

| Key | Default | Description |
|---|---|---|
| `idle_threshold_min` | 15 | Minutes idle before idle loop |
| `idle_report_min` | 30 | Minutes between idle reports |
| `idle_auto_approve` | False | Auto-approve idle upgrades |
| `session_max_turns` | 20 | Max agent turns per session |
| `agent_timeouts` | 300 | Agent timeout (seconds) |
| `flood_windows` | 30 | Flood protection window (seconds) |
| `flood_max_messages` | 10 | Max messages in flood window |
| `api_rate_limit_rpm` | 60 | API rate limit (req/min) |

### Hot-Reloadable Fields (no restart needed)

`EWS_MAX_EMAILS`, `EWS_KEYWORDS`, `IDLE_THRESHOLD_MIN`, `IDLE_REPORT_MIN`, `IDLE_AUTO_APPROVE`, `FLOOD_WINDOWS`, `FLOOD_MAX_MESSAGES`, `SESSION_MAX_TURNS`, `AGENT_TIMEOUTS`, `API_RATE_LIMIT_RPM`, `DEADMAN_PING_URL`, `LOG_LEVEL`, all `THERMAL_*` thresholds

---

## 8. Security Architecture

### Shell Allowlist (tools/shell.py)

```python
ALLOWED_BASES = {
    "df", "ls", "pwd", "whoami", "free", "ps", "uptime",
    "head", "tail", "grep", "find", "echo", "date", "ping",
    "curl", "wget", "python", "python3", "pip", "pip3",
    "git", "systemctl", "journalctl", "ollama", "nvidia-smi"
}
ALLOWED_SYSTEMCTL_SUBS = {"status", "start", "stop", "restart", "enable", "disable", "is-active"}
ALLOWED_OLLAMA_SUBS    = {"list", "show", "pull", "run", "stop", "ps", "serve"}
```

**Injection guard:** Blocks `;`, `|`, `&&`, `||`, `` ` ``, `$()`, `>`, `<` shell operators.

### guardian_engine.py — Security Fix Applied (PR 24 / Sentinel)

```python
# BEFORE (vulnerable — shell=True)
def run_cmd(cmd, timeout=30):
    r = subprocess.run(cmd, shell=True, ...)

# AFTER (secure — shell=False default)
def run_cmd(cmd, timeout=30, use_shell=False):
    args = shlex.split(cmd) if not use_shell else cmd
    r = subprocess.run(args, shell=use_shell, ...)
    # use_shell=True only for the healthcheck runner (uses cd && chaining)
```

### SSRF Guard (tools/browser.py)

Validates all URLs against `ipaddress` module — blocks private IP ranges, localhost, link-local addresses before any HTTP request.

### Telegram Security Gate

- Single `AUTHORIZED_USER_ID` check on every message
- Flood protection: 10 messages / 30-second window
- Secret masking: `mask_secrets()` helper on all outbound text
- `ParseMode` safe defaults to prevent parse errors leaking internals

---

## 9. Open Action Board

### Active FEATURE_PENDING Items

| ID | Severity | Component | Issue | File |
|---|---|---|---|---|
| F-01 | OPEN/PENDING | `core/agent.py` | Self-check pass for complex tasks | `core/agent.py` |
| F-04 | OPEN/PENDING | `tools/finance.py` | Expenditure tracker (code merged — register not updated) | `tools/finance.py` |
| F-05 | OPEN/PENDING | `tools/market.py` | DSE/CSE market monitor (dummy prices — real API needed) | `tools/market.py` |
| F-06 | OPEN/PENDING | `core/nina.py` | Proactive reminder engine (cron wired — data schema TBD) | `core/nina.py` |
| F-07 | OPEN/PENDING | `tools/officemail.py` | Email triage (EWS blocked — O-02 open) | `tools/officemail.py` |
| F-08 | OPEN/PENDING | `core/memory.py` | KB remember/recall (ChromaDB wired — Telegram cmd TBD) | `core/memory.py` |
| R-77 | OPEN/PENDING | `core/router.py` | `parallel_route` RAM guard crash | `core/router.py` |
| R-78 | OPEN/PENDING | `core/agent.py` | Tool grammar fragility — minimum viable guard | `core/agent.py` |
| config.missing_env.telegram_chat_id | OPEN | `core/config` | `TELEGRAM_CHAT_ID` missing from `.env` (non-blocking) | `.env` |
| feature.ews_blocked | OPEN | `tools/officemail` | EWS email feature blocked — O-02 | `tools/officemail.py` |
| feature.playwright_blocked | OPEN | `tools/browser` | Playwright browser tool blocked — O-01 | `tools/browser.py` |

### Priority Order (Next Tasks)

```
1. B-3  F-03  Response tone calibration  →  core/nina.py  SYSTEM_PROMPT_TEMPLATE
2. C-1  F-04  Wire finance tool to Telegram command + close register entry
3. C-2  F-05  Replace dummy prices with real DSE/CSE API (scraper or public feed)
4. C-3  F-06  Define data/reminders.json schema + test reminder_check cron
5. C-4  F-07  Unblock EWS or add mock fallback for testing
6. C-5  F-08  Add /remember and /recall Telegram commands
7. A-1  R-77  Fix parallel_route RAM guard crash
8. A-3  R-78  Tool grammar fragility guard
```

---

## 10. Phase Roadmap

### Stage A — Stability (COMPLETE)

All historical blockers, router attribute errors, startup errors, hot-reload regressions, SSRF guard, Telegram handler issues, logging duplication — all FIXED and confirmed clean by guardian.

### Stage B — Make NINA Smarter (PARTIAL)

- ✅ B-1 (F-01) Self-check pass in `core/agent.py`
- ✅ B-2 (F-02) Personal context injection in `core/memory.py` + `data/memory_facts.json`
- ⏳ **B-3 (F-03) Response tone calibration** — NEXT UP

### Stage C — Banking & Personal Tools (IN PROGRESS)

- ⏳ C-1 (F-04) Expenditure tracker — code merged, needs Telegram wiring + register close
- ⏳ C-2 (F-05) Market monitor — code merged, dummy prices → real API needed
- ⏳ C-3 (F-06) Reminder engine — cron wired, schema + testing needed
- ⏳ C-4 (F-07) Email triage — blocked on EWS access
- ⏳ C-5 (F-08) Knowledge base — ChromaDB wired, Telegram commands needed

---

## 11. ninasync.sh — What It Does (v5)

```
Step 0/8  Health check — naming convention scan, service status
Step 1/8  tgnotify — Telegram ping on sync start
Step 2/8  Guardian run
Step 3/8  Git status check
Step 4/8  Update log entry append (Python, not bash echo)
Step 5/8  Staging: git add docs/space/ + SPACEFILES
Step 6/8  Commit + push (skips if Jules PRs are open — D-12 guard)
Step 7/8  Doc coverage scan — all .md/.txt/.json vs SPACEFILES
Step 8/8  Compact exporter → ~/Downloads/nina_space_upload/nina_latest.md
```

### SPACEFILES Array (files exported to Perplexity Space)

```bash
SPACEFILES=(
  "AGENTS.md"
  "WORKFLOW.md"
  "docs/space/nina_error_register.md"
  "docs/space/nina_exporter_contract.md"
  "docs/space/nina_state.md"
)
```

---

## 12. Session Start / Close Checklists

### Session Start (Before ANY Work)

1. `cd nina && ./nina_sync.sh` — get fresh snapshot
2. Attach `exports/nina_latest.md` to Perplexity thread
3. Attach specific source files to be discussed
4. State task type: `bug | feature | doc | security | review`
5. `cat nina/juleslock.txt` — confirm no target files are locked

### Session Close (Mandatory Every Time)

1. `cd nina && ./nina_sync.sh` → produces `nina_code_backup_TIMESTAMP.md`
2. `cd nina && ./nina_docs_export.sh` → produces `nina_docs_backup_TIMESTAMP.md`
3. Upload `nina_docs_backup_*.md` to Perplexity Space manually
4. Verify `juleslock.txt` is cleared
5. Verify 0 open PRs: `gh pr list --state open`

---

## 13. Parallel Workflow — Branch & Worktree Model

### Branch Lanes

| Branch | Purpose |
|---|---|
| `main` | Production truth — merge, sync only |
| `agy/task-id-slug` | Local docs, shell, single-file hotfixes |
| `jules/task-id-slug` | Multi-file features, async PR builds |
| `review/id` | Isolated test/review/merge prep |

### Territory Rules

| Tool | Default Territory | Forbidden |
|---|---|---|
| agy | `docs/space/*.md`, `AGENTS.md`, `*.sh`, single-file hotfixes | Files claimed by Jules |
| Jules | `core/*.py`, `tools/*.py`, `interfaces/*.py`, `tests/*.py` | `.env`, secrets, lock-sensitive files |
| Both (sequential) | `requirements.txt`, `data/*.json` | Parallel edits |

### Worktree Pattern

```
~/nina/                     ← main (production)
~/nina.worktrees/agy-task-id/
~/nina.worktrees/jules-task-id/
```

All worktrees share: `~/nina/venv/bin/activate` — never create separate venvs.
Lock truth always at: `~/nina/juleslock.txt` — never local worktree copy.

### Stop Conditions

- Either tool needs a file already claimed by the other → **stop, re-plan**
- Merge conflict risk appears → **pause parallelism, integrate first**
- Never bypass review with direct overlapping edits to main

---

## 14. compact_exporter.py — Validation Gate

The exporter validates `nina_latest.md` against 7 required strings before accepting the output:

| String | Section It Validates |
|---|---|
| `SESSION START CHECKLIST` | Pre-session checklist present |
| `ARCHITECT / OVERWATCH` | Tool routing table present |
| `ASYNC CLOUD CODER` | Jules role present |
| `LOCAL MUSCLE` | agy role present |
| `agy as Merge Executor` | Merge executor rule present |
| `The Full Parallel Loop` | 7-step loop present |
| `FEATURE_PENDING` | Action board present |

If any string is missing, the export fails with an explicit error — prevents silent regressions in the context snapshot.

---

## 15. Failure Modes to Avoid

| Anti-Pattern | Why It Breaks |
|---|---|
| Blind editing — no source file attached | Perplexity cannot see actual code; hallucination risk |
| Routing urgent fixes through Jules PR pipeline | Jules is async; runtime fixes need agy (sync) |
| Using agy for broad multi-file refactors | agy is sequential — scoped single-file only |
| Starting work without checking `juleslock.txt` | Lock race condition — two tools editing same file |
| Stacking unrelated changes in one commit | Makes rollback impossible |
| Treating `nina_latest.md` as repo recovery | It is a context snapshot, NOT a git backup |
| Auto-merging Jules PRs via GitHub UI | Skips compile check and pyflakes gate |
| Using heredoc/bash echo for log entries | Corrupts log format — Python append only |

---

## 16. Appendix — Known Blocked Features

| Feature | Issue ID | Blocker | Workaround |
|---|---|---|---|
| EWS Email triage | O-02 | NTLM auth / network access | `tools/officemail.py` has compat wrapper ready |
| Playwright browser | O-01 | Playwright not installed | `tools/browser.py` fallback to `httpx` |
| `TELEGRAM_CHAT_ID` | config.missing | Not in `.env` | Non-blocking — bot still works via `AUTHORIZED_USER_ID` |

---

*Last validated: 2026-06-07 13:19 +06 | Entry 051 in nina_update_log.md | All 12 PRs merged, 0 open*
