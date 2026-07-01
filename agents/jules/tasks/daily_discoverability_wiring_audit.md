# Daily Discoverability & Wiring Audit
**Task ID:** `daily-discoverability-wiring-audit`
**Scheduled:** Daily — run every 24 hours (suggested cron: `0 2 * * *` server-local time)
**Assigned to:** Jules
**Owner:** @aibony
**Last updated:** 2026-06-18
**Severity model:** 🔴 Critical → 🟠 High → 🟡 Medium → 🟢 Low

---

## Purpose

This task is a comprehensive, automated daily health-check of the entire `aibony/nina` repository. Its goal is to detect four classes of problems **before they silently break Nina at runtime**:

1. **Discoverability failures** — files and modules that exist on disk but are not imported, referenced, or reachable from any execution path (dead code, ghost scripts, orphan tools).
2. **Wiring failures** — imports that are declared but resolve to missing modules, shell scripts that call Python files or other scripts that no longer exist, and config/service files that reference binaries or paths that are absent.
3. **Duplication & drift** — files with identical or near-identical content that have diverged (e.g. `core/observability.py` vs `core/observability_otel.py`), routing history bloat, update-log runaway growth, and stale JSON artefacts.
4. **Structural integrity** — `__init__.py` export gaps, missing `requirements.txt` entries for used imports, `.service` files pointing at non-existent Python entrypoints, and scheduler/cron wiring gaps.

The audit **reads files, computes diffs, and reports findings**. It commits a dated report to `docs/audit/YYYY-MM-DD_wiring_audit.md`. It does **not** auto-fix anything — all fixes are flagged as issues for human or follow-up Jules tasks.

---

## Repo Structure Reference

Below is the canonical directory map Jules must use as the ground truth for this audit. Every file and folder listed here must be accounted for in the audit output.

```
aibony/nina/
├── .agy/                        # AGY agent config & state
├── .cursor/                     # Cursor IDE rules
├── .gemini/                     # Gemini agent config
├── .github/                     # GitHub Actions CI/CD workflows
├── .jules/                      # Jules task definitions (this file lives here)
├── agent/                       # Agent sub-package
├── bin/                         # Executable binaries / CLI entry points
├── checks/                      # Pre-flight / health check scripts
├── config/                      # YAML/JSON runtime config files
├── core/                        # Main Python package — Nina's brain
│   ├── agents/                  # Sub-agents
│   ├── cache/                   # Cache layer modules
│   ├── cognition/               # Cognition sub-package
│   ├── cognitive/               # Cognitive sub-package
│   ├── executor/                # Executor sub-package
│   ├── planner/                 # Planner sub-package
│   ├── quota/                   # Quota sub-package
│   ├── __init__.py
│   ├── agent.py                 # (57 KB) Core agent class
│   ├── agent_loop.py            # (8 KB)
│   ├── agy_briefing.py
│   ├── ast_refactor.py
│   ├── autogen.py
│   ├── autonomy_ratchet.py
│   ├── bench_runner.py          # (15 KB)
│   ├── capabilities.py
│   ├── checkpoint.py
│   ├── circuit_breaker.py
│   ├── config.py                # (9 KB)
│   ├── crew.py
│   ├── event_bus.py
│   ├── gap_analysis.py
│   ├── goal_manager.py
│   ├── graph_rag.py
│   ├── hotreload.py
│   ├── hyperdrive_cache.py
│   ├── hyperdrive_context.py
│   ├── hyperdrive_executor.py
│   ├── hyperdrive_goals.py
│   ├── hyperdrive_policy.py
│   ├── jules_guard.py           # (8 KB)
│   ├── knowledge.py
│   ├── knowledge_graph.py
│   ├── logger.py
│   ├── mcp_client.py
│   ├── memory.py                # (28 KB)
│   ├── memory_manager.py
│   ├── nina.py                  # (21 KB) Top-level Nina class
│   ├── observability.py         # (12 KB)
│   ├── observability_otel.py
│   ├── prompt_cache.py
│   ├── quota_alert.py
│   ├── quota_dispatcher.py
│   ├── quota_router.py
│   ├── reasoning.py             # (16 KB)
│   ├── reasoning_engine.py      # (13 KB)
│   ├── reflexion.py
│   ├── registry.py
│   ├── reminders.py
│   ├── router.py                # (42 KB) ⚠ largest routing file — wiring audit priority
│   ├── rpm_scheduler.py
│   ├── sandbox.py
│   ├── schema_val.py
│   ├── shared_cache.py
│   ├── smart_router.py
│   ├── swarm.py
│   ├── swarm_engine.py
│   ├── task_classifier.py
│   ├── task_planner.py
│   ├── task_store.py            # (32 KB)
│   ├── utils.py
│   ├── vault.py
│   └── verifier.py
├── crons/                       # Cron job definitions
├── dashboard/                   # Dashboard code
├── data/                        # Runtime data / state files
├── docs/                        # Documentation
│   └── audit/                   # ← Jules writes daily reports here
├── exports/                     # Export artefacts
├── git-hooks/                   # Git hook scripts
├── interfaces/                  # External interface adapters
├── ninagate/                    # NinaGate routing / gateway module
├── scripts/                     # Utility scripts
│
├── Root-level Python files:
│   ├── main.py                  # (1 KB) Entrypoint — MUST wire correctly to core/nina.py
│   ├── agy_impact_check.py      # (7 KB)
│   ├── generate_codemap.py      # (8 KB)
│   ├── generate_backups.sh      # (6 KB) — also check sh wiring
│   ├── guardian_engine.py       # (79 KB) ⚠ largest file — check for dead internal functions
│   ├── healthcheck.py           # (59 bytes) — stub or real?
│   ├── idleloop.py              # (12 KB)
│   ├── nina_cicd.py             # (12 KB)
│   ├── nina_commit_index.py     # (3 KB)
│   ├── nina_context_graph.py    # (12 KB)
│   ├── nina_ooda.py             # (9 KB)
│   ├── nina_wiring_audit.py     # (8 KB) — existing wiring audit; compare with this task's scope
│   ├── ninajulesgithub.py       # (5 KB)
│
├── Root-level Shell scripts:
│   ├── agy_task.sh              # (6 KB)
│   ├── agy_verify.sh            # (2 KB)
│   ├── agy_watchdog.sh          # (1 KB)
│   ├── nina_aider.sh            # (1 KB)
│   ├── nina_audit.sh            # (1 KB)
│   ├── nina_cleanup.sh          # (3 KB)
│   ├── ~~nina_codebase_backup.sh~~ (deleted)  # (2 KB)
│   ├── ~~nina_docbase_backup.sh~~ (deleted)   # (1 KB)
│   ├── ~~nina_docs_export.sh~~ (deleted)      # (1 KB)
│   ├── nina_export.sh           # (1 KB)
│   ├── ~~nina_logbase_backup.sh~~ (deleted)   # (1 KB)
│   ├── nina_sync.sh             # (22 KB) ⚠ largest shell script — routing history write loop lives here
│   ├── ninagate_load_test.sh    # (1 KB)
│
├── Root-level Service/Config files:
│   ├── nina.service             # systemd unit — must reference real entrypoint
│   ├── nina-dashboard.service   # systemd unit — must reference real entrypoint
│   ├── ninajulesgithub.service  # systemd unit — must reference real Python file
│   ├── Makefile                 # (675 bytes) — check all targets reference existing files
│   ├── requirements.txt         # must cover all imports used in *.py files
│   ├── pytest.ini               # check testpaths exist
│
├── Root-level Data/Artefact files (check for staleness & bloat):
│   ├── nina_update_log.md       # (264 KB) ⚠ RUNAWAY GROWTH — check line count daily
│   ├── nina_commit_index.md     # (22 KB) — check for duplicate commit entries
│   ├── nina_context.md          # (9 KB)
│   ├── nina_context_graph.json  # (20 KB)
│   ├── call_graph_test.json     # (93 KB) — stale test artefact?
│   ├── efficiency_report.json   # (610 bytes)
│   ├── bench_report.md          # (1 KB)
│   ├── juleslock.txt            # (0 bytes) — lock file, should be empty; alert if non-empty
│   └── CHANGELOG.md             # (20 KB) — verify last entry matches latest commit
```

---

## Audit Checks — Full Specification

### SECTION A: Python Import Wiring

**A1 — Broken Imports (🔴 Critical)**
For every `.py` file in the repo (root + all subdirs):
- Parse all `import X` and `from X import Y` statements using Python `ast` module (do not regex-parse).
- For each import of an internal module (i.e., not a stdlib or third-party package listed in `requirements.txt`), verify the target file exists at the expected path.
- Flag any import where the resolved path does not exist as **BROKEN IMPORT**.
- Special attention: `core/router.py` (42 KB, highest import density), `core/agent.py` (57 KB), `guardian_engine.py` (79 KB).

**A2 — Unused Imports (🟡 Medium)**
For every `.py` file, identify imports that are declared but never referenced in the file body (use `ast` to check for name usage). Report file + line number. Do not auto-remove — flag only.

**A3 — Orphan Python Files (🟠 High)**
Identify `.py` files that are:
- Not imported by any other file in the repo, AND
- Not listed as an entrypoint in any `.service`, `Makefile`, `crons/`, or `.github/workflows/` file, AND
- Not named `__init__.py`, `conftest.py`, or matching `test_*.py` / `*_test.py`.

These are orphan files — they exist but are unreachable. Flag them.

**A4 — `__init__.py` Export Gaps (🟡 Medium)**
For each package directory that has an `__init__.py`, check whether the `__init__.py` explicitly exports (via `__all__` or direct import) the public modules in that package. If a module in `core/` is not exported from `core/__init__.py` but is imported directly by files outside `core/`, flag the inconsistency.

**A5 — `requirements.txt` Coverage (🟠 High)**
Collect every `import X` statement across all `.py` files where `X` is not a stdlib module and not an internal module. Compare against `requirements.txt`. Flag any third-party package that is imported but absent from `requirements.txt`.

**A6 — Duplicate Module Purpose (🟡 Medium)**
Check for module pairs that appear to serve the same purpose based on their names:
- `core/reasoning.py` vs `core/reasoning_engine.py`
- `core/observability.py` vs `core/observability_otel.py`
- `core/router.py` vs `core/smart_router.py` vs `core/quota_router.py`
- `core/memory.py` vs `core/memory_manager.py`
- `core/swarm.py` vs `core/swarm_engine.py`
- `core/cognition/` vs `core/cognitive/`
- `core/hyperdrive_cache.py` vs `core/shared_cache.py` vs `core/prompt_cache.py`

For each pair: check whether one imports the other (proper delegation), or whether they duplicate logic independently. If neither imports the other, flag as potential duplication.

---

### SECTION B: Shell Script Wiring

**B1 — Broken Python References in Shell Scripts (🔴 Critical)**
For every `.sh` file (root + `scripts/` + `crons/` + `git-hooks/` + `bin/`):
- Extract every `python3 some_file.py`, `python some_file.py`, `./some_file.py`, `bash some_script.sh`, `source some_script.sh`, and `./some_script.sh` call.
- Verify the referenced file exists at the stated path (relative to repo root or script location).
- Flag any reference to a non-existent file as **BROKEN SHELL REFERENCE**.

**B2 — `nina_sync.sh` Routing History Deduplication Guard (🔴 Critical)**
`nina_sync.sh` is the known source of the routing history duplication bug (see: commit `f3a2559`). Specifically:
- Locate the section of `nina_sync.sh` that writes to `NinaGate Routing History` (or equivalent primer/context file).
- Check whether the write is preceded by a deduplication guard (i.e., the script reads the last written entry and compares before appending).
- If no guard exists → flag as **MISSING DEDUP GUARD** with 🔴 Critical severity and provide the exact line range that needs fixing.
- If a guard exists → confirm it is functioning correctly (compare last entry hash/content against new content).

**B3 — Shell Script Executable Bit (🟢 Low)**
For every `.sh` file in the repo: check that the file has the executable bit set (`chmod +x`). Flag any `.sh` file lacking it.

**B4 — Shell Scripts Calling Each Other (🟡 Medium)**
Build a call graph of shell scripts that source or exec other shell scripts. Identify:
- Circular calls (A calls B calls A).
- Dead callers (script A calls script B, but script A itself is never called from any other shell, Makefile, `.service`, or workflow).

**B5 — `nina_update_log.md` Size Guard (🟠 High)**
- Count the number of lines in `nina_update_log.md`.
- If line count > 5000 → flag as **LOG RUNAWAY** and recommend a rotation/archival strategy.
- If line count > 10000 → flag as 🔴 Critical.
- Current known size: 264 KB. Track daily delta (compare against yesterday's report line count).

**B6 — `nina_sync.sh` — All File Write Targets (🟠 High)**
Parse `nina_sync.sh` for every file it writes to (via `>`, `>>`, `tee`, `echo ... >`, `cat > file`, etc.). Verify each write target path exists or is expected to be created. Flag writes to paths that are neither in `.gitignore` nor in the known repo structure.

---

### SECTION C: Service & Config Wiring

**C1 — Systemd `.service` File Entrypoints (🔴 Critical)**
For each of the three `.service` files:
- `nina.service` — extract `ExecStart=` value, verify the Python file or binary it references exists.
- `nina-dashboard.service` — same check.
- `ninajulesgithub.service` — extract `ExecStart=` and verify `ninajulesgithub.py` exists and is importable (check its own imports via A1).

**C2 — Makefile Target Coverage (🟡 Medium)**
Parse `Makefile` for all targets. For each target:
- Extract every shell command in the target body.
- Verify all Python files, scripts, and directories referenced in those commands exist.
- Flag any reference to a non-existent file.

**C3 — `pytest.ini` Test Path Coverage (🟡 Medium)**
Parse `pytest.ini` for `testpaths`. For each listed path, verify it exists in the repo. Flag any listed path that does not exist.

**C4 — `.github/workflows/` CI Wiring (🟠 High)**
For every `.yml` file in `.github/workflows/`:
- Extract `run:` steps that invoke Python files, shell scripts, or Makefile targets.
- Verify each referenced file exists.
- Flag any `uses:` action reference that is more than 2 major versions behind current (check against known action release tags where possible).

**C5 — Config Directory Completeness (🟡 Medium)**
List all files in `config/`. For each config file:
- Identify which Python module loads it (by searching for its filename in all `.py` files).
- If no Python module loads the config file → flag as **ORPHAN CONFIG**.
- Conversely, if a Python module references a config filename that does not exist in `config/` → flag as **MISSING CONFIG**.

---

### SECTION D: Data & Artefact Health

**D1 — Stale JSON Artefacts (🟡 Medium)**
Check the modification timestamp of:
- `call_graph_test.json` (93 KB) — if last modified > 7 days ago and no CI step regenerates it, flag as **STALE ARTEFACT**.
- `nina_context_graph.json` (20 KB) — same.
- `efficiency_report.json` — same.

**D2 — `juleslock.txt` Non-Empty (🟠 High)**
`juleslock.txt` should always be empty (0 bytes). If it contains any content, flag as **LOCK FILE DIRTY** — this indicates a Jules task may have crashed mid-execution without releasing the lock.

**D3 — `nina_commit_index.md` Duplication (🟡 Medium)**
Parse `nina_commit_index.md` for duplicate commit SHA entries (same SHA appearing more than once). Flag duplicates with line numbers.

**D4 — `CHANGELOG.md` vs Latest Commit Drift (🟢 Low)**
Compare the date of the most recent entry in `CHANGELOG.md` against the date of the latest commit on `main`. If the changelog is more than 3 days behind the latest commit, flag as **CHANGELOG STALE**.

**D5 — `.coverage` in Repo Root (🟢 Low)**
`.coverage` (53 KB) is a binary coverage database that should typically be in `.gitignore`. Verify it is listed in `.gitignore`. If it is not, flag and recommend adding it.

---

### SECTION E: NinaGate-Specific Wiring

**E1 — NinaGate Module Import Chain (🔴 Critical)**
The `ninagate/` directory is a critical routing layer. For every Python file in `ninagate/`:
- Run the same A1 (broken imports) check.
- Verify each file is reachable from the main NinaGate entrypoint (trace the import graph inward from the top-level `ninagate/__init__.py` or main entry file).

**E2 — NinaGate Primer File Duplication (🔴 Critical)**
The known bug: routing history blocks being appended without dedup. Check:
- The primer/context file that contains `NinaGate Routing History` (likely `nina_context.md` or a file inside `ninagate/`).
- Count the number of distinct date blocks (e.g., `[2026-06-18]`) vs the total number of routing history entries.
- If `total_entries / distinct_dates > 3` → flag as **ROUTING HISTORY BLOAT** and report the ratio.
- This check must run daily — track the ratio over time in the audit report.

**E3 — NinaGate Load Test Script Wiring (🟡 Medium)**
`ninagate_load_test.sh` (root level): verify all endpoints and addresses it hits are consistent with the current NinaGate config in `ninagate/` or `config/`.

---

### SECTION F: Cross-Cutting Discoverability

**F1 — Files Not in `.gitignore` That Should Be (🟡 Medium)**
Scan for the following file patterns that should be gitignored but may not be:
- `*.pyc`, `__pycache__/`, `.coverage`, `*.log`, `*.tmp`, `data/*.db`, `exports/*.json` (if auto-generated).
- Compare against current `.gitignore`. Flag any match that is present in the repo but absent from `.gitignore`.

**F2 — `.ninaignore` Alignment (🟡 Medium)**
`.ninaignore` controls what Nina sees in context. Verify its patterns do not accidentally exclude critical runtime files (e.g., `core/router.py`, `core/nina.py`, `main.py`). If any critical file matches a `.ninaignore` pattern → flag as **CRITICAL FILE IGNORED BY NINA**.

**F3 — `.geminiignore` Alignment (🟡 Medium)**
Same check as F2 but for `.geminiignore`. Gemini agent must not be ignoring files it needs to read for agent operations.

**F4 — Root-Level File Naming Consistency (🟢 Low)**
Nina's repo has two naming conventions: `nina_*.py` / `nina_*.sh` for Nina-owned scripts and `agy_*.py` / `agy_*.sh` for AGY-owned scripts. Detect any file at root that does not follow either convention and has no clear category home — flag for potential relocation.

**F5 — `healthcheck.py` Stub Detection (🟠 High)**
`healthcheck.py` is only 59 bytes. Read its content:
- If it contains only a `pass`, `print("ok")`, or a trivial stub → flag as **STUB HEALTHCHECK** (should be a real health check that exercises `core/nina.py` and `core/router.py`).
- If it is a real check → confirm it can be run standalone without side effects.

**F6 — `guardian` Binary vs `guardian_engine.py` (🟠 High)**
Root contains both a `guardian` file (27 KB, no extension — likely a compiled binary or shell script) and `guardian_engine.py` (79 KB). Check:
- What is `guardian`? Run `file guardian` equivalent (check shebang or magic bytes if readable).
- Does `guardian_engine.py` import or call `guardian`? Or vice versa?
- Is `guardian` referenced by any `.service`, Makefile, or workflow? If not → flag as **ORPHAN BINARY**.

---

## Output Format

Jules must write the audit report to:
```
docs/audit/YYYY-MM-DD_wiring_audit.md
```
where `YYYY-MM-DD` is today's date.

The report must use this exact structure:

```markdown
# Nina Wiring & Discoverability Audit — YYYY-MM-DD
**Run by:** Jules (scheduled daily task)
**Commit audited:** <HEAD SHA>
**Previous report:** docs/audit/YYYY-MM-DD_wiring_audit.md (yesterday)

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | N |
| 🟠 High | N |
| 🟡 Medium | N |
| 🟢 Low | N |
| ✅ Pass | N |

**Overall health:** HEALTHY / DEGRADED / CRITICAL

---

## Section A: Python Import Wiring
### A1 — Broken Imports
[findings or ✅ None found]

### A2 — Unused Imports
[findings or ✅ None found]

... (all sections A–F)

---

## Delta from Yesterday
[List any new findings that did not appear in yesterday's report]
[List any findings from yesterday that are now resolved]

---

## Action Items
[Numbered list of recommended fixes, highest severity first]
Each item must include: file path, line number if applicable, description of fix, and estimated effort (trivial/small/medium/large)
```

---

## Commit Instructions

After writing the report, Jules must commit it with:

```
git add docs/audit/YYYY-MM-DD_wiring_audit.md
git commit -m "audit(daily): wiring & discoverability report YYYY-MM-DD"
```

Jules must **not** auto-fix any findings. All fixes must be separate Jules tasks or PRs reviewed by @aibony.

Exception: if a finding is **severity 🟢 Low** AND involves only a documentation/comment update (not code) AND the fix is a single-line change → Jules may apply it directly in the same commit, appending `[auto-fixed: LOW]` to the commit message.

---

## Dependencies

Jules needs the following available in the environment:
- Python 3.10+ with `ast`, `pathlib`, `re`, `json` stdlib modules (no external deps for parsing)
- `git` CLI available
- Read access to all files in `aibony/nina` on the `main` branch
- Write access to `docs/audit/` directory (create if it does not exist)

---

## Notes for Jules

- **Do not skip sections** even if the previous run passed them cleanly. Run all checks every day — a section that passed yesterday can break from a single new commit.
- **Be precise with line numbers.** Every finding must cite the exact file path and line number. Vague findings like "router.py has issues" are not acceptable.
- **The routing history dedup check (B2 + E2) is the highest-priority daily check** based on known recurring history. Always run these first.
- **Do not modify `nina_sync.sh` directly.** Even if you find the dedup bug unfixed, report it — do not patch it. The patch requires careful testing of the full sync pipeline.
- **`guardian_engine.py` at 79 KB** is the largest single Python file. Orphan function detection (A3 equivalent) inside it should use AST class/function enumeration, not line-by-line grep.
- **Cross-reference `nina_wiring_audit.py`** (existing 8 KB script at root). Read it first — it may already perform some of these checks. Do not duplicate work; instead extend or call it where possible and note any gaps it does not cover.
- When computing the delta from yesterday's report, if no previous report exists → write "First run — no delta available."
