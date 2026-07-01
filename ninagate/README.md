# NinaGate

**NinaGate** is NINA's OpenAI-compatible HTTP gateway, running independently at `:8080`.
It is the **single entry point** for all AI clients (opencode, curl, agents) and routes
requests to cloud + local providers via a scored fallback chain.

---

## Architecture Position

```
opencode / curl / any OpenAI client
         │
         ▼  POST /v1/chat/completions  (OpenAI-compatible)
  ninagate :8080   [ninagate.service — survives nina crashes]
         │
         ├─ ResponseCache (SHA256, TTL-by-task-type)
         ├─ QuotaManager  (Gemini daily soft-limit, resets 7AM UTC)
         ├─ classify_task()  →  SIMPLE / MEDIUM / COMPLEX / MASSIVE
         ├─ ProviderHealth  →  score() + CircuitBreaker (per-provider)
         ├─ _circuit_breaker  →  global EMA health file (router_health.json)
         │
         ▼  forward_to_provider()
         ├─► SIMPLE/force_local  →  LOCAL (Ollama dulal)
         ├─► MEDIUM             →  LOCAL first, cloud fallback
         └─► COMPLEX/MASSIVE    →  cloud first, LOCAL fallback
```

**Process independence:** `ninagate.service` deliberately does NOT depend on
`nina.service` (`After=` omitted). ninagate survives NINA core crashes.

**Code dependency:** ninagate imports `core.config` and `core.task_classifier` only.
All routing logic (CircuitBreaker, ProviderHealth, QuotaManager, ResponseCache) is
self-contained inside `ninagate/main.py`.

---

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/v1/chat/completions` | POST | Main proxy. OpenAI-compatible. |
| `/genai/v1/chat/completions` | POST | Alias for genai clients. |
| `/v1/responses` | POST | Stateful Responses API shim (multi-turn sessions). |
| `/v1/models` | GET | Lists all configured providers as model IDs. |
| `/v1/status` | GET | Per-provider health: CB state, latency, key status. |
| `/v1/health/providers` | GET | EMA scores from global circuit breaker file. |
| `/v1/sessions` | GET | Lists all active response sessions. |
| `/v1/sessions/{id}` | GET | Debug a specific session (TTL, turn count). |
| `/health` | GET | Service liveness + local Ollama status. |
| `/v1/ws/telemetry` | WS | Real-time CPU/GPU/router event stream. |

---

## Routing Logic

### Task Classification → Tier

| Task Type | Primary Route | Fallback |
|---|---|---|
| SIMPLE | LOCAL (dulal) | cloud |
| MEDIUM | LOCAL first | cloud |
| COMPLEX | cloud first | LOCAL |
| MASSIVE | cloud only | LOCAL emergency |
| force_local (quota exceeded) | LOCAL | cloud |

### Provider Selection

Providers are scored: `score = (success_rate × 0.5) + (latency_score × 0.5) - penalty`

Tier boost applied if `recommended_tier` matches provider class:
- `LOCAL` boost → OLLAMA / DULAL
- `FAST` boost → CEREBRAS / GROQ
- `DEEP` boost → DEEPSEEK / MISTRAL
- `LARGE` boost → GEMINI

### Circuit Breaker States

| State | Meaning | Behaviour |
|---|---|---|
| CLOSED | Healthy | All requests pass |
| HALF_OPEN | Recovering | One probe request allowed |
| OPEN | Failed | Requests blocked until `open_until` |

A `429` response forces **300s hard cooldown** immediately.

---

## Session Store (`/v1/responses`)

Multi-turn conversations are persisted in `data/ninagate_sessions.json`.

| Task Type | Session TTL |
|---|---|
| SIMPLE | 30 min |
| MEDIUM | 2 hours |
| COMPLEX | 12 hours |
| MASSIVE | 12 hours |

Max 500 sessions; oldest 100 evicted when limit reached.

---

## Telemetry

All events are emitted to `telemetry/emitter.py` under stage `"ninagate"`:

| Event | Trigger |
|---|---|
| `request_in` | Every request entry |
| `cache_hit` | Cache served |
| `response_out` | Successful provider response |
| `error` | 503 / all providers exhausted |

Each event carries a `span_id` (8-char UUID prefix) for end-to-end tracing
across ninagate → core/router pipeline.

---

## Global Circuit Breaker (`circuit_breaker.py`)

The file-backed `CircuitBreaker` (`data/router_health.json`) persists EMA scores
across restarts. It is recorded after every `forward_to_provider()` call and
exposed via `/v1/health/providers`.

**Agents and monitoring tools should poll `/v1/health/providers`** to understand
current provider availability without reading internal state.

---

## Configuration

- Providers: `ninagate/providers.json` (hot-reloaded via watchfiles)
- Environment keys: `.env` / `.env.local` at repo root
- Quota soft-limit: `config.quota_soft_limit` (default 900 req/day for Gemini)
- Local Ollama health TTL: 300s (probed at startup + on every SIMPLE/MEDIUM route)

---

## Service Management

```bash
systemctl --user status ninagate.service
systemctl --user restart ninagate.service
journalctl --user -u ninagate.service -f
tail -f ~/nina/logs/ninagate.log
```

---

## Delta Sync Protocol

ninagate intentionally duplicates some primitives from `core/` (CircuitBreaker,
ProviderHealth, cache key logic) to remain independent if `core/` breaks.

When `core/router.py` changes those primitives:
1. Read `docs/space/DELTA_SYNC_PROTOCOL.md`
2. Manually mirror the change into `ninagate/main.py`
3. Update the `Last delta sync:` comment at the top of `ninagate/main.py`
4. Update this README if behaviour changes

---

*Last updated: 2026-06-25 by Perplexity ARCHITECT OVERWATCH — gap-fill phase 1*
