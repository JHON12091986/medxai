# NINA Self-Patch Log

> **Rule:** Append only. Never delete. Never edit past entries.  
> **Format:** Each entry is sealed with a timestamp and commit SHA.  
> **Purpose:** Immutable audit trail of every autonomous or human-directed
> code modification to the NINA codebase.  
> **Updated by:** Auditor node (`swarm/auditor.py`) on every STATE 04
> self-patch, and by ARCHITECT OVERWATCH on directed changes.

---

## Log Format

```
### PATCH-{N} · {timestamp BDT} · {commit SHA short}
File:     {file patched}
Trigger:  {AUTONOMOUS | DIRECTED | BOOTSTRAP}
Agent:    {auditor | jules | architect_overwatch | human}
Reason:   {why this patch was made}
Method:   {AST_SURGERY | FULL_REWRITE | ADDITIVE | SCHEMA_MIGRATION}
Verified: {compile() PASS | N/A}
Rollback: {WAL entry ID or git SHA}
Result:   {what changed — one paragraph}
---
```

---

## Patch History

### PATCH-001 · 24 Jun 2026 · 01:25 BDT · add6943
File:     `core/kernel.py`  
Trigger:  DIRECTED  
Agent:    architect_overwatch (Perplexity)  
Reason:   Wire Ouroboros 5 subsystems into kernel boot sequence.
          Add BloomFilter dedup gate to STATE 01.
          Add ContextCompressor pipeline to STATE 02.  
Method:   FULL_REWRITE (Pass 3 — additive over Pass 2 kernel)  
Verified: compile() PASS (Python 3.14.4)  
Rollback: Previous version at git SHA `60d81ff`  
Result:   `boot_ouroboros()` function added to kernel module.
          STATE 01 now gates on `BloomFilter.might_contain()` before
          creating TaskPacket. STATE 02 compresses context via
          `context_compressor.compress_packet()`. All 5 Ouroboros
          subsystems (Canonicalizer, BloomFilter, InvertedIndex,
          ContextCompressor, ManifestWatcher) wired into single boot call.

---

### PATCH-002 · 24 Jun 2026 · 02:36 BDT · (this commit)
File:     `core/ledger.py`  
Trigger:  DIRECTED  
Agent:    architect_overwatch (Perplexity)  
Reason:   GAP-01 — Add temporal WAL queries (`valid_from`/`valid_to` columns).
          GAP-04 — Add `vacuum(days=30)` for SQLite retention pruning.
          GAP-07 — Add `wal_commit()` + `wal_log` table for
          `asyncio.to_thread()`-safe STATE 04 WAL commits.  
Method:   ADDITIVE (schema migration + new methods, zero breaking changes)  
Verified: compile() PASS — safe ALTER TABLE with try/except for existing cols  
Rollback: Previous version git SHA `c89af9ef`  
Result:   New methods: `log_temporal()`, `fetch_at()`, `expire_at()`,
          `vacuum()`, `wal_commit()`, `wal_recent()`. New table: `wal_log`.
          Backward-compatible: all existing call sites unchanged.
          `get_ledger()` singleton added.

---

### PATCH-003 · 24 Jun 2026 · 02:36 BDT · (this commit)
File:     `core/grammar_guard.py` (NEW FILE)  
Trigger:  DIRECTED  
Agent:    architect_overwatch (Perplexity)  
Reason:   GAP-03 — CFG constrained LLM output layer. Prevents unstructured
          output from propagating through STATE 03 into STATE 04 audit.
          Guards the boundary between raw LLM text and structured action.  
Method:   ADDITIVE (new file — no existing code modified)  
Verified: compile() PASS (Python 3.14.4)  
Rollback: N/A — new file, delete to revert  
Result:   `GrammarGuard` class with `constrain()`, `regex()`, `choice()`,
          `extract_json()` methods. Backend auto-detects at import:
          outlines → lm-format-enforcer → stdlib regex fallback.
          `get_guard()` process-wide singleton. Integration point
          documented in module docstring for kernel STATE 03.

---

## Autonomous Patch Template

> When `swarm/auditor.py` completes a self-patch cycle, it MUST append
> a new entry here via `ledger.log_temporal()` AND write a human-readable
> block in this file under the next PATCH-N number.

```python
# swarm/auditor.py — self-patch completion hook
from core.ledger import get_ledger
import json, time

def record_self_patch(
    patch_n: int,
    file_path: str,
    reason: str,
    method: str,
    verified: bool,
    wal_id: int,
    commit_sha: str = "",
) -> None:
    entry = {
        "patch_n":    patch_n,
        "file":       file_path,
        "trigger":    "AUTONOMOUS",
        "agent":      "auditor",
        "reason":     reason,
        "method":     method,
        "verified":   "compile() PASS" if verified else "REJECTED",
        "wal_id":     wal_id,
        "commit_sha": commit_sha,
        "ts":         time.time(),
    }
    get_ledger().log_temporal(
        "self_patch",
        file_path,
        meta=json.dumps(entry),
        valid_from=time.time(),
    )
```
