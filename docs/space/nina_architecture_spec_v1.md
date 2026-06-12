# NINA Modular Monolith — Architecture Spec v1.0
**Author:** M. Baizid Alam (aibony)  
**Date:** 2026-06-10  
**Status:** PROPOSED — Pre-migration planning artifact  
**Source:** Combined analysis: GitHub Copilot (codebase scan) + Perplexity (architecture review) + live codebase backup 2026-06-09

---

## 1. Executive Summary

NINA currently works well architecturally but has **concern-leakage** across modules:
- `guardian_engine.py` (73 KB) mixes startup safety, runtime safety, AST scanning, and rollback
- `healthcheck.py` (34 KB) overlaps with guardian, capabilities, and router responsibilities
- Sync responsibilities are split across `nina_sync.sh`, `guardian.sh`, and file-update scripts
- No anti-corruption layer for external tools (Jules, agy, Gemini CLI)
- No test coverage for 3 critical modules (`router`, `guardian_engine`, `memory`)

The fix: **one modular monolith, six bounded modules, one routing spine.**

---

## 2. Target Module Map

```
Interface → Orchestrator → [Router | Executor | Sync | Guardian]
                ↓
           (shared: Config, Memory, Models)
```

### Module Boundaries

| Module | Owner | Files (current → target) | Forbidden Dependencies |
|--------|-------|--------------------------|------------------------|
| **Core Orchestrator** | Task lifecycle, policies, state transitions | `core/agent.py`, `core/task_store.py`, `core/capabilities.py` | Must not import from interfaces; must not know provider names |
| **Router Gateway** | Model/provider selection, rate limits, circuit breakers | `core/router.py`, `core/config.py` (RATELIMITS) | Must not import tools or sync logic |
| **Executor Layer** | Adapters for agy, Gemini CLI, Qwen, Jules | `tools/shell.py` + new `executors/` package | Must not own business logic; pure adapter pattern |
| **Sync Layer** | All git/file/Space sync | `nina_sync.sh` + new `sync/manager.py` | Must not trigger guardian checks; consumes a health signal, does not produce it |
| **Guardian Layer** | Startup checks, runtime safety, AST scan, rollback, error register | `guardian_engine.py` → split into `guardian/engine.py`, `guardian/ast_check.py`, `guardian/baseline.py`, `guardian/rollback.py` | Must not route model calls; reads error register, never writes sync state |
| **Interfaces Layer** | Telegram, CLI, Dashboard | `interfaces/telegram_interface.py`, `dashboard/`, `main.py` (entry) | Must only call Orchestrator application services; never Router or Guardian directly |

---

## 3. Canonical Data Objects

These are the single source of truth for shared data shapes. All modules consume these; none redefine them.

```python
# core/models.py  ← NEW FILE, owns all canonical schemas

@dataclass
class Task:
    id: str
    goal: str
    task_type: str        # research | coding | document | sensitive | general
    status: TaskStatus    # pending | running | done | failed
    created_at: float
    result: str = ""
    metadata: dict = field(default_factory=dict)

@dataclass  
class RouteDecision:
    provider: str
    model: str
    force_local: bool
    reason: str           # logged for observability

@dataclass
class SyncResult:
    success: bool
    snapshot_path: str
    errors: list[str]

@dataclass
class GuardianReport:
    passed: bool
    checks: list[str]     # list of check names run
    failures: list[str]   # list of failure descriptions
    rollback_available: bool
```

---

## 4. Anti-Corruption Layers

External tools (Jules, agy, Gemini CLI, Qwen, Copilot) must **not** leak their naming or payloads into NINA's internal model.

```
External Tool          ACL Adapter              NINA Internal
─────────────          ───────────              ─────────────
jules remote new   →   JulesAdapter.submit()  → ExecutorResult
agy "do X"         →   AgyAdapter.run()       → ExecutorResult  
gemini "do X"      →   GeminiCLIAdapter.run() → ExecutorResult
qwen "do X"        →   QwenAdapter.run()      → ExecutorResult
```

Each adapter lives in `executors/<tool_name>.py` and:
1. Translates NINA's `Task` object into the tool's specific CLI/API call format
2. Parses the tool's output back into a standardized `ExecutorResult`
3. Handles tool-specific errors (e.g. Jules PR not found) and maps to NINA error types
4. Never exposes tool-specific flags or arguments to callers above it

---

## 5. Single-Concern Ownership Rules

| Concern | Single Owner | What Must NOT Touch It |
|---------|-------------|------------------------|
| Provider selection logic | `Router Gateway` | Agent loop, interfaces, guardian |
| Task lifecycle / state machine | `Core Orchestrator` | All other modules |
| File/git sync | `Sync Layer` | Guardian, interfaces, cron scripts |
| Safety checks (AST, baseline, syntax) | `Guardian Layer` | Router, sync, interfaces |
| Error register writes | `Guardian Layer` | Agent loop, tools, sync |
| Capability health state | `Core Orchestrator` (via CapabilityRegistry) | Router (reads only), guardian (reads only) |
| External tool calls | `Executor Layer` adapters | Orchestrator knows *what* to execute, never *how* |

---

## 6. Guardian Layer Split (Priority #1)

`guardian_engine.py` (73 KB) must be split. Proposed target:

```
guardian/
├── __init__.py           # re-exports GuardianEngine facade
├── engine.py             # startup/runtime entry point, orchestrates checks
├── ast_check.py          # AST scanning logic (moved from guardian_engine.py)
├── baseline.py           # baseline drift detection (moved from guardian_engine.py)  
├── rollback.py           # rollback strategy + git revert logic
└── error_register.py     # error register read/append (single writer rule)
```

`guardian/engine.py` becomes a thin orchestrator that calls the sub-modules. No logic lives directly in it — it only sequences and reports.

---

## 7. Test Coverage Targets (Priority #2)

| Test File | Module | Critical Because |
|-----------|--------|-----------------|
| `tests/test_router.py` | Router Gateway | Routes every LLM call; failure = silent wrong model |
| `tests/test_guardian.py` | Guardian Layer | Safety gate for self-modifying code |
| `tests/test_memory.py` | Memory (ChromaDB) | Context quality degrades silently without tests |
| `tests/test_agent_loop.py` | Core Orchestrator | THINK→PLAN→ACT correctness |
| `tests/test_sync.py` | Sync Layer | Sync bugs corrupt Space context |

Minimum viable: `test_router.py` + `test_guardian.py` first (highest risk, zero coverage today).

---

## 8. Structured Logging (Priority #3)

Replace current mixed print/file logging with `loguru` JSON output.

```python
# Proposed: core/logging_setup.py
from loguru import logger

def configure_logging(log_level: str = "INFO"):
    logger.add(
        "docs/logs/nina.log.json",
        format="{time:ISO8601} {level} {name} {message} {extra}",
        serialize=True,      # outputs JSON
        rotation="10 MB",
        retention="30 days",
        level=log_level,
    )
```

All modules switch from `logging.getLogger(...)` to `from loguru import logger`. The structured JSON format enables future log parsing, alerting, and dashboard ingestion.

---

## 9. Dependency Pinning (Priority #4)

Run in venv and replace `requirements.txt`:

```bash
source ~/nina/venv/bin/activate
pip freeze > requirements.txt
```

Add a comment block at the top:

```
# Generated: 2026-06-10
# Python: 3.11.x
# Platform: Ubuntu 26.04 LTS / ASUS VivoBook X530FN
# Regenerate: source ~/nina/venv/bin/activate && pip freeze > requirements.txt
```

---

## 10. Migration Path (Strangler Fig — Do NOT Rewrite)

Execute in this order. Each step is independently deployable and reversible.

| Step | Action | Validation | Est. Time |
|------|--------|------------|-----------|
| 1 | Create `core/models.py` with canonical data objects | Import in `agent.py`, confirm no regression | 30 min |
| 2 | Split `guardian_engine.py` into `guardian/` package | Run `guardian.sh`, confirm startup checks pass | 2-3 hr |
| 3 | Create `executors/` package with agy + Jules ACL adapters | Test agy task via adapter, confirm behavior unchanged | 1-2 hr |
| 4 | Add `tests/test_router.py` + `tests/test_guardian.py` | `pytest tests/` passes | 2-3 hr |
| 5 | Consolidate sync into `sync/manager.py`, shell scripts call it | Run `./nina_sync.sh`, confirm Google Drive sync | 1-2 hr |
| 6 | Replace logging with loguru JSON | `cat docs/logs/nina.log.json \| jq .` produces valid JSON | 1 hr |
| 7 | Pin `requirements.txt` | Fresh venv install succeeds | 15 min |

---

## 11. Files to Merge / Delete / Rename

| Action | File | Reason |
|--------|------|--------|
| **Split** | `guardian_engine.py` → `guardian/` package | 73 KB, single-concern violation |
| **Merge** | `healthcheck.py` logic → `guardian/engine.py` + `core/capabilities.py` | Overlaps both |
| **Create** | `core/models.py` | Canonical data objects currently scattered |
| **Create** | `executors/__init__.py`, `executors/agy.py`, `executors/jules.py` | ACL adapters, currently missing |
| **Create** | `sync/manager.py` | Sync logic currently only in shell scripts |
| **Rename** | `tools/append_lock.py` → function inside `guardian/error_register.py` | One-off script, should be a module function |
| **Rename** | `append_log.py` → utility in `sync/manager.py` | Same reason |
| **Delete** | `agent/context.py` (0 bytes), `agent/__init__.py` (0 bytes) | Empty placeholder files |

---

## 12. Design Principles (North Star)

> One concern, one owner.  
> One workflow, one orchestrator.  
> One external tool, one adapter.  
> One state model, one canonical schema.

Every future NINA change must pass this check:
- Which module owns this concern? If the answer is "two modules," stop and fix that first.
- Does this change require touching an interface AND a router? If yes, it's likely a cross-cutting concern that needs a shared service, not two edits.
- Does this import go in the right direction? Interface → Orchestrator → Router/Executor/Sync/Guardian — never sideways or upward.

---

*Next step: Attach current `guardian_engine.py` + `healthcheck.py` source files and request Jules spec for Step 2 (Guardian split).*
