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

## Dashboard Endpoints
- **Metrics JSON:** `GET /health` (standard health metrics)
- **Live Visual UI:** `GET /dashboard` (renders `dashboard/ninaui.html`)

## [NEW] Live Visual Telemetry (v2.0)
The visual dashboard provides a real-time Pulse of NINA's infrastructure. It is designed to provide empirical proof of local execution by visualizing:
- **Resource "Bumps":** Real-time CPU/RAM spikes corresponding to local NinaFlash/Ollama activity.
- **Routing Efficiency:** A live graph of Local vs. Cloud request ratios.
- **Parallelism Indicator:** A gauge showing the number of concurrent `AgentLoop` tool tasks in flight.

## [NEW] Parallel Tool Monitoring
With the introduction of the **Parallel Tool Hub**, NINA now tracks:
- **`parallel_tool_executions`:** Count of tool calls executed concurrently via `asyncio.gather`.
- **`overlap_latency_savings`:** Estimated time saved by running tools in parallel vs. sequential execution.
- **`scout_success_rate`:** Success rate of speculative "Scout" patterns.

## Wiring
The observability core is deeply integrated into various parts of NINA to update the central metrics cache.
- `healthcheck.py`: Calls `get_hub().set_health_ts()` at the end of the health checks (via `get_prometheus_metrics` / `Final report`).
- `tools/nina_sync.py`: Calls `get_hub().set_sync_ts()` exactly after performing a push and logging the push event.
- `tools/nina_dashboard.py`: Exposes `get_hub().to_dict()` natively at `/health`.

## [NEW] Local Performance Monitoring
While the `ObservabilityHub` tracks high-level system state, `ninaflash` provides surgical performance monitoring:
- **Command:** `nf monitor`
- **Function:** Parses the last 200 requests from `ninagate.log` to calculate local/cloud ratios, average latencies per tier, and estimated tokens saved via local execution and caching.
