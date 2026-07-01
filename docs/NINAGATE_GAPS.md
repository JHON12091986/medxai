# NinaGate Gap Register

This document tracks all identified architectural gaps in the ninagate pipeline,
their status, and the fix applied. It is visible to all agents.

---

## GAP-01 — Orphaned `_circuit_breaker` Instance

**Status:** FIXED (2026-06-25, phase-1)

**Problem:**
`ninagate/main.py` imported and instantiated `_circuit_breaker = CircuitBreaker()`
from `ninagate/circuit_breaker.py` but never called `.record()` or `.is_open()` on it.
The file-backed EMA health scores were never updated.

**Fix:**
- `forward_to_provider()` now calls `_circuit_breaker.record(provider_name, success, latency_ms)`
  after every provider attempt.
- `/v1/health/providers` endpoint added — exposes `_circuit_breaker.health_report()` to agents.
- `circuit_breaker.py` updated to track `avg_latency_ms` via EMA (90/10 weight).

---

## GAP-02 — Incorrect Latency Recording in `ProviderHealth`

**Status:** FIXED (2026-06-25, phase-1)

**Problem:**
`ProviderHealth.record_success()` appended `time.time()` (Unix epoch) into
`self.latencies` instead of elapsed milliseconds. `avg_latency()` therefore
returned meaningless values (~1.75 trillion ms), corrupting provider scoring.

**Fix:**
Latency is now recorded in `forward_to_provider()` at the call site:
`h.latencies.append((time.time() - start_time) * 1000)`
before calling `h.record_success()`. `record_success()` no longer touches latencies.

---

## GAP-03 — No Agent-Visible Provider Health Endpoint

**Status:** FIXED (2026-06-25, phase-1)

**Problem:**
No endpoint existed for agents (Jules, opencode, monitoring tools) to query
which providers are currently healthy, open, or degraded.

**Fix:**
`GET /v1/health/providers` added. Returns:
```json
{
  "GEMINI": { "score": 0.97, "open": false, "fail_streak": 0, "avg_latency_ms": 210.3, ... },
  "GROQ":   { "score": 0.85, "open": false, "fail_streak": 1, "avg_latency_ms": 95.1,  ... }
}
```

---

## GAP-04 — `span_id` Lost at `forward_to_provider()` Boundary

**Status:** FIXED (2026-06-25, phase-1)

**Problem:**
`_span_id` was generated at `proxy_chat_completions` entry and used for
`request_in` / `cache_hit` / `response_out` telemetry — but was NOT passed
into `forward_to_provider()`. Any failure inside that function was untraced.

**Fix:**
`forward_to_provider()` now accepts `span_id: str = ""` and emits
`_telem_emit("ninagate", "provider_attempt", {...}, span_id=span_id)`
on every attempt and `"provider_failure"` on every failure.

---

## GAP-05 — `AGENTS.md` Broken Symlink (Blocks Jules Clones)

**Status:** OPEN — requires manual fix on local machine

**Problem:**
`AGENTS.md` is tracked as a Git symlink (`mode 120000`) with a target path
that exceeds the filesystem symlink length limit in Jules's container.
This causes `fatal: unable to create symlink AGENTS.md: File name too long`
on every Jules clone attempt.

**Fix required:**
```bash
# On local machine in ~/nina:
git rm AGENTS.md
cp --dereference <symlink-target> AGENTS.md
git add AGENTS.md
git commit -m "fix: convert AGENTS.md symlink to real file (fixes Jules clone)"
git push
```

---

## GAP-06 — `ninagate/README.md` Stale / Missing Pipeline Docs

**Status:** FIXED (2026-06-25, phase-1)

**Problem:**
Old README did not document sessions, telemetry events, circuit breaker states,
provider tier boost logic, or the Delta Sync Protocol contract.

**Fix:**
Full README rewrite with routing flowchart, all endpoints, session TTLs,
telemetry events, CB states, and delta sync instructions.

---

## GAP-07 — `ProviderHealth.record_success()` Signature Mismatch

**Status:** FIXED (2026-06-25, phase-1)

**Problem:**
`stream_response()` called `h.record_success()` with no latency argument,
but latency was appended manually after: `h.latencies.append((time.time() - start_time) * 1000)`.
This was redundant with GAP-02 and caused double-appends on streaming paths.

**Fix:**
Latency append removed from `record_success()` body. All latency recording
is now done explicitly at call sites before `record_success()` is called.

---

## Known Remaining Items (Phase 2)

- [ ] **GAP-05** — AGENTS.md symlink fix (requires local git action by M. Baizid)
- [ ] **MEGA-09** — agent/ vs agents/ namespace merge (blocked on Jules clone fix)
- [ ] `forward_to_provider` retry logic: 5xx retry sleeps 1s blocking the event loop — should use `asyncio.sleep` (it already does — confirmed OK)
- [ ] `/v1/ws/telemetry` WebSocket: `nvidia-smi` subprocess spawned every 500ms — should cache with TTL (already cached at 2s — confirmed OK)
- [ ] `QuotaManager.increment()` calls `run_in_executor` with `asyncio.get_event_loop()` — deprecated in Python 3.10+; should use `asyncio.get_running_loop()`
