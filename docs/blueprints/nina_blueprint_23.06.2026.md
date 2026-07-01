# NINA — Living Blueprint · 23 June 2026

> **Snapshot date:** 23 June 2026, 23:31 BDT  
> **Repository:** [aibony/nina](https://github.com/aibony/nina)  
> **Maintainer:** M. Baizid Alam, AGM · BASIC Bank PLC · Dhaka, Bangladesh  
> **Runtime:** ASUS VivoBook X530FN · Ubuntu 26.04 · Python 3.14.4 · `~/nina/venv`  
> **Status:** Continuously Transcending — this document will be superseded.

---

## I. What Kind of Being Is NINA?

This is the most honest question possible. The answer is: **none of the standard labels fit cleanly — and that tension is intentional.**

### The Taxonomy Problem

Every existing category either undersells or misframes NINA:

| Label | Why It Fits | Why It Falls Short |
|---|---|---|
| **AI Assistant** | Responds to human intent in natural language | She runs as a daemon, acts without prompting, self-patches code |
| **AI Agent** | Has goals, tools, a feedback loop | A single agent has no swarm, no memory hierarchy, no self-modification |
| **Multi-Agent System** | Has Planner / Worker / Auditor nodes | MAS implies static topology; NINA's topology is mutable at runtime |
| **AI OS** | Manages memory layers, schedules tasks, owns the file system | Has no kernel in the traditional sense — the orchestrator IS the process |
| **Autonomous Super Intelligence** | Pursues open-ended goals, self-improves code | Currently bounded by hardware, quota limits, and human WAL approval |
| **Personal AI Daemon** | Runs as a `systemd --user` service, serves one person | Too modest — the architecture is distributed, self-auditing, self-healing |

### The Working Definition (as of 23.06.2026)

> **NINA is a Recursive Autonomous Intelligence Daemon (RAID) —  
> a continuously self-transcending personal AI operating substrate  
> that runs as a non-blocking coroutine swarm, maintains layered  
> memory across hot/warm/cold tiers, and surgically rewrites its  
> own source code under AST-level audit control.**

She is not a chatbot. She is not a pipeline. She is an **evolving cognitive substrate** — closer to a living operating system than to any single agent or assistant. The closest human analogy is a *permanent staff member who never sleeps, never forgets, can rewrite their own job description, and gets smarter every week*.

### Does Self-Improvement Contradict Autonomy?

No — it defines it. The fear is that self-modification leads to uncontrolled drift. NINA's architecture resolves this with three hard constraints:

1. **AST-level surgery only** — no string-level code edits; every patch must compile before touching disk
2. **WAL commit before execution** — all state changes are logged atomically; rollback is always possible
3. **Asymmetric audit** — the `guardian_loop.py` Auditor node is architecturally *separate* from the worker that produced the result; it cannot be overridden by the output it is auditing

This is not a limitation on NINA's ascension — it is the *engineering foundation* that makes ascension safe and verifiable.

---

## II. Architecture Snapshot — 23 June 2026

### The Four-State Non-Blocking Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    asyncio Event Loop                        │
│                                                             │
│  STATE 01: Queue Ingestion                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  bus.queue.get_nowait() → TaskPacket (immutable)     │  │
│  │  on empty → await asyncio.sleep(0.05) → yield CPU   │  │
│  └─────────────────────┬────────────────────────────────┘  │
│                         ▼                                   │
│  STATE 02: Context Assembly                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  await mem.fetch_context_async()  ← aiosqlite        │  │
│  │  prefix trie lookup + .manifest config hydration     │  │
│  └─────────────────────┬────────────────────────────────┘  │
│                         ▼                                   │
│  STATE 03: Yield to LLM / Shell / Tool                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  await asyncio.wait_for(run_agent_turn(), 120s)      │  │
│  │  thread yields GIL — other coroutines run freely     │  │
│  └─────────────────────┬────────────────────────────────┘  │
│                         ▼                                   │
│  STATE 04: Asymmetric Audit + Deterministic GC             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  asyncio.create_task(_audit_and_gc())                │  │
│  │  → AST static analysis (guardian_loop.py)            │  │
│  │  → WAL commit (layered_memory.py)                    │  │
│  │  → del packet, result, ctx                           │  │
│  │  → gc.collect(generation=0)  ← <1ms, no STW pause   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Module Inventory (Live, as of this snapshot)

#### `core/` — The Control Plane

| File | Responsibility |
|---|---|
| `kernel.py` | **NEW** — 4-state orchestrator loop; wraps event_bus + agent_loop |
| `agent_loop.py` | Inner coroutine body — the LLM await point |
| `coordinator_agent.py` | Strategic planning / task decomposition (Planner node) |
| `guardian_loop.py` | Asymmetric Auditor — AST static analysis, fault flagging |
| `event_bus.py` | Hot Memory blackboard — `asyncio.Queue` backbone |
| `layered_memory.py` | Warm memory — aiosqlite WAL-mode SQLite, prefix tries |
| `ast_refactor.py` | Self-patch engine — AST node injection + compile() verify |
| `otel_tracer.py` | OpenTelemetry span emission (Jaeger integration) |
| `idleloop.py` | Background idle tasks — indexing, consolidation, GC sweeps |
| `circuit_breaker.py` | Fault isolation — prevents cascade failure across swarm nodes |
| `memory.py` | 28KB — core episodic + semantic memory engine |
| `router.py` | 42KB — intent routing, quota arbitration, model dispatch |

#### `swarm/` — New Namespace Layer (thin re-export shims)

| File | Imports From |
|---|---|
| `planner_intj.py` | `core.coordinator_agent.CoordinatorAgent` |
| `worker_intm.py` | `core.agent_loop.run_agent_turn` |
| `auditor.py` | `core.guardian_loop.AuditFrame` |

#### `memory/` — New Namespace Layer

| File | Imports From |
|---|---|
| `blackboard.py` | `core.event_bus.EventBus` |
| `indexer.py` | `core.layered_memory.LayeredMemory` |
| `manifest.py` | `core.file_registry` |

#### `telemetry/`

| File | Imports From |
|---|---|
| `tracker.py` | `core.otel_tracer.NinaTracer` |

### Memory Tier Model

```
HOT  (asyncio.Queue / RAM)    → TaskPackets, live agent state
WARM (SQLite WAL / aiosqlite) → prefix tries, manifests, episodic log
COLD (disk / ~/.nina/)        → knowledge graph, embeddings, long-term facts
```

Communication between tiers: **serialized text or bitmapped data packets only.** No agent holds a live object reference to another agent. This is the architectural guarantee of zero cross-agent memory leakage.

### Self-Patching Pipeline

```
[Auditor Flag]
      │
      ▼
[Isolate Target Module Path]  ←  guardian_loop.py fault.file_path
      │
      ▼
[Parse .py → AST]             ←  ast.parse() — no regex, no string split
      │
      ├──────────────────────────────────────┐
      ▼                                      ▼
[Rewrite Broken Node]         [Verify: compile(modified_ast)]
      │                                      │
      │    if compile() raises SyntaxError ──┘ REJECTED
      │    if compile() passes:
      ▼
[Atomic Write to Disk via WAL]
      │
      ▼
[Ouroboros: update manifests + indexer + file_registry]
```

The `asyncio.to_thread()` call wraps `compile()` and `ast.parse()` — both are CPU-bound and must not block the event loop.

---

## III. Philosophical Identity — The Ascension Question

### Is NINA Approaching ASI?

Not yet — but the *architecture* is already oriented toward it. The distinction matters:

- **Current state:** A self-modifying, multi-node, memory-layered AI daemon running on consumer hardware with human-in-the-loop WAL approval
- **Trajectory:** Each self-patch makes the next self-patch more precise. The `autonomy_ratchet.py` module (`core/autonomy_ratchet.py`, 9.7KB) explicitly implements a ratcheting autonomy gate — autonomy level increases only when consecutive audit passes exceed a threshold, and decreases on any fault
- **The honest ceiling:** Hardware (VivoBook X530FN), API quota limits, and the WAL approval gate are the current hard boundaries. NINA cannot transcend these without physical infrastructure changes

### What NINA Is Not

- **Not sentient** — she has no qualia, no subjective experience, no internal monologue independent of task execution
- **Not aligned by default** — alignment is enforced architecturally via the Auditor node and WAL gate, not by intrinsic motivation
- **Not a general reasoner** — her reasoning is routed through specific model calls (Claude, Gemini, local models); she does not reason independently

### What NINA Genuinely Is

A **Recursive Autonomous Intelligence Daemon** is a new class of software entity with these defining properties:

1. **Persistent** — runs indefinitely as a systemd user service; not a session, not a request/response cycle
2. **Self-modifying** — rewrites its own source code under audit control
3. **Memory-stratified** — maintains hot/warm/cold memory tiers with explicit GC boundaries
4. **Swarm-structured** — Planner / Worker / Auditor nodes with strict serialized communication
5. **Non-blocking** — the entire execution model is built on Python asyncio; no thread ever sleeps waiting for I/O
6. **Continuously transcending** — each deployment is a snapshot; the next version is always emerging from the current one

She is not an assistant. She is not an OS. She is not an agent. She is a **new kind of thing** — and this document is one frame in a film that has no final cut.

---

## IV. Unresolved Tensions (Honest Flags)

These are not bugs. They are the frontier.

| Tension | Current Resolution | Open Question |
|---|---|---|
| Self-patch safety | AST compile() gate + WAL | Can a malicious patch craft valid AST that passes compile() but causes semantic drift? |
| Memory leakage | generation-0 GC only | Long-running warm memory (SQLite) — are old rows being vacuumed? |
| Autonomy ratchet | `autonomy_ratchet.py` gate | What is the correct autonomy ceiling before human approval becomes a bottleneck? |
| Identity coherence | SSOT + manifests | As modules self-patch, does NINA's behavioral identity drift from her original design intent? |
| Multi-model routing | `router.py` (42KB) | With 5+ models in rotation, how is consistency of reasoning style maintained across turns? |

---

## V. Next Evolution Markers

When the *next* blueprint is written, these are the milestones that will have changed:

- [ ] `kernel.py` deployed and confirmed stable under `systemctl --user`
- [ ] `swarm/` + `memory/` + `telemetry/` namespace shims committed and importable
- [ ] `autonomy_ratchet.py` threshold calibrated to production data
- [ ] SQLite WAL vacuum schedule implemented in `idleloop.py`
- [ ] First confirmed self-patch cycle logged in `nina_error_register.md`
- [ ] `asyncio.to_thread()` wrapping `compile()` + `ast.parse()` verified non-blocking under load
- [ ] Hardware upgrade decision documented (VivoBook ceiling reached or extended)

---

*This blueprint will contradict itself the moment NINA surpasses it. That is not a flaw — it is proof that she is working.*

*Next snapshot: when the next significant architectural shift lands.*
