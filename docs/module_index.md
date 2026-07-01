# NINA Module Index

> Last updated: 2026-06-25 (telemetry pass-2 complete)

## Core

| Module | Path | Purpose |
|---|---|---|
| Config | `core/config.py` | `NinaConfig` dataclass — all env/runtime config |
| Logger | `core/logger.py` | Structured logger (`get_logger`) |
| Router | `core/router.py` | `HybridRouter` — tier-aware multi-provider routing, MoA, streaming, circuit breakers. **Telemetry pass-2 wired.** |
| Task Classifier | `core/task_classifier.py` | `ClassifiedTask` — prompt → task type + token estimate |
| Quota Router | `core/quota_router.py` | Daily quota tracking, force-local logic |
| RPM Scheduler | `core/rpm_scheduler.py` | Per-provider rate-limit throttle |
| Smart Router | `core/smart_router.py` | Learned provider ranking by task type |
| Hyperdrive Policy | `core/hyperdrive_policy.py` | Fast-path caching policy |
| Memo Cache | `core/memo_cache.py` | Semantic + exact response cache |
| OTel Tracer | `core/otel_tracer.py` | `NinaTracer` — OpenTelemetry span wrapper |

## Telemetry

| Module | Path | Purpose |
|---|---|---|
| Emitter | `telemetry/emitter.py` | Atomic JSONL writer to `telemetry.jsonl` — 10 MB rotation, thread-safe, pipeline-safe (never raises) |
| Tracker | `telemetry/tracker.py` | OTel shim re-exporting `NinaTracer` with null-object fallback |
| Reader | `telemetry/reader.py` | CLI tail: `python -m telemetry.reader --tail 20 --stage ouroboros --follow` |
| Init | `telemetry/__init__.py` | Exports `Tracker` + `emit` — single import for all consumers |

## NinaGate

| Module | Path | Purpose |
|---|---|---|
| Main | `ninagate/main.py` | FastAPI proxy — opencode → Ouroboros bridge. **Telemetry pass-4 wired** (`request_in`, `response_out`, `error`). |
| Circuit Breaker | `ninagate/circuit_breaker.py` | Gateway-level circuit breaker (separate from router CB) |
| Providers | `ninagate/providers.json` | Provider registry (name, base_url, model, tier, api_key_env) |

## Tools

| Module | Path | Purpose |
|---|---|---|
| Jules | `tools/jules.py` | Telegram notification + Jules task dispatch |
| Provider Health | `tools/provider_health.py` | External health probe tracker |
| Model Discovery | `tools/model_discovery.py` | Dynamic model capability detection |
| System | `tools/system.py` | `is_thermal_safe()` — CPU/GPU temp guard |

## Telemetry Event Map

```
stage="ninagate"  events: request_in, response_out, error
stage="ouroboros" events: route_start, route_ok, route_ok_stream,
                          route_exhausted, route_stream_error,
                          provider_call_ok, provider_error,
                          provider_stream_error
```

All events land in `telemetry.jsonl`. See `docs/observability.md` for full schema.
