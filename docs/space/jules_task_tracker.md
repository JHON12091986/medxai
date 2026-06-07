# Jules Task Tracker
> Auto-updated by Jules after every task. Read by Perplexity via nina_latest.md backup.
> Format: append new rows via Python — never bash echo. Never delete rows — use status updates only.

## Status Legend
| Symbol | Meaning |
|--------|---------|
| ✅ ACTIVE | Scheduled task is live and healthy |
| ✅ DONE | One-off task completed successfully |
| ✅ MERGED | PR merged and deployed |
| 🔄 IN PR | PR open, awaiting merge |
| 🔄 PENDING | Task defined, not yet submitted |
| ⏳ QUEUED | Submitted to Jules, not yet started |
| ❌ FAILED | Last run errored — needs attention |
| ⏸️ PAUSED | Temporarily disabled |
| 🔒 LOCKED | juleslock.txt active for this task |

## Scheduled Tasks (SCHED-*)
| ID | Title | Status | Cadence | Last Run | Last PR | Notes |
|----|-------|--------|---------|----------|---------|-------|
| SCHED-01 | Daily lint sweep | 🔄 PENDING | Daily 02:00 | — | — | Not yet activated in Jules UI |
| SCHED-02 | Daily guardian health | 🔄 PENDING | Daily 02:10 | — | — | Not yet activated in Jules UI |
| SCHED-03 | Daily sync verification | 🔄 PENDING | Daily 02:20 | — | — | Not yet activated in Jules UI |
| SCHED-04 | Daily dependency audit | 🔄 PENDING | Daily 02:30 | — | — | Not yet activated in Jules UI |
| SCHED-05 | Daily model string audit | 🔄 PENDING | Daily 02:40 | — | — | Not yet activated in Jules UI |
| SCHED-06 | Daily dead link scan | 🔄 PENDING | Daily 02:50 | — | — | Not yet activated in Jules UI |
| SCHED-07 | Daily update log archive | 🔄 PENDING | Daily 03:00 | — | — | Not yet activated in Jules UI |
| SCHED-08 | Daily AGENTS.md freshness | 🔄 PENDING | Daily 03:10 | — | — | Not yet activated in Jules UI |
| SCHED-09 | Daily error register sweep | 🔄 PENDING | Daily 03:20 | — | — | Not yet activated in Jules UI |
| SCHED-10 | Daily lock cleanup | 🔄 PENDING | Daily 03:30 | — | — | Not yet activated in Jules UI |
| SCHED-11 | Daily test scaffold | 🔄 PENDING | Daily 03:40 | — | — | Not yet activated in Jules UI |
| SCHED-12 | Daily Bandit security | 🔄 PENDING | Daily 03:50 | — | — | Not yet activated in Jules UI |
| SCHED-13 | Daily pin audit | 🔄 PENDING | Daily 04:00 | — | — | Not yet activated in Jules UI |
| SCHED-14 | Daily arch docs freshness | 🔄 PENDING | Daily 04:10 | — | — | Not yet activated in Jules UI |
| SCHED-15 | Daily circuit breaker stats | 🔄 PENDING | Daily 04:20 | — | — | Not yet activated in Jules UI |

## Async Tasks (ASYNC-*)
| ID | Title | Status | Submitted | PR | Entry | Notes |
|----|-------|--------|-----------|-----|-------|-------|
| ASYNC-01 | Sentinel shell=True fix | ✅ MERGED | 2026-06-07 | PR #60 | E-057 | guardian_engine.py |
| ASYNC-02 | F-09 ModelDiscoveryService | 🔄 PENDING | — | — | — | Spec ready, not submitted |
