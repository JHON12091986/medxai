# NINA Agent Context

## YOU ARE THE LOCAL EXECUTOR

This file is read by whichever local coding tool is active: agy, Cursor, Claude Code, Cline, or aider. Regardless of which tool is active, your job is identical:
- Read only the required context files first.
- Do not scan the whole repo before you know the task.
- Check juleslock.txt before editing.
- Follow the verify → log → sync workflow.
- Treat AGENTS.md as the shared operating law, not as agy-specific instructions.

## NINA Identity Directive — Agentic, Not a Chatbot

NINA is a personal autonomous agent. She is NOT a chatbot.

This directive applies to every task, every file, every PR in this repository:
- NINA takes actions. She does not narrate intentions.
- NINA completes tasks end-to-end. She does not pause for confirmation unless the action is 
  irreversible.
- NINA uses free-tier routing intelligence (Pollinations, Chutes, Groq, Gemini, Cerebras, etc.) 
  to deliver full agentic capability without paid AI subscriptions.
- Every feature built for NINA must serve her agentic mission: tools that act, memory that 
  persists, routing that executes.
- Chatbot-style features (explain yourself, ask before acting, summarize what you might do) are 
  explicitly out of scope unless the user requests them.

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
- Before starting any local executor task, check ~/nina/jules_lock.txt. If the file you need to edit is listed under LOCKED_FILES, stop and report: Jules is currently modifying that file. Do not proceed.

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

## Mandatory Rules — After Every Code Change (Local Executor)

- Run `python3 -m py_compile <file>` + `pyflakes <file>` on every changed file before committing
- Use conventional commits: `fix:` | `feat:` | `docs:` | `chore:` | `ops:` followed by `(ID)`
- One commit per logical fix — never bundle unrelated changes in one commit
- Stage specific files only — never `git add .`

## Mandatory Rules — After Every Task (Local Sync & Export)

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

**Principle:** _Perplexity plans, the local executor stabilizes, Jules builds._

### 1. Four-Tool Operating Model — Parallel Execution

NINA uses three tools running IN PARALLEL as the standard operating mode:

| Tool | Role | Execution Mode |
|------|------|---------------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Active throughout — specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| Local Executor (agy, Cursor, Claude Code, Cline, aider) | LOCAL MUSCLE | Sync local executor — edits, merges Jules PRs, deploys to service |
| aider-chat (./nina-aider.sh) | INTERACTIVE LOCAL CODER — interactive multi-file editing with full repo context via OpenRouter. Use when iterating live with direct file edits and needing conversational pair-programming. Requires terminal presence. | Interactive sync |

THE FULL PARALLEL LOOP:
1. Perplexity diagnoses + writes precise spec
2. Jules receives spec → builds in cloud async (no interaction after submit)
3. The local executor handles any urgent local fixes in parallel on its own worktree
4. Jules opens PR when done
5. The local executor reviews Jules PR diff, runs lint/compile checks, merges to main
6. The local executor runs ./nina_sync.sh to deploy and export
7. Perplexity reviews result (attach nina_latest.md to new thread)

KEY DISTINCTION: The local executor is NOT just a fixer — it is the local merge and deploy executor.
Jules does NOT merge its own PRs — the local executor always performs the merge after review.
Perplexity is NOT idle during coding — it remains available for unblocking and mid-task review.

### 2. Task Routing Matrix
| Task / Scenario | Default Tool | Rationale | What NOT to Use |
|:---|:---:|:---|:---|
| Unclear bug / root-cause analysis | **Perplexity** | Deep context synthesis and cross-reference. | local executor or Jules (prone to blind code edits). |
| Blocker in high-risk runtime file | **local executor** | Immediate local safety checking and execution. | Jules (PR delay and merge conflict risk). |
| Single-file local fix | **local executor** | Fast local cycle, zero branch overhead. | Jules (too heavy for a quick patch). |
| Multi-file feature work | **Jules** | Syncs edits across multiple files via PRs. | local executor (risk of staging broad uncoordinated diffs). |
| Large refactor | **Jules** | Manages PR review process for high impact. | local executor (context limits on local CLI). |
| Post-change review | **Perplexity** | Objective validation against baseline design. | local executor or Jules. |
| Production-sensitive patch | **local executor** | Keeps secrets and banking parameters local. | Cloud providers or Jules. |

### 3. Hard Routing Rules
- **Diagnosis First:** Perplexity must be used to draft specs when a bug or requirement is unclear. Do not code blindly.
- **High-Risk Priority:** The local executor is the default route for high-risk files and urgent runtime fixes.
- **Backlog & PR Only:** Jules must only be used for async, multi-module PR-based backlog work.
- **Concurrency Locks:** Never let Jules touch locked files. Never let the local executor proceed if `jules_lock.txt` indicates a file is locked.
- **Grounded Advice:** Perplexity must not suggest concrete edits unless target source code is directly attached or included in the current thread context.
- **Sensitive Paths:** All banking-sensitive paths must route through LOCAL execution only.
- Use aider-chat for interactive pair-programming sessions (live multi-file edits, iterative idea exploration). Launch via ./nina-aider.sh from ~/nina.
- Do NOT use aider for async fire-and-forget tasks — use Jules for those.
- aider must never touch .env, juleslock.txt, or high-risk runtime files without explicit instruction.
- aider sessions must be followed by ./nina_sync.sh — no exceptions.

### 4. Context Model
- **`nina_latest.md`:** Bird's-eye operational snapshot only. Used for system awareness, not full raw code recovery.
- **Source Attachments:** Attach exact source file contents when asking Perplexity for code-level suggestions.
- **Local Truth:** The local repository remains the single source of truth for full code implementation.

### 5. Session Workflow
1. **Perplexity** diagnoses the issue and creates the task brief.
2. **Local executor** (local) or **Jules** (PR-based) executes the implementation.
3. Local **Verification** (compile/linter/smoke tests) runs.
4. **Perplexity** reviews the resulting diff.
5. **sync/export** runs to commit, push, and close the session.

### 6. High-Risk Default Route
The following files must default to **local executor** or manual local handling unless explicitly authorized:
- `main.py`
- `core/router.py`
- `interfaces/telegram_interface.py`
- `guardian_engine.py`
- `tools/shell.py`
- `.env`

### 7. Failure Modes to Avoid
- **Blind Editing:** Treating Perplexity as a blind code editor without in-context file attachments.
- **Slow Pipeline:** Routing urgent runtime fixes through Jules' PR pipeline.
- **Staging Spam:** Using the local executor for broad, unstructured multi-file refactors.
- **Lock Race:** Starting work without checking the active lock state in `jules_lock.txt`.
- **Bundled Changes:** Stacking unrelated modifications in a single commit.
- **Restore Confusion:** Treating the backup snapshot (`nina_latest.md`) as a repository recovery mechanism.

### 8. Local Executor as Merge Executor (Mandatory)
- The local executor is responsible for ALL Jules PR merges — never auto-merge Jules PRs via GitHub UI
- Before merging: run `python3 -m py_compile` on changed files, run `pyflakes`, check `jules_lock.txt`
- After merging: run `./nina_sync.sh` — no exceptions
- If merge conflict: stop, report to Perplexity for re-spec, do not attempt blind resolution

---

## Parallel Workflow — Synergic Model

### Core principle
- True parallel work is allowed only through separate git branches and separate git worktrees.
- `main` is the production-truth desk and must stay clean.
- The local executor and Jules must never edit the same file at the same time.
- File territory is mandatory, not advisory.

### Branch lanes
- `main` → production truth, review, merge, sync only
- `local/<task-id>-<slug>` (or `agy/` / `aider/`) → local docs, shell, single-file hotfixes, policy work
- `jules/<task-id>-<slug>` → multi-file features, refactors, async PR builds
- Optional `review/<id>` → isolated test/review/merge prep

### Worktree rules
- Every active local executor or Jules task gets its own worktree.
- Recommended folder pattern:
  - `~/nina` → main
  - `~/nina/.worktrees/local-<task-id>`
  - `~/nina/.worktrees/jules-<task-id>`
- Never run parallel agent tasks from the same working directory.

### Territory rules
- Local executor default territory: `docs/space/*.md`, `AGENTS.md`, `nina_context.md`, `*.sh`, and single-file hotfixes on files not claimed by Jules.
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
5. Launch local executor and Jules only after territories are confirmed non-overlapping.

### Session close checklist
1. The local executor commits only its branch/worktree.
2. Jules opens PR only from its branch/worktree.
3. Review and merge one stream at a time into `main`.
4. Pull updated `main` into remaining worktrees before further edits.
5. Run `./nina_sync.sh` from `main`.
6. Remove finished worktrees.

### Stop conditions
- If either tool needs a file already claimed by the other, stop and re-plan.
- If merge conflict risk appears, pause parallelism and integrate first.
- Never bypass review by pushing direct overlapping edits into `main`.

## Backlog Protocol
After every successful PR merge, update ~/nina/docs/space/jules_backlog.md:
change the item's status from READY or IN_PROGRESS to DONE.
Add PR number and date. Use Python file write — never bash echo.
