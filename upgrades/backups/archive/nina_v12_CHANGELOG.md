# CHANGELOG

All notable changes to NINA are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [12.1.0] — 2026-05-20

### Added

- **Thermal guard — first-class preflight citizen** (`Stage 0`, `Stage 1`, `Stage 4`, `Stage 5`)
  Three-tier thermal protection added alongside the existing RAM and disk guards, reflecting the real risk of thermal throttling on an i5 8th Gen + MX150 under sustained LLM inference in Dhaka ambient temperatures.

  **Tiers:**
  - `warn` (CPU ≥80°C / GPU ≥80°C): log warning to nina.log, notify Telegram. No routing change.
  - `guard` (CPU ≥90°C / GPU ≥85°C): ban `LOCAL_HEAVY` for this invocation, force `LOCAL_FAST` + cloud only. Notify Telegram.
  - `critical` (CPU ≥95°C / GPU ≥90°C): abort agent loop entirely. Log to agent.log with tag `agent_loop_aborted_thermal`.

  Unavailable sensors return `None` and the corresponding tier is skipped silently — no false aborts.

- **`get_temps()` in SystemTool** (`Stage 4 — 4.6`)
  New async method: reads CPU temp via `psutil.sensors_temperatures()` (coretemp / k10temp / cpu_thermal) and GPU temp via `nvidia-smi --query-gpu=temperature.gpu`. `nvidia-smi` was already on the shell allowlist; no new security rules were required.

- **Thermal section in `get_status()`** (`Stage 4 — 4.6`)
  `/status` Telegram output now includes:
  `🌡️ Thermal  CPU: 72°C OK  GPU: 68°C OK`
  Status is `OK` below `thermal_warn_*` threshold, `WARN` at or above.

- **Thermal line in startup message** (`Stage 1 — 1.7`)
  Startup message now shows `Thermal: CPU {n}°C {status}  GPU {n}°C {status}` alongside RAM, VRAM, and disk.

- **`thermal_health` scheduler job** (`Stage 5 — 5.3`, `Stage 5 — 5.6`)
  10th core scheduler job, runs every 5 minutes. Calls `get_temps()`, logs and notifies if either sensor reaches warn level. No LLM call involved. Sensor unavailability is skipped silently.

- **6 thermal threshold fields in NinaConfig** (`Stage 1 — 1.3`)
  `thermal_warn_cpu`, `thermal_warn_gpu`, `thermal_guard_cpu`, `thermal_guard_gpu`, `thermal_critical_cpu`, `thermal_critical_gpu` — all with sensible defaults for MX150 hardware.

- **Thermal thresholds in `.env` template** (`Stage 1 — 1.4`)
  All 6 fields exposed in `.env` for easy tuning without code changes.

- **Thermal fields added to ConfigHotReload reloadable list** (`Stage 6 — 6.6`)
  All 6 thermal threshold fields are hot-reloadable; no restart required when adjusting thresholds.

### Changed

- **P5 design principle** updated: "thermal limits" added to the list alongside rate limits, RAM limits, disk limits, and time budgets.
- **Cross-cutting rules**: rules 22 and 23 added — thermal guard execution order and sensor-unavailability behavior.
- **Stage map**: Stage 1, 4, and 5 entries updated to reflect thermal additions. Scheduler count updated from 9 to 10 jobs.
- **Final Directive** extended with two new prohibitions:
  - Must not run LOCAL_HEAVY when CPU or GPU is at guard level or above.
  - Must not abort the agent loop for thermal reasons when sensors are unavailable.

---

## [12.0.0] — 2026-05-20

### Added

- **EWS failure handling in morning report** (`Stage 0`, `Stage 5`)
  The morning report now has a per-mailbox EWS error path matching the existing market-data error path. If EWS connection or fetch fails for either mailbox, the affected mailbox shows `"Unavailable (EWS unreachable — retry at next report)"` and the rest of the report renders normally. Failures logged to `error.log` with tag `morning_report_ews_fetch_failed`.

- **OPENAI added to provider registry** (`Stage 2 — 2.1`)
  OPENAI (`gpt-4o-mini`) was present in NinaConfig and RATE_LIMITS but absent from the Tier 2 provider registry table, making it unroutable. It is now a first-class Tier 2 provider entry. Sensitive tasks continue to route local-only; no exceptions.

- **OPENROUTER entry in RATE_LIMITS** (`Stage 0`)
  OPENROUTER is now explicitly listed in `RATE_LIMITS` (`rpm=20`, `min_spacing_s=3`). Dynamically registered sub-providers continue to use conservative defaults (`rpm=10`, `min_spacing_s=6`), now explicitly documented.

- **Agent loop global wall-clock timeout** (`Stage 0`, `Stage 1`, `Stage 5`)
  The agent loop previously had per-step budgets but no overall cap, enabling runaway tasks on hung providers. A new `agent_timeout_s` field (default `300`s) is added to `NinaConfig` and `.env`. On timeout, the partial result (if any) is returned with a notice; the event is logged to `agent.log` with tag `agent_loop_timeout`.

- **FastAPI rate limiting** (`Stage 0`, `Stage 1`, `Stage 7`)
  All FastAPI endpoints are now rate-limited to `api_rate_limit_rpm` requests per minute per source IP (default 60, configurable in `NinaConfig` and `.env`). Breaches return HTTP 429 with a `Retry-After` header and are logged to `security.log` with tag `api_rate_limit_breach`.

- **router.log JSON schema** (`Stage 0`, `Stage 7`)
  `router.log` is the primary cost and latency audit trail. A formal field schema is now defined: `ts`, `provider`, `task_type`, `input_tokens`, `output_tokens`, `cost_usd`, `ttft_ms`, `total_ms`, `parallel`, `cached`, `status`, `error`. All timestamps are ISO 8601 in UTC+6. Failure entries set `status="failure"` and zero out token/cost fields.

- **provider_hunter scheduled job** (`Stage 5 — 5.3`)
  `provider_hunter` is now the 9th core scheduler job, running daily at `02:00` Dhaka. Previously it was NLP-triggered only with no defined frequency. NLP trigger ("hunt for new providers") remains available for on-demand runs.

- **ConfigHotReload specification** (`Stage 6 — 6.6`)
  Previously listed in the stage map but unspecified. Now defined: watches `.env` every 60 seconds, lists reloadable vs non-reloadable fields, logs changed fields on success, falls back to old config on validation failure, notifies Telegram on either outcome. NLP-triggered: "reload config".

- **ABShadowTester specification** (`Stage 6 — 6.7`)
  Previously listed in the stage map but unspecified. Now defined: runs a candidate module alongside production for `shadow_n=20` live requests, computes match rate, and presents a summary before awaiting `/approve` or `/reject`. Opt-in; standard `/patch` flow does not require it.

- **CapabilityRegistry specification** (`Stage 6 — 6.8`)
  Previously listed in the stage map but unspecified. Now defined: JSON registry at `data/capabilities.json` tracking loaded/healthy state per tool. Updated on startup and after every tool health probe. Agent loop skips unhealthy tools and logs a warning rather than crashing. NLP-triggered: "show tool status".

- **NLP classification failure logging** (`Stage 3 — 3.3`, `Stage 0`)
  Classification failures were silently falling through to `general_task` with no log entry. Now a `WARNING` is written to `nina.log` with tag `nlp_classification_failed` and the first 80 characters of the input, enabling post-hoc diagnosis.

- **`session_max_turns` configurable** (`Stage 1`, `Stage 3`)
  Previously hardcoded as `20` in Stage 3. Now a `NinaConfig` field (`session_max_turns: int = 20`) and `.env` entry (`SESSION_MAX_TURNS=20`), allowing runtime adjustment without code changes.

- **Cache cleared on /reset** (`Stage 3 — 3.7`)
  `/reset` now calls `router.cache.clear()` in addition to wiping memory. The confirmation message is updated accordingly.

- **Cost tracker persistence** (`Stage 2 — 2.9`)
  Cost tracker state is now explicitly specified to persist to `data/jobs.sqlite` on each write, so daily totals survive unexpected restarts.

- **Idle definition clarified** (`Stage 2 — 2.7`)
  "Idle" is now formally defined: no user message received for `idle_threshold_min` minutes.

- **Startup message GPU format clarified** (`Stage 1 — 1.7`)
  `{fast_layers}/{heavy_layers}` was ambiguous (looked like a fraction). Changed to `fast={fast_layers} heavy={heavy_layers}` to make intent clear.

### Changed

- **Cross-cutting rule #9** (`Stage 0`)
  Browser automation flag list updated to include `--disable-dev-shm-usage`, which was present in Stage 4 (`4.4`) but missing from the design-level rule. Rule now reads:
  `browser automation always uses --disable-gpu --no-sandbox --disable-dev-shm-usage`

- **NINA version bump**: `11.0.0` → `12.0.0` in all headers.

- **Final Directive** (`Stage 7 — 7.4`) extended with two new prohibitions:
  - Must not block the morning report because an EWS mailbox fetch failed.
  - Must not run an agent loop indefinitely when providers are hung.
  - Must not route through OPENAI unless the key is present and the task is non-sensitive.

### Fixed

- **Stage map provider count**: updated from "16+ providers" to "17 providers + OPENROUTER" to reflect OPENAI addition and explicit OPENROUTER entry.
- **Stage map scheduler count**: updated from "8 jobs" to "9 jobs" to reflect `provider_hunter` addition.
- **security.log description** (`Stage 7 — 7.1`): updated to include "API rate-limit breaches" alongside unauthorized access and flood events.

---

## [11.0.0] — 2026-05-20

### Added
- Normalized routing score formula (clamped latency term; prevents unbounded scores).
- Full rate-limit table covering all 16+ registered providers (9 previously missing).
- Morning report market-data error path (`"Unavailable (retry at next report)"`).
- Per-task-type step budgets (`STEP_BUDGETS` dict + `DEFAULT_MAX_STEPS` fallback).
- Upgrade pipeline dangerous-pattern blocklist (14 patterns; defined at spec level).
- Authorized-user flood protection (`flood_window_s`, `flood_max_messages`).
- Disk preflight guard for write-heavy operations.
- FastAPI auth token generation guidance.

### Fixed
- Agent loop single `MAX_STEPS` constant replaced with per-task-type budgets.
- Shell allowlist: `journalctl` unit-locked to nina; `nvidia-smi`, `ollama ps`, `ollama list` added.

---

## [10.0.0] — prior

### Added
- RAM preflight guard and lean-mode fallback.
- Parallel reservation (reserve slots before `asyncio.gather()`).
- Guaranteed memory backup on `/reset`.
- Defined schedule resolution order.
- Idle proposal persistence (`expired_pending_review` → `idle_queue.json`).
- Provider min-spacing enforcement.
- Heartbeat dead-man escalation.
