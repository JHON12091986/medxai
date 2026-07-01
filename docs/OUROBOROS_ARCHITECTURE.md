# Ouroboros Architecture

> **Version:** Pass-2 telemetry complete — 2026-06-25

Ouroboros is the NINA routing brain: it receives every inference request from NinaGate, selects the optimal provider, manages circuit breakers, implements Mixture-of-Agents (MoA), and streams responses back.

---

## Request Flow

```
NinaGate (proxy)
    │  span_id propagated in context
    ▼
HybridRouter.route(goal, messages, task)
    │
    ├── HyperDrive cache check (memo_cache)
    ├── LPU fast-track (lpu_deterministic)
    ├── CRITICAL override → GEMINI_FLASH_PROD
    ├── ResponseCache check
    ├── MoA fast-path (research / analysis / coding)
    ├── Thermal safeguard (is_thermal_safe)
    └── Tier-aware provider selection
            │
            ├── QuotaRouter.get_sorted_providers()
            ├── SmartRouter.get_best_provider()
            └── _call_provider() / _call_provider_stream()
                    │
                    └── Ollama (local) or Cloud (httpx)
```

---

## Key Classes

### `HybridRouter`
Main entry point. Owns `health: Dict[str, ProviderHealth]`, `cache: ResponseCache`, `cost: CostTracker`, `quota_router`, `rpm_scheduler`, `smart_router`.

**Methods:**
- `route()` — primary non-stream + stream routing, OODA validation loop
- `moa_route()` — Mixture-of-Agents parallel proposer + aggregator
- `_call_provider()` — single provider HTTP call (non-stream)
- `_call_provider_stream()` — single provider SSE stream
- `parallel_route()` — RAM-guarded parallel multi-prompt dispatch
- `graceful_fallback_chain()` — local-first exhaustive fallback
- `_idle_monitor()` — 60s background: cache purge, circuit state save, quality probes

### `CircuitBreaker`
Per-provider state machine: `CLOSED → OPEN → HALF_OPEN → CLOSED`.
- Threshold: 3 failures in 120s window
- Recovery: 60s default, 300s on 429
- State persisted to `data/circuit_state.json` across restarts

### `ProviderHealth`
Per-provider metrics: success/failure counts, latency deque (max 20), daily request/token counters, health score (0–1).

### `ResponseCache`
MD5-keyed in-memory cache with TTL per task type. Saved/loaded from `data/router_cache.json`.

### `CostTracker`
Estimates cost at $0.0000002 per token, writes to `logs/router.log` via `write_log()`.

---

## Provider Tiers

| Tier | Providers | Use case |
|---|---|---|
| 1 | Premium cloud (Gemini Pro, GPT-4 class) | Deep reasoning, critical tasks |
| 2 | Mid-tier cloud (Groq, Gemini Flash, Chutes) | Balanced quality/speed |
| 3 | Free/experimental | Fallback, research tasks |
| Local | LOCALFAST, LOCALHEAVY (Ollama/dulal) | Thermal-safe, offline, deterministic |

Provider list loaded from `ninagate/providers.json` at startup.

---

## Mixture-of-Agents (MoA)

Activated for `task_type in {"research", "analysis", "coding"}` (non-streaming only).

1. Fire prompt to `_MOA_PROPOSERS = ["POLLINATIONS", "GROQ", "CHUTES"]` in parallel
2. Collect successful proposals (need ≥ 2)
3. Route to aggregator: `GEMINI → GEMINI_FLASH → GEMINI_FLASH_PROD → GROQ → LOCALFAST`
4. Aggregator synthesises best answer
5. Falls back to `route()` on any failure

---

## OODA Validation Loop

`_validate_response()` runs for `coding`, `research`, `diagnostic` tasks:
- Sends response to GROQ (or LOCALFAST) as a logic gate validator
- Validator checks technical soundness + evidence citation
- Returns `VALID` or a one-sentence failure reason
- On failure: appends retry message to conversation, tries next provider

---

## Telemetry (Pass-2 Complete)

All routing events dual-emit to both `logs/router.log` (legacy `write_log`) and `telemetry.jsonl` (structured `_telem_emit`). The `_telem_emit` import is null-safe — missing `telemetry` package never crashes routing.

### Events emitted by `core/router.py`

| Event | Source | span_id |
|---|---|---|
| `route_start` | `route()` entry | ✅ generated |
| `route_ok` | Non-stream success (all paths) | ✅ propagated |
| `route_ok_stream` | Stream generator completion | ✅ propagated |
| `route_exhausted` | All providers failed | ✅ propagated |
| `route_stream_error` | Stream generator exception | ✅ propagated |
| `provider_call_ok` | `_call_provider()` local + cloud | — |
| `provider_error` | `_call_provider()` exception | — |
| `provider_stream_error` | `_call_provider_stream()` exception | — |

See `docs/observability.md` for full event schema and CLI tail usage.

---

## Configuration

All tunable values in `core/config.py` (`NinaConfig`):
- `ollama_host` — local inference endpoint
- `ram_guard_gb` — parallel_route RAM floor (default 10.5 GB)
- Provider API keys via `key_field` → `NinaConfig` attribute lookup

---

## Files

| File | Role |
|---|---|
| `core/router.py` | Full implementation (HybridRouter + CircuitBreaker + all support classes) |
| `core/quota_router.py` | Daily quota + force-local logic |
| `core/rpm_scheduler.py` | Per-provider RPM throttle |
| `core/smart_router.py` | Learned provider ranking |
| `core/hyperdrive_policy.py` | Fast-path cache policy |
| `core/memo_cache.py` | Semantic + exact response cache |
| `ninagate/providers.json` | Provider registry |
| `data/circuit_state.json` | Persisted circuit breaker state |
| `data/router_cache.json` | Persisted response cache |
| `logs/router.log` | Legacy structured log |
| `telemetry.jsonl` | Structured pipeline telemetry |
