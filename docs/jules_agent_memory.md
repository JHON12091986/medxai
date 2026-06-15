# NINA Agent Memory (Consolidated)

This document consolidates NINA's agent memory files to streamline the repository layout while preserving all architecture, workflow, pattern, and runbook definitions.

---

## 1. NINA Current State & Active Focus

### Active Constraints
- NINA Sync blocks pushes when Jules PR branches are open.

### Open Risks and Gotchas
- **2026-06-08:** O-01: Playwright not installed (non-blocking)
- **2026-06-08:** O-02: EWS password not set (non-blocking)
- **2026-06-08:** O-04: memory context per-session refresh not implemented
- **2026-06-08:** O-05: FastAPI REST endpoints (api.py) — Phase 2, deferred

### Current Focus
- v14.2 Lightning Sync Release — Consolidation and high-throughput operations.
- Parallel execution monitoring and telemetry verification.
- **2026-06-12:** Unified 10 major PR clusters into a single stable kernel.

---

## 2. NINA Architecture

### Module Boundaries
- `core/`: Core orchestrator (`nina.py`), Agent loop (`agent.py`), Provider routing (`router.py`), Memory and capabilities.
- `tools/`: Executable actions (browsing, shell execution, system monitoring, file operations).
- `interfaces/`: External endpoints (Telegram bot, REST API).
- `crons/`: Scheduled jobs and managers.

### High-Risk / No-Touch Files
The following files default to local executor or manual local handling unless explicitly authorized. Never touch without explicit instruction:
- `interfaces/telegram_interface.py`
- `.env`
- `core/router.py`
- `main.py`
- `guardian_engine.py`
- `tools/shell.py`
- Any systemd unit files
- `nina_sync.sh` (unless documentation comments only)

### Tool Locations
- Dashboard: `dashboard/nina-guardian.html`
- Sync tool: `nina_sync.sh`
- Architect/CLI Toolset: `bin/ninaflash`

---

## 3. NINA Agent Patterns

### Backlog Protocol
- **Goal:** Keep tracking docs accurate.
- **Restraint:** NEVER use bash echo; NEVER update tracker from inside Jules.
- **Action:** `ninaflash` runs Python script post-merge to change status (`IN_PROGRESS` -> `DONE`), add PR number and date, then runs `./nina_sync.sh`.

### Task Tracker Update Protocol Example
```python
from pathlib import Path
tracker_path = Path("/home/aibony/nina/docs/space/jules_task_tracker.md")
content = tracker_path.read_text()
content = content.replace("... ⏳ QUEUED ...", "... ✅ MERGED ... PR #123 ...")
tracker_path.write_text(content)
```

### Logging Pattern
- **Goal:** Maintain accurate, structured update logs.
- **Restraint:** NEVER use heredoc or direct `bash echo >>` to `nina_update_log.md`.
- **Action:** Append log entries using Python. Auto-detect entry number, include date, title, changes, verifications, and rollback path.

### Surgical Merge Protocol (For Jules PRs)
- **Goal:** Prevent Jules PRs from overwriting local truths.
- **Restraint:** Do NOT merge Jules PRs blindly if they touch critical files (AGENTS.md, nina_sync.sh, nina_update_log.md).
- **Action:** Backup critical files -> merge PR -> restore regressions -> commit fix -> run `nina_sync.sh`.

---

## 4. NINA Runbooks & Recovery

### Stale Branches
- Prune stale remote refs before checking for PRs or sync blocks.
- If a Jules branch is stale, local executor should coordinate re-planning or discarding rather than blind rebasing.

### NINA Sync Failure
- What to do when `nina_sync.sh` refuses to push: Check if there are open Jules PR branches. NINA Sync blocks pushes when Jules PRs are active. Merge or close the PR first.

### Local/Remote Drift
- Always use the local repository as the single source of truth for full code implementation.
- If local and remote diverge, rollback procedures should start from clean `main` in `~/nina` and rely on checked-in codebase state rather than `.latest.md` snapshot.

---

### Surgical Merge Recovery

If a Jules PR was merged without surgical steps and caused a regression:

1. Identify what was overwritten:
   ```bash
   git log --oneline -10
   git diff HEAD~1 HEAD -- AGENTS.md nina_sync.sh nina_update_log.md
   ```

2. Recover from Google Drive backup:
   ```bash
   rclone copy gdrive:nina-backup/nina_latest.md ~/nina/docs/space/
   ```
   Or restore from: `/tmp/*.bak` (if the session is still active)

3. Restore manually if no backup available:
   ```bash
   git show HEAD~1:AGENTS.md > ~/nina/AGENTS.md
   git add AGENTS.md
   git commit -m "fix(agents): rollback regression from stale Jules PR"
   git push origin main
   ```

4. Run `nina_sync.sh` to re-sync state:
   ```bash
   cd ~/nina && ./nina_sync.sh
   ```

5. Add the regressed rule as an explicit "do not touch" note to `docs/jules_agent_memory.md` (formerly `docs/agent-memory/architecture.md`) for future Jules tasks.

---

## 5. NINA Agent Workflow

### Branch and PR Discipline
- **No direct commits to main.** `main` is the production-truth desk and must stay clean.
- Every active local executor or Jules task gets its own worktree/branch.
- Local executor default territory: `docs/space/*.md`, `AGENTS.md`, `nina_context.md`, `*.sh`, and single-file hotfixes on files not claimed by Jules.
- Jules default territory: multi-file work in `core/*.py`, `tools/*.py`, `interfaces/*.py`, `tests/*.py`.
- Shared but sequential only: `requirements.txt`, `data/*.json`.
- Forbidden parallel territory: `.env`, secrets, lock-sensitive runtime files.

### Sync Behavior
- **NINA Sync blocking:** Must block/defer pushes when Jules PR branches are open; prune stale remote refs before checking.
- The local executor runs `./nina_sync.sh` to deploy and export after every Jules PR merge.

### Rebase-Before-Work Rules
- Always rebase on origin/main before starting Jules tasks: `git fetch origin && git rebase origin/main`.

### Agent Coordination
- Local agents and Jules must NEVER edit the same file simultaneously.
- `jules_lock.txt` must always be read from and updated at the main worktree path: `~/nina/jules_lock.txt`.
- Per-task file territory must be explicit before parallel work begins.

---

### Surgical Merge Protocol (Mandatory for Jules PRs)

Jules is an async cloud agent that clones the repo at task-start time.
By the time Jules opens its PR, your local main may have moved ahead.
Merging Jules PRs blindly will frequently overwrite critical files (AGENTS.md, nina_sync.sh, nina_update_log.md, high-risk tools).

**Use surgical merge whenever a Jules PR touches any critical file.**

#### Critical files (always restore after a Jules PR merge):
- AGENTS.md
- nina_sync.sh
- nina_update_log.md
- tools/nina_dashboard.py
- tools/ninaflash.py
- interfaces/telegram_interface.py
- core/router.py
- main.py
- guardian_engine.py

#### Surgical merge procedure (do this every time):
1. Backup critical files from current main BEFORE merging:
   ```bash
   cp ~/nina/AGENTS.md /tmp/AGENTS.md.bak
   cp ~/nina/nina_sync.sh /tmp/nina_sync.sh.bak
   cp ~/nina/nina_update_log.md /tmp/nina_update_log.md.bak
   ```

2. Inspect the PR diff before merging:
   ```bash
   gh pr diff <PR_NUMBER> --stat
   ```
   Identify which files the PR changes vs which are regressions.

3. Merge the PR:
   ```bash
   gh pr merge <PR_NUMBER> --squash --delete-branch
   git pull origin main
   ```

4. Immediately restore any critical files that regressed:
   ```bash
   cp /tmp/AGENTS.md.bak ~/nina/AGENTS.md
   cp /tmp/nina_sync.sh.bak ~/nina/nina_sync.sh
   ```
   (only restore files that Jules incorrectly reverted)

5. Commit the restoration:
   ```bash
   git add <restored-files>
   git commit -m "fix(<scope>): restore <file> after PR #<N> surgical merge"
   git push origin main
   ```

6. Run `nina_sync.sh`:
   ```bash
   cd ~/nina && ./nina_sync.sh
   ```

#### When to use normal merge (no surgical steps needed):
- PR was based on very recent main (< 30 minutes old)
- PR only touches files Jules "owns": `core/*.py`, `tools/*.py`, `tests/*.py`
- PR does NOT touch any critical file in the list above
- `gh pr view` shows `mergeable_state: clean`

#### Rule to encode for all agents:
"Never merge a Jules PR that touches AGENTS.md, nina_sync.sh, or nina_update_log.md without first backing up the current main version and restoring it if the merge introduces a regression."

---

### 5.5 Four-Tool Operating Model — Parallel Execution

NINA uses three tools running IN PARALLEL as the standard operating mode:

| Tool | Role | Execution Mode |
|------|------|---------------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Active throughout — specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| Local Executor (ninaflash, Cursor, Claude Code, Cline, aider) | LOCAL MUSCLE | Sync local executor — edits, merges Jules PRs, deploys to service |

THE FULL PARALLEL LOOP:
1. Perplexity diagnoses + writes precise spec
2. Jules receives spec → builds in cloud async (no interaction after submit)
3. The local executor handles any urgent local fixes in parallel on its own worktree
4. Jules opens PR when done
5. The local executor reviews Jules PR diff, runs lint/compile checks, merges to main
6. The local executor runs `./nina_sync.sh` to deploy and export
7. Perplexity reviews result (attach `nina_latest.md` to new thread)

KEY DISTINCTION: The local executor is NOT just a fixer — it is the local merge and deploy executor.
Jules does NOT merge its own PRs — the local executor always performs the merge after review.
Perplexity is NOT idle during coding — it remains available for unblocking and mid-task review.

---

### 5.6 Task Routing Matrix
| Task / Scenario | Default Tool | Rationale | What NOT to Use |
|:---|:---:|:---|:---|
| Unclear bug / root-cause analysis | **Perplexity** | Deep context synthesis and cross-reference. | local executor or Jules (prone to blind code edits). |
| Blocker in high-risk runtime file | **local executor** | Immediate local safety checking and execution. | Jules (PR delay and merge conflict risk). |
| Single-file local fix | **local executor** | Fast local cycle, zero branch overhead. | Jules (too heavy for a quick patch). |
| Multi-file feature work | **Jules** | Syncs edits across multiple files via PRs. | local executor (risk of staging broad uncoordinated diffs). |
| Large refactor | **Jules** | Manages PR review process for high impact. | local executor (context limits on local CLI). |
| Post-change review | **Perplexity** | Objective validation against baseline design. | local executor or Jules. |
| Production-sensitive patch | **local executor** | Keeps secrets and banking parameters local. | Cloud providers or Jules. |

---

### Tool Routing Policy (2026-06-08)

#### Always-On Autocomplete (never disable)
- **Codeium** — VSCode extension, unlimited completions
- **Amazon Q Developer** — VSCode extension, unlimited inline

#### Decision Tree
1. Architecture / spec / GitHub MCP → **Perplexity** (Space)
2. Single-file scoped fix, urgent → **agy** (preserves other quotas)
3. Gemini CLI exhausted → **Qwen Code CLI** (Qwen3-Coder-480B, smarter model)
4. Async multi-module PR, can wait → **Jules** (Gemini 3.1 Pro, best quality)
5. All local quota gone → **Cursor Hobby** (50/month reserve)
6. Everything gone / offline → **Ollama + Continue.dev** (unlimited)

#### Quota Reference
| Tool | Model | Daily Quota | Reset |
|------|-------|-------------|-------|
| agy | gemini-2.5-flash | ~5h rolling | Rolling |
| Qwen Code CLI | Qwen3-Coder-480B | 2,000 req/day | Daily |
| Jules | Gemini 3.1 Pro | 100 tasks/day | Rolling 24h |
| Cursor Hobby | GPT-4o mini | 50 chat/month | Monthly |
| Copilot Free | GPT-4o | 50 chat/month | Monthly |

#### Quota Cascade Rule
Gemini CLI exhausted → Qwen Code → agy → Cursor → Jules (async) → Ollama
