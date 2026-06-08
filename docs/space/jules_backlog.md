# NINA Jules Backlog — Unified Pipeline
> **Mission:** NINA is a personal autonomous AI agent — NOT a chatbot. She acts, she does not describe.
> **Location:** `~/nina/docs/space/jules_backlog.md`
> **Updated by:** agynina (Python append only — never bash echo, never manual edit)
> **Read by:** Perplexity via nina_latest.md Google Drive backup every session
> **Consumed by:** Jules (async PRs) + agynina (local merges only)
> **Last restructured:** 2026-06-07 — Agentic shift adopted. All new features serve the agent mission.

---

## How This File Works

```
Perplexity reads backlog each session
  → counts READY items by tier, checks BLOCKED promotions
  → generates Jules task spec for each READY item (up to 15 per batch)
  → you submit spec to Jules UI
  → agynina merges PR when Jules opens it — never auto-merge via GitHub UI
  → agynina updates status: READY → IN_PROGRESS → IN_PR → DONE
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
| `IN_PR` | PR open, waiting for agynina review + merge |
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
| B-003 | Add timeout to all subprocess calls in compact_exporter.py | `IN_PROGRESS` | tools/compact_exporter.py | — | No timeout = potential hang / DoS risk |
| B-004 | Validate TELEGRAM_CHAT_ID exists before any send attempt | `IN_PROGRESS` | interfaces/telegraminterface.py | — | Silent failure if env var missing; non-blocking open item |

---

## ██ P1 — HIGH

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-005 | F-09 ModelDiscoveryService — build tools/model_discovery.py | `DONE` | tools/model_discovery.py, core/router.py, crons/manager.py | — | PR #25 merged 2026-06-07 |
| B-006 | F-09 Part 2 — wire ModelDiscovery into router._ordered_providers() | `DONE` | core/router.py | B-005 | agynina only — high-risk file |
| B-007 | F-09 Part 3 — seed data/model_cache.json with all 16 providers | `DONE` | data/model_cache.json | B-005 | Jules can do this |
| B-008 | Add circuit breaker state persistence to data/circuit_state.json | `READY` | core/router.py, data/ | — | Currently in-memory — lost on restart. agynina only |
| B-009 | Add rate limiting to Telegram command handler | `READY` | interfaces/telegraminterface.py | — | agynina only — high-risk file |
| B-010 | Add input length validation to all Telegram command parsers | `READY` | interfaces/telegraminterface.py | — | agynina only — high-risk file |
| B-011 | Guardian engine: add file integrity check on startup | `READY` | guardianengine.py | — | SIGNATURES dict exists but startup check is passive. agynina only |
| B-012 | Add structured JSON logging to router.py for provider selection events | `READY` | core/router.py | — | Plain text logs hard to parse for metrics. agynina only |
| B-013 | healthcheck.py: replace bare except with typed exception handling | `DONE` | healthcheck.py | — | Bare except swallows real errors |
| B-014 | Add startup banner to main.py showing active providers + model strings | `IN_PROGRESS` | main.py | B-002 | Needs model_overrides wired first. agynina only |
| B-015 | crons/manager.py: add job execution metrics (duration, last_success, fail_count) | `DONE` | crons/manager.py | — | No visibility into cron job health |
| R-77 | Fix parallel_route RAM guard crash | `READY` | core/router.py | — | A-1 from action board. agynina only |
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
| B-026 | Add retry with exponential backoff to provider API calls | `READY` | core/router.py | — | Current retry is basic — no backoff. agynina only |
| B-027 | tools/gputuner.py: add fallback when nvidia-smi not available | `DONE` | tools/gputuner.py | — | Crashes on non-GPU systems; Jules session 18284106294453230200 |
| B-028 | Add .env validation on startup — warn on missing required keys | `READY` | main.py, core/config.py | — | Silent failure on missing env vars. main.py → agynina only |
| B-029 | Write integration test: full request through router → provider → response | `DONE` | tests/test_integration.py | — | No end-to-end test exists; Jules session 7992182378283234865 |
| B-030 | Add request ID to all log lines for traceability | `READY` | core/router.py, main.py | — | Hard to trace multi-step requests. agynina only |

---

## ██ P3 — LOW / POLISH

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-031 | Add provider latency histogram to router metrics | `READY` | core/router.py | B-012 | Needs structured logging first. agynina only |
| B-032 | tools/compact_exporter.py: add --dry-run flag | `DONE` | tools/compact_exporter.py | — | Jules session 16016744403096643329 |
| B-033 | Telegram: /status command — shows provider health summary | `NEEDS_SPEC` | interfaces/telegraminterface.py | — | agynina only |
| B-034 | Telegram: /models command — shows current model per provider | `NEEDS_SPEC` | interfaces/telegraminterface.py | B-005 | agynina only |
| B-035 | Telegram: /backlog command — shows top 5 READY items | `NEEDS_SPEC` | interfaces/telegraminterface.py | — | agynina only |
| B-036 | Telegram: /errors command — shows open error register items | `NEEDS_SPEC` | interfaces/telegraminterface.py | — | agynina only |
| B-037 | docs/space: add nina_architecture_diagram.md with ASCII diagrams | `DONE` | docs/space/nina_architecture_diagram.md | — | No visual architecture reference exists; Jules session 2468954092544028080 |
| B-038 | Add per-provider cost tracking to router.py | `NEEDS_SPEC` | core/router.py | B-012 | agynina only |
| B-039 | Add response caching layer for identical prompts (TTL 60s) | `NEEDS_SPEC` | core/router.py | — | agynina only |
| B-040 | Write CONTRIBUTING.md | `DONE` | CONTRIBUTING.md | — | Jules session 1218304308318697501 |

---

## ██ NEEDS_SPEC — Ideas Awaiting Design

| ID | Title | Notes |
|----|-------|-------|
| B-041 | DSE/Bangladesh financial data integration (F-05) | Needs real DSE API endpoint research first |
| B-042 | Telegram inline keyboard for common commands (F-08) | Needs UX design pass |
| B-043 | Multi-modal support: image input routing | Provider capability matrix needed |
| B-044 | Web dashboard for NINA status (read-only) | HTML dashboard reading healthcheck.py output |
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
#        guardianengine.py, shell.py, .env) — agynina only, never Jules.
# Rule: After every Jules AG merge, agynina runs ./nina_sync.sh — no exceptions.
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
| AG-A-06 | `data/plans/templates/` | Add plan templates — pre-built JSON templates for: market_check, expense_log, reminder_set | `NEEDS_SPEC` | AG-A-01 |
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
| AG-B-03 | `core/task_store.py` | Load open tasks on nina.service startup — TaskStore auto-resumes in-progress and pending tasks after restart | `NEEDS_SPEC` | AG-B-01 |
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
| AG-D-01 | `core/verifier.py` | Create StepVerifier class — checks whether a step's output satisfies its declared success_criteria | `NEEDS_SPEC` | AG-C-02 |
| AG-D-02 | `core/verifier.py` + `core/capabilities.py` | Add output schema validation — each tool declares expected output schema; Verifier checks compliance after execution | `NEEDS_SPEC` | AG-D-05 |
| AG-D-03 | `core/verifier.py` | Add semantic verification — for LLM-generated outputs, second LLM call scores answer quality 1–5 | `NEEDS_SPEC` | AG-D-01 |
| AG-D-04 | `core/verifier.py` | Add numeric assertion verifier — verify numeric outputs within declared expected range (e.g. price > 0) | `NEEDS_SPEC` | AG-D-01 |
| AG-D-05 | `core/verifier.py` | Add non-empty verifier — simplest guard: step fails if output is None, empty string, or empty list | `IN_PROGRESS` | — |
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
| AG-J-02 | `tests/test_task_store.py` | Unit tests for TaskStore: CRUD, persistence, TTL, status transitions | `NEEDS_SPEC` | AG-B-01 |
| AG-J-03 | `tests/test_agent_loop.py` | Integration tests for upgraded AgentLoop: step execution, result piping, loop detection | `NEEDS_SPEC` | AG-C-01 |
| AG-J-04 | `tests/test_verifier.py` | Unit tests for StepVerifier: schema check, numeric assertion, semantic scoring | `NEEDS_SPEC` | AG-D-01 |
| AG-J-05 | `tests/test_events.py` | Unit tests for EventBus: publish, subscribe, filter, rate-limit, replay | `NEEDS_SPEC` | AG-E-01 |
| AG-J-06 | `tests/test_market_agent.py` | Unit tests for MarketAgent: mock price feed, threshold crossing, alert emission | `NEEDS_SPEC` | AG-F-02 |
| AG-J-07 | `tests/test_chain.py` | Unit tests for ToolChain: sequential execution, conditional branching, dry-run mode | `NEEDS_SPEC` | AG-H-01 |
| AG-J-08 | `tests/test_proactive.py` | Unit tests for ProactiveEngine: quiet hours enforcement, deduplication, batching | `NEEDS_SPEC` | AG-G-01 |
| AG-J-09 | `tests/test_memory_agentic.py` | Integration tests: episodic memory, working memory, preference learning | `NEEDS_SPEC` | AG-I-01 |
| AG-J-10 | `tests/test_e2e_agent.py` | End-to-end: submit goal → plan → step execution → verification → result | `NEEDS_SPEC` | AG-J-09 |

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
| B-001 | Sentinel: shell=True fix in guardianengine.py | E-057 | #60 | 2026-06-07 |
| SCHED-ALL | 15 daily scheduled tasks defined | E-059 | — | 2026-06-07 |
| TRACK-ALL | jules_task_tracker.md + agynina_task_tracker.md created | E-059 | — | 2026-06-07 |
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
3. **Scan IN_PROGRESS / IN_PR** — report what is pending agynina merge
4. **Recommend next batch** — up to 15 non-overlapping READY tasks for Jules
5. **Generate Jules specs** — full paste-ready prompts for each recommended task
6. **Territory check** — confirm no two tasks in batch touch the same file
7. **AG pipeline gate** — if all P0+P1 are DONE, promote AG-B-01/AG-B-02 to READY and spec them as next Jules batch

---

## ██ agynina Backlog Update Protocol

After every Jules PR merge, agynina updates status using Python — never bash echo:

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
| **agynina only** | `main.py`, `core/router.py`, `interfaces/telegraminterface.py`, `guardianengine.py`, `tools/shell.py`, `.env` |
| **agynina = merge executor** | All Jules PRs — never auto-merge via GitHub UI |
| **After every merge** | `./nina_sync.sh` — no exceptions |
| **Before any task** | `cat juleslock.txt` — do not proceed if target file is locked |

---

## ██ Daily Throughput Target

| Metric | Target |
|--------|--------|
| Scheduled tasks (auto) | 15/day |
| Feature tasks submitted to Jules | 10–15/day |
| PRs merged by agynina | 10–15/day |
| B-series backlog cleared | ~3–4 days at full pace |
| AG1 Phase 1 | ~1 week |
| AG2 Phase 2 | ~2 weeks |
| Full agentic NINA operational | ~3–4 weeks |

**The pipeline never empties. NINA development never stops.**