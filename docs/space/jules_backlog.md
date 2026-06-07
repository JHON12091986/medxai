# NINA Jules Backlog
> **The perpetual pipeline.** Perplexity reads this file at session start and converts READY items into Jules task specs on demand.
> **Location:** `~/nina/docs/space/jules_backlog.md`
> **Updated by:** agy (Python append only — never bash echo, never manual edit)
> **Read by:** Perplexity via nina_latest.md Google Drive backup every session
> **Consumed by:** Jules (async PRs) + agy (local merges)

---

## How This File Works

```
Perplexity reads backlog each session
  → identifies READY items by priority tier
  → generates Jules task spec for each
  → you submit to Jules UI or jules remote new
  → agy merges PR when done
  → agy updates status: READY → IN_PROGRESS → DONE
  → next session: Perplexity picks next READY batch
```

**Territory rule:** Perplexity will never spec two concurrent tasks that touch the same file.
**Batch size:** Perplexity specs up to 15 tasks per batch (= Jules concurrent limit).
**Daily budget:** 15 SCHED tasks + up to 75 backlog tasks = 90/100 daily limit. 10 reserved for emergencies.

---

## Status Definitions

| Status | Meaning |
|--------|---------|
| `READY` | Fully specced, no blockers — pick up immediately |
| `IN_PROGRESS` | Jules task submitted, PR not yet open |
| `IN_PR` | PR open, waiting for agy merge |
| `BLOCKED` | Has unresolved dependency — do not pick up |
| `DONE` | Merged, deployed, verified |
| `DEFERRED` | Valid but deprioritised — revisit later |
| `NEEDS_SPEC` | Idea captured, Perplexity needs to write full spec |

---

## Priority Tiers

- **P0 — CRITICAL:** Security, data loss, service down. Fix before anything else.
- **P1 — HIGH:** Core functionality gaps, reliability, routing quality.
- **P2 — MEDIUM:** Developer experience, observability, performance.
- **P3 — LOW:** Nice-to-have, polish, future-proofing.

---

## ██ P0 — CRITICAL

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-001 | Sentinel: remove shell=True from run_cmd in guardian_engine.py | `DONE` | guardian_engine.py | — | E-057, PR #60 merged |
| B-002 | Wire model_overrides dict to .env hot-reload in router.py | `IN_PROGRESS` | core/router.py, core/config.py | — | model_overrides exists in NinaConfig but not wired |
| B-003 | Add timeout to all subprocess calls in compact_exporter.py | `IN_PROGRESS` | tools/compact_exporter.py | — | No timeout = potential hang, DoS risk |
| B-004 | Validate TELEGRAM_CHAT_ID exists before any send attempt | `IN_PROGRESS` | interfaces/telegram_interface.py | — | Silent failure if env var missing |

---

## ██ P1 — HIGH

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-005 | F-09 ModelDiscoveryService — build tools/model_discovery.py | `DONE` | tools/model_discovery.py, core/router.py, crons/manager.py | B-002 | Full spec written by Perplexity — see session 2026-06-07 |
| B-006 | F-09 Part 2 — wire ModelDiscovery into router._ordered_providers() | `READY` | core/router.py | B-005 | Cannot start until B-005 PR merged |
| B-007 | F-09 Part 3 — seed data/model_cache.json with all 16 providers | `IN_PROGRESS` | data/model_cache.json | B-005 | |
| B-008 | Add circuit breaker state persistence to data/circuit_state.json | `READY` | core/router.py, data/ | — | Currently in-memory only — lost on restart |
| B-009 | Add rate limiting to Telegram command handler | `READY` | interfaces/telegram_interface.py | — | No rate limit = potential spam/DoS from authorized user fat-finger |
| B-010 | Add input length validation to all Telegram command parsers | `READY` | interfaces/telegram_interface.py | — | Commands with no length limit are DoS risk |
| B-011 | Guardian engine: add file integrity check on startup | `READY` | guardian_engine.py | — | SIGNATURES dict exists but startup check is passive |
| B-012 | Add structured JSON logging to router.py for provider selection events | `READY` | core/router.py | — | Currently plain text — hard to parse for metrics |
| B-013 | healthcheck.py: replace bare except with typed exception handling | `IN_PROGRESS` | healthcheck.py | — | Bare except swallows real errors |
| B-014 | Add startup banner to main.py showing active providers + model strings | `IN_PROGRESS` | main.py | B-002 | Needs model_overrides wired first for accurate display |
| B-015 | crons/manager.py: add job execution metrics (duration, last_success, fail_count) | `IN_PROGRESS` | crons/manager.py | — | No visibility into cron job health |

---

## ██ P2 — MEDIUM

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-016 | Write tests for tools/shell.py — full coverage of blocklist and allowlist | `READY` | tests/test_shell.py | — | Most critical security tool has no tests |
| B-017 | Write tests for core/router.py — provider ordering, circuit breaker, fallback | `READY` | tests/test_router.py | — | |
| B-018 | Write tests for tools/browser.py — SSRF guard, URL validation | `READY` | tests/test_browser.py | — | |
| B-019 | Write tests for guardian_engine.py — SIGNATURES check, run_cmd | `READY` | tests/test_guardian.py | — | High-risk file needs test coverage |
| B-020 | Write tests for tools/model_discovery.py | `BLOCKED` | tests/test_model_discovery.py | B-005 | Cannot write until module exists |
| B-021 | Add prometheus-style metrics endpoint to healthcheck.py | `READY` | healthcheck.py | — | Enables external monitoring |
| B-022 | tools/compact_exporter.py: add progress logging for long exports | `READY` | tools/compact_exporter.py | — | Silent during long runs |
| B-023 | Add AGENTS.md section: tracker update protocol for Jules tasks | `READY` | AGENTS.md | — | Jules needs instructions to update jules_task_tracker.md after each run |
| B-024 | Add AGENTS.md section: backlog update protocol | `DONE` | AGENTS.md | — | Jules needs to mark B-IDs as DONE after successful PR merge |
| B-025 | crons/manager.py: add graceful shutdown handler (SIGTERM) | `READY` | crons/manager.py | — | Currently no clean shutdown on systemd stop |
| B-026 | Add retry logic to provider API calls with exponential backoff | `READY` | core/router.py | — | Current retry is basic — no backoff |
| B-027 | tools/gputuner.py: add fallback when nvidia-smi not available | `READY` | tools/gputuner.py | — | Crashes on non-GPU systems |
| B-028 | Add .env validation on startup — warn if required keys missing | `READY` | main.py, core/config.py | — | Silent failure on missing env vars |
| B-029 | Write integration test: full request through router → provider → response | `READY` | tests/test_integration.py | — | No end-to-end test exists |
| B-030 | Add request ID to all log lines for traceability | `READY` | core/router.py, main.py | — | Hard to trace multi-step requests in logs |

---

## ██ P3 — LOW / POLISH

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-031 | Add provider latency histogram to router metrics | `READY` | core/router.py | B-012 | Needs structured logging first |
| B-032 | tools/compact_exporter.py: add --dry-run flag | `READY` | tools/compact_exporter.py | — | Useful for testing without writing output |
| B-033 | Add Telegram command: /status — shows provider health summary | `NEEDS_SPEC` | interfaces/telegram_interface.py | — | Useful operational command |
| B-034 | Add Telegram command: /models — shows current model per provider | `NEEDS_SPEC` | interfaces/telegram_interface.py | B-005 | Needs ModelDiscovery first |
| B-035 | Add Telegram command: /backlog — shows top 5 READY items | `NEEDS_SPEC` | interfaces/telegram_interface.py | — | Operational visibility from phone |
| B-036 | Add Telegram command: /errors — shows open error register items | `NEEDS_SPEC` | interfaces/telegram_interface.py | — | |
| B-037 | docs/space: add nina_architecture_diagram.md with ASCII diagrams | `READY` | docs/space/nina_architecture_diagram.md | — | No visual architecture reference exists |
| B-038 | Add per-provider cost tracking to router.py | `NEEDS_SPEC` | core/router.py | B-012 | Track estimated token cost per provider call |
| B-039 | Add response caching layer for identical prompts (TTL 60s) | `NEEDS_SPEC` | core/router.py | — | Prevent duplicate API calls on retry |
| B-040 | Write contributing guide: CONTRIBUTING.md | `READY` | CONTRIBUTING.md | — | No guide for future contributors |

---

## ██ NEEDS_SPEC — Ideas Not Yet Specced

| ID | Title | Notes |
|----|-------|-------|
| B-041 | F-05: DSE/Bangladesh financial data integration | Needs real DSE API endpoint research first |
| B-042 | F-08: Telegram inline keyboard for common commands | Needs UX design pass |
| B-043 | Multi-modal support: image input routing | Provider capability matrix needed |
| B-044 | Web dashboard for NINA status (read-only) | HTML dashboard reading healthcheck.py output |
| B-045 | Conversation memory persistence across sessions | Storage design needed |

---

## ██ DONE — Completed Items

| ID | Title | Entry | PR | Date |
|----|-------|-------|----|------|
| B-001 | Sentinel: shell=True fix in guardian_engine.py | E-057 | #60 | 2026-06-07 |
| SCHED-ALL | 15 daily scheduled tasks defined | E-059 | — | 2026-06-07 |
| TRACK-ALL | jules_task_tracker.md + agy_task_tracker.md created | E-059 | — | 2026-06-07 |
| B-024 | Add AGENTS.md section: backlog update protocol | E-060 | — | 2026-06-07 |
| B-005 | F-09 ModelDiscoveryService — build tools/model_discovery.py | E-061 | #25 | 2026-06-07 |

---

## ██ Perplexity Session Briefing Protocol

At the start of every session where this file is attached, Perplexity will:

1. **Count READY items by tier** — report as: "P0: N ready, P1: N ready, P2: N ready"
2. **Check BLOCKED items** — if their dependency is now DONE, promote to READY
3. **Check IN_PROGRESS / IN_PR** — report what's pending agy merge
4. **Recommend next batch** — up to 15 non-overlapping READY tasks for Jules
5. **Generate Jules specs** — full paste-ready prompts for each recommended task
6. **Territory check** — confirm no two tasks in the batch touch the same file

---

## ██ agy Backlog Update Protocol

After every Jules PR merge, agy must:

```python
# Update backlog status — run via Python, never bash echo
import re
from pathlib import Path
from datetime import date

backlog_path = Path("/home/aibony/nina/docs/space/jules_backlog.md")
content = backlog_path.read_text()

# Replace status for completed item
content = content.replace(
    "| B-XXX | Title | `READY`",
    f"| B-XXX | Title | `DONE`"
)
# Move to DONE table with entry and PR info
backlog_path.write_text(content)
```

---

## ██ Daily Throughput Target

| Metric | Target |
|--------|--------|
| Scheduled tasks (auto) | 15/day |
| Feature tasks submitted | 10–15/day |
| PRs merged via agy | 10–15/day |
| Backlog items cleared | 10–15/day |
| **At this rate, full backlog cleared in** | **~3–4 days** |

After the current backlog is cleared, Perplexity generates new tasks from:
- Phase B roadmap features
- New NEEDS_SPEC items promoted to READY
- Sentinel daily security findings
- Community/operational requests via Telegram

**The pipeline never empties. NINA development never stops.**

