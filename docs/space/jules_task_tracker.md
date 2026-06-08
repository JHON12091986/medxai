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
| ASYNC-02 | F-09 ModelDiscoveryService | ✅ MERGED | 2026-06-07 | PR #25 | E-061 | Spec ready, submitted and merged |

| ASYNC-03 | B-002: Wire model_overrides dict to .env hot-reload in router.py | ⏳ QUEUED | 2026-06-07 | — | — | Session: [13876164946786086522](https://jules.google.com/session/13876164946786086522) |
| ASYNC-04 | B-003: Add timeout to all subprocess calls in compact_exporter.py | ⏳ QUEUED | 2026-06-07 | — | — | Session: [890874151317558069](https://jules.google.com/session/890874151317558069) |
| ASYNC-05 | B-004: Validate TELEGRAM_CHAT_ID exists before any send attempt | ⏳ QUEUED | 2026-06-07 | — | — | Session: [3544127208157451730](https://jules.google.com/session/3544127208157451730) |
| ASYNC-06 | B-007: F-09 Part 3 — seed data/model_cache.json with all 16 providers | ✅ MERGED | 2026-06-07 | PR #42 | 2026-06-08 | Session: [4718778617163535359](https://jules.google.com/session/4718778617163535359) |
| ASYNC-07 | B-013: healthcheck.py: replace bare except with typed exception handling | ✅ MERGED | 2026-06-07 | PR #46 | 2026-06-08 | Session: [10635814989193465007](https://jules.google.com/session/10635814989193465007) |
| ASYNC-08 | B-014: Add startup banner to main.py showing active providers + model strings | ⏳ QUEUED | 2026-06-07 | — | — | Session: [16604506654173776295](https://jules.google.com/session/16604506654173776295) |
| ASYNC-09 | B-015: crons/manager.py: add job execution metrics (duration, last_success, fail_count) | ✅ MERGED | 2026-06-07 | PR #45 | 2026-06-08 | Session: [6671558330966465193](https://jules.google.com/session/6671558330966465193) |
| ASYNC-10 | AG-B-01: Create TaskStore with full CRUD and JSON persistence | ⏳ IN_PROGRESS | 2026-06-08 | — | — | Submitted via agynina |
| ASYNC-11 | AG-D-05: Create StepVerifier with non-empty output check | ⏳ IN_PROGRESS | 2026-06-08 | — | — | Submitted via agynina |
