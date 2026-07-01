# NINA Operational AI Snapshot — 2026-06-07 13:17:49
_Generated: 2026-06-07 13:17:49 | Repo: github.com/aibony/nina | Branch: main | Python: 3.14.4_
_Purpose: AI context snapshot for Perplexity Space_
_Target size: Compact, low-noise context (~200KB-300KB)_

---

## SESSION START CHECKLIST (Perplexity)
Before opening a new Perplexity thread:
1. cd ~/nina && ./nina_sync.sh  (generates fresh nina_latest.md)
2. Attach: exports/nina_latest.md
3. Attach: the specific source file(s) to be discussed
4. State: task type — bug / feature / doc / security / review
5. Check: cat ~/nina/juleslock.txt — confirm no target files are locked

---


## Executive Snapshot

### Identity & Deployment Summary
- **Project Name:** NINA
- **Owner:** M. Baizid Alam — AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **Deployment Machine:** ASUS VivoBook X530FN — Ubuntu 26.04 LTS — Python 3.14.4 — User: aibony
- **Service Name:** systemd `nina.service` — Restart=always, depends on `ollama.service`

### Core Architecture Summary
- **Core Modules**: 
  - `core/nina.py` (Orchestrator)
  - `core/router.py` (HybridRouter V4)
  - `core/config.py` (NinaConfig)
  - `core/agent.py` (AgentLoop)
  - `core/memory.py` (MemorySystem)
  - `core/capabilities.py` (CapabilityRegistry)
  - `core/hotreload.py` (ConfigHotReload)
- **Interfaces**:
  - `interfaces/telegraminterface.py` (Telegram bot / security gate)
- **Guardian Engine**:
  - `guardianengine.py` (Forensic checks)
- **Key Files**:
  - `main.py` (Entry point)
  - `data/memory/facts.json` (Personal context facts)
  - `guardian.sh` (Shell validation script)

### Tool Routing & Quota Strategy Summary
- **Priority Priority List:** Free first → Groq → Gemini → Cerebras → DeepSeek → Mistral → Together → Cohere → Fireworks → Perplexity → SambaNova → OpenRouter → xAI → OpenAI (paid, last resort)
- **Provider Tiers:**
  - **Tier 1 (Keyless):** POLLINATIONS, CHUTES, HFPUBLIC
  - **Tier 2 (Keyed):** CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini), ONEBRAIN
  - **Tier 3:** OPENROUTER
  - **Local:** LOCALFAST (qwen2.5:1.5b), LOCALHEAVY (qwen2.5:7b)
- **Routing Score Algorithm:** `success_rate × 0.4 + (1 - latency / 5000) × 0.4 + not_near_limit × 0.2`
- **Circuit Breaker state:** CLOSED → OPEN (3 failures/5min) → HALF-OPEN (probe after 1800s)

### NINA Tool Routing Policy v2 Summary
**Principle:** Perplexity plans, agy stabilizes, Jules builds — running IN PARALLEL.

### Three-Tool Parallel Model

| Tool | Role | Execution Mode |
|------|------|---------------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Active throughout — specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| Antigravity CLI (agy) | LOCAL MUSCLE | Sync local executor — edits, merges Jules PRs, deploys to service |

### The Full Parallel Loop
1. Perplexity diagnoses + writes precise spec
2. Jules receives spec → builds in cloud async (no interaction after submit)
3. agy handles any urgent local fixes in parallel on its own worktree
4. Jules opens PR when done
5. agy reviews Jules PR diff, runs lint/compile checks, merges to main
6. agy runs `./nina_sync.sh` to deploy and export
7. Perplexity reviews result (attach `nina_latest.md` to new thread)

### agy as Merge Executor (Mandatory)
- agy performs ALL Jules PR merges — never auto-merge via GitHub UI
- Before merge: `python3 -m py_compile` + `pyflakes` on changed files, check `jules_lock.txt`
- After merge: `./nina_sync.sh` — no exceptions
- Merge conflict → stop, escalate to Perplexity for re-spec

### Key Rules
- Check `jules_lock.txt` before starting any task.
- High-risk files (`main.py`, `router.py`, `telegram_interface.py`, `guardian_engine.py`, `shell.py`, `.env`) default to agy/local only.
- Perplexity requires exact source attachments for code edits; `nina_latest.md` is for snapshot awareness only.
- Sensitive paths remain LOCAL only — never cloud.

### High-Risk Files
- `interfaces/telegram_interface.py` (Telegram bot / security gate)
- `.env` (Secrets — NEVER commit, NEVER send to cloud)
- `core/router.py` (HybridRouter V4)
- `main.py` (Entry point)
- `guardian_engine.py` (Forensic engine)
- `tools/shell.py` (Allowlist-gated shell)

### Latest Verified Runtime Status
- **nina.service Status:** active


## Current Action Board

### Summary Counts
- **🔴 BLOCKER:** 0
- **🟠 WARN:** 0
- **🟡 DEBT:** 0
- **🔵 FEATURE/PENDING:** 11

#### 🔵 FEATURE/PENDING
| ID | Severity | Component | Issue (short) | Status | Assignee | Fixed In | File(s) |
|----|----------|-----------|---------------|--------|----------|----------|---------|
| F-01 | 🔵 OPEN/PENDING | - | B-1 · Self-check pass for complex tasks | OPEN | unassigned | — | core/agent.py |
| F-04 | 🔵 OPEN/PENDING | - | C-1 · Expenditure tracker tool | OPEN | unassigned | — | tools/finance.py |
| F-05 | 🔵 OPEN/PENDING | - | C-2 · Share market monitor (DSE/CSE alerts) | OPEN | unassigned | — | tools/market.py |
| F-06 | 🔵 OPEN/PENDING | - | C-3 · Proactive reminder engine | OPEN | unassigned | — | core/nina.py |
| F-07 | 🔵 OPEN/PENDING | - | C-4 · Email triage improvement | OPEN | unassigned | — | tools/office_mail.py |
| F-08 | 🔵 OPEN/PENDING | - | C-5 · Personal knowledge base (`/remember` and `/recall`) | OPEN | unassigned | — | core/memory.py |
| R-77 | 🔵 OPEN/PENDING | - | A-1 · Fix `parallel_route` RAM guard crash | OPEN | unassigned | — | core/router.py |
| R-78 | 🔵 OPEN/PENDING | - | A-3 · Fix tool grammar fragility (minimum viable guard) | OPEN | unassigned | — | core/agent.py |
| config.missing_env.telegramchatid | 🔵 OPEN/PENDING | core.config | TELEGRAMCHATID missing from .env (non-blocking) | OPEN | unassigned | — | .env |
| feature.ews_blocked | 🔵 OPEN/PENDING | tools.officemail | EWS email feature blocked (open issue O-02) | OPEN | unassigned | — | tools/officemail.py |
| feature.playwright_blocked | 🔵 OPEN/PENDING | tools.browser | Playwright browser tool blocked (open issue O-01) | OPEN | unassigned | — | tools/browser.py |



## Current Phase & Roadmap

### Current Stage & Next Task
- **Current Stage:** Stage B — Make NINA Smarter (PARTIAL)
- **What is done:**
  - B-1 F-01 Self-check pass in `core/agent.py` (DONE)
  - B-2 F-02 Personal context injection in `core/memory.py` and `data/memory/facts.json` (DONE)
- **What is next:**
  - B-3 F-03 Response tone calibration in system prompt (`core/nina.py` SYSTEM_PROMPT_TEMPLATE)

### Open Milestones
- **B-3 F-03**: Response tone calibration in system prompt (`core/nina.py` SYSTEM_PROMPT_TEMPLATE)
- **C-1 F-04**: Expenditure tracker tool (`tools/finance.py`)
- **C-2 F-05**: Share market monitor (`tools/market.py`) + `crons/manager.py`
- **C-3 F-06**: Proactive reminder engine (`core/nina.py` + `data/reminders.json`)
- **C-4 F-07**: Email triage improvement (`tools/office_mail.py`)
- **C-5 F-08**: Personal knowledge base (`core/memory.py` + Telegram command handler)

### Action Board Confidence
- **Revalidation Pass:** Conducted on 2026-06-06 against live code and guardian evidence.
- **Historical Blocker & Warning Signatures (Confirmed Stale/FIXED):**
  - Router attribute issues (`router.attr.forcelocal`, `router.attr.orderedproviders`, `router.attr.selfhttp`) are verified as resolved.
  - Startup issues (`startup.nameError`, `startup.syntaxError`, etc.) are resolved; `guardian` now returns `Status: PASS` cleanly.
  - Hot-reload environment reverts (`hotreload.deletedkeyrevert`) and SSRF guard regressions (`browser.ssrf.guardregression`) are fixed in live source code.
  - Env variables (`apisecretkey`, `authorizeduserid`, `telegrambottoken`) are populated and loaded properly at runtime.
  - Conflicting scheduler ID issues (`cron.conflictingid`) are resolved.
  - Telegram interface issues (`telegram.document.handler_order` via dedicated handler, `telegram.key.echoed_in_chat` via centralized mask helper, and `telegram.parsemode.badrequest` via safe defaults) are resolved.
  - Logging handler duplication check (`logger.duplicate_handler`) is resolved via a root.handlers guard.
- **Genuinely Unresolved Items (Confirmed OPEN):**
  - None (all warning items from the register are resolved).
- **Refreshed Board Priority:** Action priority must now follow the refreshed error register board.


## Recent Meaningful Changes

## Entry 110 — 2026-06-06 · D-14 jules_lock.txt created — agy/Jules file territory system

**Triggered by:** User request to introduce a file territory coordination system.

**What changed:**
- Created the new file `jules_lock.txt` to track files locked/modified by Jules.
- Added a check rule for `agy` to the Jules rules section in `AGENTS.md`.
- Added an update rule for `agy` to the agy rules section in `AGENTS.md`.

**What was verified:**
- `cat jules_lock.txt`: verified exact template content
- `grep "jules_lock" AGENTS.md`: verified the two added rules in the Jules and agy sections

**Rollback path:**
- `rm jules_lock.txt && git checkout HEAD -- AGENTS.md`

---

## Entry 114 — 2026-06-06 · D-15 Learn Jules Tools Reference and Examples

**Triggered by:** User request to learn Jules CLI documentation.

**What changed:**
- Read and learned the command line reference for Jules CLI (`jules`).
- Read and learned the practical scripting examples for Jules CLI.

**What was verified:**
- Completed viewing and understanding of Jules CLI reference docs and scripting examples.

**Rollback path:**
- `git checkout HEAD -- nina_update_log.md`

---

## Entry 116 — 2026-06-06 · D-16 Pushed main to origin after PR status verification

**Triggered by:** User request to close open PRs and push main.

**What changed:**
- Checked for open pull requests on `aibony/nina` (found 0 open PRs; all 7 existing PRs were already closed).
- Pushed main branch to origin (`git push origin main` succeeded, updating origin main to `c427dc6`).

**What was verified:**
- Verified `git log --oneline -3` matches the latest post-session sync.

**Rollback path:**
- `git checkout HEAD -- nina_update_log.md`

---

## Entry 119 — 2026-06-06 · D-17 fetch prune and final verification

**Triggered by:** User request to prune stale remote branches and push main.

**What changed:**
- Executed `git fetch --prune origin`.
- Pushed main branch to origin (`git push origin main`).

**What was verified:**
- Verified `git log --oneline -3` matches expected commit history.

**Rollback path:**
- `git checkout HEAD -- nina_update_log.md`

---

## Entry 121 — 2026-06-06 · D-18 Fix nina_sync.sh Jules PR branch push check logic

**Triggered by:** User request to fix nina_sync.sh push check.

**What changed:**
- Modified `nina_sync.sh` to check for open pull requests using `gh pr list --state open` instead of checking for existing remote branches via `git ls-remote`.
- Added jq filtering for branch patterns `jules-*`, `nina-j*`, `feat/*`, and `pr-*`.
- Ensured graceful fallback to `0` if `gh` or `jq` queries fail.

**What was verified:**
- Verified bash syntax of `nina_sync.sh` (`bash -n nina_sync.sh`).
- Verified jq and gh pipeline locally to ensure it correctly returns 0 when no open PRs exist.

**Rollback path:**
- `git checkout HEAD -- nina_sync.sh nina_update_log.md`

---

## Entry 123 — 2026-06-06 · chore: Consolidated docs/space/ from 10 files to 3

**Triggered by:** User request to consolidate docs/space/ and optimize space file count.

**What changed:**
- Consolidated `docs/space/` from 10 files to 3.
- Created `docs/space/nina_state.md` to hold identity, architecture, providers, roadmap phase, milestones, capabilities, facts, and key paths.
- Trimmed `docs/space/nina_error_register.md` to keep only open and in-progress entries, added `ASSIGNEE` column, and moved FIXED entries to `exports/nina_error_register_archive.md`.
- Kept only the last 30 update log entries in `nina_update_log.md` and moved older ones to `exports/nina_update_log_archive_2026-05.md`.
- Moved entire `docs/space/nina_problem_log.md` to `exports/nina_problem_log_archive.md` and deleted it from `docs/space/`.
- Deleted redundant files from `docs/space/` (`nina_context.md`, `nina_phase1_roadmap.md`, `capabilities.json`, `facts.json`, `requirements.txt`).
- Moved `docs/space/nina_v12_blueprint.md` to `docs/archive/nina_v12_blueprint.md`.
- Updated `SPACE_FILES` array in `nina_sync.sh` to reference exactly `AGENTS.md`, `docs/space/nina_error_register.md`, and `docs/space/nina_state.md`.

**What was verified:**
- Verified folder structure of `docs/space/` (exactly 4 files including `nina_update_log.md`).
- Verified bash syntax of `nina_sync.sh`.

**Rollback path:**
- `git checkout HEAD -- nina_sync.sh docs/space/ nina_update_log.md`

---

## Entry 124 — 2026-06-06 · docs:(D-17) optimize ninalatest context export for size and signal

**Triggered by:** User request to optimize Step 8 backup export for Perplexity Space.

**What changed:**
- Created a dedicated Python script `tools/compact_exporter.py` to generate `nina_latest.md` as a compact operational snapshot.
- Refactored Step 8 of `nina_sync.sh` to call `tools/compact_exporter.py` instead of the raw inline bash find-and-dump block.
- Standardized snapshot structure to feature only: Header, Executive Snapshot, Current Action Board (open issues only), Phase/Roadmap, Recent Meaningful Changes (skipping D-sync spam), Key Rules, Targeted Code Context (summarized class/method signatures for large files, full codes for short/critical files), and Appendix Pointers.

**What was verified:**
- Verified bash syntax of `nina_sync.sh` (`bash -n nina_sync.sh`).
- Verified python syntax and execution of `tools/compact_exporter.py` (`python3 -m py_compile tools/compact_exporter.py && tools/compact_exporter.py`).
- Reduced `nina_latest.md` size from ~392KB to ~63KB.

**Rollback path:**
- `git checkout HEAD -- nina_sync.sh nina_update_log.md && rm tools/compact_exporter.py`

---

## Entry 125 — 2026-06-06 · docs:(D-18) add NINA Tool Routing Policy v2 for Perplexity agy Jules

**Triggered by:** User request to write and integrate NINA Tool Routing Policy v2.

**What changed:**
- Created a concise `NINA Tool Routing Policy v2` detailing the operating model ("Perplexity plans, agy stabilizes, Jules builds"), a task routing matrix, hard routing rules, context model rules, session workflow, high-risk default routing, and common failure modes to avoid.
- Integrated the long version of the policy into `AGENTS.md` and mirrored it to `docs/space/AGENTS.md`.
- Integrated a summary version of the policy into `docs/space/nina_state.md`.
- Adjusted `tools/compact_exporter.py` to extract and export this routing policy summary cleanly into the backup snapshot.

**What was verified:**
- Verified bash syntax of `nina_sync.sh` (`bash -n nina_sync.sh`).
- Verified python syntax of `tools/compact_exporter.py` (`python3 -m py_compile tools/compact_exporter.py`).
- Executed `tools/compact_exporter.py` and confirmed `nina_latest.md` includes the routing policy summary.

**Rollback path:**
- `git checkout HEAD -- AGENTS.md docs/space/AGENTS.md docs/space/nina_state.md tools/compact_exporter.py nina_update_log.md`

---

## Entry 126 — 2026-06-06 · docs:(D-19) revalidate open blocker board against live code and guardian evidence

**Triggered by:** User request to revalidate open blocker board against live code and guardian evidence.

**What changed:**
- Revalidated 26 items on the blocker board in `docs/space/nina_error_register.md` against the live source code and `guardian` runtime checks.
- Marked 22 stale/fixed items as `✅ FIXED` (including router attribute trio, startup error block, SSRF ipaddress checks, hot-reload environment defaults, conflicting job IDs, and ghost instance safeguards).
- Retained genuinely unresolved warning items (`logger.duplicate_handler` and Telegram interface issues) as `OPEN`.
- Updated the canonical state document `docs/space/nina_state.md` with an `Action Board Confidence` summary.
- Modified `guardian` to remove the deleted `core.logger` module from the import validation list.
- Updated `tools/compact_exporter.py` to parse and export the refreshed Action Board Confidence section to the backup snapshot.

**What was verified:**
- Verified bash syntax of `nina_sync.sh` (`bash -n nina_sync.sh`).
- Verified python syntax and compile/lint on changed file `tools/compact_exporter.py` (`py_compile` and `pyflakes` passed 100% cleanly).
- Ran `./guardian --skip-deploy` and verified it reports `All checks passed — NINA is healthy 🎉` with health score 9.8/10.

**Rollback path:**
- `git checkout HEAD -- docs/space/nina_error_register.md docs/space/nina_state.md guardian tools/compact_exporter.py nina_update_log.md`

---

## Entry 127 — 2026-06-06 · fix:(D-20) harden Telegram interface masking handler order parse_mode

**Triggered by:** User request to harden the Telegram interface to mask secrets, separate document uploads, and handle parse_mode safely.

**What changed:**
- Masked all outgoing Telegram message paths (`_reply` and `_edit_message`) by wrapping them to pass all text through the centralized `_mask_secrets` helper before sending.
- Fixed the recursive infinite loop bug inside `_reply` by redirecting it to call `update.message.reply_text` correctly.
- Centralized `parse_mode` defaults to `None` (`PARSE_MODE_DEFAULT`) and `"MarkdownV2"` (`PARSE_MODE_MARKDOWN_V2`) inside `TelegramInterface` to prevent BadRequest parse errors, and updated all send paths to respect this centralization.
- Gated and prioritized document updates by registering a dedicated `MessageHandler` filtering for all documents (`filters.Document.ALL`) before the catch-all `filters.ALL` generic message handler.
- Cleaned up `docs/space/nina_error_register.md` and `docs/space/nina_state.md` to document the fixes for Telegram warnings.

**What was verified:**
- Compiled and linted `interfaces/telegram_interface.py` successfully (`py_compile` and `pyflakes` passed 100% cleanly).
- Verified `guardian --skip-deploy` completed with status `PASS` and a perfect health score of `9.8/10`.
- Verified no new blocker errors were introduced.

**Rollback path:**
- `git checkout HEAD -- interfaces/telegram_interface.py docs/space/nina_error_register.md docs/space/nina_state.md nina_update_log.md`

---

_Note: 26 automated sync runs omitted; no material policy or architecture change._


## Key Rules for Future Patches

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

### 1. Three-Tool Operating Model — Parallel Execution

NINA uses three tools running IN PARALLEL as the standard operating mode:

| Tool | Role | Execution Mode |
|------|------|---------------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Active throughout — specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| Antigravity CLI (agy) | LOCAL MUSCLE | Sync local executor — edits, merges Jules PRs, deploys to service |

THE FULL PARALLEL LOOP:
1. Perplexity diagnoses + writes precise spec
2. Jules receives spec → builds in cloud async (no interaction after submit)
3. agy handles any urgent local fixes in parallel on its own worktree
4. Jules opens PR when done
5. agy reviews Jules PR diff, runs lint/compile checks, merges to main
6. agy runs ./nina_sync.sh to deploy and export
7. Perplexity reviews result (attach nina_latest.md to new thread)

KEY DISTINCTION: agy is NOT just a fixer — it is the local merge and deploy executor.
Jules does NOT merge its own PRs — agy always performs the merge after review.
Perplexity is NOT idle during coding — it remains available for unblocking and mid-task review.

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

### 8. agy as Merge Executor (Mandatory)
- agy is responsible for ALL Jules PR merges — never auto-merge Jules PRs via GitHub UI
- Before merging: run `python3 -m py_compile` on changed files, run `pyflakes`, check `jules_lock.txt`
- After merging: run `./nina_sync.sh` — no exceptions
- If merge conflict: stop, report to Perplexity for re-spec, do not attempt blind resolution

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


## Targeted Code Context

### `core/router.py` (Compact Signatures Summary)

#### Imports
```python
import asyncio, hashlib, json, logging, re, time, uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, cast
import httpx, psutil
from core.config import NinaConfig, RATELIMITS
from tools import jules_api
```

#### Classes & Signatures
```python
class CircuitBreaker:
  def __init__(self):
  def _prune(self):
  def allow_request(self) -> bool:
  def record_success(self):
  def record_failure(self, cooldown_s: Optional[float] = None):
  def set_cooldown(self, seconds: float):
class ProviderHealth:
  def cooldown_until(self) -> float:
  def degraded_until(self) -> float:
  def avg_latency_ms(self) -> float:
  def success_rate(self) -> float:
  def is_available(self, has_key: bool) -> bool:
  def is_degraded(self) -> bool:
  def is_near_limit(self, pid: str) -> bool:
  def is_exhausted(self, pid: str) -> bool:
  def composite_score(self, pid: str) -> float:
  def record_success(self, latency_ms: float, total_tokens: int):
  def record_failure(self, cooldown_s: Optional[float] = None):
  def reset_daily(self):
class ClassifiedTask:
class ResponseCache:
  def __init__(self):
  def _k(self, prompt: str, messages: list | None = None) -> str:
  def get(self, prompt: str, tt: str, messages: list | None = None) -> Optional[str]:
  def set(self, prompt: str, tt: str, response: str, provider: str, messages: list | None = None):
  def clear(self):
  def purge_expired(self):
class CostTracker:
  def __init__(self):
  def record(self, provider, tt, in_t, out_t, cost, ttf, total, parallel=False, cached=False, error=None, req_id=""):
  def reset_daily(self):
class HybridRouter:
  def __init__(self, config: NinaConfig):
  def size_rank(name: str):
  def _has_key(self, pid: str) -> bool:
  def _ordered_providers(self, task: ClassifiedTask, force_local: bool = False) -> list:
  def reset_daily_counters(self):
  def get_status(self) -> str:
```

---

### `core/agent.py` (Compact Signatures Summary)

#### Docstring
"""NINA v12 — AgentLoop (Stage 5)
THINK -> PLAN -> ACT -> OBSERVE -> ADAPT. Variable step budget + global timeout + thermal preflight.
"""

#### Imports
```python
import asyncio, logging, re
from core.router import HybridRouter, ClassifiedTask, STEP_BUDGETS, DEFAULT_MAX_STEPS
from tools import system
from core.capabilities import CapabilityRegistry
```

#### Classes & Signatures
```python
class AgentLoop:
  def __init__(self, config, router: HybridRouter, memory, tools: dict):
  def _should_self_check(self, task: ClassifiedTask) -> bool:
  def _is_bangla(cls, text: str) -> bool:
```

---

### `core/nina.py` (Compact Signatures Summary)

#### Docstring
"""NINA v12 — NinaOS orchestrator (Stage 1)."""
import logging, os, time
from core.config import load_config
from core.router import HybridRouter
from core.memory import MemorySystem
from core.agent import AgentLoop
from crons.manager import TaskScheduler
from tools.upgradepipeline import UpgradePipeline, IDLE_QUEUE as _IDLE_QUEUE
from idleloop import IdleUpgradeLoop
from core.hotreload import ConfigHotReload
from interfaces.telegram_interface import TelegramInterface
from tools import shell, browser, system as systool, jules_api

SYSTEM_PROMPT_TEMPLATE = """You are NINA — Neural Intelligent Network Assistant.
You run continuously on a local laptop in Dhaka, Bangladesh for M. Baizid Alam, Senior Banker at BASIC Bank.
Be concise. Reason step by step for non-trivial tasks. State uncertainty plainly.
Current datetime (Dhaka): {datetime}
Memory context: {memory_context}
Available tools: shell (run commands), web/search (Tavily+Serper+DDG), browser (fetch URL), system (status).

#### Imports
```python
import logging, os, time
from core.config import load_config
from core.router import HybridRouter
from core.memory import MemorySystem
from core.agent import AgentLoop
from crons.manager import TaskScheduler
from tools.upgradepipeline import UpgradePipeline, IDLE_QUEUE as _IDLE_QUEUE
from idleloop import IdleUpgradeLoop
from core.hotreload import ConfigHotReload
from interfaces.telegram_interface import TelegramInterface
from tools import shell, browser, system as systool, jules_api
```

#### Classes & Signatures
```python
class NinaOS:
  def __init__(self):
  def file_handler(filename, level=logging.DEBUG):
  def _has_handler(logger_obj, filename=None, stream=False):
```

---

### `core/config.py`

```python
"""NINA v12 — NinaConfig + RATELIMITS (Stage 1+2)."""
import os
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

RATELIMITS = {
    "GROQ":       {"rpm":30,  "tpd":14400,   "rpd":14400, "min_spacing_s":2},
    "CEREBRAS":   {"rpm":30,  "tpd":100000,  "rpd":None,  "min_spacing_s":2},
    "GEMINI":     {"rpm":15,  "tpd":1500000, "rpd":1500,  "min_spacing_s":4},
    "MISTRAL":    {"rpm":1,   "tpd":None,    "rpd":None,  "min_spacing_s":61},
    "POLLINATIONS":{"rpm":5,  "tpd":None,    "rpd":None,  "min_spacing_s":12},
    "CHUTES":     {"rpm":3,   "tpd":None,    "rpd":None,  "min_spacing_s":20},
    "HFPUBLIC":   {"rpm":10,  "tpd":None,    "rpd":None,  "min_spacing_s":6},
    "DEEPSEEK":   {"rpm":60,  "tpd":500000,  "rpd":None,  "min_spacing_s":1},
    "TOGETHER":   {"rpm":60,  "tpd":None,    "rpd":None,  "min_spacing_s":1},
    "COHERE":     {"rpm":20,  "tpd":None,    "rpd":1000,  "min_spacing_s":3},
    "FIREWORKS":  {"rpm":30,  "tpd":None,    "rpd":None,  "min_spacing_s":2},
    "XAI":        {"rpm":60,  "tpd":None,    "rpd":None,  "min_spacing_s":1},
    "SAMBANOVA":  {"rpm":30,  "tpd":100000,  "rpd":None,  "min_spacing_s":2},
    "HYPERBOLIC": {"rpm":60,  "tpd":None,    "rpd":None,  "min_spacing_s":1},
    "NOVITA":     {"rpm":30,  "tpd":None,    "rpd":None,  "min_spacing_s":2},
    "PERPLEXITY": {"rpm":50,  "tpd":None,    "rpd":None,  "min_spacing_s":2},
    "OPENAI":     {"rpm":500, "tpd":None,    "rpd":None,  "min_spacing_s":0},
    "ONEBRAIN":   {"rpm":20,  "tpd":None,    "rpd":None,  "min_spacing_s":3},
    "OPENROUTER": {"rpm":20,  "tpd":None,    "rpd":None,  "min_spacing_s":3},
}

class NinaConfig(BaseModel):
    telegram_bot_token:   str
    authorized_user_id:   str
    ollama_host:          str = "http://localhost:11434"
    cerebras_api_key:     Optional[str] = None
    groq_api_key:         Optional[str] = None
    gemini_api_key:       Optional[str] = None
    mistral_api_key:      Optional[str] = None
    openrouter_api_key:   Optional[str] = None
    openai_api_key:       Optional[str] = None
    deepseek_api_key:     Optional[str] = None
    perplexity_api_key:   Optional[str] = None
    together_api_key:     Optional[str] = None
    cohere_api_key:       Optional[str] = None
    fireworks_api_key:    Optional[str] = None
    xai_api_key:          Optional[str] = None
    sambanova_api_key:    Optional[str] = None
    hyperbolic_api_key:   Optional[str] = None
    novita_api_key:       Optional[str] = None
    one_brain_api_key:    Optional[str] = None
    one_brain_api_base:   Optional[str] = None
    api_secret_key:       Optional[str] = None
    api_rate_limit_rpm:   int = 60
    ews_server:           str = "webmail.basicbanklimited.com"
    ews_domain:           str = "basic.bank"
    ews_username:         Optional[str] = None
    ews_password:         Optional[str] = None
    ews_auth_type:        str = "NTLM"
    ews_my_email:         Optional[str] = None
    ews_shared_email:     Optional[str] = None
    ews_max_emails:       int = 10
    ews_keywords:         str = "SWIFT,LC,MT103,MT202,MT700,discrepancy,amendment,BG,overdue,urgent"
    log_level:            str = "INFO"
    workspace_dir:        Path = Path("data/workspace")
    max_ram_gb:           float = 12.0
    ram_guard_gb:         float = 10.5
    disk_guard_pct:       float = 90.0
    idle_threshold_min:   int = 15
    idle_report_min:      int = 30
    idle_auto_approve:    bool = False
    session_max_turns:    int = 20
    agent_timeout_s:      int = 300
    flood_window_s:       int = 30
    flood_max_messages:   int = 10
    dead_man_ping_url:    Optional[str] = None
    dead_man_max_interval_min: int = 65
    thermal_warn_cpu:     int = 80
    thermal_warn_gpu:     int = 80
    thermal_guard_cpu:    int = 90
    thermal_guard_gpu:    int = 85
    thermal_critical_cpu: int = 95
    thermal_critical_gpu: int = 90
    model_overrides: dict = {}

def load_config() -> NinaConfig:
    tok = os.getenv("TELEGRAM_BOT_TOKEN")
    uid = os.getenv("AUTHORIZED_USER_ID")
    if not tok:
        raise RuntimeError("TELEGRAM_BOT_TOKEN missing from .env — cannot start NINA.")
    if not uid:
        raise RuntimeError("AUTHORIZED_USER_ID missing from .env — cannot start NINA.")
    cfg = NinaConfig(
        telegram_bot_token = tok,
        authorized_user_id = uid,
        **{k: os.getenv(v) for k,v in {  # type: ignore  # dynamically populated config fields
            "ollama_host":"OLLAMAHOST","cerebras_api_key":"CEREBRASAPIKEY",
            "groq_api_key":"GROQAPIKEY","gemini_api_key":"GEMINIAPIKEY",
            "mistral_api_key":"MISTRALAPIKEY","openrouter_api_key":"OPENROUTERAPIKEY",
            "openai_api_key":"OPENAIAPIKEY","deepseek_api_key":"DEEPSEEKAPIKEY",
            "perplexity_api_key":"PERPLEXITYAPIKEY","together_api_key":"TOGETHERAPIKEY",
            "cohere_api_key":"COHEREAPIKEY","fireworks_api_key":"FIREWORKSAPIKEY",
            "xai_api_key":"XAIAPIKEY","sambanova_api_key":"SAMBANOVAAPIKEY",
            "hyperbolic_api_key":"HYPERBOLICAPIKEY","novita_api_key":"NOVITAAPIKEY",
            "one_brain_api_key":"ONEBRAINAPIKEY","one_brain_api_base":"ONEBRAINAPIBASE",
            "api_secret_key":"API_SECRET_KEY","ews_password":"EWSPASSWORD","ews_username":"EWS_USERNAME","ews_my_email":"EWS_MY_EMAIL","ews_shared_email":"EWS_SHARED_EMAIL",
            "dead_man_ping_url":"DEADMANPINGURL",
        }.items() if os.getenv(v)}
    )
    if v := os.getenv("IDLE_AUTO_APPROVE"):
        cfg.idle_auto_approve = v.lower() == "true"
    if v := os.getenv("IDLE_THRESHOLD_MIN"):
        cfg.idle_threshold_min = int(v)
    if v := os.getenv("IDLE_REPORT_MIN"):
        cfg.idle_report_min = int(v)
    return cfg

```

---

### `core/memory.py` (Compact Signatures Summary)

#### Imports
```python
import asyncio, json, logging, shutil, time, uuid
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
```

#### Classes & Signatures
```python
class MemorySystem:
  def __init__(self):
  def conversation_count(self):
  def fact_count(self):
```

---

### `core/hotreload.py`

```python
"""NINA v12 -- ConfigHotReload (Stage 6.6)
Watches .env every 60s. Reloads reloadable fields without restart.
Non-reloadable fields require restart -- changes are logged but ignored.
"""
import asyncio, logging
from pathlib import Path
from dotenv import dotenv_values
from pydantic.fields import PydanticUndefined

logger = logging.getLogger("nina.config")

RELOADABLE = {
    "EWS_MAX_EMAILS":       ("ews_max_emails",        int),
    "EWS_KEYWORDS":         ("ews_keywords",           str),
    "IDLE_THRESHOLD_MIN":   ("idle_threshold_min",     int),
    "IDLE_REPORT_MIN":      ("idle_report_min",        int),
    "IDLE_AUTO_APPROVE":    ("idle_auto_approve",      lambda v: v.lower() == "true"),
    "FLOOD_WINDOW_S":       ("flood_window_s",         int),   # FIX: was FLOOD_WINDOWS
    "FLOOD_MAX_MESSAGES":   ("flood_max_messages",     int),
    "SESSION_MAX_TURNS":    ("session_max_turns",      int),
    "AGENT_TIMEOUT_S":      ("agent_timeout_s",        int),   # FIX: was AGENT_TIMEOUTS
    "API_RATE_LIMIT_RPM":   ("api_rate_limit_rpm",     int),
    "DEAD_MAN_PING_URL":    ("dead_man_ping_url",      str),
    "LOG_LEVEL":            ("log_level",              str),
    "THERMAL_WARN_CPU":     ("thermal_warn_cpu",       int),
    "THERMAL_WARN_GPU":     ("thermal_warn_gpu",       int),
    "THERMAL_GUARD_CPU":    ("thermal_guard_cpu",      int),
    "THERMAL_GUARD_GPU":    ("thermal_guard_gpu",      int),
    "THERMAL_CRITICAL_CPU": ("thermal_critical_cpu",   int),
    "THERMAL_CRITICAL_GPU": ("thermal_critical_gpu",   int),
}


class ConfigHotReload:
    def __init__(self, config, telegram=None):
        self.config    = config
        self.telegram  = telegram
        self._env_path = Path(".env")
        self._last_mtime: float = self._mtime()
        self._task = None

    def _mtime(self) -> float:
        try:
            return self._env_path.stat().st_mtime
        except Exception as e:
            logger.warning(f"config_hotreload_mtime_failed {e}")
            return 0.0

    async def initialize(self):
        self._task = asyncio.create_task(self._watch())
        logger.info("ConfigHotReload watching .env every 60s")

    async def _watch(self):
        while True:
            try:
                await asyncio.sleep(60)
                mtime = self._mtime()
                if mtime <= self._last_mtime:
                    continue
                self._last_mtime = mtime
                await self._reload()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"config_hotreload_error {e}")

    async def _reload(self):
        try:
            env     = dotenv_values(".env")
            changed = []
            for env_key, (attr, cast) in RELOADABLE.items():
                val = env.get(env_key)
                if val is None or val.strip() == "":
                    field = self.config.model_fields.get(attr)
                    if field is not None:
                        default = field.default
                        if default is not PydanticUndefined and getattr(self.config, attr) != default:
                            setattr(self.config, attr, default)
                            changed.append(f"{attr}: reverted to default({default})")
                    continue
                try:
                    new_val = cast(val)
                except Exception:
                    continue
                old_val = getattr(self.config, attr, None)
                if new_val != old_val:
                    setattr(self.config, attr, new_val)
                    changed.append(f"{attr}: {old_val} -> {new_val}")

            if changed:
                msg = "Config reloaded:\n" + "\n".join(changed)
                logger.info(f"config_hotreload changed={changed}", extra={"log": "nina.log"})
                if self.telegram:
                    await self.telegram.send_message(msg)
            else:
                logger.info("config_hotreload no reloadable changes")
        except Exception as e:
            logger.error(f"config_hotreload_failed {e}")
            if self.telegram:
                await self.telegram.send_message(
                    f"Config reload failed: {e} -- keeping old config.")

```

---

### `interfaces/telegram_interface.py` (Compact Signatures Summary)

#### Docstring
"""
NINA v12 -- TelegramInterface (Stage 3)
Security gate, command handler, NLP fallback, streaming, flood protection, reset UX.
"""

#### Imports
```python
import asyncio, logging, re, time
from pathlib import Path
from typing import Optional
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from core.config import NinaConfig
from core.router import HybridRouter, ClassifiedTask, classify_task
```

#### Classes & Signatures
```python
class TelegramInterface:
  def __init__(self, config: NinaConfig, nina_os):
  def _mask_secrets(self, text: str) -> str:
  def esc(t):
```

---

### `tools/shell.py`

```python
import asyncio, logging, shlex, subprocess

# ---- Allowlists -------------------------------------------------------------
ALLOWED_BASES = {
    "df", "ls", "pwd", "whoami", "free", "ps", "uptime",
    "head", "tail", "grep", "find", "echo", "date",
    "ping", "curl", "wget", "python", "python3", "pip", "pip3",
    "git", "systemctl", "journalctl", "ollama", "nvidia-smi",
}
ALLOWED_SYSTEMCTL_SUBS = {
    "status", "start", "stop", "restart", "enable", "disable", "is-active",
}
ALLOWED_OLLAMA_SUBS = {
    "list", "show", "pull", "run", "stop", "ps", "serve",
}
# cat removed in R-48, verified clean R-97.

ALLOWED = ALLOWED_BASES   # backward-compat alias

logger = logging.getLogger("nina.tools.shell")


async def run(cmd: str) -> str:
    cmd   = cmd.strip()
    parts = shlex.split(cmd) if cmd else []
    base  = parts[0] if parts else ""

    if base not in ALLOWED_BASES:
        logger.warning(f"shell:blocked cmd={cmd!r}", extra={"log": "tools.log", "tool_name": "shell"})
        return f"Blocked: {base!r} not in allowlist."

    # FIX: compare only parts[1] (the subcommand token), not the joined tail
    if base == "systemctl":
        sub = parts[1] if len(parts) > 1 else ""
        if sub not in ALLOWED_SYSTEMCTL_SUBS:
            return f"Blocked: systemctl subcommand {sub!r} not allowed."

    if base == "ollama":
        sub = parts[1] if len(parts) > 1 else ""
        if sub not in ALLOWED_OLLAMA_SUBS:
            return f"Blocked: ollama subcommand {sub!r} not allowed."

    for evil in (";", "&&", "||", "|", "`", "$("):
        if evil in cmd:
            logger.warning(f"shell_injection_blocked cmd={cmd!r}", extra={"log": "tools.log", "tool_name": "shell"})
            return "Blocked: shell operators not allowed in command."

    try:
        loop = asyncio.get_running_loop()
        r = await asyncio.wait_for(
            loop.run_in_executor(None,
                lambda: subprocess.run(
                    shlex.split(cmd),
                    capture_output=True, text=True, timeout=10)),
            timeout=12)

        out = (r.stdout + r.stderr).strip()[:2000]

        if r.returncode != 0:
            logger.warning(
                f"shell_nonzero cmd={cmd!r} rc={r.returncode} err={r.stderr[:80]!r}",
                extra={"log": "tools.log", "tool_name": "shell"})
            return f"Exit {r.returncode}: {out or '(no output)'}"

        logger.info(f"shell_ok cmd={cmd!r} out={out[:80]!r}", extra={"log": "tools.log", "tool_name": "shell"})
        return out or "(no output)"

    except asyncio.TimeoutError:
        return "Command timed out (10s)."
    except FileNotFoundError:
        return f"Command not found: {cmd.split()[0]}"
    except Exception as e:
        return f"Error: {e}"

```

---

### `tools/browser.py`

```python
import logging, socket
from playwright.async_api import async_playwright
import ipaddress as ipaddr
from urllib.parse import urlparse as urlparse

logger = logging.getLogger("nina.tools.browser")


def _is_internal(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
        addr = ipaddr.ip_address(host)
        return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved
    except ValueError:
        try:
            resolved = socket.gethostbyname(host)
            addr = ipaddr.ip_address(resolved)
            return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved
        except socket.gaierror:
            return True
# SSRF guard uses ipaddress module — R-64 verified, O-03 closed.


async def fetch(url: str) -> str:
    if _is_internal(url):                # FIX: was is_internal (missing underscore)
        return "Blocked: internal network target."
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(executable_path="/usr/bin/chromium-browser",
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"])
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            text = await page.inner_text("body")
            await browser.close()
            out = text[:5000]
            logger.info(f"browser_fetch url={url!r} chars={len(out)}", extra={"log": "tools.log", "tool_name": "browser"})
            return out
    except Exception as e:
        logger.warning(f"browser_fetch_failed url={url!r} err={e}", extra={"log": "tools.log", "tool_name": "browser"})
        return f"Browser error: {e}"

```

---

### `tools/upgradepipeline.py` (Compact Signatures Summary)

#### Docstring
"""
NINA v12 — UpgradePipeline (Stage 6)
Pattern scan → sandbox test → diff → approve/reject → deploy + backup.
"""

#### Imports
```python
import ast, json, logging, re, shutil, time
from pathlib import Path
```

#### Classes & Signatures
```python
class UpgradePipeline:
  def __init__(self, config, router):
  def _scan(self, code: str) -> list[str]:
  def _in_writable_scope(self, filename: str) -> bool:
  def _expire_pending(self):
class ABShadowTester:
  def __init__(self, pipeline, shadow_n=20):
  def status(self):
  def reject(self):
```

---

### `tools/finance.py`

```python
import csv
import io
import json
import logging
from collections import defaultdict

logger = logging.getLogger("nina.tools.finance")
# Using a file handler for tools.log
file_handler = logging.FileHandler("tools.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

def run_expenditure_report(expenses_data: str) -> str:
    """
    Parses expenses from CSV or text, categorizes and sums them by month and category.
    Returns a JSON string containing a compact text summary and a structured report.

    Expected CSV columns (or text lines comma-separated): date, amount, category, note
    Example line: 2023-10-15, 50.00, Groceries, Weekly shopping
    """
    logger.info("TAG:finance action=run_expenditure_report msg=starting_report_generation")

    if not expenses_data or not expenses_data.strip():
        logger.warning("TAG:finance action=run_expenditure_report msg=empty_input")
        return json.dumps({
            "summary": "No expenditure data provided.",
            "report": {}
        })

    report = defaultdict(lambda: defaultdict(float))
    total_spent = 0.0
    valid_entries = 0
    errors = 0

    try:
        # Simple heuristic to detect if it's text/csv.
        # We process line by line, trying to split by comma
        reader = csv.reader(io.StringIO(expenses_data.strip()))
        for row_num, row in enumerate(reader):
            # Skip empty lines
            if not row:
                continue

            # If header row, skip
            if row_num == 0 and any(h.strip().lower() in ['date', 'amount', 'category'] for h in row):
                continue

            if len(row) < 3:
                logger.warning(f"TAG:finance action=parse_row msg=invalid_row_format row_num={row_num}")
                errors += 1
                continue

            date_str = row[0].strip()
            amount_str = row[1].strip()
            category = row[2].strip()
            # Note is optional, but if present it's row[3]

            try:
                # Extract month (YYYY-MM format ideally, but try to handle parts)
                # If date is YYYY-MM-DD, taking first 7 chars is fine.
                # If it's something else, fallback to "Unknown" if it's too short
                if len(date_str) >= 7:
                    month = date_str[:7]
                else:
                    month = "Unknown"

                amount = float(amount_str)

                report[month][category] += amount
                total_spent += amount
                valid_entries += 1
            except ValueError:
                logger.warning(f"TAG:finance action=parse_row msg=value_error row_num={row_num} amount={amount_str}")
                errors += 1
                continue

        # Format the output
        text_summary = f"Processed {valid_entries} expenses with {errors} errors. Total spent: {total_spent:.2f}."
        for month, categories in sorted(report.items()):
            text_summary += f"\nMonth: {month}"
            month_total = 0.0
            for cat, amt in sorted(categories.items()):
                text_summary += f"\n  - {cat}: {amt:.2f}"
                month_total += amt
            text_summary += f"\n  Total for {month}: {month_total:.2f}"

        logger.info(f"TAG:finance action=run_expenditure_report msg=success valid_entries={valid_entries} errors={errors} total={total_spent}")

        return json.dumps({
            "summary": text_summary,
            "report": {month: dict(cats) for month, cats in report.items()}
        })

    except Exception as e:
        logger.error(f"TAG:finance action=run_expenditure_report msg=unexpected_error error={str(e)}")
        return json.dumps({
            "summary": "Failed to process expenditure report due to an internal error.",
            "report": {}
        })

```

---

### `tools/market.py`

```python
import json
import logging
from datetime import datetime

logger = logging.getLogger("nina.tools")

WATCHLIST = [
    {"ticker": "GP", "threshold_pct": 1.0, "last_price": 250.0},
    {"ticker": "BATBC", "threshold_pct": 1.0, "last_price": 500.0},
    {"ticker": "SQURPHARMA", "threshold_pct": 1.5, "last_price": 210.0},
]

def _fetch_dummy_price(ticker: str) -> float:
    """
    Abstracted dummy price source.
    Returns a mocked price to simulate market movements.
    """
    # Simple deterministic mock for now.
    mock_prices = {
        "GP": 253.5,        # +1.4%
        "BATBC": 498.0,     # -0.4%
        "SQURPHARMA": 215.0 # +2.3%
    }
    return mock_prices.get(ticker, 100.0)

async def run_market_monitor(nina_os=None):
    """
    Evaluates a watchlist of tickers against dummy prices.
    Generates a human-readable summary and JSON result.
    Logs output to tools.log.
    """
    logger.info("market_monitor_started")
    results = []
    alerts = []

    for item in WATCHLIST:
        ticker = item["ticker"]
        threshold = item["threshold_pct"]
        last_price = item["last_price"]

        current_price = _fetch_dummy_price(ticker)

        change = current_price - last_price
        change_pct = (change / last_price) * 100

        status = {
            "ticker": ticker,
            "last_price": last_price,
            "current_price": current_price,
            "change_pct": round(change_pct, 2),
            "alert": False
        }

        if abs(change_pct) >= threshold:
            status["alert"] = True
            direction = "UP" if change > 0 else "DOWN"
            alerts.append(f"{ticker}: {current_price} ({direction} {abs(change_pct):.2f}%)")

        results.append(status)

    summary = "Market Monitor Run: "
    if alerts:
        summary += "Alerts triggered for: " + ", ".join(alerts)
    else:
        summary += "No significant movements."

    logger.info(f"market_monitor_summary: {summary}")
    logger.info(f"market_monitor_json: {json.dumps(results)}")

    return {
        "summary": summary,
        "details": results,
        "timestamp": datetime.now().isoformat()
    }

```

---

### `tools/officemail.py`

```python
# Wrapper to maintain backwards compatibility while introducing the new office_mail.py

from .office_mail import (
    EWSConnection,
    EmailItem,
    fetch_messages,
    triage_messages,
    fetch,
)

__all__ = [
    "EWSConnection",
    "EmailItem",
    "fetch_messages",
    "triage_messages",
    "fetch",
]

```

---

### `crons/manager.py`

```python
"""
NINA v12 — TaskScheduler (Stage 5)
11 core jobs. APScheduler-based.
"""
import functools
import logging
from crons.backup_jobs import run_memory_backup, run_py_backup
from tools.market import run_market_monitor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Hard constraint (cron.lambda_coroutine_drop): Do not use lambda wrappers for async job callables.
# Lambda wrappers drop coroutine execution. Use functools.partial or pass the coroutine directly.

logger = logging.getLogger("nina.scheduler")

async def _cache_purge_job(nina_os):
    nina_os.router.cache.purge_expired()

class TaskScheduler:
    def __init__(self, nina_os):
        self.nina = nina_os
        self._sched = AsyncIOScheduler(timezone="Asia/Dhaka")

    def start(self):
        n = self.nina
        add = self._sched.add_job

        add(n.run_morning_report,    CronTrigger(hour=9,  minute=0,  timezone="Asia/Dhaka"), id="morning_report")
        add(n.run_heartbeat,         IntervalTrigger(hours=1),                               id="heartbeat")
        add(functools.partial(_cache_purge_job, n), CronTrigger(hour=3, minute=5, timezone="Asia/Dhaka"), id="cache_purge")
        add(n.run_cost_report,       CronTrigger(hour=23, minute=0,  timezone="Asia/Dhaka"), id="cost_report")
        add(n.router.reset_daily_counters, CronTrigger(hour=0, minute=1, second=0,
                                           timezone="UTC"),                                  id="rate_limit_reset")
        add(n.run_idle_summary,      IntervalTrigger(minutes=30),                            id="idle_summary")
        add(n.run_log_rotation,      CronTrigger(hour=4,  minute=0,  timezone="Asia/Dhaka"), id="log_rotation")
        add(n.run_provider_health,   IntervalTrigger(hours=6),                               id="provider_health")
        add(n.run_provider_hunter,   CronTrigger(hour=2,  minute=0,  timezone="Asia/Dhaka"), id="provider_hunter")
        add(n.run_thermal_health,    IntervalTrigger(minutes=5),                             id="thermal_health")
        add(functools.partial(run_memory_backup, n), CronTrigger(hour=2, minute=30, timezone="Asia/Dhaka"), id="memory_backup")
        add(functools.partial(run_py_backup, n),     CronTrigger(hour=3, minute=0,  timezone="Asia/Dhaka"), id="py_backup")
        add(n.run_reminder_check,    IntervalTrigger(minutes=15),                            id="reminder_check")
        add(functools.partial(run_market_monitor, n), CronTrigger(hour="10-14", minute="*/30", timezone="Asia/Dhaka"), id="market_monitor")

        add(n.pipeline._expire_pending,            IntervalTrigger(minutes=15), id="expire_pending")
        self._sched.start()
        logger.info(f"Scheduler started — {len(self._sched.get_jobs())} jobs", extra={"module": "cron", "job_id": "manager"})

    def shutdown(self, wait=False):
        self._sched.shutdown(wait=wait)

    def next_job_time(self, job_id: str) -> str:
        job = self._sched.get_job(job_id)
        return str(job.next_run_time) if job else "unknown"

    @property
    def job_count(self): return len(self._sched.get_jobs())

```

---

### `guardian_engine.py` (Compact Signatures Summary)

#### Docstring
"""
NINA Guardian 2.0 — Forensic Engine
Invoked by the `guardian` bash entry point.
Reads logs, correlates evidence, matches issue signatures, scores health,
emits terminal summary + report.json + summary.md + incident artifacts.
"""

#### Imports
```python
import argparse
import hashlib
import json
import logging
import os
import platform
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
```

#### Classes & Signatures
```python
class C:
def red(s):    return f"{C.RED}{s}{C.NC}"
def green(s):  return f"{C.GREEN}{s}{C.NC}"
def yellow(s): return f"{C.YELLOW}{s}{C.NC}"
def cyan(s):   return f"{C.CYAN}{s}{C.NC}"
def bold(s):   return f"{C.BOLD}{s}{C.NC}"
def section(title):
def ok(msg):   print(f"  {green('✔')}  {msg}")
def warn(msg): print(f"  {yellow('⚠')}  {yellow(msg)}")
def fail(msg): print(f"  {red('✖')}  {red(msg)}")
def info(msg): print(f"  {cyan('ℹ')}  {msg}")
def run_cmd(cmd, timeout=30, use_shell=False):
def file_sha256(path):
def read_file_safe(path, max_bytes=200_000):
def load_env_file(path):
def now_iso():
def now_stamp():
def relative_time(seconds_ago):
def collect_journal_recent():
def collect_journal_errors():
def collect_journal_15min():
def collect_service_status():
def collect_nina_logs():
def collect_incident_reports():
def collect_downloads_clues():
def collect_all_log_text():
def match_signatures(log_text, env_keys):
def resolve_root_cause(findings):
def compute_confidence(findings, service_active):
def inspect_service_state(journal_recent, journal_15min):
def compute_health_score(findings, service_state, env_keys):
def load_baseline():
def compute_file_hashes():
def pip_freeze_sha():
def compute_baseline_drift(baseline, current_hashes, current_pip_sha, env_keys):
def save_baseline(service_state, env_keys, current_hashes, pip_sha):
def build_timeline(journal_recent, journal_15min, guardian_start_ts):
def build_evidence_list(journal_recent, journal_errors, nina_logs, downloads_clues):
def build_suggested_actions(findings, service_state, baseline_drift):
def collect_recent_changes(baseline):
def find_latest_backup():
def write_incident_artifacts(incident_dir, report, journal_recent, service_status,
def write_summary_md(incident_dir, report):
def write_pass_summary_md(incident_dir, report):
def print_diagnosis(report):
def run_engine(args):
```

---

### `main.py`

```python
import asyncio
import os
import sys
import fcntl
import time
import signal
import logging
from core.nina import NinaOS

logger = logging.getLogger("main")

def acquire_lock():
    os.makedirs("data", exist_ok=True)
    pid_file = "data/nina.pid"
    lock_file = "data/nina.lock"

    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                old_pid = int(f.read().strip())
            if os.path.exists(f"/proc/{old_pid}"):
                logger.info("Ghost process %s is running. Sending SIGTERM.", old_pid)
                os.kill(old_pid, signal.SIGTERM)
                for _ in range(50):
                    time.sleep(0.1)
                    if not os.path.exists(f"/proc/{old_pid}"):
                        break
                else:
                    logger.warning("Process %s did not respond to SIGTERM after 5 seconds.", old_pid)
        except (ValueError, OSError):
            pass

    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    global _lock_fd
    _lock_fd = open(lock_file, "w")
    try:
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        logger.error("nina.lock held, cannot start")
        sys.exit(1)

async def main():
    nina = NinaOS()
    await nina.start()
    await asyncio.Event().wait()   # keep alive forever

if __name__ == "__main__":
    acquire_lock()
    asyncio.run(main())

```

---

### `nina_sync.sh`

```bash
#!/usr/bin/env bash
# nina_sync.sh v5 — Full post-session sync + built-in MD scan (Step 7)
# D-12: skip git push when Jules PR branches are open to prevent merge conflicts

set -euo pipefail

PATH="$HOME/bin:$PATH"

NINA=~/nina
SPACE_DIR="$NINA/docs/space"
LOGS_DIR="$NINA/logs"
DRY_RUN=false
[ "${1:-}" = "--dry-run" ] && DRY_RUN=true

SPACE_FILES=(
  AGENTS.md
  WORKFLOW.md
  docs/space/nina_error_register.md
  docs/space/nina_exporter_contract.md
  docs/space/nina_state.md
)

TS=$(date '+%Y-%m-%d %H:%M')
DATE=$(date '+%Y-%m-%d')

echo "================================================"
echo " NINA POST-SESSION SYNC  $TS$([ "$DRY_RUN" = true ] && echo " [DRY-RUN]")"
echo "================================================"

cd "$NINA"

_tg_notify() {
  local msg="$1"
  local token user_id
  token=$(grep -E '^TELEGRAM_BOT_TOKEN=' "$NINA/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' || true)
  user_id=$(grep -E '^AUTHORIZED_USER_ID=' "$NINA/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' || true)
  if [ -n "$token" ] && [ -n "$user_id" ]; then
    curl -s -X POST "https://api.telegram.org/bot${token}/sendMessage" \
      -d "chat_id=${user_id}" -d "text=${msg}" > /dev/null 2>&1 || true
  fi
}

echo "[0/8] Health check..."
BAD_FILES=$(find "$NINA" -maxdepth 1 \( -name "*-*.md" -o -name "*-*.sh" \) 2>/dev/null || true)
if [ -n "$BAD_FILES" ]; then
  echo "  ⚠  Hyphenated filenames — auto-renaming to snake_case:"
  while IFS= read -r bad; do
    good=$(basename "$bad" | sed 's/-/_/g')
    echo "     $(basename $bad) → $good"
    [ "$DRY_RUN" = false ] && git mv "$(basename $bad)" "$good" 2>/dev/null || true
  done <<< "$BAD_FILES"
else
  echo "  ✓ Naming convention consistent"
fi

SVC_STATUS=$(systemctl is-active nina 2>/dev/null || echo "unknown")
[ "$SVC_STATUS" = "active" ] && echo "  ✓ nina.service running" || echo "  ⚠  nina.service is $SVC_STATUS"

git fetch origin --quiet 2>/dev/null || true
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
[ "$BEHIND" -gt 0 ] && echo "  ⚠  $BEHIND commit(s) behind origin/main" || echo "  ✓ In sync with origin/main"

echo "[1/8] Auto-fetch from Downloads..."
FETCHED=0
for f in "${SPACE_FILES[@]}"; do
  SRC="$HOME/Downloads/$(basename "$f")"; DST="$NINA/$f"
  if [ -f "$SRC" ]; then
    if ! diff -q "$SRC" "$DST" > /dev/null 2>&1; then
      echo "  ↓ $f (updated from Downloads)"
      [ "$DRY_RUN" = false ] && cp "$SRC" "$DST"
      FETCHED=$((FETCHED+1))
    else
      echo "  = $f (Downloads copy identical)"
    fi
  fi
done
[ "$FETCHED" -eq 0 ] && echo "  (no new Downloads files)"

echo "[2/8] Mirror to docs/space/..."
[ "$DRY_RUN" = false ] && mkdir -p "$SPACE_DIR"
for f in "${SPACE_FILES[@]}"; do
  SRC="$NINA/$f"; DST="$SPACE_DIR/$(basename "$f")"
  if [ ! -f "$SRC" ]; then echo "  ✗ MISSING: $f"; continue; fi
  if [ ! -f "$DST" ] || ! diff -q "$SRC" "$DST" > /dev/null 2>&1; then
    echo "  ✓ $f (updated)"; [ "$DRY_RUN" = false ] && cp "$SRC" "$DST"
  else
    echo "  = $f (unchanged)"
  fi
done
for lf in nina_update_log.md nina_problem_log.md; do
  if [ -f "$LOGS_DIR/$lf" ] && [ -f "$NINA/$lf" ]; then
    if ! diff -q "$LOGS_DIR/$lf" "$NINA/$lf" > /dev/null 2>&1; then
      echo "  ✓ $lf (synced from logs/)"; [ "$DRY_RUN" = false ] && cp "$LOGS_DIR/$lf" "$NINA/$lf"
    fi
  fi
done

echo "[3/8] Backup cleanup..."
OLD_FILES=$(find "$NINA/upgrades/backups" -maxdepth 3 \
  \( -name "*.bak" -o -name "*.fix" -o -name "*.save" \) -mtime +30 2>/dev/null || true)
if [ -n "$OLD_FILES" ]; then
  COUNT=$(echo "$OLD_FILES" | wc -l | tr -d ' ')
  echo "  🗑  $COUNT stale file(s) >30 days old"
  if [ "$DRY_RUN" = false ]; then
    echo "$OLD_FILES" | xargs rm -f && echo "  ✓ Cleaned"
  else
    echo "  (dry-run: would delete)"
  fi
else
  echo "  ✓ No stale backup files"
fi

echo "[4/8] Update log entry..."
LAST_ENTRY=$(grep -c "^## Entry" "$NINA/nina_update_log.md" 2>/dev/null || echo "0")
NEXT_NUM=$(printf '%03d' $((LAST_ENTRY + 1)))
CHANGED_FILES=$(git status --porcelain 2>/dev/null | awk '{print $2}' | tr '\n' ',' | sed 's/,$//' || echo "none")
if [ "$DRY_RUN" = false ] && [ -n "$CHANGED_FILES" ] && [ "$CHANGED_FILES" != "none" ]; then
  python3 - << PYEOF
lines = [
    "",
    "---",
    "",
    "## Entry $NEXT_NUM — $DATE · D-sync Post-session sync",
    "",
    "**Triggered by:** nina_sync.sh v5 automated run",
    "",
    "**Files changed:** $CHANGED_FILES",
    "",
    "**Verification:** git push OK, nina.service $SVC_STATUS",
    "",
]
entry = chr(10).join(lines)
for path in ["$NINA/nina_update_log.md", "$LOGS_DIR/nina_update_log.md"]:
    try:
        open(path, "a").write(entry)
    except Exception:
        pass
print("  ✓ Log entry appended (Entry $NEXT_NUM)")
PYEOF
else
  echo "  = No changes to log"
fi

echo "[5/8] Staging..."
if [ "$DRY_RUN" = false ]; then
  git add docs/space/ "${SPACE_FILES[@]}" nina_sync.sh 2>/dev/null || true
  git add -u 2>/dev/null || true
fi

echo "[6/8] Committing and pushing..."
if [ "$DRY_RUN" = true ]; then
  echo "  (dry-run: skipping commit)"
else
  STAGED=$(git diff --cached --name-only 2>/dev/null || true)
  if [ -n "$STAGED" ]; then
    echo "  Changed files:"; echo "$STAGED" | sed 's/^/     /'
    git commit -m "docs: post-session sync $TS"

    # D-12: Check for open Jules PR branches before pushing to main
    # This prevents nina_sync.sh from moving main ahead of Jules branches
    # and causing merge conflicts on all open Jules PRs.
    JULES_BRANCHES=$(gh pr list --state open --json headRefName --limit 100 2>/dev/null | jq '[.[] | select(.headRefName | (startswith("jules-") or startswith("nina-j") or startswith("feat/") or startswith("pr-")))] | length' 2>/dev/null || echo "0")
    if [ "$JULES_BRANCHES" -gt 0 ]; then
      echo ""
      echo "  ⚠️  PUSH SKIPPED — $JULES_BRANCHES open Jules PR branch(es) detected on origin."
      echo "     Pushing now would cause merge conflicts on open Jules PRs."
      echo "     → Merge or close all Jules PRs first, then run: cd ~/nina && git push origin main"
      echo ""
      _tg_notify "⚠️ NINA sync [$TS] — Push SKIPPED: $JULES_BRANCHES Jules PR branch(es) open. Merge/close PRs first, then push manually."
    else
      git push origin main
      STAT=$(git show --stat HEAD | tail -1)
      echo "  ✓ Pushed — $STAT"
      _tg_notify "✅ NINA sync [$TS]
$STAT
Service: $SVC_STATUS"
    fi
  else
    echo "  Nothing to commit"
    _tg_notify "ℹ️ NINA sync [$TS] — nothing to commit. Service: $SVC_STATUS"
  fi
fi

echo "[7/8] Doc/config coverage scan..."
echo "  ── All .md/.txt/.json files in ~/nina (excl. venv/.git/exports/backups) ──"

COVERED_BASES=()
for f in "${SPACE_FILES[@]}"; do
  COVERED_BASES+=("$(basename "$f")")
done

ALL_MD=$(find "$NINA" \
  \( -path "*/venv/*" -o -path "*/.git/*" -o -path "*/node_modules/*" \
     -o -path "*/upgrades/backups/*" -o -path "*/exports/*" \
     -o -path "*/__pycache__/*" \) -prune \
  -o \( -name "*.md" -o -name "*.txt" -o -name "*.json" \) -print | sort)

TOTAL=0; COVERED=0; UNCOVERED=0
UNCOVERED_LIST=""

while IFS= read -r filepath; do
  [ -z "$filepath" ] && continue
  rel="${filepath#$NINA/}"
  base=$(basename "$filepath")
  lines=$(wc -l < "$filepath" 2>/dev/null || echo "?")
  mtime=$(stat -c "%y" "$filepath" 2>/dev/null | cut -d'.' -f1 || echo "?")
  TOTAL=$((TOTAL+1))

  IN_SPACE=false
  if [ -f "$SPACE_DIR/$base" ]; then
    IN_SPACE=true
  fi
  for cb in "${COVERED_BASES[@]}"; do
    [ "$cb" = "$base" ] && IN_SPACE=true
  done

  if [ "$IN_SPACE" = true ]; then
    echo "  ✅  $rel  ($lines lines, $mtime)"
    COVERED=$((COVERED+1))
  else
    echo "  ⚠️   $rel  ($lines lines, $mtime)  ← NOT in docs/space or SPACE_FILES"
    UNCOVERED=$((UNCOVERED+1))
    UNCOVERED_LIST="$UNCOVERED_LIST\n  • $rel"
  fi
done <<< "$ALL_MD"

echo ""
echo "  ── Summary ──"
echo "  Total .md files : $TOTAL"
echo "  Covered         : $COVERED"
echo "  NOT covered     : $UNCOVERED"
if [ "$UNCOVERED" -gt 0 ]; then
  echo ""
  echo "  ⚠️  Files not in docs/space (not uploaded to Perplexity):"
  echo -e "$UNCOVERED_LIST"
  echo ""
  echo "  → Add them to SPACE_FILES array in nina_sync.sh if needed."
fi
echo "[8/8] Full master export for Perplexity Space..."
if [ "$DRY_RUN" = true ]; then
  echo "  (dry-run: skipping)"
else
  # Step 8: Call the compact exporter Python script
  python3 "$NINA/tools/compact_exporter.py"
  FIXED_FILE="$HOME/Downloads/nina_space_upload/nina_latest.md"

  SIZE=$(wc -c < "$FIXED_FILE" | tr -d ' ')
  echo ""
  echo "  ╔══════════════════════════════════════════════╗"
  echo "  ║  ✅  UPLOAD TO PERPLEXITY SPACE:             ║"
  echo "  ║      nina_latest.md  (${SIZE} bytes)         ║"
  echo "  ║      ~/Downloads/nina_space_upload/          ║"
  echo "  ╚══════════════════════════════════════════════╝"
  echo ""

  if command -v rclone >/dev/null 2>&1 && rclone listremotes 2>/dev/null | grep -q "gdrive:"; then
    rclone copy "$FIXED_FILE" "gdrive:nina-backup/" --no-traverse 2>/dev/null && \
      echo "  ☁️  Synced to Google Drive: gdrive:nina-backup/nina_latest.md" || \
      echo "  ⚠️  rclone upload failed (sync still complete)"
  fi
fi

echo "================================================"
echo " SYNC COMPLETE  $TS"
echo "================================================"

```

---



## Appendix Pointers

- **Full Update Log Archive:** `exports/nina_update_log_archive_2026-05.md` (Contains the history of entries 001 to 093)
- **Full Error Register Archive:** `exports/nina_error_register_archive.md` (Contains all historically FIXED entries)
- **Exports Directory:** `exports/` (Contains backups and problem log archives)
- **Handoff/Baseline Configurations:** `upgrades/.guardian_handoff.json` and `upgrades/guardian_baseline.json`

## Mega-Task Index

| v# | Codename | Status | Summary |
|:---|:---|:---|:---|
| 4.0 | NINA-Evolve | 🔄 ACTIVE | Autonomous self-optimization loop via performance metrics. |
| 5.0 | Lightning Sync | 🔄 ACTIVE | Incremental backup system reducing sync latency by 60%. |
| 6.0 | Ghost Context | ⏳ PENDING | Symbol maps and diffs to eliminate context tax. |
| 10.0 | Sovereign NINA | ⏳ PENDING | Total autonomous self-maintenance and weekly reporting. |
