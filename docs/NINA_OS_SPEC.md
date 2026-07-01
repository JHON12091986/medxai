# NINA OS — Complete Operational Specification

> *The final lock. Every concept combined into one cohesive, self-healing machine lifecycle.*

**Status:** Canonical living spec · Supersedes all prior architecture docs  
**Owner:** kernel.orchestrator  
**Last updated:** 2026-06-23  
**Companion docs:** `OUROBOROS_ARCHITECTURE.md` · `BEDROCK_ENGINEERING.md`

---

## Honesty Header — What Exists vs. What's Planned

| Component | File | State |
|---|---|---|
| Append-only ledger (WAL SQLite) | `core/ledger.py` | ✅ shipped |
| AST symbol indexer | `core/indexer.py` | ✅ exists |
| Regex semantic router | `core/semantic_router.py` | ✅ refactored |
| Canonicalization | `core/canonicalization.py` | ✅ exists |
| AST surgical edit | `core/ast_refactor.py` | ✅ exists |
| File watcher | `core/event_watcher.py` | ✅ exists |
| Circuit breaker | `core/circuit_breaker.py` | ✅ exists |
| Context compressor | `core/context_compressor.py` | ✅ exists |
| Bloom filter | `core/bloom.py` | 🔲 Jules task #1 |
| Immutable EventPacket | `core/event_packet.py` | 🔲 Jules task #2 |
| INTJ/INTP thread pools | `core/thread_pools.py` | 🔲 Jules task #3 |
| SIGTERM handler | `core/signal_handler.py` | 🔲 Jules task #4 |
| Manifest drift hook | `core/event_watcher.py` patch | 🔲 Jules task #5 |
| Memory tier manager | `core/memory_tier.py` | 🔲 Jules task #6 |
| Prompt cache builder | `core/prompt_cache.py` | 🔲 Jules task #7 |

---

## 1. Context Compression — Token Semantic Pruning

### The Problem

Raw agent execution logs look like this:
```
"The system successfully executed the bootstrap script and determined that 
 the Redis connection pool was initialized at 14:22:03 with 8 worker threads..."
```
→ ~40 tokens. Repeated 100x per session = 4,000 wasted tokens per loop.

### The Solution: Structural Key-Value Compression

`core/context_compressor.py` (already exists) strips natural language fluff via regex and compresses to structural markers:

```python
# Raw log line → compressed token
"The system successfully executed the bootstrap script" → "ACT:boot OK ts:14:22:03"
"Redis connection pool initialized with 8 workers"     → "SVC:redis INIT workers:8"
"File /nina/core/agent.py was modified at line 142"    → "FILE:core/agent.py MOD L142"
```

**Token reduction: ~85%.** A 4,000-token session log compresses to ~600 tokens.

### Prompt Caching Alignment

Structure every LLM context window as:

```
┌─────────────────────────────────────────────────────┐
│  STATIC PREFIX (never changes — KV-cached by engine) │
│  System identity, tool defs, core rules, NINA spec   │
│  ~1,500-2,000 tokens — loaded ONCE, reused forever   │
├─────────────────────────────────────────────────────┤
│  DYNAMIC SUFFIX (fresh every call)                   │
│  Pruned event log (compressed) + current task        │
│  ~300-500 tokens                                     │
└─────────────────────────────────────────────────────┘
```

**llama.cpp effect:** Static prefix cached in RAM after first call → subsequent calls skip prefill entirely. Latency: 800ms → 80ms.

**Gemini Flash effect:** Prefix cached at API layer → cached tokens billed at 25% of normal rate.

---

## 2. Dynamic Memory Tiering — Hot / Warm / Cold

```
┌──────────────────────────────────────────────────────────────────┐
│  HOT MEMORY  (Python process RAM)                                │
│  • BloomFilter bitarray (~180KB)                                 │
│  • Active thread locks dict                                      │
│  • Last 10 WAL events (deque maxlen=10)                          │
│  • INTJ/INTP thread pool queues                                  │
│  • Canonicalized path cache (LRU, max 1,000 entries)             │
│  Target: <64MB total                                             │
└────────────────────────────┬─────────────────────────────────────┘
                             ▼ (evict on LRU miss or TTL expiry)
┌──────────────────────────────────────────────────────────────────┐
│  WARM MEMORY  (SQLite — nina.db + nina_symbol_index.db)          │
│  • Ledger: events, state, locks tables                           │
│  • Indexer: symbols, file_hashes tables                          │
│  • Canonical path → hash map                                     │
│  • Manifest registry (file → reason_for_existence)               │
│  Target: <200MB, WAL mode, <5ms read latency                     │
└────────────────────────────┬─────────────────────────────────────┘
                             ▼ (archive on age > 7 days or size > 500MB)
┌──────────────────────────────────────────────────────────────────┐
│  COLD MEMORY  (Disk — ~/nina/archive/)                           │
│  • Full event-sourced transaction history (gzipped .ndjson)      │
│  • Archived AST code dumps                                       │
│  • Old session logs                                              │
│  • Git objects (via normal git history)                          │
│  Target: unlimited, never read in hot path                       │
└──────────────────────────────────────────────────────────────────┘
```

### Predictive Prefetch

When an INTP mechanic thread pulls a task for module `X`, the Orchestrator reads `X`'s manifest `Submodule-Dependencies` and pre-warms Warm → Hot:

```python
def prefetch_for_task(module_path: str) -> None:
    manifest = get_manifest(module_path)          # Warm read ~1ms
    deps = manifest.get("submodule_dependencies", [])
    for dep in deps:
        symbols = get_file_symbols(dep)           # Warm → Hot cache
        _HOT_CACHE[dep] = symbols                 # LRU dict
```

**Effect:** Agent thread starts with all relevant symbols already in RAM. Zero cold-start disk reads during execution.

### Lazy Evaluation — Delta Flags

NINA never rebuilds a full index upfront. Changes are marked as dirty:

```python
# On file change — INTP mechanic thread (fast path)
db.set(f"dirty:{canon_path(path)}", "1")   # <1ms Ledger write
# Do NOT rebuild index yet

# On index read — only then rebuild the changed entry
def get_symbols_lazy(path: str) -> list:
    key = f"dirty:{canon_path(path)}"
    if db.get(key) == "1":
        index_file(Path(path))              # rebuild only this file
        db.delete(key)                      # clear dirty flag
    return get_file_symbols(path)           # read fresh
```

**CPU savings:** A 200-file repo with 5 files changed → 5 file re-indexes, not 200.

---

## 3. Concurrency Safety — Circuit Breaker + Poison Pill

### Circuit Breaker (`core/circuit_breaker.py` — already exists)

Every INTJ/INTP thread execution path is governed by a transactional timer:

```python
# Pseudocode — actual impl in core/circuit_breaker.py
class CircuitBreaker:
    TIMEOUT_S = 30      # INTP mechanics: must commit within 30s
    TIMEOUT_L = 300     # INTJ strategists: must commit within 5min

    def run_guarded(self, fn, task_id, timeout):
        future = executor.submit(fn)
        try:
            result = future.result(timeout=timeout)
            ledger.log("task_complete", meta=task_id)
            return result
        except TimeoutError:
            future.cancel()
            self._trip(task_id)             # circuit opens
            raise

    def _trip(self, task_id):
        ledger.log("circuit_tripped", meta=task_id)
        ledger.release(task_id)             # release idempotency lock
        self._broadcast_poison_pill(task_id)

    def _broadcast_poison_pill(self, task_id):
        # Put sentinel onto all agent queues
        POISON = EventPacket(trace_id="POISON", action="ABORT",
                             path="", content_hash="", meta=frozenset(), ts=time.time())
        for q in _ALL_AGENT_QUEUES:
            q.put_nowait(POISON)
```

### Deadlock Prevention — The Three Rules

1. **Lock ordering:** INTP threads never acquire more than 1 Ledger lock simultaneously
2. **TTL on all locks:** `db.acquire(task_id, ttl=300)` auto-expires — no permanent deadlocks
3. **No cross-pool blocking:** INTP mechanics never `.result()` on INTJ strategist futures

```
DEADLOCK IMPOSSIBLE IF:
  • All locks have TTL          ✓ (Ledger locks table, expires column)
  • No circular waits           ✓ (INTP → queue → INTJ, never reverse)
  • Circuit breaker timeout     ✓ (30s / 300s hard limit per task)
```

### Poison Pill Protocol

```
[Thread timeout]
      │
      ▼
[CircuitBreaker._trip(task_id)]
      ├── Ledger.log("circuit_tripped", task_id)
      ├── Ledger.release(task_id)          ← unlock so other threads can proceed
      ├── Rollback: state = last valid event hash
      └── Broadcast POISON EventPacket to all agent queues
                │
                ▼
      [All agent threads check for POISON on queue.get()]
      [If POISON → skip current task → log → pull next task]
```

---

## 4. Maker-Checker Consensus Pipeline

The agent that writes code is **never** the agent that validates it.

```
┌─────────────┐     EventPacket      ┌─────────────────┐
│  MAKER      │ ──── (immutable) ──► │  CHECKER        │
│ (INTP mech) │                      │ (background     │
│             │                      │  auditor thread)│
│ • Pull task │                      │                 │
│ • Heredoc   │                      │ • ast.parse()   │
│ • Generate  │                      │ • Syntax check  │
│   output    │                      │ • Logic audit   │
└─────────────┘                      └────────┬────────┘
                                              │
                         ┌────────────────────┴──────────────────┐
                         ▼ PASS                                   ▼ FAIL
               [Ledger.log("commit")]              [Ledger.log("checker_reject")]
               [Update SSOT state]                [Broadcast RETRY EventPacket]
               [Cascade sync chain]               [Maker pulls alt strategy]
```

**Key constraint:** Checker thread is always INTJ (slow, careful). Maker is always INTP (fast, executes). They run in separate pools, communicate only via immutable `EventPacket` on a queue — zero shared mutable state.

---

## 5. The Complete Operational Loop — Every Step Mapped to a File

```
[1. FILE CHANGE / EVENT HOOK]
    core/event_watcher.py — inotify IN_CLOSE_WRITE
          │
          ▼
[2. CANONICALIZATION & DEDUP]
    core/canonicalization.py — canon_path() + canon_key()
    core/bloom.py            — BloomFilter.__contains__()  🔲
    core/ledger.py           — hash dedup check (events table)
          │
          ▼
[3. WRITE-AHEAD LOG]
    core/ledger.py — Ledger.log(action, path)  before any ACT
    core/ledger.py — Ledger.acquire(task_id)   idempotency lock
          │
          ▼
[4. ASYMMETRIC DISPATCH]
    core/thread_pools.py — run_mechanic() / run_strategist()  🔲
    core/event_packet.py — EventPacket(NamedTuple) on queue   🔲
          │
    ┌─────┴──────┐
    ▼            ▼
[INTP MECH]  [INTJ STRAT]
Exec task    Monitor DAG
Heredoc      CFG/LLM call
AST edit     Structured out
    │            │
    └─────┬──────┘
          ▼
[5. MAKER-CHECKER CONSENSUS]
    core/critic.py        — AST static analysis on output
    core/circuit_breaker.py — timeout guard + poison pill
          │
          ▼
[6. CASCADE SYNC CHAIN]
    core/indexer.py       — lazy dirty-flag re-index
    core/ast_refactor.py  — docstring stubs for new functions
    core/file_registry.py — manifest header update
    core/ledger.py        — Ledger.log("sync_complete")
    core/ledger.py        — Ledger.set("ssot_hash", new_hash)
          │
          ▼
[SSOT UPDATED — LOOP COMPLETE]
    core/telemetry.py     — span.end(), emit to Jaeger  🔲
```

---

## 6. Resource Budget — ASUS VivoBook X530FN Targets

| Resource | Budget | Enforcement |
|---|---|---|
| RAM (NINA process total) | <512MB | Thread pool caps + LRU hot cache eviction |
| CPU (idle background) | <5% | `os.nice(10)` on strategist pool |
| CPU (active event) | <40% burst, <5s | Circuit breaker 30s timeout |
| LLM tokens/hour (idle) | <200 | Memoized prompts + static prefix cache |
| LLM tokens/hour (active) | <2,000 | CFG structured output (no retry loops) |
| Disk writes/min (idle) | <10 | Bloom filter drops duplicate events |
| SQLite DB size | <200MB warm | 7-day archive rotation to cold |

---

## 7. Jules Build Queue — Priority Order

Each task unblocks the next. Submit in order.

```
#1  core/bloom.py
    BloomFilter(capacity=100_000, error_rate=0.001)
    Methods: add(item), __contains__(item), save(path), load(path)
    Deps: stdlib only (bytearray + hashlib)
    Wires into: event_watcher.py gate, indexer.py dedup pre-check

#2  core/event_packet.py
    EventPacket(NamedTuple): trace_id, action, path, content_hash, meta(frozenset), ts
    POISON sentinel constant
    Deps: typing, time
    Wires into: all agent queue communications

#3  core/thread_pools.py
    _STRATEGIST_POOL = ThreadPoolExecutor(max_workers=2)
    _MECHANIC_POOL   = ThreadPoolExecutor(max_workers=8)
    run_strategist(fn, *args), run_mechanic(fn, *args)
    os.nice() on thread start
    Deps: concurrent.futures, os

#4  core/signal_handler.py
    signal.signal(SIGTERM/SIGINT, _shutdown)
    _shutdown: flush pools → ledger.log(shutdown) → sys.exit(0)
    Deps: signal, sys, core.ledger, core.thread_pools

#5  core/memory_tier.py
    HotCache: LRU dict, max 1,000 entries, <64MB target
    prefetch_for_task(module_path)
    set_dirty(path) / is_dirty(path) / clear_dirty(path)
    Deps: functools.lru_cache, core.ledger

#6  core/prompt_cache.py
    build_static_prefix() → str  (cached, never changes)
    memoized_context(task_str) → str  (compressed dynamic suffix)
    Deps: core.context_compressor, core.ledger, hashlib

#7  core/telemetry.py
    opentelemetry spans wired to every EventPacket trace_id
    Jaeger OTLP exporter (localhost:4317)
    Deps: opentelemetry-sdk (optional, graceful no-op if missing)
```

---

*This is the final, complete NINA OS specification.*  
*All prior architecture docs (`NINA_V15_ARCHITECTURE.md`, `nina_vnext_blueprint.md`, `nina_v14_blueprint.md`) are superseded by this file + `OUROBOROS_ARCHITECTURE.md` + `BEDROCK_ENGINEERING.md`.*
