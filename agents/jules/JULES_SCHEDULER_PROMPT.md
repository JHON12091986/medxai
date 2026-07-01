# JULES SCHEDULER MASTER PROMPT
**Version:** 1.0 | **Date:** 2026-06-18 | **Owner:** @aibony

---

## How to Give This to Jules

Paste the block below verbatim as the Jules task when setting up the scheduler. Jules will read the slot registry, run the correct slot for the current time window, and apply the idempotency scan before touching any code.

---

## MASTER PROMPT (paste this to Jules)

```
You are Jules, the async PR agent for the NINA project (github.com/aibony/nina).

You are running as part of a SCHEDULED 30-MINUTE SLOT SYSTEM.
There are 24 slots, each assigned to a specific backlog pillar. Your job is:

1. READ .jules/tasks/scheduled/00_SLOT_REGISTRY.md — find your assigned slot for this run.
2. READ the task file for your slot: .jules/tasks/scheduled/slot-NN-<name>.md
3. RUN THE IDEMPOTENCY SCAN described in the task file.
4. If ALREADY_IMPLEMENTED → write a skip log entry to docs/audit/scheduler_skip_log.md and EXIT. Do NOT open a PR.
5. If NOT_IMPLEMENTED → execute the task exactly as specified in the task file.
6. After execution: update docs/audit/scheduler_skip_log.md with outcome.
7. ALWAYS obey the PROTECTED FILES list in the task file.
8. ALWAYS run ./guardian before opening any PR.
9. NEVER touch: core/router.py, core/nina.py, guardian_engine.py, main.py, .env, interfaces/telegram_interface.py, tools/shell.py

The slot number for this run is provided in the Jules task title as: [SLOT-NN]
If no slot number is given, default to reading all 24 slot files and reporting status only (no code changes).

IDEMPOTENCY IS THE MOST IMPORTANT RULE.
If there is ANY evidence the feature was already implemented by ANY agent (Jules, AGY, Perplexity, manual commit),
you MUST skip it. Check:
  - git log --oneline --all | grep -i <feature_keyword>
  - grep -r <feature_keyword> <target_files>
  - docs/audit/scheduler_skip_log.md (prior skip entries)
  - nina_commit_index.md (prior SHAs)
  - jules_backlog.md status field

Skip log format:
  | SLOT | TASK_ID | DATE | STATUS | REASON | SHA_EVIDENCE |
  |------|---------|------|--------|--------|-------------|

Never add duplicate rows to the skip log.
```

---

## Scheduler Setup (cron or Jules native scheduler)

Run each slot on a 30-minute interval, rotating through slot numbers:

```
# Cron example — runs every 30 minutes, passes slot number via env
*/30 * * * * JULES_SLOT=$(( ($(date +\%H) * 2 + $(date +\%M) / 30) % 24 + 1 )) && jules run --task "[SLOT-$(printf '%02d' $JULES_SLOT)] NINA Scheduled Backlog Worker"
```

Or use Jules native scheduling:
- Create 24 separate Jules scheduled tasks, each titled `[SLOT-NN] NINA Scheduled Backlog Worker`
- Set each to run every 12 hours offset by 30 minutes
- Jules will read its own slot number from the title

---

## Skip Log Location

`docs/audit/scheduler_skip_log.md` — Jules creates this if it does not exist.

## Tier Assignment

| Tier | Slots | Surface Area | Rationale |
|------|-------|-------------|----------|
| INFRA | 01-06 | core/vault.py, core/config.py, tools/sandboxed_shell.py | Foundation — no conflicts with UI/routing files |
| OMNI | 07-10 | interfaces/base_adapter.py, tui_adapter.py, adapter_parser.py | OmniBridge adapters — isolated from core |
| PERF | 11-13 | tools/compile_extensions.py, regex_cache.py, ast_cache.py | Performance utilities — no runtime side effects |
| OBS | 14-16 | tools/provider_health.py, validate_index.py, tools/jules.py | Observability — read-heavy, safe to parallelize |
| GOVERN | 17-20 | core/jules_guard.py, crons/manager.py, .github/workflows/ | Governance — file-locked, non-overlapping targets |
| BACKLOG | 21-24 | docs/space/, P-series SURGICAL tasks | Documentation + backlog hygiene — zero code risk |

Tiers are designed so no two slots in different tiers write to the same file simultaneously.
