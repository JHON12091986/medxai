# NINA Agent Context

NINA is a self-hosted personal AI assistant running on Ubuntu 26.04 via systemd.
Python 3.14, asyncio-based. Repo: github.com/aibony/nina

## Dev Environment Stack
- **AI Tooling:** Perplexity Enterprise Pro with Claude Sonnet 4.6
- **Developer CLI + Local Build Agent (Claude Sonnet 4.6 Thinking):** Antigravity CLI agy v1.0.5
- **Primary Developer Agent:** Jules at jules.google
- **Reference & Search:** NotebookLM
- **Note:** Gemini CLI was removed on June 5, 2026.

## Key Files
- core/router.py — HybridRouter V4, CircuitBreaker, 19+ providers
- core/agent.py — AgentLoop, THINK-PLAN-ACT, thermal guard
- core/nina.py — NinaOS orchestrator
- interfaces/telegram_interface.py — Telegram bot, security gate
- guardian.sh + guardian_engine.py — forensic health check

## Rules for Jules
- Do NOT pause for confirmation at any point. Complete all batches sequentially without asking for feedback. Open the PR when done.
- Proceed immediately to the next batch without waiting for approval.
- Never use `git add .` — stage specific files only
- Run `python3 -m py_compile <file>` before any commit
- One purpose per patch, assign an ID (R-xx or G-xx)
- Never touch .env or hardcode secrets
- All fixes must be recoverable (git commit before changing)
- Before starting any agy task, check ~/nina/jules_lock.txt. If the file you need to edit is listed under LOCKED_FILES, stop and report: Jules is currently modifying that file. Do not proceed.

## Guardian Gate (Mandatory)
- Every patch must pass: `python3 -m py_compile <file>` + `pyflakes <file>`
- Never bundle unrelated changes in one commit
- Sensitive tasks route LOCAL only — never add cloud provider calls to agent.py sensitive path
- Do not modify: .env, data/memory/facts.json, upgrades/guardian_baseline.json
- Do not remove or weaken shell allowlist in tools/shell.py

## Current Open Issues
- O-01: Playwright not installed (non-blocking)
- O-02: EWS password not set (non-blocking)
- O-04: memory context per-session refresh not implemented
- O-05: FastAPI REST endpoints (api.py) — Phase 2, deferred

## Test Command After Every Change
cd ~/nina && source venv/bin/activate && python3 -m py_compile <changed_file> && pyflakes <changed_file>

Alternatively, you can use the developer helper Makefile:
- `make check` — Runs `py_compile` and `pyflakes` automatically on all modified `.py` files.
- `make test` — Runs pytest on the `tests/` directory (if tests exist).

## Mandatory Rules — After Every Code Change (agy)

- Run `python3 -m py_compile <file>` + `pyflakes <file>` on every changed file before committing
- Use conventional commits: `fix:` | `feat:` | `docs:` | `chore:` | `ops:` followed by `(ID)`
- One commit per logical fix — never bundle unrelated changes in one commit
- Stage specific files only — never `git add .`

## Mandatory Rules — After Every Task (agy close)

- Append a log entry to `nina_update_log.md` using **Python only** — never heredoc, never bash echo
  - Auto-detect the next entry number from the file
  - Include: entry number, date, title, what changed, what was verified, rollback path
- Run `cd ~/nina && ./nina_sync.sh` — no exceptions
- Before inserting any content into a file, grep the target file to confirm that content does not already exist. If it does, skip the insertion.
- After completing a task that touches .py files, update ~/nina/jules_lock.txt LOCKED_FILES= with the files you just changed, so Jules avoids overwriting them.

## High-Risk Files — Never Touch Without Explicit Instruction in the Prompt

- `interfaces/telegram_interface.py`
- `.env`
- `core/router.py`
- `main.py`
- `guardian_engine.py`
- `tools/shell.py`

## Never Do

- Write log entries with heredoc (`<< 'EOF'`) or direct `bash echo >>` — always use Python
- Auto-merge Jules PRs — all Jules PRs require explicit review and approval
- Bundle multiple unrelated fixes in one commit

---

## NINA Tool Routing Policy v2

**Principle:** _Perplexity plans, agy stabilizes, Jules builds._

### 1. Three-Tool Operating Model
- **Perplexity Enterprise Pro (THINK):** Diagnosis, root-cause analysis, architecture design, prompt-spec writing, and code review.
- **Antigravity CLI (agy) (LOCAL-BUILD):** Scoped single-file or tightly bounded runtime-safe edits, urgent fixes, and deployment.
- **Google Jules (BUILD):** Async multi-file implementation, broad refactors, and PR-based backlog work.

### 2. Task Routing Matrix
| Task / Scenario | Default Tool | Rationale | What NOT to Use |
|:---|:---:|:---|:---|
| Unclear bug / root-cause analysis | **Perplexity** | Deep context synthesis and cross-reference. | agy or Jules (prone to blind code edits). |
| Blocker in high-risk runtime file | **agy** | Immediate local safety checking and execution. | Jules (PR delay and merge conflict risk). |
| Single-file local fix | **agy** | Fast local cycle, zero branch overhead. | Jules (too heavy for a quick patch). |
| Multi-file feature work | **Jules** | Syncs edits across multiple files via PRs. | agy (risk of staging broad uncoordinated diffs). |
| Large refactor | **Jules** | Manages PR review process for high impact. | agy (context limits on local CLI). |
| Post-change review | **Perplexity** | Objective validation against baseline design. | agy or Jules. |
| Production-sensitive patch | **agy** | Keeps secrets and banking parameters local. | Cloud providers or Jules. |

### 3. Hard Routing Rules
- **Diagnosis First:** Perplexity must be used to draft specs when a bug or requirement is unclear. Do not code blindly.
- **High-Risk Priority:** agy is the default route for high-risk files and urgent runtime fixes.
- **Backlog & PR Only:** Jules must only be used for async, multi-module PR-based backlog work.
- **Concurrency Locks:** Never let Jules touch locked files. Never let agy proceed if `jules_lock.txt` indicates a file is locked.
- **Grounded Advice:** Perplexity must not suggest concrete edits unless target source code is directly attached or included in the current thread context.
- **Sensitive Paths:** All banking-sensitive paths must route through LOCAL execution only.

### 4. Context Model
- **`nina_latest.md`:** Bird's-eye operational snapshot only. Used for system awareness, not full raw code recovery.
- **Source Attachments:** Attach exact source file contents when asking Perplexity for code-level suggestions.
- **Local Truth:** The local repository remains the single source of truth for full code implementation.

### 5. Session Workflow
1. **Perplexity** diagnoses the issue and creates the task brief.
2. **agy** (local) or **Jules** (PR-based) executes the implementation.
3. Local **Verification** (compile/linter/smoke tests) runs.
4. **Perplexity** reviews the resulting diff.
5. **sync/export** runs to commit, push, and close the session.

### 6. High-Risk Default Route
The following files must default to **agy** or manual local handling unless explicitly authorized:
- `main.py`
- `core/router.py`
- `interfaces/telegram_interface.py`
- `guardian_engine.py`
- `tools/shell.py`
- `.env`

### 7. Failure Modes to Avoid
- **Blind Editing:** Treating Perplexity as a blind code editor without in-context file attachments.
- **Slow Pipeline:** Routing urgent runtime fixes through Jules' PR pipeline.
- **Staging Spam:** Using agy for broad, unstructured multi-file refactors.
- **Lock Race:** Starting work without checking the active lock state in `jules_lock.txt`.
- **Bundled Changes:** Stacking unrelated modifications in a single commit.
- **Restore Confusion:** Treating the backup snapshot (`nina_latest.md`) as a repository recovery mechanism.

---

## Parallel Workflow — Synergic Model

### Core principle
- True parallel work is allowed only through separate git branches and separate git worktrees.
- `main` is the production-truth desk and must stay clean.
- agy and Jules must never edit the same file at the same time.
- File territory is mandatory, not advisory.

### Branch lanes
- `main` → production truth, review, merge, sync only
- `agy/<task-id>-<slug>` → local docs, shell, single-file hotfixes, policy work
- `jules/<task-id>-<slug>` → multi-file features, refactors, async PR builds
- Optional `review/<id>` → isolated test/review/merge prep

### Worktree rules
- Every active agy or Jules task gets its own worktree.
- Recommended folder pattern:
  - `~/nina` → main
  - `~/nina/.worktrees/agy-<task-id>`
  - `~/nina/.worktrees/jules-<task-id>`
- Never run parallel agent tasks from the same working directory.

### Territory rules
- agy default territory: `docs/space/*.md`, `AGENTS.md`, `nina_context.md`, `*.sh`, and single-file hotfixes on files not claimed by Jules.
- Jules default territory: multi-file work in `core/*.py`, `tools/*.py`, `interfaces/*.py`, `tests/*.py`.
- Shared but sequential only: `requirements.txt`, `data/*.json`.
- Forbidden parallel territory: `.env`, secrets, lock-sensitive runtime files.

### Concurrency & Environment Refinements
- **Virtual Environment Sharing:** All worktrees must use the primary venv located at `~/nina/venv/bin/activate`. Never create separate virtual environments in worktree folders.
- **Centralized Lock Truth:** `jules_lock.txt` must always be read from and updated at the main worktree path: `~/nina/jules_lock.txt`. Do not rely on local worktree branch lock states.
- **Local State Verification:** Divergent worktree state files (e.g. `data/memory/facts.json`) must be sequentially verified and merged on integration.

### Session start checklist
1. Start from clean `main` in `~/nina`.
2. Run `./nina_sync.sh`.
3. Create branch + worktree for each task.
4. Record claimed files in the centralized `~/nina/jules_lock.txt`.
5. Launch agy and Jules only after territories are confirmed non-overlapping.

### Session close checklist
1. agy commits only its branch/worktree.
2. Jules opens PR only from its branch/worktree.
3. Review and merge one stream at a time into `main`.
4. Pull updated `main` into remaining worktrees before further edits.
5. Run `./nina_sync.sh` from `main`.
6. Remove finished worktrees.

### Stop conditions
- If either tool needs a file already claimed by the other, stop and re-plan.
- If merge conflict risk appears, pause parallelism and integrate first.
- Never bypass review by pushing direct overlapping edits into `main`.
