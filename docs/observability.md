# NINA Observability Layer

## Overview
The NINA Observability Layer provides a single, structured source of truth for the system's health, metrics, and telemetry. It relies on a lazy singleton, `ObservabilityHub`, to centrally aggregate operation and performance metrics, allowing components to emit consistent and standardized JSON logs.

## Metrics Reference

| field                | type      | description                                        |
| -------------------- | --------- | -------------------------------------------------- |
| uptime_seconds       | float     | Uptime in seconds since hub initialization         |
| tasks_total          | int       | Total number of tasks processed                    |
| tasks_ok             | int       | Total number of successfully completed tasks       |
| tasks_fail           | int       | Total number of failed tasks                       |
| router_calls         | int       | Total number of router calls made                  |
| last_sync_ts         | str       | ISO8601 timestamp of the last successful sync      |
| last_health_check_ts | str       | ISO8601 timestamp of the last health check run     |
| active_providers     | list[str] | List of active AI provider names                   |
| error_rate           | float     | Error rate calculated as (tasks_fail/tasks_total)  |
| memory_mb            | float     | Memory usage footprint mapped into megabytes       |

## Health Status
The health status represents the overall readiness and stability of NINA based on operational metrics.
- **HEALTHY:** NINA is operating correctly. (error_rate <= 0.2)
- **DEGRADED:** NINA is experiencing a high rate of errors. (0.2 < error_rate <= 0.5)
- **CRITICAL:** NINA has encountered severe failures and requires immediate attention. (error_rate > 0.5)

## Dashboard Endpoint
A new endpoint is exposed on the dashboard to easily observe NINA's metrics on demand.
**Endpoint:** `GET /health`

**Example JSON Response:**
```json
{
  "uptime_seconds": 120.5,
  "tasks_total": 10,
  "tasks_ok": 9,
  "tasks_fail": 1,
  "router_calls": 5,
  "last_sync_ts": "2023-10-24T12:00:00Z",
  "last_health_check_ts": "2023-10-24T12:05:00Z",
  "active_providers": ["Ollama", "OpenAI"],
  "error_rate": 0.1,
  "memory_mb": 150.0,
  "status": "HEALTHY"
}
```

## Wiring
The observability core is deeply integrated into various parts of NINA to update the central metrics cache.
- `healthcheck.py`: Calls `get_hub().set_health_ts()` at the end of the health checks (via `get_prometheus_metrics` / `Final report`).
- `tools/nina_sync.py`: Calls `get_hub().set_sync_ts()` exactly after performing a push and logging the push event.
- `tools/nina_dashboard.py`: Exposes `get_hub().to_dict()` natively at `/health`.
