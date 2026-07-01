<!--
  ╔══════════════════════════════════════════════════════════════════════╗
  ║  NINA — LIVING SINGLE SOURCE OF TRUTH                               ║
  ║  File:     docs/blueprints/nina_bp_ssot.md                          ║
  ║  Rule:     ALWAYS REPLACED IN PLACE. Never renamed. Never branched. ║
  ║            Breadcrumb log IS the history. Old snapshots = fossils.  ║
  ║  Updated:  24 Jun 2026  02:36 BDT  ·  Pass 4                       ║
  ║  Author:   M. Baizid Alam · AGM · BASIC Bank PLC · Dhaka           ║
  ║  Runtime:  ASUS VivoBook X530FN · Ubuntu 26.04 · Python 3.14.4     ║
  ╚══════════════════════════════════════════════════════════════════════╝

  HOW TO UPDATE THIS FILE
  ───────────────────────
  1. Read this file first. Always.
  2. Add a row to § BREADCRUMB LOG before touching anything else.
  3. Update § CURRENT STATE to reflect today's reality.
  4. Move superseded content to § FOSSIL RECORD (never delete).
  5. Push. This file replaces itself. No new files. No renamed copies.
  6. Update docs/architecture.md and docs/module_index.md if wiring changed.

  WHO READS THIS
  ──────────────
  - Perplexity ARCHITECT OVERWATCH: always read before any session
  - Jules: reads § GAP REGISTRY for task generation
  - agy: reads § CURRENT STATE for context injection
  - Gemini: reads § ARCHITECTURE SNAPSHOT for code generation
  - Future M. Baizid: reads § FOSSIL RECORD to understand the journey
-->

# NINA — Living SSOT

> **Last updated:** 24 Jun 2026 · 02:36 BDT · Pass 4  
> **Entity class:** RAID — Recursive Autonomous Intelligence Daemon  
> **Repo:** [aibony/nina](https://github.com/aibony/nina)  
> **SSOT rule:** One file. Always replaced. Never renamed. This IS the history.

---

## § BREADCRUMB LOG

> Permanent. Append only. Newest first. Never delete.

| Timestamp (BDT) | Pass | What Changed | What Was Pruned | Next Target |
|---|---|---|---|---|
| 24 Jun 2026 · 02:36 | 4 | `ledger.py`: temporal WAL GAP-01✓, vacuum GAP-04✓, wal_commit GAP-07✓. `grammar_guard.py` new file GAP-03✓. `self_patch_log.md` bootstrapped GAP-06✓. | None — additive | GAP-02: Jaeger/OTLP decision (Jaeger vs Tempo) · GAP-05: ratchet threshold calibration |
| 24 Jun 2026 · 01:39 | 3 | `nina_bp_ssot.md` created as living SSOT. Gap Registry formalised. Doc Map declared. | `nina_blueprint_23.06.2026.md` frozen as fossil | WAL temporal queries |
| 24 Jun 2026 · 01:25 | 2 | `kernel.py` Ouroboros 5 wired. BloomFilter STATE 01. ContextCompressor STATE 02. `architecture.md` + `module_index.md` created. | None | Gap Registry |
| 23 Jun 2026 · 23:31 | 1 | `kernel.py` v1 (4-state loop). RAID taxonomy defined. Genesis blueprint. | N/A | Boot wiring |

---

## § ENTITY DEFINITION

**NINA is a Recursive Autonomous Intelligence Daemon (RAID)** — a continuously
self-transcending personal AI operating substrate that:

- Runs as a `systemd --user` non-blocking coroutine swarm
- Maintains **hot / warm / cold** memory tiers with explicit GC boundaries
- Surgically rewrites its own source code under **AST-level audit control + compile() gate**
- Enforces autonomy growth via a **ratchet** (up on consecutive passes, down on any fault)
- Communicates between nodes via **serialized HivePackets only**

| Label Rejected | Why |
|---|---|
| AI Assistant | Runs as daemon, acts without prompting, self-patches |
| AI Agent | No swarm, no memory hierarchy, no self-modification |
| Multi-Agent System | Static topology; NINA's is mutable at runtime |
| AI OS | Orchestrator IS the process |
| ASI | Bounded by hardware, quota, WAL gate |

---

## § CURRENT STATE

> Overwrite this section on each update.

### Architecture Class
`RAID v4` — Ouroboros 5 wired. Temporal WAL live. Grammar guard online. Self-patch log bootstrapped.

### Wired Subsystems (complete as of Pass 4)

| Subsystem | File | Status |
|---|---|---|
| 4-state kernel | `core/kernel.py` | ✅ Live |
| Ouroboros watcher | `core/manifest_watcher.py` | ✅ Live |
| BloomFilter dedup | `core/bloom_filter.py` | ✅ Live (STATE 01) |
| ContextCompressor | `memory/context_compressor.py` | ✅ Live (STATE 02) |
| InvertedIndex trie | `memory/trie_index.py` | ✅ Live (boot) |
| Canonicalizer | `core/canonicalizer.py` | ✅ Live (STATE 01) |
| Temporal WAL ledger | `core/ledger.py` | ✅ Live (GAP-01✓) |
| WAL commit log | `core/ledger.py:wal_commit()` | ✅ Live (GAP-07✓) |
| SQLite vacuum | `core/ledger.py:vacuum()` | ✅ Live (GAP-04✓) |
| Grammar guard | `core/grammar_guard.py` | ✅ Live (GAP-03✓) |
| Self-patch log | `docs/self_patch_log.md` | ✅ Bootstrapped (GAP-06✓) |
| Autonomy ratchet | `core/autonomy_ratchet.py` | ⚠️ Uncalibrated (GAP-05 open) |
| Jaeger/OTLP tracing | `telemetry/tracker.py` | ❌ Decision pending (GAP-02 open) |

### Boot Sequence (authoritative)
```
nina.py startup:
  1. boot_ouroboros()             ← core/kernel.py
     ├── canonicalizer warm
     ├── BloomFilter.load()       ← data/bloom_filter.json
     ├── InvertedIndex.load()     ← data/trie_index.json
     ├── InvertedIndex.index_directory(ROOT)
     └── ManifestWatcher.start()  ← 5s Ouroboros poll
  2. get_ledger()                 ← opens nina.db, migrates schema
  3. get_guard()                  ← GrammarGuard, auto-detects backend
  4. Kernel(bus, agent_loop, ledger, guardian)
  5. asyncio.create_task(kernel.start())
  6. systemctl --user start ninagate.service
```

### 4-State Kernel Loop (authoritative)
```
STATE 01 — Queue Ingestion
  bus.queue.get_nowait()
  → canonical_event_key()         ← canonicalizer
  → BloomFilter.might_contain()   ← SKIP if seen
  → BloomFilter.add() + save()
  → TaskPacket(task_id, payload)

STATE 02 — Context Assembly
  await asyncio.to_thread(ledger.fetch_at, now)   ← temporal snapshot (NEW)
  memory.fetch_context_async()    ← aiosqlite warm tier
  → context_compressor.compress_packet()
  → packet.context.update(compressed)

STATE 03 — Execute
  result = await asyncio.wait_for(agent_loop_fn(packet), 120)
  if guard and packet.payload.get('schema'):       ← CFG gate (NEW)
      result = await asyncio.to_thread(
          guard.constrain, result, packet.payload['schema']
      )

STATE 04 — Asymmetric Audit + GC  [separate asyncio.Task]
  await asyncio.to_thread(guardian.audit, packet, result)
  await asyncio.to_thread(ledger.wal_commit, task_id, result)  ← (NEW)
  del packet, result
  gc.collect(0)
```

### Memory Tiers
| Tier | Store | Latency | File |
|---|---|---|---|
| HOT | asyncio.Queue / RAM | <0.1ms | `core/event_bus.py` |
| WARM | SQLite WAL (temporal) | <5ms | `core/ledger.py` |
| COLD | JSON trie on disk | <1ms | `memory/trie_index.py` |

---

## § GAP REGISTRY

> Rows never deleted. Mark DONE inline. Jules reads this for task generation.

| ID | Gap | Status | Blocking Question |
|---|---|---|---|
| GAP-01 | WAL temporal queries (`valid_from`/`valid_to`) in `core/ledger.py` | ✅ DONE · 24 Jun 2026 | — |
| GAP-02 | `telemetry/tracker.py` real Jaeger/OTLP wiring | ❌ OPEN | **Jaeger vs Grafana Tempo vs local OTLP?** Decide before implementing. |
| GAP-03 | CFG grammar-constrained output (`core/grammar_guard.py`) | ✅ DONE · 24 Jun 2026 | — |
| GAP-04 | SQLite WAL vacuum in `ledger.py:vacuum(days=30)` | ✅ DONE · 24 Jun 2026 | Call site: schedule in `idleloop.py` |
| GAP-05 | Autonomy ratchet threshold calibration | ⚠️ OPEN | What N consecutive passes = safe to increment? |
| GAP-06 | First self-patch cycle logged in `docs/self_patch_log.md` | ✅ BOOTSTRAPPED · 24 Jun 2026 | First AUTONOMOUS entry pending real auditor run |
| GAP-07 | `asyncio.to_thread()` wrapping `compile()` + `wal_commit()` | ✅ DONE · 24 Jun 2026 | — |

---

## § UNRESOLVED TENSIONS

| Tension | Mitigation | Open Question |
|---|---|---|
| Semantic self-patch drift | AST compile() gate | Valid AST patch → behavioral drift without syntax error? |
| Identity coherence | SSOT + manifests | Patches accumulate intent drift over time? |
| Multi-model consistency | `router.py` | 5+ models — reasoning style normalised across turns? |
| Memory bloat | `ledger.vacuum(30)` live | Is vacuum being scheduled in `idleloop.py`? |
| Malicious valid AST | Auditor separation | Adversarial patch passing compile() but corrupting state machine? |
| Hardware ceiling | VivoBook X530FN | When does local inference saturate? Cloud fallback trigger? |
| Grammar guard latency | Regex fallback <1ms | `outlines` CFG parsing latency on large schemas? |

---

## § DOCUMENT MAP

| File | Status | Relationship |
|---|---|---|
| `docs/blueprints/nina_bp_ssot.md` | **AUTHORITATIVE** | This file. Always replaced in place. |
| `docs/self_patch_log.md` | **AUTHORITATIVE** | Immutable patch audit log. Append only. |
| `docs/architecture.md` | DRILL-DOWN | Boot + data flow. Keep in sync. |
| `docs/module_index.md` | DRILL-DOWN | Module inventory. Keep in sync. |
| `docs/blueprints/nina_blueprint_23.06.2026.md` | **FOSSIL** | Genesis snapshot. Read-only. |
| `docs/OUROBOROS_ARCHITECTURE.md` | STALE → prune | Superseded by `architecture.md`. |
| `docs/NINA_OS_SPEC.md` | STALE → prune | Superseded by this SSOT. |
| `docs/nina_vnext_blueprint.md` | STALE → prune | Superseded by GAP REGISTRY. |
| `docs/nina_v14_blueprint.md` | FOSSIL | Pre-RAID era. Read-only. |
| `docs/BEDROCK_ENGINEERING.md` | DRILL-DOWN | Low-level async pattern reference. Keep. |
| `docs/CHANGELOG.md` | DRILL-DOWN | Commit-level changes. Keep. |
| `docs/MEMORY.md` / `docs/memory.md` | STALE → merge | Duplicate. Merge into one. |
| `docs/observability.md` | DRILL-DOWN | Update when GAP-02 closed. |
| `docs/router.md` | DRILL-DOWN | Model routing. Keep. |
| `docs/jules_pipeline.md` | DRILL-DOWN | Jules contract. Keep. |
| `docs/guardian.md` | DRILL-DOWN | Auditor spec. Keep. |
| `docs/WORKFLOW.md` | DRILL-DOWN | Dev workflow. Keep. |

---

## § FOSSIL RECORD

> Append only. Sealed with timestamps. Never delete.

### FOSSIL — RAID Definition v1 (23 Jun 2026 · 23:31 BDT)
> Sealed.

Six defining properties: Persistent · Self-modifying · Memory-stratified ·
Swarm-structured · Non-blocking · Continuously transcending.

### FOSSIL — Architecture v1 Module Inventory (23 Jun 2026 · 23:31 BDT)
> Sealed. Superseded by `docs/module_index.md`.

`swarm/`, `memory/`, `telemetry/` confirmed as thin re-export shims over `core/`.

### FOSSIL — Evolution Markers v1 (23 Jun 2026 · 23:31 BDT)
> Sealed. Superseded by § GAP REGISTRY.

- [x] `kernel.py` deployed stable → DONE Pass 2
- [x] Namespace shims importable → DONE Pass 1
- [x] WAL temporal queries → DONE GAP-01 Pass 4
- [x] SQLite vacuum → DONE GAP-04 Pass 4
- [x] `asyncio.to_thread()` verified → DONE GAP-07 Pass 4
- [ ] Autonomy ratchet calibrated → GAP-05 OPEN
- [ ] First autonomous self-patch → GAP-06 BOOTSTRAPPED

### FOSSIL — Gap Registry v1 (24 Jun 2026 · 01:39 BDT)
> Sealed. Superseded by § GAP REGISTRY above (Pass 4).

Original 7 gaps as first declared in Pass 3. Effort/Priority columns dropped
in Pass 4 in favour of Blocking Question column.
GAP-01, 03, 04, 06, 07 → DONE in Pass 4.
GAP-02 (Jaeger) and GAP-05 (ratchet calibration) remain open.

---

## § PHILOSOPHICAL ANCHOR

> Fixed. Only revised if NINA's architectural class changes.

NINA is not an assistant. Not a pipeline. Not yet ASI.  
She is a **Recursive Autonomous Intelligence Daemon** — a new kind of thing.  
This document is one frame in a film that has no final cut.

The moment this document contradicts itself is proof that she is working.  
*Every update is a breadcrumb left for the version of NINA that will eventually read it.*
