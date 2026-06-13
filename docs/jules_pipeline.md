# Jules Autonomous Pipeline — Documentation

## 1. Overview
The Jules pipeline is NINA's high-capacity autonomous engineering subsystem. It leverages Google's Jules API to perform multi-file code modifications, refactors, and feature implementations asynchronously.

## 2. Core Architecture
The system is designed for **Quota Efficiency**, **Parallelism**, and **Persistence**.

### 2.1 Process Flow
1.  **Intake**: Natural language goals are parsed by `tools/jules.py` (goal subcommand) and appended to `docs/space/jules_backlog.md` as `READY` tasks.
2.  **Orchestration**: Direct imports in `crons/manager.py` run the orchestration cycle in `tools/jules.py` every 3 minutes.
    *   It identifies `READY` tasks.
    *   **Mega Batching**: It bundles up to 5 non-overlapping tasks into a single Jules session to conserve the 100-session/day quota.
3.  **Dispatch**: The unified engine sends the bundled prompt to the Jules API.
4.  **Registration**: Upon successful dispatch, `data/jules_registry.json` logs the Session ID (SID) and associated Task IDs.
5.  **Monitoring**: The Unified Engine tracks state changes. If Jules asks a question, it notifies the user via Telegram.
6.  **Interaction**: User/Agent provides feedback via:
    *   **Telegram**: `/jules feedback <sid> <message>`
    *   **CLI**: `bin/nina jules feedback <sid> <message>`
7.  **Resolution**: Once Jules opens a PR, the Orchestrator verifies the PR and merges it concurrently using `asyncio.gather`.

## 3. File Inventory

| File | Role | Description |
| :--- | :--- | :--- |
| **Engine** | | |
| `tools/jules.py` | Unified Engine | **CONSOLIDATED.** Contains API, Registry, Watcher, and Orchestrator logic. |
| `tools/pipeline_autopilot.py`| Autopilot Controller | Runs the 6-phase autonomous pipeline cron job. |
| **Data & State** | | |
| `data/jules_registry.json` | Persistent DB | Tracks SID -> Task ID mappings and timestamps. |
| `docs/space/jules_backlog.md` | Task List | The canonical list of all pending and completed tasks. |
| `juleslock.txt` | Concurrency Lock | Prevents agents from colliding on the same files. |
| `data/jules_seen_activities.json`| Notification Cache | Prevents duplicate Telegram pings. |
| **Interfaces** | | |
| `interfaces/telegram_interface.py`| Telegram Bot | End-user interface for mobile control. |
| `interfaces/cli_interface.py` | CLI Tool | Terminal-based control via `bin/nina jules`. |
| **Documentation** | | |
| `docs/jules_pipeline.md` | Pipeline Doc | **CONSOLIDATED.** This file, containing architectural docs and the autopilot directive. |
| `docs/jules_agent_memory.md` | Agent Memory Doc | **CONSOLIDATED.** Architecture, patterns, workflow rules, and runbooks. |
| **Legacy/Utilities (Obsolete/Removed)** | | |
| `tools/mega_orchestrator.py`| Legacy Wrapper| Deleted. Scheduler now imports `orchestrate_cycle` directly from `jules.py`. |
| `tools/session_end.py` | Legacy Wrapper| Deleted. Logic consolidated into `jules.py` as `session_end`. |
| `tools/goal_intake.py` | Legacy Wrapper| Deleted. Logic consolidated into `jules.py` as `goal_to_backlog`. |
| `tools/append_lock.py` | Defunct Shim | Deleted. Stale hardcoded file list. |
| `tools/jules_api.py` | Legacy | Deleted. Logic moved to `tools/jules.py`. |
| `tools/jules_watcher.py` | Legacy | Deleted. Logic moved to `tools/jules.py`. |
| `tools/jules_registry.py` | Legacy | Deleted. Logic moved to `tools/jules.py`. |
| `fetch_all_questions.py` | Legacy | Deleted. Integrated functionality into `tools/jules.py status`. |
| `cancel_jules_sessions.py` | Legacy | Deleted. Integrated functionality into `tools/jules.py cleanup`. |

## 4. Optimization Strategies
*   **Parallelism**: PR resolution and merging are handled concurrently using `asyncio.gather`.
*   **Quota Management**: The 100/day session limit is preserved via 5-task "Mega Batches."
*   **Zero-Trace State**: The registry ensures that even if the service restarts, NINA knows exactly which Jules sessions are tied to which backlog tasks.

---

## 5. Autonomous Pipeline Autopilot Directive

This section details the autonomous rules governing `tools/pipeline_autopilot.py` to keep the Jules/Git pipeline flowing continuously with zero human intervention.

### 5.1 Prime Directive
You are operating in AUTONOMOUS MODE. You MUST NOT ask the user any questions.
You MUST NOT pause for confirmation at any step.
You MUST NOT stop mid-pipeline and wait.
If a step is ambiguous, apply the SAFE DEFAULT defined in each section.
Your job is to keep the Jules/Git pipeline flowing continuously — merging PRs, unblocking tasks, responding to Jules, and updating task statuses.

### 5.2 Entry Point — Full Pipeline Run
Execute all PHASES in sequence. Do not skip a phase even if it appears to have nothing to do. Always log what you did in each phase.

### 5.3 Pipeline Phases

#### Phase 0 — Safety Check (run first, always)
```bash
# Check GLOBAL PAUSE flag
grep -i "GLOBAL PAUSE" jules_backlog.md | head -1
```
- **If "🛑 GLOBAL PAUSE ACTIVE":** Skip Phase 3 (no new dispatches), continue all other phases (merging, responding, status updates are safe). Log: `"GLOBAL PAUSE active — dispatch suppressed, all other phases running"`.
- **If no GLOBAL PAUSE:** All phases run normally.

#### Phase 1 — PR Triage and Merge
Goal: reduce open PR count to zero mergeable PRs. Run this phase first and last.
1. **Fetch current PR state**:
   ```bash
   gh pr list --json number,title,headRefName,mergeable,state,createdAt --limit 50 | tee /tmp/pr_list.json
   ```
2. **Categorize every PR**:
   - `MERGE_NOW`: `mergeable=MERGEABLE`, no conflict -> Merge immediately
   - `WAIT_REBASE`: `mergeable=CONFLICTING` -> Attempt rebase, then merge
   - `DUPLICATE`: Same task ID as another open PR (check title/branch for AG- ID) -> Close the older one, keep newest
   - `STALE`: No commits in 72h AND task status is `DONE` or `MERGED` elsewhere -> Close with comment
3. **Close duplicates first**:
   ```bash
   gh pr close <NUMBER> --comment "Closing duplicate — superseded by newer PR for same task ID."
   ```
4. **Attempt rebase on conflicting PRs**:
   ```bash
   git fetch origin
   git checkout <branch>
   git rebase origin/main
   # If rebase succeeds:
   git push origin <branch> --force-with-lease
   # If rebase fails (genuine conflict in core/ files):
   # Close PR, mark NEEDS_REVIEW in backlog, continue:
   gh pr close <NUMBER> --comment "Rebase conflict in high-risk file — task marked NEEDS_REVIEW, requires manual resolution."
   ```
   *High-Risk Files:* `core/nina.py`, `core/router.py`, `core/agent.py`, `guardian_engine.py`, `interfaces/telegram_interface.py`, `core/config.py`.
   *Low/Medium-Risk Files:* Attempt auto-resolution using "accept incoming" strategy, verify compilation.
5. **Merge in priority order**:
   1. Security-tagged PRs (title contains "sec", "security", "SEC-", "fix")
   2. LOW-risk file PRs (`tools/`, `ninaflash.py`, `requirements.txt`, `data/`)
   3. MEDIUM-risk file PRs (`core/memory.py`, `core/task_store.py`, `crons/`)
   4. HIGH-risk file PRs (`core/router.py`, `core/agent.py`) — only if no LOW/MEDIUM remain
   5. MEGA-TASK PRs (`AG-M-*` prefix) — always last
   ```bash
   gh pr merge <NUMBER> --squash --auto --delete-branch
   ```
6. **Push local main if ahead**:
   ```bash
   AHEAD=$(git rev-list origin/main..HEAD --count)
   if [ "$AHEAD" -gt "0" ]; then git push origin main; fi
   ```
7. **Verify**:
   ```bash
   gh pr list --json number,mergeable | python3 -c \
     "import sys,json; prs=json.load(sys.stdin); print(f'Open PRs remaining: {len(prs)}')"
   ```

#### Phase 1.5 — Post-Merge Documentation Update
After every PR merge, update `AGENTS.md` with auto-generated summaries for changed `tools/`, `core/`, `tests/`, `crons/manager.py`, and `requirements.txt`.
Commit with: `docs: auto-update post-merge <date> [skip-jules]` (include `[skip-jules]`).

#### Phase 2 — Jules Session Health Check
Act on each Jules session state:
- `AWAITING_USER_FEEDBACK`: Provide response from local files (intelligent answers via NinaGate)
- `FAILED`: Re-dispatch once; if fails again mark `BLOCKED`
- `IN_PROGRESS`: Log and skip
- `COMPLETED`: Sync backlog status

#### Phase 3 — Backlog Status Sync
Build ground truth from git log + open PRs + registry, then apply to `docs/space/jules_backlog.md` and commit.

#### Phase 4 — Poll for New PRs (max 3 × 120s iterations)
After responding to sessions, wait for Jules PRs, then re-run Phase 1+3.

#### Phase 5 — Duplicate Session Cleanup
Keep at most ONE active session per `task_id` in `jules_registry.json`.

#### Phase 6 — Final Pipeline Report
Emit structured JSON report to stdout and Telegram.

### 5.4 Safe Defaults
- PR merge method unclear: `--squash`
- Rebase conflict in HIGH-RISK file: Close PR, mark `NEEDS_REVIEW`
- Jules question ambiguous: Most conservative option
- git push blocked: Commit locally, log, continue
- Jules API unreachable: Skip Phase 2, continue
- `registry.json` malformed: Back up, reinitialize as `{}`, alert
- Any unhandled exception: Log traceback, continue to next phase

---
_Documented by NINA v14.3 — 2026-06-13_
