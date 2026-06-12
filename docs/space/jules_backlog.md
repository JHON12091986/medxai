# NINA Jules Backlog — Unified Pipeline
> **Mission:** NINA is a personal autonomous AI agent — NOT a chatbot. She acts, she does not describe.
> **Location:** `~/nina/docs/space/jules_backlog.md`
> **Updated by:** ninaflash (Python append only — never bash echo, never manual edit)
> **Read by:** Perplexity via nina_latest.md Google Drive backup every session
> **Consumed by:** Jules (async PRs) + ninaflash (local merges only)
> **Last restructured:** 2026-06-07 — Agentic shift adopted. All new features serve the agent mission.

---

## How This File Works

```
Perplexity reads backlog each session
  → counts READY items by tier, checks BLOCKED promotions
  → generates Jules task spec for each READY item (up to 15 per batch)
  → you submit spec to Jules UI
  → ninaflash merges PR when Jules opens it — never auto-merge via GitHub UI
  → ninaflash updates status: READY → IN_PROGRESS → IN_PR → DONE
  → next session: Perplexity picks next READY batch
```

**Territory rule:** Perplexity will never spec two concurrent tasks that touch the same file.
**Batch size:** Up to 15 non-overlapping READY tasks per Jules batch.
**Daily budget:** 15 SCHED tasks + up to 75 backlog tasks = 90/100 daily limit. 10 reserved for emergencies.

---

## ID Namespaces

| Prefix | Format | Purpose |
|--------|--------|---------|
| `B-001` | B + 3-digit | Infrastructure backlog — routing, security, observability, tests |
| `AG-A` … `AG-J` | AG + group letter + 2-digit | Agentic pipeline — planning, task state, autonomous loops, verification |

---

## Status Definitions

| Status | Meaning |
|--------|---------|
| `READY` | Fully specced, no blockers — Perplexity submits to Jules immediately |
| `IN_PROGRESS` | Jules task submitted, PR not yet open |
| `IN_PR` | PR open, waiting for ninaflash review + merge |
| `BLOCKED` | Has unresolved dependency — do not pick up |
| `DONE` | Merged, deployed, verified by Guardian |
| `DEFERRED` | Valid but deprioritised — revisit next sprint |
| `NEEDS_SPEC` | Idea captured — Perplexity must write full spec before Jules submission |

---

## Priority Tiers

| Tier | Label | Description |
|------|-------|-------------|
| P0 | CRITICAL | Security, data loss, service down — fix before anything else |
| P1 | HIGH | Core functionality gaps, reliability, routing quality |
| P2 | MEDIUM | Observability, developer experience, test coverage |
| P3 | LOW | Polish, nice-to-have, future-proofing |
| AG1 | AGENTIC PHASE 1 | Agency core — planner, task state, loop upgrade, verifier |
| AG2 | AGENTIC PHASE 2 | Proactive intelligence — events, autonomous agents, outbound push |
| AG3 | AGENTIC PHASE 3 | Agentic test coverage — runs parallel with AG2 |

---

## ██ P0 — CRITICAL

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-001 | Sentinel: remove shell=True from run_cmd in guardianengine.py | `DONE` | guardianengine.py | — | PR #60 merged 2026-06-07 |
| B-002 | Wire model_overrides dict to .env hot-reload | `IN_PROGRESS` | core/router.py, core/config.py | — | model_overrides in NinaConfig but not wired to hot-reload |
| B-003 | Add timeout to all subprocess calls in compact_exporter.py | `DONE` | tools/compact_exporter.py | — | No timeout = potential hang / DoS risk |
| B-004 | Validate TELEGRAM_CHAT_ID exists before any send attempt | `IN_PROGRESS` | interfaces/telegraminterface.py | — | Silent failure if env var missing; non-blocking open item |

---

## ██ P1 — HIGH

| B-048 | Auto-close stale Jules sessions (>24h blocked) | `IN_PROGRESS` | TBD | — | Auto-ingested via Goal Intake |


| B-047 | Build a NinaGate routing telemetry dashboard | `IN_PROGRESS` | TBD | — | Auto-ingested via Goal Intake |


| B-046 | Implement conflict-skip and error register logging | `IN_PROGRESS` | TBD | — | Auto-ingested via Goal Intake |


| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-005 | F-09 ModelDiscoveryService — build tools/model_discovery.py | `DONE` | tools/model_discovery.py, core/router.py, crons/manager.py | — | PR #25 merged 2026-06-07 |
| B-006 | F-09 Part 2 — wire ModelDiscovery into router._ordered_providers() | `DONE` | core/router.py | B-005 | ninaflash only — high-risk file |
| B-007 | F-09 Part 3 — seed data/model_cache.json with all 16 providers | `DONE` | data/model_cache.json | B-005 | Jules can do this |
| B-008 | Add circuit breaker state persistence to data/circuit_state.json | `DONE` | core/router.py, data/ | — | Currently in-memory — lost on restart. ninaflash only |
| B-009 | Add rate limiting to Telegram command handler | `IN_PROGRESS` | interfaces/telegraminterface.py | — | ninaflash only — high-risk file |
| B-010 | Add input length validation to all Telegram command parsers | `IN_PROGRESS` | interfaces/telegraminterface.py | — | ninaflash only — high-risk file |
| B-011 | Guardian engine: add file integrity check on startup | `IN_PROGRESS` | guardianengine.py | — | SIGNATURES dict exists but startup check is passive. ninaflash only |
| B-012 | Add structured JSON logging to router.py for provider selection events | `IN_PROGRESS` | core/router.py | — | Plain text logs hard to parse for metrics. ninaflash only |
| B-013 | healthcheck.py: replace bare except with typed exception handling | `DONE` | healthcheck.py | — | Bare except swallows real errors |
| B-014 | Add startup banner to main.py showing active providers + model strings | `IN_PROGRESS` | main.py | B-002 | Needs model_overrides wired first. ninaflash only |
| B-015 | crons/manager.py: add job execution metrics (duration, last_success, fail_count) | `DONE` | crons/manager.py | — | No visibility into cron job health |
| R-77 | Fix parallel_route RAM guard crash | `IN_PROGRESS` | core/router.py | — | A-1 from action board. ninaflash only |
| R-78 | Fix tool grammar fragility — minimum viable guard | `DONE` | core/agent.py | — | A-3 from action board; Jules session 230224707076942630 |

---

## ██ P2 — MEDIUM

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-016 | Write tests for tools/shell.py — full blocklist and allowlist coverage | `DONE` | tests/test_shell.py | — | Most critical security tool has zero tests; Jules session 15759165614254551433 |
| B-017 | Write tests for core/router.py — provider ordering, circuit breaker, fallback | `DONE` | tests/test_router.py | — | Jules session 9354379735932974598 |
| B-018 | Write tests for tools/browser.py — SSRF guard, URL validation | `DONE` | tests/test_browser.py | — | Jules session 9340521117119167710 |
| B-019 | Write tests for guardianengine.py — SIGNATURES check, run_cmd | `DONE` | tests/test_guardian.py | — | High-risk file needs test coverage; Jules session 13016195312630697079 |
| B-020 | Write tests for tools/model_discovery.py | `DONE` | tests/test_model_discovery.py | B-005 | Unblock now — B-005 is DONE |
| B-021 | Add prometheus-style metrics endpoint to healthcheck.py | `DONE` | healthcheck.py | — | Enables external monitoring; Jules session 4745946253740770652 |
| B-022 | tools/compact_exporter.py: add progress logging for long exports | `DONE` | tools/compact_exporter.py | — | Silent during long runs; Jules session 7514279750845525195 |
| B-023 | Add AGENTS.md section: tracker update protocol for Jules tasks | `DONE` | AGENTS.md | — | Jules needs instructions to update task tracker after each run; Jules session 15026902744619615986 |
| B-024 | Add AGENTS.md section: backlog update protocol | `DONE` | AGENTS.md | — | 2026-06-07 |
| B-025 | crons/manager.py: add graceful shutdown handler (SIGTERM) | `DONE` | crons/manager.py | — | No clean shutdown on systemd stop; Jules session 5406292542431629720 |
| B-026 | Add retry with exponential backoff to provider API calls | `IN_PROGRESS` | core/router.py | — | Current retry is basic — no backoff. ninaflash only |
| B-027 | tools/gputuner.py: add fallback when nvidia-smi not available | `DONE` | tools/gputuner.py | — | Crashes on non-GPU systems; Jules session 18284106294453230200 |
| B-028 | Add .env validation on startup — warn on missing required keys | `IN_PR` (partial — config.py done) | main.py, core/config.py | — | Silent failure on missing env vars. main.py → ninaflash only |
| B-029 | Write integration test: full request through router → provider → response | `DONE` | tests/test_integration.py | — | No end-to-end test exists; Jules session 7992182378283234865 |
| B-030 | Add request ID to all log lines for traceability | `IN_PROGRESS` | core/router.py, main.py | — | Hard to trace multi-step requests. ninaflash only |

---

## ██ P3 — LOW / POLISH

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-031 | Add provider latency histogram to router metrics | `IN_PROGRESS` | core/router.py | B-012 | Needs structured logging first. ninaflash only |
| B-032 | tools/compact_exporter.py: add --dry-run flag | `DONE` | tools/compact_exporter.py | — | Jules session 16016744403096643329 |
| B-033 | Telegram: /status command — shows provider health summary | `IN_PROGRESS` | interfaces/telegraminterface.py | — | ninaflash only |
| B-034 | Telegram: /models command — shows current model per provider | `IN_PROGRESS` | interfaces/telegraminterface.py | B-005 | ninaflash only |
| B-035 | Telegram: /backlog command — shows top 5 READY items | `IN_PROGRESS` | interfaces/telegraminterface.py | — | ninaflash only |
| B-036 | Telegram: /errors command — shows open error register items | `IN_PROGRESS` | interfaces/telegraminterface.py | — | ninaflash only |
| B-037 | docs/space: add nina_architecture_diagram.md with ASCII diagrams | `DONE` | docs/space/nina_architecture_diagram.md | — | No visual architecture reference exists; Jules session 2468954092544028080 |
| B-038 | Add per-provider cost tracking to router.py | `NEEDS_SPEC` | core/router.py | B-012 | ninaflash only |
| B-039 | Add response caching layer for identical prompts (TTL 60s) | `DONE` | core/router.py | — | Persistent cache implemented by Gemini CLI 2026-06-11 |
| B-040 | Write CONTRIBUTING.md | `DONE` | CONTRIBUTING.md | — | Jules session 1218304308318697501 |

---

## ██ NEEDS_SPEC — Ideas Awaiting Design

| ID | Title | Notes |
|----|-------|-------|
| B-041 | DSE/Bangladesh financial data integration (F-05) | Needs real DSE API endpoint research first |
| B-042 | Telegram inline keyboard for common commands (F-08) | Needs UX design pass |
| B-043 | Multi-modal support: image input routing | Provider capability matrix needed |
| B-044 | Web dashboard for NINA status (read-only) | `DONE` |
| B-045 | Conversation memory persistence across sessions | Storage design needed |

---

---

# ══════════════════════════════════════
# ██  AGENTIC PIPELINE  ██
# ══════════════════════════════════════
#
# Goal: Transform NINA from reactive chatbot to true autonomous agent.
#
# Rule: ALL AG items are NEEDS_SPEC until Perplexity writes a full Jules spec.
# Rule: AG1 must be fully merged + Guardian stable before AG2 begins.
# Rule: High-risk files (main.py, router.py, telegraminterface.py,
#        guardianengine.py, shell.py, .env) — ninaflash only, never Jules.
# Rule: After every Jules AG merge, ninaflash runs ./nina_sync.sh — no exceptions.
# Rule: Check juleslock.txt before starting any AG task.
#
# Perplexity: when all P0+P1 items are DONE, promote AG-A and AG-B
# to READY and write their specs as the next Jules batch.

---

## ██ AG1 — AGENTIC PHASE 1: Agency Core
_These four groups must be built and merged before any AG2 work begins._
_Strict build order: AG-B → AG-A → AG-C → AG-D_

---

### AG-A — Planning Layer
_New file: `core/planner.py`_
_Dependency: AG-B-01 and AG-B-02 must be DONE first_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-A-01 | `core/planner.py` | Create GoalDecomposer class — accepts natural language goal, returns ordered list of tool-call steps with declared dependencies | `NEEDS_SPEC` | AG-B-01 |
| AG-A-02 | `core/planner.py` | Implement step dependency graph — steps declare which prior steps must complete before they can start | `NEEDS_SPEC` | AG-A-01 |
| AG-A-03 | `core/planner.py` + `core/capabilities.py` | Add plan validation — verify each step's required tool exists in CapabilityRegistry before execution begins | `NEEDS_SPEC` | AG-A-01 |
| AG-A-04 | `core/planner.py` | Add plan serialization — save/load active plans to/from data/plans/ as JSON so plans survive service restarts | `NEEDS_SPEC` | AG-B-03 |
| AG-A-05 | `core/planner.py` | Add plan branching — if step A fails, planner executes defined alternative step B (if-else planning) | `NEEDS_SPEC` | AG-A-02 |
| AG-A-06 | `data/plans/templates/` | Add plan templates — pre-built JSON templates for: market_check, expense_log, reminder_set | `DONE` | AG-A-01 |
| AG-A-07 | `core/planner.py` | Add plan confidence scoring — rate each generated plan 0.0–1.0; log score before execution | `NEEDS_SPEC` | AG-A-01 |
| AG-A-08 | `core/planner.py` | Add plan pre-announcement — NINA summarises what it will do and waits for /approve or /cancel before starting | `NEEDS_SPEC` | AG-A-01 |
| AG-A-09 | `core/planner.py` | Add per-step timeout budget — assign max_seconds per step; abort and mark failed if exceeded | `NEEDS_SPEC` | AG-A-02 |
| AG-A-10 | `core/planner.py` | Add /plan show command — display active plan: steps, statuses, current position, elapsed time via Telegram | `NEEDS_SPEC` | AG-A-01 |

---

### AG-B — Task State & Persistence
_New file: `core/task_store.py`_
_This is the foundation. Build AG-B-01 and AG-B-02 first — everything else depends on them._

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-B-01 | `core/task_store.py` | Create TaskStore class — full CRUD for Task objects persisted to data/tasks.json | `DONE` | — |
| AG-B-02 | `core/task_store.py` | Define Task schema — id, goal, plan_steps, status (pending/running/paused/done/failed), created_at, updated_at, retries, result | `NEEDS_SPEC` | AG-B-01 |
| AG-B-03 | `core/task_store.py` | Load open tasks on nina.service startup — TaskStore auto-resumes in-progress and pending tasks after restart | `DONE` | AG-B-01 |
| AG-B-04 | `core/task_store.py` | Add task indexing — lookup by status, tool_used, date range without full JSON scan | `NEEDS_SPEC` | AG-B-01 |
| AG-B-05 | `core/task_store.py` | Add /tasks list command — show active, pending, and failed tasks with summary via Telegram | `NEEDS_SPEC` | AG-B-01 |
| AG-B-06 | `core/task_store.py` | Add /task cancel <id> — gracefully stop a running task and mark it cancelled | `NEEDS_SPEC` | AG-B-01 |
| AG-B-07 | `core/task_store.py` | Add /task retry <id> — re-queue a failed task from its last failed step, not from the beginning | `NEEDS_SPEC` | AG-B-01 |
| AG-B-08 | `core/task_store.py` | Add task TTL — auto-expire completed tasks after N configurable days; archive to data/tasks_archive.json | `NEEDS_SPEC` | AG-B-01 |
| AG-B-09 | `core/task_store.py` | Add task dependency — Task B declares it must wait for Task A's completion before starting | `NEEDS_SPEC` | AG-B-01 |
| AG-B-10 | `core/task_store.py` | Add task priority queue — priority field (high/normal/low) determines which queued task runs first | `NEEDS_SPEC` | AG-B-01 |

---

### AG-C — AgentLoop Upgrade
_Existing file: `core/agent.py`_
_Dependency: AG-B-01 and AG-A-01 must be DONE first_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-C-01 | `core/agent.py` | Upgrade AgentLoop.run() to accept a Task object as input, not a raw message string | `NEEDS_SPEC` | AG-B-02 |
| AG-C-02 | `core/agent.py` | Add step-by-step executor — iterate through plan steps, call correct tool per step, store result in Task | `NEEDS_SPEC` | AG-C-01 |
| AG-C-03 | `core/agent.py` | Add step result piping — output of step N passed automatically as input context to step N+1 | `NEEDS_SPEC` | AG-C-02 |
| AG-C-04 | `core/agent.py` | Add mid-plan LLM reasoning — between steps, call LLM to interpret step output before deciding next step | `NEEDS_SPEC` | AG-C-02 |
| AG-C-05 | `core/agent.py` | Add loop detection guard — if same step attempted >3 times with identical input, break the loop | `NEEDS_SPEC` | AG-C-02 |
| AG-C-06 | `core/agent.py` | Add human-in-the-loop gate — steps marked require_approval=True pause until /approve or /reject via Telegram | `NEEDS_SPEC` | AG-C-02 |
| AG-C-07 | `core/agent.py` | Add parallel step executor — steps with no declared dependency run concurrently via asyncio.gather | `NEEDS_SPEC` | AG-C-02 |
| AG-C-08 | `core/agent.py` | Add step timeout watchdog — if step exceeds time budget, mark failed and route to fallback | `NEEDS_SPEC` | AG-A-09 |
| AG-C-09 | `core/agent.py` | Add agent execution log — write every step start/end/result to logs/agent_execution.jsonl | `NEEDS_SPEC` | AG-C-02 |
| AG-C-10 | `core/agent.py` | Add /agent status command — show current task, active step, elapsed time, last result via Telegram | `NEEDS_SPEC` | AG-C-02 |
| AG-C-11 | `core/agent.py` | Implement goal completion detector — after final step, second LLM call evaluates if original goal was achieved | `NEEDS_SPEC` | AG-D-01 |
| AG-C-12 | `core/agent.py` | Add graceful shutdown — on SIGTERM, AgentLoop saves current task state before process exits | `NEEDS_SPEC` | AG-B-01 |

---

### AG-D — Self-Verification Engine
_New file: `core/verifier.py`_
_Dependency: AG-C-02 must be DONE first_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-D-01 | `core/verifier.py` | Create StepVerifier class — checks whether a step's output satisfies its declared success_criteria | `DONE` | AG-C-02 |
| AG-D-02 | `core/verifier.py` + `core/capabilities.py` | Add output schema validation — each tool declares expected output schema; Verifier checks compliance after execution | `NEEDS_SPEC` | AG-D-05 |
| AG-D-03 | `core/verifier.py` | Add semantic verification — for LLM-generated outputs, second LLM call scores answer quality 1–5 | `DONE` | AG-D-01 |
| AG-D-04 | `core/verifier.py` | Add numeric assertion verifier — verify numeric outputs within declared expected range (e.g. price > 0) | `DONE` | AG-D-01 |
| AG-D-05 | `core/verifier.py` | Add non-empty verifier — simplest guard: step fails if output is None, empty string, or empty list | `DONE` | — |
| AG-D-06 | `core/verifier.py` + `core/planner.py` | Add replan trigger — when Verifier fails, send step back to Planner to generate alternative approach | `NEEDS_SPEC` | AG-D-01 |
| AG-D-07 | `core/verifier.py` + `core/task_store.py` | Add verification result storage — store pass/fail and reason per step inside the Task object | `NEEDS_SPEC` | AG-D-01 |
| AG-D-08 | `core/verifier.py` | Add verification scorecard — final task result includes per-step pass/fail summary from Verifier | `NEEDS_SPEC` | AG-D-07 |
| AG-D-09 | `core/verifier.py` + `core/capabilities.py` | Add custom verifier hooks — tools can register their own verifier function in CapabilityRegistry | `NEEDS_SPEC` | AG-D-01 |
| AG-D-10 | `core/verifier.py` | Add /verify last command — show verification results of last completed task via Telegram | `NEEDS_SPEC` | AG-D-08 |

---

## ██ AG2 — AGENTIC PHASE 2: Proactive Intelligence
_Start only after all AG1 groups (AG-A through AG-D) are merged and Guardian score is stable._

---

### AG-E — Event System
_New file: `core/events.py`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-E-01 | `core/events.py` | Create EventBus class — typed publish/subscribe for all internal NINA events | `NEEDS_SPEC` | AG1 complete |
| AG-E-02 | `core/events.py` | Define core event types — TASK_STARTED, TASK_COMPLETED, TASK_FAILED, STEP_DONE, ALERT_FIRED, MEMORY_UPDATED | `NEEDS_SPEC` | AG-E-01 |
| AG-E-03 | `core/events.py` | Add event persistence — write all events to logs/events.jsonl with timestamp and payload | `NEEDS_SPEC` | AG-E-01 |
| AG-E-04 | `core/events.py` + `core/task_store.py` | Add event-triggered task launching — MARKET_ALERT event auto-starts a defined downstream Task | `NEEDS_SPEC` | AG-E-02 |
| AG-E-05 | `core/events.py` | Add event filtering — subscribers declare event types they care about; receive no other noise | `NEEDS_SPEC` | AG-E-01 |
| AG-E-06 | `core/events.py` | Add event replay on startup — replay last N events so listeners restore state after restart | `NEEDS_SPEC` | AG-E-03 |
| AG-E-07 | `core/events.py` | Add event rate limiting — suppress duplicate events of same type within configurable cooldown window | `NEEDS_SPEC` | AG-E-01 |
| AG-E-08 | `core/events.py` | Add Telegram event notifier subscriber — high-priority events auto-push Telegram message | `NEEDS_SPEC` | AG-E-02 |
| AG-E-09 | `core/events.py` | Add /events last 10 command — show last 10 events with type, timestamp, payload summary via Telegram | `NEEDS_SPEC` | AG-E-03 |
| AG-E-10 | `core/events.py` + `core/task_store.py` | Add cross-task event wiring — Task A emits named event on completion that auto-triggers Task B | `NEEDS_SPEC` | AG-E-04 |

---

### AG-F — Autonomous Agents
_New directory: `tools/agents/`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-F-01 | `tools/agents/__init__.py` | Create BaseAutonomousAgent base class — run(), stop(), get_status() interface all agents must implement | `NEEDS_SPEC` | AG-E-01 |
| AG-F-02 | `tools/agents/market_agent.py` | MarketAgent — watches DSE/CSE prices on schedule, emits ALERT event when watchlist threshold crossed | `NEEDS_SPEC` | AG-F-01 |
| AG-F-03 | `tools/agents/expense_agent.py` | ExpenseAgent — monitors Telegram messages for expense patterns, auto-logs to finance tool | `NEEDS_SPEC` | AG-F-01 |
| AG-F-04 | `tools/agents/email_agent.py` | EmailAgent — polls EWS inbox periodically, classifies emails, surfaces top 3 urgent items | `NEEDS_SPEC` | AG-F-01 |
| AG-F-05 | `tools/agents/reminder_agent.py` | ReminderAgent — scans data/reminders.json every minute, fires due reminders as ALERT events | `NEEDS_SPEC` | AG-F-01 |
| AG-F-06 | `tools/agents/news_agent.py` | NewsAgent — fetches BD financial news daily, summarises and pushes to Telegram | `NEEDS_SPEC` | AG-F-01 |
| AG-F-07 | `tools/agents/health_agent.py` | HealthAgent — monitors nina.service logs for error patterns, fires ALERT on anomaly | `NEEDS_SPEC` | AG-F-01 |
| AG-F-08 | `tools/agents/quota_agent.py` | QuotaAgent — watches provider quota consumption, switches default provider before exhaustion | `NEEDS_SPEC` | AG-F-01 |
| AG-F-09 | `tools/agents/goal_tracker_agent.py` | GoalTrackerAgent — reviews open tasks daily, nudges user via Telegram on stalled goals | `NEEDS_SPEC` | AG-F-01 |
| AG-F-10 | `tools/agents/memory_agent.py` | MemoryAgent — reviews facts.json periodically, flags stale or contradictory facts for review | `NEEDS_SPEC` | AG-F-01 |
| AG-F-11 | `core/capabilities.py` | Add agent registry — register all autonomous agents; start/stop/status via /agent start <name> | `NEEDS_SPEC` | AG-F-01 |
| AG-F-12 | `core/capabilities.py` | Add /agents list command — show all agents, running/stopped status, last action time via Telegram | `NEEDS_SPEC` | AG-F-11 |

---

### AG-G — Proactive Intelligence Engine
_New file: `core/proactive.py`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-G-01 | `core/proactive.py` | Create ProactiveEngine — decides when and what to push to user without being asked | `NEEDS_SPEC` | AG-E-01 |
| AG-G-02 | `core/proactive.py` | Add daily briefing composer — weather + DSE + reminders + news in single Telegram message at 7:30 AM | `NEEDS_SPEC` | AG-G-01 |
| AG-G-03 | `core/proactive.py` | Add anomaly notifier — push Telegram alert unprompted when monitored metric crosses threshold | `NEEDS_SPEC` | AG-G-01 |
| AG-G-04 | `core/proactive.py` | Add task completion push — send result summary to user when background task completes | `NEEDS_SPEC` | AG-G-01 |
| AG-G-05 | `core/proactive.py` | Add smart quiet hours — respect configurable quiet hours in data/settings.json; no alerts 11PM–7AM | `NEEDS_SPEC` | AG-G-01 |
| AG-G-06 | `core/proactive.py` | Add notification deduplication — never send same alert twice within configurable time window | `NEEDS_SPEC` | AG-G-01 |
| AG-G-07 | `core/proactive.py` | Add /quiet <duration> command — pause all proactive messages for specified duration | `NEEDS_SPEC` | AG-G-01 |
| AG-G-08 | `core/proactive.py` | Add priority-based batching — batch low-priority alerts into single digest instead of individual spam | `NEEDS_SPEC` | AG-G-06 |

---

### AG-H — Tool Chaining Framework
_New file: `tools/chain.py`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-H-01 | `tools/chain.py` | Create ToolChain class — executes ordered list of tool calls with automatic data piping between steps | `NEEDS_SPEC` | AG1 complete |
| AG-H-02 | `tools/chain.py` | Add named output slots — each tool call defines output_key; downstream tools reference by name not position | `NEEDS_SPEC` | AG-H-01 |
| AG-H-03 | `tools/chain.py` | Add conditional branching — if tool_output["status"] == "alert" jump to step 5, else continue to step 3 | `NEEDS_SPEC` | AG-H-02 |
| AG-H-04 | `tools/chain.py` | Add chain dry-run mode — execute with mock outputs to validate chain logic before any real tool calls | `NEEDS_SPEC` | AG-H-01 |
| AG-H-05 | `data/chains/` + `tools/chain.py` | Add pre-built chain templates — expense_log_chain, market_check_chain, daily_brief_chain | `NEEDS_SPEC` | AG-H-01 |
| AG-H-06 | `tools/chain.py` | Add /chain run <name> command — execute named chain template on demand via Telegram | `NEEDS_SPEC` | AG-H-05 |
| AG-H-07 | `tools/chain.py` | Add chain execution history — store last 10 run results per chain in data/chain_history.json | `NEEDS_SPEC` | AG-H-01 |
| AG-H-08 | `tools/chain.py` | Add chain editor wizard — /chain edit <name> opens guided step-builder via Telegram | `NEEDS_SPEC` | AG-H-06 |

---

### AG-I — Agentic Memory
_Existing file: `core/memory.py`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-I-01 | `core/memory.py` | Add episodic memory — store past task executions (goal + result) as retrievable episodes in ChromaDB | `NEEDS_SPEC` | AG1 complete |
| AG-I-02 | `core/memory.py` + `core/planner.py` | Add memory-driven planning — Planner queries ChromaDB for similar past goals before generating new plan | `NEEDS_SPEC` | AG-I-01 |
| AG-I-03 | `core/memory.py` | Add outcome memory — store which plan succeeded for which goal type; reuse successful plans | `NEEDS_SPEC` | AG-I-01 |
| AG-I-04 | `core/memory.py` | Add working memory — short-term slot-based memory for current task context, cleared on task completion | `NEEDS_SPEC` | AG-I-01 |
| AG-I-05 | `core/memory.py` + `core/agent.py` | Add context injection from history — inject top-3 relevant past outcomes into current LLM system prompt | `NEEDS_SPEC` | AG-I-01 |
| AG-I-06 | `core/memory.py` | Add memory conflict resolver — detect contradictory facts; surface via /memory conflicts for user review | `NEEDS_SPEC` | AG-I-01 |
| AG-I-07 | `core/memory.py` | Add preference learning — store user correction patterns as preferences (e.g. always BDT not USD) | `NEEDS_SPEC` | AG-I-01 |
| AG-I-08 | `core/memory.py` + `core/task_store.py` | Add failure memory — when task fails, store failure reason in ChromaDB to avoid repeating same mistake | `NEEDS_SPEC` | AG-I-01 |
| AG-I-09 | `core/memory.py` | Add long-term goal memory — /goal set <text> stores persistent goal NINA references in daily briefing | `NEEDS_SPEC` | AG-I-01 |
| AG-I-10 | `core/memory.py` | Add /memory timeline command — show facts and episodes chronologically for past 7 days via Telegram | `NEEDS_SPEC` | AG-I-01 |

---

## ██ AG3 — AGENTIC PHASE 3: Tests
_Run in parallel with AG2. AG-J-10 is strictly last — requires all AG1 + AG2 stable._

### AG-J — Agentic Test Coverage
_Directory: `tests/`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-J-01 | `tests/test_planner.py` | Unit tests for GoalDecomposer: goal parsing, step generation, dependency ordering | `NEEDS_SPEC` | AG-A-01 |
| AG-J-02 | `tests/test_task_store.py` | Unit tests for TaskStore: CRUD, persistence, TTL, status transitions | `DONE` | AG-B-01 |
| AG-J-03 | `tests/test_agent_loop.py` | Integration tests for upgraded AgentLoop: step execution, result piping, loop detection | `NEEDS_SPEC` | AG-C-01 |
| AG-J-04 | `tests/test_verifier.py` | Unit tests for StepVerifier: schema check, numeric assertion, semantic scoring | `DONE` | 2026-06-09 |
| AG-J-05 | `tests/test_events.py` | Unit tests for EventBus: publish, subscribe, filter, rate-limit, replay | `NEEDS_SPEC` | AG-E-01 |
| AG-J-06 | `tests/test_market_agent.py` | Unit tests for MarketAgent: mock price feed, threshold crossing, alert emission | `NEEDS_SPEC` | AG-F-02 |
| AG-J-07 | `tests/test_chain.py` | Unit tests for ToolChain: sequential execution, conditional branching, dry-run mode | `NEEDS_SPEC` | AG-H-01 |
| AG-J-08 | `tests/test_proactive.py` | Unit tests for ProactiveEngine: quiet hours enforcement, deduplication, batching | `NEEDS_SPEC` | AG-G-01 |
| AG-J-09 | `tests/test_memory_agentic.py` | Integration tests: episodic memory, working memory, preference learning | `NEEDS_SPEC` | AG-I-01 |
| AG-J-10 | `tests/test_e2e_agent.py` | End-to-end: submit goal → plan → step execution → verification → result | `NEEDS_SPEC` | AG-J-09 |

---

### AG-M — Throughput Maximizer
_MEGA-TASK: V2.0 Architecture Upgrade_
_Dependency: AG-B-01 and AG-B-02 must be DONE first_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-M-01 | Multi-module | 🚀 MEGA-TASK: NINA Throughput Maximizer (v2.0 Architecture) — Implement Domains 1-5 to accelerate NINA. | `READY` | AG-B-01 |
| AG-M-02 | Multi-module | 📉 MEGA-TASK: Token-Surgical Architecture (v2.1) — Aggressive cloud token reduction via local RAG and surgical context selection. | `DONE` | AG-M-01 |
| AG-M-03 | Multi-module | 🛠️ NF-EXT: Surgical Code Intelligence — Add `nf code symbol`, `find-symbol`, and `sigs` for zero-token code research. | `DONE` | — |
| AG-M-04 | `AGENTS.md` | 📝 DOC-COMP: Instruction Compression — Refactor `AGENTS.md` into high-density directives; move guides to `docs/agent-memory/`. | `DONE` | — |
| AG-M-05 | `ninaflash.py` | 📊 NF-BACKLOG: Incremental State Monitoring — Add `backlog summary` and `task active` to avoid reading full backlog tables. | `DONE` | — |
| AG-M-06 | `.geminiignore` | 🛡️ SEC-IGNORE: Global Context Filtering — Implement project-wide `.geminiignore` for automated context pruning. | `READY` | — |
| AG-M-07 | `ninaflash.py` | 🧹 NF-CLEAN: Automated Hygiene — Add `nf check code --fix` and `nf doc check --fix` for local error resolution. | `DONE` | — |
| AG-M-08 | `ninaflash.py` | 💓 NF-STATUS: High-Density Pulse — Implement `nf status --pulse` and `nf log next-id` for 10-line project heartbeats. | `DONE` | — |
| AG-M-09 | `ninaflash.py` | 📦 NF-ARCHIVE: Historical Offloading — Implement `nf backlog archive` to move `DONE` tasks to historical storage. | `DONE` | — |
| AG-M-10 | `ninagate/` | 📡 GATE-PROMPT: System Prompt Templating — Move `AGENTS.md` into cached NinaGate system prompts. | `DONE` | AG-M-04 |
| AG-M-11 | `ninaflash.py` | 📉 NF-LOG: Sliding Window Summarizer — Implement log compression and `nf log summarize` for noisy update logs. | `DONE` | — |
| AG-M-12 | `ninaflash.py` | 📦 NF-SESSIONS: Checkpoint & Resume — Add `nf session checkpoint` to preserve task state across restarts. | `DONE` | — |

---

### AG-N — Advanced Code Intelligence
_Focus: Zero-token research and semantic mapping_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-N-01 | `ninaflash.py` | Global Symbol Indexer — Generate JSON map of all classes/functions. | `DONE` | — |
| AG-N-02 | `ninaflash.py` | Local Call Graph Generator — Trace function calls locally without LLM. | `READY` | AG-N-01 |
| AG-N-03 | `core/` | Type Hint Enforcement — Automated script to add missing type hints. | `READY` | — |
| AG-N-04 | `ninaflash.py` | Dead Code Detector — Identify and flag unused functions/imports. | `READY` | — |
| AG-N-05 | `ninaflash.py` | Symbol-Based Context Injector — Read only the call stack of a function. | `READY` | AG-N-02 |
| AG-N-06 | `ninaflash.py` | Docstring Quality Audit — Score docstrings on clarity and completeness. | `READY` | — |
| AG-N-07 | `core/` | Automated Refactoring: Method Extraction — Split large functions via AST. | `READY` | — |
| AG-N-08 | `ninaflash.py` | Dependency Cycle Detector — Identify circular imports locally. | `READY` | — |
| AG-N-09 | `ninaflash.py` | Code Complexity Watchdog — Calculate cyclomatic complexity. | `READY` | — |
| AG-N-10 | `ninaflash.py` | Symbol Migration Tool — Automate renaming and moving symbols. | `READY` | — |

---

### AG-O — Automated Testing & QA
_Focus: Reducing debug turns through local verification_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-O-01 | `tests/` | Test Scaffold Generator — Create test stubs for every new function. | `READY` | — |
| AG-O-02 | `tests/` | Mutation Test Suite — Implement basic mutation testing for core modules. | `READY` | — |
| AG-O-03 | `tests/` | Coverage Optimizer — Identify "coldest" code paths with zero tests. | `READY` | — |
| AG-O-04 | `ninaflash.py` | Automated Regression Bench — Run benchmarks on every PR. | `READY` | — |
| AG-O-05 | `tests/` | Mock Factory — Automated generation of mocks for external APIs. | `READY` | — |
| AG-O-06 | `tests/` | Flaky Test Detector — Identify intermittent test failures. | `READY` | — |
| AG-O-07 | `tests/` | Integration Test Parallelizer — Run tests in concurrent chunks. | `READY` | — |
| AG-O-08 | `tests/` | Data-Driven Test Generator — Create tests from session logs. | `READY` | — |
| AG-O-09 | `bin/` | Security Scan: Dependency Audit — Automated venv security audit. | `READY` | — |
| AG-O-10 | `tests/` | Doc-Test Validator — Ensure MD code examples are runnable. | `READY` | — |

---

### AG-P — Performance & Latency
_Focus: High-velocity execution and low overhead_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-P-01 | `core/router.py` | Router Latency Optimizer — Profile and reduce router overhead. | `READY` | — |
| AG-P-02 | `core/router.py` | Persistent Response Cache — Move cache to SQLite for speed. | `READY` | — |
| AG-P-03 | `core/router.py` | Parallel Provider Dispatch — Concurrent routing to fallbacks. | `READY` | — |
| AG-P-04 | `core/config.py` | Hot-Reload Speedup — Optimize NinaConfig reload time. | `READY` | — |
| AG-P-05 | `core/memory.py` | Memory Fetch Indexer — Vector indexing for faster retrieval. | `READY` | — |
| AG-P-06 | `ninaflash.py` | Subprocess Pool — Reuse subprocesses for shell tools. | `READY` | — |
| AG-P-07 | `core/` | Async IO Optimization — Ensure non-blocking file/network ops. | `READY` | — |
| AG-P-08 | `core/task_store.py`| Task Queue Prioritizer — Move to priority-based execution. | `READY` | — |
| AG-P-09 | `core/observability.py`| Hardware Metric Optimization — Reduce sampling frequency. | `READY` | — |
| AG-P-10 | `main.py` | Startup Time Minimizer — Profile and reduce boot time. | `READY` | — |

---

### AG-Q — Memory & Knowledge
_Focus: Precision retrieval and minimal noise_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-Q-01 | `data/memory/` | ChromaDB Cluster — Shard vector memory by domain. | `READY` | — |
| AG-Q-02 | `core/memory.py` | Automatic Fact Extraction — LLM-driven mining of logs. | `READY` | — |
| AG-Q-03 | `core/memory.py` | Memory Conflict Resolver v2 — Automated contradiction detection. | `READY` | — |
| AG-Q-04 | `tools/` | Knowledge Graph Visualization — Generate DOT relationships. | `READY` | — |
| AG-Q-05 | `core/memory.py` | Memory Pruning — Remove redundant/low-utility memories. | `READY` | — |
| AG-Q-06 | `core/memory.py` | Context-Aware Memory Retrieval — Filter by task type. | `READY` | — |
| AG-Q-07 | `core/memory.py` | Shared Fact Validation — Cross-reference external sources. | `READY` | — |
| AG-Q-08 | `core/memory.py` | Episodic Memory Summarization — Compress old session logs. | `READY` | — |
| AG-Q-09 | `core/memory.py` | Entity Linking — Consolidate duplicate entities in memory. | `READY` | — |
| AG-Q-10 | `data/memory/` | Memory Backup Sync — Multi-region backup implementation. | `READY` | — |

---

### AG-R — Repository Hygiene
_Focus: Minimal repo size and clean structure_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-R-01 | `ninaflash.py` | Stale File Archiver — Auto-move 60-day untouched files. | `READY` | — |
| AG-R-02 | `requirements.txt`| Requirement Pinner — Lock dependencies to exact hashes. | `READY` | — |
| AG-R-03 | `ninaflash.py` | Large File Pointer — Move binary assets to external storage. | `READY` | — |
| AG-R-04 | `ninaflash.py` | Directory Structure Audit — Enforce snake_case rules. | `READY` | — |
| AG-R-05 | `ninaflash.py` | License Header Inserter — Add headers to all source files. | `READY` | — |
| AG-R-06 | `ninaflash.py` | Orphaned Config Cleaner — Remove unused keys from .env.example. | `READY` | — |
| AG-R-07 | `templates/` | Template Consolidator — Merge redundant dashboard templates. | `READY` | — |
| AG-R-08 | `ninaflash.py` | Automated CHANGELOG — Generate from commit history. | `READY` | — |
| AG-R-09 | `ninaflash.py` | Metadata Quality Gate — Require summaries for new dirs. | `READY` | — |
| AG-R-10 | `dashboard/` | Repo Hygiene Dashboard v2 — Health trends and drift alerts. | `READY` | — |

---

### AG-S — Interface & Interaction
_Focus: Fast feedback and low-overhead communication_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-S-01 | `interfaces/telegram_interface.py`| Telegram Batching — Consolidate short messages. | `READY` | — |
| AG-S-02 | `ninaflash.py` | CLI Progress Bars — Rich bars for long nf commands. | `READY` | — |
| AG-S-03 | `core/proactive.py`| Notification Priority — Gated alerts by activity hours. | `READY` | — |
| AG-S-04 | `interfaces/telegram_interface.py`| Telegram Inline Results — Inline query status checks. | `READY` | — |
| AG-S-05 | `core/observability.py`| Multi-Channel Alerts — Discord/Slack webhook support. | `READY` | — |
| AG-S-06 | `ninaflash.py` | Command Autocomplete — Bash/Zsh completion for nf. | `READY` | — |
| AG-S-07 | `dashboard/` | Visual Task Graph — Render current plan as SVG. | `READY` | — |
| AG-S-08 | `ninaflash.py` | Interactive REPL — shell-like interactive mode for nf. | `READY` | — |
| AG-S-09 | `interfaces/telegram_interface.py`| Voice Command Bridge — STT integration for voice. | `READY` | — |
| AG-S-10 | `dashboard/` | Dashboard Dark Mode — High-contrast visual polish. | `READY` | — |

---

### AG-T — Token & Context Engineering
_Focus: Absolute minimum context overhead_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-T-01 | `core/agent.py` | Dynamic Prompting — Adjust prompt length by task diff. | `READY` | — |
| AG-T-02 | `ninaflash.py` | Context Window Estimator — Predict token usage before call. | `READY` | — |
| AG-T-03 | `core/agent.py` | Instruction Deduplication — Strip identical rules. | `READY` | — |
| AG-T-04 | `ninaflash.py` | Token-Optimized JSON — Key-abbreviations in exports. | `READY` | — |
| AG-T-05 | `ninaflash.py` | Differential PR Body — Symbol-focused descriptions. | `READY` | — |
| AG-T-06 | `ninaflash.py` | Tool Metadata Compression — Strip docstrings in prompt. | `READY` | — |
| AG-T-07 | `tools/` | Incremental Search — Search tools return delta only. | `READY` | — |
| AG-T-08 | `ninaflash.py` | Context-Specific Ignore — .geminiignore by task type. | `READY` | — |
| AG-T-09 | `core/nina.py` | Prompt Versioning — AB test different system prompts. | `READY` | — |
| AG-T-10 | `ninaflash.py` | Token Usage Forecasting — Predict weekly costs. | `READY` | — |
| AG-T-11 | `ninaflash.py` | Final Synthesis — Consolidate all 100+ functions. | `READY` | — |

---

## ██ Agentic Build Order (strict — do not deviate)

```
AG1 Phase 1:
  AG-B-01 → AG-B-02           ← Foundation. Nothing else starts until these exist.
  AG-A-01 → AG-A-02 → AG-A-03 ← GoalDecomposer
  AG-C-01 → AG-C-02 → AG-C-03 ← AgentLoop upgrade
  AG-D-05 → AG-D-01 → AG-D-02 ← Verifier: empty check first, then schema
  AG-A-04 + AG-B-03            ← Plan + task persistence on restart
  AG-C-11 + AG-D-06            ← Goal completion + replan trigger (wires AG-C to AG-D)
  Remaining AG-A/B/C/D in any order

AG2 Phase 2 (AG1 must be fully merged first):
  AG-E-01 → AG-E-02 → AG-E-03 ← EventBus core
  AG-F-01 → AG-F-02            ← BaseAgent + MarketAgent (first real autonomous agent)
  AG-G-01 → AG-G-05 → AG-G-06 ← ProactiveEngine core + quiet hours + dedup
  AG-H-01 → AG-H-02 → AG-H-03 ← ToolChain core
  AG-I-01 → AG-I-04 → AG-I-02 ← Episodic → working → memory-driven planning
  Remaining AG-E/F/G/H/I tasks in any order

AG3 Phase 3 (parallel with AG2):
  AG-J-01 through AG-J-09 in any order
  AG-J-10 strictly last
```

---

## ██ DONE — Completed Items

| ID | Title | Entry | PR | Date |
|----|-------|-------|----|------|
| F-02 | memory: deterministic personal_context | E-sync | — | 2026-06-09 |
| B-001 | Sentinel: shell=True fix in guardianengine.py | E-057 | #60 | 2026-06-07 |
| SCHED-ALL | 15 daily scheduled tasks defined | E-059 | — | 2026-06-07 |
| TRACK-ALL | jules_task_tracker.md + ninaflash_task_tracker.md created | E-059 | — | 2026-06-07 |
| B-024 | AGENTS.md: backlog update protocol | E-060 | — | 2026-06-07 |
| B-005 | F-09 ModelDiscoveryService — tools/model_discovery.py | E-061 | #25 | 2026-06-07 |
| B-037 | docs/space: add nina_architecture_diagram.md with ASCII diagrams | E-sync | #26 | 2026-06-07 |
| B-027 | tools/gputuner.py: add fallback when nvidia-smi not available | E-sync | #27 | 2026-06-07 |
| B-029 | Write integration test: full request through router → provider → response | E-sync | #28 | 2026-06-08 |
| B-025 | crons/manager.py: add graceful shutdown handler (SIGTERM) | E-sync | #29 | 2026-06-08 |
| B-017 | Write tests for core/router.py — provider ordering, circuit breaker, fallback | E-sync | #30 | 2026-06-08 |
| B-019 | Write tests for guardianengine.py — SIGNATURES check, run_cmd | E-sync | #33 | 2026-06-08 |
| R-78 | Fix tool grammar fragility — minimum viable guard | E-sync | #35 | 2026-06-08 |
| B-040 | Write CONTRIBUTING.md | E-sync | #36 | 2026-06-08 |
| B-021 | Add prometheus-style metrics endpoint to healthcheck.py | E-sync | #38 | 2026-06-08 |
| B-023 | Add AGENTS.md section: tracker update protocol for Jules tasks | E-sync | #43 | 2026-06-08 |
| B-007 | F-09 Part 3 — seed data/model_cache.json with all 16 providers | E-sync | #42 | 2026-06-08 |
| B-020 | Write tests for tools/model_discovery.py | E-sync | #41 | 2026-06-08 |
| B-022 | tools/compact_exporter.py: add progress logging for long exports | E-sync | #44 | 2026-06-08 |
| B-015 | crons/manager.py: add job execution metrics (duration, last_success, fail_count) | E-sync | #45 | 2026-06-08 |
| B-013 | healthcheck.py: replace bare except with typed exception handling | E-sync | #46 | 2026-06-08 |

---

## ██ Perplexity Session Briefing Protocol

At the start of every session where this file is attached, Perplexity will:

1. **Count READY items by tier** — "P0: N, P1: N, P2: N, AG1: N needs-spec"
2. **Unblock promotions** — any BLOCKED item whose dependency is now DONE → promote to READY
3. **Scan IN_PROGRESS / IN_PR** — report what is pending ninaflash merge
4. **Recommend next batch** — up to 15 non-overlapping READY tasks for Jules
5. **Generate Jules specs** — full paste-ready prompts for each recommended task
6. **Territory check** — confirm no two tasks in batch touch the same file
7. **AG pipeline gate** — if all P0+P1 are DONE, promote AG-B-01/AG-B-02 to READY and spec them as next Jules batch

---

## ██ ninaflash Backlog Update Protocol

After every Jules PR merge, ninaflash updates status using Python — never bash echo:

```python
from pathlib import Path

backlog_path = Path("/home/aibony/nina/docs/space/jules_backlog.md")
content = backlog_path.read_text()
content = content.replace(
    "| B-XXX | Title here | `READY`",
    "| B-XXX | Title here | `DONE`"
)
backlog_path.write_text(content)
```

---

## ██ Routing Rules (canonical)

| Route | Files |
|-------|-------|
| **Jules** | `core/*.py` (not router.py), `tools/*.py` (not shell.py), `tests/*.py`, `data/`, `docs/` |
| **ninaflash only** | `main.py`, `core/router.py`, `interfaces/telegraminterface.py`, `guardianengine.py`, `tools/shell.py`, `.env` |
| **ninaflash = merge executor** | All Jules PRs — never auto-merge via GitHub UI |
| **After every merge** | `./nina_sync.sh` — no exceptions |
| **Before any task** | `cat juleslock.txt` — do not proceed if target file is locked |

---

## ██ Daily Throughput Target

| Metric | Target |
|--------|--------|
| Scheduled tasks (auto) | 15/day |
| Feature tasks submitted to Jules | 10–15/day |
| PRs merged by ninaflash | 10–15/day |
| B-series backlog cleared | ~3–4 days at full pace |
| AG1 Phase 1 | ~1 week |
| AG2 Phase 2 | ~2 weeks |
| Full agentic NINA operational | ~3–4 weeks |

**The pipeline never empties. NINA development never stops.**

---

## 📜 Task Specifications

### From: jules_mega_task.md
# TASK: NINA Observability & Memory Upgrade v4.0 (The NINA-Evolve Protocol)

## 0. OBJECTIVE: AUTONOMOUS SELF-OPTIMIZATION
*Goal: Create a self-reinforcing "Vicious Cycle" where NINA monitors its performance, identifies bottlenecks, proposes upgrades, and autonomously implements them.*

## 1. PHASE 1: THE PERFORMANCE ANALYTIC LAYER (SENSE)
- **Deep Metrics Engine:** Enhance `tools/monitor.py` to calculate:
  - **Token Savings:** (Estimated Baseline Cloud Tokens) - (Actual Cloud Tokens Used).
  - **Time Efficiency:** (Sequential Execution Time) - (Parallel Execution Time).
  - **Throughput Rank:** Requests per minute handled locally vs. cloud.
- **Efficiency Baseline:** Establish a "Plain Gemini CLI" baseline to measure improvement.

## 2. PHASE 2: THE AUTONOMOUS FEEDBACK LOOP (THINK)
- **Bottleneck Identifier:** Create `tools/evolve.py` to analyze `logs/ninagate.log` and `logs/router.log` for:
  - Frequent cloud escalations that *could* have been local (OFFLOAD_OPPORTUNITY).
  - High-latency tool calls.
  - Repetitive mechanical tasks.
- **Improvement Proposals:** Every 10 tasks, the engine must generate an `EVOLVE_PROPOSAL.md` with specific code or configuration upgrades.

## 3. PHASE 3: AUTONOMOUS IMPLEMENTATION (ACT)
- **Self-Upgrade Pipeline:** When an `EVOLVE_PROPOSAL.md` is generated, NINA must:
  - Create a temporary branch.
  - Apply the proposed optimization (e.g., refactoring a tool for better parallelism).
  - Run the `test/smoke.py` and `test/performance.py` suites.
  - If tests pass and metrics improve, merge the upgrade.
- **Incremental Documentation:** For every upgrade, autonomously update `ARCHITECTURE.md` and `CHANGELOG.md` to reflect the new system state.

## 4. PHASE 4: THE VICIOUS CYCLE (EVOLVE)
- **Recursive Learning:** The system must treat its own code as a subject for continuous "Surgical Surgery."
- **Fact Persistence:** The learnings from each optimization cycle must be appended to `AGENTS.md` and the `MEMORY.md` index to prevent regressing on efficiency.

## 5. ARCHITECTURAL MANDATES
- **Closed-Loop:** The cycle must run without user intervention (Sense -> Think -> Act -> Document -> Repeat).
- **Safety First:** Self-upgrades MUST be validated by the `Verifier` and never bypass the `pyflakes`/`py_compile` gates.
- **Metrics-Driven:** No upgrade is merged unless it proves a >5% improvement in time or token efficiency.

## 6. ACCEPTANCE CRITERIA
1. NINA generates an `efficiency_report.json` after every session.
2. The system autonomously identifies and fixes at least one latency bottleneck per cycle.
3. `ARCHITECTURE.md` is updated incrementally with every self-implemented feature.
4. The dashboard shows a "System Evolution" score (cumulative efficiency gains).


### From: jules_spec_backlog_inc.md
📊 MEGA-TASK: NF-BACKLOG Incremental State (AG-M-05)
Assignee: Jules (Async Cloud Coder)
Objective: Reduce token consumption by providing high-density summaries of project state instead of reading large markdown tables.

🏗️ Domain 1: Backlog Summarization
- nf backlog summary: Provide a 5-line summary of the backlog: count of READY, IN_PROGRESS, BLOCKED, and DONE tasks.
- nf task active: List only tasks currently in `IN_PROGRESS` or `IN_PR` along with the files they have locked in `jules_lock.txt`.

🧠 Domain 2: Incremental Logs
- nf log tail <n>: Read only the last <n> entries of `nina_update_log.md`.
- nf log next-id: Parse the update log to find the last entry number and return the next available ID (e.g., "173").

📝 Acceptance Criteria:
- Commands must be fast and zero-token in cloud (local execution).
- Update `ninaflash.py` help menu.


### From: jules_spec_gemini_ignore.md
🛡️ MEGA-TASK: SEC-IGNORE Global Context Filtering (AG-M-06)
Assignee: Jules (Async Cloud Coder)
Objective: Automatically prune the agent's context window using project-wide exclusion rules.

🏗️ Domain 1: .geminiignore Implementation
- Create a canonical `.geminiignore` in the repo root.
- Exclusion list: `logs/`, `data/plans/`, `upgrades/backups/`, `*.pyc`, `__pycache__/`, `venv/`.

🧠 Domain 2: Tool-Level Compliance
- Update `ninaflash.py` and `tools/files.py` to respect `.geminiignore` patterns when listing or reading files.
- nf check ignore: A diagnostic command that shows which files are currently being hidden from the agent.

📝 Acceptance Criteria:
- Reduced "noise" in global searches (`grep_search`).
- No sensitive logs or large data files leaked into the cloud context.


### From: jules_spec_token_surgical.md
📉 MEGA-TASK: Token-Surgical Architecture (v2.1)
Assignee: Jules (Async Cloud Coder)
Objective: Reduce NINA's total cloud token consumption by an additional 50% (on top of v2.0) by moving context management from "Dumb Truncation" to "Surgical Selection."

🏗️ Domain 1: Semantic Context Selection (Local-First RAG)
- nf context-map: Automatically generate a semantic map of the codebase using local models (qwen2.5:1.5b).
- nf chunk-search: Replace full-file reading with a RAG-based chunk search. Use ChromaDB locally. When an agent requests a file, nf returns only the relevant semantic chunks (e.g., "router's circuit breaker") across multiple files instead of entire large files.

🧠 Domain 2: Local Reasoning Offloading (Thinking-on-the-Edge)
- nf plan-local: Move the 7-step code scaffold reasoning (from AGENTS.md) to a local model (Ollama). The cloud agent only receives the final verified plan.
- Local Error Pre-Verification: Before the cloud agent attempts to "fix" a file, nf runs pyflakes and compile locally and provides a one-line error summary: "Fix IndentationError at line 45" instead of the whole file.

📉 Domain 3: Differential Context Injector (Git-Diff Primary)
- nf diff-context: Modify the primary agent prompt to prioritize git diff over file content. For files >500 lines, nf sends only the changed blocks + symbol outline (function signatures).
- Skeleton Outlining: Use the Python `ast` module to generate a "Skeleton" of large files. The cloud agent sees class/function signatures and docstrings but no bodies, unless specifically requested via `nf read --full`.

🛡️ Domain 4: Token-Aware Tooling (Surgical Read/Write)
- Surgical Read: Update tools/files.py to support line-range reads (`--lines 40-80`) and symbol-based reads (`--symbol HybridRouter`).
- Log Compression: Implement a sliding-window log summarizer in tools/ninaflash.py that collapses identical repeating log lines (e.g., "Heartbeat..." x 100) into a single summary line.

📡 Domain 5: NinaGate Prompt Optimization
- System Prompt Templating: Move the heavy AGENTS.md instructions into a cached system prompt in NinaGate. 
- Tool Definition Stripping: Dynamically strip unused tool definitions from the cloud agent's context based on the current task classification (e.g., remove "market" tools from a "coding" task).

📝 Acceptance Criteria for Jules:
1. Token Reduction: Demonstrate (via mocks or logs) that a standard coding task uses 30-50% fewer tokens.
2. Stability: Surgical reads must include enough context (at least 5 lines above/below) to prevent hallucination.
3. Documentation: Update nina_update_log.md for every module completed.
4. Testing: Provide unit tests for the RAG chunking and Skeleton outlining logic.

Jules, you are cleared to proceed with AG-M-02. Start with Domain 4 (Surgical Tooling) to enable the infrastructure for surgical reading.


### From: jules_spec_throughput_maximizer.md
🚀 MEGA-TASK: NINA Throughput Maximizer (v2.0 Architecture) Assignee: Jules (Async Cloud Coder)
Objective: Transform ninaflash and NinaGate into a high-velocity, low-cost autonomous control plane that reduces cloud token usage by 90% and accelerates feature delivery by 10x.

🏗️ Domain 1: NinaGate "Fast-Path" & Local Drafting Engine Leverage NinaGate to move boilerplate and scaffolding from Cloud to Local AI.

    Local Fast-Path Routing: Add a local_fast model category to NinaGate. Route specifically to qwen2.5-coder:1.5b or deepseek-coder:1.3b on Ollama for instant local inference.
    Boilerplate Scaffolding: Implement nf draft. Use local Jinja2 templates + Local Fast-Path AI to generate NINA-style tool stubs and class structures for free.
    Local Syntax Fixer: Create a local hook that catches common Python syntax errors (missing imports, indentations) and uses the Local Fast-Path AI to fix them locally before a cloud turn is wasted.
    Commit Message Autogen: Add nf gen-commit. Analyzes git diff via NinaGate to generate structured, professional commit messages.
    Docstring Engine: Automatically populate missing docstrings in newly created files using local tiny-models.

🧠 Domain 2: Autonomous Governance & Self-Healing Move repository maintenance from "Manual Quests" to "Autonomous Tasks."

    Governance Task Feed: Update tools/generate_dashboard.py to output data/governance_tasks.json. Every "Missing Test" or "Low Metadata" entry is now an executable task object.
    IdleLoop Integration: Configure idleloop.py to consume the Task Feed. NINA now heals her own metadata and writes missing tests when idle.
    Repro Script Factory: When pytest fails, nf uses NinaGate to write a standalone bin/repro_fail_X.py script. The cloud agent's goal shifts from "fix bug" to "fix script."
    Dependency Self-Healer: Catch ModuleNotFoundError during local runs; nf automatically cross-references requirements.txt and runs pip install in the venv.
    Auto-Archiver: Automatically move files flagged as purge_candidate by the index into exports/archive/ after a 30-day window.

📉 Domain 3: Context Engineering & Token Compression Stop sending "Noise" to the cloud. Send only the "Signal."

    Context Distillation: Create nf distill
    The Bitmask Index: Generate a tiny, token-optimized version of nina_index.json containing only governed files and their guardrails.
    Task Sandboxing (Workbench): nf workbench --task F-06. Creates a transient directory of symlinks to ONLY the files relevant to the task (via dependency mapping).
    Virtual Governance Headers: Modify tools/files.py (read tool). When an agent reads a file, prepend a virtual header: # GOVERNANCE: ROLE=SOT, GUARDRAILS=APPEND_ONLY.
    Incremental Log Summarizer: Instead of full logs, nf provides a 10-line summary of the last 100 log entries using NinaGate.

🛡️ Domain 4: Decision Engine & Safety Rails Turn the index from a list of files into a "Rules of Engagement" enforcement engine.

    Workflow Compression (nf wrap): Consolidate update_index, validate, cleanup, dashboard, and sync into one high-level command.
    Semantic Relationship Mapping: Enhance query_index.py to show dependencies (e.g., "File X is used by Tool Y").
    Policy-Based Blocking: If a cloud agent attempts to write to a read_only_for_agents file, nf kills the task locally and immediately.
    Metadata Quality Scoring (Target: 95%): Add stricter scoring in validate_index.py that fails the build if new files lack summaries.
    Security Sandbox: nf runs bandit security scans automatically on every local modification.

📡 Domain 5: Visibility & Performance Watchdog Make NINA proactive in reporting her own health and speed.

    Proactive Telegram Governance Bot: NINA pings the user if hygiene metrics drop or if an autonomous task fails local validation.
    Performance Regression Watcher: Benchmark core functions (Router latency, Memory fetch time) after every merge. Flag regressions.
    Log Memory (ChromaDB): Index nina_update_log.md into NINA's vector memory so agents can "recall" previous fixes.
    Throughput Dashboard: Add a "Throughput" section to the Governance Dashboard tracking "Tasks Closed per Week" and "Tokens Saved via Local Drafting."
    Weekly Hygiene Report: Automated Sunday summary of repo drift and stale files sent via Telegram.

📝 Acceptance Criteria for Jules:

    Local Execution: All generation must use http://localhost:8765 (NinaGate).
    Governance: Every new tool/script must be indexed and have a doc_delta_required: true flag.
    Tests: Provide unit tests for each new nf command.
    Documentation: Update nina_update_log.md with an entry for every module completed.

Jules, you are cleared to proceed. This is a multi-file, multi-subsystem feature. Begin with Domain 1 (Fast-Path & Drafting) to establish the infrastructure for the rest of the work.


### From: jules_spec_doc_compression.md
📝 MEGA-TASK: DOC-COMP Instruction Compression (AG-M-04)
Assignee: Jules (Async Cloud Coder)
Objective: Refactor `AGENTS.md` into a high-density, token-efficient directive list.

🏗️ Domain 1: Structural Compression
- Move verbose "Guides", "Tool Lists", and "Examples" from `AGENTS.md` to dedicated files in `docs/agent-memory/workflow.md` or `docs/agent-memory/patterns.md`.
- Replace these with one-line pointers (e.g., "See docs/patterns.md for log formatting").

🧠 Domain 2: Directive Mapping
- Rewrite the "Rules of Engagement" into high-density "Directive Lists" (Goal-Restraint-Action).
- Example: Replace "Please never use git add ." with "Directive: NEVER use 'git add .'; stage specific files only."

📝 Acceptance Criteria:
- `AGENTS.md` file size reduced by >40%.
- All core constraints preserved.


### From: jules_spec_status_pulse.md
💓 MEGA-TASK: NF-STATUS High-Density Pulse (AG-M-08)
Assignee: Jules (Async Cloud Coder)
Objective: Minimize context bloat by providing a ultra-short project pulse.

🏗️ Domain 1: The Pulse Command
- nf status --pulse: Returns exactly 10 lines containing:
  1. Git SHA + Branch
  2. Venv Status
  3. Last Sync Timestamp
  4. Active Lock Status (jules_lock.txt summary)
  5. Backlog Tally (READY/DONE)
  6. Recent Errors (last 3 from nina_error_register.md)
  7. Thermal/VRAM Status

🧠 Domain 2: Zero-Token Log Parsing
- nf log find-id <task_id>: Return only the log entry associated with a specific task ID without reading the full log file.

📝 Acceptance Criteria:
- Pulse output must be under 1KB.
- Command must be registered as a primary `ninaflash` capability.


### From: jules_spec_surgical_intel.md
🛠️ MEGA-TASK: NF-EXT Surgical Code Intelligence (AG-M-03)
Assignee: Jules (Async Cloud Coder)
Objective: Implement local code research tools in ninaflash to eliminate the need for full-file reads in the cloud.

🏗️ Domain 1: Symbol Extraction
- nf code symbol <file> <name>: Use Python's `ast` module to parse the file and return only the source code for the specified class or function.
- nf find-symbol <name>: Recursively search the repository for where the specified class or function is defined and return its file path and line number.

🧠 Domain 2: Symbol Mapping
- nf code sigs <dir>: Generate a high-density map of all function and class signatures in a directory. Output should include docstrings but skip method bodies.

📉 Domain 3: Docstring Search
- nf code doc <keyword>: Search for keywords only within docstrings to help find relevant tools and logic without full-text grep.

📝 Acceptance Criteria:
- All commands must be implemented as named functions in `ninaflash.py`.
- No new dependencies; use standard library `ast` and `pathlib`.
- Provide unit tests in `tests/test_ninaflash_ext.py`.


### From: jules_spec_gate_prompt.md
📡 MEGA-TASK: GATE-PROMPT System Prompt Templating (AG-M-10)
Assignee: Jules (Async Cloud Coder)
Objective: Shift instruction overhead from every turn's prompt to a cached system template in NinaGate.

🏗️ Domain 1: NinaGate Template Engine
- Update `ninagate/main.py` to support "System Templates." 
- Move the core `AGENTS.md` operating laws into a static JSON template.
- Implement a `/v1/chat/completions` wrapper that injects these templates based on a `X-NINA-ROLE` header.

🧠 Domain 2: Prompt Stripping
- Modify `nina.py` and `agent.py` to strip redundant instructions from the `AgentLoop` prompt if it detects it is running through NinaGate.

📝 Acceptance Criteria:
- Measured reduction in "Input Tokens" per turn.
- Compatibility with all BYOK tools (Aider, Cursor, etc.).


### From: jules_spec_hygiene_fix.md
🧹 MEGA-TASK: NF-CLEAN Automated Hygiene (AG-M-07)
Assignee: Jules (Async Cloud Coder)
Objective: Offload code linting and document formatting from the cloud agent to local ninaflash commands.

🏗️ Domain 1: Code Auto-Fixing
- nf check code --fix: Automatically run `ruff --fix` and `black` (if available) on the target file.
- Implement pre-commit hooks in `ninaflash` that prevent committing code with syntax errors.

🧠 Domain 2: Document Auto-Formatting
- nf doc check --fix: Automatically format the `nina_update_log.md` entry headers and tables to maintain repository standards.
- nf doc consolidate: Automatically move log entries older than 30 days into `exports/nina_update_log_archive.md`.

📝 Acceptance Criteria:
- No human intervention required for common linting/formatting fixes.
- `ninaflash.py` hard cap of 100 functions must be maintained (consolidate where possible).


### From: jules_spec_session_mgmt.md
📦 MEGA-TASK: NF-SESSIONS Checkpoint & Resume (AG-M-12)
Assignee: Jules (Async Cloud Coder)
Objective: Ensure NINA's task state survives Gemini CLI session resets and crashes.

🏗️ Domain 1: Session Checkpointing
- nf session checkpoint: Save the current git branch, changed files, and the active "Goal" to `data/session_checkpoint.json`.
- nf session resume: Read the checkpoint and automatically restore the environment (git branch, re-verify changes).

🧠 Domain 2: Transient Memory
- nf memory stash <text>: Save a snippet of "Working Memory" (e.g., a specific line number or a temporary variable name) to a local JSON stash that persists across CLI restarts.

📝 Acceptance Criteria:
- Checkpoint file must be excluded from `.geminiignore` (it's for me to read).
- `ninaflash.py` implementation must handle JSON serialization errors gracefully.


### From: jules_spec_archive_ops.md
📦 MEGA-TASK: NF-ARCHIVE Historical Offloading (AG-M-09)
Assignee: Jules (Async Cloud Coder)
Objective: Keep the main working documents lean by archiving historical data.

🏗️ Domain 1: Backlog Archiving
- nf backlog archive: Move all tasks with status `DONE` or `DEFERRED` from `docs/space/jules_backlog.md` to `docs/archive/jules_backlog_archive.md`.

🧠 Domain 2: Error Register Archiving
- nf error archive: Move `✅ FIXED` entries from `docs/space/nina_error_register.md` to `exports/nina_error_register_archive.md`.

📝 Acceptance Criteria:
- Archiving must be idempotent.
- Maintain a 10-entry "Recent History" in the main files for immediate context.


### From: jules_spec_log_summary.md
📉 MEGA-TASK: NF-LOG Sliding Window Summarizer (AG-M-11)
Assignee: Jules (Async Cloud Coder)
Objective: Prevent context overflow from noisy logs and long markdown files.

🏗️ Domain 1: Log Compression
- nf log summarize: Use a local tiny-model (via NinaGate) or regex patterns to collapse repeating log patterns.
- Implement a sliding window for `nina_update_log.md` where the agent only sees the "Relevant Window" (last 10 entries + task-specific entries).

🧠 Domain 2: Tool Log Rotation
- nf ops rotate-logs: Automatically compress and archive `logs/*.log` into `logs/archive/` using gzip.

📝 Acceptance Criteria:
- Log summarization must preserve all Entry IDs and Dates.
- Integration with `compact_exporter.py` to ensure `nina_latest.md` stays under 64KB.


### From: nina_docs_revamp_jules_spec.md
# Jules Task Spec: NINA Documentation Revamp
**Task ID:** DOCS-001  
**Type:** Documentation  
**Priority:** High  
**Assigned To:** Jules (Async Cloud Coder)  
**Reviewed By:** Perplexity (Architect)  
**Branch:** `jules/docs-001-documentation-revamp`  
**Date:** 2026-06-09

---

## Overview

The current NINA documentation does not reflect the actual system architecture. `README.md` describes an outdated v1.0 Telegram bot with no mention of agynina, Jules, or the Universe-Mode kernel. This spec instructs Jules to perform a full documentation revamp — rewriting core docs, creating missing architecture files, and reorganizing log files out of the repo root.

**Constraint:** Do NOT modify any `.py`, `.sh`, `.service`, `.env`, `.json`, or `.txt` files. Documentation changes only.

---

## Task Batch

### Batch 1 — Rewrite README.md

**File:** `README.md`  
**Action:** Full rewrite. Replace current content entirely.

**Target length:** ~15KB  
**Target audience:** A new developer (or Jules itself on a fresh task) who needs to understand NINA in under 5 minutes.

**Required sections:**

#### 1. Title & Tagline
```
# NINA — Neural Intelligent Network Assistant
```
Tagline: *A self-hosted, self-developing autonomous AI OS running on Ubuntu 26.04.*

#### 2. What is NINA?
One paragraph explaining NINA is NOT a chatbot. It is an action-first autonomous agent that:
- Routes tasks across 20+ AI providers via HybridRouter V4
- Develops itself autonomously via Jules + agynina pipeline
- Manages email (EWS), monitors markets (DSE/CSE), handles finance, and self-repairs
- Keeps all banking and sensitive data strictly on the local machine in Dhaka

#### 3. Three-Tier Agent Model (the heart of NINA's architecture)
A table + narrative explaining the three parallel agents:

| Agent | Role | Backend | Scope |
|---|---|---|---|
| Perplexity Enterprise Pro | Architect + Overwatch | Claude Sonnet 4.6 | Strategic direction, specs, post-execution review |
| Jules (jules.google.com) | Async Cloud Coder | Gemini 3.1 Pro | Multi-file feature builds, submits PRs |
| agynina (Antigravity CLI) | Local Executor | Gemini Flash | Hotfixes, PR merges, deploys, syncs |

Narrative: Explain that Jules builds features asynchronously in the cloud. agynina reviews and merges Jules' PRs locally. Perplexity architects before and reviews after. Nobody does manual coding.

#### 4. agynina — The Local Executor
Explain agynina's role as NINA's local muscle:
- CLI tool at `bin/agynina` (Antigravity CLI, v1.0.5)
- Powered by Claude Sonnet 4.6 Thinking
- Commands:
  - `agynina status` — checks locks, git workspace, backlog
  - `agynina pr merge <PR>` — lint check → merge → sync → backlog update
  - `agynina dispatch <TASK_ID>` — locks files → IN_PROGRESS → sends to Jules API
  - `agynina aider <TASK_ID>` — launches aider with task context
  - `agynina doctor` — finds latest Python traceback in logs
  - `agynina ninaloop` — activates continuous autonomous developer loop

#### 5. Universe-Mode Kernel (agynina v8.0)
Explain the kernel architecture:
- **Nucleus:** 1,001 core functions (`tools/agynina.py`)
- **Synapses:** 1,000,000 specialized Neural Op-Codes across 1,000 sector files (`tools/kernel/sector_000.py` → `sector_999.py`)
- **Omniscient Dispatcher:** Dynamic on-demand sector loader — executes any op-code without loading all sectors into memory
- Purpose: Gives agynina near-infinite local skill capability at zero cloud token cost

#### 6. HybridRouter V4
Describe the routing engine in `core/router.py`:
- Routes across 19+ cloud providers (Groq, Gemini, Cerebras, DeepSeek, Mistral, OpenRouter, Together, Cohere, Fireworks, xAI, SambaNova, Hyperbolic, Novita, Perplexity, OpenAI, Pollinations, Chutes, and more)
- 2 local models via Ollama (qwen2.5:1.5b for fast tasks, qwen2.5:7b for heavy reasoning)
- CircuitBreaker pattern prevents cascading failures
- Weighted scoring: success rate × latency × rate limits
- Free-tier first routing philosophy

#### 7. Guardian Gate
Describe the safety pipeline in `guardian_engine.py`:
- AST (Abstract Syntax Tree) scan on every patch
- Baseline drift analysis against `upgrades/guardian_baseline.json`
- Syntax + linter checks (`py_compile` + `pyflakes`)
- Verification workflow: Verify → Log (`nina_update_log.md`) → Sync (`nina_sync.sh`)
- Single-instance locking via `jules_lock.txt` — prevents Jules and agynina from colliding

#### 8. Memory System
Describe `core/memory.py`:
- **ChromaDB** — semantic/vector recall for episodic memory (what happened when)
- **facts.json** (`data/memory/facts.json`) — hardcoded personal identity anchor, prevents context drift

#### 9. Technical Stack
| Component | Detail |
|---|---|
| Runtime | Python 3.14, asyncio-based |
| OS | Ubuntu 26.04, systemd managed |
| Primary UI | Telegram bot (Gatekeeper) |
| CLI | `bin/agynina` |
| Local Models | Ollama: qwen2.5:1.5b, qwen2.5:7b |
| Services | `nina.service`, `nina-dashboard.service` |
| Dev Stack | Perplexity + Jules + agynina (parallel) |

#### 10. Tool Quota Cascade (Daily)
| Tool | Model | Daily Quota | Reset |
|---|---|---|---|
| agynina (agy) | Gemini Flash | ~5h rolling | Rolling |
| Qwen Code CLI | Qwen3-Coder-480B | 2,000 req/day | Daily |
| Jules | Gemini 3.1 Pro | 100 tasks/day | Rolling 24h |
| Cursor Hobby | GPT-4o mini | 50 chat/month | Monthly |
| Ollama | Local | Unlimited | — |

Cascade order: `agy → Qwen Code → Jules (async) → Cursor → Ollama`

#### 11. Autonomous Development Loop (How NINA Builds Itself)
Step-by-step narrative:
1. Perplexity drafts spec with precise requirements
2. Jules receives spec → builds async in cloud VM (no interaction after submit)
3. agynina handles urgent local fixes in parallel (separate worktree)
4. Jules opens PR when feature is complete
5. agynina runs Guardian lint/compile checks on the PR diff
6. agynina merges PR → runs `./nina_sync.sh` → deploys to systemd
7. Perplexity reviews result in new thread

#### 12. Project Structure (Updated)
```
nina/
├── main.py                    # Entry point
├── guardian                   # Guardian watchdog script
├── guardian_engine.py         # Guardian AST + forensic engine (73KB)
├── healthcheck.py             # System health monitor
├── idleloop.py                # Background idle proposals
├── core/
│   ├── agent.py               # AgentLoop: THINK-PLAN-ACT + thermal guard
│   ├── config.py              # NinaConfig + rate limits
│   ├── memory.py              # ChromaDB + facts.json memory
│   ├── router.py              # HybridRouter V4 + CircuitBreaker
│   ├── nina.py                # NinaOS orchestrator
│   ├── capabilities.py        # Capability registry
│   └── hotreload.py           # Live config reload
├── tools/
│   ├── agynina.py             # Universe-Mode kernel (Nucleus: 1,001 functions)
│   ├── kernel/
│   │   ├── sector_000.py      # Neural Op-Code sectors (1,000 files)
│   │   └── sector_999.py      # 1,000,000 total op-codes
│   ├── browser.py             # Web browsing
│   ├── search.py              # Web search
│   ├── shell.py               # Shell execution (allowlisted)
│   ├── files.py               # File operations
│   ├── system.py              # System monitoring
│   ├── gputuner.py            # GPU management
│   ├── officemail.py          # EWS email (Exchange/NTLM)
│   └── upgradepipeline.py     # Self-upgrade system
├── interfaces/
│   ├── api.py                 # REST API (Phase 2)
│   └── telegram_interface.py  # Telegram bot + security gate
├── bin/
│   └── agynina                # agynina CLI entry point
├── crons/
│   ├── manager.py             # Cron job manager
│   └── backup_jobs.py         # Scheduled backups
├── dashboard/
│   └── nina-guardian.html     # Web dashboard
├── docs/
│   ├── agynina.md             # agynina architecture (NEW)
│   ├── router.md              # HybridRouter V4 deep-dive (NEW)
│   ├── guardian.md            # Guardian Gate pipeline (NEW)
│   ├── memory.md              # Memory system (NEW)
│   └── space/                 # Task tracker, backlog, context
├── upgrades/
│   └── guardian_baseline.json # Guardian integrity baseline
├── data/
│   └── memory/
│       └── facts.json         # Identity anchor (DO NOT MODIFY)
├── AGENTS.md                  # Agent operating law (canonical)
├── ARCHITECTURE.md            # System architecture overview (NEW)
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Contribution guide
├── WORKFLOW.md                # Dev workflow
├── SECURITY.md                # Security policy
├── requirements.txt
├── jules_lock.txt             # Active file lock registry
├── nina.service               # systemd unit
└── nina-dashboard.service     # systemd dashboard unit
```

#### 13. Installation
Keep current installation section (it is accurate).

#### 14. Supported AI Providers
Keep current providers table (it is accurate). Add a note that `routing is handled automatically by HybridRouter V4 with free-tier priority`.

#### 15. License & Author
Keep current content.

---

### Batch 2 — Create ARCHITECTURE.md

**File:** `ARCHITECTURE.md`  
**Action:** Create new file.  
**Target length:** ~8KB

**Content:**

Title: `# NINA Architecture`

Sections:

1. **System Overview** — One paragraph. NINA is a three-tier autonomous agentic OS. Not a chatbot. Action-first.

2. **Architecture Diagram** (ASCII)
```
┌─────────────────────────────────────────────────────────────┐
│                    NINA Ecosystem                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Perplexity  │    │    Jules     │    │   agynina    │  │
│  │  Enterprise  │    │  (Cloud VM)  │    │(Antigravity) │  │
│  │    Pro       │    │Gemini 3.1 Pro│    │Gemini Flash  │  │
│  │              │    │              │    │              │  │
│  │  ARCHITECT   │    │ASYNC BUILDER │    │LOCAL MUSCLE  │  │
│  │  + OVERWATCH │    │              │    │              │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │ specs             │ PRs               │ merges   │
│         │                  ▼                   │          │
│         │           ┌──────────────┐           │          │
│         │           │   GitHub     │◄──────────┘          │
│         │           │  (PR Gate)   │                      │
│         │           └──────┬───────┘                      │
│         │                  │ merged                       │
│         │                  ▼                              │
│         │         ┌────────────────┐                      │
│         └────────►│  NINA (Live)   │                      │
│          review   │  systemd svc   │                      │
│                   └────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

3. **Component Deep-Dives** — For each: agynina Universe-Mode Kernel, HybridRouter V4, AgentLoop (THINK-PLAN-ACT), Guardian Gate, Memory System. Each gets 3-5 sentences describing what it does, where it lives, and why it exists.

4. **Data Flow** — How a Telegram message becomes an action. Telegram → `telegram_interface.py` → `AgentLoop` → `HybridRouter` → Provider → Response → Telegram.

5. **Safety Architecture** — Guardian Gate, jules_lock.txt, shell allowlist, local-only routing for sensitive paths.

6. **Deployment Architecture** — systemd services, Ollama local models, worktree branching strategy.

---

### Batch 3 — Create docs/agynina.md

**File:** `docs/agynina.md`  
**Action:** Create new file.  
**Target length:** ~5KB

Content must cover:
- What agynina is (Local Executor, not just a tool)
- agynina CLI commands (all 6 listed in Batch 1, Section 4)
- Universe-Mode Kernel architecture (Nucleus + Synapses + Dispatcher)
- How agynina integrates with Jules (review → merge → deploy loop)
- How agynina integrates with Antigravity CLI
- Token cost model (agynina absorbs routine work at near-zero token cost)
- `ninaloop` — the continuous autonomous developer loop

---

### Batch 4 — Create docs/guardian.md

**File:** `docs/guardian.md`  
**Action:** Create new file.  
**Target length:** ~4KB

Content must cover:
- Purpose: forensic safety layer for autonomous self-patching
- Components: `guardian` (watchdog script), `guardian_engine.py` (73KB AST engine)
- Verification pipeline: AST scan → baseline drift check → py_compile → pyflakes → log → sync
- Guardian baseline: `upgrades/guardian_baseline.json`
- Log: `nina_update_log.md`
- Sync: `nina_sync.sh`
- High-risk files that always route through Guardian
- Recommended enhancement: auto-rollback on drift detection via `git reset --hard`

---

### Batch 5 — Create docs/router.md

**File:** `docs/router.md`  
**Action:** Create new file.  
**Target length:** ~4KB

Content must cover:
- HybridRouter V4 location: `core/router.py`
- Provider list (all 19+ cloud + 2 Ollama local)
- Routing algorithm: weighted scoring (success rate × latency × rate limits)
- CircuitBreaker pattern: how it prevents hammering a failed provider
- Free-tier priority philosophy
- Rate limit tracking: RPM, RPD, TPD per provider
- Local model routing for sensitive/banking data paths

---

### Batch 6 — Create docs/memory.md

**File:** `docs/memory.md`  
**Action:** Create new file.  
**Target length:** ~3KB

Content must cover:
- `core/memory.py` — the memory orchestrator
- ChromaDB: semantic vector store for episodic recall
- `data/memory/facts.json`: hardcoded identity anchor (personal facts, prevents context drift)
- Why dual-memory matters: episodic + identity = persistent agent personality
- What NOT to touch: facts.json is a protected file (listed in Guardian high-risk list)
- Recommended enhancement: short-term working memory / scratchpad layer for in-flight AgentLoop state

---

### Batch 7 — Update WORKFLOW.md

**File:** `WORKFLOW.md`  
**Action:** Rewrite to reflect current Jules + agynina pipeline.

**Must include:**
1. Standard session start checklist (from AGENTS.md)
2. Jules dispatch → PR → agynina merge → sync cycle
3. Worktree branching strategy (main / local/ / jules/)
4. Quota cascade order: `agy → Qwen Code → Jules → Cursor → Ollama`
5. After-task mandatory steps: update task tracker, run `./nina_sync.sh`

---

### Batch 8 — Expand SECURITY.md

**File:** `SECURITY.md`  
**Action:** Expand from 129 bytes to ~2KB.

**Must include:**
- Local-only data philosophy (banking data never leaves machine)
- High-risk files list (mirror from AGENTS.md)
- Guardian Gate as security enforcement mechanism
- Shell allowlist in `tools/shell.py`
- Telegram as authenticated gatekeeper (authorized_user_id only)
- No secrets in code — `.env` only
- `facts.json` and `guardian_baseline.json` are immutable via agent

---

### Batch 9 — Move Log Files

**Files to move:**
- `nina_update_log.md` → `docs/logs/nina_update_log.md`
- `nina_problem_log.md` → `docs/logs/nina_problem_log.md`
- `nina_phase1_roadmap.md` → `docs/roadmap/nina_phase1_roadmap.md`

**Action:** Move files using `git mv`. Update any references to these files in AGENTS.md and README.md to reflect new paths.

**Rationale:** These files are operational noise in the repo root. They inflate context windows for every agent reading the root directory. Moving them to `docs/logs/` and `docs/roadmap/` preserves history while decluttering the working directory.

---

## Constraints & Rules

1. **Do NOT modify any `.py`, `.sh`, `.service`, `.env`, `.json`, or `.txt` files** — documentation only
2. **Do NOT auto-merge** — open PR only; agynina will review and merge
3. **Stage specific files only** — never `git add .`
4. **Run `python3 -m py_compile` on any accidentally modified .py file** before committing
5. **One commit per batch** — 9 commits total, one per batch
6. **Conventional commit format:**
   - `docs(README): rewrite to reflect three-tier agent architecture (DOCS-001-B1)`
   - `docs(ARCHITECTURE): create system architecture overview (DOCS-001-B2)`
   - `docs(agynina): create agynina subsystem documentation (DOCS-001-B3)`
   - etc.
7. **Check `jules_lock.txt`** before starting — confirm no .md files are currently locked
8. **Open PR** when all 9 batches are committed. Title: `docs: NINA documentation revamp (DOCS-001)`

---

## Verification (Before Opening PR)

For each created/modified `.md` file, verify:
- [ ] Valid Markdown syntax (no broken tables, unclosed code blocks)
- [ ] All internal file paths referenced exist in the repo
- [ ] No `.py` files were touched
- [ ] Commit count = 9 (one per batch)
- [ ] PR title follows convention: `docs: NINA documentation revamp (DOCS-001)`

---

## Expected Output

A single PR containing:
- `README.md` — rewritten (~15KB)
- `ARCHITECTURE.md` — new file (~8KB)
- `docs/agynina.md` — new file (~5KB)
- `docs/guardian.md` — new file (~4KB)
- `docs/router.md` — new file (~4KB)
- `docs/memory.md` — new file (~3KB)
- `WORKFLOW.md` — rewritten (~3KB)
- `SECURITY.md` — expanded (~2KB)
- `docs/logs/nina_update_log.md` — moved from root
- `docs/logs/nina_problem_log.md` — moved from root
- `docs/roadmap/nina_phase1_roadmap.md` — moved from root

**Total new documentation: ~44KB of accurate, architecture-aligned docs**  
**Root directory cleanup: 3 large log/roadmap files removed from root**

---

## Post-Merge Actions (agynina)

After merging this PR:
1. Update `docs/space/jules_task_tracker.md` — set DOCS-001 to ✅ DONE
2. Update `docs/space/jules_backlog.md` — set status to DONE with PR number and date
3. Run `./nina_sync.sh`
4. Report completion to Perplexity for post-merge review

---

*Spec authored by: Perplexity Enterprise Pro (Architect)*  
*Task assigned to: Jules (Cloud Coder)*  
*Merge executor: agynina (Local Executor)*  
*Date: 2026-06-09*


### From: nina_docs_revamp_jules_spec(1).md
# Jules Task Spec: NINA Documentation Revamp
**Task ID:** DOCS-001  
**Type:** Documentation  
**Priority:** High  
**Assigned To:** Jules (Async Cloud Coder)  
**Reviewed By:** Perplexity (Architect)  
**Branch:** `jules/docs-001-documentation-revamp`  
**Date:** 2026-06-09

---

## Overview

The current NINA documentation does not reflect the actual system architecture. `README.md` describes an outdated v1.0 Telegram bot with no mention of agynina, Jules, or the Universe-Mode kernel. This spec instructs Jules to perform a full documentation revamp — rewriting core docs, creating missing architecture files, and reorganizing log files out of the repo root.

**Constraint:** Do NOT modify any `.py`, `.sh`, `.service`, `.env`, `.json`, or `.txt` files. Documentation changes only.

---

## Task Batch

### Batch 1 — Rewrite README.md

**File:** `README.md`  
**Action:** Full rewrite. Replace current content entirely.

**Target length:** ~15KB  
**Target audience:** A new developer (or Jules itself on a fresh task) who needs to understand NINA in under 5 minutes.

**Required sections:**

#### 1. Title & Tagline
```
# NINA — Neural Intelligent Network Assistant
```
Tagline: *A self-hosted, self-developing autonomous AI OS running on Ubuntu 26.04.*

#### 2. What is NINA?
One paragraph explaining NINA is NOT a chatbot. It is an action-first autonomous agent that:
- Routes tasks across 20+ AI providers via HybridRouter V4
- Develops itself autonomously via Jules + agynina pipeline
- Manages email (EWS), monitors markets (DSE/CSE), handles finance, and self-repairs
- Keeps all banking and sensitive data strictly on the local machine in Dhaka

#### 3. Three-Tier Agent Model (the heart of NINA's architecture)
A table + narrative explaining the three parallel agents:

| Agent | Role | Backend | Scope |
|---|---|---|---|
| Perplexity Enterprise Pro | Architect + Overwatch | Claude Sonnet 4.6 | Strategic direction, specs, post-execution review |
| Jules (jules.google.com) | Async Cloud Coder | Gemini 3.1 Pro | Multi-file feature builds, submits PRs |
| agynina (Antigravity CLI) | Local Executor | Gemini Flash | Hotfixes, PR merges, deploys, syncs |

Narrative: Explain that Jules builds features asynchronously in the cloud. agynina reviews and merges Jules' PRs locally. Perplexity architects before and reviews after. Nobody does manual coding.

#### 4. agynina — The Local Executor
Explain agynina's role as NINA's local muscle:
- CLI tool at `bin/agynina` (Antigravity CLI, v1.0.5)
- Powered by Claude Sonnet 4.6 Thinking
- Commands:
  - `agynina status` — checks locks, git workspace, backlog
  - `agynina pr merge <PR>` — lint check → merge → sync → backlog update
  - `agynina dispatch <TASK_ID>` — locks files → IN_PROGRESS → sends to Jules API
  - `agynina aider <TASK_ID>` — launches aider with task context
  - `agynina doctor` — finds latest Python traceback in logs
  - `agynina ninaloop` — activates continuous autonomous developer loop

#### 5. Universe-Mode Kernel (agynina v8.0)
Explain the kernel architecture:
- **Nucleus:** 1,001 core functions (`tools/agynina.py`)
- **Synapses:** 1,000,000 specialized Neural Op-Codes across 1,000 sector files (`tools/kernel/sector_000.py` → `sector_999.py`)
- **Omniscient Dispatcher:** Dynamic on-demand sector loader — executes any op-code without loading all sectors into memory
- Purpose: Gives agynina near-infinite local skill capability at zero cloud token cost

#### 6. HybridRouter V4
Describe the routing engine in `core/router.py`:
- Routes across 19+ cloud providers (Groq, Gemini, Cerebras, DeepSeek, Mistral, OpenRouter, Together, Cohere, Fireworks, xAI, SambaNova, Hyperbolic, Novita, Perplexity, OpenAI, Pollinations, Chutes, and more)
- 2 local models via Ollama (qwen2.5:1.5b for fast tasks, qwen2.5:7b for heavy reasoning)
- CircuitBreaker pattern prevents cascading failures
- Weighted scoring: success rate × latency × rate limits
- Free-tier first routing philosophy

#### 7. Guardian Gate
Describe the safety pipeline in `guardian_engine.py`:
- AST (Abstract Syntax Tree) scan on every patch
- Baseline drift analysis against `upgrades/guardian_baseline.json`
- Syntax + linter checks (`py_compile` + `pyflakes`)
- Verification workflow: Verify → Log (`nina_update_log.md`) → Sync (`nina_sync.sh`)
- Single-instance locking via `jules_lock.txt` — prevents Jules and agynina from colliding

#### 8. Memory System
Describe `core/memory.py`:
- **ChromaDB** — semantic/vector recall for episodic memory (what happened when)
- **facts.json** (`data/memory/facts.json`) — hardcoded personal identity anchor, prevents context drift

#### 9. Technical Stack
| Component | Detail |
|---|---|
| Runtime | Python 3.14, asyncio-based |
| OS | Ubuntu 26.04, systemd managed |
| Primary UI | Telegram bot (Gatekeeper) |
| CLI | `bin/agynina` |
| Local Models | Ollama: qwen2.5:1.5b, qwen2.5:7b |
| Services | `nina.service`, `nina-dashboard.service` |
| Dev Stack | Perplexity + Jules + agynina (parallel) |

#### 10. Tool Quota Cascade (Daily)
| Tool | Model | Daily Quota | Reset |
|---|---|---|---|
| agynina (agy) | Gemini Flash | ~5h rolling | Rolling |
| Qwen Code CLI | Qwen3-Coder-480B | 2,000 req/day | Daily |
| Jules | Gemini 3.1 Pro | 100 tasks/day | Rolling 24h |
| Cursor Hobby | GPT-4o mini | 50 chat/month | Monthly |
| Ollama | Local | Unlimited | — |

Cascade order: `agy → Qwen Code → Jules (async) → Cursor → Ollama`

#### 11. Autonomous Development Loop (How NINA Builds Itself)
Step-by-step narrative:
1. Perplexity drafts spec with precise requirements
2. Jules receives spec → builds async in cloud VM (no interaction after submit)
3. agynina handles urgent local fixes in parallel (separate worktree)
4. Jules opens PR when feature is complete
5. agynina runs Guardian lint/compile checks on the PR diff
6. agynina merges PR → runs `./nina_sync.sh` → deploys to systemd
7. Perplexity reviews result in new thread

#### 12. Project Structure (Updated)
```
nina/
├── main.py                    # Entry point
├── guardian                   # Guardian watchdog script
├── guardian_engine.py         # Guardian AST + forensic engine (73KB)
├── healthcheck.py             # System health monitor
├── idleloop.py                # Background idle proposals
├── core/
│   ├── agent.py               # AgentLoop: THINK-PLAN-ACT + thermal guard
│   ├── config.py              # NinaConfig + rate limits
│   ├── memory.py              # ChromaDB + facts.json memory
│   ├── router.py              # HybridRouter V4 + CircuitBreaker
│   ├── nina.py                # NinaOS orchestrator
│   ├── capabilities.py        # Capability registry
│   └── hotreload.py           # Live config reload
├── tools/
│   ├── agynina.py             # Universe-Mode kernel (Nucleus: 1,001 functions)
│   ├── kernel/
│   │   ├── sector_000.py      # Neural Op-Code sectors (1,000 files)
│   │   └── sector_999.py      # 1,000,000 total op-codes
│   ├── browser.py             # Web browsing
│   ├── search.py              # Web search
│   ├── shell.py               # Shell execution (allowlisted)
│   ├── files.py               # File operations
│   ├── system.py              # System monitoring
│   ├── gputuner.py            # GPU management
│   ├── officemail.py          # EWS email (Exchange/NTLM)
│   └── upgradepipeline.py     # Self-upgrade system
├── interfaces/
│   ├── api.py                 # REST API (Phase 2)
│   └── telegram_interface.py  # Telegram bot + security gate
├── bin/
│   └── agynina                # agynina CLI entry point
├── crons/
│   ├── manager.py             # Cron job manager
│   └── backup_jobs.py         # Scheduled backups
├── dashboard/
│   └── nina-guardian.html     # Web dashboard
├── docs/
│   ├── agynina.md             # agynina architecture (NEW)
│   ├── router.md              # HybridRouter V4 deep-dive (NEW)
│   ├── guardian.md            # Guardian Gate pipeline (NEW)
│   ├── memory.md              # Memory system (NEW)
│   └── space/                 # Task tracker, backlog, context
├── upgrades/
│   └── guardian_baseline.json # Guardian integrity baseline
├── data/
│   └── memory/
│       └── facts.json         # Identity anchor (DO NOT MODIFY)
├── AGENTS.md                  # Agent operating law (canonical)
├── ARCHITECTURE.md            # System architecture overview (NEW)
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Contribution guide
├── WORKFLOW.md                # Dev workflow
├── SECURITY.md                # Security policy
├── requirements.txt
├── jules_lock.txt             # Active file lock registry
├── nina.service               # systemd unit
└── nina-dashboard.service     # systemd dashboard unit
```

#### 13. Installation
Keep current installation section (it is accurate).

#### 14. Supported AI Providers
Keep current providers table (it is accurate). Add a note that `routing is handled automatically by HybridRouter V4 with free-tier priority`.

#### 15. License & Author
Keep current content.

---

### Batch 2 — Create ARCHITECTURE.md

**File:** `ARCHITECTURE.md`  
**Action:** Create new file.  
**Target length:** ~8KB

**Content:**

Title: `# NINA Architecture`

Sections:

1. **System Overview** — One paragraph. NINA is a three-tier autonomous agentic OS. Not a chatbot. Action-first.

2. **Architecture Diagram** (ASCII)
```
┌─────────────────────────────────────────────────────────────┐
│                    NINA Ecosystem                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Perplexity  │    │    Jules     │    │   agynina    │  │
│  │  Enterprise  │    │  (Cloud VM)  │    │(Antigravity) │  │
│  │    Pro       │    │Gemini 3.1 Pro│    │Gemini Flash  │  │
│  │              │    │              │    │              │  │
│  │  ARCHITECT   │    │ASYNC BUILDER │    │LOCAL MUSCLE  │  │
│  │  + OVERWATCH │    │              │    │              │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │ specs             │ PRs               │ merges   │
│         │                  ▼                   │          │
│         │           ┌──────────────┐           │          │
│         │           │   GitHub     │◄──────────┘          │
│         │           │  (PR Gate)   │                      │
│         │           └──────┬───────┘                      │
│         │                  │ merged                       │
│         │                  ▼                              │
│         │         ┌────────────────┐                      │
│         └────────►│  NINA (Live)   │                      │
│          review   │  systemd svc   │                      │
│                   └────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

3. **Component Deep-Dives** — For each: agynina Universe-Mode Kernel, HybridRouter V4, AgentLoop (THINK-PLAN-ACT), Guardian Gate, Memory System. Each gets 3-5 sentences describing what it does, where it lives, and why it exists.

4. **Data Flow** — How a Telegram message becomes an action. Telegram → `telegram_interface.py` → `AgentLoop` → `HybridRouter` → Provider → Response → Telegram.

5. **Safety Architecture** — Guardian Gate, jules_lock.txt, shell allowlist, local-only routing for sensitive paths.

6. **Deployment Architecture** — systemd services, Ollama local models, worktree branching strategy.

---

### Batch 3 — Create docs/agynina.md

**File:** `docs/agynina.md`  
**Action:** Create new file.  
**Target length:** ~5KB

Content must cover:
- What agynina is (Local Executor, not just a tool)
- agynina CLI commands (all 6 listed in Batch 1, Section 4)
- Universe-Mode Kernel architecture (Nucleus + Synapses + Dispatcher)
- How agynina integrates with Jules (review → merge → deploy loop)
- How agynina integrates with Antigravity CLI
- Token cost model (agynina absorbs routine work at near-zero token cost)
- `ninaloop` — the continuous autonomous developer loop

---

### Batch 4 — Create docs/guardian.md

**File:** `docs/guardian.md`  
**Action:** Create new file.  
**Target length:** ~4KB

Content must cover:
- Purpose: forensic safety layer for autonomous self-patching
- Components: `guardian` (watchdog script), `guardian_engine.py` (73KB AST engine)
- Verification pipeline: AST scan → baseline drift check → py_compile → pyflakes → log → sync
- Guardian baseline: `upgrades/guardian_baseline.json`
- Log: `nina_update_log.md`
- Sync: `nina_sync.sh`
- High-risk files that always route through Guardian
- Recommended enhancement: auto-rollback on drift detection via `git reset --hard`

---

### Batch 5 — Create docs/router.md

**File:** `docs/router.md`  
**Action:** Create new file.  
**Target length:** ~4KB

Content must cover:
- HybridRouter V4 location: `core/router.py`
- Provider list (all 19+ cloud + 2 Ollama local)
- Routing algorithm: weighted scoring (success rate × latency × rate limits)
- CircuitBreaker pattern: how it prevents hammering a failed provider
- Free-tier priority philosophy
- Rate limit tracking: RPM, RPD, TPD per provider
- Local model routing for sensitive/banking data paths

---

### Batch 6 — Create docs/memory.md

**File:** `docs/memory.md`  
**Action:** Create new file.  
**Target length:** ~3KB

Content must cover:
- `core/memory.py` — the memory orchestrator
- ChromaDB: semantic vector store for episodic recall
- `data/memory/facts.json`: hardcoded identity anchor (personal facts, prevents context drift)
- Why dual-memory matters: episodic + identity = persistent agent personality
- What NOT to touch: facts.json is a protected file (listed in Guardian high-risk list)
- Recommended enhancement: short-term working memory / scratchpad layer for in-flight AgentLoop state

---

### Batch 7 — Update WORKFLOW.md

**File:** `WORKFLOW.md`  
**Action:** Rewrite to reflect current Jules + agynina pipeline.

**Must include:**
1. Standard session start checklist (from AGENTS.md)
2. Jules dispatch → PR → agynina merge → sync cycle
3. Worktree branching strategy (main / local/ / jules/)
4. Quota cascade order: `agy → Qwen Code → Jules → Cursor → Ollama`
5. After-task mandatory steps: update task tracker, run `./nina_sync.sh`

---

### Batch 8 — Expand SECURITY.md

**File:** `SECURITY.md`  
**Action:** Expand from 129 bytes to ~2KB.

**Must include:**
- Local-only data philosophy (banking data never leaves machine)
- High-risk files list (mirror from AGENTS.md)
- Guardian Gate as security enforcement mechanism
- Shell allowlist in `tools/shell.py`
- Telegram as authenticated gatekeeper (authorized_user_id only)
- No secrets in code — `.env` only
- `facts.json` and `guardian_baseline.json` are immutable via agent

---

### Batch 9 — Move Log Files

**Files to move:**
- `nina_update_log.md` → `docs/logs/nina_update_log.md`
- `nina_problem_log.md` → `docs/logs/nina_problem_log.md`
- `nina_phase1_roadmap.md` → `docs/roadmap/nina_phase1_roadmap.md`

**Action:** Move files using `git mv`. Update any references to these files in AGENTS.md and README.md to reflect new paths.

**Rationale:** These files are operational noise in the repo root. They inflate context windows for every agent reading the root directory. Moving them to `docs/logs/` and `docs/roadmap/` preserves history while decluttering the working directory.

---

## Constraints & Rules

1. **Do NOT modify any `.py`, `.sh`, `.service`, `.env`, `.json`, or `.txt` files** — documentation only
2. **Do NOT auto-merge** — open PR only; agynina will review and merge
3. **Stage specific files only** — never `git add .`
4. **Run `python3 -m py_compile` on any accidentally modified .py file** before committing
5. **One commit per batch** — 9 commits total, one per batch
6. **Conventional commit format:**
   - `docs(README): rewrite to reflect three-tier agent architecture (DOCS-001-B1)`
   - `docs(ARCHITECTURE): create system architecture overview (DOCS-001-B2)`
   - `docs(agynina): create agynina subsystem documentation (DOCS-001-B3)`
   - etc.
7. **Check `jules_lock.txt`** before starting — confirm no .md files are currently locked
8. **Open PR** when all 9 batches are committed. Title: `docs: NINA documentation revamp (DOCS-001)`

---

## Verification (Before Opening PR)

For each created/modified `.md` file, verify:
- [ ] Valid Markdown syntax (no broken tables, unclosed code blocks)
- [ ] All internal file paths referenced exist in the repo
- [ ] No `.py` files were touched
- [ ] Commit count = 9 (one per batch)
- [ ] PR title follows convention: `docs: NINA documentation revamp (DOCS-001)`

---

## Expected Output

A single PR containing:
- `README.md` — rewritten (~15KB)
- `ARCHITECTURE.md` — new file (~8KB)
- `docs/agynina.md` — new file (~5KB)
- `docs/guardian.md` — new file (~4KB)
- `docs/router.md` — new file (~4KB)
- `docs/memory.md` — new file (~3KB)
- `WORKFLOW.md` — rewritten (~3KB)
- `SECURITY.md` — expanded (~2KB)
- `docs/logs/nina_update_log.md` — moved from root
- `docs/logs/nina_problem_log.md` — moved from root
- `docs/roadmap/nina_phase1_roadmap.md` — moved from root

**Total new documentation: ~44KB of accurate, architecture-aligned docs**  
**Root directory cleanup: 3 large log/roadmap files removed from root**

---

## Post-Merge Actions (agynina)

After merging this PR:
1. Update `docs/space/jules_task_tracker.md` — set DOCS-001 to ✅ DONE
2. Update `docs/space/jules_backlog.md` — set status to DONE with PR number and date
3. Run `./nina_sync.sh`
4. Report completion to Perplexity for post-merge review

---

*Spec authored by: Perplexity Enterprise Pro (Architect)*  
*Task assigned to: Jules (Cloud Coder)*  
*Merge executor: agynina (Local Executor)*  
*Date: 2026-06-09*



---

## 📅 Scheduled Tasks (SCHED)

### From: nina_jules_scheduled_tasks.md
# NINA — Jules UI Scheduled Tasks (All 15)
> Repo: `aibony/nina` | Pro Plan: 100 tasks/day, 15 concurrent | Last updated: 2026-06-07
>
> **How to use:** Go to jules.google.com → select `aibony/nina` → paste prompt → Planning dropdown → Scheduled Task → set cadence shown for each task.
>
> **Budget math:** On the heaviest day (1st of month), 8 tasks fire = 8/100 daily budget used. All other days: 3–5 tasks max. ~85 tasks/day remain for interactive work.

---

## DAILY TASKS (fire every day)

---

### TASK 1 — Daily Lint & Syntax Sweep
**Cadence:** Daily · 02:00 AM (server local time)
**Jules UI Schedule:** Every day

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Daily automated lint and syntax sweep.

STEPS:
1. Activate venv: source ~/nina/venv/bin/activate
2. Run: python3 -m py_compile on every .py file under ~/nina/ (excluding venv/, __pycache__, .git)
   Collect any files that fail with their error message.
3. Run: pyflakes on every .py file under ~/nina/ (same exclusions)
   Collect all warnings and errors.
4. If zero issues found: do NOT open a PR. Exit silently.
5. If issues found: open a PR titled "fix(lint): daily sweep found N issues — [YYYY-MM-DD]"
   PR body must list each file + error on its own line.
   Do NOT attempt to fix the issues — report only.
6. Append entry to nina_update_log.md via Python (not bash echo):
   Format: E-XXX | chore(lint): daily sweep [YYYY-MM-DD] — N issues found

DO NOT touch: .env, juleslock.txt, guardian_engine.py, tools/shell.py, interfaces/telegram_interface.py
DO NOT auto-fix any errors — report only.
```

---

### TASK 2 — Daily Guardian Health Verification
**Cadence:** Daily · 03:00 AM (server local time)
**Jules UI Schedule:** Every day

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Daily guardian engine health verification.

STEPS:
1. Read ~/nina/guardian_engine.py — identify the SIGNATURES dict and all monitored files.
2. For each file listed in SIGNATURES: verify it exists on disk at its expected path.
3. Read ~/nina/docs/space/nina_error_register.md — find all rows with status OPEN.
4. Count OPEN errors. If any OPEN error is older than 72 hours, flag it.
5. Check ~/nina/juleslock.txt — verify no lock entry is older than 7 days (stale lock).
6. If everything is healthy: do NOT open a PR. Exit silently.
7. If issues found (missing files, stale OPEN errors, stale locks):
   Open PR titled "ops(guardian): daily health check flagged issues — [YYYY-MM-DD]"
   PR body: list each issue with file path and description.
8. Append entry to nina_update_log.md via Python.

DO NOT modify: guardian_engine.py, .env, any source file.
DO NOT attempt fixes — report and flag only.
```

---

### TASK 3 — Daily nina_sync Verification
**Cadence:** Daily · 04:00 AM (server local time)
**Jules UI Schedule:** Every day

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Verify nina_sync.sh output is current and complete.

STEPS:
1. Read ~/nina/nina_sync.sh — identify what files it generates and exports.
2. Check that nina_latest.md exists and its file mtime is within the last 26 hours.
3. Verify nina_latest.md contains all required sections by checking for these exact strings:
   - "## Architecture"
   - "## Open Error Register"
   - "## Roadmap"
   - "## Tool Signatures"
   - "## Session Start Checklist"
   - "## Routing Policy"
   - "## Scheduled Jobs"
4. If all checks pass: do NOT open a PR. Exit silently.
5. If any check fails (file too old, missing section):
   Open PR titled "ops(sync): nina_latest.md stale or incomplete — [YYYY-MM-DD]"
   PR body: list exactly which checks failed.
6. Append entry to nina_update_log.md via Python.

DO NOT modify nina_latest.md or nina_sync.sh directly.
DO NOT touch: .env, guardian_engine.py, tools/shell.py
```

---

## WEEKLY TASKS (fire once per week)

---

### TASK 4 — Weekly Dependency Audit
**Cadence:** Weekly · Monday · 03:00 AM
**Jules UI Schedule:** Every week on Monday

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Weekly dependency audit and update PR.

STEPS:
1. source ~/nina/venv/bin/activate
2. Run: pip list --outdated --format=json > /tmp/outdated.json
3. Read /tmp/outdated.json and requirements.txt.
4. For each outdated package that appears in requirements.txt:
   - Flag if the installed version is 2+ minor versions behind latest.
   - Flag if the package name appears in a known CVE list (check https://pypi.org/pypi/{package}/json
     and look for "vulnerabilities" key in the response).
5. If no packages qualify: do NOT open a PR. Exit silently.
6. If qualifying packages found:
   - Update requirements.txt with the safe latest version for each flagged package.
   - Run python3 -m py_compile on any file that imports the updated package to verify compatibility.
   - If py_compile fails on any file: revert that package update and note it as SKIPPED.
   - Open PR titled "chore(deps): weekly dependency audit — [YYYY-MM-DD]"
   - PR body: table of updated packages (name | old version | new version | reason).
7. Append entry to nina_update_log.md via Python.

DO NOT touch: .env, guardian_engine.py, tools/shell.py, interfaces/telegram_interface.py
DO NOT update packages that are not in requirements.txt.
DO NOT update if py_compile fails — skip and note instead.
```

---

### TASK 5 — Weekly Model String Audit
**Cadence:** Weekly · Monday · 04:00 AM
**Jules UI Schedule:** Every week on Monday

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Weekly provider model string audit — verify hardcoded model names are still valid.

STEPS:
1. Read ~/nina/core/router.py — extract every hardcoded model string (search for lines
   containing provider names like "gemini", "llama", "mistral", "deepseek", "command").
2. Read ~/nina/data/model_cache.json if it exists.
3. For each provider with a known public models endpoint, attempt a GET request
   (5 second timeout, no auth — use public/open endpoints only):
   - Groq: https://api.groq.com/openai/v1/models (skip if no GROQ_API_KEY in env)
   - Mistral: https://api.mistral.ai/v1/models (skip if no MISTRAL_API_KEY)
   - DeepSeek: https://api.deepseek.com/models (skip if no DEEPSEEK_API_KEY)
   If API keys are unavailable, compare against known deprecation patterns only.
4. Cross-reference current hardcoded strings against discovered model lists.
5. Flag any model string that:
   - No longer appears in the provider's model list, OR
   - Has a newer stable non-preview version available
6. If no issues: do NOT open PR. Exit silently.
7. If issues found:
   - Update router.py model strings to the best current stable model for each flagged provider.
   - Update data/model_cache.json accordingly.
   - Run python3 -m py_compile ~/nina/core/router.py
   - Open PR titled "chore(router): weekly model audit — update stale model strings [YYYY-MM-DD]"
8. Append entry to nina_update_log.md via Python.
9. Add core/router.py to juleslock.txt during work, remove after PR is opened.

DO NOT touch: .env, guardian_engine.py, tools/shell.py
DO NOT change routing logic — model strings only.
```

---

### TASK 6 — Weekly Dead Link Scan
**Cadence:** Weekly · Wednesday · 03:00 AM
**Jules UI Schedule:** Every week on Wednesday

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Weekly dead link scan across all documentation files.

STEPS:
1. Find all .md files under ~/nina/docs/ and ~/nina/ (root level only, not recursive for root).
2. Extract all URLs using regex: https?://[^\s\)\]"']+
3. For each unique URL found (deduplicate first):
   - Send a HEAD request with 5 second timeout.
   - If HEAD returns 405, retry with GET.
   - Record: URL, source file, line number, HTTP status code.
4. Categorise results:
   - BROKEN: status 4xx or 5xx or connection timeout
   - REDIRECT: status 3xx (note final destination)
   - OK: status 2xx
5. If zero BROKEN links: do NOT open PR. Exit silently.
6. If BROKEN links found:
   - Open PR titled "docs(links): weekly dead link report — N broken [YYYY-MM-DD]"
   - PR body: markdown table of broken links (URL | file | line | status).
   - Do NOT attempt to fix or replace URLs — report only.
7. Append entry to nina_update_log.md via Python.

DO NOT modify any source or doc files — report only.
DO NOT touch: .env, guardian_engine.py, tools/shell.py
```

---

### TASK 7 — Weekly Update Log Archive
**Cadence:** Weekly · Friday · 11:00 PM
**Jules UI Schedule:** Every week on Friday

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Weekly nina_update_log.md maintenance — archive old entries if log is too large.

STEPS:
1. Read ~/nina/nina_update_log.md.
2. Count total entries (lines starting with "E-" followed by digits).
3. If entry count is 60 or fewer: do NOT open PR. Exit silently.
4. If entry count exceeds 60:
   - Identify the oldest 20 entries (lowest E-numbers).
   - Create or append to ~/nina/exports/nina_update_log_archive.md:
     Add a section header "## Archived [YYYY-MM-DD]" then paste the 20 entries.
   - Remove those 20 entries from nina_update_log.md.
   - Verify the remaining entries in nina_update_log.md are valid (no broken formatting).
   - Open PR titled "chore(docs): archive oldest 20 log entries — log was at N entries"
5. Do NOT renumber remaining entries.
6. Append a new entry to nina_update_log.md via Python after archiving.

DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
DO NOT modify any entry content — move only.
```

---

### TASK 8 — Weekly AGENTS.md Freshness Check
**Cadence:** Weekly · Saturday · 03:00 AM
**Jules UI Schedule:** Every week on Saturday

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Weekly AGENTS.md freshness verification — ensure Jules rules match live architecture.

STEPS:
1. Read ~/nina/AGENTS.md.
2. Read ~/nina/core/router.py — extract: list of providers, high-risk files mentioned in comments,
   and any files flagged as DO NOT TOUCH.
3. Read ~/nina/docs/space/ — identify current high-risk files list.
4. Cross-check AGENTS.md against live state:
   - High-risk files list: does AGENTS.md match what's actually sensitive in the codebase?
   - Jules rules section: are the DO NOT TOUCH files still accurate?
   - agy rules section: are the sequential task rules still consistent with current architecture?
   - Provider list: does AGENTS.md mention all active providers in router.py?
5. If AGENTS.md is fully accurate: do NOT open PR. Exit silently.
6. If any section is stale:
   - Update AGENTS.md with accurate information.
   - Open PR titled "docs(agents): weekly AGENTS.md freshness update — [YYYY-MM-DD]"
   - PR body: bullet list of each change made and why.
7. Append entry to nina_update_log.md via Python.

DO NOT modify router.py, guardian_engine.py, .env, or any source file.
Only AGENTS.md may be modified by this task.
```

---

### TASK 9 — Weekly Open Error Register Review
**Cadence:** Weekly · Sunday · 03:00 AM
**Jules UI Schedule:** Every week on Sunday

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Weekly open error register sweep — flag stale unresolved errors.

STEPS:
1. Read ~/nina/docs/space/nina_error_register.md.
2. Parse all rows — find every entry with status OPEN.
3. For each OPEN entry: calculate age from the date field.
4. Categorise:
   - CRITICAL STALE: OPEN and older than 14 days
   - STALE: OPEN and older than 7 days
   - RECENT: OPEN but within 7 days
5. If zero OPEN entries exist: do NOT open PR. Exit silently.
6. If CRITICAL STALE entries exist (older than 14 days):
   - Open PR titled "ops(errors): CRITICAL — N errors open >14 days — [YYYY-MM-DD]"
   - PR body: full table of all CRITICAL STALE + STALE entries with age in days.
   - Mark PR as high priority.
7. If only STALE entries (7-14 days), no CRITICAL:
   - Open PR titled "ops(errors): N stale open errors need attention — [YYYY-MM-DD]"
8. Do NOT close or modify any error register entries — report only.
9. Append entry to nina_update_log.md via Python.

DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
DO NOT modify nina_error_register.md — report only.
```

---

### TASK 10 — Weekly juleslock.txt Cleanup
**Cadence:** Weekly · Thursday · 03:00 AM
**Jules UI Schedule:** Every week on Thursday

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Weekly juleslock.txt stale lock cleanup.

STEPS:
1. Read ~/nina/juleslock.txt.
2. For each locked file entry: check if a corresponding open PR exists in the aibony/nina
   repository by searching PR titles for the file name or associated task ID.
3. A lock is considered stale if:
   - The associated PR has been merged or closed, OR
   - No open PR references the locked file and the lock entry has no recent timestamp
4. Remove all stale lock entries from juleslock.txt.
5. If no stale locks found: do NOT open PR. Exit silently.
6. If stale locks removed:
   - Open PR titled "chore(locks): weekly juleslock cleanup — removed N stale entries"
   - PR body: list of removed entries with reason.
7. Append entry to nina_update_log.md via Python.

DO NOT remove locks for files that have ACTIVE open PRs.
DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
```

---

### TASK 15 — Weekly Circuit Breaker Stats Review
**Cadence:** Weekly · Thursday · 04:00 AM
**Jules UI Schedule:** Every week on Thursday

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Weekly circuit breaker state review across all providers.

STEPS:
1. Read ~/nina/core/router.py — identify the circuit breaker implementation,
   provider list, and any state persistence (JSON file or in-memory).
2. If circuit breaker state is persisted to disk (e.g. data/circuit_state.json):
   - Read that file.
   - Identify any provider whose circuit is OPEN (failing) or HALF-OPEN.
   - Calculate how long each has been in that state.
3. If state is in-memory only: read the code logic to understand failure thresholds
   and document the current configured thresholds.
4. Cross-reference with nina_update_log.md — search for recent entries mentioning
   provider failures or fallback events.
5. If all providers appear healthy and no persistent OPEN circuits: do NOT open PR. Exit silently.
6. If any provider has been in OPEN state for more than 48 hours OR failure threshold
   seems misconfigured:
   - Open PR titled "ops(router): circuit breaker review — provider issues flagged [YYYY-MM-DD]"
   - PR body: table of provider | circuit state | duration | recommended action.
7. Append entry to nina_update_log.md via Python.

DO NOT modify router.py or circuit breaker logic.
DO NOT touch: .env, guardian_engine.py, tools/shell.py
```

---

## MONTHLY TASKS (fire once per month)

---

### TASK 11 — Monthly Test Scaffold Generator
**Cadence:** Monthly · 1st of month · 02:00 AM
**Jules UI Schedule:** Every month on the 1st

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Monthly test scaffold — generate stub tests for any untested modules.

STEPS:
1. List all .py files under ~/nina/tools/ and ~/nina/core/ (non-recursive, direct children only).
2. List all existing test files under ~/nina/tests/.
3. For each source file (tools/*.py, core/*.py):
   - Check if a corresponding test file exists: tests/test_{filename}.py
   - A file is considered "tested" if tests/test_{filename}.py exists AND
     contains at least one function starting with "test_"
4. Collect all untested files.
5. If all files have tests: do NOT open PR. Exit silently.
6. For each untested file:
   - Read the source file to identify exported functions and classes.
   - Generate a stub test file at tests/test_{filename}.py with:
     * Standard imports (pytest, unittest.mock)
     * One stub test function per exported function/class
     * Each stub: raises NotImplementedError("TODO: implement test for {function_name}")
     * A module-level docstring: "Auto-generated test stubs — [YYYY-MM-DD]. Implement these."
   - Keep each stub file under 80 lines.
7. Run python3 -m py_compile on every generated test file.
8. Open PR titled "test(scaffold): monthly stub generation — N new test files [YYYY-MM-DD]"
   PR body: list of generated files with count of stubs per file.
9. Append entry to nina_update_log.md via Python.

DO NOT modify existing test files — only create new ones for untested modules.
DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
```

---

### TASK 12 — Monthly Security Audit (Bandit)
**Cadence:** Monthly · 1st of month · 03:00 AM
**Jules UI Schedule:** Every month on the 1st

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Monthly automated security audit using Bandit.

STEPS:
1. source ~/nina/venv/bin/activate
2. Check if bandit is installed: pip show bandit
   If not installed: pip install bandit --quiet
3. Run: bandit -r ~/nina/ --exclude ~/nina/venv,~/nina/.git,~/nina/tests \
         --severity-level medium --format json -o /tmp/bandit_report.json
4. Parse /tmp/bandit_report.json:
   - Count CRITICAL severity issues (severity: HIGH, confidence: HIGH)
   - Count HIGH severity issues
   - Count MEDIUM severity issues
5. Compare against previous report if ~/nina/data/bandit_baseline.json exists:
   - Identify NEW issues (not in baseline)
   - Identify RESOLVED issues (in baseline but not in current)
6. Save current report as ~/nina/data/bandit_baseline.json
7. If zero new CRITICAL or HIGH issues: do NOT open PR. Exit silently.
8. If new CRITICAL or HIGH issues found:
   - Open PR titled "🛡️ ops(security): monthly Bandit audit — N new HIGH/CRITICAL issues [YYYY-MM-DD]"
   - PR body: table of new issues (file | line | severity | issue type | code snippet).
   - Mark PR as high priority. Do NOT expose exploit details publicly.
   - Do NOT attempt to fix issues — report and flag only.
9. Append entry to nina_update_log.md via Python.

DO NOT touch: .env, guardian_engine.py, tools/shell.py, interfaces/telegram_interface.py
DO NOT fix security issues in this task — report only, fixes go through Sentinel review.
```

---

### TASK 13 — Monthly requirements.txt Pin Audit
**Cadence:** Monthly · 15th of month · 02:00 AM
**Jules UI Schedule:** Every month on the 15th

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Monthly requirements.txt version pin audit.

STEPS:
1. Read ~/nina/requirements.txt line by line.
2. Categorise each dependency:
   - UNPINNED: package with no version constraint (e.g. "requests")
   - LOOSE: package with >= or ~= constraint only (e.g. "requests>=2.0")
   - OVERLY_BROAD: package with wide range (e.g. "requests>=2.0,<4.0")
   - PINNED: package with exact == pin (e.g. "requests==2.31.0") — this is ideal
3. For each UNPINNED or LOOSE package:
   - Query PyPI: https://pypi.org/pypi/{package}/json
   - Get the latest stable version.
   - Propose pinning to: package==latest_stable
4. If all packages are already pinned with ==: do NOT open PR. Exit silently.
5. If unpinned/loose packages found:
   - Update requirements.txt with exact == pins for all UNPINNED and LOOSE packages.
   - Run: pip install -r requirements.txt --dry-run (if supported) to verify compatibility.
   - Run python3 -m py_compile on main.py and core/router.py to verify no import breaks.
   - Open PR titled "chore(deps): monthly pin audit — pinned N loose dependencies [YYYY-MM-DD]"
   - PR body: table of changes (package | old constraint | new pin).
6. Append entry to nina_update_log.md via Python.

DO NOT downgrade any package.
DO NOT touch: .env, guardian_engine.py, tools/shell.py, interfaces/telegram_interface.py
DO NOT change packages that are already pinned with ==.
```

---

### TASK 14 — Monthly Architecture Docs Freshness
**Cadence:** Monthly · 1st of month · 04:00 AM
**Jules UI Schedule:** Every month on the 1st

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK: Monthly architecture documentation freshness check.

STEPS:
1. Read all .md files under ~/nina/docs/space/.
2. Read ~/nina/core/router.py, ~/nina/main.py, ~/nina/crons/manager.py.
3. Cross-check documentation against live code for staleness:

   CHECK A — Provider list:
   Extract provider names from router.py RATE_LIMITS or equivalent dict.
   Verify docs/space/ mentions the same set of providers. Flag missing or extra.

   CHECK B — Scheduled jobs:
   Extract all job IDs and schedules from crons/manager.py.
   Verify docs/space/ has an accurate scheduled jobs table. Flag missing or outdated entries.

   CHECK C — High-risk files:
   Extract high-risk file list from docs/space/ and AGENTS.md.
   Verify each listed file still exists at the stated path. Flag missing files.

   CHECK D — Tool inventory:
   List all files under ~/nina/tools/.
   Verify docs/space/ architecture section mentions each tool. Flag undocumented tools.

4. If all checks pass (no stale entries): do NOT open PR. Exit silently.
5. If any check fails:
   - Update the relevant docs/space/ file(s) to match live code.
   - Open PR titled "docs(arch): monthly architecture doc sync — [YYYY-MM-DD]"
   - PR body: bullet list of each check, result (PASS/UPDATED), and changes made.
6. Append entry to nina_update_log.md via Python.

DO NOT modify any source .py files — documentation only.
DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
```

---

## BUDGET SUMMARY

| Day type | Tasks firing | Daily budget used | Remaining for interactive |
|---|---|---|---|
| Regular weekday | Tasks 1, 2, 3 | 3 / 100 | 97 |
| Monday | Tasks 1, 2, 3, 4, 5 | 5 / 100 | 95 |
| Wednesday | Tasks 1, 2, 3, 6 | 4 / 100 | 96 |
| Thursday | Tasks 1, 2, 3, 10, 15 | 5 / 100 | 95 |
| Friday | Tasks 1, 2, 3, 7 | 4 / 100 | 96 |
| Saturday | Tasks 1, 2, 3, 8 | 4 / 100 | 96 |
| Sunday | Tasks 1, 2, 3, 9 | 4 / 100 | 96 |
| 1st of month | Tasks 1, 2, 3, 4, 5, 11, 12, 14 | 8 / 100 | 92 |
| 15th of month | Tasks 1, 2, 3, 13 | 4 / 100 | 96 |

**Maximum spend on any single day: 8 tasks.** Interactive budget never drops below 92/day.

---

## HOW TO PASTE INTO JULES UI

1. Go to **jules.google.com**
2. Select repo **aibony/nina**
3. Paste the prompt block (everything inside the triple backtick block)
4. Click the **Planning** dropdown (next to the submit button)
5. Select **Scheduled Task**
6. Set the cadence shown above each task
7. Submit — Jules will confirm scheduling

> ⚠️ Each scheduled task fires against your 100/day rolling quota when it executes.
> Tasks that find nothing to do (all checks pass) still consume 1 task credit.
> Consider disabling Task 3 (nina_sync verification) if you run nina_sync.sh manually each session.



### From: nina_jules_15_daily_tasks.md
# NINA — Jules UI Scheduled Tasks (All 15 · All Daily)
> Repo: `aibony/nina` | Pro Plan: 100 tasks/day, 15 concurrent | Last updated: 2026-06-07
>
> **All 15 tasks run every day.** Daily budget cost: 15/100 tasks. Interactive budget remaining: 85/day minimum.
>
> **How to paste:** jules.google.com → select `aibony/nina` → paste prompt block → Planning dropdown → Scheduled Task → Every day → set time → Submit.
>
> **Stagger start times 10 minutes apart** (02:00, 02:10, 02:20 ... 04:20 AM) so tasks don't compete for the same files.

---

## TASK 1 — Daily Lint & Syntax Sweep
**Cadence:** Every day · 02:00 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-01
TASK: Daily automated lint and syntax sweep.

STEPS:
1. source ~/nina/venv/bin/activate
2. Run python3 -m py_compile on every .py file under ~/nina/
   (exclude: venv/, __pycache__/, .git/, tests/)
   Collect any files that fail with their error message.
3. Run pyflakes on every .py file under ~/nina/ (same exclusions).
   Collect all warnings and errors.
4. If zero issues found: do NOT open a PR. Exit silently.
5. If issues found:
   Open PR titled "fix(lint): SCHED-01 daily sweep found N issues — [YYYY-MM-DD]"
   PR body: list each file + error on its own line.
   Do NOT attempt to fix the issues — report only.
6. Append entry to nina_update_log.md via Python (not bash echo):
   Format: "E-XXX | chore(lint): SCHED-01 daily sweep [YYYY-MM-DD] — N issues found"

DO NOT touch: .env, juleslock.txt, guardian_engine.py, tools/shell.py, interfaces/telegram_interface.py
DO NOT auto-fix any errors — report only.
```

---

## TASK 2 — Daily Guardian Health Verification
**Cadence:** Every day · 02:10 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-02
TASK: Daily guardian engine health verification.

STEPS:
1. Read ~/nina/guardian_engine.py — identify the SIGNATURES dict and all monitored files.
2. For each file listed in SIGNATURES: verify it exists on disk at its expected path.
3. Read ~/nina/docs/space/nina_error_register.md — find all rows with status OPEN.
4. Count OPEN errors. If any OPEN error is older than 72 hours, flag it.
5. Check ~/nina/juleslock.txt — verify no lock entry is older than 7 days (stale lock).
6. If everything is healthy: do NOT open a PR. Exit silently.
7. If issues found (missing files, stale OPEN errors, stale locks):
   Open PR titled "ops(guardian): SCHED-02 daily health flagged issues — [YYYY-MM-DD]"
   PR body: list each issue with file path and description.
8. Append entry to nina_update_log.md via Python.

DO NOT modify: guardian_engine.py, .env, any source file.
DO NOT attempt fixes — report and flag only.
```

---

## TASK 3 — Daily nina_sync Verification
**Cadence:** Every day · 02:20 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-03
TASK: Verify nina_latest.md is current and structurally complete.

STEPS:
1. Read ~/nina/nina_sync.sh — identify what files it generates.
2. Check that nina_latest.md exists and its file mtime is within the last 26 hours.
3. Verify nina_latest.md contains all required sections by checking for these exact strings:
   - "## Architecture"
   - "## Open Error Register"
   - "## Roadmap"
   - "## Tool Signatures"
   - "## Session Start Checklist"
   - "## Routing Policy"
   - "## Scheduled Jobs"
4. If all checks pass: do NOT open a PR. Exit silently.
5. If any check fails (file too old, missing section):
   Open PR titled "ops(sync): SCHED-03 nina_latest.md stale or incomplete — [YYYY-MM-DD]"
   PR body: list exactly which checks failed.
6. Append entry to nina_update_log.md via Python.

DO NOT modify nina_latest.md or nina_sync.sh directly.
DO NOT touch: .env, guardian_engine.py, tools/shell.py
```

---

## TASK 4 — Daily Dependency Audit
**Cadence:** Every day · 02:30 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-04
TASK: Daily dependency audit — flag outdated packages in requirements.txt.

STEPS:
1. source ~/nina/venv/bin/activate
2. Run: pip list --outdated --format=json > /tmp/outdated.json
3. Read /tmp/outdated.json and ~/nina/requirements.txt.
4. For each outdated package that appears in requirements.txt:
   - Flag if the installed version is 2+ minor versions behind latest.
   - Check https://pypi.org/pypi/{package}/json for "vulnerabilities" key — flag if present.
5. If no packages qualify: do NOT open a PR. Exit silently.
6. If qualifying packages found:
   - Update requirements.txt with the safe latest version for each flagged package.
   - Run python3 -m py_compile on any file that imports the updated package.
   - If py_compile fails on any file: revert that package update and note it as SKIPPED.
   - Open PR titled "chore(deps): SCHED-04 dependency audit — [YYYY-MM-DD]"
   - PR body: table of updated packages (name | old version | new version | reason).
7. Append entry to nina_update_log.md via Python.

DO NOT touch: .env, guardian_engine.py, tools/shell.py, interfaces/telegram_interface.py
DO NOT update packages not in requirements.txt.
DO NOT update if py_compile fails — skip and note instead.
```

---

## TASK 5 — Daily Model String Audit
**Cadence:** Every day · 02:40 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-05
TASK: Daily provider model string audit — verify hardcoded model names are still valid.

STEPS:
1. Read ~/nina/core/router.py — extract every hardcoded model string.
2. Read ~/nina/data/model_cache.json if it exists.
3. For each provider that has an API key available in the environment,
   attempt a GET request (5 second timeout) to its models endpoint:
   - Groq: https://api.groq.com/openai/v1/models (Bearer GROQ_API_KEY)
   - Mistral: https://api.mistral.ai/v1/models (Bearer MISTRAL_API_KEY)
   - DeepSeek: https://api.deepseek.com/models (Bearer DEEPSEEK_API_KEY)
   - Cerebras: https://api.cerebras.ai/v1/models (Bearer CEREBRAS_API_KEY)
   If API key not in env: skip that provider silently.
4. Flag any model string that no longer appears in the provider's live model list,
   OR has a newer stable non-preview version available.
5. If no issues: do NOT open PR. Exit silently.
6. If stale model strings found:
   - Update router.py model strings to the best current stable model.
   - Update data/model_cache.json accordingly.
   - Run python3 -m py_compile ~/nina/core/router.py
   - Open PR titled "chore(router): SCHED-05 model audit — update stale strings [YYYY-MM-DD]"
7. Append entry to nina_update_log.md via Python.
8. Add core/router.py to juleslock.txt during work, remove after PR is opened.

DO NOT touch: .env, guardian_engine.py, tools/shell.py
DO NOT change routing logic — model strings only.
```

---

## TASK 6 — Daily Dead Link Scan
**Cadence:** Every day · 02:50 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-06
TASK: Daily dead link scan across all documentation files.

STEPS:
1. Find all .md files under ~/nina/docs/ and ~/nina/ root level.
2. Extract all URLs using regex: https?://[^\s\)\]"']+
3. For each unique URL (deduplicated):
   - Send HEAD request, 5 second timeout.
   - If HEAD returns 405: retry with GET.
   - Record: URL, source file, line number, HTTP status.
4. Categorise:
   - BROKEN: 4xx, 5xx, or timeout
   - REDIRECT: 3xx
   - OK: 2xx
5. If zero BROKEN links: do NOT open PR. Exit silently.
6. If BROKEN links found:
   Open PR titled "docs(links): SCHED-06 dead link report — N broken [YYYY-MM-DD]"
   PR body: markdown table (URL | file | line | status).
   Do NOT attempt to fix or replace URLs — report only.
7. Append entry to nina_update_log.md via Python.

DO NOT modify any source or doc files — report only.
DO NOT touch: .env, guardian_engine.py, tools/shell.py
```

---

## TASK 7 — Daily Update Log Maintenance
**Cadence:** Every day · 03:00 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-07
TASK: Daily nina_update_log.md maintenance — archive old entries if log exceeds threshold.

STEPS:
1. Read ~/nina/nina_update_log.md.
2. Count total entries (lines starting with "E-" followed by digits).
3. If entry count is 60 or fewer: do NOT open PR. Exit silently.
4. If entry count exceeds 60:
   - Identify the oldest 20 entries (lowest E-numbers).
   - Create or append to ~/nina/exports/nina_update_log_archive.md:
     Add section header "## Archived [YYYY-MM-DD]" then paste the 20 entries.
   - Remove those 20 entries from nina_update_log.md.
   - Verify remaining entries have no broken formatting.
   - Open PR titled "chore(docs): SCHED-07 archive oldest 20 log entries — was N entries"
5. Do NOT renumber remaining entries.
6. Append new entry to nina_update_log.md via Python after archiving.

DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
DO NOT modify any entry content — move only.
```

---

## TASK 8 — Daily AGENTS.md Freshness Check
**Cadence:** Every day · 03:10 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-08
TASK: Daily AGENTS.md freshness — verify Jules rules match live architecture.

STEPS:
1. Read ~/nina/AGENTS.md.
2. Read ~/nina/core/router.py — extract: provider list, high-risk files in comments,
   DO NOT TOUCH file references.
3. Read ~/nina/docs/space/ — identify current high-risk files list.
4. Cross-check AGENTS.md:
   - High-risk files list matches what's actually sensitive in the codebase.
   - DO NOT TOUCH files in Jules rules are still accurate.
   - agy rules are consistent with current architecture.
   - Provider list matches all active providers in router.py.
5. If AGENTS.md is fully accurate: do NOT open PR. Exit silently.
6. If any section is stale:
   - Update AGENTS.md with accurate information.
   - Open PR titled "docs(agents): SCHED-08 daily AGENTS.md sync — [YYYY-MM-DD]"
   - PR body: bullet list of each change made and why.
7. Append entry to nina_update_log.md via Python.

DO NOT modify router.py, guardian_engine.py, .env, or any source file.
Only AGENTS.md may be modified by this task.
```

---

## TASK 9 — Daily Open Error Register Review
**Cadence:** Every day · 03:20 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-09
TASK: Daily open error register sweep — flag stale unresolved errors.

STEPS:
1. Read ~/nina/docs/space/nina_error_register.md.
2. Parse all rows — find every entry with status OPEN.
3. For each OPEN entry: calculate age from the date field.
4. Categorise:
   - CRITICAL STALE: OPEN and older than 14 days
   - STALE: OPEN and older than 7 days
   - RECENT: OPEN but within 7 days
5. If zero OPEN entries: do NOT open PR. Exit silently.
6. If CRITICAL STALE entries exist (>14 days):
   Open PR titled "ops(errors): SCHED-09 CRITICAL — N errors open >14 days — [YYYY-MM-DD]"
   PR body: full table of CRITICAL STALE + STALE entries with age in days.
   Mark PR as high priority.
7. If only STALE entries (7-14 days, no CRITICAL):
   Open PR titled "ops(errors): SCHED-09 N stale open errors — [YYYY-MM-DD]"
8. If only RECENT entries: do NOT open PR. Exit silently.
9. Append entry to nina_update_log.md via Python.

DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
DO NOT modify nina_error_register.md — report only.
```

---

## TASK 10 — Daily juleslock.txt Cleanup
**Cadence:** Every day · 03:30 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-10
TASK: Daily juleslock.txt stale lock cleanup.

STEPS:
1. Read ~/nina/juleslock.txt.
2. For each locked file entry: check if a corresponding open PR exists in aibony/nina
   by searching PR titles for the file name or associated task ID.
3. A lock is stale if:
   - The associated PR has been merged or closed, OR
   - No open PR references the locked file and the lock has no recent timestamp.
4. Remove all stale lock entries from juleslock.txt.
5. If no stale locks found: do NOT open PR. Exit silently.
6. If stale locks removed:
   Open PR titled "chore(locks): SCHED-10 daily lock cleanup — removed N stale entries"
   PR body: list of removed entries with reason.
7. Append entry to nina_update_log.md via Python.

DO NOT remove locks for files with ACTIVE open PRs.
DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
```

---

## TASK 11 — Daily Test Scaffold Generator
**Cadence:** Every day · 03:40 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-11
TASK: Daily test scaffold — generate stub tests for any newly untested modules.

STEPS:
1. List all .py files under ~/nina/tools/ and ~/nina/core/ (direct children only).
2. List all existing test files under ~/nina/tests/.
3. For each source file: check if tests/test_{filename}.py exists AND contains
   at least one function starting with "test_".
4. Collect all untested files.
5. If all files have tests: do NOT open PR. Exit silently.
6. For each untested file:
   - Read the source file to identify exported functions and classes.
   - Generate stub test file at tests/test_{filename}.py with:
     * Standard imports (pytest, unittest.mock)
     * One stub test function per exported function/class
     * Each stub raises NotImplementedError("TODO: implement test for {function_name}")
     * Module docstring: "Auto-generated test stubs — [YYYY-MM-DD]. Implement these."
   - Keep each stub file under 80 lines.
7. Run python3 -m py_compile on every generated test file.
8. Open PR titled "test(scaffold): SCHED-11 daily stub generation — N new test files [YYYY-MM-DD]"
   PR body: list of generated files with stub count per file.
9. Append entry to nina_update_log.md via Python.

DO NOT modify existing test files — only create new ones for untested modules.
DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
```

---

## TASK 12 — Daily Security Audit (Bandit)
**Cadence:** Every day · 03:50 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-12
TASK: Daily Bandit security audit — flag new HIGH or CRITICAL issues only.

STEPS:
1. source ~/nina/venv/bin/activate
2. Check if bandit is installed: pip show bandit
   If not installed: pip install bandit --quiet
3. Run: bandit -r ~/nina/ \
         --exclude ~/nina/venv,~/nina/.git,~/nina/tests \
         --severity-level medium --format json -o /tmp/bandit_report.json
4. Parse /tmp/bandit_report.json — collect all CRITICAL (HIGH severity + HIGH confidence)
   and HIGH severity issues.
5. Load baseline from ~/nina/data/bandit_baseline.json if it exists.
   Identify NEW issues not present in baseline (match by file + line + issue_text).
6. Save current report as ~/nina/data/bandit_baseline.json (overwrite).
7. If zero NEW CRITICAL or HIGH issues: do NOT open PR. Exit silently.
8. If new issues found:
   Open PR titled "🛡️ ops(security): SCHED-12 Bandit — N new HIGH/CRITICAL [YYYY-MM-DD]"
   PR body: table (file | line | severity | issue type).
   Mark PR as high priority.
   Do NOT expose detailed exploit information.
   Do NOT attempt to fix issues — report only.
9. Append entry to nina_update_log.md via Python.

DO NOT touch: .env, guardian_engine.py, tools/shell.py, interfaces/telegram_interface.py
DO NOT fix security issues in this task — Sentinel handles fixes.
```

---

## TASK 13 — Daily requirements.txt Pin Audit
**Cadence:** Every day · 04:00 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-13
TASK: Daily requirements.txt version pin audit — enforce exact == pins.

STEPS:
1. Read ~/nina/requirements.txt line by line.
2. Categorise each dependency:
   - UNPINNED: no version constraint (e.g. "requests")
   - LOOSE: >= or ~= only (e.g. "requests>=2.0")
   - PINNED: exact == pin (e.g. "requests==2.31.0") — ideal, skip these
3. For each UNPINNED or LOOSE package:
   - Query https://pypi.org/pypi/{package}/json → get latest stable version.
   - Propose: package==latest_stable
4. If all packages already pinned with ==: do NOT open PR. Exit silently.
5. If unpinned/loose found:
   - Update requirements.txt with exact == pins for UNPINNED and LOOSE packages.
   - Run python3 -m py_compile on main.py and core/router.py to verify no import breaks.
   - If py_compile fails: revert that package change, note as SKIPPED.
   - Open PR titled "chore(deps): SCHED-13 pin audit — pinned N loose dependencies [YYYY-MM-DD]"
   - PR body: table (package | old constraint | new pin).
6. Append entry to nina_update_log.md via Python.

DO NOT downgrade any package.
DO NOT touch: .env, guardian_engine.py, tools/shell.py, interfaces/telegram_interface.py
DO NOT change packages already pinned with ==.
```

---

## TASK 14 — Daily Architecture Docs Freshness
**Cadence:** Every day · 04:10 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-14
TASK: Daily architecture documentation freshness check.

STEPS:
1. Read all .md files under ~/nina/docs/space/.
2. Read ~/nina/core/router.py, ~/nina/main.py, ~/nina/crons/manager.py.
3. Run four checks:

   CHECK A — Provider list:
   Extract provider names from router.py RATE_LIMITS or equivalent.
   Verify docs/space/ mentions the same provider set. Flag missing or extra.

   CHECK B — Scheduled jobs:
   Extract all job IDs and schedules from crons/manager.py.
   Verify docs/space/ has an accurate scheduled jobs table. Flag missing/outdated.

   CHECK C — High-risk files:
   Extract high-risk file list from docs/space/ and AGENTS.md.
   Verify each listed file exists at the stated path. Flag missing files.

   CHECK D — Tool inventory:
   List all files under ~/nina/tools/.
   Verify docs/space/ mentions each tool. Flag undocumented tools.

4. If all four checks pass: do NOT open PR. Exit silently.
5. If any check fails:
   - Update the relevant docs/space/ file(s) to match live code.
   - Open PR titled "docs(arch): SCHED-14 daily arch doc sync — [YYYY-MM-DD]"
   - PR body: bullet list of each check with result (PASS/UPDATED) and changes made.
6. Append entry to nina_update_log.md via Python.

DO NOT modify any .py source files — documentation only.
DO NOT touch: .env, guardian_engine.py, tools/shell.py, core/router.py
```

---

## TASK 15 — Daily Circuit Breaker Stats Review
**Cadence:** Every day · 04:20 AM

```
Do NOT pause for confirmation at any point. Complete all steps sequentially and open a PR when done.

REPO: aibony/nina
TASK ID: SCHED-15
TASK: Daily circuit breaker state review across all providers.

STEPS:
1. Read ~/nina/core/router.py — identify circuit breaker implementation and provider list.
2. If circuit breaker state is persisted (e.g. data/circuit_state.json): read that file.
   Identify any provider whose circuit is OPEN or HALF-OPEN and how long it has been so.
3. If state is in-memory only: read the failure threshold configuration from the code
   and document current thresholds in the PR body.
4. Cross-reference nina_update_log.md for recent entries mentioning provider failures
   or fallback events in the last 24 hours.
5. If all providers healthy and no OPEN circuits: do NOT open PR. Exit silently.
6. If any provider has been OPEN for more than 24 hours OR failure threshold
   seems misconfigured relative to provider uptime:
   Open PR titled "ops(router): SCHED-15 circuit breaker — provider issue flagged [YYYY-MM-DD]"
   PR body: table (provider | circuit state | duration | recommended action).
7. Append entry to nina_update_log.md via Python.

DO NOT modify router.py or circuit breaker logic.
DO NOT touch: .env, guardian_engine.py, tools/shell.py
```

---

## BUDGET SUMMARY — ALL 15 DAILY

| Metric | Value |
|---|---|
| Tasks firing per day | 15 |
| Daily budget used | 15 / 100 |
| Interactive tasks remaining | **85 / day minimum** |
| Concurrent slots used (all staggered) | 1 at a time (10 min gaps) |
| Tasks that open PRs when healthy | 0 (all have silent exit) |
| Max PRs in one day (everything broken) | 15 |

## STAGGER SCHEDULE

| Time | Task |
|---|---|
| 02:00 | SCHED-01 Lint sweep |
| 02:10 | SCHED-02 Guardian health |
| 02:20 | SCHED-03 Sync verification |
| 02:30 | SCHED-04 Dependency audit |
| 02:40 | SCHED-05 Model string audit |
| 02:50 | SCHED-06 Dead link scan |
| 03:00 | SCHED-07 Update log archive |
| 03:10 | SCHED-08 AGENTS.md freshness |
| 03:20 | SCHED-09 Error register sweep |
| 03:30 | SCHED-10 Lock cleanup |
| 03:40 | SCHED-11 Test scaffold |
| 03:50 | SCHED-12 Bandit security |
| 04:00 | SCHED-13 Pin audit |
| 04:10 | SCHED-14 Arch docs freshness |
| 04:20 | SCHED-15 Circuit breaker stats |

> All tasks run between 02:00–04:30 AM local time while NINA is in low-traffic overnight window.
> Every task has a silent exit condition — if nothing is wrong, no PR is opened and no noise is generated.
> The only output you see is PRs that actually need attention.


