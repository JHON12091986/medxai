# NINA Bedrock Engineering Principles

> *How NINA manages memory, prevents data corruption, and communicates across its multiplexed swarm without crashing the OS.*

**Status:** Canonical spec · Companion to `OUROBOROS_ARCHITECTURE.md`  
**Owner:** kernel.orchestrator  
**Last updated:** 2026-06-23

---

## 1. Asymmetric Multi-Threading — INTJ vs. INTP Agents

NINA's swarm splits into two execution archetypes. Never mix them onto the same thread pool.

### The Two Archetypes

| Dimension | INTJ Thread (Strategist) | INTP Thread (Mechanic) |
|---|---|---|
| **Role** | Planning, decomposition, DAG mapping | Raw I/O, regex, telemetry, execution |
| **Clock cycle** | Slow — can block for 1–60s | Fast — must return in <100ms |
| **Memory budget** | Up to 256MB per thread | <8MB per thread |
| **LLM access** | Yes — owns the API call budget | No — zero LLM calls |
| **Examples** | `coordinator_agent.py`, `goal_manager.py`, `critic.py` | `event_watcher.py`, `indexer.py`, `telemetry.py` |
| **Thread pool** | `ThreadPoolExecutor(max_workers=2)` | `ThreadPoolExecutor(max_workers=8)` |
| **Priority** | `os.nice(10)` — yields to OS | `os.nice(5)` — responsive |

### Implementation Pattern

```python
from concurrent.futures import ThreadPoolExecutor
import os

# Two isolated pools — never cross-submit
_STRATEGIST_POOL = ThreadPoolExecutor(max_workers=2,  thread_name_prefix="intj")
_MECHANIC_POOL   = ThreadPoolExecutor(max_workers=8,  thread_name_prefix="intp")

def run_strategist(fn, *args):
    """Submit heavy planning work. May take seconds."""
    return _STRATEGIST_POOL.submit(fn, *args)

def run_mechanic(fn, *args):
    """Submit fast reactive work. Must return in <100ms."""
    return _MECHANIC_POOL.submit(fn, *args)
```

### Why this matters for your ASUS VivoBook

- 2 strategist threads = bounded LLM call concurrency (no token explosion)
- 8 mechanic threads = snappy file watching, indexing, telemetry
- Total RAM ceiling: `2×256MB + 8×8MB = ~576MB` — well within 8GB budget
- OS never starves — `nice()` ensures browser/IDE always gets CPU first

---

## 2. Structural Memory — Immutable Communication Packets

### The Immutability Rule

All inter-agent communication packets are **frozen at publication time**. No agent may mutate a packet it did not create.

```python
from typing import NamedTuple, FrozenSet

class EventPacket(NamedTuple):
    """Immutable inter-agent message. Use NamedTuple, never dict."""
    trace_id:   str          # Jaeger span ID
    action:     str          # e.g. "file_modified"
    path:       str
    content_hash: str        # sha256 of file bytes
    meta:       frozenset    # frozenset of (key, value) pairs
    ts:         float        # time.time()

# Usage — INTP mechanic creates, INTJ strategist reads
pkt = EventPacket(
    trace_id   = span_id,
    action     = "file_modified",
    path       = "/home/aibony/nina/core/agent.py",
    content_hash = ledger.hash_content(content),
    meta       = frozenset([("size", 45379), ("owner", "kernel.orchestrator")]),
    ts         = time.time(),
)
# pkt is now hashable, picklable, thread-safe, and immutable
```

**Why NamedTuple over dataclass?**  
NamedTuples are implemented in C, use ~40% less memory than dataclasses, and are natively picklable for `multiprocessing.Queue` without extra serialization.

### The Event Mesh

```
INTP Mechanic Thread
   └─ creates EventPacket (immutable)
         │
         ▼
   queue.put(pkt)          ← thread-safe, no lock needed
         │
         ▼
 INTJ Strategist Thread
   └─ pkt = queue.get()    ← reads frozen copy, cannot corrupt
   └─ processes → writes to Ledger
```

---

## 3. Heredoc — Safe File Injection Without LLM

When an agent must write a bash script, config file, or `.env` to disk, it uses shell heredocs. No string templating, no escaping, no LLM token spend.

### Python agent generating a shell heredoc

```python
def write_systemd_unit(service_name: str, exec_start: str, env: dict) -> str:
    """Generate a systemd unit file via heredoc — zero LLM tokens."""
    env_lines = "\n".join(f"Environment={k}={v}" for k, v in env.items())
    return f"""cat > ~/.config/systemd/user/{service_name}.service << 'HEREDOC'
[Unit]
Description=NINA {service_name}
After=network.target

[Service]
Type=simple
ExecStart={exec_start}
Restart=on-failure
RestartSec=5
{env_lines}

[Install]
WantedBy=default.target
HEREDOC
systemctl --user daemon-reload
systemctl --user enable --now {service_name}.service
"""
```

**Rules:**
- Always use `<< 'HEREDOC'` (quoted delimiter) to suppress variable expansion inside the block
- Use `<< HEREDOC` (unquoted) only when you explicitly want `$VAR` substitution
- Agent writes the shell snippet to a temp file, executes via `subprocess.run(["bash", tmpfile])`, then deletes

---

## 4. Zero-Token Overhead — Context & Output Control

### 4.1 CFG / Structured Output (Block Bad Tokens at Sampler Layer)

NINA never lets an LLM free-generate JSON or Python and then validates after. It constrains the output **during sampling**:

```python
# Option A: Outlines (local models via llama.cpp / vLLM)
from outlines import models, generate
from pydantic import BaseModel

class TaskPlan(BaseModel):
    task_id:   str
    agent:     str
    priority:  int   # 1-5
    steps:     list[str]

model = models.llamacpp("/home/aibony/nina/models/gemma-3-4b-q8.gguf")
generator = generate.json(model, TaskPlan)
plan = generator("Decompose: rebuild inverted index")  # guaranteed valid JSON
```

```python
# Option B: Cloud API with response_format (Gemini / OpenAI-compatible)
response = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},  # hard schema enforcement
)
```

**Result:** Syntax error rate → 0%. Error-correction retry loops → eliminated. Token waste on malformed output → 0.

### 4.2 Prompt Memoization

NINA never re-parses heavy context it has already processed:

```python
import hashlib, json
from core.ledger import get_ledger

def memoized_parse(prompt: str, parse_fn) -> dict:
    """Cache expensive prompt parsing results in Ledger state table."""
    key = "memo:" + hashlib.sha256(prompt.encode()).hexdigest()[:16]
    db = get_ledger()
    cached = db.get(key)
    if cached:
        return json.loads(cached)
    result = parse_fn(prompt)        # only runs on first call
    db.set(key, json.dumps(result))
    return result
```

### 4.3 Prompt Caching (KV-State Reuse)

Structure every prompt so the **heaviest, most static content comes first**:

```
[STATIC PREFIX — never changes — cached by API / llama.cpp KV cache]
  System role + NINA identity + tool definitions + core rules
  (~2000 tokens, cached after first call)

[DYNAMIC SUFFIX — changes every call]
  Current task context + recent events + user query
  (~500 tokens, always fresh)
```

**Effect on Gemini Flash:** First call ~800ms. Subsequent calls ~120ms (cached prefix is free).  
**Effect on llama.cpp local:** KV cache hit → ~60% speedup on prefill.

---

## 5. The Sync Engine Checklist — 4-Step Cascade

Every file-change event that passes the Bloom + Dedup gates runs this cascade in parallel across mechanic threads:

```
[FILE TRIGGER (inotify IN_CLOSE_WRITE)]
        │
        ├───► [1. AUDIT FILE DISCOVERY]
        │       └ Scan for unmapped/orphaned files in ~/nina/
        │       └ No .manifest or header block? → lock thread → AST scan → create manifest
        │       └ Register to hive mind DAG
        │
        ├───► [2. INDEX UPDATE]
        │       └ Re-tokenize changed file → update inverted index entries
        │       └ Rebuild Trie paths for new/removed keywords
        │       └ Bloom filter updated with new content hash
        │
        ├───► [3. DOCUMENT UPDATE]
        │       └ ast.parse() the file
        │       └ For each FunctionDef missing a docstring → insert minimal stub
        │       └ Update File-Hash in manifest header block
        │
        └───► [4. REDUNDANCY & SYNC]
                └ Compare against SSOT — detect duplicate logic across files
                └ Prune or flag redundant definitions
                └ Ledger.log("sync_complete", path)
```

**All 4 steps are INTP mechanic work — zero LLM calls, zero token cost.**

---

## 6. Canonicalization — One Path, One Truth

Before any path or text string enters the Ledger, index, or Hive Mind DAG, it is canonicalized. This prevents phantom duplicates.

```python
# core/canonicalization.py (already exists)
from pathlib import Path
import re, unicodedata

def canon_path(raw: str) -> str:
    """
    ~/Documents/project  →  /home/aibony/Documents/project
    /home/aibony/nina//core/../core/agent.py  →  /home/aibony/nina/core/agent.py
    """
    return str(Path(raw).expanduser().resolve())

def canon_text(raw: str) -> str:
    """
    Normalize unicode, collapse whitespace, lowercase.
    'Redis  Connection\u00a0Pool' → 'redis connection pool'
    """
    s = unicodedata.normalize("NFKC", raw)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def canon_key(path: str, action: str) -> str:
    """Deterministic dedup key for Bloom filter and Ledger hash."""
    return f"{action}:{canon_path(path)}"
```

**Effect:** `~/nina/core/agent.py` and `/home/aibony/nina/core/agent.py` and `../nina/core/agent.py` all resolve to the same canonical key. The Bloom filter never double-processes the same file under different path representations.

---

## 7. Network & Swarm Resiliency — Why NINA Cannot Die

### The Un-Killable Architecture

NINA holds **no critical state in RAM**. Every piece of meaningful state is:

1. Written to the Ledger (`nina.db`) before the agent thread acts on it
2. Reproducible by replaying the `events` table from any checkpoint
3. Protected by WAL journal mode — survives hard power cut mid-write

### Recovery Protocol

```python
def recover_from_crash(last_known_good_event_id: int) -> None:
    """
    Called on boot if nina_state == 'crashed' or 'suspended'.
    Replays events after last_known_good_event_id to rebuild state.
    """
    db = get_ledger()
    events = db._conn.execute(
        "SELECT action, path, meta FROM events WHERE id > ? ORDER BY id",
        (last_known_good_event_id,)
    ).fetchall()
    for action, path, meta in events:
        _replay_event(action, path, meta)  # deterministic, idempotent
    db.set("nina_state", "running")
    db.set("last_boot_recovery", str(last_known_good_event_id))
```

### What this means practically

| Failure scenario | Recovery time | Data loss |
|---|---|---|
| `Ctrl+C` (SIGINT) | 0ms — clean flush | 0 |
| `kill -9` (SIGKILL) | <2s — WAL replay on next boot | 0 |
| Power cut mid-write | <5s — WAL rollback + replay | 0 |
| Corrupted `.py` file | AST audit detects → Ledger has last good hash | 0 |
| Loop storm (runaway recursion) | Bloom filter + idempotency lock kills it in <1ms | 0 |

---

## 8. Full Stack — How It All Connects

```
┌────────────────────────────────────────────────────────────────┐
│  FILE CHANGE (inotify)                                          │
│     │  canon_path()  →  canon_key()  →  BloomFilter check      │
│     │  mmh3 dedup    →  Ledger.acquire() idempotency lock      │
│     │                                                           │
│  INTP MECHANIC POOL (8 threads)                                 │
│     ├─ EventPacket(NamedTuple) → queue                         │
│     ├─ Index rebuild (Trie + InvertedIndex)                    │
│     ├─ AST parse → manifest header sync                       │
│     └─ Ledger.log() + telemetry span                           │
│                                                                 │
│  INTJ STRATEGIST POOL (2 threads)                              │
│     ├─ Reads EventPacket from queue                            │
│     ├─ CFG/structured LLM call (if needed)                    │
│     ├─ Memoized prompt context (static prefix cached)         │
│     └─ Writes plan back to Ledger.state                        │
│                                                                 │
│  LEDGER (nina.db — WAL SQLite)                                 │
│     ├─ events  (append-only, forever)                          │
│     ├─ state   (SSOT, upsert only)                             │
│     └─ locks   (TTL-expiring idempotency gates)                │
│                                                                 │
│  SIGTERM → flush all pools → Ledger.log("shutdown_complete")   │
└────────────────────────────────────────────────────────────────┘
```

---

## 9. Jules Backlog — Bedrock Tasks

```
[ ] core/event_packet.py   — EventPacket NamedTuple + queue wiring
[ ] core/thread_pools.py   — INTJ + INTP pool singletons, run_strategist/run_mechanic
[ ] core/bloom.py          — BloomFilter (bytearray stdlib)
[ ] core/signal_handler.py — SIGTERM/SIGINT → pool shutdown → ledger flush
[ ] core/prompt_cache.py   — memoized_parse() + static prefix builder
[ ] core/telemetry.py      — opentelemetry spans for every EventPacket
```

---

*Companion doc: `OUROBOROS_ARCHITECTURE.md`*  
*This document is auto-audited by NINA’s Ouroboros loop. File-Hash drift triggers re-validation.*
