# NINA Architecture — Boot Sequence & Data Flow

> Last updated: 24 Jun 2026 · Pass 3 — Ouroboros 5 wired

---

## Boot Sequence

Call order in `nina.py` (before serving requests):

```
1. boot_ouroboros()                  ← core/kernel.py
   ├── canonicalizer.canonical_key   ← path normalization firewall
   ├── BloomFilter.load()            ← data/bloom_filter.json
   ├── InvertedIndex.load()          ← data/trie_index.json
   ├── InvertedIndex.index_directory(ROOT)  ← warms token index
   └── ManifestWatcher.start()       ← 5-second Ouroboros polling loop

2. Kernel(event_bus, agent_loop, memory, guardian)
3. asyncio.create_task(kernel.start())
4. systemctl --user start ninagate.service
```

---

## 4-State Kernel Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                      KERNEL LOOP (asyncio)                          │
│                                                                     │
│  STATE 01 — Queue Ingestion                                         │
│    event_bus.queue.get_nowait()                                     │
│    → canonical_event_key()          (canonicalizer)                 │
│    → BloomFilter.might_contain()    ← SKIP if seen                  │
│    → BloomFilter.add() + save()     ← mark seen                     │
│    → TaskPacket(task_id, payload)                                   │
│                                                                     │
│  STATE 02 — Context Assembly                                        │
│    layered_memory.fetch_context_async() / build_context()           │
│    → context_compressor.compress_packet()  ← ~60% token reduction   │
│    → packet.context.update(compressed_ctx)                         │
│                                                                     │
│  STATE 03 — Execute                                                 │
│    asyncio.wait_for(agent_loop_fn(packet), timeout=120s)            │
│    → LLM call / shell exec / tool call                              │
│                                                                     │
│  STATE 04 — Audit + GC  [separate asyncio.Task]                     │
│    guardian.audit(packet, result)   ← AST verify                    │
│    memory.wal_commit(task_id, result)                               │
│    gc.collect(0)                    ← deterministic gen-0           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Ouroboros Self-Healing Loop

The ManifestWatcher runs a background thread polling every 5 seconds.
Any file hash change fires the cascade:

```
file saved / patched
  → ManifestWatcher._check_drift()
  → HivePacket.emit(BLACKBOARD_MUTATION, scope=path)
      ├── ledger.WAL write
      └── EventBus.publish(BLACKBOARD_MUTATION)
           └── Auditor wakes
                ├── AST verify patch
                ├── InvertedIndex.index_file(path)
                ├── BloomFilter.add(canonical_key)
                └── self_patch_logger.record()
```

This loop cannot be stopped by the LLM output it is auditing (asymmetric
by design — Auditor node is a separate thread/task).

---

## Three-Layer Memory Architecture

```
 HOT   core/layered_memory.py   in-process dict  <1ms   recency window
 WARM  core/ledger.py           SQLite WAL        <5ms   session history
 COLD  memory/trie_index.py     JSON on disk      <1ms   full text index
       (no sentence-transformers — pure token match)
```

---

## Ouroboros 5 Module Wiring Map

| Module | Wired In | Trigger | Effect |
|--------|----------|---------|--------|
| `core/canonicalizer.py` | kernel.py STATE 01 | every event | normalises path keys, kills duplicate task routing |
| `core/bloom_filter.py` | kernel.py STATE 01 | every event | probabilistic dedup gate, skips already-seen events |
| `memory/trie_index.py` | boot_ouroboros() + Auditor | boot + BLACKBOARD_MUTATION | sub-ms keyword search, replaces sentence-transformers |
| `core/manifest_watcher.py` | boot_ouroboros() | boot → 5s poll | hash drift → HivePacket → Auditor cascade |
| `memory/context_compressor.py` | kernel.py STATE 02 | every context assembly | compresses context dict ~60% before LLM injection |

---

## Signal Handling

`ManifestWatcher.register_signals()` is called during `boot_ouroboros()`.
SIGTERM and SIGINT stop the watcher gracefully before process exit.
Never use `sudo systemctl` — always `systemctl --user`.
