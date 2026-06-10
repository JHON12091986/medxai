| B-001 | Sentinel: remove shell=True from run_cmd in guardianengine.py | `DONE` | guardianengine.py | — | PR #60 merged 2026-06-07 |
| B-003 | Add timeout to all subprocess calls in compact_exporter.py | `DONE` | tools/compact_exporter.py | — | No timeout = potential hang / DoS risk |
| B-005 | F-09 ModelDiscoveryService — build tools/model_discovery.py | `DONE` | tools/model_discovery.py, core/router.py, crons/manager.py | — | PR #25 merged 2026-06-07 |
| B-006 | F-09 Part 2 — wire ModelDiscovery into router._ordered_providers() | `DONE` | core/router.py | B-005 | ninaflash only — high-risk file |
| B-007 | F-09 Part 3 — seed data/model_cache.json with all 16 providers | `DONE` | data/model_cache.json | B-005 | Jules can do this |
| B-008 | Add circuit breaker state persistence to data/circuit_state.json | `DONE` | core/router.py, data/ | — | Currently in-memory — lost on restart. ninaflash only |
| B-013 | healthcheck.py: replace bare except with typed exception handling | `DONE` | healthcheck.py | — | Bare except swallows real errors |
| B-015 | crons/manager.py: add job execution metrics (duration, last_success, fail_count) | `DONE` | crons/manager.py | — | No visibility into cron job health |
| R-78 | Fix tool grammar fragility — minimum viable guard | `DONE` | core/agent.py | — | A-3 from action board; Jules session 230224707076942630 |
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
| B-027 | tools/gputuner.py: add fallback when nvidia-smi not available | `DONE` | tools/gputuner.py | — | Crashes on non-GPU systems; Jules session 18284106294453230200 |
| B-029 | Write integration test: full request through router → provider → response | `DONE` | tests/test_integration.py | — | No end-to-end test exists; Jules session 7992182378283234865 |
| B-032 | tools/compact_exporter.py: add --dry-run flag | `DONE` | tools/compact_exporter.py | — | Jules session 16016744403096643329 |
| B-037 | docs/space: add nina_architecture_diagram.md with ASCII diagrams | `DONE` | docs/space/nina_architecture_diagram.md | — | No visual architecture reference exists; Jules session 2468954092544028080 |
| B-039 | Add response caching layer for identical prompts (TTL 60s) | `DONE` | core/router.py | — | Persistent cache implemented by Gemini CLI 2026-06-11 |
| B-040 | Write CONTRIBUTING.md | `DONE` | CONTRIBUTING.md | — | Jules session 1218304308318697501 |
| B-044 | Web dashboard for NINA status (read-only) | `DONE` |
| AG-A-06 | `data/plans/templates/` | Add plan templates — pre-built JSON templates for: market_check, expense_log, reminder_set | `DONE` | AG-A-01 |
| AG-B-01 | `core/task_store.py` | Create TaskStore class — full CRUD for Task objects persisted to data/tasks.json | `DONE` | — |
| AG-B-03 | `core/task_store.py` | Load open tasks on nina.service startup — TaskStore auto-resumes in-progress and pending tasks after restart | `DONE` | AG-B-01 |
| AG-D-01 | `core/verifier.py` | Create StepVerifier class — checks whether a step's output satisfies its declared success_criteria | `DONE` | AG-C-02 |
| AG-D-03 | `core/verifier.py` | Add semantic verification — for LLM-generated outputs, second LLM call scores answer quality 1–5 | `DONE` | AG-D-01 |
| AG-D-04 | `core/verifier.py` | Add numeric assertion verifier — verify numeric outputs within declared expected range (e.g. price > 0) | `DONE` | AG-D-01 |
| AG-D-05 | `core/verifier.py` | Add non-empty verifier — simplest guard: step fails if output is None, empty string, or empty list | `DONE` | — |
| AG-J-02 | `tests/test_task_store.py` | Unit tests for TaskStore: CRUD, persistence, TTL, status transitions | `DONE` | AG-B-01 |
| AG-J-04 | `tests/test_verifier.py` | Unit tests for StepVerifier: schema check, numeric assertion, semantic scoring | `DONE` | 2026-06-09 |
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
