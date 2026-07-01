# NINA Changelog

---

## [15.4.0] — 2026-06-30

### Fixed
- **`core/router.py`** — Added explicit safeguarding for local Ollama providers returning `HTTP 400 Bad Request`. When Ollama throws a 400 (context size limit overrun or invalid parameters), the router now raises a `ValueError` to abort local retries immediately and trigger fallback, preventing connection hangs.
- **`crons/manager.py`** — Corrected import paths for `nina_ooda` and `nina_cicd` modules. Bare `import nina_ooda` fails because these live in the `tools` package directory. Fixed to `from tools import nina_ooda` and `from tools import nina_cicd`, resolving errors blocking self-healing.
- **`tools/jules.py`** — Replaced generic `LGTM` unblock message with a smart contextual unblock engine (`_smart_unblock_reply`) that checks local project file status, and added `prune_orphan_branches()` to clean up branch graveyard.

### Commits
- `0bf1cb5a` — `fix(router): prevent local provider HTTP 400 hanging router`
- `df3b98fc` — `fix(crons/manager): correct nina_ooda/nina_cicd module import path`
- `d79cec0c` — `fix(jules): smart auto-unblock + orphan branch pruner`

---

## [15.3.0] — 2026-06-29

### Fixed
- **`core/memory.py`** — Made `chromadb` fully optional: dynamic import with graceful fallback mocks when the library is not installed.
- **`core/reflexion.py`** — Fixed `generate_reflection` to call synchronous `dispatcher.dispatch()` correctly.
- **`core/agent_loop.py`** — Removed hallucinated kwargs `is_read_only=False, is_write_only=False` from `ClassifiedTask()` instantiation.

### Added
- **`tests/test_classified_task_contract.py`** — Three-tier LLM hallucination guard: field schema check, runtime validation tests, and full codebase AST scanner.
- **`git-hooks/pre-commit`** — Integrated contract tests and `mypy` type checks into the pre-commit gate.

### Commits
- `4296c4b7` — `fix(memory,reflexion): make chromadb optional and fix unit tests`
- `98f0c0c9` — `fix(agent_loop): remove invalid ClassifiedTask kwargs is_read_only/is_write_only`
- `8b386df9` — `test(contract): add ClassifiedTask signature guard + mypy pre-commit layer`

---

## [15.2.0] — 2026-06-29

### Fixed
- **System Restoration**: Resolved syntax errors, indentation faults in `tools/ninagate/main.py`, and git conflict markers in `tools/semantic_dedup.py`, `tools/pipeline_autopilot.py`, and `tools/ninagate_client.py`.
- **AST Refactoring**: Restored missing `extract_method` and `VarVisitor` back to `core/ast_refactor.py`.
- **Cognitive Modules**: Restored archived `base.py`, `evaluator.py`, `planner.py`, `registry.py`, and `verifier.py` back to `core/cognitive/`.
- **Knowledge Graph**: 
  - Restored `knowledge_graph` instance.
  - Added support for constructor `file_path` with JSON load/save support.
  - Implemented dictionary description parsing, `attributes` persistence, and node `attributes` extraction on node fetch.
  - Added `get_all_entities_by_type` and `query_neighbors` methods.
- **Autonomy Ratchet**: Restored `autonomy_ratchet` and `AutonomyTier = Rung` alias.
- **Git Repo Hygiene**: Surgically pruned and resolved all stale and obsolete branches (local and remote).


## [Unreleased] — 2026-06-25

### Added — Telemetry Pass-2: Full Pipeline Instrumentation

**`telemetry/emitter.py`** (new)
- Atomic, thread-safe JSONL writer to `telemetry.jsonl`
- Schema: `{ts, span_id, stage, event, payload}` per line
- 10 MB auto-rotation → `telemetry.jsonl.1`
- Pipeline-safe: all I/O errors swallowed to stderr, never raises

**`telemetry/__init__.py`** (updated)
- Now exports both `Tracker` (OTel) and `emit` (JSONL)
- Single import: `from telemetry import Tracker, emit`

**`telemetry/reader.py`** (new)
- CLI tail for `telemetry.jsonl`
- Flags: `--tail N`, `--stage`, `--event`, `--span`, `--follow`, `--json`
- ANSI colour-coded by stage (ninagate=blue, ouroboros=cyan)
- Usage: `python -m telemetry.reader --tail 20 --follow`

**`core/router.py`** (updated — telemetry pass-2)
- Added null-safe `_telem_emit` import block (fallback no-op on `ImportError`)
- Dual-emit `_telem_emit` alongside all existing `write_log` calls — no `write_log` removed
- Events wired: `route_start`, `route_ok` (all paths incl. critical), `route_ok_stream`, `route_exhausted`, `route_stream_error`, `provider_call_ok` (local + cloud + stream), `provider_error`, `provider_stream_error`
- `span_id` generated at `route()` entry, propagated to all downstream emit calls
- `circuit_state` included in every provider-level event payload

**`ninagate/main.py`** (updated — telemetry pass-4)
- `_telem_emit` wired at request entry (`request_in`), response exit (`response_out`), and exception handler (`error`)
- `span_id = uuid4()[:8]` generated at entry, logged through full request lifecycle

### Updated — Documentation
- `docs/observability.md` — full telemetry architecture, event reference, schema, CLI usage, dual-emit pattern, span propagation
- `docs/module_index.md` — telemetry package fully documented; ninagate and router telemetry status noted
- `docs/OUROBOROS_ARCHITECTURE.md` — pass-2 telemetry section added with full event table
- `docs/CHANGELOG.md` — this entry

### Commits
- `f777e79` — `core/router.py` telemetry pass-2 dual-emit
- This commit — documentation sync

---

## 2026-06-24

### Added — Telemetry Pass-1 (router write_log stubs)
- `write_log` stubs added to `route()`, `_call_provider()` in `core/router.py` covering `route_start`, `route_ok`, `route_ok_stream`, `route_exhausted`, `provider_call_ok`
- `telemetry/tracker.py` shim created (re-exports `NinaTracer` with null-object fallback)
- `telemetry.jsonl` root file created

---

## 2026-06-23

### Added
- MoA (Mixture-of-Agents) routing for `research`, `analysis`, `coding` task types
- `_MOA_PROPOSERS = [POLLINATIONS, GROQ, CHUTES]` parallel proposer pattern
- OODA validation loop in `_validate_response()` using GROQ as logic gate
- HyperDrive policy + MemoCache semantic response caching
- `core/rpm_scheduler.py` per-provider RPM throttle
- `core/quota_router.py` daily quota tracking + force-local logic
- `core/smart_router.py` learned provider ranking by task type
- Quality probe in `_idle_monitor()` for degraded providers
- `parallel_route()` RAM-guarded parallel multi-prompt dispatch
- CRITICAL task override → `GEMINI_FLASH_PROD`
- LPU deterministic fast-track → `LOCALFAST`
- 429 rate-limit → 5-minute circuit open + Telegram alert
- `graceful_fallback_chain()` local-first exhaustive fallback
- Circuit breaker state persistence (`data/circuit_state.json`)
- `get_available_providers()` + `get_models_status()` status APIs

---

## 2026-06-20

### Added
- `ninagate/circuit_breaker.py` — gateway-level circuit breaker
- `ninagate/providers.json` — provider registry (name, base_url, model, tier, api_key_env)
- NinaGate FastAPI proxy (`ninagate/main.py`) — opencode → Ouroboros bridge
- `CircuitBreaker` class in `core/router.py` with CLOSED/OPEN/HALF_OPEN states
- `ProviderHealth` dataclass with rolling latency deque and health score
- `ResponseCache` with MD5 key + TTL per task type
- `CostTracker` estimating $0.0000002/token, writing to `logs/router.log`
- Multi-tier provider loading from `providers.json` at startup
- Thermal safeguard (`tools/system.py::is_thermal_safe`) blocking local inference on overheating

---

## 2026-06-15

### Added
- Initial NINA architecture: `core/config.py`, `core/logger.py`, `core/task_classifier.py`
- Ollama local provider (`LOCALFAST`, `LOCALHEAVY`) — model: `dulal`
- Jules Telegram notification bridge (`tools/jules.py`)
- Provider health external probe tracker (`tools/provider_health.py`)
- `docs/` directory with initial architecture, README, OUROBOROS_ARCHITECTURE
