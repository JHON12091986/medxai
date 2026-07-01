# NINA Observability & Telemetry

> **Status:** Telemetry Pass-2 COMPLETE — 2026-06-25  
> All three pipeline layers (NinaGate → Ouroboros → providers) are fully instrumented.

---

## Architecture Overview

```
opencode / user shell
       │
       ▼  HTTP
  NinaGate (ninagate/main.py)
       │  emit("ninagate", "request_in")   ← span_id generated here
       │  emit("ninagate", "response_out")
       │  emit("ninagate", "error")
       ▼
  Ouroboros Router (core/router.py)
       │  emit("ouroboros", "route_start")       ← span_id propagated
       │  emit("ouroboros", "provider_call_ok")
       │  emit("ouroboros", "provider_error")
       │  emit("ouroboros", "provider_stream_error")
       │  emit("ouroboros", "route_ok")
       │  emit("ouroboros", "route_ok_stream")
       │  emit("ouroboros", "route_stream_error")
       │  emit("ouroboros", "route_exhausted")
       ▼
  Ollama / Cloud Providers
       │
       ▼
  telemetry.jsonl  ←── atomic append, 10 MB rotation, thread-safe
       │
       ▼  (parallel, non-blocking)
  NinaTracer (OTel → Jaeger, null-fallback if SDK absent)
```

---

## Telemetry Package (`telemetry/`)

### `telemetry/emitter.py` — Core JSONL Sink

Atomic, thread-safe writer to `telemetry.jsonl`. Never raises — all I/O errors are swallowed to stderr.

```python
emit(stage: str, event: str, payload: dict, span_id: str | None = None)
```

**Schema per event line:**
```json
{
  "ts": 1750000000.0,
  "span_id": "a3f1c9b2",
  "stage": "ouroboros",
  "event": "route_ok",
  "payload": {
    "provider": "GROQ",
    "task_type": "coding",
    "latency_ms": 412.3,
    "tokens_in": 180,
    "tokens_out": 340,
    "circuit_state": "CLOSED"
  }
}
```

**Rotation:** `telemetry.jsonl` is renamed to `telemetry.jsonl.1` when it exceeds 10 MB.

### `telemetry/__init__.py` — Unified Export

```python
from telemetry import Tracker, emit
```

Both `Tracker` (OTel shim) and `emit` (JSONL) are available from one import.

### `telemetry/reader.py` — CLI Tail

```bash
# Tail last 20 events
python -m telemetry.reader --tail 20

# Filter by stage
python -m telemetry.reader --stage ouroboros --tail 50

# Filter by event type
python -m telemetry.reader --event route_exhausted

# Follow live (like tail -f)
python -m telemetry.reader --follow

# Raw JSON output
python -m telemetry.reader --json --tail 10
```

---

## Event Reference

### NinaGate Events (`stage: "ninagate"`)

| Event | When | Key payload fields |
|---|---|---|
| `request_in` | Every proxy request entry | `provider`, `model`, `token_est`, `user_id`, `span_id` |
| `response_out` | Successful response | `latency_ms`, `status`, `tokens_used` |
| `error` | Exception in handler | `exc_type`, `msg` |

### Ouroboros Events (`stage: "ouroboros"`)

| Event | When | Key payload fields |
|---|---|---|
| `route_start` | `route()` entry | `task_type`, `estimated_tokens`, `stream`, `force_local` |
| `route_ok` | Non-stream success | `provider`, `task_type`, `fallback_attempt`, `latency_ms`, `tokens_in`, `tokens_out`, `circuit_state` |
| `route_ok_stream` | Stream success | `provider`, `task_type`, `latency_ms`, `tokens_est`, `circuit_state` |
| `route_exhausted` | All providers failed | `task_type` |
| `route_stream_error` | Stream generator exception | `provider`, `task_type`, `exc_type`, `msg` |
| `provider_call_ok` | `_call_provider()` success | `provider`, `task_type`, `latency_ms`, `local`, `tokens_in`, `tokens_out`, `circuit_state` |
| `provider_error` | `_call_provider()` exception | `provider`, `task_type`, `exc_type`, `msg`, `circuit_state` |
| `provider_stream_error` | `_call_provider_stream()` exception | `provider`, `task_type`, `exc_type`, `msg`, `circuit_state` |

---

## Span ID Propagation

A `span_id` (8-char UUID prefix) is generated at **NinaGate request entry** and propagated:

```
NinaGate: span_id = uuid4()[:8]  →  passed in request context dict
Outoboros route():   _span_id received / or generates own if called standalone
_call_provider():    span_id available via route() closure
```

This allows correlating a single user request across all three layers in `telemetry.jsonl`.

---

## Dual-Emit Pattern

`core/router.py` runs **both** sinks in parallel — no existing `write_log` calls were removed:

```python
# Legacy structured log (logs/router.log) — unchanged
write_log({"event": "route_ok", "span_id": _span_id, ...})

# Telemetry pass-2: dual-emit to telemetry.jsonl
_telem_emit("ouroboros", "route_ok", {
    "provider": pid,
    "task_type": task.task_type,
    "latency_ms": round(lat, 1),
    "circuit_state": self.health[pid].cb.state,
}, span_id=_span_id)
```

The `_telem_emit` import block in `core/router.py` is null-safe:
```python
try:
    from telemetry.emitter import emit as _telem_emit
except ImportError:
    def _telem_emit(stage, event, payload, span_id=None): pass
```

---

## OTel / Jaeger (Optional)

`telemetry/tracker.py` wraps `core/otel_tracer.py::NinaTracer`. If the OTel SDK or Jaeger is unavailable, the null-object fallback activates automatically — the JSONL emitter continues running independently.

To enable Jaeger export, set `OTEL_EXPORTER_JAEGER_ENDPOINT` in the environment.

---

## Log Files

| File | Written by | Format | Rotation |
|---|---|---|---|
| `telemetry.jsonl` | `telemetry/emitter.py` | JSONL | 10 MB → `.jsonl.1` |
| `logs/router.log` | `core/router.py::write_log` | JSONL | 100 KB → keep last 100 lines |

---

## Telemetry Pass History

| Pass | Date | Scope |
|---|---|---|
| Pass-1 | 2026-06-24 | `write_log` stubs in `core/router.py` (`route_start`, `route_ok`, `route_ok_stream`, `route_exhausted`, `provider_call_ok`) |
| Pass-2 | 2026-06-25 | `telemetry/emitter.py` + `telemetry/reader.py` created; `_telem_emit` dual-emit wired into all router paths; NinaGate `request_in` / `response_out` / `error` wired |
