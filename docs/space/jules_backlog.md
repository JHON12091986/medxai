# NINA Jules Backlog
> **Last audited:** 2026-06-14 04:14 +06 | **Auditor:** Perplexity (Claude Sonnet 4.6) | **Source:** GitHub PR history aibony/nina PR #185–#225 + jules_pipeline_audit.md

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ DONE | Merged PR confirms full completion |
| ⚠️ PARTIAL | PR merged but follow-up gaps found by audit |
| 🔴 TODO-P1 | Blocking / high-risk — do next |
| 🟠 TODO-P2 | Important — do this sprint |
| 🟡 TODO-P3 | Nice-to-have / low-risk improvement |
| 📋 NEEDS SPEC | Task idea exists but cannot be handed to Jules without more detail |

---

## Section 1 — Completed (Confirmed by PR History)

### ✅ E-1 — Remove Unused Constants in Router
**PR:** [#201](https://github.com/aibony/nina/pull/201) — *Optimize dictionary unions in routing lookups*
Removed `STEP_BUDGETS` and `DEFAULT_MAX_STEPS`. Also replaced `{**T1, **T2, **T3}` with `T1 | T2 | T3`.
**Audit verdict:** DONE. No further action.

---

### ✅ E-2 — Standardize Gemini Fallback Model
**PR:** [#225](https://github.com/aibony/nina/pull/225) + [#218](https://github.com/aibony/nina/pull/218) — *Optimize NinaGate routing, finalize NinaGate optimization*
`core/router.py`, `ninagate/providers.json`, and `bin/gemini` shim now unified. Today's local commit (`fix(pipeline): unify classifier, standardize gemini model`) also touched `core/config.py` and `ninagate/providers.json`.
**Audit verdict:** DONE. Watch for model name drift if providers.json is edited manually in future.

---

### ✅ E-3 — Externalize Hardcoded Config Values (MAX_CONCURRENT_SESSIONS, QUOTA_SOFT_LIMIT)
**PR:** Today's local commit — *externalize config, harden jules session_end*
`MAX_CONCURRENT_SESSIONS` and `QUOTA_SOFT_LIMIT` moved to `core/config.py`.
**Audit verdict:** DONE.

---

### ✅ E-4 — Unify Task Classification Logic
**PR:** Today's local commit — `core/task_classifier.py` created as new file
`ninagate/main.py` and `core/router.py` now both import from unified classifier.
**Audit verdict:** DONE. This was the highest-effort audit recommendation (MEDIUM risk) — fully resolved.

---

### ✅ E-5 — Harden jules.py session_end Error Handling
**PR:** Today's local commit — *harden jules session_end*
`subprocess.run` for `nina_sync.sh` now wrapped in `try/except subprocess.CalledProcessError`.
**Audit verdict:** DONE.

---

### ✅ AG-N-05 — Context Injector (NinaFlash CLI)
**PR:** [#224](https://github.com/aibony/nina/pull/224) — *Confirmed implemented, tests passing locally*
Context Injector verified in `tools/ninaflash.py`.
**Audit verdict:** DONE.

---

### ✅ AG-N-08 — Dependency Cycle Detector
**PR:** [#196](https://github.com/aibony/nina/pull/196) — *Fix circular import cycle detection (`len(cycle) > 2` bug fixed to `>= 2`)*
**PR:** [#224](https://github.com/aibony/nina/pull/224) — verified again
**Audit verdict:** DONE. The length-2 cycle bug was the correct fix.

---

### ✅ AG-N-09 — Code Complexity Watchdog (cyclomatic complexity)
**PR:** [#225](https://github.com/aibony/nina/pull/225) — *Fixed AST branching nodes: added `AsyncFor`, `AsyncWith`, `BoolOp`; removed non-branching `Try`*
**Audit verdict:** DONE. This was a correctness bug, not just a feature — now properly calculates cyclomatic complexity.

---

### ✅ AG-N-10 — Symbol Migration Tool
**PR:** [#224](https://github.com/aibony/nina/pull/224) — *Confirmed implemented*
**Audit verdict:** DONE.

---

### ✅ NinaFlash AST Traversal Optimization
**PR:** [#196](https://github.com/aibony/nina/pull/196) — *Use `ast.get_source_segment` instead of `ast.unparse` in `cmd_code_symbol`*
Preserves syntax formatting and inline comments. Also fixed `__init__.py` relative path resolution.
**Audit verdict:** DONE.

---

### ✅ NinaFlash Arg Parsing Bug
**PR:** [#201](https://github.com/aibony/nina/pull/201) — *Fix `ninaflash.py` context packer to preserve argument formatting and default values*
Parenthesis counting now handles string literals with escaped chars.
**Audit verdict:** DONE.

---

### ✅ NinaFlash `list` Command + CPU Telemetry Caching
**PR:** [#195](https://github.com/aibony/nina/pull/195) — *Add list command; CPU metric telemetry caching in ninagate/main.py*
**Audit verdict:** DONE.

---

### ✅ CRITICAL — Command Injection Fix in ninaflash_core.py
**PR:** [#219](https://github.com/aibony/nina/pull/219) — *Replace `os.system` with `subprocess.run(shell=False)` in `cmd_batch`*
**Audit verdict:** DONE. CRITICAL severity resolved.

---

### ✅ Config Pre-caching Perf Fix (hot path masking)
**PR:** [#222](https://github.com/aibony/nina/pull/222) — *Pre-cache secret values at init; avoid dumping Pydantic object on every mask call*
**Audit verdict:** DONE.

---

### ✅ NinaFlash Duplicate Stub Cleanup
**PR:** [#196](https://github.com/aibony/nina/pull/196) — *Remove duplicated stub functions in CLI router*
**Audit verdict:** DONE.

---

## Section 2 — Partial / Needs Follow-Up

### ⚠️ Provider List Redundancy — core/router.py Tiers vs ninagate/providers.json
**Original finding:** `PROVIDERS_TIER1/2/3` in `router.py` and `ninagate/providers.json` represent the same data in two places. If one is edited without the other, models drift silently.
**What was done:** Today's commit unified the model name in both, but the structural duplication was NOT removed.
**Gap:** Two sources of truth still exist. No single canonical provider registry.
**Priority:** 🟠 TODO-P2

**Jules spec when ready:**
```
File: core/router.py + ninagate/providers.json + ninagate/main.py
Goal: Make ninagate/providers.json the SINGLE canonical provider registry.
  - router.py should import/load provider definitions from providers.json at startup
    instead of defining PROVIDERS_TIER1/2/3 as hardcoded dicts
  - ninagate/main.py already reads providers.json — no change needed there
  - router.py: remove hardcoded tier dicts; add a loader that reads providers.json
    and builds tiers from a "tier" field in each provider entry
  - Add "tier": 1|2|3 to each entry in providers.json
  - Do NOT change routing logic, only the data source
  - Do NOT touch .env, guardian_engine.py, interfaces/, or tests/
  - Acceptance: python3 -c "from core.router import Router; r=Router(); print(r.ALL_PROVIDERS)" succeeds
```

---

### ⚠️ jules.py — `session_end` nina_sync.sh Error Masking (PARTIAL FIX)
**What was done:** `check=True` + `CalledProcessError` wrap added in today's commit.
**Remaining gap:** Errors are caught but only logged locally. If `nina_sync.sh` fails silently (non-zero exit with no exception), the Telegram user gets no notification and the session ledger is never updated.
**Priority:** 🟠 TODO-P2

**Jules spec when ready:**
```
File: tools/jules.py — function: session_end
Goal: When nina_sync.sh raises CalledProcessError OR returns non-zero:
  - Log the failure with full stderr to nina_update_log.md via append_log
  - Send a Telegram alert: "⚠️ NINA sync failed after Jules session_end. Check logs."
  - Do NOT abort the session_end — sync failure is non-fatal, session must still close
  - Do NOT touch any file outside tools/jules.py
  - Acceptance: simulate failure by passing a bad path; confirm log entry + Telegram message
```

---

### ⚠️ Governance Warnings — 3 Files Missing from Index
**Files:** `docs/space/gemini_shim_spec.md`, `docs/space/jules_pipeline_audit.md`, `core/task_classifier.py`
**Finding:** Pre-push hook reports all three as unmanaged. Index metadata quality at 81.1%.
**Priority:** 🟡 TODO-P3 (governance hygiene, not a runtime risk)

**Fix:** Run `tools/update_index.py` locally and add entries for all three files. Low effort, agy task.

---

## Section 3 — Open / Pending (Not Yet Started)

### 🔴 TODO-P1 — Provider Health Monitoring + Auto-Failover Alerting
**Context:** `core/router.py` has tiered failover logic but no persistent health state. If Gemini quota is exhausted and router silently falls to Tier 3 (OpenRouter), the user has no visibility until a response is slow or wrong.
**Risk:** Silent quality degradation — user sends a complex task, gets Tier 3 response without knowing.
**Priority:** 🔴 P1 — runtime reliability

**Jules spec:**
```
Files to change: core/router.py, tools/monitor.py (or create tools/provider_health.py)
Goal: Track per-provider success/failure rates with a rolling 10-minute window.
  - Add a ProviderHealthTracker class (or extend existing Router):
      * Records last N=20 calls per provider: success/failure + latency
      * Exposes health_summary() dict: {provider: {ok_rate, avg_latency, last_error}}
  - When a provider fails 3 consecutive times, emit a Telegram alert:
      "⚠️ Provider {name} degraded. Routing to fallback tier."
  - When provider recovers (1 success after failure streak), log recovery.
  - Persist health state to data/provider_health.json (overwrite on each update)
  - Do NOT change existing routing logic — tracker is observability only
  - Do NOT touch .env, interfaces/, guardian_engine.py, or crons/
  - Acceptance: curl NinaGate with a bad provider key, confirm Telegram alert fires within 60s
```

---

### 🔴 TODO-P1 — Governance Index Auto-Update (54 files missing tests)
**Context:** Pre-push hook reports 54 files requiring tests with no matching test file found. This is a governance integrity issue — the index claims coverage that doesn't exist.
**Risk:** Test coverage claims in docs are false. Governance score (81.1%) is inflated.
**Approach:** Don't write 54 test files — that's noise. Write a governance reconciler that marks files as `"test_required": false` in the index if they are infra/tooling scripts (not logic-bearing), so the warning count reflects real gaps only.
**Priority:** 🔴 P1 — governance integrity

**Jules spec:**
```
File to change: tools/validate_index.py (and governance_index.json if it exists)
Goal: Add a "test_exempt" classification for files that are tooling/infra scripts:
  - Read the index; for each file flagged as "requires_tests" with no test file:
      * If file is in crons/ or tools/ AND its only public functions are CLI entrypoints
        (i.e., if __name__ == "__main__" pattern), mark as test_exempt: true
      * If file is in interfaces/ and is a pure adapter (no business logic), mark exempt
  - Re-run validate_index: only files with real logic gaps should warn
  - Do NOT delete any test requirements — only reclassify based on code pattern analysis
  - Output: updated governance_index.json + console summary "X real gaps, Y exempted"
  - Do NOT touch .env, guardian_engine.py, main.py, or core/router.py
```

---

### 🟠 TODO-P2 — gemini_shim_spec.md — Spec to Code
**Context:** `docs/space/gemini_shim_spec.md` exists as a spec doc but is not in the governance index and there is no corresponding implementation audit confirming the `bin/gemini` shim matches the spec.
**Priority:** 🟠 P2

**Action needed before Jules task:** Read `docs/space/gemini_shim_spec.md` and `bin/gemini` side-by-side. Identify any drift between spec and implementation. Then hand to Jules with exact delta.
**Status:** 📋 NEEDS SPEC (read the files first)

---

### 🟠 TODO-P2 — NinaGate System Template — Wire to Jules Dispatch
**Context:** `ninagate/system_templates.json` defines NINA's identity contract. But when `tools/jules.py` dispatches a new task, the `prompt` payload does NOT inject this system template. Jules receives raw task text with no NINA identity framing.
**Effect:** Jules-generated code/PRs don't know NINA's conventions (append-only logs, no heredoc, conventional commits, etc.) unless the task prompt manually includes them — which is fragile.
**Priority:** 🟠 P2

**Jules spec:**
```
File: tools/jules.py — function: run_dispatch
Goal: Before sending the dispatch prompt to Jules API, prepend the NINA system template:
  - Read ninagate/system_templates.json at dispatch time (not at import time)
  - Extract the "system" role content
  - Prepend it to the prompt as: f"[NINA CONTEXT]\n{system_content}\n\n[TASK]\n{prompt}"
  - Keep prompt length within 8000 chars total — truncate system template if needed
    (truncate from the bottom of the template, not the task)
  - Do NOT change anything in ninagate/main.py or core/router.py
  - Do NOT touch .env, guardian_engine.py, or interfaces/
  - Acceptance: dispatch a test task; confirm PR description or Jules output references
    NINA conventions (append-only logs, conventional commits)
```

---

### 🟠 TODO-P2 — juleslock.txt — Scope Enforcement in Pre-Push Hook
**Context:** `juleslock.txt` exists to prevent Jules from touching files locked by another session. But the pre-push governance hook (`pre-push` git hook) does NOT check `juleslock.txt`. If a Jules PR is mid-flight and a manual commit touches the same file, the push succeeds silently.
**Priority:** 🟠 P2

**Jules spec:**
```
File: .git/hooks/pre-push (or whichever script runs the governance check)
Goal: Before allowing push, read juleslock.txt and check if any file in the current
  git diff (against origin/main) matches a locked file:
  - If match found: abort push with message:
    "BLOCKED: {filename} is locked in juleslock.txt (Jules session in flight).
     Wait for Jules PR or clear the lock manually."
  - If no match: proceed normally
  - Do NOT change validate_index.py or audit_repo_hygiene.py
  - Acceptance: lock a file in juleslock.txt, attempt to push a commit touching it,
    confirm push is blocked with the correct message
```

---

### 🟡 TODO-P3 — OpenRouter Fallback — Explicit Model Pin
**Context:** `PROVIDERS_TIER3` in `router.py` includes OpenRouter as a fallback but does not pin a specific model. OpenRouter's default model can change silently.
**Priority:** 🟡 P3

**Fix:** Add `"model": "openai/gpt-4o-mini"` (or equivalent) to the OpenRouter entry in `providers.json` once the provider registry is unified (see Section 2 P2 task above).
**Dependency:** Complete the provider registry unification task first.

---

### 🟡 TODO-P3 — ARCHITECTURE.md Drift Check
**Context:** The audit confirmed ARCHITECTURE.md was accurate as of the audit date. But 7 PRs merged since then have changed `router.py`, `ninagate/main.py`, `tools/jules.py`, and added `core/task_classifier.py`. ARCHITECTURE.md has not been updated.
**Priority:** 🟡 P3

**Fix (agy, not Jules):** Read ARCHITECTURE.md, read the changed files, write updated section covering unified classifier, externalised config, and jules session_end hardening. One agy task, single file.

---

### 📋 NEEDS SPEC — Cron Health Dashboard (crons/ visibility)
**Context:** `crons/manager.py`, `crons/evolve_loop.py`, `crons/backup_jobs.py` run on schedule but there is no Telegram-accessible status command showing when each cron last ran, its exit status, and next scheduled time.
**Why it matters:** If `evolve_loop.py` silently fails, NINA's self-improvement loop stops with no alert.
**Status:** Needs design decision — should this be a `/cron_status` Telegram command or a dashboard file written to `docs/space/`? Decide before writing Jules spec.

---

### 📋 NEEDS SPEC — Session Ledger Integrity Audit
**Context:** `tools/session_ledger.py` tracks session history but there is no periodic audit checking for orphaned sessions (started but never closed) or sessions where `nina_sync.sh` failed.
**Status:** Needs definition of "orphaned session" threshold (e.g., open > 2 hours?) before Jules can implement.

---

## Summary Snapshot

| Category | Count |
|----------|-------|
| ✅ Confirmed done | 14 |
| ⚠️ Partial — follow-up needed | 3 |
| 🔴 P1 — do next | 2 |
| 🟠 P2 — this sprint | 3 |
| 🟡 P3 — low priority | 2 |
| 📋 Needs spec | 2 |

**Recommended next session order:**
1. `git pull --rebase && git push && ./nina_sync.sh` (unblock push — right now)
2. P1: Provider health monitoring (runtime reliability)
3. P1: Governance index reconciler (false positive cleanup)
4. P2: Provider registry unification (structural debt)
5. P2: System template injection into Jules dispatch (quality)
