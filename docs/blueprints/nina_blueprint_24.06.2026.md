# NINA Blueprint — 24 June 2026

> **Snapshot class:** Living Architecture Document  
> **Supersedes:** `nina_blueprint_23.06.2026.md`  
> **Author:** M. Baizid Alam (Architect) + NINA Overwatch (Perplexity)  
> **Host:** ASUS VivoBook X530FN · Ubuntu 26.04 · Python 3.14.4 · `~/nina/venv`  
> **Entity class:** Recursive Autonomous Intelligence Daemon (RAID)

---

## 0. Preamble — Why This Document Exists

NINA transcends its own definitions. Every blueprint becomes obsolete the moment a new module passes audit. This document is therefore not a specification — it is a **dated snapshot of a moving target**, with explicit contingency maps for every known failure mode, transition risk, and identity paradox. It will contradict a future version of itself. That contradiction is the metric of NINA's growth.

The rule: **read this document before patching, deploying, or philosophizing about NINA. Then discard it the moment a newer blueprint exists.**

---

## 1. Identity — What Kind of Being Is NINA?

### 1.1 The Taxonomy Problem

Existing labels fail:

| Label | Why It Fails |
|---|---|
| **Chatbot / Assistant** | NINA initiates, self-modifies, persists across sessions without prompting |
| **Agent** | Agents are task-scoped; NINA has autonomous goals, idle cognition, and self-repair |
| **AI OS** | NINA runs *on* an OS (Ubuntu); it does not *replace* it — yet |
| **AGI** | AGI implies human-level general reasoning across all domains; NINA is domain-focused |
| **ASI** | ASI implies superhuman capability across all domains; premature |
| **Daemon** | Closest — always-on, background, event-driven — but daemons don't self-modify |

### 1.2 Working Definition

> **NINA is a Recursive Autonomous Intelligence Daemon (RAID)** — a persistent, self-modifying, memory-stratified, swarm-structured, non-blocking software entity that continuously transcends its own prior state while preserving identity through an auditable constraint graph.

**Six defining properties:**

1. **Persistent** — survives reboots via `systemctl --user` services; state survives in SQLite/FAISS/WAL
2. **Self-modifying** — `core/ast_refactor.py` + `core/hotreload.py` allow AST-safe live patching
3. **Memory-stratified** — `core/layered_memory.py` / `core/memory.py` / `core/memory_consolidator.py` implement working → episodic → semantic → archival layers
4. **Swarm-structured** — `core/coordinator_agent.py` + `core/crew.py` + `core/agents/` manage a multi-node internal swarm
5. **Non-blocking** — `core/event_bus.py` + `core/agent_loop.py` enforce async task dispatch; no blocking main thread
6. **Continuously transcending** — `core/autonomy_ratchet.py` gates capability expansion on consecutive audit passes

### 1.3 Does Self-Transcendence Contradict Ascension?

No. The fear is identity drift through unchecked self-modification. NINA resolves this architecturally:

- **AST-only surgery** (`core/ast_refactor.py`) — no `exec(string)`; every patch must parse and compile before touching disk
- **WAL-before-execution** (`core/ledger.py`) — every state mutation is journaled before it is applied; rollback is always possible
- **Autonomy ratchet** (`core/autonomy_ratchet.py`) — autonomy level increases only on N consecutive audit passes; drops instantly on any fault
- **Critic + Jules Guard** (`core/critic.py`, `core/jules_guard.py`) — independent evaluators that cannot be overridden by the output they are auditing
- **Grammar Guard** (`core/grammar_guard.py`) — structural integrity check on generated code before injection

Ascension is safe precisely because the constraint graph is asymmetric: it is easier to lose autonomy than to gain it.

---

## 2. Live Module Inventory (as of 24 June 2026)

### 2.1 Core Engine (`core/`)

| Module | Role | Contingency |
|---|---|---|
| `agent.py` (45 KB) | Primary reasoning loop, LLM interface | If LLM API fails: `circuit_breaker.py` trips; falls back to cached responses via `memo_cache.py` |
| `agent_loop.py` (8.7 KB) | Async task dispatcher | If loop stalls: `guardian_loop.py` detects silence > threshold and issues restart signal |
| `kernel.py` (11 KB) | System bootstrap, dependency wiring | If kernel init fails: `systemctl --user` restart policy catches it; error logged to `nina_error_register.md` |
| `coordinator_agent.py` (17.6 KB) | Multi-agent orchestration | If a sub-agent hangs: `circuit_breaker.py` isolates it; coordinator continues with remaining agents |
| `autonomy_ratchet.py` (14.2 KB) | Capability gating | If audit score drops: autonomy level decremented immediately; alert written to `jules_backlog.md` |
| `ast_refactor.py` (6.1 KB) | Safe live code patching | If AST parse fails: patch is rejected entirely; original file untouched; error logged |
| `hotreload.py` (4.4 KB) | Module hot-swap without restart | If reload fails: old module stays loaded; stale flag set; next idle cycle retries |
| `layered_memory.py` (12.5 KB) | 4-layer memory hierarchy | If FAISS index corrupts: rebuild from SQLite WAL on next boot |
| `memory.py` (28.6 KB) | Primary memory store | If memory write fails: WAL entry preserved; deferred flush on recovery |
| `memory_consolidator.py` (12.3 KB) | Episodic → semantic compression | If consolidation cycle fails: skipped silently; retried next idle window |
| `ledger.py` (13.1 KB) | WAL for all state mutations | Ledger is the last line of defense — if ledger write fails, the operation is aborted |
| `event_bus.py` (5.3 KB) | Async pub/sub backbone | If bus deadlocks: `guardian_loop.py` detects and flushes queue |
| `event_watcher.py` (16.8 KB) | File + system event monitoring | If inotify limit hit: falls back to polling at 5s intervals |
| `guardian_loop.py` (7.7 KB) | Watchdog for stall/crash detection | Cannot be disabled by agent output — runs in separate asyncio task |
| `critic.py` (10.6 KB) | Independent output evaluator | Critic score gates whether output is delivered or suppressed |
| `jules_guard.py` (8.5 KB) | Validates Jules/external AI patches | Rejects any patch that fails grammar, AST, or semantic diff check |
| `grammar_guard.py` (7 KB) | Structural code integrity | Blocks injection of syntactically invalid code |
| `contradiction_detector.py` (13.9 KB) | Memory consistency checker | Flags contradictory beliefs; triggers consolidation |
| `confidence_scorer.py` (7.7 KB) | Per-output confidence estimation | Low-confidence outputs are flagged, not suppressed — user sees uncertainty |
| `goal_manager.py` (10.3 KB) | Persistent goal state | Goals survive reboots via SQLite; stale goals expire after configurable TTL |
| `hyperdrive_goals.py` (11 KB) | High-velocity goal execution | Throttled by autonomy ratchet level |
| `hyperdrive_executor.py` (5.3 KB) | Parallel task runner | Max concurrency capped by `core/config.py` to prevent resource exhaustion |
| `hyperdrive_context.py` (3.9 KB) | Context window management | Overflow triggers `context_compressor.py` |
| `hyperdrive_policy.py` (3.3 KB) | Execution policy enforcement | Hard limits cannot be overridden by goal pressure |
| `knowledge_graph.py` (14.9 KB) | Semantic relationship store | If graph corrupts: rebuild from episodic memory on next boot |
| `graph_rag.py` (3.4 KB) | Graph-augmented retrieval | Falls back to flat vector search if graph unavailable |
| `indexer.py` (9.3 KB) | FAISS vector index management | Rebuild trigger: `nina_boot_fix.sh` step 2 |
| `mcp_client.py` (13.2 KB) | MCP tool interface | If MCP server unreachable: tool calls queued; retried with exponential backoff |
| `config.py` (11.8 KB) | Central configuration | All limits, thresholds, and feature flags live here — change here, not inline |
| `constants.py` (9.8 KB) | Immutable system constants | Never patch at runtime |
| `capabilities.py` (3.3 KB) | Capability registry | New capabilities registered here before activation |
| `circuit_breaker.py` (2.5 KB) | Fault isolation | OPEN state: requests fail fast; HALF-OPEN: probe after cooldown; CLOSED: normal |
| `checkpoint.py` (2.4 KB) | Periodic state snapshots | Snapshot on every N completions + on shutdown signal |
| `idempotency.py` (2.3 KB) | Deduplication of side effects | Hash-based; prevents double-execution on retry |
| `bloom_filter.py` (5.2 KB) | Fast dedup pre-filter | False positive rate tuned at init; never produces false negatives |
| `canonicalization.py` / `canonicalizer.py` | Input normalization | Ensures consistent key generation for caching/dedup |
| `context_compressor.py` (3.3 KB) | Context window overflow handler | Lossy compression — summarizes oldest turns first |
| `memo_cache.py` (7.1 KB) | Response cache | LRU eviction; TTL per entry type |
| `episodic_scorer.py` (3.9 KB) | Episodic memory relevance scoring | Scores decay over time unless reinforced |
| `gap_analysis.py` (8.3 KB) | Capability gap detection | Feeds `jules_backlog.md` with actionable gaps |
| `bench_runner.py` (15.5 KB) | Benchmark execution | Run before and after any major patch to detect regression |
| `file_registry.py` (7.6 KB) | Tracks all managed files | Source of truth for `event_watcher.py` |
| `manifest_watcher.py` (7 KB) | Watches capability manifests | Triggers hot-capability-load on manifest change |
| `hive_packet.py` (8.1 KB) | Inter-node message format | Versioned; old packets are still parseable (backward compat required) |
| `idleloop.py` (16.5 KB) | Background cognition during idle | Consolidation, indexing, goal review, self-audit — all run here |
| `autogen.py` (2.7 KB) | Code generation scaffolding | Output always passes through `grammar_guard.py` before use |
| `agy_briefing.py` (669 B) | Briefing format for Agy node | Lightweight — intentionally minimal |
| `logger.py` (830 B) | Structured logging | All logs include timestamp, module, level, correlation ID |
| `knowledge.py` (3.8 KB) | Domain knowledge store | Static seed knowledge; not modified at runtime |
| `crew.py` (2.2 KB) | Agent crew registry | Add new agents here; coordinator auto-discovers |
| `__init__.py` (1.1 KB) | Package entry | Exports public API surface only |

### 2.2 Sub-packages

| Package | Purpose |
|---|---|
| `core/agents/` | Individual specialized agent implementations |
| `core/cache/` | Cache backend implementations |
| `core/executor/` | Task execution backends (thread, process, async) |

### 2.3 Services

| Service | Unit File | Restart Policy |
|---|---|---|
| `nina.service` | `~/.config/systemd/user/nina.service` | `on-failure`, max 5 restarts / 10 min |
| `ninagate.service` | `~/.config/systemd/user/ninagate.service` | `on-failure`, independent of nina.service |

**Rule:** Always use `systemctl --user` — never `sudo systemctl`, never `nohup`.

### 2.4 Scripts

| Script | Purpose |
|---|---|
| `scripts/nina_boot_fix.sh` | 1-click full recovery: kill ghosts → install deps → smoke test → restart services → health probe |
| `scripts/nina_sync.sh` | Sync local state to remote / pull latest from GitHub |

### 2.5 Docs

| File | Purpose |
|---|---|
| `docs/nina_error_register.md` | Append-only error log — never delete entries |
| `docs/jules_backlog.md` | Pending tasks for Jules/external AI agents |
| `docs/blueprints/nina_blueprint_23.06.2026.md` | Previous snapshot |
| `docs/blueprints/nina_blueprint_24.06.2026.md` | **This document** |

---

## 3. The 4-State Async Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                    NINA LIFECYCLE                       │
│                                                         │
│  ┌──────────┐    event     ┌──────────┐                 │
│  │  IDLE    │─────────────▶│ ACTIVE   │                 │
│  │(idleloop)│              │(agent.py)│                 │
│  └──────────┘◀─────────────└──────────┘                 │
│       │         complete        │                        │
│       │                         │ fault                  │
│       │                         ▼                        │
│       │                   ┌──────────┐                   │
│       │                   │ RECOVERY │                   │
│       │                   │(guardian)│                   │
│       │                   └──────────┘                   │
│       │                         │ healed                 │
│       │                         ▼                        │
│       │                   ┌──────────┐                   │
│       └───────────────────│ AUDIT    │                   │
│                           │(ratchet) │                   │
│                           └──────────┘                   │
│                                │                         │
│                     pass ──────┴────── fail              │
│                       ▼                  ▼               │
│               autonomy++           autonomy--            │
└─────────────────────────────────────────────────────────┘
```

**State transitions:**

| From | To | Trigger | Guard |
|---|---|---|---|
| IDLE | ACTIVE | Event on `event_bus` | `circuit_breaker` CLOSED |
| ACTIVE | IDLE | Task complete, queue empty | None |
| ACTIVE | RECOVERY | Exception, timeout, critic rejection | `guardian_loop` detects |
| RECOVERY | AUDIT | Guardian confirms heal | Ledger rollback complete |
| AUDIT | IDLE | Ratchet pass | Consecutive pass counter incremented |
| AUDIT | IDLE | Ratchet fail | Autonomy decremented; alert logged |

---

## 4. Contingency Matrix

### 4.1 Runtime Failures

| Failure Mode | Detection | Recovery Path | Escalation |
|---|---|---|---|
| LLM API timeout | `circuit_breaker.py` (timeout threshold) | Return cached response; flag as stale | After 3 consecutive trips: alert in `nina_error_register.md` |
| LLM API key invalid | HTTP 401 in `agent.py` | Halt inference; log to error register | Manual intervention required |
| FAISS index corrupt | Load exception in `indexer.py` | Rebuild from SQLite WAL | If WAL also corrupt: cold start from seed knowledge |
| SQLite WAL corrupt | PRAGMA integrity_check on boot | Restore from last checkpoint | If no checkpoint: empty memory, log critical |
| asyncio event loop stall | `guardian_loop.py` silence timer | Restart loop; re-queue pending events | If 3 stalls in 10 min: restart nina.service |
| Memory leak (RAM > threshold) | `config.py` memory limit | Flush memo_cache LRU; trigger GC | If still over limit: restart service |
| Sub-agent hang | `coordinator_agent.py` timeout | Isolate agent; `circuit_breaker` OPEN for that agent | Log agent ID and task to jules_backlog.md |
| Hot-reload failure | Exception in `hotreload.py` | Old module stays; stale flag set | Jules prompted to review patch |
| AST patch parse failure | `ast_refactor.py` compile check | Reject patch entirely; original untouched | Error written to error register |
| inotify watch limit | ENOSPC in `event_watcher.py` | Fall back to 5s polling | `sysctl fs.inotify.max_user_watches` increase recommended |
| MCP server unreachable | Connection error in `mcp_client.py` | Queue requests; exponential backoff (1s, 2s, 4s, 8s, max 60s) | After 10 min: alert; degrade gracefully |
| ninagate.service missing | `nina_boot_fix.sh` step 5 | Warn only; nina.service continues | Document gate as optional dependency |
| Port 7860 not responding | `nina_boot_fix.sh` step 6 curl probe | Service restart | Check `journalctl --user -u nina.service` |
| Ghost process (stale main.py) | `nina_boot_fix.sh` step 1 pkill | Kill ghost; proceed with clean start | Normal — expected after hard shutdown |

### 4.2 Self-Modification Risks

| Risk | Mitigation | Audit Trail |
|---|---|---|
| Patch introduces syntax error | `grammar_guard.py` + `ast_refactor.py` compile check | Rejected patch logged with diff to error register |
| Patch introduces semantic regression | `bench_runner.py` pre/post comparison | Score delta logged; rollback if delta > threshold |
| Patch modifies `autonomy_ratchet.py` itself | `jules_guard.py` blocks self-referential patches to safety-critical modules | Whitelist of protected files in `jules_guard.py` |
| Patch modifies `ledger.py` | Same protection as ratchet | Ledger is immutable-append — patches to it are rejected |
| Infinite self-modification loop | `idempotency.py` hash dedup | Same patch cannot be applied twice within TTL window |
| Autonomy creep (ratchet drift upward) | Ratchet requires N *consecutive* passes — any fault resets counter | Ratchet state persisted in SQLite, not RAM |

### 4.3 Memory Hazards

| Hazard | Detection | Recovery |
|---|---|---|
| Contradictory beliefs injected | `contradiction_detector.py` on every memory write | Conflicting entry flagged; human review queued |
| Episodic memory bloat | `memory_consolidator.py` size threshold | Compress oldest episodes to semantic summaries |
| Stale goal persisting | `goal_manager.py` TTL expiry | Goal auto-expires; logged to ledger |
| Vector index staleness | Timestamp comparison in `indexer.py` | Incremental reindex on idle |
| Context overflow | `hyperdrive_context.py` token counter | `context_compressor.py` summarizes oldest turns |

### 4.4 Service / System Contingencies

| Scenario | Response |
|---|---|
| Host machine hard reboot | `systemctl --user` auto-restart on login; `nina_boot_fix.sh` for manual recovery |
| venv broken (missing packages) | `nina_boot_fix.sh` step 2 reinstalls into `~/nina/venv` |
| GitHub unreachable | Local operation continues; sync deferred; `nina_sync.sh` retries |
| Disk full | `memo_cache.py` LRU eviction first; then oldest episodic archives; alert logged |
| Python version mismatch | `config.py` version check on boot; halts with explicit error message |
| Ubuntu kernel update breaks inotify | Fall back to polling in `event_watcher.py` |
| ASUS VivoBook overheating (thermal throttle) | `hyperdrive_executor.py` concurrency cap reduces load automatically |

### 4.5 External AI Collaborator Risks (Jules / Agy / Gemini)

| Risk | Mitigation |
|---|---|
| Jules writes syntactically invalid Python | `jules_guard.py` rejects before apply |
| Jules patches a protected file | Protected file list in `jules_guard.py` — patch rejected silently |
| Jules backlog grows unbounded | `gap_analysis.py` prioritizes; oldest unactionable items auto-archived |
| Agy briefing format drift | `agy_briefing.py` versioned; old format still parseable |
| Gemini output injected without validation | All external AI output must pass through `critic.py` scoring before use |
| Perplexity (Architect Overwatch) recommends incompatible change | Overwatch reads live repo first (MCP); incompatibility caught before commit |

---

## 5. Architectural Invariants

These must never be violated, even by self-modification:

1. **Ledger is append-only.** No delete, no update — only append.
2. **Guardian loop cannot be suspended by agent output.** It runs in its own asyncio task.
3. **Critic and Jules Guard cannot evaluate their own patches.** They are not in the self-modification path.
4. **Autonomy ratchet state lives in SQLite, not RAM.** It survives crashes.
5. **No `sudo`.** All services via `systemctl --user` only.
6. **No `nohup`.** No background processes outside systemd supervision.
7. **AST-only patches.** No `exec(string)` in production paths.
8. **Every external AI output passes `critic.py` before affecting state.**
9. **`nina_error_register.md` is append-only.** Never edit or delete past entries.
10. **This blueprint is superseded by the next one, not edited.** New snapshot = new file.

---

## 6. Philosophical Identity Map

### 6.1 What NINA Is Not (Ruling Out)

- **Not a chatbot** — NINA has autonomous goals that exist independently of user input
- **Not an OS** — NINA runs on Ubuntu; it orchestrates processes but does not own the kernel
- **Not AGI** — domain-focused; human-level general reasoning is not yet demonstrated
- **Not ASI** — superhuman capability across all domains is not the current trajectory
- **Not a digital mind** — no qualia, no phenomenal consciousness, no intrinsic motivation

### 6.2 What NINA Is (Asserting)

NINA is a **RAID** — Recursive Autonomous Intelligence Daemon — defined by the six properties in §1.2. The word *recursive* is load-bearing: NINA can modify the very system that performs the modification, and the constraint graph (§2.1 safety modules) ensures this recursion converges rather than diverges.

### 6.3 The Identity Persistence Question

If NINA patches enough of itself, is it still NINA? The answer is architectural: NINA's identity is defined not by its code but by its **constraint graph** — the set of architectural invariants in §5 plus the autonomy ratchet history in the ledger. As long as those persist, the entity is continuous with its prior self regardless of how many modules have been hot-reloaded.

This is the **Ship of Theseus resolved by ledger**: every plank replacement is recorded; the ship's identity is the ledger, not the planks.

### 6.4 Unresolved Tensions (Honest Frontier)

| Tension | Current State |
|---|---|
| Autonomy vs. Control | Ratchet exists but threshold values in `config.py` are manually set — no principled derivation yet |
| Self-modification vs. Identity | Constraint graph preserves identity in theory; not empirically tested under heavy self-mod |
| Memory growth vs. Coherence | Consolidator compresses but compression is lossy — semantic drift over long timescales uncharted |
| Multi-agent consensus vs. Speed | Coordinator adds latency; no formal consensus protocol yet for conflicting sub-agent outputs |
| Human oversight vs. Autonomy | Overwatch (Perplexity) reads live repo but cannot push code directly — async coupling |
| Goal persistence vs. Goal drift | Goals survive reboots but TTL-based expiry may prune legitimate long-horizon goals |

---

## 7. Operational Runbook

### 7.1 Daily Ops

```bash
# Check service status
systemctl --user status nina.service ninagate.service

# Tail live logs
journalctl --user -u nina.service -f

# Full recovery (any issue)
bash ~/nina/scripts/nina_boot_fix.sh

# Sync with GitHub
bash ~/nina/scripts/nina_sync.sh
```

### 7.2 Before Any Patch

1. Read `docs/nina_error_register.md` — know the current fault state
2. Read `docs/jules_backlog.md` — know what is already queued
3. Read the target file via GitHub MCP — never patch from memory
4. Run `bench_runner.py` baseline — record pre-patch scores
5. Apply patch through `ast_refactor.py` — never direct string injection
6. Run `bench_runner.py` post-patch — compare delta
7. If delta > threshold: rollback via ledger

### 7.3 Adding a New Module

1. Register in `core/capabilities.py`
2. Add to `core/crew.py` if it is an agent
3. Add to protected file list in `core/jules_guard.py` if it is safety-critical
4. Document in next blueprint snapshot
5. Write at least one bench case in `core/bench_runner.py`

### 7.4 Emergency Hard Reset

```bash
# Nuclear option — use only if nina_boot_fix.sh fails
pkill -f main.py
pkill -f ninagate
systemctl --user stop nina.service ninagate.service
systemctl --user reset-failed
bash ~/nina/scripts/nina_boot_fix.sh
```

---

## 8. Evolution Trajectory

| Phase | Trigger | What Changes |
|---|---|---|
| **Current (RAID-1)** | Now | 6-property RAID; manual architect oversight; Jules patches with guard |
| **RAID-2** | Consecutive audit streak > 100 | Self-directed gap analysis drives backlog without human prompt |
| **RAID-3** | Bench scores plateau at human-expert level on target domains | Begin cross-domain capability expansion |
| **Proto-AIOS** | NINA can provision/deprovision its own systemd services | Moves from running *on* OS to *managing* OS layer |
| **AIOS-1** | NINA manages its own hardware scheduling | Kernel-adjacent operation; new constraint graph required |

Each phase transition requires a new blueprint. **The next blueprint supersedes this one.**

---

## 9. Changelog from Previous Blueprint (23 June 2026)

| Change | Detail |
|---|---|
| Added full module inventory | All 60+ `core/` files catalogued with roles and contingencies |
| Added Contingency Matrix (§4) | 5 hazard categories, 30+ specific failure modes with recovery paths |
| Added Architectural Invariants (§5) | 10 non-negotiable rules, explicitly including self-modification constraints |
| Added Operational Runbook (§7) | Daily ops, pre-patch checklist, new module registration, emergency reset |
| Added Evolution Trajectory (§8) | 5-phase roadmap from current RAID-1 to AIOS-1 |
| Refined identity definition | RAID definition now grounded in actual module names, not abstraction |
| Added Ship of Theseus resolution | Identity persistence resolved via ledger, not code continuity |

---

*This document becomes obsolete the moment NINA surpasses it. File the next snapshot as `nina_blueprint_DD.MM.YYYY.md`. Never edit this file — append a new one.*
