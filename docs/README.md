# NINA Docs Index

> **Canonical navigation index for all NINA documentation.**
> Source of truth for file locations: [`config/file_registry.yaml`](../config/file_registry.yaml)
> Last updated: 2026-06-19

---

## 📁 Full Directory Map

```
docs/
├── README.md                              ← YOU ARE HERE
│
├── context/                               ← Agent-loaded context (boot & runtime)
│   ├── NINA_AGENT_PRIMER.md               ← Full agent boot context (62KB)
│   ├── AGY_PROMPTS.md                     ← AGY-specific prompt library
│   ├── NINA_RULES.md                      ← Core behaviour rules
│   ├── NINA_OPS.md                        ← Operational instructions
│   ├── NINA_WORKFLOW.md                   ← Workflow definitions
│   ├── task_routing_policy.md             ← Task → agent routing policy
│   ├── nina_v15_perplexity_prompt.md      ← Perplexity master prompt (v15)
│   ├── PERPLEXITY_OVERWATCH.md            ← Perplexity overwatch rules
│   ├── PERPLEXITY_SPACE_INSTRUCTIONS.md   ← Space-level instructions
│   └── nina_session_log.md                ← Rolling session log
│
├── agyspec/                               ← AGY agent task specs & batches
│   ├── README.md                          ← AGY spec overview
│   ├── agy_batch_01.md                    ← Batch 01 task specs
│   ├── agy_batch_02.md                    ← Batch 02 task specs
│   ├── agy_batch_03.md                    ← Batch 03 task specs
│   ├── agy_batch_04.md                    ← Batch 04 task specs
│   ├── queue.md                           ← AGY task queue
│   ├── spec_log.md                        ← Spec execution log
│   └── run_batch.sh                       ← Batch runner script
│
├── roadmap/                               ← Release planning & milestones
│
├── space/                                 ← Space/environment configs
│
├── audit/                                 ← Audit snapshots & error ledger
│   ├── nina_error_register.md             ← COMMITTED — permanent error ledger
│   └── violations.md                      ← Registry violation log (auto-written)
│
├── generated/                             ← AUTO-GENERATED — gitignored, local only
│   ├── .gitignore                         ← Ignores all *.md/*.json inside
│   ├── NDEV_*.md                          ← Jules task report outputs
│   ├── nina_md_audit.md                   ← MD audit output
│   ├── nina_sh_py_audit.md                ← Script audit output
│   ├── bench_report.md                    ← Benchmark reports
│   ├── nina_commit_index.md               ← Commit index snapshots
│   └── efficiency_report.json             ← Performance snapshots
│
│   ── [PLANNED — not yet migrated] ──────────────────────────
├── architecture/                          ← System design & internals
│   ├── overview.md                        ← (← ARCHITECTURE.md at root)
│   ├── router.md                          ← (← docs/router.md)
│   ├── ninaflash.md                       ← (← docs/ninaflash.md)
│   └── guardian.md                        ← (← docs/guardian.md)
│
├── agents/                                ← Per-agent documentation
│   ├── jules_pipeline.md                  ← (← docs/jules_pipeline.md)
│   ├── jules_agent_memory.md              ← (← docs/jules_agent_memory.md)
│   └── gemini_perf.md                     ← (← docs/gemini_perf.md)
│
├── memory/                                ← Memory & session system
│   ├── memory.md                          ← (← docs/memory.md)
│   └── session_ledger.md                  ← (← docs/session_ledger.md)
│
├── observability/                         ← Monitoring & proxy
│   ├── observability.md                   ← (← docs/observability.md)
│   └── nina_proxy_usage.md                ← (← docs/nina_proxy_usage.md)
│
└── dev/                                   ← Developer workflow docs
    ├── WORKFLOW.md                        ← (← root/WORKFLOW.md)
    ├── CONTRIBUTING.md                    ← (← root/CONTRIBUTING.md)
    ├── SECURITY.md                        ← (← root/SECURITY.md)
    └── EVOLVE_PROPOSAL.md                 ← (← root/EVOLVE_PROPOSAL.md)
```

> Files marked `(← source)` are **planned migrations** — they still live at their
> original path. Do not move them until generator scripts are updated to use new paths.

---

## 🗂️ Agent Workspaces (outside docs/)

```
.jules/                                    ← Jules agent workspace
├── JULES_SCHEDULER_PROMPT.md              ← Jules scheduler instructions
├── bolt.md                                ← Jules bolt task spec
├── sentinel.md                            ← Jules sentinel rules
└── tasks/                                 ← Jules task queue directory

.agy/                                      ← AGY agent workspace
.gemini/                                   ← Gemini agent workspace
.cursor/                                   ← Cursor IDE rules
```

---

## 📄 File Type Permissions

| Type | Committed | Written By | Lives In | Rotation |
|------|-----------|------------|----------|----------|
| `*.md` permanent doc | ✅ yes | human, perplexity | `docs/*/` | none |
| `*.md` agent report | ❌ no | jules, agy, gemini | `docs/generated/` | keep last 5 |
| `*.md` audit snapshot | ❌ no | guardian, agy | `docs/audit/` | keep last 3 |
| `*.md` update_log | ❌ no | nina, agy | `data/logs/` | tail 500 lines |
| `*.md` error_register | ✅ yes | nina, guardian, human | `docs/audit/` | none |
| `*.json` config | ✅ yes | nina, agy | `config/` | none |
| `*.json` call_graph | ❌ no | agy | `data/graphs/` | keep last 2 |
| `*.json` report | ❌ no | guardian | `data/reports/` | keep last 5 |
| `*.txt` lockfile | ✅ yes | jules, agy, nina | `./` root only | none |
| `*.txt` log | ❌ no | any | `data/logs/` | tail 1000 lines |
| `*.yaml` registry | ✅ yes | human, perplexity | `config/` | none |
| `*.py` core | ✅ yes | human, jules, agy | `core/`, `agent/` | none |
| `*.sh` scripts | ✅ yes | human, jules, agy | `./`, `bin/` | none |
| `.env` live | ❌ no | human | `./` | gitignored |

Full rules → [`config/file_registry.yaml`](../config/file_registry.yaml)

---

## 🚫 Root Forbidden Patterns

These are **blocked at pre-commit** and must never appear at repo root:

```
NDEV*.md              → docs/generated/
*_audit.md            → docs/audit/
*_report.md           → docs/generated/
*_report.json         → data/reports/
bench_*.md            → docs/generated/
call_graph_*.json     → data/graphs/
efficiency_*.json     → data/reports/
nina_update_log.md    → data/logs/
nina_commit_index.md  → docs/generated/
agy_session.md        → docs/generated/
```

---

## 🔒 Enforcement Chain

| Layer | File | Trigger | Action |
|-------|------|---------|--------|
| Pre-commit hook | `git-hooks/pre-commit` | Every `git commit` | Block + log violation |
| Runtime guardian | `guardian_engine.py` | Agent file writes | Log to `docs/audit/violations.md` |
| Emergency bypass | `git commit --no-verify` | Human only | Bypasses hook, not guardian |

---

## 📌 Permanent Root Files

These 6 files are the **only MDs/key files** that live at root permanently:

| File | Purpose |
|------|---------|
| `README.md` | Project overview for GitHub |
| `CHANGELOG.md` | Version history |
| `Makefile` | Build & task commands |
| `guardian_engine.py` | Runtime file + behaviour guardian |
| `idleloop.py` | Main NINA event loop |
| `juleslock.txt` | Jules agent lock signal |

---

> **Rule:** Every file needs a registered type in [`config/file_registry.yaml`](../config/file_registry.yaml).
> Unregistered files are blocked. To add a new type: edit the registry → update this index.
