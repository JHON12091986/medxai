# NINA Agent Context

## Pre-Code Reasoning Scaffold (All Agents — Mandatory)

Before writing any code, every agent must complete the following scaffold in order.
Skipping steps is not permitted. Writing code before step 7 is a violation.

=== NINA CODE SCAFFOLD — complete before writing ===

1. RESTATE — Write the task in your own words in one sentence. Do not copy-paste the prompt.

2. LOCATE — What existing file/function does this live near?
   Run: grep -r "<keyword>" ~/nina/core ~/nina/tools ~/nina/interfaces
   Never create a new pattern when an existing one fits.

3. CONSTRAINTS — List 3 things that must NOT break:
   - Response time must stay under 2s (agynina hard limit)
   - No new dependencies without explicit instruction
   - Must run on i5-8265U / MX150 — never assume GPU

4. FAILURE MODE FIRST — How does this fail? Write the error handler before the happy path.

5. MINIMAL SCOPE — What is the smallest change that solves this?
   If your answer touches more than 2 files, stop and ask.

6. PATTERN CHECK — Find one existing function in the repo that does something similar.
   Follow its exact style, naming, and error-handling pattern.

7. NOW write the code.

8. SELF-CHECK before committing:
   - Run: python3 -m py_compile <file> && pyflakes <file>
   - Run: agynina check code <file>
   - Does it match the pattern from step 6?
   - Would this work if RAM is at 9.5GB? (nina hw gate)

=== END SCAFFOLD ===

Meta-instruction (inject into every agent system prompt):
When writing code for NINA: reason before you act.
State what already exists. State what must not break.
Write the error path first. Write the minimum solution.
Then verify with agynina check code.
Never write more than what was asked.


## YOU ARE THE LOCAL EXECUTOR

This file is read by whichever local coding tool is active: agynina, Cursor, Claude Code, Cline, or aider. Regardless of which tool is active, your job is identical:
- Read only the required context files first.
- **Index-First Workflow (Mandatory Governance):**
  1. Consult the **Repository Index** (`docs/space/nina_index.md` / `.json`) or use `python3 tools/query_index.py --path <file>` before creating or modifying governed artifacts. Check `role`, `governed`, `duplicate_cluster_id`, and `guardrails`.
  2. **Obey Guardrails:**
     - If `high_risk_do_not_edit_directly`: Do not edit directly via CLI/script. Suggest a PR or request manual human review.
     - If `append_only`: Do not modify past content, only append to the end.
     - If `read_only_for_agents`: Strictly read-only for all automated tools. Do not write to these files.
  3. **Doc Delta Required:** If `query_index.py` indicates a Doc Delta is required, you MUST update `nina_update_log.md` (and any relevant backlog tracking docs) in the same PR or commit batch.
  4. If the file is part of a `duplicate_cluster_id`, you MUST ONLY write to the `canonical_path`.
  5. If creating, moving, renaming, archiving, or deleting a governed file, you must run `python3 tools/update_index.py`.
  6. Run `python3 tools/validate_index.py`. No PR or task touching governed paths is "Done" unless this validator passes. The index is the single enforceable contract for doc/log/code inventory.
  7. Run `./nina_audit.sh` to reconcile the local filesystem with Git and check for stale files.
  8. Run `python3 tools/generate_dashboard.py` to refresh the [Operational Governance Dashboard](docs/space/nina_governance_dashboard.md).
- Do not scan the whole repo before you know the task.
- Check juleslock.txt before editing.
- Follow the verify → log → sync workflow.
- Treat AGENTS.md as the shared operating law, not as agynina-specific instructions.

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
- **Developer CLI + Local Build Agent (Claude Sonnet 4.6 Thinking):** Antigravity CLI agynina v1.0.6
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

## Mandatory Verification — After Every Task (Local Executor)

1. **Syntax Check:** Run `python3 -m py_compile <file>` + `pyflakes <file>` on every changed file.
2. **Full Test Suite:** Run the complete test suite to ensure no regressions:
   `./venv/bin/python -m pytest tests/`
   (Note: Ensure all ~112 tests pass, or justify any known failures).

## Mandatory Rules — After Every Code Change (Local Executor)

- Run `python3 -m py_compile <file>` + `pyflakes <file>` on every changed file before committing
- Use conventional commits: `fix:` | `feat:` | `docs:` | `chore:` | `ops:` followed by `(ID)`
- One commit per logical fix — never bundle unrelated changes in one commit
- Stage specific files only — never `git add .`

## Mandatory Rules — After Every Task (Local Sync & Export)

- Append a log entry to `docs/logs/nina_update_log.md` using **Python only** — never heredoc, never bash echo
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

## Tool Routing Policy (2026-06-08)

### Always-On Autocomplete (never disable)
- **Codeium** — VSCode extension, unlimited completions
- **Amazon Q Developer** — VSCode extension, unlimited inline

### Decision Tree
1. Architecture / spec / GitHub MCP → **Perplexity** (Space)
2. Single-file scoped fix, urgent → **agy** (preserves other quotas)
3. Gemini CLI exhausted → **Qwen Code CLI** (Qwen3-Coder-480B, smarter model)
4. Async multi-module PR, can wait → **Jules** (Gemini 3.1 Pro, best quality)
5. All local quota gone → **Cursor Hobby** (50/month reserve)
6. Everything gone / offline → **Ollama + Continue.dev** (unlimited)

### Quota Reference
| Tool | Model | Daily Quota | Reset |
|------|-------|-------------|-------|
| agy | Gemini Flash | ~5h rolling | Rolling |
| Qwen Code CLI | Qwen3-Coder-480B | 2,000 req/day | Daily |
| Jules | Gemini 3.1 Pro | 100 tasks/day | Rolling 24h |
| Cursor Hobby | GPT-4o mini | 50 chat/month | Monthly |
| Copilot Free | GPT-4o | 50 chat/month | Monthly |

### Tool Rules
- agy: always start prompt with "Use the permanent JSON approval setting..."
- agy: one file at a time, sequential, never parallel
- Gemini CLI: use for speed-sensitive tasks and anything needing image/multimodal
- Qwen Code CLI: use for complex logic, deep refactors, when quality > speed
- Jules: fire-and-forget only — NOT a chat tool, always opens PR
- Jules PRs: always reviewed + merged by agy, never auto-merged
- After ANY merge: run ./nina_sync.sh — no exceptions

### Quota Cascade Rule
Gemini CLI exhausted → Qwen Code → agy → Cursor → Jules (async) → Ollama

---

### 1. Four-Tool Operating Model — Parallel Execution

NINA uses three tools running IN PARALLEL as the standard operating mode:

| Tool | Role | Execution Mode |
|------|------|---------------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Active throughout — specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| Local Executor (agynina, Cursor, Claude Code, Cline, aider) | LOCAL MUSCLE | Sync local executor — edits, merges Jules PRs, deploys to service |

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

### 9. Antigravity CLI Toolset (agynina)
Every local executor should use the automated `agynina` CLI toolset (located at `bin/agynina`) to run standard workflows:
- **`agynina status`**: Checks active file locks, git workspace, and backlog status.
- **`agynina pr merge <PR_NUMBER>`**: Automatically runs syntax/linter checks on the PR, merges it, updates the backlog status to `DONE`, clears locks, and triggers the sync script.
- **`agynina dispatch <TASK_ID>`**: Locks target files in `jules_lock.txt`, sets status to `IN_PROGRESS`, and sends task spec to the Jules API.
- **`agynina aider <TASK_ID>`**: Launches `aider` preloaded with the task's files in the LLM context.
- **`agynina doctor`**: Locates and prints the most recent Python traceback from NINA's logs or systemd journal.
- **`agynina ninaloop`**: Activates the continuous autonomous developer loop.

---

## Parallel Workflow — Synergic Model

### Core principle
- True parallel work is allowed only through separate git branches and separate git worktrees.
- `main` is the production-truth desk and must stay clean.
- The local executor and Jules must never edit the same file at the same time.
- File territory is mandatory, not advisory.

### Branch lanes
- `main` → production truth, review, merge, sync only
- `local/<task-id>-<slug>` (or `agynina/` / `aider/`) → local docs, shell, single-file hotfixes, policy work
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

## Task Tracker Update Protocol
After every Jules PR is merged, agynina updates `~/nina/docs/space/jules_task_tracker.md` using Python only — never bash echo.

Fields to update:
- Change status from `IN_PROGRESS` to `DONE`
- Add PR number (e.g., `PR #123`)
- Add merged date (e.g., `2026-06-08`)

Rules:
- Never update tracker from inside Jules — only agynina does tracker updates post-merge.
- Run `./nina_sync.sh` after every tracker update.

Example Python update block:
```python
from pathlib import Path

tracker_path = Path("/home/aibony/nina/docs/space/jules_task_tracker.md")
content = tracker_path.read_text()
# Replace the old table row with the updated table row
content = content.replace(
    "| ASYNC-03 | B-002: Wire model_overrides dict to .env hot-reload in router.py | ⏳ QUEUED | 2026-06-07 | — | — | Session: [13876164946786086522](https://jules.google.com/session/13876164946786086522) |",
    "| ASYNC-03 | B-002: Wire model_overrides dict to .env hot-reload in router.py | ✅ MERGED | 2026-06-07 | PR #123 | E-062 | Session: [13876164946786086522](https://jules.google.com/session/13876164946786086522) |"
)
tracker_path.write_text(content)
```
