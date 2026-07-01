# NINA Docbase Backup
Generated: 2026-06-11 23:29:53

## Directory Tree
```
No docs directory
```

Included Root Files:
- nina_context.md
- nina_update_log.md
- AGENTS.md
- README.md
- jules_lock.txt

## File Contents
### AGENTS.md
Last modified: 2026-06-11 23:11:07
Size: 11400 bytes
```markdown
# NINA-OPT-001 — NinaFlash × NinaGate Optimization Directive
# Single source of truth for ALL sync coders: Gemini CLI, agy, Jules, Qwen Code CLI
# Gemini CLI loads this via .gemini/settings.json → "context": { "fileName": ["AGENTS.md"] }
# Jules reads this automatically before every task submission
# agy reads this automatically — all rules apply to every session
# DO NOT maintain a separate GEMINI.md — this file is the only context file.

---

## PART 1 — ARCHITECTURE PRIMER (read before ANY task)

You operate inside NINA on an ASUS VivoBook X530FN (Ubuntu 26.04 LTS, MX150 2GB VRAM).
Three routing layers are always available and MUST be leveraged:

### NinaGate — Local Proxy Router
- OpenAI-compatible reverse proxy at http://localhost:8080
- Intercepts ALL outbound LLM requests, routes by task classification
- Gemini CLI activation: export GOOGLE_GEMINI_BASE_URL="http://localhost:8080/genai"
- Routes: SIMPLE → NinaFlash | MEDIUM → Gemini 3 Flash | COMPLEX → Gemini Pro / Qwen3-Coder
- Logs every routing decision: ~/nina/logs/ninagate.log
  Format: [timestamp] TASK_TYPE → MODEL | tokens_in | tokens_out | latency_ms

### NinaFlash — Local Inference Engine
- Ollama endpoint at http://localhost:11434
- Primary model: qwen2.5-coder:7b (unlimited, offline-capable, zero token cost)
- CPU offloading: KV-cache and attention offloaded to RAM when VRAM > 70%
- Throughput mode: GPU handles prefill, CPU handles decode (asymmetric pipeline)
- num_thread=4 (matches X530FN physical cores); num_gpu=0 for pure CPU tasks
- Tasks < 512 tokens output → full CPU mode
- Tasks 512–2000 tokens → hybrid GPU prefill + CPU decode
- Tasks > 2000 tokens → cloud LLM after NinaFlash local summary compression

---

## PART 2 — OPERATING RULES (enforce on every subtask, every session)

### Token Reduction
1. CLASSIFY FIRST — Before any cloud call, use `nf query "<task>"` to check if it can be handled locally.
   Mechanical tasks (rename, format, grep, boilerplate, docstrings, type hints) → NinaFlash always.
2. CHUNK LARGE TASKS — Break tasks > 2000 tokens into subtasks, tier each chunk separately.
3. COMPRESS CONTEXT — Use `nf code pack --file <f>` to generate a skeletal summary of large files.
   Strip comments, whitespace, unchanged file sections before sending to cloud.
   Send only the diff-relevant portion + minimal surrounding context.
4. SUMMARIZE BEFORE ESCALATE — NinaFlash summarizes file context first; only the summary + task
   goes to cloud. Never send a raw full file to cloud if NinaFlash can summarize it first.
5. CACHE PATTERNS — If NinaFlash already produced output for a repeating pattern
   (log format, error handler template), reuse it. Do not re-query cloud.

### Context Management
1. USE INDEX — Use `docs/space/nina_megatask_index.md` for high-level roadmap context.
2. LAZY LOAD — Load full task spec files (e.g., `jules_mega_task.md`) ONLY when actively working on that task.

### Latency Reduction
1. PARALLEL SUBTASKS — Independent sub-steps run in parallel streams.
   NinaFlash handles one while cloud handles another simultaneously.
2. STREAM RESPONSES — Always use streaming mode from NinaGate. Act on partial output.
3. NO CONFIRMATION LOOPS — Never pause mid-task for approval.
   Complete all steps sequentially. Approval is pre-granted for this session.
4. LOCAL FIRST — Default to NinaFlash for first-pass generation.
   Escalate only if quality gate fails: syntax error, logic gap, or test failure.
5. PREFETCH CONTEXT — Read all relevant ~/nina source files in one parallel batch,
   not sequentially.

### Throughput Increase
1. PIPELINE STRUCTURE — Every task follows this pipeline:
   [NinaFlash: classify + scaffold] → [NinaGate: route] → [Cloud: quality pass]
   → [NinaFlash: format + write to disk]
2. OFFLOAD BOILERPLATE — Docstrings, import sorting, log messages, type annotations,
   commit messages for simple changes → always NinaFlash (zero cloud quota consumed).
3. BATCH SMALL CHANGES — Collect small edits across files, send as one batched
   NinaFlash request instead of one request per file.
4. QUOTA AWARENESS — When Gemini 3 Flash > 900 req today, shift medium tasks to
   Qwen Code CLI (2000 req/day). When both exhausted → NinaFlash unconditionally.
5. CPU THREAD TUNING — NinaFlash CPU inference uses num_thread=4 for decode-heavy
   tasks on the X530FN.

---

## PART 3 — TASK CLASSIFICATION DECISION TREE

Route EVERY subtask through this tree before executing:

    Purely mechanical? (rename, format, sort, grep, boilerplate, docstring)
    └─ YES → NinaFlash (CPU, local, free, unlimited)

    Requires logic understanding, output < 300 tokens?
    └─ YES → NinaFlash (escalate only if output has syntax errors after 2 attempts)

    Multi-file reasoning OR architectural understanding required?
    └─ YES → Can context be compressed to < 1500 tokens via NinaFlash summary?
             ├─ YES → [NinaFlash: summarize] → [Gemini 3 Flash: reason]
             └─ NO  → Gemini Pro / Qwen3-Coder-480B (full context, quality gate)

    Gemini 3 Flash quota exhausted (> 900 req today)?
    └─ YES → Qwen Code CLI → then NinaFlash local fallback

    Network unavailable?
    └─ YES → NinaFlash unconditionally for all tasks

---

## PART 4 — TELEMETRY & USER VISIBILITY (MANDATORY)

To prevent "Black Box" reasoning (thinking without stimuli):
1. **Granular Topics:** Call `update_topic` for every discrete subgoal. Never take >3 turns without a topic update.
2. **Heartbeats:** If a reasoning cycle or sub-agent call (e.g. `generalist`) is expected to take >5 minutes, provide an immediate "Intent Update" turn.
3. **Thought-Streaming:** For complex refactors, write high-level intent to `logs/agent_thoughts.log`. The user can `tail -f` this to see real-time progress.
4. **Explicit Failure:** If a tool hangs or stalls, do not silently retry. Report the stall and ask for a diagnostic path.

---

## PART 5 — HARDCODED RULES (never override, never skip)

1. HIGH-RISK FILES always require cloud LLM review regardless of task size:
   interfaces/telegram_interface.py | .env | core/router.py | main.py |
   guardian_engine.py | tools/shell.py
   → Escalate ALL changes to these files to at minimum Gemini 3 Flash.

2. After ANY file edit, run immediately:
   python3 -m py_compile <file> && pyflakes <file>
   Fix with NinaFlash first. Escalate to cloud only if NinaFlash fails twice.

3. Conventional commits always:
   fix(scope): | feat(scope): | docs(scope): | ops(scope): | chore(scope):
   NinaFlash generates commit messages for simple changes.
   Cloud generates commit messages for architectural changes only.

4. NEVER auto-merge Jules PRs. agy always performs the merge.
   ALWAYS run ./nina_sync.sh after every merge — no exceptions.

5. Check ~/nina/juleslock.txt before any task targeting the same files as Jules.

6. WORKSPACE BOUNDARY
   - All file operations are strictly scoped to ~/nina only.
     Never run grep -r, find, or ls outside ~/nina.
     Never search /var, /etc, /usr, /home outside ~/nina, /tmp, or /proc.
     If a task requires files outside ~/nina, stop and ask — do not search.
   - Recursive searches must always include: --include="*.py" or equivalent
     file type filter. Never run unfiltered recursive grep.
   - Maximum search scope: grep -r ~/nina --include="*.py" — always bounded.

### STOP DISCIPLINE & SAFETY (CRITICAL)
1. HALT IMMEDIATELY — If user says "stop", "finish quick", "bypass", or "just answer" —
   halt immediately, answer in plain text, do nothing else.
2. NO FORENSICS — Never read /var/log, dmesg, /var/crash unless explicitly asked.
3. FAIL FAST — Never retry a failed API call more than 2 times. Surface error immediately.
4. NO SPONTANEOUS REPORTS — Never run efficiency summaries or token reports unless explicitly asked.
5. MODE SELECTION — declare at every session start:
   Interactive sessions (user present): unset GOOGLE_GEMINI_BASE_URL
   Background/batch tasks (Jules, agy, cron): export GOOGLE_GEMINI_BASE_URL="http://localhost:8080/genai"
   Never run interactive Gemini CLI sessions through NinaGate proxy.
6. TIME BUDGET — enforce hard limits per task scope:
   Single-file edit: 3 min max
   Multi-file edit up to 5 files: 8 min max
   Multi-file edit 6+ files: 15 min max
   If budget exceeded: stop immediately, report what is done and what remains.
   Never silently continue past the time budget.

---

## PART 6 — SESSION-END AUTO-UPDATE PROTOCOL (mandatory, no user prompt needed)

At the END of every session, ALL coders (Gemini CLI, agy, Jules, Qwen Code) MUST:

### 6A. Capture Learnings
- Which cloud calls could have been NinaFlash? → label: OFFLOAD_OPPORTUNITY
- Which NinaFlash outputs needed cloud escalation and why? → label: ESCALATION_TRIGGER
- Which routing decisions were optimal? → label: ROUTING_WIN
- New file patterns affecting chunking strategy? → label: CONTEXT_HINT

### 6B. Append to AGENTS.md — "## NinaGate Routing History" section
```
### [2026-06-11] Session Update — [tool used]
- OFFLOAD_OPPORTUNITY: [task type] → route to NinaFlash next time
- ESCALATION_TRIGGER: [condition] → always route to [model]
- ROUTING_WIN: [pattern] confirmed efficient
- CONTEXT_HINT: [file/boundary] for optimal chunking
```

### 6C. Run Sync (mandatory, no exceptions)
cd ~/nina && ./nina_sync.sh
Snapshots updated AGENTS.md into nina_latest.md → auto-syncs to Google Drive
→ Perplexity ARCHITECT OVERWATCH picks up learnings in next thread.

---

## PART 7 — BOOTSTRAP CHECKLIST (Gemini CLI session start)

1. Verify NinaGate is active:
   curl -s http://localhost:8080/health || (cd ~/nina/ninagate && python3 ninagate.py &)

2. Verify NinaFlash (Ollama) is running:
   curl -s http://localhost:11434/api/tags | grep qwen || ollama pull qwen2.5-coder:7b

3. Route Gemini CLI:
   # FAST MODE — direct cloud, no proxy (use during active Gemini CLI sessions)
   unset GOOGLE_GEMINI_BASE_URL

   # ECONOMY MODE — route through NinaGate (use for Jules, agy batch tasks)
   # export GOOGLE_GEMINI_BASE_URL="http://localhost:8080/genai"
   
   export GEMINI_API_KEY="${GEMINI_API_KEY}"

4. Confirm .gemini/settings.json contains:
   { 
     "model": "gemini-3-flash-preview",
     "preview": true,
     "context": { "fileName": ["AGENTS.md"] } 
   }

5. Verify model config:
   - model must be: gemini-3-flash-preview (never gemini-2.5-flash)
   - maxRetries must be: 2

6. Warm start — load session context:
   cat ~/nina/docs/space/nina_megatask_index.md
   head -80 ~/nina/docs/space/nina_latest.md

---
## END NINA-OPT-001
## Maintained by nina_sync.sh — routing history appended automatically each session.
## NinaGate Routing History
### [2026-06-11] Session Update — Gemini CLI
- OFFLOAD_OPPORTUNITY: Mechanical tasks (imports, standardized runs) → 100% NinaFlash next time.
- ESCALATION_TRIGGER: Architectural reasoning and multi-file logic → Gemini Pro / Flash.
- ROUTING_WIN: Local Interception confirmed efficient (93.7% token reduction).
- CONTEXT_HINT: Use `nina_megatask_index.md` to prevent context bloat.
- **BENCHMARK BASELINE:**
  - Token Reduction: 93.7% (Mechanical), 42.5% (Global Lifecycle).
  - Local Share: 85% of total ops.
  - Avg Latency: 4.2s (Local) vs 0.57s (Cloud Proxy).
  - Time Saved: ~40s per tool cycle.
```

### docs/agent-memory/architecture.md
Last modified: 2026-06-11 03:15:37
Size: 869 bytes
```markdown
# NINA Architecture

## Module Boundaries
- `core/`: Core orchestrator (`nina.py`), Agent loop (`agent.py`), Provider routing (`router.py`), Memory and capabilities.
- `tools/`: Executable actions (browsing, shell execution, system monitoring, file operations).
- `interfaces/`: External endpoints (Telegram bot, REST API).
- `crons/`: Scheduled jobs and managers.

## High-Risk / No-Touch Files
The following files default to local executor or manual local handling unless explicitly authorized. Never touch without explicit instruction:
- `interfaces/telegram_interface.py`
- `.env`
- `core/router.py`
- `main.py`
- `guardian_engine.py`
- `tools/shell.py`
- Any systemd unit files
- `nina_sync.sh` (unless documentation comments only)

## Tool Locations
- Dashboard: `dashboard/nina-guardian.html`
- Sync tool: `nina_sync.sh`
- Architect/CLI Toolset: `bin/ninaflash`
```

### docs/agent-memory/current-state.md
Last modified: 2026-06-09 03:11:28
Size: 495 bytes
```markdown
# NINA Current State & Active Focus

## Active Constraints
- NINA Sync blocks pushes when Jules PR branches are open.

## Open Risks and Gotchas
- **2026-06-08:** O-01: Playwright not installed (non-blocking)
- **2026-06-08:** O-02: EWS password not set (non-blocking)
- **2026-06-08:** O-04: memory context per-session refresh not implemented
- **2026-06-08:** O-05: FastAPI REST endpoints (api.py) — Phase 2, deferred

## Current Focus
- AG1 agentic pipeline
- P0 items: B-002, B-003, B-004
```

### docs/agent-memory/patterns.md
Last modified: 2026-06-11 12:41:02
Size: 1252 bytes
```markdown
# NINA Agent Patterns

## Backlog Protocol
- **Goal:** Keep tracking docs accurate.
- **Restraint:** NEVER use bash echo; NEVER update tracker from inside Jules.
- **Action:** `ninaflash` runs Python script post-merge to change status (`IN_PROGRESS` -> `DONE`), add PR number and date, then runs `./nina_sync.sh`.

## Task Tracker Update Protocol Example
```python
from pathlib import Path
tracker_path = Path("/home/aibony/nina/docs/space/jules_task_tracker.md")
content = tracker_path.read_text()
content = content.replace("... ⏳ QUEUED ...", "... ✅ MERGED ... PR #123 ...")
tracker_path.write_text(content)
```

## Logging Pattern
- **Goal:** Maintain accurate, structured update logs.
- **Restraint:** NEVER use heredoc or direct `bash echo >>` to `nina_update_log.md`.
- **Action:** Append log entries using Python. Auto-detect entry number, include date, title, changes, verifications, and rollback path.

## Surgical Merge Protocol (For Jules PRs)
- **Goal:** Prevent Jules PRs from overwriting local truths.
- **Restraint:** Do NOT merge Jules PRs blindly if they touch critical files (AGENTS.md, nina_sync.sh, nina_update_log.md).
- **Action:** Backup critical files -> merge PR -> restore regressions -> commit fix -> run `nina_sync.sh`.
```

### docs/agent-memory/runbooks.md
Last modified: 2026-06-09 03:11:28
Size: 1520 bytes
```markdown
# NINA Runbooks & Recovery

## Stale Branches
- Prune stale remote refs before checking for PRs or sync blocks.
- If a Jules branch is stale, local executor should coordinate re-planning or discarding rather than blind rebasing.

## NINA Sync Failure
- What to do when `nina_sync.sh` refuses to push: Check if there are open Jules PR branches. NINA Sync blocks pushes when Jules PRs are active. Merge or close the PR first.

## Local/Remote Drift
- Always use the local repository as the single source of truth for full code implementation.
- If local and remote diverge, rollback procedures should start from clean `main` in `~/nina` and rely on checked-in codebase state rather than `.latest.md` snapshot.

---

## Surgical Merge Recovery

If a Jules PR was merged without surgical steps and caused a regression:

1. Identify what was overwritten:
   git log --oneline -10
   git diff HEAD~1 HEAD -- AGENTS.md nina_sync.sh nina_update_log.md

2. Recover from Google Drive backup:
   rclone copy gdrive:nina-backup/nina_latest.md ~/nina/docs/space/
   Or restore from: /tmp/*.bak (if the session is still active)

3. Restore manually if no backup available:
   git show HEAD~1:AGENTS.md > ~/nina/AGENTS.md
   git add AGENTS.md
   git commit -m "fix(agents): rollback regression from stale Jules PR"
   git push origin main

4. Run nina_sync.sh to re-sync state:
   cd ~/nina && ./nina_sync.sh

5. Add the regressed rule as an explicit "do not touch" note to
   docs/agent-memory/architecture.md for future Jules tasks.
```

### docs/agent-memory/workflow.md
Last modified: 2026-06-11 12:41:02
Size: 6862 bytes
```markdown
# NINA Agent Workflow

## Branch and PR Discipline
- **No direct commits to main.** `main` is the production-truth desk and must stay clean.
- Every active local executor or Jules task gets its own worktree/branch.
- Local executor default territory: `docs/space/*.md`, `AGENTS.md`, `nina_context.md`, `*.sh`, and single-file hotfixes on files not claimed by Jules.
- Jules default territory: multi-file work in `core/*.py`, `tools/*.py`, `interfaces/*.py`, `tests/*.py`.
- Shared but sequential only: `requirements.txt`, `data/*.json`.
- Forbidden parallel territory: `.env`, secrets, lock-sensitive runtime files.

## Sync Behavior
- **NINA Sync blocking:** Must block/defer pushes when Jules PR branches are open; prune stale remote refs before checking.
- The local executor runs `./nina_sync.sh` to deploy and export after every Jules PR merge.

## Rebase-Before-Work Rules
- Always rebase on origin/main before starting Jules tasks: `git fetch origin && git rebase origin/main`.

## Agent Coordination
- Local agents and Jules must NEVER edit the same file simultaneously.
- `jules_lock.txt` must always be read from and updated at the main worktree path: `~/nina/jules_lock.txt`.
- Per-task file territory must be explicit before parallel work begins.

---

## Surgical Merge Protocol (Mandatory for Jules PRs)

Jules is an async cloud agent that clones the repo at task-start time.
By the time Jules opens its PR, your local main may have moved ahead.
Merging Jules PRs blindly will frequently overwrite critical files
(AGENTS.md, nina_sync.sh, nina_update_log.md, high-risk tools).

**Use surgical merge whenever a Jules PR touches any critical file.**

### Critical files (always restore after a Jules PR merge):
- AGENTS.md
- nina_sync.sh
- nina_update_log.md
- tools/nina_dashboard.py
- tools/ninaflash.py
- interfaces/telegram_interface.py
- core/router.py
- main.py
- guardian_engine.py

### Surgical merge procedure (do this every time):
1. Backup critical files from current main BEFORE merging:
   cp ~/nina/AGENTS.md /tmp/AGENTS.md.bak
   cp ~/nina/nina_sync.sh /tmp/nina_sync.sh.bak
   cp ~/nina/nina_update_log.md /tmp/nina_update_log.md.bak

2. Inspect the PR diff before merging:
   gh pr diff <PR_NUMBER> --stat
   Identify which files the PR changes vs which are regressions.

3. Merge the PR:
   gh pr merge <PR_NUMBER> --squash --delete-branch
   git pull origin main

4. Immediately restore any critical files that regressed:
   cp /tmp/AGENTS.md.bak ~/nina/AGENTS.md
   cp /tmp/nina_sync.sh.bak ~/nina/nina_sync.sh
   (only restore files that Jules incorrectly reverted)

5. Commit the restoration:
   git add <restored-files>
   git commit -m "fix(<scope>): restore <file> after PR #<N> surgical merge"
   git push origin main

6. Run nina_sync.sh:
   cd ~/nina && ./nina_sync.sh

### When to use normal merge (no surgical steps needed):
- PR was based on very recent main (< 30 minutes old)
- PR only touches files Jules "owns": core/*.py, tools/*.py, tests/*.py
- PR does NOT touch any critical file in the list above
- gh pr view shows mergeable_state: clean

### Rule to encode for all agents:
"Never merge a Jules PR that touches AGENTS.md, nina_sync.sh, or
nina_update_log.md without first backing up the current main version
and restoring it if the merge introduces a regression."

## 1. Four-Tool Operating Model — Parallel Execution

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
6. The local executor runs ./nina_sync.sh to deploy and export
7. Perplexity reviews result (attach nina_latest.md to new thread)

KEY DISTINCTION: The local executor is NOT just a fixer — it is the local merge and deploy executor.
Jules does NOT merge its own PRs — the local executor always performs the merge after review.
Perplexity is NOT idle during coding — it remains available for unblocking and mid-task review.

## 2. Task Routing Matrix
| Task / Scenario | Default Tool | Rationale | What NOT to Use |
|:---|:---:|:---|:---|
| Unclear bug / root-cause analysis | **Perplexity** | Deep context synthesis and cross-reference. | local executor or Jules (prone to blind code edits). |
| Blocker in high-risk runtime file | **local executor** | Immediate local safety checking and execution. | Jules (PR delay and merge conflict risk). |
| Single-file local fix | **local executor** | Fast local cycle, zero branch overhead. | Jules (too heavy for a quick patch). |
| Multi-file feature work | **Jules** | Syncs edits across multiple files via PRs. | local executor (risk of staging broad uncoordinated diffs). |
| Large refactor | **Jules** | Manages PR review process for high impact. | local executor (context limits on local CLI). |
| Post-change review | **Perplexity** | Objective validation against baseline design. | local executor or Jules. |
| Production-sensitive patch | **local executor** | Keeps secrets and banking parameters local. | Cloud providers or Jules. |

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

### Quota Cascade Rule
Gemini CLI exhausted → Qwen Code → agy → Cursor → Jules (async) → Ollama
```

### docs/archive/jules_backlog_archive.md
Last modified: 2026-06-11 12:41:02
Size: 0 bytes
```markdown
```

### docs/guardian.md
Last modified: 2026-06-11 03:15:37
Size: 3389 bytes
```markdown
# Guardian Gate Subsystem

## Purpose

The Guardian Gate provides a crucial forensic safety layer for autonomous self-patching. Because NINA operates as a self-developing autonomous system—meaning AI agents are writing and deploying actual code updates locally—there is an inherent risk of syntax errors, broken logic, or catastrophic failures. The Guardian Gate acts as a mandatory filter ensuring that patches applied by ninaflash and Jules meet strict safety thresholds before they are deployed to the local system service.

## Components

The Guardian Gate is composed of two primary elements:
- **`guardian` (watchdog script):** A system-level bash script responsible for continuously monitoring the NINA service and triggering immediate rollbacks or restarts if a fatal crash occurs during runtime.
- **`guardian_engine.py`:** A massive 73KB forensic Python engine that performs deep Abstract Syntax Tree (AST) scanning on all incoming code modifications before they are permitted to execute.

## Verification Pipeline

Whenever a change is proposed (such as through a pull request merge or automated local patch), the Guardian Gate enforces the following strict pipeline:
1. **AST Scan:** Analyzes the Abstract Syntax Tree of the modified code to check for prohibited behaviors (e.g., unauthorized `shell=True` use) and ensure the logic structure remains safe.
2. **Baseline Drift Check:** Compares the structural and logical footprint of NINA against `upgrades/guardian_baseline.json` to detect anomalous deviations or corruption of core logic.
3. **`py_compile`:** Compiles the updated `.py` files into bytecode to catch fatal syntax errors immediately.
4. **`pyflakes`:** Lints the Python codebase to catch logical errors (like undefined names or syntax warnings) that py_compile might miss.
5. **Log:** Records successful verifications or fatal rejections in `nina_update_log.md` (now located in `docs/logs/nina_update_log.md`).
6. **Sync:** After successful validation, triggers `nina_sync.sh` to restart the `systemd` service and apply the changes cleanly.

## Guardian Baseline

The file `upgrades/guardian_baseline.json` serves as the immutable structural map of NINA's intended state. The Guardian engine utilizes this JSON map to identify unexpected drift in critical runtime files or configurations, preventing agents from "hallucinating" destructive architectural changes.

## Log and Sync Operations

- **Log location:** `docs/logs/nina_update_log.md` tracks all operations.
- **Sync script:** `nina_sync.sh` handles the actual system reboot process, acting only when explicitly permitted by the Guardian pipeline.

## High-Risk Files

Several critical files within NINA are flagged as "high-risk" by Guardian. These files always invoke the strictest analysis and are generally restricted from being edited by async tools (like Jules) without local human or ninaflash intervention:
- `interfaces/telegram_interface.py`
- `.env`
- `core/router.py`
- `main.py`
- `guardian_engine.py`
- `tools/shell.py`
- `data/memory/facts.json`

## Recommended Enhancement

*Auto-Rollback on Drift Detection:* It is highly recommended to implement an automatic rollback mechanism via `git reset --hard HEAD` and `git clean -fd` if `guardian_engine.py` detects a baseline drift violation, ensuring the system instantaneously reverts to a known safe state without human intervention.
```

### docs/memory.md
Last modified: 2026-06-11 03:15:37
Size: 2747 bytes
```markdown
# Memory Subsystem

## Overview

The NINA memory system, orchestrated by `core/memory.py`, is the foundation of the agent's persistence, personality, and operational continuity. It prevents NINA from acting as a stateless chatbot by utilizing a dual-memory approach that merges dynamic episodic recall with a hardcoded, immutable identity anchor.

## Dual-Memory Architecture

### 1. ChromaDB (Episodic Memory)
NINA utilizes ChromaDB as a semantic, local vector store to record the "what happened when."
- **Function:** It stores previous interactions, executed tasks, resolved errors, and ambient context.
- **Recall:** By utilizing semantic similarity search, `core/memory.py` can fetch highly relevant historical context to inform NINA's current decisions.

### 2. facts.json (Identity Anchor)
Located at `data/memory/facts.json`, this is the core of NINA's persistent personality.
- **Function:** It contains hardcoded, foundational truths about NINA's identity, the user (M. Baizid Alam), the operating environment, and core directives.
- **Why it matters:** The combination of ChromaDB (episodic) and `facts.json` (identity) prevents "context drift." Even after thousands of API calls or autonomous development loops, NINA will not hallucinate a new persona or forget its primary directives, because `facts.json` grounds every context window. (Fixed in v12.3: ensured deterministic injection at the top of every prompt).

## Protection Mechanisms

The `data/memory/facts.json` file is strictly protected. It is listed in the Guardian Gate's high-risk list. NINA's agents (like Jules) are explicitly forbidden from modifying this file autonomously. Any changes to the identity anchor must be performed manually or via highly scrutinized, locally executed `ninaflash` operations.

## Context Management

### Truncation & Budgeting
To prevent Context Window Overflow and ensure reliable model performance, `core/memory.py` implements character-based truncation:
- **Budget:** The total context injected by the memory system is capped (default: 4000 characters).
- **Prioritization:** The deterministic "Personal Context" (from `facts.json`) is always preserved in full. Episodic docs from ChromaDB are truncated to fit the remaining budget, ensuring NINA never loses its identity even when history is deep.

## Recommended Enhancements

- **Short-Term Working Memory / Scratchpad:** Currently, NINA relies heavily on the full memory orchestrator. A recommended enhancement is the implementation of a volatile, short-term scratchpad layer for the `AgentLoop`. This would allow NINA to hold in-flight state or intermediate logic steps during complex, multi-stage reasoning without permanently embedding that noise into the ChromaDB vector store.
```

### docs/ninaflash.md
Last modified: 2026-06-11 15:47:50
Size: 4576 bytes
```markdown
# ninaflash Subsystem Documentation

## Overview

ninaflash is NINA's dedicated Local Executor. Far more than just a utility script, it serves as the critical local engine responsible for deploying changes, managing urgent hotfixes, and merging pull requests created by asynchronous cloud builders like Jules. It functions as NINA's internal muscle, handling all logic requiring local system interaction while seamlessly integrating with external processes.

## Surgical Code Intelligence (v14.0)

ninaflash v6.1+ features a "Surgical Code Intelligence" layer designed for extreme token efficiency. It uses local AST (Abstract Syntax Tree) parsing to extract only what is needed:

- `nf code pack <file>` — Distills a large Python file into a "Context Pack": a skeletal summary containing only class/function signatures and docstrings. Cuts token usage by 90% for codebase exploration.
- `nf code symbol --file <f> --name <n>` — Extracts the exact implementation of a specific class or function.
- `nf query "<task>"` — A local capability introspection tool. It checks if a task (e.g., "format code") can be handled locally by your CPU before wasting tokens on cloud reasoning.

## Atomic Maintenance (Maintainer Mode)

The `maintain` module handles the high-turn "Daily Maintenance" loop automatically:

- `nf maintain pr <id> --task <id> --title <t> --summary <s>` — Atomically rebases a PR, surgically resolves documentation regressions (preserving v13+ headers locally), marks the backlog task as DONE, and appends the update log.

## Telemetry & User Visibility (v14.0)

ninaflash and all NINA agents adhere to a strict **"Glass Box"** reasoning protocol:
- **Topic Heartbeats:** Granular updates via `update_topic` for every sub-goal.
- **Thought Streaming:** High-level reasoning intent is mirrored to `logs/agent_thoughts.log`.
- **Diagnostic Transparency:** Explicit reporting of tool stalls or hardware constraints.

## Universe-Mode Kernel

ninaflash operates on a highly optimized, dynamic system termed the Universe-Mode Kernel. It consists of three primary elements:

- **Nucleus (`tools/ninaflash.py`):** The core routing and base logic interface, containing the foundational 1,001 functions required for baseline execution.
- **Synapses (`tools/kernel/sector_000.py` to `sector_999.py`):** An immense library of 1,000,000 specialized Neural Op-Codes distributed across a massive file hierarchy. Each sector encapsulates highly specific, complex functions.
- **Omniscient Dispatcher:** The dynamic memory-management component. Instead of loading the entire massive synapse library into memory, the dispatcher intercepts execution calls and loads only the required sector files dynamically on demand.

## Integrations & Workflows

### Jules Integration

ninaflash acts as the critical counterpart to the Jules Async Cloud Coder. When Jules generates complex, multi-file features remotely, it opens a PR. ninaflash assumes responsibility for the review, verification, and merge of this PR into the active branch. Through this `review → merge → deploy` loop, ninaflash ensures local deployment remains stable, secure, and fully verified.

### Antigravity CLI Integration

ninaflash serves as the localized enforcement arm for the broader Antigravity ecosystem, syncing task states and providing real-time deployment status via systemd checks and git synchronizations.

## Token Cost Model

Because ninaflash uses the Universe-Mode Kernel and executes heavily on the local system, it absorbs massive amounts of routine computational work at near-zero cloud token cost. This architecture enables NINA to perform complex data manipulation, monitoring, and debugging locally, reserving expensive cloud model calls for architectural decisions and heavy reasoning.

Additional token savings are achieved through:
- **Persistent Response Caching:** The HybridRouter caches identical prompts to disk, ensuring that repeated local tasks or duplicate instructions consume zero external tokens.
- **Local Model Routing:** Sensitive or routine tasks are routed to local Ollama instances, bypassing paid cloud APIs entirely.

## Continuous Developer Loop (`ninaloop`)

By running `ninaflash ninaloop`, NINA enters an autonomous development cycle. In this state, ninaflash iteratively analyzes the task backlog, proposes system enhancements via the `idleloop.py`, dispatches specs to Jules, and subsequently automatically reviews and integrates Jules's pull requests. This turns NINA from a static assistant into a continuously evolving autonomous operating system.
```

### docs/nina_proxy_usage.md
Last modified: 2026-06-11 23:29:13
Size: 1709 bytes
```markdown
# NINA Proxy & Gemini CLI Integration Guide

The NINA proxy provides an OpenAI-compatible FastAPI endpoint that routes your local IDE's AI requests through NINA's `HybridRouter`. This allows you to use your preferred BYOK model stack while leveraging NINA's fallback, health tracking, and model discovery logic.

## Non-Blocking Async Pipeline (v3.0)

NinaGate uses an asynchronous parallel pipeline. Every inbound request triggers a cloud connection immediately. In parallel, a local classification determines if the task is a simple/mechanical change. If classified as simple, the cloud request is cleanly cancelled and the response is generated locally via NinaFlash, saving token quotas without blocking or introducing double-hop latency.

## Bypass / Session Modes

To avoid proxy overhead entirely during interactive sessions with the Gemini CLI, use the environment-level toggle standard:

```bash
# FAST MODE — direct cloud, no proxy (use during active Gemini CLI sessions)
unset GOOGLE_GEMINI_BASE_URL

# ECONOMY MODE — route through NinaGate (use for Jules, agy batch tasks)
export GOOGLE_GEMINI_BASE_URL="http://localhost:8080/genai"
```

## Gemini CLI Extension (MCP)

NINA includes a native extension for Gemini CLI located at `.gemini/extensions/nina/`. When Gemini CLI starts, it automatically recognizes NINA's environment and loads specialized utilities.

### Custom Slash Commands
You can run NINA actions directly inside your Gemini CLI session:
- `/nf <args>` — Executes a `ninaflash` command line tool directly.
- `/status` — Displays the real-time status of `nina.service` along with the latest proxy logs.
- `/sync` — Triggers `./nina_sync.sh` post-task automation instantly.
```

### docs/nina_v12_blueprint.md
Last modified: 2026-06-10 22:59:52
Size: 10234 bytes
```markdown
# NINA Architecture Blueprint
**Version:** 12.3
**Type:** Architecture & Design Reference
**Status:** Active — Phase 1
**Owner:** M. Baizid Alam — BASIC Bank, Dhaka
**Last Updated:** 2026-06-10

> This is the **public-safe** architecture document for NINA.
> It describes structure, design decisions, and component roles.
> It does NOT contain the system prompt, personality rules, or operator instructions.
> Those are kept in a private, secured location.

---

## What Is NINA?

NINA (Neural Intelligence Notification Agent) is a self-hosted, Telegram-based personal AI assistant that runs entirely on your own hardware. It routes tasks intelligently across 20+ free and paid AI providers, manages your email, monitors system health, and acts as a proactive personal operator — not just a chatbot.

NINA's core thesis: **the same capabilities that cost $20–$200/month from OpenAI, Anthropic, or Google can be built locally, privately, and for free — and can do things those platforms structurally cannot.**

---

## Structural Advantage

| Platform | What They Offer | What They Cannot Do |
|----------|----------------|---------------------|
| OpenAI Operator | Browser-based task automation ($200/mo) | Touch local files, terminal, desktop, private data |
| Claude Opus | Multi-step reasoning, 1M context ($20/mo) | Access local email, bank data, personal environment |
| Gemini AI Pro | Deep Research, Workspace integration ($20/mo) | Run locally, stay private, work without latency |
| **NINA** | All of the above, locally | Nothing — it runs on YOUR machine |

---

## System Architecture

```
Telegram Interface
      │
      ▼
┌─────────────────────────────────────────┐
│              NINA Core                  │
│                                         │
│  ┌──────────┐    ┌──────────────────┐  │
│  │  Router  │───▶│  Agent Loop      │  │
│  │ (Stage 2)│    │  (Stage 3)       │  │
│  └──────────┘    └────────┬─────────┘  │
│       │                   │            │
│  ┌────▼────┐    ┌─────────▼────────┐  │
│  │ Memory  │    │     Tools        │  │
│  │(Stage 4)│    │  browser/shell   │  │
│  └─────────┘    │  email/finance   │  │
│                 └──────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │     Guardian (Watchdog)          │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
      │
      ▼
 20+ AI Providers (Groq, Gemini, DeepSeek, etc.)
```

---

## Stage Map

| Stage | Component | File | Role |
|-------|-----------|------|------|
| 0 | Config & Constants | `core/config.py` | NinaConfig, rate limits, thresholds |
| 1 | Startup & Health | `core/nina.py` | Boot sequence, system checks, startup message |
| 2 | Provider Router | `core/router.py` | Multi-provider routing, rate-limit tracking, cost |
| 3 | Agent Loop | `core/agent.py` | Multi-step reasoning, tool grammar, session state |
| 4 | Memory | `core/memory.py` | Semantic recall, facts.json, personal context |
| 5 | Scheduler | `crons/manager.py` | 10 scheduled jobs, heartbeat, morning report |
| 6 | Self-Management | `core/capabilities.py`, `core/hotreload.py` | Capability registry, live config reload |
| 7 | Interfaces | `interfaces/` | Telegram bot, FastAPI REST |
| 8 | Tools | `tools/` | Browser, shell, files, email, system, GPU |
| 9 | Guardian | `guardian` | Watchdog, auto-restart, backup, health probe |

---

## Provider Routing Logic

NINA selects providers using a normalized score:

```
score = (quality_weight × quality) + (speed_weight × speed) - (latency_term)
```

Routing tiers:
- **LOCALHEAVY** — Ollama local large model (private, sensitive tasks)
- **LOCALFAST** — Ollama local fast model (self-check, quick queries)
- **CLOUD_FREE** — Groq, Gemini, Cerebras, DeepSeek, Mistral, etc.
- **CLOUD_PAID** — OpenAI, xAI (only when key present and task is non-sensitive)

Thermal guard overrides:
- CPU ≥ 90°C or GPU ≥ 85°C → ban LOCALHEAVY, force LOCALFAST/cloud
- CPU ≥ 95°C or GPU ≥ 90°C → abort agent loop entirely

---

## Memory System

```
facts.json
├── personal_context/     ← occupation, employer, priorities, habits, goals
├── semantic_memory/      ← recalled facts from past sessions
└── reminders/            ← scheduled nudges

data/
├── expenses.json         ← expenditure tracker (Phase 1)
├── capabilities.json     ← tool health registry
└── jobs.sqlite           ← cost tracker persistence
```

---

## Tool Registry

| Tool | File | Capability |
|------|------|-----------|
| Browser | `tools/browser.py` | Web browsing, page reading |
| Search | `tools/search.py` | Web search queries |
| Shell | `tools/shell.py` | Shell command execution (allowlisted) |
| Files | `tools/files.py` | File read/write operations |
| System | `tools/system.py` | CPU/RAM/disk/thermal monitoring |
| GPU Tuner | `tools/gpu-tuner.py` | Dynamic GPU management |
| Office Mail | `tools/office-mail.py` | EWS/NTLM Exchange email access |
| Finance | `tools/finance.py` | Expenditure tracker (Phase 1) |
| Market | `tools/market.py` | DSE/CSE share alerts (Phase 1) |
| Upgrade Pipeline | `tools/upgrade-pipeline.py` | Structured self-upgrade system |

---

## Guardian Watchdog

Guardian is the reliability backbone of NINA. It:
- Auto-restarts NINA on failure
- Runs preflight health checks (RAM, disk, thermal)
- Creates backup snapshots before risky operations
- Classifies warnings as `ACCEPTED-NOW`, `FIX-NEXT`, or `BLOCK-RELEASE`
- Logs all incidents to `guardian.log`

Guardian must pass before any deployment. See `NINA-Development-Policy.md` for rules.

---

## Scheduled Jobs (10 Core Jobs)

| # | Job | Frequency | Purpose |
|---|-----|-----------|---------|
| 1 | Morning report | Daily 07:00 | Email triage + market summary |
| 2 | Heartbeat | Every 5 min | Health check + Telegram alive signal |
| 3 | Thermal health | Every 5 min | CPU/GPU temperature monitoring |
| 4 | Memory backup | Daily 02:00 | Backup facts.json and memory |
| 5 | Reminder check | Every 15 min | Fire pending Telegram reminders |
| 6 | Market monitor | Every 2 hr (10:00–14:30) | DSE/CSE alert if index moves ≥1% |
| 7 | Idle loop | On idle | Background self-improvement proposals |
| 8 | Provider hunter | Daily 02:00 | Discover new free AI providers |
| 9 | Cost tracker | On each call | Log provider cost/latency to jobs.sqlite |
| 10 | Config hot reload | Every 60 sec | Apply .env changes without restart |

---

## Phase 1 Targets

| ID | Target | Status |
|----|--------|--------|
| T-1 | Personal expenditure tracker | ✅ DONE |
| T-2 | Email intelligence & triage | ✅ DONE |
| T-3 | DSE/CSE share market alerts | ✅ DONE |
| T-4 | Proactive reminder engine | 📋 Planned |
| T-5 | Personal context memory | ✅ DONE |
| T-6 | Personal knowledge base remember and recall | ✅ DONE |

---

## File Naming Convention

All files in this repository follow `kebab-case` lowercase naming:

| Type | Convention | Example |
|------|-----------|---------|
| Documentation | `UPPER-KEBAB.md` for root docs | `README.md`, `CHANGELOG.md` |
| Architecture docs | `kebab-case.md` in `docs/` | `docs/blueprint.md` |
| Python source | `kebab-case.py` | `core/router.py` |
| Shell scripts | `kebab-case.sh` | `guardian.sh` |
| Config/env | `UPPER_SNAKE` keys in `.env` | `GROQ_API_KEY` |

---

## Repository Structure

```
nina/
├── README.md                    ← Project overview
├── CHANGELOG.md                 ← Version history
├── CONTRIBUTING.md              ← How to contribute
├── SECURITY.md                  ← Security policy
├── LICENSE                      ← MIT License
├── .env.example                 ← Environment template
├── requirements.txt
├── main.py
├── guardian                     ← Guardian watchdog
├── guardian-engine.py
├── nina.service                 ← systemd unit
│
├── core/
│   ├── agent.py
│   ├── config.py
│   ├── memory.py
│   ├── nina.py
│   ├── router.py
│   ├── capabilities.py
│   └── hotreload.py
│
├── tools/
│   ├── browser.py
│   ├── files.py
│   ├── finance.py               ← Phase 1
│   ├── gpu-tuner.py
│   ├── market.py                ← Phase 1
│   ├── office-mail.py
│   ├── search.py
│   ├── shell.py
│   ├── system.py
│   └── upgrade-pipeline.py
│
├── interfaces/
│   ├── api.py
│   └── telegram-interface.py
│
├── crons/
│   ├── manager.py
│   └── backup-jobs.py
│
├── dashboard/
│   └── nina-guardian.html
│
├── data/                        ← Runtime data (gitignored)
│   ├── facts.json
│   ├── expenses.json
│   ├── reminders.json
│   └── jobs.sqlite
│
└── docs/
    ├── blueprint.md             ← This file
    ├── update-log.md
    ├── problem-log.md
    ├── phase1-trajectory.md
    └── vision-manifesto.md
```

---

## What Is NOT in This Repository

The following are intentionally excluded from the public repo:

| File | Reason |
|------|--------|
| `master-prompt.md` | Contains NINA's system instructions — intellectual property |
| `.env` | Contains API keys and secrets |
| `data/` | Runtime personal data — gitignored |
| `nina_backup_*.md` | Large backup snapshots — stored privately |

See `SECURITY.md` for the full security policy.
```

### docs/observability.md
Last modified: 2026-06-10 22:24:05
Size: 2760 bytes
```markdown
# NINA Observability Layer

## Overview
The NINA Observability Layer provides a single, structured source of truth for the system's health, metrics, and telemetry. It relies on a lazy singleton, `ObservabilityHub`, to centrally aggregate operation and performance metrics, allowing components to emit consistent and standardized JSON logs.

## Metrics Reference

| field                | type      | description                                        |
| -------------------- | --------- | -------------------------------------------------- |
| uptime_seconds       | float     | Uptime in seconds since hub initialization         |
| tasks_total          | int       | Total number of tasks processed                    |
| tasks_ok             | int       | Total number of successfully completed tasks       |
| tasks_fail           | int       | Total number of failed tasks                       |
| router_calls         | int       | Total number of router calls made                  |
| last_sync_ts         | str       | ISO8601 timestamp of the last successful sync      |
| last_health_check_ts | str       | ISO8601 timestamp of the last health check run     |
| active_providers     | list[str] | List of active AI provider names                   |
| error_rate           | float     | Error rate calculated as (tasks_fail/tasks_total)  |
| memory_mb            | float     | Memory usage footprint mapped into megabytes       |

## Health Status
The health status represents the overall readiness and stability of NINA based on operational metrics.
- **HEALTHY:** NINA is operating correctly. (error_rate <= 0.2)
- **DEGRADED:** NINA is experiencing a high rate of errors. (0.2 < error_rate <= 0.5)
- **CRITICAL:** NINA has encountered severe failures and requires immediate attention. (error_rate > 0.5)

## Dashboard Endpoint
A new endpoint is exposed on the dashboard to easily observe NINA's metrics on demand.
**Endpoint:** `GET /health`

**Example JSON Response:**
```json
{
  "uptime_seconds": 120.5,
  "tasks_total": 10,
  "tasks_ok": 9,
  "tasks_fail": 1,
  "router_calls": 5,
  "last_sync_ts": "2023-10-24T12:00:00Z",
  "last_health_check_ts": "2023-10-24T12:05:00Z",
  "active_providers": ["Ollama", "OpenAI"],
  "error_rate": 0.1,
  "memory_mb": 150.0,
  "status": "HEALTHY"
}
```

## Wiring
The observability core is deeply integrated into various parts of NINA to update the central metrics cache.
- `healthcheck.py`: Calls `get_hub().set_health_ts()` at the end of the health checks (via `get_prometheus_metrics` / `Final report`).
- `tools/nina_sync.py`: Calls `get_hub().set_sync_ts()` exactly after performing a push and logging the push event.
- `tools/nina_dashboard.py`: Exposes `get_hub().to_dict()` natively at `/health`.
```

### docs/roadmap/nina_phase1_roadmap.md
Last modified: 2026-06-09 13:29:16
Size: 7799 bytes
```markdown
# NINA Phase 1 — Development Trajectory

**Document type:** Actionable development roadmap
**Scope:** Phase 1 only — what to build, in what order, and why
**Based on:** SWOT analysis, codebase backup, blueprint, master prompt, development policy, and owner Q&A session
**Owner:** M. Baizid Alam — BASIC Bank, Dhaka
**Date:** 2026-05-24

---

## The Core Insight

NINA's purpose is not to compete with Gemini on general knowledge. NINA's purpose is to do things Gemini **cannot** do: act inside your environment, remember your personal context, monitor your real-world signals, and take multi-step action autonomously over Telegram — from a laptop in Dhaka that never sleeps.

The goal for Phase 1 is not "implement every blueprint item." It is to make NINA reliably useful as a **personal operator** for five specific real-world tasks you care about.

---

## The Five Real-World Targets

These come directly from the owner's stated needs:

| # | Target | What NINA does that Gemini cannot |
|---|--------|----------------------------------|
| T-1 | Track personal expenditure | Reads, stores, recalls and analyzes *your* spending data locally |
| T-2 | Email intelligence | Reads *your* BASIC Bank mailboxes, gives subject/sender triage |
| T-3 | Share market alerts | Monitors DSE/CSE and notifies you via Telegram on developments |
| T-4 | Proactive reminders | Watches your context and nudges you without being asked |
| T-5 | Personal context memory | Knows your habits, routines, priorities, and refers to them |

None of these require a dashboard. None require a REST API. All are deliverable over Telegram. All require fixing current weaknesses first.

---

## Phase 1 Roadmap

Ordered strictly: fix crashes first, then smarter reasoning, then new capabilities.

---

### Stage A — Stop Active Failures (Do First, ~1–2 sessions)

These are breaking issues. Nothing else matters until these are resolved.

#### A-1 · Fix `parallel_route` RAM guard crash
- **ID:** R-77
- **File:** `core/router.py`
- **Change:** `self.config.ramguardgb` → `self.config.ram_guard_gb`

#### A-2 · Delete `core/logger.py`
- **ID:** D-01
- **File:** `core/logger.py`
- **Change:** Delete file. Confirm no other module imports it.

#### A-3 · Fix tool grammar fragility (minimum viable guard)
- **ID:** R-78
- **File:** `core/agent.py`
- **Change:** Wrap `TOOL:` / `FINAL:` parsing in a fallback: if neither marker found after all steps, return a graceful "I couldn't complete this" message rather than crashing or silently returning empty string.


### Stage B — Make NINA Smarter (Core Priority, ~2–3 sessions)

NINA feels dumb because she doesn't understand *you*. Better reasoning quality comes from better context injection and a self-check pass before sending answers.

#### B-1 · Self-check pass for complex tasks
- **ID:** F-01
- **File:** `core/agent.py`
- **Change:** After the final answer is formed for task types `research`, `coding`, `sensitive`, `document` — run one additional local model pass asking: "Is this answer complete, accurate and relevant to the original question? If not, revise it." Return the revised answer.

#### B-2 · Personal context injection into every prompt
- **ID:** F-02
- **File:** `core/memory.py`, `core/nina.py`
- **Change:** Add a dedicated `personal_context` section to `facts.json` with structured keys: `occupation`, `employer`, `priorities`, `working_hours`, `personal_habits`, `current_goals`. Inject this as a fixed top section in `build_context()` before semantic recall results — so every single NINA response is grounded in who you are.

#### B-3 · Response tone calibration in system prompt
- **ID:** F-03
- **File:** `core/nina.py` (SYSTEM_PROMPT_TEMPLATE)
- **Change:** Remove the duplicate `Available tools:` section. Add explicit tone calibration: direct, peer-level, not overly formal, proactively flags risk, uses Bangla or English based on your register.


### Stage C — New Capabilities (High Value, ~3–5 sessions)

Only build capabilities that serve the five real-world targets. Everything else waits.

#### C-1 · Expenditure tracker tool
- **ID:** F-04
- **File:** `tools/finance.py` (new)
- **Change:** A simple local tool that can:

#### C-2 · Share market monitor (DSE/CSE alerts)
- **ID:** F-05
- **File:** `tools/market.py` (new) + `crons/manager.py`
- **Change:**

#### C-3 · Proactive reminder engine
- **ID:** F-06
- **File:** `core/nina.py` + `data/reminders.json`
- **Change:**

#### C-4 · Email triage improvement
- **ID:** F-07
- **File:** `tools/office_mail.py`
- **Change:**

#### C-5 · Personal knowledge base (`/remember` and `/recall`)
- **ID:** F-08
- **File:** `core/memory.py` + Telegram command handler
- **Change:**


### Stage D — Stability Hardening (Ongoing, parallel with C)

Do one of these per session alongside Stage C work.

| ID | Change | File | Why |
|----|--------|------|-----|
| S-01 | Fix SSRF substring → `ipaddress` module | `tools/browser.py` | Security debt, Guardian flags it |
| S-02 | Wrap memory file I/O in `asyncio.to_thread` | `core/memory.py` | Blocking I/O in async path causes slow replies |
| S-03 | Fix `ResponseCache.purge_expired` dict mutation | `core/router.py` | RuntimeError during cache purge under load |
| S-04 | Add model version override dict to `NinaConfig` | `core/config.py` | Hardcoded model strings go stale silently |
| S-05 | Add `if not root.handlers` guard in logger setup | `core/nina.py` | Prevents duplicate log handlers on restart |

---

## What Is Explicitly Out of Phase 1

These are not blocked forever — they are just not needed to achieve the five real-world targets.

| Item | Reason to defer |
|------|----------------|
| FastAPI / `interfaces/api.py` | No external automation needed in Phase 1. Telegram is sufficient. |
| Prometheus / Grafana metrics | Explicitly not needed. Guardian + logs is enough. |
| 3-tier memory (episodic/semantic/working) | Overkill for current usage. B-2 personal injection fixes the real problem. |
| Token cost tracking per provider | No budget pressure on free models. |
| Full test suite | Valuable long-term, not Phase 1 priority. |
| Provider YAML consolidation | Low user-impact. Schedule as D-series debt ticket. |

---

## Development Rules for This Phase

These are not the full policy — just the minimum that keeps NINA stable:

1. **One change per session.** Do not stack fixes.
2. **Run Guardian before and after every change** that touches `core/`, `tools/`, or `interfaces/`.
3. **Every change needs a runtime proof** — not just "it didn't crash on import."
4. **If Guardian shows a new BLOCKER after your change, roll back first, investigate second.**
5. **Log the ID, file, and outcome** the same day, even if just in a text note.

---

## Sequence Summary

```
Week 1   A-1 A-2 A-3          (stop crashes and fragility)
Week 2   B-1 B-2 B-3          (smarter reasoning and context)
Week 3   C-1 C-3              (expenditure tracker + reminder engine)
Week 4   C-4 C-2              (email triage improvement + market alerts)
Week 5   C-5 + D-series       (personal knowledge base + stability hardening)
```

This is a guide, not a contract. If something blocks you, skip it and move to the next. If something is easier than expected, pull the next item forward.

---

## What NINA Looks Like After Phase 1

- She does not crash on complex tasks
- She understands who you are and responds accordingly
- She monitors your email and flags what matters
- She watches the share market and pushes alerts to your Telegram
- She tracks your spending and summarizes it on demand
- She reminds you of things without being asked
- She remembers personal facts you teach her

None of these are things you can get from Gemini on your phone. All of them run on your laptop in Dhaka.
```

### docs/router.md
Last modified: 2026-06-11 14:47:31
Size: 3748 bytes
```markdown
# HybridRouter V4 Subsystem

## Overview

Located in `core/router.py`, the HybridRouter V4 is NINA's sophisticated model routing engine. NINA is not bound to a single LLM provider; instead, it leverages this router to dynamically select the optimal provider for every task, ensuring high availability, minimizing costs, and respecting API rate limits.

## Supported Providers

The router maintains connections to 19+ cloud providers and 2 local model variants:
- **Cloud Providers:** Groq, Gemini, Cerebras, DeepSeek, Mistral, OpenRouter, Together, Cohere, Fireworks, xAI, SambaNova, Hyperbolic, Novita, Perplexity, OpenAI, Pollinations, Chutes, and more.
- **Local Models (via Ollama):**
  - `qwen2.5:1.5b` (For rapid, lightweight parsing and fast tasks)
  - `qwen2.5:7b` (For heavy reasoning and complex logic parsing)

## Routing Algorithm

HybridRouter V4 does not just pick a model at random; it employs a weighted scoring algorithm to determine the absolute best route for the current prompt. The scoring mechanism calculates the viability of a provider using the formula:
**`Success Rate × Latency × Rate Limits`**

This ensures that NINA routes heavily toward providers that are currently fast, reliable, and well below their quota limits.

## Live Quota Tracker (v14.0)

NinaGate features a **Live Quota Tracker** to protect cloud API limits and automate routing shifts:
- **Monitoring:** Tracks total requests per provider (e.g., Gemini Flash).
- **Auto-Downgrade:** When a limit (e.g., 900 req/day) is approached, NinaGate automatically skips that provider and routes to local NinaFlash (Ollama) or next-tier cloud models.
- **Daily Reset:** Quotas reset automatically at **1 PM BD** (Midnight PT), ensuring continuous operation without manual intervention.

## CircuitBreaker Pattern

To prevent NINA from hanging or cascading into total failure when a specific provider experiences an outage, HybridRouter V4 implements a strict CircuitBreaker pattern. If a provider fails multiple times in rapid succession, the CircuitBreaker trips, temporarily removing that provider from the active pool. The router will automatically fallback to the next highest-scoring provider, ensuring seamless user experience.

## Free-Tier Priority

NINA operates on a strict "free-tier first" philosophy. The router is explicitly configured to exhaust the quotas of high-quality free API tiers (like Groq, Together, or Gemini's free tiers) before gracefully degrading or shifting to paid APIs. This prevents runaway API costs during autonomous self-development loops.

## Rate Limit Tracking

The router rigorously tracks usage statistics internally to avoid HTTP 429 (Too Many Requests) errors. It monitors:
- **RPM:** Requests Per Minute
- **RPD:** Requests Per Day
- **TPD:** Tokens Per Day

If an impending rate limit is detected for the top-priority provider, the router preemptively shifts the load to the next available provider.

## Response Caching

To further minimize token usage and latency, HybridRouter V4 includes a persistent response caching layer.
- **Deduplication:** Identical prompts (including recent message history) are hashed and checked against the cache before any provider call is made.
- **Persistence:** Unlike standard in-memory caches, NINA's cache is persisted to `data/router_cache.json`. This ensures that cached responses survive service restarts and system reboots.
- **TTL Management:** Cache entries have specific Time-To-Live (TTL) values based on task type (e.g., `coding` tasks may be cached for 6 hours, while `quick` tasks are cached for 1 hour). Sensitive tasks are never cached.
- **Automatic Purging:** The cache periodically purges expired entries during idle periods to maintain a lean storage footprint.
```

### docs/space/claude_feed.md
Last modified: 2026-06-11 23:29:48
Size: 19503 bytes
```markdown
# NINA Claude Feed — Session Startup Context
> Auto-generated by nina_sync.sh — do not edit manually
> Claude: read this. Then generate 10 non-overlapping Jules specs.

## 1. Snapshot
- Generated: 2026-06-11 23:29 +06
- Git HEAD: 3d72bda9b00c9a3ac030cf1f3de598625aa30b8c
- Last commit: docs: post-session sync 2026-06-11 23:28
- Service: activating
unknown
```
● nina.service - NINA Autonomous Agent
     Loaded: loaded (/etc/systemd/system/nina.service; enabled; preset: enabled)
     Active: activating (auto-restart) (Result: exit-code) since Thu 2026-06-11 23:29:41 +06; 2s ago
 Invocation: 36a5f275a0f845d2ae1a639c93fd4002
    Process: 102730 ExecStart=/home/aibony/nina/venv/bin/python main.py (code=exited, status=1/FAILURE)
   Main PID: 102730 (code=exited, status=1/FAILURE)
   Mem peak: 27.5M
        CPU: 249ms
unavailable
```
## 2. Active Jules Sessions (live)
Active Jules Sessions:
#1 [358132093278995322] System Bug Fixes and Agent Optimization — FAILED — no PR yet
#2 [15353880579548246468] NINA Mega Task 5: Stability, Observability, and Context Hygiene — AWAITING_USER_FEEDBACK — no PR yet
#3 [7396398476427288048] Mega Task 10: NINA Sovereign Self-Maintenance Protocol — COMPLETED — https://github.com/aibony/nina/pull/112
#4 [12486530914500192869] Mega Task 9: Speculative Execution & Scout Agents — COMPLETED — https://github.com/aibony/nina/pull/109
#5 [729439358701133165] Mega Task 8: The Glass Box Dashboard — COMPLETED — https://github.com/aibony/nina/pull/108
#6 [1909469007448016875] Autonomous QA & Self-Fixing Implementation — COMPLETED — https://github.com/aibony/nina/pull/114
#7 [6823805920751039478] Surgical Context Optimization (Mega Task 6) — COMPLETED — https://github.com/aibony/nina/pull/113
#8 [17892297084289591100] NINA Mega Task 5: Lightning Edition Implementation — COMPLETED — https://github.com/aibony/nina/pull/115
#9 [9390249204279541291] NINA-Evolve: Autonomous Self-Optimization Protocol — COMPLETED — https://github.com/aibony/nina/pull/111
#10 [10948090147375231066] NINA v3.0: Lightning Observability & Persistent Memory — COMPLETED — no PR yet
#11 [5693617654071384777] NINA v2.0: Observable Local Engine & Memory Upgrade — COMPLETED — https://github.com/aibony/nina/pull/110
#12 [14109430478887759619] NINA Observability & Memory Upgrade — COMPLETED — https://github.com/aibony/nina/pull/107
#13 [6517172233685149283] Implement AG-N-01: Global Symbol Indexer in ninaflash.py — COMPLETED — https://github.com/aibony/nina/pull/97
#14 [9570975373503583765] Implement AG-M-12: NF-SESSIONS Checkpoint & Resume per docs/ — COMPLETED — https://github.com/aibony/nina/pull/100
#15 [13185833759609299904] Implement AG-M-11: NF-LOG Sliding Window Summarizer per docs — COMPLETED — https://github.com/aibony/nina/pull/103
#16 [10135412826971545639] Implement AG-M-10: GATE-PROMPT System Prompt Templating per  — COMPLETED — https://github.com/aibony/nina/pull/105
#17 [7537211368798200186] Implement AG-M-09: NF-ARCHIVE Historical Offloading per docs — COMPLETED — https://github.com/aibony/nina/pull/98
#18 [5503859994610952764] Implement AG-M-08: NF-STATUS High-Density Pulse per docs/spa — COMPLETED — https://github.com/aibony/nina/pull/96
#19 [16853848519420810103] Implement AG-M-07: NF-CLEAN Automated Hygiene per docs/space — COMPLETED — https://github.com/aibony/nina/pull/106
#20 [8261678623607038143] Implement AG-M-06: SEC-IGNORE Global Context Filtering per d — AWAITING_USER_FEEDBACK — no PR yet
#21 [18219510094834116674] Implement AG-M-05: NF-BACKLOG Incremental State per docs/spa — COMPLETED — https://github.com/aibony/nina/pull/104
#22 [4898120370834123044] Implement AG-M-04: DOC-COMP Instruction Compression per docs — COMPLETED — https://github.com/aibony/nina/pull/101
#23 [15969685038089350386] Implement AG-M-03: NF-EXT Surgical Code Intelligence per doc — COMPLETED — https://github.com/aibony/nina/pull/102
#24 [5225035707782933030] Implement AG-M-02: Token-Surgical Architecture (v2.1) per do — COMPLETED — https://github.com/aibony/nina/pull/99
#25 [16087617206011709240] Implement AG-M-01: NINA Throughput Maximizer (v2.0 Architect — AWAITING_USER_FEEDBACK — no PR yet
#26 [10138180872701920532] ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
✦ This is a high-impact list of 20 "Token-Surgical" upgrades. These are designed to collapse high-token cloud reasoning into zero-token local commands within ninaflash.

  ⚡ The "Token-Surgical" Action Plan (20 Upgrades)

  I. Surgical Research (Moving Code Reading to Local)
   1. nf code symbol <file> <name>: Use AST to extract ONLY a specific class or function instead of the whole file.
   2. nf code sigs <dir>: Generate a signature-only map of an entire directory (e.g., core/) to help me "LOCATE" without reading.
   3. nf find-symbol <name>: Global search for where a class/function is defined across the repo.
   4. nf capability list: Shows available tools and their docstrings without reading core/capabilities.py.

  II. Context Hygiene (Reducing Instruction Overhead)
   5. AGENTS.md Pruning: Move "How-To" guides to docs/agent-memory/ and keep only P0 directives in the root.
   6. Project-level .geminiignore: Block logs/, data/plans/, and backups/ from my indexing and search tools.
   7. nf index query --mini: Returns only a file's role and guardrails instead of the full metadata JSON.
   8. nf log tail <n>: Reads only the last N entries of nina_update_log.md to find the next ID.

  III. Validation & Logic (Preventing Wasted Turns)
   9. nf check diff: Runs syntax/linter checks ONLY on the lines I changed.
   10. nf check code --fix: Automatically runs ruff --fix or black locally before I even see the errors.
   11. nf doc check --fix: Automatically formats my nina_update_log.md entries to match the repo style.
   12. nf session checkpoint: Saves the current "Goal + File List" to a 1KB JSON to survive session resets.

  IV. Backlog & Task Management (Reducing Table Reading)
   13. nf backlog summary: Replaces the 500-line backlog table with a 5-line summary (READY: 5, DONE: 100).
   14. nf task active: Lists only IN_PROGRESS tasks with their current locked files.
   15. nf backlog dag --mini: Shows only the direct dependencies of the current task.
   16. nf session archive: Moves DONE tasks from the main backlog to an archive file to keep the main context small.

  V. Sync & Observability (Reducing High-Volume Output)
   17. nf sync --quiet: A version of the sync script that only prints errors/success, hiding the 100-line file list.
   18. nf status --pulse: A 10-line project heartbeat (Git, Env, Venv, Active Task).
   19. nf pr diff-mini <id>: Shows file names and line counts for a PR instead of the full diff text.
   20. nf log summarize: Collapses 100 lines of repeating logs into "Heartbeat x 100".

  ---

  🚀 MEGA-TASK: Gemini CLI Token Optimizer (v1.0)
  Assignee: Jules (Async Cloud Coder)

    1 Objective: Upgrade ninaflash (nf) and AGENTS.md to minimize the token footprint of Gemini CLI sessions.
    2
    3 🏗️ Domain 1: Surgical Code Intelligence
    4 - Implement `nf code symbol` and `nf find-symbol` using Python's `ast` module.
    5 - Implement `nf code sigs` to generate directory-level symbol maps.
    6
    7 🧠 Domain 2: Instruction Compression
    8 - Refactor `AGENTS.md`: Move non-essential "Patterns" and "Guides" to `docs/agent-memory/workflow.md`.
    9 - Replace verbose sections with high-density "Directive Lists."
   10
   11 📉 Domain 3: Incremental State Management
   12 - Update `ninaflash.py` to support `backlog summary` and `task active` commands.
   13 - Implement `nf log next-id` and `nf log tail` to avoid reading the massive 2000-line update log.
   14
   15 🛡️ Domain 4: Automated Hygiene
   16 - Create a global `.geminiignore` excluding all `logs/`, `data/`, and `upgrades/` folders.
   17 - Implement `nf check code --fix` to offload linting to local tools.
   18
   19 ACCEPTANCE CRITERIA:
   20 - `ninaflash` must pass `nf check code` with 0 new errors.
   21 - `AGENTS.md` size must be reduced by at least 40%.
   22 - All new `nf` commands must be registered in the `ninaflash` help menu.

 — COMPLETED — no PR yet
#27 [12472411724478378253] NINA: Token-Surgical Architecture (v2.1) — COMPLETED — no PR yet
#28 [9366433283406156154] Implement Self-Healing Foundation: Governance Task Feed and Safe Idleloop Integration — COMPLETED — no PR yet
#29 [611206915375312400] NINA v2.0: High-Velocity Autonomous Control Plane & Throughput Maximizer — COMPLETED — no PR yet
#30 [1275031342912292988] Bolt: Performance Optimization Agent — AWAITING_USER_FEEDBACK — no PR yet
#31 [1574419446092272855] Sentinel: Security Vulnerability Protection Agent — AWAITING_USER_FEEDBACK — no PR yet
#32 [10160574285881231440] Bolt ⚡ Performance Optimization Agent — COMPLETED — https://github.com/aibony/nina/pull/95
#33 [7268677664812904161] Implement Robust SSRF Protection in tools/browser.py — COMPLETED — no PR yet
#34 [17152236090245737003] Enriching NINA User Context in facts.json — COMPLETED — https://github.com/aibony/nina/pull/89
#35 [4387163849844491775] Unit Tests for MemorySystem (core/memory.py) — COMPLETED — https://github.com/aibony/nina/pull/87
#36 [10909349624388531776] Create Initial Plan Templates for NINA — COMPLETED — https://github.com/aibony/nina/pull/88
#37 [2263125060445490680] Implement Environment Variable Validation in NinaConfig — COMPLETED — https://github.com/aibony/nina/pull/92
#38 [15140647001143967458] Implement timeouts for subprocesses in compact_exporter.py — COMPLETED — https://github.com/aibony/nina/pull/90
#39 [11879535673965449416] Inject Deterministic Personal Context into Memory System — COMPLETED — https://github.com/aibony/nina/pull/93
#40 [7077821852816108419] Implement Semantic Scoring and Numeric Assertions in core/verifier.py — COMPLETED — https://github.com/aibony/nina/pull/91
#41 [6894265727609131811] Comprehensive Unit Tests for TaskStore — COMPLETED — https://github.com/aibony/nina/pull/94
#42 [10700815354040855410] Enhance TaskStore Schema, Indexing, and Archiving (AG-B-02, AG-B-04, AG-B-08) — AWAITING_USER_FEEDBACK — no PR yet
#43 [7979733904089825750] Developer Tooling Hardening: Jules API, Shell Allowlist & Model Discovery — COMPLETED — https://github.com/aibony/nina/pull/84
#44 [7958652979132541763] Centralized Cron Registry & Result Logging — COMPLETED — https://github.com/aibony/nina/pull/79
#45 [10120257988537896914] Agent Loop Refactor: THINK-PLAN-ACT Extraction — COMPLETED — https://github.com/aibony/nina/pull/82
#46 [14446618339490913116] Finance & Market Tools Hardening: Retry Logic & Structured Returns — COMPLETED — https://github.com/aibony/nina/pull/86
#47 [13000109120090282729] Telegram Interface Hardening: Rate Limiting & Error Handling — COMPLETED — https://github.com/aibony/nina/pull/81
#48 [14124915954782378145] Memory System Hardening: ChromaDB Resilience and Scratchpad Layer — COMPLETED — https://github.com/aibony/nina/pull/83
#49 [3956940177468171330] NINA Initial Test Suite and Loop Resilience — COMPLETED — https://github.com/aibony/nina/pull/80
#50 [13392071392650141737] Implement Unified Observability & Health Layer — COMPLETED — https://github.com/aibony/nina/pull/78

## 3. Locked Files (do not touch in new specs)
```
LOCKED_FILES=tools/nina_sync.py,tests/test_nina_sync.py,.ninaignore,requirements.txt
JULES_TASK=B-005
JULES_PR=feat/b-005-nina-sync
LOCKED_SINCE=2026-06-08T16:58:50+00:00
```

## 4. READY Items (eligible for new Jules specs)
_Found 8 READY items_

### AG-M — Throughput Maximizer
_MEGA-TASK: V2.0 Architecture Upgrade_
_Dependency: AG-B-01 and AG-B-02 must be DONE first_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-M-01 | Multi-module | 🚀 MEGA-TASK: NINA Throughput Maximizer (v2.0 Architecture) — Implement Domains 1-5 to accelerate NINA. | `READY` | AG-B-01 |
| AG-M-02 | Multi-module | 📉 MEGA-TAS

### AG-N — Advanced Code Intelligence
_Focus: Zero-token research and semantic mapping_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-N-01 | `ninaflash.py` | Global Symbol Indexer — Generate JSON map of all classes/functions. | `DONE` | — |
| AG-N-02 | `ninaflash.py` | Local Call Graph Generator — Trace function calls locally without LLM. | `READY` | A

### AG-O — Automated Testing & QA
_Focus: Reducing debug turns through local verification_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-O-01 | `tests/` | Test Scaffold Generator — Create test stubs for every new function. | `READY` | — |
| AG-O-02 | `tests/` | Mutation Test Suite — Implement basic mutation testing for core modules. | `READY` | — |
| A

### AG-P — Performance & Latency
_Focus: High-velocity execution and low overhead_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-P-01 | `core/router.py` | Router Latency Optimizer — Profile and reduce router overhead. | `READY` | — |
| AG-P-02 | `core/router.py` | Persistent Response Cache — Move cache to SQLite for speed. | `READY` | — |
| AG-P-03 | `

### AG-Q — Memory & Knowledge
_Focus: Precision retrieval and minimal noise_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-Q-01 | `data/memory/` | ChromaDB Cluster — Shard vector memory by domain. | `READY` | — |
| AG-Q-02 | `core/memory.py` | Automatic Fact Extraction — LLM-driven mining of logs. | `READY` | — |
| AG-Q-03 | `core/memory.py` | Memory C

### AG-R — Repository Hygiene
_Focus: Minimal repo size and clean structure_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-R-01 | `ninaflash.py` | Stale File Archiver — Auto-move 60-day untouched files. | `READY` | — |
| AG-R-02 | `requirements.txt`| Requirement Pinner — Lock dependencies to exact hashes. | `READY` | — |
| AG-R-03 | `ninaflash.py` | La

### AG-S — Interface & Interaction
_Focus: Fast feedback and low-overhead communication_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-S-01 | `interfaces/telegram_interface.py`| Telegram Batching — Consolidate short messages. | `READY` | — |
| AG-S-02 | `ninaflash.py` | CLI Progress Bars — Rich bars for long nf commands. | `READY` | — |
| AG-S-03 | `co

### AG-T — Token & Context Engineering
_Focus: Absolute minimum context overhead_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-T-01 | `core/agent.py` | Dynamic Prompting — Adjust prompt length by task diff. | `READY` | — |
| AG-T-02 | `ninaflash.py` | Context Window Estimator — Predict token usage before call. | `READY` | — |
| AG-T-03 | `core/agent.p


## 5. Last 5 Completions
```
3d72bda docs: post-session sync 2026-06-11 23:28
29e8543 feat(sync): claude_feed service detail + PR merge list
ef1d7c1 docs: post-session sync 2026-06-11 23:20
26675d4 fix(ninagate): classifier expansion, async race fix, quota save non-blocking, fast-fail timeout, rglob depth cap
648ddc1 docs: post-session sync 2026-06-11 23:11
```

## 6. Open Blockers
- → counts READY items by tier, checks BLOCKED promotions
- | `BLOCKED` | Has unresolved dependency — do not pick up |
- | AG-F-02 | `tools/agents/market_agent.py` | MarketAgent — watches DSE/CSE prices on schedule, emits ALERT event when watchlist threshold crossed | `NEEDS_SPEC` | AG-F-01 |
- | AG-F-03 | `tools/agents/expense_agent.py` | ExpenseAgent — monitors Telegram messages for expense patterns, auto-logs to finance tool | `NEEDS_SPEC` | AG-F-01 |
- | AG-J-06 | `tests/test_market_agent.py` | Unit tests for MarketAgent: mock price feed, threshold crossing, alert emission | `NEEDS_SPEC` | AG-F-02 |
- | AG-O-02 | `tests/` | Mutation Test Suite — Implement basic mutation testing for core modules. | `READY` | — |
- | AG-O-06 | `tests/` | Flaky Test Detector — Identify intermittent test failures. | `READY` | — |
- | AG-S-01 | `interfaces/telegram_interface.py`| Telegram Batching — Consolidate short messages. | `READY` | — |
- | AG-S-02 | `ninaflash.py` | CLI Progress Bars — Rich bars for long nf commands. | `READY` | — |
- AG-F-01 → AG-F-02            ← BaseAgent + MarketAgent (first real autonomous agent)
- | F-02 | memory: deterministic personal_context | E-sync | — | 2026-06-09 |

## 7. File Ownership Cheatsheet
| File | Purpose | Risk |
|------|---------|------|
| core/nina.py | NinaOS orchestrator, system prompt | HIGH |
| core/router.py | HybridRouter V4, 19+ providers, circuit breaker | HIGH |
| core/agent.py | AgentLoop THINK→PLAN→ACT, self-check, RAM guard | HIGH |
| core/memory.py | ChromaDB + facts.json, build_context() | MEDIUM |
| core/task_store.py | TaskStore persistence, file locking | MEDIUM |
| core/config.py | NinaConfig, RATELIMITS | HIGH |
| interfaces/telegram_interface.py | Telegram bot, auth gate | HIGH |
| guardian_engine.py | Forensic engine, AST scans, baseline | HIGH |
| tools/jules_api.py | Jules REST API dispatch/status | LOW |
| tools/market.py | DSE/CSE monitor (dummy prices — needs real API) | LOW |
| tools/finance.py | Expenditure tracker | LOW |
| tools/office_mail.py | Email triage (EWS blocked — O-02 open) | LOW |
| tools/shell.py | Shell execution (cat in allowlist — O-06 CRITICAL) | HIGH |
| tools/browser.py | URL fetch (SSRF fix S-01 pending) | MEDIUM |
| ninagate/main.py | OpenAI-compatible proxy (duplicate router — debt) | MEDIUM |
| idleloop.py | IdleProposalLoop, IMPACT briefs | LOW |
| crons/manager.py | APScheduler, reminders, daily reports | MEDIUM |
| data/memory/facts.json | Personal context facts (F-02 injection pending) | MEDIUM |
## 8. PRs Ready to Merge (agy merge candidates)
#115 feat(core): implement mega task 5 lightning edition [jules-17892297084289591100-7a514cf9]
#114 Mega Task 7: Autonomous QA (The Guardian Hardening) [feat/autonomous-qa-guardian-1909469007448016875]
#113 Implement Surgical Context with context-pack and ChromaDB RAG [jules-6823805920751039478-4fa46e96]
#112 feat(maintenance): implement Sovereign Self-Maintenance Protocol [jules-7396398476427288048-4a94a9ca]
#111 feat(evolve): Implement functional NINA-Evolve Protocol with real log parsing and safe execution [feature/nina-evolve-protocol-9390249204279541291]
#110 feat: NINA Observability & Memory Upgrade v2.0 [jules-5693617654071384777-a898bda6]
#109 Implement Speculative Pipeline in AgentLoop [jules-agent-loop-scout-12486530914500192869]
#108 feat(dashboard): implement live visual telemetry dashboard [feat/visual-telemetry-dashboard-729439358701133165]
#107 NINA Observability & Memory Upgrade (Observable Local Execution Layer) [jules/opt-observable-local-layer-14109430478887759619]


---
_Feed size: 18786 bytes_```

### docs/space/jules_backlog.md
Last modified: 2026-06-11 12:51:54
Size: 46279 bytes
```markdown
# NINA Jules Backlog — Unified Pipeline
> **Mission:** NINA is a personal autonomous AI agent — NOT a chatbot. She acts, she does not describe.
> **Location:** `~/nina/docs/space/jules_backlog.md`
> **Updated by:** ninaflash (Python append only — never bash echo, never manual edit)
> **Read by:** Perplexity via nina_latest.md Google Drive backup every session
> **Consumed by:** Jules (async PRs) + ninaflash (local merges only)
> **Last restructured:** 2026-06-07 — Agentic shift adopted. All new features serve the agent mission.

---

## How This File Works

```
Perplexity reads backlog each session
  → counts READY items by tier, checks BLOCKED promotions
  → generates Jules task spec for each READY item (up to 15 per batch)
  → you submit spec to Jules UI
  → ninaflash merges PR when Jules opens it — never auto-merge via GitHub UI
  → ninaflash updates status: READY → IN_PROGRESS → IN_PR → DONE
  → next session: Perplexity picks next READY batch
```

**Territory rule:** Perplexity will never spec two concurrent tasks that touch the same file.
**Batch size:** Up to 15 non-overlapping READY tasks per Jules batch.
**Daily budget:** 15 SCHED tasks + up to 75 backlog tasks = 90/100 daily limit. 10 reserved for emergencies.

---

## ID Namespaces

| Prefix | Format | Purpose |
|--------|--------|---------|
| `B-001` | B + 3-digit | Infrastructure backlog — routing, security, observability, tests |
| `AG-A` … `AG-J` | AG + group letter + 2-digit | Agentic pipeline — planning, task state, autonomous loops, verification |

---

## Status Definitions

| Status | Meaning |
|--------|---------|
| `READY` | Fully specced, no blockers — Perplexity submits to Jules immediately |
| `IN_PROGRESS` | Jules task submitted, PR not yet open |
| `IN_PR` | PR open, waiting for ninaflash review + merge |
| `BLOCKED` | Has unresolved dependency — do not pick up |
| `DONE` | Merged, deployed, verified by Guardian |
| `DEFERRED` | Valid but deprioritised — revisit next sprint |
| `NEEDS_SPEC` | Idea captured — Perplexity must write full spec before Jules submission |

---

## Priority Tiers

| Tier | Label | Description |
|------|-------|-------------|
| P0 | CRITICAL | Security, data loss, service down — fix before anything else |
| P1 | HIGH | Core functionality gaps, reliability, routing quality |
| P2 | MEDIUM | Observability, developer experience, test coverage |
| P3 | LOW | Polish, nice-to-have, future-proofing |
| AG1 | AGENTIC PHASE 1 | Agency core — planner, task state, loop upgrade, verifier |
| AG2 | AGENTIC PHASE 2 | Proactive intelligence — events, autonomous agents, outbound push |
| AG3 | AGENTIC PHASE 3 | Agentic test coverage — runs parallel with AG2 |

---

## ██ P0 — CRITICAL

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-001 | Sentinel: remove shell=True from run_cmd in guardianengine.py | `DONE` | guardianengine.py | — | PR #60 merged 2026-06-07 |
| B-002 | Wire model_overrides dict to .env hot-reload | `IN_PROGRESS` | core/router.py, core/config.py | — | model_overrides in NinaConfig but not wired to hot-reload |
| B-003 | Add timeout to all subprocess calls in compact_exporter.py | `DONE` | tools/compact_exporter.py | — | No timeout = potential hang / DoS risk |
| B-004 | Validate TELEGRAM_CHAT_ID exists before any send attempt | `IN_PROGRESS` | interfaces/telegraminterface.py | — | Silent failure if env var missing; non-blocking open item |

---

## ██ P1 — HIGH

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-005 | F-09 ModelDiscoveryService — build tools/model_discovery.py | `DONE` | tools/model_discovery.py, core/router.py, crons/manager.py | — | PR #25 merged 2026-06-07 |
| B-006 | F-09 Part 2 — wire ModelDiscovery into router._ordered_providers() | `DONE` | core/router.py | B-005 | ninaflash only — high-risk file |
| B-007 | F-09 Part 3 — seed data/model_cache.json with all 16 providers | `DONE` | data/model_cache.json | B-005 | Jules can do this |
| B-008 | Add circuit breaker state persistence to data/circuit_state.json | `DONE` | core/router.py, data/ | — | Currently in-memory — lost on restart. ninaflash only |
| B-009 | Add rate limiting to Telegram command handler | `READY` | interfaces/telegraminterface.py | — | ninaflash only — high-risk file |
| B-010 | Add input length validation to all Telegram command parsers | `READY` | interfaces/telegraminterface.py | — | ninaflash only — high-risk file |
| B-011 | Guardian engine: add file integrity check on startup | `READY` | guardianengine.py | — | SIGNATURES dict exists but startup check is passive. ninaflash only |
| B-012 | Add structured JSON logging to router.py for provider selection events | `READY` | core/router.py | — | Plain text logs hard to parse for metrics. ninaflash only |
| B-013 | healthcheck.py: replace bare except with typed exception handling | `DONE` | healthcheck.py | — | Bare except swallows real errors |
| B-014 | Add startup banner to main.py showing active providers + model strings | `IN_PROGRESS` | main.py | B-002 | Needs model_overrides wired first. ninaflash only |
| B-015 | crons/manager.py: add job execution metrics (duration, last_success, fail_count) | `DONE` | crons/manager.py | — | No visibility into cron job health |
| R-77 | Fix parallel_route RAM guard crash | `READY` | core/router.py | — | A-1 from action board. ninaflash only |
| R-78 | Fix tool grammar fragility — minimum viable guard | `DONE` | core/agent.py | — | A-3 from action board; Jules session 230224707076942630 |

---

## ██ P2 — MEDIUM

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-016 | Write tests for tools/shell.py — full blocklist and allowlist coverage | `DONE` | tests/test_shell.py | — | Most critical security tool has zero tests; Jules session 15759165614254551433 |
| B-017 | Write tests for core/router.py — provider ordering, circuit breaker, fallback | `DONE` | tests/test_router.py | — | Jules session 9354379735932974598 |
| B-018 | Write tests for tools/browser.py — SSRF guard, URL validation | `DONE` | tests/test_browser.py | — | Jules session 9340521117119167710 |
| B-019 | Write tests for guardianengine.py — SIGNATURES check, run_cmd | `DONE` | tests/test_guardian.py | — | High-risk file needs test coverage; Jules session 13016195312630697079 |
| B-020 | Write tests for tools/model_discovery.py | `DONE` | tests/test_model_discovery.py | B-005 | Unblock now — B-005 is DONE |
| B-021 | Add prometheus-style metrics endpoint to healthcheck.py | `DONE` | healthcheck.py | — | Enables external monitoring; Jules session 4745946253740770652 |
| B-022 | tools/compact_exporter.py: add progress logging for long exports | `DONE` | tools/compact_exporter.py | — | Silent during long runs; Jules session 7514279750845525195 |
| B-023 | Add AGENTS.md section: tracker update protocol for Jules tasks | `DONE` | AGENTS.md | — | Jules needs instructions to update task tracker after each run; Jules session 15026902744619615986 |
| B-024 | Add AGENTS.md section: backlog update protocol | `DONE` | AGENTS.md | — | 2026-06-07 |
| B-025 | crons/manager.py: add graceful shutdown handler (SIGTERM) | `DONE` | crons/manager.py | — | No clean shutdown on systemd stop; Jules session 5406292542431629720 |
| B-026 | Add retry with exponential backoff to provider API calls | `READY` | core/router.py | — | Current retry is basic — no backoff. ninaflash only |
| B-027 | tools/gputuner.py: add fallback when nvidia-smi not available | `DONE` | tools/gputuner.py | — | Crashes on non-GPU systems; Jules session 18284106294453230200 |
| B-028 | Add .env validation on startup — warn on missing required keys | `IN_PR` (partial — config.py done) | main.py, core/config.py | — | Silent failure on missing env vars. main.py → ninaflash only |
| B-029 | Write integration test: full request through router → provider → response | `DONE` | tests/test_integration.py | — | No end-to-end test exists; Jules session 7992182378283234865 |
| B-030 | Add request ID to all log lines for traceability | `READY` | core/router.py, main.py | — | Hard to trace multi-step requests. ninaflash only |

---

## ██ P3 — LOW / POLISH

| ID | Title | Status | Files Touched | Blocks | Notes |
|----|-------|--------|---------------|--------|-------|
| B-031 | Add provider latency histogram to router metrics | `READY` | core/router.py | B-012 | Needs structured logging first. ninaflash only |
| B-032 | tools/compact_exporter.py: add --dry-run flag | `DONE` | tools/compact_exporter.py | — | Jules session 16016744403096643329 |
| B-033 | Telegram: /status command — shows provider health summary | `NEEDS_SPEC` | interfaces/telegraminterface.py | — | ninaflash only |
| B-034 | Telegram: /models command — shows current model per provider | `NEEDS_SPEC` | interfaces/telegraminterface.py | B-005 | ninaflash only |
| B-035 | Telegram: /backlog command — shows top 5 READY items | `NEEDS_SPEC` | interfaces/telegraminterface.py | — | ninaflash only |
| B-036 | Telegram: /errors command — shows open error register items | `NEEDS_SPEC` | interfaces/telegraminterface.py | — | ninaflash only |
| B-037 | docs/space: add nina_architecture_diagram.md with ASCII diagrams | `DONE` | docs/space/nina_architecture_diagram.md | — | No visual architecture reference exists; Jules session 2468954092544028080 |
| B-038 | Add per-provider cost tracking to router.py | `NEEDS_SPEC` | core/router.py | B-012 | ninaflash only |
| B-039 | Add response caching layer for identical prompts (TTL 60s) | `DONE` | core/router.py | — | Persistent cache implemented by Gemini CLI 2026-06-11 |
| B-040 | Write CONTRIBUTING.md | `DONE` | CONTRIBUTING.md | — | Jules session 1218304308318697501 |

---

## ██ NEEDS_SPEC — Ideas Awaiting Design

| ID | Title | Notes |
|----|-------|-------|
| B-041 | DSE/Bangladesh financial data integration (F-05) | Needs real DSE API endpoint research first |
| B-042 | Telegram inline keyboard for common commands (F-08) | Needs UX design pass |
| B-043 | Multi-modal support: image input routing | Provider capability matrix needed |
| B-044 | Web dashboard for NINA status (read-only) | `DONE` |
| B-045 | Conversation memory persistence across sessions | Storage design needed |

---

---

# ══════════════════════════════════════
# ██  AGENTIC PIPELINE  ██
# ══════════════════════════════════════
#
# Goal: Transform NINA from reactive chatbot to true autonomous agent.
#
# Rule: ALL AG items are NEEDS_SPEC until Perplexity writes a full Jules spec.
# Rule: AG1 must be fully merged + Guardian stable before AG2 begins.
# Rule: High-risk files (main.py, router.py, telegraminterface.py,
#        guardianengine.py, shell.py, .env) — ninaflash only, never Jules.
# Rule: After every Jules AG merge, ninaflash runs ./nina_sync.sh — no exceptions.
# Rule: Check juleslock.txt before starting any AG task.
#
# Perplexity: when all P0+P1 items are DONE, promote AG-A and AG-B
# to READY and write their specs as the next Jules batch.

---

## ██ AG1 — AGENTIC PHASE 1: Agency Core
_These four groups must be built and merged before any AG2 work begins._
_Strict build order: AG-B → AG-A → AG-C → AG-D_

---

### AG-A — Planning Layer
_New file: `core/planner.py`_
_Dependency: AG-B-01 and AG-B-02 must be DONE first_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-A-01 | `core/planner.py` | Create GoalDecomposer class — accepts natural language goal, returns ordered list of tool-call steps with declared dependencies | `NEEDS_SPEC` | AG-B-01 |
| AG-A-02 | `core/planner.py` | Implement step dependency graph — steps declare which prior steps must complete before they can start | `NEEDS_SPEC` | AG-A-01 |
| AG-A-03 | `core/planner.py` + `core/capabilities.py` | Add plan validation — verify each step's required tool exists in CapabilityRegistry before execution begins | `NEEDS_SPEC` | AG-A-01 |
| AG-A-04 | `core/planner.py` | Add plan serialization — save/load active plans to/from data/plans/ as JSON so plans survive service restarts | `NEEDS_SPEC` | AG-B-03 |
| AG-A-05 | `core/planner.py` | Add plan branching — if step A fails, planner executes defined alternative step B (if-else planning) | `NEEDS_SPEC` | AG-A-02 |
| AG-A-06 | `data/plans/templates/` | Add plan templates — pre-built JSON templates for: market_check, expense_log, reminder_set | `DONE` | AG-A-01 |
| AG-A-07 | `core/planner.py` | Add plan confidence scoring — rate each generated plan 0.0–1.0; log score before execution | `NEEDS_SPEC` | AG-A-01 |
| AG-A-08 | `core/planner.py` | Add plan pre-announcement — NINA summarises what it will do and waits for /approve or /cancel before starting | `NEEDS_SPEC` | AG-A-01 |
| AG-A-09 | `core/planner.py` | Add per-step timeout budget — assign max_seconds per step; abort and mark failed if exceeded | `NEEDS_SPEC` | AG-A-02 |
| AG-A-10 | `core/planner.py` | Add /plan show command — display active plan: steps, statuses, current position, elapsed time via Telegram | `NEEDS_SPEC` | AG-A-01 |

---

### AG-B — Task State & Persistence
_New file: `core/task_store.py`_
_This is the foundation. Build AG-B-01 and AG-B-02 first — everything else depends on them._

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-B-01 | `core/task_store.py` | Create TaskStore class — full CRUD for Task objects persisted to data/tasks.json | `DONE` | — |
| AG-B-02 | `core/task_store.py` | Define Task schema — id, goal, plan_steps, status (pending/running/paused/done/failed), created_at, updated_at, retries, result | `NEEDS_SPEC` | AG-B-01 |
| AG-B-03 | `core/task_store.py` | Load open tasks on nina.service startup — TaskStore auto-resumes in-progress and pending tasks after restart | `DONE` | AG-B-01 |
| AG-B-04 | `core/task_store.py` | Add task indexing — lookup by status, tool_used, date range without full JSON scan | `NEEDS_SPEC` | AG-B-01 |
| AG-B-05 | `core/task_store.py` | Add /tasks list command — show active, pending, and failed tasks with summary via Telegram | `NEEDS_SPEC` | AG-B-01 |
| AG-B-06 | `core/task_store.py` | Add /task cancel <id> — gracefully stop a running task and mark it cancelled | `NEEDS_SPEC` | AG-B-01 |
| AG-B-07 | `core/task_store.py` | Add /task retry <id> — re-queue a failed task from its last failed step, not from the beginning | `NEEDS_SPEC` | AG-B-01 |
| AG-B-08 | `core/task_store.py` | Add task TTL — auto-expire completed tasks after N configurable days; archive to data/tasks_archive.json | `NEEDS_SPEC` | AG-B-01 |
| AG-B-09 | `core/task_store.py` | Add task dependency — Task B declares it must wait for Task A's completion before starting | `NEEDS_SPEC` | AG-B-01 |
| AG-B-10 | `core/task_store.py` | Add task priority queue — priority field (high/normal/low) determines which queued task runs first | `NEEDS_SPEC` | AG-B-01 |

---

### AG-C — AgentLoop Upgrade
_Existing file: `core/agent.py`_
_Dependency: AG-B-01 and AG-A-01 must be DONE first_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-C-01 | `core/agent.py` | Upgrade AgentLoop.run() to accept a Task object as input, not a raw message string | `NEEDS_SPEC` | AG-B-02 |
| AG-C-02 | `core/agent.py` | Add step-by-step executor — iterate through plan steps, call correct tool per step, store result in Task | `NEEDS_SPEC` | AG-C-01 |
| AG-C-03 | `core/agent.py` | Add step result piping — output of step N passed automatically as input context to step N+1 | `NEEDS_SPEC` | AG-C-02 |
| AG-C-04 | `core/agent.py` | Add mid-plan LLM reasoning — between steps, call LLM to interpret step output before deciding next step | `NEEDS_SPEC` | AG-C-02 |
| AG-C-05 | `core/agent.py` | Add loop detection guard — if same step attempted >3 times with identical input, break the loop | `NEEDS_SPEC` | AG-C-02 |
| AG-C-06 | `core/agent.py` | Add human-in-the-loop gate — steps marked require_approval=True pause until /approve or /reject via Telegram | `NEEDS_SPEC` | AG-C-02 |
| AG-C-07 | `core/agent.py` | Add parallel step executor — steps with no declared dependency run concurrently via asyncio.gather | `NEEDS_SPEC` | AG-C-02 |
| AG-C-08 | `core/agent.py` | Add step timeout watchdog — if step exceeds time budget, mark failed and route to fallback | `NEEDS_SPEC` | AG-A-09 |
| AG-C-09 | `core/agent.py` | Add agent execution log — write every step start/end/result to logs/agent_execution.jsonl | `NEEDS_SPEC` | AG-C-02 |
| AG-C-10 | `core/agent.py` | Add /agent status command — show current task, active step, elapsed time, last result via Telegram | `NEEDS_SPEC` | AG-C-02 |
| AG-C-11 | `core/agent.py` | Implement goal completion detector — after final step, second LLM call evaluates if original goal was achieved | `NEEDS_SPEC` | AG-D-01 |
| AG-C-12 | `core/agent.py` | Add graceful shutdown — on SIGTERM, AgentLoop saves current task state before process exits | `NEEDS_SPEC` | AG-B-01 |

---

### AG-D — Self-Verification Engine
_New file: `core/verifier.py`_
_Dependency: AG-C-02 must be DONE first_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-D-01 | `core/verifier.py` | Create StepVerifier class — checks whether a step's output satisfies its declared success_criteria | `DONE` | AG-C-02 |
| AG-D-02 | `core/verifier.py` + `core/capabilities.py` | Add output schema validation — each tool declares expected output schema; Verifier checks compliance after execution | `NEEDS_SPEC` | AG-D-05 |
| AG-D-03 | `core/verifier.py` | Add semantic verification — for LLM-generated outputs, second LLM call scores answer quality 1–5 | `DONE` | AG-D-01 |
| AG-D-04 | `core/verifier.py` | Add numeric assertion verifier — verify numeric outputs within declared expected range (e.g. price > 0) | `DONE` | AG-D-01 |
| AG-D-05 | `core/verifier.py` | Add non-empty verifier — simplest guard: step fails if output is None, empty string, or empty list | `DONE` | — |
| AG-D-06 | `core/verifier.py` + `core/planner.py` | Add replan trigger — when Verifier fails, send step back to Planner to generate alternative approach | `NEEDS_SPEC` | AG-D-01 |
| AG-D-07 | `core/verifier.py` + `core/task_store.py` | Add verification result storage — store pass/fail and reason per step inside the Task object | `NEEDS_SPEC` | AG-D-01 |
| AG-D-08 | `core/verifier.py` | Add verification scorecard — final task result includes per-step pass/fail summary from Verifier | `NEEDS_SPEC` | AG-D-07 |
| AG-D-09 | `core/verifier.py` + `core/capabilities.py` | Add custom verifier hooks — tools can register their own verifier function in CapabilityRegistry | `NEEDS_SPEC` | AG-D-01 |
| AG-D-10 | `core/verifier.py` | Add /verify last command — show verification results of last completed task via Telegram | `NEEDS_SPEC` | AG-D-08 |

---

## ██ AG2 — AGENTIC PHASE 2: Proactive Intelligence
_Start only after all AG1 groups (AG-A through AG-D) are merged and Guardian score is stable._

---

### AG-E — Event System
_New file: `core/events.py`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-E-01 | `core/events.py` | Create EventBus class — typed publish/subscribe for all internal NINA events | `NEEDS_SPEC` | AG1 complete |
| AG-E-02 | `core/events.py` | Define core event types — TASK_STARTED, TASK_COMPLETED, TASK_FAILED, STEP_DONE, ALERT_FIRED, MEMORY_UPDATED | `NEEDS_SPEC` | AG-E-01 |
| AG-E-03 | `core/events.py` | Add event persistence — write all events to logs/events.jsonl with timestamp and payload | `NEEDS_SPEC` | AG-E-01 |
| AG-E-04 | `core/events.py` + `core/task_store.py` | Add event-triggered task launching — MARKET_ALERT event auto-starts a defined downstream Task | `NEEDS_SPEC` | AG-E-02 |
| AG-E-05 | `core/events.py` | Add event filtering — subscribers declare event types they care about; receive no other noise | `NEEDS_SPEC` | AG-E-01 |
| AG-E-06 | `core/events.py` | Add event replay on startup — replay last N events so listeners restore state after restart | `NEEDS_SPEC` | AG-E-03 |
| AG-E-07 | `core/events.py` | Add event rate limiting — suppress duplicate events of same type within configurable cooldown window | `NEEDS_SPEC` | AG-E-01 |
| AG-E-08 | `core/events.py` | Add Telegram event notifier subscriber — high-priority events auto-push Telegram message | `NEEDS_SPEC` | AG-E-02 |
| AG-E-09 | `core/events.py` | Add /events last 10 command — show last 10 events with type, timestamp, payload summary via Telegram | `NEEDS_SPEC` | AG-E-03 |
| AG-E-10 | `core/events.py` + `core/task_store.py` | Add cross-task event wiring — Task A emits named event on completion that auto-triggers Task B | `NEEDS_SPEC` | AG-E-04 |

---

### AG-F — Autonomous Agents
_New directory: `tools/agents/`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-F-01 | `tools/agents/__init__.py` | Create BaseAutonomousAgent base class — run(), stop(), get_status() interface all agents must implement | `NEEDS_SPEC` | AG-E-01 |
| AG-F-02 | `tools/agents/market_agent.py` | MarketAgent — watches DSE/CSE prices on schedule, emits ALERT event when watchlist threshold crossed | `NEEDS_SPEC` | AG-F-01 |
| AG-F-03 | `tools/agents/expense_agent.py` | ExpenseAgent — monitors Telegram messages for expense patterns, auto-logs to finance tool | `NEEDS_SPEC` | AG-F-01 |
| AG-F-04 | `tools/agents/email_agent.py` | EmailAgent — polls EWS inbox periodically, classifies emails, surfaces top 3 urgent items | `NEEDS_SPEC` | AG-F-01 |
| AG-F-05 | `tools/agents/reminder_agent.py` | ReminderAgent — scans data/reminders.json every minute, fires due reminders as ALERT events | `NEEDS_SPEC` | AG-F-01 |
| AG-F-06 | `tools/agents/news_agent.py` | NewsAgent — fetches BD financial news daily, summarises and pushes to Telegram | `NEEDS_SPEC` | AG-F-01 |
| AG-F-07 | `tools/agents/health_agent.py` | HealthAgent — monitors nina.service logs for error patterns, fires ALERT on anomaly | `NEEDS_SPEC` | AG-F-01 |
| AG-F-08 | `tools/agents/quota_agent.py` | QuotaAgent — watches provider quota consumption, switches default provider before exhaustion | `NEEDS_SPEC` | AG-F-01 |
| AG-F-09 | `tools/agents/goal_tracker_agent.py` | GoalTrackerAgent — reviews open tasks daily, nudges user via Telegram on stalled goals | `NEEDS_SPEC` | AG-F-01 |
| AG-F-10 | `tools/agents/memory_agent.py` | MemoryAgent — reviews facts.json periodically, flags stale or contradictory facts for review | `NEEDS_SPEC` | AG-F-01 |
| AG-F-11 | `core/capabilities.py` | Add agent registry — register all autonomous agents; start/stop/status via /agent start <name> | `NEEDS_SPEC` | AG-F-01 |
| AG-F-12 | `core/capabilities.py` | Add /agents list command — show all agents, running/stopped status, last action time via Telegram | `NEEDS_SPEC` | AG-F-11 |

---

### AG-G — Proactive Intelligence Engine
_New file: `core/proactive.py`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-G-01 | `core/proactive.py` | Create ProactiveEngine — decides when and what to push to user without being asked | `NEEDS_SPEC` | AG-E-01 |
| AG-G-02 | `core/proactive.py` | Add daily briefing composer — weather + DSE + reminders + news in single Telegram message at 7:30 AM | `NEEDS_SPEC` | AG-G-01 |
| AG-G-03 | `core/proactive.py` | Add anomaly notifier — push Telegram alert unprompted when monitored metric crosses threshold | `NEEDS_SPEC` | AG-G-01 |
| AG-G-04 | `core/proactive.py` | Add task completion push — send result summary to user when background task completes | `NEEDS_SPEC` | AG-G-01 |
| AG-G-05 | `core/proactive.py` | Add smart quiet hours — respect configurable quiet hours in data/settings.json; no alerts 11PM–7AM | `NEEDS_SPEC` | AG-G-01 |
| AG-G-06 | `core/proactive.py` | Add notification deduplication — never send same alert twice within configurable time window | `NEEDS_SPEC` | AG-G-01 |
| AG-G-07 | `core/proactive.py` | Add /quiet <duration> command — pause all proactive messages for specified duration | `NEEDS_SPEC` | AG-G-01 |
| AG-G-08 | `core/proactive.py` | Add priority-based batching — batch low-priority alerts into single digest instead of individual spam | `NEEDS_SPEC` | AG-G-06 |

---

### AG-H — Tool Chaining Framework
_New file: `tools/chain.py`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-H-01 | `tools/chain.py` | Create ToolChain class — executes ordered list of tool calls with automatic data piping between steps | `NEEDS_SPEC` | AG1 complete |
| AG-H-02 | `tools/chain.py` | Add named output slots — each tool call defines output_key; downstream tools reference by name not position | `NEEDS_SPEC` | AG-H-01 |
| AG-H-03 | `tools/chain.py` | Add conditional branching — if tool_output["status"] == "alert" jump to step 5, else continue to step 3 | `NEEDS_SPEC` | AG-H-02 |
| AG-H-04 | `tools/chain.py` | Add chain dry-run mode — execute with mock outputs to validate chain logic before any real tool calls | `NEEDS_SPEC` | AG-H-01 |
| AG-H-05 | `data/chains/` + `tools/chain.py` | Add pre-built chain templates — expense_log_chain, market_check_chain, daily_brief_chain | `NEEDS_SPEC` | AG-H-01 |
| AG-H-06 | `tools/chain.py` | Add /chain run <name> command — execute named chain template on demand via Telegram | `NEEDS_SPEC` | AG-H-05 |
| AG-H-07 | `tools/chain.py` | Add chain execution history — store last 10 run results per chain in data/chain_history.json | `NEEDS_SPEC` | AG-H-01 |
| AG-H-08 | `tools/chain.py` | Add chain editor wizard — /chain edit <name> opens guided step-builder via Telegram | `NEEDS_SPEC` | AG-H-06 |

---

### AG-I — Agentic Memory
_Existing file: `core/memory.py`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-I-01 | `core/memory.py` | Add episodic memory — store past task executions (goal + result) as retrievable episodes in ChromaDB | `NEEDS_SPEC` | AG1 complete |
| AG-I-02 | `core/memory.py` + `core/planner.py` | Add memory-driven planning — Planner queries ChromaDB for similar past goals before generating new plan | `NEEDS_SPEC` | AG-I-01 |
| AG-I-03 | `core/memory.py` | Add outcome memory — store which plan succeeded for which goal type; reuse successful plans | `NEEDS_SPEC` | AG-I-01 |
| AG-I-04 | `core/memory.py` | Add working memory — short-term slot-based memory for current task context, cleared on task completion | `NEEDS_SPEC` | AG-I-01 |
| AG-I-05 | `core/memory.py` + `core/agent.py` | Add context injection from history — inject top-3 relevant past outcomes into current LLM system prompt | `NEEDS_SPEC` | AG-I-01 |
| AG-I-06 | `core/memory.py` | Add memory conflict resolver — detect contradictory facts; surface via /memory conflicts for user review | `NEEDS_SPEC` | AG-I-01 |
| AG-I-07 | `core/memory.py` | Add preference learning — store user correction patterns as preferences (e.g. always BDT not USD) | `NEEDS_SPEC` | AG-I-01 |
| AG-I-08 | `core/memory.py` + `core/task_store.py` | Add failure memory — when task fails, store failure reason in ChromaDB to avoid repeating same mistake | `NEEDS_SPEC` | AG-I-01 |
| AG-I-09 | `core/memory.py` | Add long-term goal memory — /goal set <text> stores persistent goal NINA references in daily briefing | `NEEDS_SPEC` | AG-I-01 |
| AG-I-10 | `core/memory.py` | Add /memory timeline command — show facts and episodes chronologically for past 7 days via Telegram | `NEEDS_SPEC` | AG-I-01 |

---

## ██ AG3 — AGENTIC PHASE 3: Tests
_Run in parallel with AG2. AG-J-10 is strictly last — requires all AG1 + AG2 stable._

### AG-J — Agentic Test Coverage
_Directory: `tests/`_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-J-01 | `tests/test_planner.py` | Unit tests for GoalDecomposer: goal parsing, step generation, dependency ordering | `NEEDS_SPEC` | AG-A-01 |
| AG-J-02 | `tests/test_task_store.py` | Unit tests for TaskStore: CRUD, persistence, TTL, status transitions | `DONE` | AG-B-01 |
| AG-J-03 | `tests/test_agent_loop.py` | Integration tests for upgraded AgentLoop: step execution, result piping, loop detection | `NEEDS_SPEC` | AG-C-01 |
| AG-J-04 | `tests/test_verifier.py` | Unit tests for StepVerifier: schema check, numeric assertion, semantic scoring | `DONE` | 2026-06-09 |
| AG-J-05 | `tests/test_events.py` | Unit tests for EventBus: publish, subscribe, filter, rate-limit, replay | `NEEDS_SPEC` | AG-E-01 |
| AG-J-06 | `tests/test_market_agent.py` | Unit tests for MarketAgent: mock price feed, threshold crossing, alert emission | `NEEDS_SPEC` | AG-F-02 |
| AG-J-07 | `tests/test_chain.py` | Unit tests for ToolChain: sequential execution, conditional branching, dry-run mode | `NEEDS_SPEC` | AG-H-01 |
| AG-J-08 | `tests/test_proactive.py` | Unit tests for ProactiveEngine: quiet hours enforcement, deduplication, batching | `NEEDS_SPEC` | AG-G-01 |
| AG-J-09 | `tests/test_memory_agentic.py` | Integration tests: episodic memory, working memory, preference learning | `NEEDS_SPEC` | AG-I-01 |
| AG-J-10 | `tests/test_e2e_agent.py` | End-to-end: submit goal → plan → step execution → verification → result | `NEEDS_SPEC` | AG-J-09 |

---

### AG-M — Throughput Maximizer
_MEGA-TASK: V2.0 Architecture Upgrade_
_Dependency: AG-B-01 and AG-B-02 must be DONE first_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-M-01 | Multi-module | 🚀 MEGA-TASK: NINA Throughput Maximizer (v2.0 Architecture) — Implement Domains 1-5 to accelerate NINA. | `READY` | AG-B-01 |
| AG-M-02 | Multi-module | 📉 MEGA-TASK: Token-Surgical Architecture (v2.1) — Aggressive cloud token reduction via local RAG and surgical context selection. | `DONE` | AG-M-01 |
| AG-M-03 | Multi-module | 🛠️ NF-EXT: Surgical Code Intelligence — Add `nf code symbol`, `find-symbol`, and `sigs` for zero-token code research. | `DONE` | — |
| AG-M-04 | `AGENTS.md` | 📝 DOC-COMP: Instruction Compression — Refactor `AGENTS.md` into high-density directives; move guides to `docs/agent-memory/`. | `DONE` | — |
| AG-M-05 | `ninaflash.py` | 📊 NF-BACKLOG: Incremental State Monitoring — Add `backlog summary` and `task active` to avoid reading full backlog tables. | `DONE` | — |
| AG-M-06 | `.geminiignore` | 🛡️ SEC-IGNORE: Global Context Filtering — Implement project-wide `.geminiignore` for automated context pruning. | `READY` | — |
| AG-M-07 | `ninaflash.py` | 🧹 NF-CLEAN: Automated Hygiene — Add `nf check code --fix` and `nf doc check --fix` for local error resolution. | `DONE` | — |
| AG-M-08 | `ninaflash.py` | 💓 NF-STATUS: High-Density Pulse — Implement `nf status --pulse` and `nf log next-id` for 10-line project heartbeats. | `DONE` | — |
| AG-M-09 | `ninaflash.py` | 📦 NF-ARCHIVE: Historical Offloading — Implement `nf backlog archive` to move `DONE` tasks to historical storage. | `DONE` | — |
| AG-M-10 | `ninagate/` | 📡 GATE-PROMPT: System Prompt Templating — Move `AGENTS.md` into cached NinaGate system prompts. | `DONE` | AG-M-04 |
| AG-M-11 | `ninaflash.py` | 📉 NF-LOG: Sliding Window Summarizer — Implement log compression and `nf log summarize` for noisy update logs. | `DONE` | — |
| AG-M-12 | `ninaflash.py` | 📦 NF-SESSIONS: Checkpoint & Resume — Add `nf session checkpoint` to preserve task state across restarts. | `DONE` | — |

---

### AG-N — Advanced Code Intelligence
_Focus: Zero-token research and semantic mapping_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-N-01 | `ninaflash.py` | Global Symbol Indexer — Generate JSON map of all classes/functions. | `DONE` | — |
| AG-N-02 | `ninaflash.py` | Local Call Graph Generator — Trace function calls locally without LLM. | `READY` | AG-N-01 |
| AG-N-03 | `core/` | Type Hint Enforcement — Automated script to add missing type hints. | `READY` | — |
| AG-N-04 | `ninaflash.py` | Dead Code Detector — Identify and flag unused functions/imports. | `READY` | — |
| AG-N-05 | `ninaflash.py` | Symbol-Based Context Injector — Read only the call stack of a function. | `READY` | AG-N-02 |
| AG-N-06 | `ninaflash.py` | Docstring Quality Audit — Score docstrings on clarity and completeness. | `READY` | — |
| AG-N-07 | `core/` | Automated Refactoring: Method Extraction — Split large functions via AST. | `READY` | — |
| AG-N-08 | `ninaflash.py` | Dependency Cycle Detector — Identify circular imports locally. | `READY` | — |
| AG-N-09 | `ninaflash.py` | Code Complexity Watchdog — Calculate cyclomatic complexity. | `READY` | — |
| AG-N-10 | `ninaflash.py` | Symbol Migration Tool — Automate renaming and moving symbols. | `READY` | — |

---

### AG-O — Automated Testing & QA
_Focus: Reducing debug turns through local verification_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-O-01 | `tests/` | Test Scaffold Generator — Create test stubs for every new function. | `READY` | — |
| AG-O-02 | `tests/` | Mutation Test Suite — Implement basic mutation testing for core modules. | `READY` | — |
| AG-O-03 | `tests/` | Coverage Optimizer — Identify "coldest" code paths with zero tests. | `READY` | — |
| AG-O-04 | `ninaflash.py` | Automated Regression Bench — Run benchmarks on every PR. | `READY` | — |
| AG-O-05 | `tests/` | Mock Factory — Automated generation of mocks for external APIs. | `READY` | — |
| AG-O-06 | `tests/` | Flaky Test Detector — Identify intermittent test failures. | `READY` | — |
| AG-O-07 | `tests/` | Integration Test Parallelizer — Run tests in concurrent chunks. | `READY` | — |
| AG-O-08 | `tests/` | Data-Driven Test Generator — Create tests from session logs. | `READY` | — |
| AG-O-09 | `bin/` | Security Scan: Dependency Audit — Automated venv security audit. | `READY` | — |
| AG-O-10 | `tests/` | Doc-Test Validator — Ensure MD code examples are runnable. | `READY` | — |

---

### AG-P — Performance & Latency
_Focus: High-velocity execution and low overhead_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-P-01 | `core/router.py` | Router Latency Optimizer — Profile and reduce router overhead. | `READY` | — |
| AG-P-02 | `core/router.py` | Persistent Response Cache — Move cache to SQLite for speed. | `READY` | — |
| AG-P-03 | `core/router.py` | Parallel Provider Dispatch — Concurrent routing to fallbacks. | `READY` | — |
| AG-P-04 | `core/config.py` | Hot-Reload Speedup — Optimize NinaConfig reload time. | `READY` | — |
| AG-P-05 | `core/memory.py` | Memory Fetch Indexer — Vector indexing for faster retrieval. | `READY` | — |
| AG-P-06 | `ninaflash.py` | Subprocess Pool — Reuse subprocesses for shell tools. | `READY` | — |
| AG-P-07 | `core/` | Async IO Optimization — Ensure non-blocking file/network ops. | `READY` | — |
| AG-P-08 | `core/task_store.py`| Task Queue Prioritizer — Move to priority-based execution. | `READY` | — |
| AG-P-09 | `core/observability.py`| Hardware Metric Optimization — Reduce sampling frequency. | `READY` | — |
| AG-P-10 | `main.py` | Startup Time Minimizer — Profile and reduce boot time. | `READY` | — |

---

### AG-Q — Memory & Knowledge
_Focus: Precision retrieval and minimal noise_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-Q-01 | `data/memory/` | ChromaDB Cluster — Shard vector memory by domain. | `READY` | — |
| AG-Q-02 | `core/memory.py` | Automatic Fact Extraction — LLM-driven mining of logs. | `READY` | — |
| AG-Q-03 | `core/memory.py` | Memory Conflict Resolver v2 — Automated contradiction detection. | `READY` | — |
| AG-Q-04 | `tools/` | Knowledge Graph Visualization — Generate DOT relationships. | `READY` | — |
| AG-Q-05 | `core/memory.py` | Memory Pruning — Remove redundant/low-utility memories. | `READY` | — |
| AG-Q-06 | `core/memory.py` | Context-Aware Memory Retrieval — Filter by task type. | `READY` | — |
| AG-Q-07 | `core/memory.py` | Shared Fact Validation — Cross-reference external sources. | `READY` | — |
| AG-Q-08 | `core/memory.py` | Episodic Memory Summarization — Compress old session logs. | `READY` | — |
| AG-Q-09 | `core/memory.py` | Entity Linking — Consolidate duplicate entities in memory. | `READY` | — |
| AG-Q-10 | `data/memory/` | Memory Backup Sync — Multi-region backup implementation. | `READY` | — |

---

### AG-R — Repository Hygiene
_Focus: Minimal repo size and clean structure_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-R-01 | `ninaflash.py` | Stale File Archiver — Auto-move 60-day untouched files. | `READY` | — |
| AG-R-02 | `requirements.txt`| Requirement Pinner — Lock dependencies to exact hashes. | `READY` | — |
| AG-R-03 | `ninaflash.py` | Large File Pointer — Move binary assets to external storage. | `READY` | — |
| AG-R-04 | `ninaflash.py` | Directory Structure Audit — Enforce snake_case rules. | `READY` | — |
| AG-R-05 | `ninaflash.py` | License Header Inserter — Add headers to all source files. | `READY` | — |
| AG-R-06 | `ninaflash.py` | Orphaned Config Cleaner — Remove unused keys from .env.example. | `READY` | — |
| AG-R-07 | `templates/` | Template Consolidator — Merge redundant dashboard templates. | `READY` | — |
| AG-R-08 | `ninaflash.py` | Automated CHANGELOG — Generate from commit history. | `READY` | — |
| AG-R-09 | `ninaflash.py` | Metadata Quality Gate — Require summaries for new dirs. | `READY` | — |
| AG-R-10 | `dashboard/` | Repo Hygiene Dashboard v2 — Health trends and drift alerts. | `READY` | — |

---

### AG-S — Interface & Interaction
_Focus: Fast feedback and low-overhead communication_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-S-01 | `interfaces/telegram_interface.py`| Telegram Batching — Consolidate short messages. | `READY` | — |
| AG-S-02 | `ninaflash.py` | CLI Progress Bars — Rich bars for long nf commands. | `READY` | — |
| AG-S-03 | `core/proactive.py`| Notification Priority — Gated alerts by activity hours. | `READY` | — |
| AG-S-04 | `interfaces/telegram_interface.py`| Telegram Inline Results — Inline query status checks. | `READY` | — |
| AG-S-05 | `core/observability.py`| Multi-Channel Alerts — Discord/Slack webhook support. | `READY` | — |
| AG-S-06 | `ninaflash.py` | Command Autocomplete — Bash/Zsh completion for nf. | `READY` | — |
| AG-S-07 | `dashboard/` | Visual Task Graph — Render current plan as SVG. | `READY` | — |
| AG-S-08 | `ninaflash.py` | Interactive REPL — shell-like interactive mode for nf. | `READY` | — |
| AG-S-09 | `interfaces/telegram_interface.py`| Voice Command Bridge — STT integration for voice. | `READY` | — |
| AG-S-10 | `dashboard/` | Dashboard Dark Mode — High-contrast visual polish. | `READY` | — |

---

### AG-T — Token & Context Engineering
_Focus: Absolute minimum context overhead_

| ID | File | Task | Status | Depends On |
|----|------|------|--------|------------|
| AG-T-01 | `core/agent.py` | Dynamic Prompting — Adjust prompt length by task diff. | `READY` | — |
| AG-T-02 | `ninaflash.py` | Context Window Estimator — Predict token usage before call. | `READY` | — |
| AG-T-03 | `core/agent.py` | Instruction Deduplication — Strip identical rules. | `READY` | — |
| AG-T-04 | `ninaflash.py` | Token-Optimized JSON — Key-abbreviations in exports. | `READY` | — |
| AG-T-05 | `ninaflash.py` | Differential PR Body — Symbol-focused descriptions. | `READY` | — |
| AG-T-06 | `ninaflash.py` | Tool Metadata Compression — Strip docstrings in prompt. | `READY` | — |
| AG-T-07 | `tools/` | Incremental Search — Search tools return delta only. | `READY` | — |
| AG-T-08 | `ninaflash.py` | Context-Specific Ignore — .geminiignore by task type. | `READY` | — |
| AG-T-09 | `core/nina.py` | Prompt Versioning — AB test different system prompts. | `READY` | — |
| AG-T-10 | `ninaflash.py` | Token Usage Forecasting — Predict weekly costs. | `READY` | — |
| AG-T-11 | `ninaflash.py` | Final Synthesis — Consolidate all 100+ functions. | `READY` | — |

---

## ██ Agentic Build Order (strict — do not deviate)

```
AG1 Phase 1:
  AG-B-01 → AG-B-02           ← Foundation. Nothing else starts until these exist.
  AG-A-01 → AG-A-02 → AG-A-03 ← GoalDecomposer
  AG-C-01 → AG-C-02 → AG-C-03 ← AgentLoop upgrade
  AG-D-05 → AG-D-01 → AG-D-02 ← Verifier: empty check first, then schema
  AG-A-04 + AG-B-03            ← Plan + task persistence on restart
  AG-C-11 + AG-D-06            ← Goal completion + replan trigger (wires AG-C to AG-D)
  Remaining AG-A/B/C/D in any order

AG2 Phase 2 (AG1 must be fully merged first):
  AG-E-01 → AG-E-02 → AG-E-03 ← EventBus core
  AG-F-01 → AG-F-02            ← BaseAgent + MarketAgent (first real autonomous agent)
  AG-G-01 → AG-G-05 → AG-G-06 ← ProactiveEngine core + quiet hours + dedup
  AG-H-01 → AG-H-02 → AG-H-03 ← ToolChain core
  AG-I-01 → AG-I-04 → AG-I-02 ← Episodic → working → memory-driven planning
  Remaining AG-E/F/G/H/I tasks in any order

AG3 Phase 3 (parallel with AG2):
  AG-J-01 through AG-J-09 in any order
  AG-J-10 strictly last
```

---

## ██ DONE — Completed Items

| ID | Title | Entry | PR | Date |
|----|-------|-------|----|------|
| F-02 | memory: deterministic personal_context | E-sync | — | 2026-06-09 |
| B-001 | Sentinel: shell=True fix in guardianengine.py | E-057 | #60 | 2026-06-07 |
| SCHED-ALL | 15 daily scheduled tasks defined | E-059 | — | 2026-06-07 |
| TRACK-ALL | jules_task_tracker.md + ninaflash_task_tracker.md created | E-059 | — | 2026-06-07 |
| B-024 | AGENTS.md: backlog update protocol | E-060 | — | 2026-06-07 |
| B-005 | F-09 ModelDiscoveryService — tools/model_discovery.py | E-061 | #25 | 2026-06-07 |
| B-037 | docs/space: add nina_architecture_diagram.md with ASCII diagrams | E-sync | #26 | 2026-06-07 |
| B-027 | tools/gputuner.py: add fallback when nvidia-smi not available | E-sync | #27 | 2026-06-07 |
| B-029 | Write integration test: full request through router → provider → response | E-sync | #28 | 2026-06-08 |
| B-025 | crons/manager.py: add graceful shutdown handler (SIGTERM) | E-sync | #29 | 2026-06-08 |
| B-017 | Write tests for core/router.py — provider ordering, circuit breaker, fallback | E-sync | #30 | 2026-06-08 |
| B-019 | Write tests for guardianengine.py — SIGNATURES check, run_cmd | E-sync | #33 | 2026-06-08 |
| R-78 | Fix tool grammar fragility — minimum viable guard | E-sync | #35 | 2026-06-08 |
| B-040 | Write CONTRIBUTING.md | E-sync | #36 | 2026-06-08 |
| B-021 | Add prometheus-style metrics endpoint to healthcheck.py | E-sync | #38 | 2026-06-08 |
| B-023 | Add AGENTS.md section: tracker update protocol for Jules tasks | E-sync | #43 | 2026-06-08 |
| B-007 | F-09 Part 3 — seed data/model_cache.json with all 16 providers | E-sync | #42 | 2026-06-08 |
| B-020 | Write tests for tools/model_discovery.py | E-sync | #41 | 2026-06-08 |
| B-022 | tools/compact_exporter.py: add progress logging for long exports | E-sync | #44 | 2026-06-08 |
| B-015 | crons/manager.py: add job execution metrics (duration, last_success, fail_count) | E-sync | #45 | 2026-06-08 |
| B-013 | healthcheck.py: replace bare except with typed exception handling | E-sync | #46 | 2026-06-08 |

---

## ██ Perplexity Session Briefing Protocol

At the start of every session where this file is attached, Perplexity will:

1. **Count READY items by tier** — "P0: N, P1: N, P2: N, AG1: N needs-spec"
2. **Unblock promotions** — any BLOCKED item whose dependency is now DONE → promote to READY
3. **Scan IN_PROGRESS / IN_PR** — report what is pending ninaflash merge
4. **Recommend next batch** — up to 15 non-overlapping READY tasks for Jules
5. **Generate Jules specs** — full paste-ready prompts for each recommended task
6. **Territory check** — confirm no two tasks in batch touch the same file
7. **AG pipeline gate** — if all P0+P1 are DONE, promote AG-B-01/AG-B-02 to READY and spec them as next Jules batch

---

## ██ ninaflash Backlog Update Protocol

After every Jules PR merge, ninaflash updates status using Python — never bash echo:

```python
from pathlib import Path

backlog_path = Path("/home/aibony/nina/docs/space/jules_backlog.md")
content = backlog_path.read_text()
content = content.replace(
    "| B-XXX | Title here | `READY`",
    "| B-XXX | Title here | `DONE`"
)
backlog_path.write_text(content)
```

---

## ██ Routing Rules (canonical)

| Route | Files |
|-------|-------|
| **Jules** | `core/*.py` (not router.py), `tools/*.py` (not shell.py), `tests/*.py`, `data/`, `docs/` |
| **ninaflash only** | `main.py`, `core/router.py`, `interfaces/telegraminterface.py`, `guardianengine.py`, `tools/shell.py`, `.env` |
| **ninaflash = merge executor** | All Jules PRs — never auto-merge via GitHub UI |
| **After every merge** | `./nina_sync.sh` — no exceptions |
| **Before any task** | `cat juleslock.txt` — do not proceed if target file is locked |

---

## ██ Daily Throughput Target

| Metric | Target |
|--------|--------|
| Scheduled tasks (auto) | 15/day |
| Feature tasks submitted to Jules | 10–15/day |
| PRs merged by ninaflash | 10–15/day |
| B-series backlog cleared | ~3–4 days at full pace |
| AG1 Phase 1 | ~1 week |
| AG2 Phase 2 | ~2 weeks |
| Full agentic NINA operational | ~3–4 weeks |

**The pipeline never empties. NINA development never stops.**```

### docs/space/jules_spec_archive_ops.md
Last modified: 2026-06-11 04:29:41
Size: 670 bytes
```markdown
📦 MEGA-TASK: NF-ARCHIVE Historical Offloading (AG-M-09)
Assignee: Jules (Async Cloud Coder)
Objective: Keep the main working documents lean by archiving historical data.

🏗️ Domain 1: Backlog Archiving
- nf backlog archive: Move all tasks with status `DONE` or `DEFERRED` from `docs/space/jules_backlog.md` to `docs/archive/jules_backlog_archive.md`.

🧠 Domain 2: Error Register Archiving
- nf error archive: Move `✅ FIXED` entries from `docs/space/nina_error_register.md` to `exports/nina_error_register_archive.md`.

📝 Acceptance Criteria:
- Archiving must be idempotent.
- Maintain a 10-entry "Recent History" in the main files for immediate context.
```

### docs/space/jules_spec_backlog_inc.md
Last modified: 2026-06-11 04:29:03
Size: 865 bytes
```markdown
📊 MEGA-TASK: NF-BACKLOG Incremental State (AG-M-05)
Assignee: Jules (Async Cloud Coder)
Objective: Reduce token consumption by providing high-density summaries of project state instead of reading large markdown tables.

🏗️ Domain 1: Backlog Summarization
- nf backlog summary: Provide a 5-line summary of the backlog: count of READY, IN_PROGRESS, BLOCKED, and DONE tasks.
- nf task active: List only tasks currently in `IN_PROGRESS` or `IN_PR` along with the files they have locked in `jules_lock.txt`.

🧠 Domain 2: Incremental Logs
- nf log tail <n>: Read only the last <n> entries of `nina_update_log.md`.
- nf log next-id: Parse the update log to find the last entry number and return the next available ID (e.g., "173").

📝 Acceptance Criteria:
- Commands must be fast and zero-token in cloud (local execution).
- Update `ninaflash.py` help menu.
```

### docs/space/jules_spec_doc_compression.md
Last modified: 2026-06-11 04:29:53
Size: 822 bytes
```markdown
📝 MEGA-TASK: DOC-COMP Instruction Compression (AG-M-04)
Assignee: Jules (Async Cloud Coder)
Objective: Refactor `AGENTS.md` into a high-density, token-efficient directive list.

🏗️ Domain 1: Structural Compression
- Move verbose "Guides", "Tool Lists", and "Examples" from `AGENTS.md` to dedicated files in `docs/agent-memory/workflow.md` or `docs/agent-memory/patterns.md`.
- Replace these with one-line pointers (e.g., "See docs/patterns.md for log formatting").

🧠 Domain 2: Directive Mapping
- Rewrite the "Rules of Engagement" into high-density "Directive Lists" (Goal-Restraint-Action).
- Example: Replace "Please never use git add ." with "Directive: NEVER use 'git add .'; stage specific files only."

📝 Acceptance Criteria:
- `AGENTS.md` file size reduced by >40%.
- All core constraints preserved.
```

### docs/space/jules_spec_gate_prompt.md
Last modified: 2026-06-11 04:29:47
Size: 794 bytes
```markdown
📡 MEGA-TASK: GATE-PROMPT System Prompt Templating (AG-M-10)
Assignee: Jules (Async Cloud Coder)
Objective: Shift instruction overhead from every turn's prompt to a cached system template in NinaGate.

🏗️ Domain 1: NinaGate Template Engine
- Update `ninagate/main.py` to support "System Templates." 
- Move the core `AGENTS.md` operating laws into a static JSON template.
- Implement a `/v1/chat/completions` wrapper that injects these templates based on a `X-NINA-ROLE` header.

🧠 Domain 2: Prompt Stripping
- Modify `nina.py` and `agent.py` to strip redundant instructions from the `AgentLoop` prompt if it detects it is running through NinaGate.

📝 Acceptance Criteria:
- Measured reduction in "Input Tokens" per turn.
- Compatibility with all BYOK tools (Aider, Cursor, etc.).
```

### docs/space/jules_spec_gemini_ignore.md
Last modified: 2026-06-11 04:29:34
Size: 803 bytes
```markdown
🛡️ MEGA-TASK: SEC-IGNORE Global Context Filtering (AG-M-06)
Assignee: Jules (Async Cloud Coder)
Objective: Automatically prune the agent's context window using project-wide exclusion rules.

🏗️ Domain 1: .geminiignore Implementation
- Create a canonical `.geminiignore` in the repo root.
- Exclusion list: `logs/`, `data/plans/`, `upgrades/backups/`, `*.pyc`, `__pycache__/`, `venv/`.

🧠 Domain 2: Tool-Level Compliance
- Update `ninaflash.py` and `tools/files.py` to respect `.geminiignore` patterns when listing or reading files.
- nf check ignore: A diagnostic command that shows which files are currently being hidden from the agent.

📝 Acceptance Criteria:
- Reduced "noise" in global searches (`grep_search`).
- No sensitive logs or large data files leaked into the cloud context.
```

### docs/space/jules_spec_hygiene_fix.md
Last modified: 2026-06-11 04:29:10
Size: 897 bytes
```markdown
🧹 MEGA-TASK: NF-CLEAN Automated Hygiene (AG-M-07)
Assignee: Jules (Async Cloud Coder)
Objective: Offload code linting and document formatting from the cloud agent to local ninaflash commands.

🏗️ Domain 1: Code Auto-Fixing
- nf check code --fix: Automatically run `ruff --fix` and `black` (if available) on the target file.
- Implement pre-commit hooks in `ninaflash` that prevent committing code with syntax errors.

🧠 Domain 2: Document Auto-Formatting
- nf doc check --fix: Automatically format the `nina_update_log.md` entry headers and tables to maintain repository standards.
- nf doc consolidate: Automatically move log entries older than 30 days into `exports/nina_update_log_archive.md`.

📝 Acceptance Criteria:
- No human intervention required for common linting/formatting fixes.
- `ninaflash.py` hard cap of 100 functions must be maintained (consolidate where possible).
```

### docs/space/jules_spec_log_summary.md
Last modified: 2026-06-11 04:29:22
Size: 773 bytes
```markdown
📉 MEGA-TASK: NF-LOG Sliding Window Summarizer (AG-M-11)
Assignee: Jules (Async Cloud Coder)
Objective: Prevent context overflow from noisy logs and long markdown files.

🏗️ Domain 1: Log Compression
- nf log summarize: Use a local tiny-model (via NinaGate) or regex patterns to collapse repeating log patterns.
- Implement a sliding window for `nina_update_log.md` where the agent only sees the "Relevant Window" (last 10 entries + task-specific entries).

🧠 Domain 2: Tool Log Rotation
- nf ops rotate-logs: Automatically compress and archive `logs/*.log` into `logs/archive/` using gzip.

📝 Acceptance Criteria:
- Log summarization must preserve all Entry IDs and Dates.
- Integration with `compact_exporter.py` to ensure `nina_latest.md` stays under 64KB.
```

### docs/space/jules_spec_session_mgmt.md
Last modified: 2026-06-11 04:29:28
Size: 860 bytes
```markdown
📦 MEGA-TASK: NF-SESSIONS Checkpoint & Resume (AG-M-12)
Assignee: Jules (Async Cloud Coder)
Objective: Ensure NINA's task state survives Gemini CLI session resets and crashes.

🏗️ Domain 1: Session Checkpointing
- nf session checkpoint: Save the current git branch, changed files, and the active "Goal" to `data/session_checkpoint.json`.
- nf session resume: Read the checkpoint and automatically restore the environment (git branch, re-verify changes).

🧠 Domain 2: Transient Memory
- nf memory stash <text>: Save a snippet of "Working Memory" (e.g., a specific line number or a temporary variable name) to a local JSON stash that persists across CLI restarts.

📝 Acceptance Criteria:
- Checkpoint file must be excluded from `.geminiignore` (it's for me to read).
- `ninaflash.py` implementation must handle JSON serialization errors gracefully.
```

### docs/space/jules_spec_status_pulse.md
Last modified: 2026-06-11 04:29:16
Size: 778 bytes
```markdown
💓 MEGA-TASK: NF-STATUS High-Density Pulse (AG-M-08)
Assignee: Jules (Async Cloud Coder)
Objective: Minimize context bloat by providing a ultra-short project pulse.

🏗️ Domain 1: The Pulse Command
- nf status --pulse: Returns exactly 10 lines containing:
  1. Git SHA + Branch
  2. Venv Status
  3. Last Sync Timestamp
  4. Active Lock Status (jules_lock.txt summary)
  5. Backlog Tally (READY/DONE)
  6. Recent Errors (last 3 from nina_error_register.md)
  7. Thermal/VRAM Status

🧠 Domain 2: Zero-Token Log Parsing
- nf log find-id <task_id>: Return only the log entry associated with a specific task ID without reading the full log file.

📝 Acceptance Criteria:
- Pulse output must be under 1KB.
- Command must be registered as a primary `ninaflash` capability.
```

### docs/space/jules_spec_surgical_intel.md
Last modified: 2026-06-11 04:28:57
Size: 1125 bytes
```markdown
🛠️ MEGA-TASK: NF-EXT Surgical Code Intelligence (AG-M-03)
Assignee: Jules (Async Cloud Coder)
Objective: Implement local code research tools in ninaflash to eliminate the need for full-file reads in the cloud.

🏗️ Domain 1: Symbol Extraction
- nf code symbol <file> <name>: Use Python's `ast` module to parse the file and return only the source code for the specified class or function.
- nf find-symbol <name>: Recursively search the repository for where the specified class or function is defined and return its file path and line number.

🧠 Domain 2: Symbol Mapping
- nf code sigs <dir>: Generate a high-density map of all function and class signatures in a directory. Output should include docstrings but skip method bodies.

📉 Domain 3: Docstring Search
- nf code doc <keyword>: Search for keywords only within docstrings to help find relevant tools and logic without full-text grep.

📝 Acceptance Criteria:
- All commands must be implemented as named functions in `ninaflash.py`.
- No new dependencies; use standard library `ast` and `pathlib`.
- Provide unit tests in `tests/test_ninaflash_ext.py`.
```

### docs/space/jules_spec_throughput_maximizer.md
Last modified: 2026-06-11 04:11:16
Size: 4904 bytes
```markdown
🚀 MEGA-TASK: NINA Throughput Maximizer (v2.0 Architecture) Assignee: Jules (Async Cloud Coder)
Objective: Transform ninaflash and NinaGate into a high-velocity, low-cost autonomous control plane that reduces cloud token usage by 90% and accelerates feature delivery by 10x.

🏗️ Domain 1: NinaGate "Fast-Path" & Local Drafting Engine Leverage NinaGate to move boilerplate and scaffolding from Cloud to Local AI.

    Local Fast-Path Routing: Add a local_fast model category to NinaGate. Route specifically to qwen2.5-coder:1.5b or deepseek-coder:1.3b on Ollama for instant local inference.
    Boilerplate Scaffolding: Implement nf draft. Use local Jinja2 templates + Local Fast-Path AI to generate NINA-style tool stubs and class structures for free.
    Local Syntax Fixer: Create a local hook that catches common Python syntax errors (missing imports, indentations) and uses the Local Fast-Path AI to fix them locally before a cloud turn is wasted.
    Commit Message Autogen: Add nf gen-commit. Analyzes git diff via NinaGate to generate structured, professional commit messages.
    Docstring Engine: Automatically populate missing docstrings in newly created files using local tiny-models.

🧠 Domain 2: Autonomous Governance & Self-Healing Move repository maintenance from "Manual Quests" to "Autonomous Tasks."

    Governance Task Feed: Update tools/generate_dashboard.py to output data/governance_tasks.json. Every "Missing Test" or "Low Metadata" entry is now an executable task object.
    IdleLoop Integration: Configure idleloop.py to consume the Task Feed. NINA now heals her own metadata and writes missing tests when idle.
    Repro Script Factory: When pytest fails, nf uses NinaGate to write a standalone bin/repro_fail_X.py script. The cloud agent's goal shifts from "fix bug" to "fix script."
    Dependency Self-Healer: Catch ModuleNotFoundError during local runs; nf automatically cross-references requirements.txt and runs pip install in the venv.
    Auto-Archiver: Automatically move files flagged as purge_candidate by the index into exports/archive/ after a 30-day window.

📉 Domain 3: Context Engineering & Token Compression Stop sending "Noise" to the cloud. Send only the "Signal."

    Context Distillation: Create nf distill
    The Bitmask Index: Generate a tiny, token-optimized version of nina_index.json containing only governed files and their guardrails.
    Task Sandboxing (Workbench): nf workbench --task F-06. Creates a transient directory of symlinks to ONLY the files relevant to the task (via dependency mapping).
    Virtual Governance Headers: Modify tools/files.py (read tool). When an agent reads a file, prepend a virtual header: # GOVERNANCE: ROLE=SOT, GUARDRAILS=APPEND_ONLY.
    Incremental Log Summarizer: Instead of full logs, nf provides a 10-line summary of the last 100 log entries using NinaGate.

🛡️ Domain 4: Decision Engine & Safety Rails Turn the index from a list of files into a "Rules of Engagement" enforcement engine.

    Workflow Compression (nf wrap): Consolidate update_index, validate, cleanup, dashboard, and sync into one high-level command.
    Semantic Relationship Mapping: Enhance query_index.py to show dependencies (e.g., "File X is used by Tool Y").
    Policy-Based Blocking: If a cloud agent attempts to write to a read_only_for_agents file, nf kills the task locally and immediately.
    Metadata Quality Scoring (Target: 95%): Add stricter scoring in validate_index.py that fails the build if new files lack summaries.
    Security Sandbox: nf runs bandit security scans automatically on every local modification.

📡 Domain 5: Visibility & Performance Watchdog Make NINA proactive in reporting her own health and speed.

    Proactive Telegram Governance Bot: NINA pings the user if hygiene metrics drop or if an autonomous task fails local validation.
    Performance Regression Watcher: Benchmark core functions (Router latency, Memory fetch time) after every merge. Flag regressions.
    Log Memory (ChromaDB): Index nina_update_log.md into NINA's vector memory so agents can "recall" previous fixes.
    Throughput Dashboard: Add a "Throughput" section to the Governance Dashboard tracking "Tasks Closed per Week" and "Tokens Saved via Local Drafting."
    Weekly Hygiene Report: Automated Sunday summary of repo drift and stale files sent via Telegram.

📝 Acceptance Criteria for Jules:

    Local Execution: All generation must use http://localhost:8765 (NinaGate).
    Governance: Every new tool/script must be indexed and have a doc_delta_required: true flag.
    Tests: Provide unit tests for each new nf command.
    Documentation: Update nina_update_log.md with an entry for every module completed.

Jules, you are cleared to proceed. This is a multi-file, multi-subsystem feature. Begin with Domain 1 (Fast-Path & Drafting) to establish the infrastructure for the rest of the work.
```

### docs/space/jules_spec_token_surgical.md
Last modified: 2026-06-11 04:17:04
Size: 2882 bytes
```markdown
📉 MEGA-TASK: Token-Surgical Architecture (v2.1)
Assignee: Jules (Async Cloud Coder)
Objective: Reduce NINA's total cloud token consumption by an additional 50% (on top of v2.0) by moving context management from "Dumb Truncation" to "Surgical Selection."

🏗️ Domain 1: Semantic Context Selection (Local-First RAG)
- nf context-map: Automatically generate a semantic map of the codebase using local models (qwen2.5:1.5b).
- nf chunk-search: Replace full-file reading with a RAG-based chunk search. Use ChromaDB locally. When an agent requests a file, nf returns only the relevant semantic chunks (e.g., "router's circuit breaker") across multiple files instead of entire large files.

🧠 Domain 2: Local Reasoning Offloading (Thinking-on-the-Edge)
- nf plan-local: Move the 7-step code scaffold reasoning (from AGENTS.md) to a local model (Ollama). The cloud agent only receives the final verified plan.
- Local Error Pre-Verification: Before the cloud agent attempts to "fix" a file, nf runs pyflakes and compile locally and provides a one-line error summary: "Fix IndentationError at line 45" instead of the whole file.

📉 Domain 3: Differential Context Injector (Git-Diff Primary)
- nf diff-context: Modify the primary agent prompt to prioritize git diff over file content. For files >500 lines, nf sends only the changed blocks + symbol outline (function signatures).
- Skeleton Outlining: Use the Python `ast` module to generate a "Skeleton" of large files. The cloud agent sees class/function signatures and docstrings but no bodies, unless specifically requested via `nf read --full`.

🛡️ Domain 4: Token-Aware Tooling (Surgical Read/Write)
- Surgical Read: Update tools/files.py to support line-range reads (`--lines 40-80`) and symbol-based reads (`--symbol HybridRouter`).
- Log Compression: Implement a sliding-window log summarizer in tools/ninaflash.py that collapses identical repeating log lines (e.g., "Heartbeat..." x 100) into a single summary line.

📡 Domain 5: NinaGate Prompt Optimization
- System Prompt Templating: Move the heavy AGENTS.md instructions into a cached system prompt in NinaGate. 
- Tool Definition Stripping: Dynamically strip unused tool definitions from the cloud agent's context based on the current task classification (e.g., remove "market" tools from a "coding" task).

📝 Acceptance Criteria for Jules:
1. Token Reduction: Demonstrate (via mocks or logs) that a standard coding task uses 30-50% fewer tokens.
2. Stability: Surgical reads must include enough context (at least 5 lines above/below) to prevent hallucination.
3. Documentation: Update nina_update_log.md for every module completed.
4. Testing: Provide unit tests for the RAG chunking and Skeleton outlining logic.

Jules, you are cleared to proceed with AG-M-02. Start with Domain 4 (Surgical Tooling) to enable the infrastructure for surgical reading.
```

### docs/space/jules_task_tracker.md
Last modified: 2026-06-11 03:15:37
Size: 5152 bytes
```markdown
# Jules Task Tracker
> Auto-updated by Jules after every task. Read by Perplexity via nina_latest.md backup.
> Format: append new rows via Python — never bash echo. Never delete rows — use status updates only.

## Status Legend
| Symbol | Meaning |
|--------|---------|
| ✅ ACTIVE | Scheduled task is live and healthy |
| ✅ DONE | One-off task completed successfully |
| ✅ MERGED | PR merged and deployed |
| 🔄 IN PR | PR open, awaiting merge |
| 🔄 PENDING | Task defined, not yet submitted |
| ⏳ QUEUED | Submitted to Jules, not yet started |
| ❌ FAILED | Last run errored — needs attention |
| ⏸️ PAUSED | Temporarily disabled |
| 🔒 LOCKED | juleslock.txt active for this task |

## Scheduled Tasks (SCHED-*)
| ID | Title | Status | Cadence | Last Run | Last PR | Notes |
|----|-------|--------|---------|----------|---------|-------|
| SCHED-01 | Daily lint sweep | 🔄 PENDING | Daily 02:00 | — | — | Not yet activated in Jules UI |
| SCHED-02 | Daily guardian health | 🔄 PENDING | Daily 02:10 | — | — | Not yet activated in Jules UI |
| SCHED-03 | Daily sync verification | 🔄 PENDING | Daily 02:20 | — | — | Not yet activated in Jules UI |
| SCHED-04 | Daily dependency audit | 🔄 PENDING | Daily 02:30 | — | — | Not yet activated in Jules UI |
| SCHED-05 | Daily model string audit | 🔄 PENDING | Daily 02:40 | — | — | Not yet activated in Jules UI |
| SCHED-06 | Daily dead link scan | 🔄 PENDING | Daily 02:50 | — | — | Not yet activated in Jules UI |
| SCHED-07 | Daily update log archive | 🔄 PENDING | Daily 03:00 | — | — | Not yet activated in Jules UI |
| SCHED-08 | Daily AGENTS.md freshness | 🔄 PENDING | Daily 03:10 | — | — | Not yet activated in Jules UI |
| SCHED-09 | Daily error register sweep | 🔄 PENDING | Daily 03:20 | — | — | Not yet activated in Jules UI |
| SCHED-10 | Daily lock cleanup | 🔄 PENDING | Daily 03:30 | — | — | Not yet activated in Jules UI |
| SCHED-11 | Daily test scaffold | 🔄 PENDING | Daily 03:40 | — | — | Not yet activated in Jules UI |
| SCHED-12 | Daily Bandit security | 🔄 PENDING | Daily 03:50 | — | — | Not yet activated in Jules UI |
| SCHED-13 | Daily pin audit | 🔄 PENDING | Daily 04:00 | — | — | Not yet activated in Jules UI |
| SCHED-14 | Daily arch docs freshness | 🔄 PENDING | Daily 04:10 | — | — | Not yet activated in Jules UI |
| SCHED-15 | Daily circuit breaker stats | 🔄 PENDING | Daily 04:20 | — | — | Not yet activated in Jules UI |

## Async Tasks (ASYNC-*)
| ID | Title | Status | Submitted | PR | Entry | Notes |
|----|-------|--------|-----------|-----|-------|-------|
| ASYNC-01 | Sentinel shell=True fix | ✅ MERGED | 2026-06-07 | PR #60 | E-057 | guardian_engine.py |
| ASYNC-02 | F-09 ModelDiscoveryService | ✅ MERGED | 2026-06-07 | PR #25 | E-061 | Spec ready, submitted and merged |

| ASYNC-03 | B-002: Wire model_overrides dict to .env hot-reload in router.py | ✅ MERGED | 2026-06-07 | PR | 2026-06-09 | Session: [13876164946786086522](https://jules.google.com/session/13876164946786086522) |
| ASYNC-04 | B-003: Add timeout to all subprocess calls in compact_exporter.py | ✅ MERGED | 2026-06-07 | PR | 2026-06-09 | Session: [890874151317558069](https://jules.google.com/session/890874151317558069) |
| ASYNC-05 | B-004: Validate TELEGRAM_CHAT_ID exists before any send attempt | ✅ MERGED | 2026-06-07 | PR | 2026-06-09 | Session: [3544127208157451730](https://jules.google.com/session/3544127208157451730) |
| ASYNC-06 | B-007: F-09 Part 3 — seed data/model_cache.json with all 16 providers | ✅ MERGED | 2026-06-07 | PR #42 | 2026-06-08 | Session: [4718778617163535359](https://jules.google.com/session/4718778617163535359) |
| ASYNC-07 | B-013: healthcheck.py: replace bare except with typed exception handling | ✅ MERGED | 2026-06-07 | PR #46 | 2026-06-08 | Session: [10635814989193465007](https://jules.google.com/session/10635814989193465007) |
| ASYNC-08 | B-014: Add startup banner to main.py showing active providers + model strings | ⏳ QUEUED | 2026-06-07 | — | — | Session: [16604506654173776295](https://jules.google.com/session/16604506654173776295) |
| ASYNC-09 | B-015: crons/manager.py: add job execution metrics (duration, last_success, fail_count) | ✅ MERGED | 2026-06-07 | PR #45 | 2026-06-08 | Session: [6671558330966465193](https://jules.google.com/session/6671558330966465193) |
| ASYNC-10 | AG-B-01: Create TaskStore with full CRUD and JSON persistence | ✅ MERGED | 2026-06-08 | PR #50 | E-121 | Submitted via ninaflash |
| ASYNC-11 | AG-D-05: Create StepVerifier with non-empty output check | ✅ MERGED | 2026-06-08 | PR #51 | E-122 | Submitted via ninaflash |
| ASYNC-12 | AG-D-01: Extend StepVerifier with criteria, numeric, schema checks | ✅ MERGED | 2026-06-08 | PR #53 | E-123 | Submitted via ninaflash |
| ASYNC-13 | AG-B-03: Add startup auto-resume to TaskStore | ✅ MERGED | 2026-06-08 | PR #55 | E-124 | Submitted via ninaflash |
| ASYNC-14 | AG-B-05: Add format_tasks_summary and format_task_detail to TaskStore | ✅ MERGED | 2026-06-08 | PR #57 | E-125 | Submitted via ninaflash |
```

### docs/space/nina_architecture_diagram.md
Last modified: 2026-06-08 00:29:48
Size: 7892 bytes
```markdown
# NINA Architecture Diagram

This document details the core architecture and operational flow of the NINA system (v12).

## High-Level System Architecture

```ascii
                      +-------------------------------------------------+
                      |                Telegram Interface               |
                      |          (interfaces/telegram_interface.py)     |
                      |  - Receives user input                          |
                      |  - Sends markdown formatted replies             |
                      |  - Handles commands (/ask, /task, /shell, etc)  |
                      +-----------------------+-------------------------+
                                              |
                                              v
                      +-----------------------+-------------------------+
                      |                   NinaOS (Core)                 |
                      |                 (core/nina.py)                  |
                      |  - Orchestrator for all sub-systems             |
                      |  - Manages startup, shutdown, lock              |
                      +---+-------------------+---------------------+---+
                          |                   |                     |
          +---------------+                   |                     +-----------------+
          |                                   |                                       |
+---------v---------+               +---------v---------+                   +---------v---------+
|   MemorySystem    |               |    AgentLoop      |                   |   TaskScheduler   |
| (core/memory.py)  |               |  (core/agent.py)  |                   |  (crons/manager)  |
| - ChromaDB facts  | <-----------> | - THINK/PLAN/ACT  |                   | - APScheduler     |
| - JSON reminders  |               | - Thermal guards  |                   | - Reminder checks |
| - Context builder |               | - Task budget     |                   | - Daily reports   |
+-------------------+               +----+----+----+----+                   +-------------------+
                                         |    |    |
                   +---------------------+    |    +---------------------+
                   |                          |                          |
                   v                          v                          v
         +-------------------+      +-------------------+      +-------------------+
         |    Tools Dict     |      |   HybridRouter    |      |  UpgradePipeline  |
         | (tools/*.py)      |      | (core/router.py)  |      | - Idle updates    |
         | - shell, web,     |      | - Provider health |      | - Self-patching   |
         | - system, browser |      | - Rate limits     |      +-------------------+
         | - jules           |      | - Cost tracking   |
         +-------------------+      +---------+---------+
                                              |
                                              v
                                    +-------------------+
                                    |    Providers      |
                                    | - LOCALFAST       |
                                    | - Cloud (Tier 1-3)|
                                    +-------------------+
```

## The Agent Loop (THINK -> PLAN -> ACT -> OBSERVE)

```ascii
+-----------------------+
|  User Goal Received   |
+-----------+-----------+
            |
            v
+-----------+-----------+       +-------------------+
| System Frame Injected | ----> |   Memory Context  |
| (Goal + Rules)        | <---- |   (ChromaDB)      |
+-----------+-----------+       +-------------------+
            |
            v
+-----------+-----------+
|      Step Loop        | <------------------------------------+
| (Up to task budget)   |                                      |
+-----------+-----------+                                      |
            |                                                  |
            v                                                  |
+-----------+-----------+       +-------------------+          |
|    Hybrid Router      | ----> |   Model Provider  |          |
|   (Route request)     | <---- |   (Response)      |          |
+-----------+-----------+       +-------------------+          |
            |                                                  |
            +------------------------------------+             |
            |                                    |             |
            v                                    v             |
+-----------+-----------+              +---------+---------+   |
|   Response Analysis   |              |  Response Analysis|   |
|   Contains "TOOL:"?   |              | Contains "FINAL:"?|   |
+-----------+-----------+              +---------+---------+   |
            |                                    |             |
            v (Yes)                              v (Yes)       |
+-----------+-----------+              +---------+---------+   |
|    Execute Tool       |              |    Self-Check     |   |
| (shell, web, system)  |              | (Review accuracy) |   |
+-----------+-----------+              +---------+---------+   |
            |                                    |             |
            v                                    v             |
+-----------+-----------+              +---------+---------+   |
|   Append Output to    |              |  Return Final     |   |
|      Scratchpad       | -------------|     Answer        |   |
+-----------------------+              +-------------------+   |
            |                                                  |
            +--------------------------------------------------+
```

## Hybrid Router & Provider Selection

```ascii
+-----------------------+
|     Route Request     |
| (Prompt, Task Type)   |
+-----------+-----------+
            |
            v
+-----------+-----------+       +-------------------+
|       Cache Check     | ----> |    Return Cached  | (If hit)
|  (Prompt + Messages)  |       |      Result       |
+-----------+-----------+       +-------------------+
            | (Miss)
            v
+-----------+-----------+
|    Provider Ordering  |
| - Bangla overrides    |
| - Task sensitivity    |
| - Provider score      |
+-----------+-----------+
            |
            v
+-----------+-----------+
|    Provider Attempt   | <----------------+
| (Wait for rate limit) |                  |
+-----------+-----------+                  |
            |                              |
            +-------------------+          |
            |                   |          |
            v (Success)         v (Fail)   |
+-----------+-----------+   +---+----------+----+
|  Record Metrics &     |   |  Record Failure   |
|       Cost            |   | (Cooldown, error) |
+-----------+-----------+   +---+----------+----+
            |                   |
            v                   v
+-----------+-----------+   +---+-------------------+
|    Return Result      |   | Try Next Provider /   |
+-----------------------+   | Raise Error if Exhausted|
                            +-----------------------+
```

## Data Persistence Strategy

* **Memory (`core/memory.py`):** Uses ChromaDB for factual/historical conversations, stored locally in `data/memory/chromadb`. Reminder engine writes to JSON (`data/reminders.json`).
* **Router Cache (`core/router.py`):** Uses an in-memory dictionary caching mechanism, potentially persisted locally based on configuration.
* **Costs & Metrics:** Stored in local JSON files (e.g. `data/cost.json`, `data/metrics.json`) via explicit persistence calls.
* **Logs (`logs/*.log`):** Application logs separated by module (e.g., `agent.log`, `router.log`, `nina.log`), with daily rotation.
```

### docs/space/nina_architecture_spec_v1.md
Last modified: 2026-06-10 22:24:05
Size: 10266 bytes
```markdown
# NINA Modular Monolith — Architecture Spec v1.0
**Author:** Baizid Bostami (aibony)  
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
```

### docs/space/nina_error_register.md
Last modified: 2026-06-11 12:22:38
Size: 6696 bytes
```markdown
---
title: NINA Error & Fix Register
version: 1.0
updated: 2026-06-06
source: auto-generated by ninaflash D-06 from update_log + guardian signatures + context
note: Update row status after every fix. Append new rows, never delete old ones.
---

## Legend
🔴 BLOCKER | 🟠 WARN | 🟡 DEBT | 🔵 OPEN/PENDING | ✅ FIXED

| ID | Severity | Component | Issue (short) | Status | Assignee | Fixed In | File(s) |
|----|----------|-----------|---------------|--------|----------|----------|---------|
| config.missing_env.apisecretkey | 🔴 BLOCKER | core.config | APISECRETKEY missing or empty in .env | ✅ FIXED | unassigned | v12.2.0 | .env, core/config.py |
| config.missing_env.authorizeduserid | 🔴 BLOCKER | core.config | AUTHORIZEDUSERID missing from .env | ✅ FIXED | unassigned | v12.2.0 | .env, core/config.py |
| config.missing_env.telegrambottoken | 🔴 BLOCKER | core.config | TELEGRAMBOTTOKEN missing from .env | ✅ FIXED | unassigned | v12.2.0 | .env, core/config.py |
| cron.conflicting_id | 🔴 BLOCKER | crons.manager | APScheduler ConflictingIdError — duplicate job ID | ✅ FIXED | unassigned | R-23 | crons/manager.py |
| process.ghost_instance | 🔴 BLOCKER | process | Ghost NINA process still running | ✅ FIXED | unassigned | v12.0.0 | data/nina.pid, main.py |
| process.lock_conflict | 🔴 BLOCKER | process | BlockingIOError on nina.lock — concurrent process conflict | ✅ FIXED | unassigned | v12.0.0 | data/nina.lock, main.py |
| router.attr.forcelocal | 🔴 BLOCKER | core.router | NameError: forcelocal not defined (should be force_local) | ✅ FIXED | unassigned | R-70 | core/router.py, core/agent.py |
| router.attr.orderedproviders | 🔴 BLOCKER | core.router | HybridRouter AttributeError: ordered_providers vs _ordere... | ✅ FIXED | unassigned | R-69 | core/router.py |
| router.attr.self_http | 🔴 BLOCKER | core.router | HybridRouter AttributeError: self._http vs self.http | ✅ FIXED | unassigned | R-72 | core/router.py |
| startup.attributeError | 🔴 BLOCKER | startup | AttributeError at startup/import | ✅ FIXED | unassigned | v12.2.0 | main.py |
| startup.importError | 🔴 BLOCKER | startup | ImportError or ModuleNotFoundError at startup | ✅ FIXED | unassigned | v12.2.0 | main.py |
| startup.nameError | 🔴 BLOCKER | startup | NameError at startup/import | ✅ FIXED | unassigned | v12.2.0 | main.py |
| startup.syntaxError | 🔴 BLOCKER | startup | SyntaxError in Python source file | ✅ FIXED | unassigned | v12.2.0 | main.py |
| startup.typeError | 🔴 BLOCKER | startup | TypeError at startup/import | ✅ FIXED | unassigned | v12.2.0 | main.py |
| capabilities.race_condition | 🟠 WARN | core.capabilities | Race condition on capabilities.json writes | ✅ FIXED | unassigned | D-22 | core/capabilities.py |
| cron.lambda_coroutine_drop | 🟠 WARN | crons.manager | APScheduler lambda returning coroutine without await | ✅ FIXED | unassigned | D-23 | crons/manager.py |
| hotreload.deleted_key_revert | 🟠 WARN | core.hotreload | Hot-reload silently ignores deleted .env keys | ✅ FIXED | unassigned | R-44 | core/hotreload.py |
| logger.duplicate_handler | 🟠 WARN | core.nina | Duplicate log handler added on every restart | ✅ FIXED | unassigned | D-21 | core/nina.py |
| memory.blocking_io_in_async | 🟠 WARN | core.memory | Blocking IO inside async memory methods | ✅ FIXED | unassigned | R-34 | core/memory.py |
| queue.path_mismatch | 🟠 WARN | core.nina | Idle queue path mismatch: idlequeue.json vs idle_queue.json | ✅ FIXED | unassigned | R-61 | core/nina.py, tools/upgradepipeline.py |
| router.cache.dict_mutation | 🟠 WARN | core.router | ResponseCache purge_expired mutates dict during iteration | ✅ FIXED | unassigned | R-58 | core/router.py |
| router.fallback.no_user_safe_reply | 🟠 WARN | core.router | Router raises RuntimeError instead of user-safe fallback ... | ✅ FIXED | unassigned | R-59 | core/router.py |
| telegram.document.handler_order | 🟠 WARN | interfaces.telegram | Document uploads silently dropped — handler order bug | ✅ FIXED | unassigned | D-20 | interfaces/telegram_interface.py |
| telegram.key.echoed_in_chat | 🟠 WARN | interfaces.telegram | API key echoed in Telegram chat without masking | ✅ FIXED | unassigned | D-20 | interfaces/telegram_interface.py |
| telegram.parsemode.badrequest | 🟠 WARN | interfaces.telegram | Telegram BadRequest caused by parse_mode=Markdown | ✅ FIXED | unassigned | D-20 | interfaces/telegram_interface.py |
| browser.ssrf.guard_regression | 🟡 DEBT | tools.browser | SSRF guard uses substring matching instead of ipaddress m... | ✅ FIXED | unassigned | R-64 | tools/browser.py |
| pipeline.eval_regex_weak | 🟡 DEBT | tools.upgradepipeline | Weak eval/exec/compile regex in upgrade scanner | ✅ FIXED | unassigned | R-54 | tools/upgradepipeline.py |
| pipeline.no_content_type_guard | 🟡 DEBT | tools.upgradepipeline | Remote patch fetch missing Content-Type and size guard | ✅ FIXED | unassigned | R-63 | tools/upgradepipeline.py |
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
| E-062 | 🔵 INFO | - | B-020 promoted READY — B-005 dependency confirmed DONE (PR #25) | CLOSED | unassigned | 2026-06-08 | - |

Archived FIXED entries → exports/nina_error_register_archive.md
```

### docs/space/nina_exporter_contract.md
Last modified: 2026-06-11 03:15:37
Size: 2522 bytes
```markdown
# nina_latest.md — Exporter Contract

## Purpose
This contract defines the mandatory sections that tools/compact_exporter.py
MUST include in every nina_latest.md export. If any section is missing or
shows "not parsed", the exporter is broken and must be fixed before the
next session.

## Mandatory Sections (in order)

### 1. Header
- Generated timestamp
- Repo, branch, Python version
- Purpose line: "AI context snapshot for Perplexity Space"

### 2. Executive Snapshot
Must contain ALL of the following subsections:
- Identity & Deployment Summary (project name, owner, machine, service)
- Core Architecture Summary (provider tiers, routing score algorithm)
- NINA Tool Routing Policy v2 Summary (3-row tool table: Perplexity / Jules / ninaflash)
- Three-Tool Parallel Model (the 7-step parallel loop)
- ninaflash as Merge Executor — Mandatory (4-rule block)
- Key Rules (high-risk file list, juleslock check, sensitive paths)
- High-Risk Files
- Latest Verified Runtime Status (guardian health score, BLOCKER/WARN counts)

### 3. Current Action Board
- Summary counts (BLOCKER, WARN, DEBT, FEATURE_PENDING)
- All OPEN issues with ID, severity, component, assignee

### 4. Current Phase Roadmap
- Current stage and next task
- Open milestones

### 5. Recent Meaningful Changes
- Last 5 meaningful update log entries (skip D-sync spam)

### 6. Key Rules (ninaflash + Jules)
- ninaflash mandatory rules after every code change
- ninaflash mandatory rules after every task close
- Jules rules
- Guardian gate
- Never-do list

### 7. Targeted Code Context
- compact signatures for: core/router.py, core/agent.py, core/nina.py,
  interfaces/telegram_interface.py, core/memory.py
- full source for: tools/shell.py, tools/browser.py

## Validation Test
After every exporter run, confirm these strings appear in nina_latest.md:
- "ARCHITECT" (routing policy table)
- "ASYNC CLOUD CODER" (routing policy table)
- "LOCAL MUSCLE" (routing policy table)
- "ninaflash as Merge Executor" (executive snapshot section)
- "The Full Parallel Loop" (executive snapshot section)
- "BLOCKER" (action board)
- "Guardian Gate" (key rules)

If any string is missing, the exporter has a parse failure. Fix compact_exporter.py
before uploading nina_latest.md to Perplexity Space.

## Parse Failure History
- 2026-06-07: "NINA Tool Routing Policy v2 Summary" section was not parsed due to
  heading mismatch between nina_state.md and compact_exporter.py section matcher.
  Fixed by aligning the section header string in compact_exporter.py.
```

### docs/space/ninaflash_task_tracker.md
Last modified: 2026-06-11 03:15:39
Size: 1142 bytes
```markdown
# ninaflash Task Tracker
> Updated by ninaflash after every task via Python append. Read by Perplexity via nina_latest.md backup.
> Format: append new rows via Python — never bash echo. Never delete rows — use status updates only.

## Status Legend
| Symbol | Meaning |
|--------|---------|
| ✅ DONE | Completed, committed, pushed |
| 🔄 PENDING | Defined, not yet started |
| ⏳ IN PROGRESS | ninaflash currently working |
| ❌ FAILED | Errored — see Notes |
| ⏸️ BLOCKED | Waiting on dependency |

## Task Log
| ID | Title | Status | Started | Completed | Entry | Depends On | Notes |
|----|-------|--------|---------|-----------|-------|------------|-------|
| NINAFLASH-01 | Upgrade Gemini to gemini-2.5-flash | ✅ DONE | 2026-06-07 | 2026-06-07 | E-057 | — | router.py |
| NINAFLASH-02 | Wire model_overrides to .env | 🔄 PENDING | — | — | — | ASYNC-02 | After F-09 merges |
| NINAFLASH-03 | Merge PR F-09 ModelDiscovery | ⏸️ BLOCKED | — | — | — | ASYNC-02 submitted | Not yet in PR |
| B-008 | Circuit Breaker Persistence | ✅ DONE | 2026-06-09 | 2026-06-09 | E-141 | — | router.py persistence |
```

### docs/space/nina_governance_dashboard.md
Last modified: 2026-06-11 03:33:00
Size: 2374 bytes
```markdown
# NINA Governance Dashboard
_Generated by `tools/generate_dashboard.py` on 2026-06-11 03:33:00_

## 1. Summary Metrics
- **Metadata Completeness:** 81.0% (Threshold: 75.0%)
- **Governed Files:** 1845
- **Duplicate Clusters:** 148
- **Purge Candidates:** 461
- **Files Requiring Tests:** 50
- **Files Missing Obvious Tests:** 34

## 2. Hotspots

### Top 10 Missing-Test Files
- `crons/manager.py`
- `crons/backup_jobs.py`
- `crons/runner.py`
- `tools/providerhunter.py`
- `tools/audit_repo_hygiene.py`
- `tools/ninaflash.py`
- `tools/upgradepipeline.py`
- `tools/system.py`
- `tools/compact_exporter.py`
- `tools/validate_index.py`

### Top 10 Lowest Metadata Quality
- `LICENSE` (80%)
- `nina_docs_export.sh` (80%)
- `Makefile` (80%)
- `pytest.ini` (80%)
- `jules_lock.txt` (80%)
- `.env` (80%)
- `requirements.txt` (80%)
- `.env.example` (80%)
- `commit_message.txt` (80%)
- `pr_desc.txt` (80%)

### Top Duplicate Clusters
- `dup-0005` (73 members) -> Canonical: `upgrades/incidents/guardian_20260523_214327/recent_changes.txt`
- `dup-0025` (43 members) -> Canonical: `upgrades/backups/backup_20260606_234938/tools/system.py`
- `dup-0047` (35 members) -> Canonical: `upgrades/backups/backup_20260608_115158/tools/upgradepipeline.py`
- `dup-0048` (35 members) -> Canonical: `upgrades/backups/backup_20260608_115158/tools/officemail.py`
- `dup-0049` (35 members) -> Canonical: `upgrades/backups/backup_20260608_115158/tools/shell.py`

### Top Purge Candidates & Ephemeral Paths
- `exports/nina_problem_log_archive.md`
- `exports/nina_latest.md`
- `upgrades/incidents/guardian_20260523_214327/evidence.txt`
- `upgrades/incidents/guardian_20260523_214327/journal.txt`
- `upgrades/incidents/guardian_20260523_214327/report.json`

## 3. Guardrail Hotspots
- **high_risk_do_not_edit_directly** (7 files): `.env`, `main.py`, `guardian_engine.py`...
- **append_only** (2 files): `nina_update_log.md`, `docs/space/nina_error_register.md`
- **read_only_for_agents** (4 files): `docs/nina_v12_blueprint.md`, `docs/space/nina_index.json`, `docs/space/nina_index.md`...

## 4. Recommended Actions
1. **Testing:** Write tests for the top missing-test files to improve system resilience.
2. **Cleanup:** Run `python3 tools/cleanup_by_index.py` and review output to clear purge candidates.
3. **Metadata:** Enrich summaries for the lowest quality metadata files in `tools/update_index.py`.
```

### docs/space/nina_index.json
Last modified: 2026-06-11 12:41:02
Size: 123055 bytes
```markdown
{
  "version": "1.2",
  "updated": "2026-06-10",
  "governed_scope": "All docs under docs/ and docs/space/, shims/scripts under tools/, configs (*.service, requirements.txt, .env.example), exported snapshots in exports/ and logs. Excludes temp data and cache.",
  "files": [
    {
      "path": ".ninaignore",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "ninagate_load_test.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": ".gitignore",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "main.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [
        "high_risk_do_not_edit_directly"
      ],
      "summary": "Primary entry point for the NINA systemd service.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools.log",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": ".env.example",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "CHANGELOG.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "User-friendly summary of major version releases.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "jules_lock.txt",
      "category": "other",
      "role": "system_of_record",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "system_of_record",
        "active"
      ]
    },
    {
      "path": "WORKFLOW.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Repository rules of engagement and development lifecycle.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_cleanup.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Permanent wrapper script for safe redundancy cleanup execution.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "LICENSE",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_audit.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Permanent wrapper script for the repository hygiene audit.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "guardian_engine.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [
        "high_risk_do_not_edit_directly"
      ],
      "summary": "Forensic AST scanner and baseline drift analyzer (73KB).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_codebase_backup.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "pytest.ini",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_update_log.md",
      "category": "doc",
      "role": "system_of_record",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [
        "append_only"
      ],
      "summary": "Canonical live activity log (Entry 001-167). Newest entries at top.",
      "tags": [
        "doc",
        "system_of_record",
        "active"
      ]
    },
    {
      "path": "pr_desc.txt",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "CONTRIBUTING.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "requirements.txt",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": ".coverage",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_sync.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Post-session synchronization and deployment script.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "generate_backups.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_logbase_backup.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina.service",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "commit_message.txt",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "AGENTS.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Agent Operating Law (permissions and scopes for Jules, agy, etc).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "SECURITY.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_export.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "idleloop.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "healthcheck.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Pre-deployment health and dependency verification suite.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "Makefile",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_aider.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina-dashboard.service",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "guardian",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "README.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Human-facing project overview, agent model, and installation guide.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_context.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "AI session grounding profile & architecture context. Attach to new threads.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_docbase_backup.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "nina_docs_export.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "ARCHITECTURE.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "High-level system design and logic flow map.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "templates/dashboard.html",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "dashboard/ninaui.html",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "dashboard/nina-guardian.html",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "dashboard/puter_architect.html",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/runner.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/cron_checks.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/import_checks.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/syntax_checks.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/env_checks.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/package_checks.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/__init__.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/router_checks.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/state_checks.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/system_checks.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "checks/security_checks.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "upgrades/guardian_baseline.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "upgrades/.guardian_handoff.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "upgrades/backups/archive/.gitkeep",
      "category": "backup",
      "role": "archive",
      "governed": true,
      "canonical": true,
      "lifecycle": "archived",
      "retention_policy": "keep_latest_n: 10",
      "origin": "script:backup",
      "owner": "system",
      "duplicate_cluster_id": null,
      "series_id": "archive",
      "series_type": "backup",
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "backup",
        "archive",
        "archived"
      ]
    },
    {
      "path": "git-hooks/pre-push",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/memory.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/nina_v12_blueprint.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [
        "read_only_for_agents"
      ],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/ninaflash.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/guardian.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/nina_proxy_usage.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/observability.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/router.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/roadmap/nina_phase1_roadmap.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/agent-memory/workflow.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/agent-memory/runbooks.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/agent-memory/current-state.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/agent-memory/architecture.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_token_surgical.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_architecture_spec_v1.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_architecture_diagram.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_gate_prompt.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_index.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "script:update_index",
      "owner": "system",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [
        "read_only_for_agents"
      ],
      "summary": "Canonical repository index (this document).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_gemini_ignore.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_error_register.md",
      "category": "doc",
      "role": "system_of_record",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [
        "append_only"
      ],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "system_of_record",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_repo_hygiene_dashboard.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Auto-generated repository hygiene dashboard.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_status_pulse.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_session_mgmt.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_task_tracker.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_doc_compression.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_index.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "script:update_index",
      "owner": "system",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [
        "read_only_for_agents"
      ],
      "summary": "Machine-readable repository index companion.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_surgical_intel.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_hygiene_fix.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/ninaflash_task_tracker.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_state.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_master_backup_2026-06-10.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_governance_dashboard.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Auto-generated operational governance dashboard.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_log_summary.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_backlog_inc.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_archive_ops.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/claude_feed.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_backlog.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/jules_spec_throughput_maximizer.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/space/nina_exporter_contract.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "docs/logs/nina_update_log.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash).",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/memory.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/logger.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/router.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [
        "high_risk_do_not_edit_directly"
      ],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/memory_manager.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/task_store.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/observability.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/verifier.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/__init__.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/config.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/agent.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/nina.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/hotreload.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/agent_loop.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "core/capabilities.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "System orchestrator, router, memory, and config modules.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "ninagate/main.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "ninagate/providers.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "ninagate/ninagate.service",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "ninagate/README.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/tasks.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0001",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/circuit_state.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": false,
      "lifecycle": "deprecated",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0001",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/modeldiscovery.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": false,
      "lifecycle": "deprecated",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0002",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/gpuconfig.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0002",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/model_cache.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/capabilities.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/discoveredproviders.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/plans/templates/expense_log.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/plans/templates/reminder_set.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/plans/templates/daily_brief.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/plans/templates/market_check.json",
      "category": "config",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "config",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/plans/templates/README.md",
      "category": "doc",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "doc",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "data/memory/facts.json",
      "category": "config",
      "role": "system_of_record",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [
        "read_only_for_agents"
      ],
      "summary": "Immutable personal identity anchor (Owner facts).",
      "tags": [
        "config",
        "system_of_record",
        "active"
      ]
    },
    {
      "path": "interfaces/cli_interface.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Telegram and REST API communication layers.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "interfaces/api.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": false,
      "lifecycle": "deprecated",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0003",
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Telegram and REST API communication layers.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "interfaces/__init__.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": false,
      "lifecycle": "deprecated",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0003",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Telegram and REST API communication layers.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "interfaces/middleware.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Telegram and REST API communication layers.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "interfaces/telegram_interface.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [
        "high_risk_do_not_edit_directly"
      ],
      "summary": "Telegram and REST API communication layers.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "exports/nina_latest.md",
      "category": "export",
      "role": "generated",
      "governed": true,
      "canonical": true,
      "lifecycle": "generated",
      "retention_policy": "ephemeral",
      "origin": "script:sync",
      "owner": "system",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "export",
        "generated",
        "generated"
      ]
    },
    {
      "path": "exports/nina_problem_log_archive.md",
      "category": "export",
      "role": "generated",
      "governed": true,
      "canonical": true,
      "lifecycle": "generated",
      "retention_policy": "ephemeral",
      "origin": "script:sync",
      "owner": "system",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "export",
        "generated",
        "generated"
      ]
    },
    {
      "path": "tools/web.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/nina_dashboard.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/update_index.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Utility to regenerate the repository index.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/cleanup_by_index.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Safe dry-run cleanup planner based on retention policies.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/market.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/validate_index.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Automated validator for repository index consistency.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/finance.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/query_index.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Agent API to query file governance status.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/office_mail.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/providerhunter.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/shell.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [
        "high_risk_do_not_edit_directly"
      ],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/model_discovery.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/ninaflash.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/browser.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [
        "high_risk_do_not_edit_directly"
      ],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/retry.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/jules_api.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/__init__.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/append_log.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/create_pr.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/audit_repo_hygiene.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Deep repository audit tool for Git vs FS reconciliation.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/nina_sync.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/generate_dashboard.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Generates the operational governance dashboard.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/files.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/append_lock.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/nina_proxy.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/prune_duplicates.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Active redundancy pruner for incident and backup duplicates.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/upgradepipeline.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/compact_exporter.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/system.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tools/search.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Capability kernel and domain-specific action modules (ninaflash nucleus).",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "logs/nina_sync.log",
      "category": "log",
      "role": "derived",
      "governed": true,
      "canonical": false,
      "lifecycle": "deprecated",
      "retention_policy": "rotate",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0003",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "log",
        "derived",
        "active"
      ]
    },
    {
      "path": "logs/agent_actions.log",
      "category": "log",
      "role": "derived",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "rotate",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "log",
        "derived",
        "active"
      ]
    },
    {
      "path": "tests/test_finance.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_tools_smoke.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_shell.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_tools_hardening.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_finance_market.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_task_store.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_nina_proxy.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_memory.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_cron_registry.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/conftest.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_idleloop.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_nina_sync.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_model_discovery.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/__init__.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": false,
      "lifecycle": "deprecated",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0003",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_smoke.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_guardian.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_router.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_integration.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_memory_kb.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_agent_loop.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_verifier.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_append_utils.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_telegram_middleware.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "tests/test_browser.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "bin/ninagate",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "bin/install_governance.sh",
      "category": "script",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Bootstrap installer for NINA repository governance and Git hooks.",
      "tags": [
        "script",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "bin/nina",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "bin/nf",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0004",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "bin/ninaflash",
      "category": "other",
      "role": "source_of_truth",
      "governed": true,
      "canonical": false,
      "lifecycle": "deprecated",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0004",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": false,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "other",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "crons/manager.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "crons/runner.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "crons/__init__.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": false,
      "lifecycle": "deprecated",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0003",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "crons/registry.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "crons/backup_jobs.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": null,
      "series_id": null,
      "series_type": null,
      "requires_tests": true,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "agent/__init__.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": false,
      "lifecycle": "deprecated",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0003",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    },
    {
      "path": "agent/context.py",
      "category": "code",
      "role": "source_of_truth",
      "governed": true,
      "canonical": true,
      "lifecycle": "active",
      "retention_policy": "keep",
      "origin": "manual",
      "owner": "engineering",
      "duplicate_cluster_id": "dup-0003",
      "series_id": null,
      "series_type": null,
      "requires_tests": false,
      "doc_required": true,
      "guardrails": [],
      "summary": "Governed artifact.",
      "tags": [
        "code",
        "source_of_truth",
        "active"
      ]
    }
  ],
  "duplicate_clusters": [
    {
      "cluster_id": "dup-0001",
      "canonical_path": "data/tasks.json",
      "members": [
        "data/tasks.json",
        "data/circuit_state.json"
      ],
      "reason": "exact_md5_duplicate"
    },
    {
      "cluster_id": "dup-0002",
      "canonical_path": "data/gpuconfig.json",
      "members": [
        "data/modeldiscovery.json",
        "data/gpuconfig.json"
      ],
      "reason": "exact_md5_duplicate"
    },
    {
      "cluster_id": "dup-0003",
      "canonical_path": "agent/context.py",
      "members": [
        "interfaces/api.py",
        "interfaces/__init__.py",
        "logs/nina_sync.log",
        "tests/__init__.py",
        "crons/__init__.py",
        "agent/__init__.py",
        "agent/context.py"
      ],
      "reason": "exact_md5_duplicate"
    },
    {
      "cluster_id": "dup-0004",
      "canonical_path": "bin/nf",
      "members": [
        "bin/nf",
        "bin/ninaflash"
      ],
      "reason": "exact_md5_duplicate"
    }
  ]
}```

### docs/space/nina_index.md
Last modified: 2026-06-11 12:41:02
Size: 7468 bytes
```markdown
# NINA Repository Index
_Single Source of Truth for File Inventory & Governance_

## 1. Overview & Scope
This index tracks all governed artifacts in the NINA repository.
- **Governed:** true. Includes docs, tools, scripts, configs, exports, and persistent logs.
- **Unmanaged:** Excludes `__pycache__`, `.venv`, `.git`, transient temp files.

## 2. File Inventory
| Path | Role | Lifecycle | Retention | Summary | Canonical |
|------|------|-----------|-----------|---------|-----------|
| `.coverage` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.env.example` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.gitignore` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.ninaignore` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `AGENTS.md` | source_of_truth | active | keep | Agent Operating Law (permissions and scopes for Jules, agy, etc). | ✅ YES |
| `ARCHITECTURE.md` | source_of_truth | active | keep | High-level system design and logic flow map. | ✅ YES |
| `CHANGELOG.md` | source_of_truth | active | keep | User-friendly summary of major version releases. | ✅ YES |
| `CONTRIBUTING.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `LICENSE` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `Makefile` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `README.md` | source_of_truth | active | keep | Human-facing project overview, agent model, and installation guide. | ✅ YES |
| `SECURITY.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `WORKFLOW.md` | source_of_truth | active | keep | Repository rules of engagement and development lifecycle. | ✅ YES |
| `commit_message.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `generate_backups.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `guardian` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `guardian_engine.py` | source_of_truth | active | keep | Forensic AST scanner and baseline drift analyzer (73KB). | ✅ YES |
| `healthcheck.py` | source_of_truth | active | keep | Pre-deployment health and dependency verification suite. | ✅ YES |
| `idleloop.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `jules_lock.txt` | system_of_record | active | keep | Governed artifact. | ✅ YES |
| `main.py` | source_of_truth | active | keep | Primary entry point for the NINA systemd service. | ✅ YES |
| `nina-dashboard.service` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina.service` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_aider.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_audit.sh` | source_of_truth | active | keep | Permanent wrapper script for the repository hygiene audit. | ✅ YES |
| `nina_cleanup.sh` | source_of_truth | active | keep | Permanent wrapper script for safe redundancy cleanup execution. | ✅ YES |
| `nina_codebase_backup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_context.md` | source_of_truth | active | keep | AI session grounding profile & architecture context. Attach to new threads. | ✅ YES |
| `nina_docbase_backup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_docs_export.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_export.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_logbase_backup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_sync.sh` | source_of_truth | active | keep | Post-session synchronization and deployment script. | ✅ YES |
| `nina_update_log.md` | system_of_record | active | keep | Canonical live activity log (Entry 001-167). Newest entries at top. | ✅ YES |
| `ninagate_load_test.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `pr_desc.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `pytest.ini` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `requirements.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools.log` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `agent/` | subsystem | active | keep | Subsystem directory containing agent logic/docs. | ✅ YES |
| `bin/` | subsystem | active | keep | Subsystem directory containing bin logic/docs. | ✅ YES |
| `checks/` | subsystem | active | keep | Subsystem directory containing checks logic/docs. | ✅ YES |
| `core/` | subsystem | active | keep | System orchestrator, router, memory, and config modules. | ✅ YES |
| `crons/` | subsystem | active | keep | Subsystem directory containing crons logic/docs. | ✅ YES |
| `dashboard/` | subsystem | active | keep | Subsystem directory containing dashboard logic/docs. | ✅ YES |
| `data/` | subsystem | active | keep | Subsystem directory containing data logic/docs. | ✅ YES |
| `docs/` | subsystem | active | keep | Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash). | ✅ YES |
| `exports/` | subsystem | active | keep | Subsystem directory containing exports logic/docs. | ✅ YES |
| `git-hooks/` | subsystem | active | keep | Subsystem directory containing git-hooks logic/docs. | ✅ YES |
| `interfaces/` | subsystem | active | keep | Telegram and REST API communication layers. | ✅ YES |
| `logs/` | subsystem | active | keep | Subsystem directory containing logs logic/docs. | ✅ YES |
| `ninagate/` | subsystem | active | keep | Subsystem directory containing ninagate logic/docs. | ✅ YES |
| `templates/` | subsystem | active | keep | Subsystem directory containing templates logic/docs. | ✅ YES |
| `tests/` | subsystem | active | keep | Subsystem directory containing tests logic/docs. | ✅ YES |
| `tools/` | subsystem | active | keep | Capability kernel and domain-specific action modules (ninaflash nucleus). | ✅ YES |
| `upgrades/` | subsystem | active | keep | Subsystem directory containing upgrades logic/docs. | ✅ YES |

## 3. Redundancy & Conflicts
The following clusters contain identical content. Consolidate to the canonical source where possible.

- **Cluster `dup-0001`**: Canonical is `data/tasks.json`. Members: `data/tasks.json`, `data/circuit_state.json`
- **Cluster `dup-0002`**: Canonical is `data/gpuconfig.json`. Members: `data/modeldiscovery.json`, `data/gpuconfig.json`
- **Cluster `dup-0003`**: Canonical is `agent/context.py`. Members: `interfaces/api.py`, `interfaces/__init__.py`, `logs/nina_sync.log`, `tests/__init__.py`, `crons/__init__.py`, `agent/__init__.py`, `agent/context.py`
- **Cluster `dup-0004`**: Canonical is `bin/nf`. Members: `bin/nf`, `bin/ninaflash`

## 4. Governance Rules & Index-First Workflow
1. **Check the Index:** `python3 tools/query_index.py --path <file>`
2. **Duplicate Clusters:** When writing to a path that belongs to a duplicate cluster, you MUST only write to the `canonical_path`.
3. **Index Modification:** If creating/moving a governed file:
   - Run `python3 tools/update_index.py`.
   - Run `python3 tools/validate_index.py`.
4. **Validation:** No PR touching governed paths is "Done" unless `validate_index.py` passes.
5. **Contract:** The index is the single enforceable contract for doc/log/code inventory.

---
_Generated by NINA Indexer on 2026-06-10_
```

### docs/space/nina_master_backup_2026-06-10.md
Last modified: 2026-06-11 03:15:37
Size: 20229 bytes
```markdown
# NINA Master Reference Backup — 2026-06-07

> **Snapshot base:** `nina_latest.md` generated `2026-06-07 13:19:17`
> **Branch:** `main` | **Python:** 3.14.4 | **OS:** Ubuntu 26.04 LTS
> **Owner:** M. Baizid Alam, AGM, BASIC Bank Limited, Dhaka, Bangladesh
> **Deployment:** ASUS VivoBook X530FN | Service: `systemd nina.service`
> **Repo:** `github.com/aibony/nina`

---

## 1. Session Health Check (Current State)

| Metric | Value |
|---|---|
| **BLOCKER** | 0 |
| **WARN** | 0 |
| **DEBT** | 0 |
| **FEATURE_PENDING** | 11 |
| **Guardian Status** | PASS (clean) |
| **Open PRs** | 0 |
| **`juleslock.txt`** | CLEARED |
| **`nina.service`** | active |
| **ninaflash Claude quota** | SPENT (resets ~127h from session) |
| **Jules daily quota** | 100 tasks/day (rolling 24h) |

### Today's Merged PRs (2026-06-07)

| PR | Task ID | What Was Added | Key Files |
|---|---|---|---|
| 13 | R-82 | `Makefile` dev helpers | `Makefile` |
| 14 | D-24 | Provider architecture docs | `docs/space/nina_context.md` |
| 15 | R-81 | Smoke tests for tools | `tests/test_tools_smoke.py`, `pytest.ini` |
| 16 | F-08 | KB core primitives | `core/memory.py` |
| 17 | R-80 | Structured `extra=` logging (12 files) | tools/crons |
| 18 | R-79 | `IdleProposalLoop` IMPACT briefs | `idleloop.py` |
| 19 | F-07 | Email triage refactor + compat wrapper | `tools/officemail.py` |
| 20 | F-06 | Proactive reminder engine | `core/nina.py`, `data/reminders.json` |
| 21 | F-05 | DSE/CSE market monitor | `tools/market.py`, `crons/manager.py` |
| 22 | F-04 | Expenditure tracker + tests | `tools/finance.py` |
| 23 | Bolt | `is_bangla` compiled regex (10× faster) | `core/agent.py` |
| 24 | Sentinel | `shell=True` → `shlex.split` / `shell=False` | `guardian_engine.py` |

---

## 2. Three-Tool Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  THE PARALLEL LOOP                         │
│                                                            │
│  1. Perplexity ─── diagnoses + writes precise spec        │
│         │                                                  │
│         ├──► Jules ─── async cloud VM ──► PR              │
│         │      (fire-and-forget, NO interaction)           │
│         │                                                  │
│         └──► ninaflash ─── local executor ──► merge + deploy    │
│                (sync, single-file hotfixes in parallel)    │
│                                                            │
│  5. ninaflash reviews Jules PR diff                             │
│  6. ninaflash: pycompile + pyflakes → merge → .ninasync.sh      │
│  7. Perplexity reviews: attach fresh nina_latest.md        │
└────────────────────────────────────────────────────────────┘
```

### Tool Routing Table

| Tool | Model | Role | Execution | Reset |
|---|---|---|---|---|
| Perplexity Enterprise Pro | Claude Sonnet 4.6 Thinking | ARCHITECT / OVERWATCH | Active throughout | — |
| Google Jules | Gemini 3.1 Pro (built-in) | ASYNC CLOUD CODER | Fire-and-forget → PR | 100 tasks/24h |
| Antigravity CLI (`ninaflash`) | Gemini 3.5 Flash Medium (default) | LOCAL MUSCLE | Sync executor, merge, deploy | ~5h rolling |

### ninaflash Model Tiers

| Model | Budget | Use When |
|---|---|---|
| Gemini 3.5 Flash Medium | ~5h rolling | Default — always try first |
| Gemini 3.5 Flash High | ~5h rolling | Moderate complexity |
| Gemini 3.1 Pro High | ~5h rolling | High complexity local tasks |
| Claude Sonnet 4.6 Thinking | Weekly (~7 days) | Reserve — burns budget fast |
| Claude Opus 4.6 Thinking | Weekly (~7 days) | Last resort — same pool as Sonnet |

### ninaflash Mandatory Rules

- **Always start every ninaflash prompt with:** `"Use the permanent JSON approval setting — approve all steps without prompting for this task."`
- Never generate bash scripts or code — write plain-English prompts only
- Never write log entries, commits, or file edits directly — always instruct ninaflash
- Sequential only — one task at a time, one file at a time
- ninaflash performs **ALL** Jules PR merges — never auto-merge via GitHub UI
- Before merge: `python3 -m pycompile` + `pyflakes` on changed files + check `juleslock.txt`
- After merge: `.ninasync.sh` — no exceptions

### Jules Mandatory Rules

- `jules remote new --repo aibony/nina --task start --session "full task spec"`
- Fire-and-forget: submit and walk away — check GitHub for PR
- Jules reads `AGENTS.md` automatically — keep it updated
- Jules does **NOT** merge its own PRs — ninaflash always does the merge
- Daily limit: 100 tasks (Pro)
- **Do NOT pause for confirmation** at any point in the Jules spec

---

## 3. Key Paths

| Item | Path |
|---|---|
| NINA repo | `~/nina` |
| venv activate | `source ~/nina/venv/bin/activate` |
| ninaflash binary | `~/.local/bin/ninaflash` |
| Service restart | `sudo systemctl restart nina.service` |
| Guardian run | `cd ~/nina && bash guardian.sh` |
| Post-session sync | `cd ~/nina && ./nina_sync.sh` |
| Export snapshot | `cd ~/nina && ./nina_docs_export.sh` |
| Space upload dir | `~/Downloads/nina_space_upload/` |
| Error register | `~/nina/docs/space/nina_error_register.md` |
| Canonical docs | `~/nina/docs/space/` only |
| Update log | `~/nina/nina_update_log.md` |
| Jules lock | `~/nina/juleslock.txt` |
| Workflow doc | `~/nina/WORKFLOW.md` |
| Exporter contract | `~/nina/docs/space/nina_exporter_contract.md` |

---

## 4. High-Risk Files (Strict Rules)

| File | Risk | Default Route |
|---|---|---|
| `interfaces/telegram_interface.py` | Security gate, user-facing | ninaflash local only |
| `.env` | All secrets | NEVER cloud, NEVER commit |
| `core/router.py` | HybridRouter V4 | ninaflash local only |
| `main.py` | Entry point, PID lock | ninaflash local only |
| `guardian_engine.py` | Forensic engine | ninaflash local only |
| `tools/shell.py` | Allowlist-gated shell | ninaflash local only |

**Rule:** Jules can only touch these files if explicitly authorized in the task spec and they are **not** locked in `juleslock.txt`.

---

## 5. Core Architecture

### Module Map

| Module | File | Role |
|---|---|---|
| Orchestrator | `core/nina.py` | `NinaOS` — top-level coordinator |
| Router | `core/router.py` | `HybridRouter V4` — provider selection, circuit breaker |
| Agent | `core/agent.py` | `AgentLoop` — THINK→PLAN→ACT→OBSERVE→ADAPT (Stage 5) |
| Memory | `core/memory.py` | `MemorySystem` — conversation + facts + KB (ChromaDB) |
| Config | `core/config.py` | `NinaConfig` — Pydantic model, `.env` loading |
| Capabilities | `core/capabilities.py` | `CapabilityRegistry` |
| Hot Reload | `core/hotreload.py` | `ConfigHotReload` — watches `.env` every 60s |
| Telegram | `interfaces/telegram_interface.py` | Security gate, command handler, flood protection |
| Guardian | `guardian_engine.py` | Forensic health checks |
| Shell | `tools/shell.py` | Allowlist-gated shell execution |
| Finance | `tools/finance.py` | Expenditure tracker (F-04) |
| Market | `tools/market.py` | DSE/CSE monitor (F-05) |
| Officemail | `tools/officemail.py` | EWS email triage (F-07) |
| Upgrade Pipeline | `tools/upgrade_pipeline.py` | Pattern scan, sandbox, approve/reject |
| Crons | `crons/manager.py` | `TaskScheduler` — APScheduler jobs |
| Idle Loop | `idleloop.py` | `IdleUpgradeLoop` — IMPACT briefs |
| Entry Point | `main.py` | PID lock, asyncio bootstrap |

### Provider Routing Priority

```
Free first → Groq → Gemini → Cerebras → DeepSeek → Mistral →
Together → Cohere → Fireworks → Perplexity → SambaNova →
OpenRouter → xAI → OpenAI (paid — last resort)
```

**Tier 1 (Keyless):** POLLINATIONS, CHUTES, HFPUBLIC
**Tier 2 (Keyed):** CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini), ONEBRAIN
**Tier 3:** OPENROUTER
**Local:** LOCALFAST (qwen2.5-1.5b), LOCALHEAVY (qwen2.5-7b)

### Routing Score Algorithm

```
score = (success_rate × 0.4) + ((1 - latency/5000) × 0.4) + (not_near_limit × 0.2)
```

**Circuit Breaker:** CLOSED → OPEN (3 failures/5min) → HALF-OPEN (probe after 1800s)

---

## 6. Scheduled Jobs (crons/manager.py)

| Job ID | Trigger | Function |
|---|---|---|
| `morning_report` | Daily 09:00 Asia/Dhaka | Morning briefing |
| `heartbeat` | Every 1h | Service health ping |
| `cache_purge` | Daily 03:05 Asia/Dhaka | Cache cleanup |
| `cost_report` | Daily 23:00 Asia/Dhaka | Provider cost summary |
| `rate_limit_reset` | Daily 00:01 UTC | Provider daily counters reset |
| `idle_summary` | Every 30min | Idle session summary |
| `log_rotation` | Daily 04:00 Asia/Dhaka | Log cleanup |
| `provider_health` | Every 6h | Provider availability check |
| `provider_hunter` | Daily 02:00 Asia/Dhaka | New provider scan |
| `thermal_health` | Every 5min | CPU/GPU temperature guard |
| `memory_backup` | Daily 02:30 Asia/Dhaka | Memory system backup |
| `py_backup` | Daily 03:00 Asia/Dhaka | Python code backup |
| `reminder_check` | Every 15min | Proactive reminder engine (F-06) |
| `market_monitor` | 10:30–14:30 Asia/Dhaka | DSE/CSE alerts (F-05) |
| `expire_pending` | Every 15min | Upgrade pipeline expiry |

---

## 7. Configuration Reference (NinaConfig)

### Thermal Thresholds

| Key | Default | Description |
|---|---|---|
| `thermal_warn_cpu` | 80 | CPU warn % |
| `thermal_warn_gpu` | 80 | GPU warn % |
| `thermal_guard_cpu` | 90 | CPU throttle % |
| `thermal_guard_gpu` | 85 | GPU throttle % |
| `thermal_critical_cpu` | 95 | CPU critical % |
| `thermal_critical_gpu` | 90 | GPU critical % |

### Resource Limits

| Key | Default | Description |
|---|---|---|
| `max_ram_gb` | 12.0 | Max RAM before guard |
| `ram_guard_gb` | 10.5 | RAM guard threshold |
| `disk_guard_pct` | 90.0 | Disk usage guard % |

### Agent Behaviour

| Key | Default | Description |
|---|---|---|
| `idle_threshold_min` | 15 | Minutes idle before idle loop |
| `idle_report_min` | 30 | Minutes between idle reports |
| `idle_auto_approve` | False | Auto-approve idle upgrades |
| `session_max_turns` | 20 | Max agent turns per session |
| `agent_timeouts` | 300 | Agent timeout (seconds) |
| `flood_windows` | 30 | Flood protection window (seconds) |
| `flood_max_messages` | 10 | Max messages in flood window |
| `api_rate_limit_rpm` | 60 | API rate limit (req/min) |

### Hot-Reloadable Fields (no restart needed)

`EWS_MAX_EMAILS`, `EWS_KEYWORDS`, `IDLE_THRESHOLD_MIN`, `IDLE_REPORT_MIN`, `IDLE_AUTO_APPROVE`, `FLOOD_WINDOWS`, `FLOOD_MAX_MESSAGES`, `SESSION_MAX_TURNS`, `AGENT_TIMEOUTS`, `API_RATE_LIMIT_RPM`, `DEADMAN_PING_URL`, `LOG_LEVEL`, all `THERMAL_*` thresholds

---

## 8. Security Architecture

### Shell Allowlist (tools/shell.py)

```python
ALLOWED_BASES = {
    "df", "ls", "pwd", "whoami", "free", "ps", "uptime",
    "head", "tail", "grep", "find", "echo", "date", "ping",
    "curl", "wget", "python", "python3", "pip", "pip3",
    "git", "systemctl", "journalctl", "ollama", "nvidia-smi"
}
ALLOWED_SYSTEMCTL_SUBS = {"status", "start", "stop", "restart", "enable", "disable", "is-active"}
ALLOWED_OLLAMA_SUBS    = {"list", "show", "pull", "run", "stop", "ps", "serve"}
```

**Injection guard:** Blocks `;`, `|`, `&&`, `||`, `` ` ``, `$()`, `>`, `<` shell operators.

### guardian_engine.py — Security Fix Applied (PR 24 / Sentinel)

```python
# BEFORE (vulnerable — shell=True)
def run_cmd(cmd, timeout=30):
    r = subprocess.run(cmd, shell=True, ...)

# AFTER (secure — shell=False default)
def run_cmd(cmd, timeout=30, use_shell=False):
    args = shlex.split(cmd) if not use_shell else cmd
    r = subprocess.run(args, shell=use_shell, ...)
    # use_shell=True only for the healthcheck runner (uses cd && chaining)
```

### SSRF Guard (tools/browser.py)

Validates all URLs against `ipaddress` module — blocks private IP ranges, localhost, link-local addresses before any HTTP request.

### Telegram Security Gate

- Single `AUTHORIZED_USER_ID` check on every message
- Flood protection: 10 messages / 30-second window
- Secret masking: `mask_secrets()` helper on all outbound text
- `ParseMode` safe defaults to prevent parse errors leaking internals

---

## 9. Open Action Board

### Active FEATURE_PENDING Items

| ID | Severity | Component | Issue | File |
|---|---|---|---|---|
| F-01 | OPEN/PENDING | `core/agent.py` | Self-check pass for complex tasks | `core/agent.py` |
| F-04 | OPEN/PENDING | `tools/finance.py` | Expenditure tracker (code merged — register not updated) | `tools/finance.py` |
| F-05 | OPEN/PENDING | `tools/market.py` | DSE/CSE market monitor (dummy prices — real API needed) | `tools/market.py` |
| F-06 | OPEN/PENDING | `core/nina.py` | Proactive reminder engine (cron wired — data schema TBD) | `core/nina.py` |
| F-07 | OPEN/PENDING | `tools/officemail.py` | Email triage (EWS blocked — O-02 open) | `tools/officemail.py` |
| F-08 | OPEN/PENDING | `core/memory.py` | KB remember/recall (ChromaDB wired — Telegram cmd TBD) | `core/memory.py` |
| R-77 | OPEN/PENDING | `core/router.py` | `parallel_route` RAM guard crash | `core/router.py` |
| R-78 | OPEN/PENDING | `core/agent.py` | Tool grammar fragility — minimum viable guard | `core/agent.py` |
| config.missing_env.telegram_chat_id | OPEN | `core/config` | `TELEGRAM_CHAT_ID` missing from `.env` (non-blocking) | `.env` |
| feature.ews_blocked | OPEN | `tools/officemail` | EWS email feature blocked — O-02 | `tools/officemail.py` |
| feature.playwright_blocked | OPEN | `tools/browser` | Playwright browser tool blocked — O-01 | `tools/browser.py` |

### Priority Order (Next Tasks)

```
1. B-3  F-03  Response tone calibration  →  core/nina.py  SYSTEM_PROMPT_TEMPLATE
2. C-1  F-04  Wire finance tool to Telegram command + close register entry
3. C-2  F-05  Replace dummy prices with real DSE/CSE API (scraper or public feed)
4. C-3  F-06  Define data/reminders.json schema + test reminder_check cron
5. C-4  F-07  Unblock EWS or add mock fallback for testing
6. C-5  F-08  Add /remember and /recall Telegram commands
7. A-1  R-77  Fix parallel_route RAM guard crash
8. A-3  R-78  Tool grammar fragility guard
```

---

## 10. Phase Roadmap

### Stage A — Stability (COMPLETE)

All historical blockers, router attribute errors, startup errors, hot-reload regressions, SSRF guard, Telegram handler issues, logging duplication — all FIXED and confirmed clean by guardian.

### Stage B — Make NINA Smarter (PARTIAL)

- ✅ B-1 (F-01) Self-check pass in `core/agent.py`
- ✅ B-2 (F-02) Personal context injection in `core/memory.py` + `data/memory_facts.json`
- ⏳ **B-3 (F-03) Response tone calibration** — NEXT UP

### Stage C — Banking & Personal Tools (IN PROGRESS)

- ⏳ C-1 (F-04) Expenditure tracker — code merged, needs Telegram wiring + register close
- ⏳ C-2 (F-05) Market monitor — code merged, dummy prices → real API needed
- ⏳ C-3 (F-06) Reminder engine — cron wired, schema + testing needed
- ⏳ C-4 (F-07) Email triage — blocked on EWS access
- ⏳ C-5 (F-08) Knowledge base — ChromaDB wired, Telegram commands needed

---

## 11. ninasync.sh — What It Does (v5)

```
Step 0/8  Health check — naming convention scan, service status
Step 1/8  tgnotify — Telegram ping on sync start
Step 2/8  Guardian run
Step 3/8  Git status check
Step 4/8  Update log entry append (Python, not bash echo)
Step 5/8  Staging: git add docs/space/ + SPACEFILES
Step 6/8  Commit + push (skips if Jules PRs are open — D-12 guard)
Step 7/8  Doc coverage scan — all .md/.txt/.json vs SPACEFILES
Step 8/8  Compact exporter → ~/Downloads/nina_space_upload/nina_latest.md
```

### SPACEFILES Array (files exported to Perplexity Space)

```bash
SPACEFILES=(
  "AGENTS.md"
  "WORKFLOW.md"
  "docs/space/nina_error_register.md"
  "docs/space/nina_exporter_contract.md"
  "docs/space/nina_state.md"
)
```

---

## 12. Session Start / Close Checklists

### Session Start (Before ANY Work)

1. `cd nina && ./nina_sync.sh` — get fresh snapshot
2. Attach `exports/nina_latest.md` to Perplexity thread
3. Attach specific source files to be discussed
4. State task type: `bug | feature | doc | security | review`
5. `cat nina/juleslock.txt` — confirm no target files are locked

### Session Close (Mandatory Every Time)

1. `cd nina && ./nina_sync.sh` → produces `nina_code_backup_TIMESTAMP.md`
2. `cd nina && ./nina_docs_export.sh` → produces `nina_docs_backup_TIMESTAMP.md`
3. Upload `nina_docs_backup_*.md` to Perplexity Space manually
4. Verify `juleslock.txt` is cleared
5. Verify 0 open PRs: `gh pr list --state open`

---

## 13. Parallel Workflow — Branch & Worktree Model

### Branch Lanes

| Branch | Purpose |
|---|---|
| `main` | Production truth — merge, sync only |
| `ninaflash/task-id-slug` | Local docs, shell, single-file hotfixes |
| `jules/task-id-slug` | Multi-file features, async PR builds |
| `review/id` | Isolated test/review/merge prep |

### Territory Rules

| Tool | Default Territory | Forbidden |
|---|---|---|
| ninaflash | `docs/space/*.md`, `AGENTS.md`, `*.sh`, single-file hotfixes | Files claimed by Jules |
| Jules | `core/*.py`, `tools/*.py`, `interfaces/*.py`, `tests/*.py` | `.env`, secrets, lock-sensitive files |
| Both (sequential) | `requirements.txt`, `data/*.json` | Parallel edits |

### Worktree Pattern

```
~/nina/                     ← main (production)
~/nina.worktrees/ninaflash-task-id/
~/nina.worktrees/jules-task-id/
```

All worktrees share: `~/nina/venv/bin/activate` — never create separate venvs.
Lock truth always at: `~/nina/juleslock.txt` — never local worktree copy.

### Stop Conditions

- Either tool needs a file already claimed by the other → **stop, re-plan**
- Merge conflict risk appears → **pause parallelism, integrate first**
- Never bypass review with direct overlapping edits to main

---

## 14. compact_exporter.py — Validation Gate

The exporter validates `nina_latest.md` against 7 required strings before accepting the output:

| String | Section It Validates |
|---|---|
| `SESSION START CHECKLIST` | Pre-session checklist present |
| `ARCHITECT / OVERWATCH` | Tool routing table present |
| `ASYNC CLOUD CODER` | Jules role present |
| `LOCAL MUSCLE` | ninaflash role present |
| `ninaflash as Merge Executor` | Merge executor rule present |
| `The Full Parallel Loop` | 7-step loop present |
| `FEATURE_PENDING` | Action board present |

If any string is missing, the export fails with an explicit error — prevents silent regressions in the context snapshot.

---

## 15. Failure Modes to Avoid

| Anti-Pattern | Why It Breaks |
|---|---|
| Blind editing — no source file attached | Perplexity cannot see actual code; hallucination risk |
| Routing urgent fixes through Jules PR pipeline | Jules is async; runtime fixes need ninaflash (sync) |
| Using ninaflash for broad multi-file refactors | ninaflash is sequential — scoped single-file only |
| Starting work without checking `juleslock.txt` | Lock race condition — two tools editing same file |
| Stacking unrelated changes in one commit | Makes rollback impossible |
| Treating `nina_latest.md` as repo recovery | It is a context snapshot, NOT a git backup |
| Auto-merging Jules PRs via GitHub UI | Skips compile check and pyflakes gate |
| Using heredoc/bash echo for log entries | Corrupts log format — Python append only |

---

## 16. Appendix — Known Blocked Features

| Feature | Issue ID | Blocker | Workaround |
|---|---|---|---|
| EWS Email triage | O-02 | NTLM auth / network access | `tools/officemail.py` has compat wrapper ready |
| Playwright browser | O-01 | Playwright not installed | `tools/browser.py` fallback to `httpx` |
| `TELEGRAM_CHAT_ID` | config.missing | Not in `.env` | Non-blocking — bot still works via `AUTHORIZED_USER_ID` |

---

*Last validated: 2026-06-07 13:19 +06 | Entry 051 in nina_update_log.md | All 12 PRs merged, 0 open*
```

### docs/space/nina_megatask_index.md
Last modified: 2026-06-11 18:54:14
Size: 2125 bytes
```markdown
# NINA Mega-Task Index
> Compact reference of NINA's strategic evolution. Full specs reside in individual files.

| v# | Codename | Status | Summary |
|:---|:---|:---|:---|
| 1.0 | Foundation | ✅ DONE | Core autonomous agent loop and tool routing. |
| 2.0 | Throughput Maximizer | ✅ DONE | High-velocity autonomous control plane; 90% cloud token reduction. |
| 2.1 | Token-Surgical | ✅ DONE | Semantic context selection and local-first RAG. |
| 3.0 | Lightning Edition | ✅ DONE | Speculative prefetching and sub-second local interception. |
| 4.0 | NINA-Evolve | 🔄 ACTIVE | Autonomous self-optimization loop via performance metrics. |
| 5.0 | Lightning Sync | 🔄 ACTIVE | Incremental backup system reducing sync latency by 60%. |
| 6.0 | Ghost Context | ⏳ PENDING | Symbol maps and diffs to eliminate context tax. |
| 7.0 | Guardian Hardening | ⏳ PENDING | Zero-bug self-upgrades through local parallel testing. |
| 8.0 | Glass Box | ⏳ PENDING | Visual telemetry dashboard for real-time CPU/GPU pulse. |
| 9.0 | Speculative Pipeline | ⏳ PENDING | scout agents and overlapped local/cloud execution. |
| 10.0 | Sovereign NINA | ⏳ PENDING | Total autonomous self-maintenance and weekly reporting. |

---

### AG-M Series (Feature Specific)
| ID | Title | Status | Link |
|:---|:---|:---|:---|
| AG-M-02 | Token-Surgical | ✅ DONE | [Spec](jules_spec_token_surgical.md) |
| AG-M-03 | Surgical Code Intel | ✅ DONE | [Spec](jules_spec_surgical_intel.md) |
| AG-M-04 | DOC-COMP | ✅ DONE | [Spec](jules_spec_doc_compression.md) |
| AG-M-05 | NF-BACKLOG | ✅ DONE | [Spec](jules_spec_backlog_inc.md) |
| AG-M-06 | SEC-IGNORE | ✅ DONE | [Spec](jules_spec_gemini_ignore.md) |
| AG-M-07 | NF-CLEAN | ✅ DONE | [Spec](jules_spec_hygiene_fix.md) |
| AG-M-08 | NF-STATUS | ✅ DONE | [Spec](jules_spec_status_pulse.md) |
| AG-M-09 | NF-ARCHIVE | ✅ DONE | [Spec](jules_spec_archive_ops.md) |
| AG-M-10 | GATE-PROMPT | ✅ DONE | [Spec](jules_spec_gate_prompt.md) |
| AG-M-11 | NF-LOG | ✅ DONE | [Spec](jules_spec_log_summary.md) |
| AG-M-12 | NF-SESSIONS | ✅ DONE | [Spec](jules_spec_session_mgmt.md) |
```

### docs/space/nina_repo_hygiene_dashboard.md
Last modified: 2026-06-11 21:46:38
Size: 1255 bytes
```markdown
# NINA Repository Hygiene Dashboard
_Generated by `tools/audit_repo_hygiene.py` on 2026-06-11 21:46:38_

## 1. Hygiene Status
- **Git Tracked Files:** 216
- **Stray Locals (Untracked):** 1704
- **Missing Locally:** 0
- **Stale Governed Files (>6 months):** 0

## 2. Hard Violations (Blocks CI)
- ❌ Untracked file in governed directory: core/utils.py

## 3. Stale Governed Files (Action Required)
✅ None.

## 4. Stray Locals (Top 20)
- 🗑️ `.env`
- 🗑️ `.env.save`
- 🗑️ `.gemini/settings.json`
- 🗑️ `core/utils.py`
- 🗑️ `data/.guardian_hash`
- 🗑️ `data/circuit_state.json`
- 🗑️ `data/deploy.log`
- 🗑️ `data/healthcheck_registry.txt`
- 🗑️ `data/memory/chromadb/chroma.sqlite3`
- 🗑️ `data/nina.lock`
- 🗑️ `data/nina.pid`
- 🗑️ `data/proposals/2026-05-22_proposals.md`
- 🗑️ `data/proposals/2026-05-23_proposals.md`
- 🗑️ `data/proposals/2026-05-24_proposals.md`
- 🗑️ `data/proposals/2026-06-01_proposals.md`
- 🗑️ `data/proposals/2026-06-02_proposals.md`
- 🗑️ `data/proposals/2026-06-04_proposals.md`
- 🗑️ `data/proposals/2026-06-05_proposals.md`
- 🗑️ `data/proposals/2026-06-06_proposals.md`
- 🗑️ `data/proposals/2026-06-07_proposals.md`
- ... and 1684 more.
```

### docs/space/nina_state.md
Last modified: 2026-06-11 03:15:37
Size: 8217 bytes
```markdown
# NINA State — Single Source of Truth
_Last updated: 2026-06-08_

## Identity
- **Project Name:** NINA
- **Owner:** M. Baizid Alam — AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **Deployment Machine:** ASUS VivoBook X530FN — Ubuntu 26.04 LTS — Python 3.14.4 — User: aibony
- **Service Name:** systemd `nina.service` (Agent) + `nina-dashboard.service` (Architect)

NINA IDENTITY DIRECTIVE (canonical, applies everywhere):
NINA is a personal autonomous AI agent — NOT a chatbot. She acts, she does not describe. She completes tasks end-to-end using free-tier AI routing (Pollinations, Chutes, Groq, Gemini, Cerebras, DeepSeek and others) without requiring paid AI subscriptions for agentic capability. Her agency comes from her tools, her memory, and her routing intelligence. Every session, every feature, and every spec must serve this mission.

## Architecture & Stack
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
- **Dashboard & Architect**:
  - `tools/nina_dashboard.py` (Flask server)
  - `dashboard/puter_architect.html` (Puter.js Dev Console)
- **Key Files**:
  - `main.py` (Entry point)
  - `data/memory/facts.json` (Personal context facts)
  - `guardian.sh` (Shell validation script)

## AI Providers & Quota
- **Priority Priority List:** Free first → Groq → Gemini → Cerebras → DeepSeek → Mistral → Together → Cohere → Fireworks → Perplexity → SambaNova → OpenRouter → xAI → OpenAI (paid, last resort)
- **Provider Tiers:**
  - **Tier 1 (Keyless):** POLLINATIONS, CHUTES, HFPUBLIC
  - **Tier 2 (Keyed):** CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini), ONEBRAIN
  - **Tier 3:** OPENROUTER
  - **Local:** LOCALFAST (qwen2.5:1.5b), LOCALHEAVY (qwen2.5:7b)
- **Routing Score Algorithm:** `success_rate × 0.4 + (1 - latency / 5000) × 0.4 + not_near_limit × 0.2`
- **Circuit Breaker state:** CLOSED → OPEN (3 failures/5min) → HALF-OPEN (probe after 1800s)

## Current Phase & Next Task
- **Current Stage:** Stage B — Make NINA Smarter (PARTIAL)
- **What is done:**
  - B-1 F-01 Self-check pass in `core/agent.py` (DONE)
  - B-2 F-02 Personal context injection in `core/memory.py` and `data/memory/facts.json` (DONE)
- **What is next:**
  - B-3 F-03 Response tone calibration in system prompt (`core/nina.py` SYSTEM_PROMPT_TEMPLATE)

## Open Milestones
- **B-3 F-03**: Response tone calibration in system prompt (`core/nina.py` SYSTEM_PROMPT_TEMPLATE)
- **C-1 F-04**: Expenditure tracker tool (`tools/finance.py`)
- **C-2 F-05**: Share market monitor (`tools/market.py`) + `crons/manager.py`
- **C-3 F-06**: Proactive reminder engine (`core/nina.py` + `data/reminders.json`)
- **C-4 F-07**: Email triage improvement (`tools/office_mail.py`)
- **C-5 F-08**: Personal knowledge base (`core/memory.py` + Telegram command handler)
## Completed Milestones
- **S-01**: Fix SSRF substring → `ipaddress` module (`tools/browser.py`) (DONE)
- **S-02**: Wrap memory file I/O in `asyncio.to_thread` (`core/memory.py`) (DONE)
- **S-03**: Fix `ResponseCache.purge_expired` dict mutation (`core/router.py`) (DONE)
- **S-04**: Add model version override dict to `NinaConfig` (`core/config.py`) (DONE)
- **S-05**: Add `if not root.handlers` guard in logger setup (`core/nina.py`) (DONE)

## Action Board Confidence
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

## Capabilities
- **shell**: loaded=true, healthy=true
- **web**: loaded=true, healthy=true
- **browser**: loaded=true, healthy=true
- **file**: loaded=true, healthy=true
- **system**: loaded=true, healthy=true
- **email**: loaded=true, healthy=true
- **gpu**: loaded=true, healthy=true

## Memory Facts
- **name**: M. Baizid Alam
- **role**: AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **language**: English and Bangla — match the register used
- **timezone**: UTC+6 (Dhaka)
- **domains**: SWIFT, MT103, MT202, MT700, LC, BG, BB compliance, ISO 27001 Lead Auditor
- **style**: Direct, peer-level, no fluff. Concise. Flag risks proactively.
- **github**: github.com/aibony
- **project**: NINA — local-first autonomous AI operator, self-hosted on VivoBook Ubuntu

## Key File Paths
- **Repository:** `/home/aibony/nina`
- **Virtual Environment:** `/home/aibony/nina/ninavenv` (or `.venv`)
- **Systemd Service:** `/etc/systemd/system/nina.service`
- **Rotating Logs Directory:** `/home/aibony/nina/logs/`
- **Exports Directory:** `/home/aibony/nina/exports/`

## NINA Tool Routing Policy v2 Summary

**Principle:** Perplexity plans, the local executor stabilizes, Jules builds — running IN PARALLEL.

### Four-Tool Parallel Model

| Tool | Role | Execution Mode |
|------|------|---------------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Active throughout — specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| Local Executor (ninaflash, Cursor, Claude Code, Cline, aider) | LOCAL MUSCLE | Sync local executor — edits, merges Jules PRs, deploys to service |
| aider-chat (./nina-aider.sh) | INTERACTIVE LOCAL CODER — interactive multi-file editing with full repo context via OpenRouter. Use when iterating live with direct file edits and needing conversational pair-programming. Requires terminal presence. | Interactive sync |

### The Full Parallel Loop
1. Perplexity diagnoses + writes precise spec
2. Jules receives spec → builds in cloud async (no interaction after submit)
3. The local executor handles any urgent local fixes in parallel on its own worktree
4. Jules opens PR when done
5. The local executor reviews Jules PR diff, runs lint/compile checks, merges to main
6. The local executor runs `./nina_sync.sh` to deploy and export
7. Perplexity reviews result (attach `nina_latest.md` to new thread)

### Local Executor as Merge Executor (Mandatory)
- The local executor performs ALL Jules PR merges — never auto-merge via GitHub UI
- Before merge: `python3 -m py_compile` + `pyflakes` on changed files, check `jules_lock.txt`
- After merge: `./nina_sync.sh` — no exceptions
- Merge conflict → stop, escalate to Perplexity for re-spec

### Key Rules
- Check `jules_lock.txt` before starting any task.
- High-risk files (`main.py`, `router.py`, `telegram_interface.py`, `guardian_engine.py`, `shell.py`, `.env`) default to local executor / manual local only.
- Perplexity requires exact source attachments for code edits; `nina_latest.md` is for snapshot awareness only.
- Sensitive paths remain LOCAL only — never cloud.
```

### jules_lock.txt
Last modified: 2026-06-09 20:39:28
Size: 171 bytes
```markdown
LOCKED_FILES=tools/nina_sync.py,tests/test_nina_sync.py,.ninaignore,requirements.txt
JULES_TASK=B-005
JULES_PR=feat/b-005-nina-sync
LOCKED_SINCE=2026-06-08T16:58:50+00:00
```

### nina_context.md
Last modified: 2026-06-11 15:46:24
Size: 8963 bytes
```markdown
---
title: NINA Context
version: 14.0
updated: 2026-06-11
stage: "A✅ B✅ C✅ M(high-throughput)🚀"
---

# NINA Context — Attach to Every New Thread

## Overview
A comprehensive state-of-the-union document for NINA, mapping her identity, environment, and development status. This is the canonical source for new agent threads to understand their context.

## 2026-06-11 Update: Optimization Offensive (v14.0)
NINA has entered the "High-Throughput" phase. All agents now operate under **NINA-OPT-001**, prioritizing local CPU/GPU execution (NinaFlash/NinaGate) to reduce cloud token costs by 90%. Unified context is now maintained exclusively in `AGENTS.md`.

## Purpose
To provide instant alignment for AI agents (Jules, Perplexity, ninaflash) on project architecture, owner preferences, and the current phase of autonomous development.

## Usage
Attach this file to the beginning of every new conversation with a NINA-aligned agent to ensure continuity and prevent architectural drift.

## Owner Profile

- **Name:** M. Baizid Alam — AGM, BASIC Bank Limited, Dhaka, Bangladesh
- **Personal email:** onlybony@gmail.com | **Work:** alam.b@basicbanklimited.com | **Shared:** basicid@basicbanklimited.com
- **LinkedIn:** linkedin.com/in/mba2009 | **GitHub:** github.com/aibony
- **Background:** 16 yrs banking — SWIFT/MT103/MT202/MT700, LC, BG, BB compliance, ISO 27001 Lead Auditor, BSc Engg + MBA
- **Language:** English and Bangla — match the register used
- **Style:** Direct, peer-level, no fluff. Flag risks first. Concise only.
- **Domains:** SWIFT, MT103, LC, BG, Bangladesh Bank compliance, ISO 27001

## What NINA Is

Local-first autonomous AI operator — not a chatbot. Runs 24/7 on owner's laptop in Dhaka. Acts inside the real environment: reads BASIC Bank Exchange mailbox (EWS/NTLM), runs shell commands, monitors markets, tracks expenses, pushes proactive Telegram alerts, self-upgrades with human approval. Never sends sensitive/banking data to cloud providers.

**PRIME DIRECTIVE:** Reduce cloud token usage by 90%, accelerate feature delivery by 10x, and maximize local autonomous throughput.

**One-line test for every feature:** *Does this make NINA more like an extension of me, or just more like a chatbot?* If it passes, build it. If not, defer it.

- **Repo:** github.com/aibony/nina — Public, MIT, v13.0 released 2026-06-11
- **Portfolio:** aibony.github.io
- **Grant target:** Anthropic Claude $1,200 OSS grant

## Environment

- **Machine:** ASUS VivoBook X530FN — Ubuntu 26.04 LTS — Python 3.14.4 — User: aibony
- **GPU:** MX150 2GB VRAM | **RAM:** 16GB
- **Repo/Venv:** `nina` / `venv`
- **Service:** systemd `nina.service` — Restart=always, depends on `ollama.service`, `ninagate.service`
- **Local models:** Ollama — `qwen2.5-coder:1.5b` (LOCALFAST), `qwen2.5-coder:7b` (LOCALHEAVY), `deepseek-coder:1.3b`
- **EWS:** webmail.basicbanklimited.com — Auth: NTLM — Domain: basic.bank
- **NinaGate:** OpenAI-compatible proxy at `http://localhost:8080`

## Start / Stop / Restart

```bash
cd nina && ./guardian          # Recommended — full health check before start
sudo systemctl start nina      # Direct systemd
sudo systemctl stop nina
sudo systemctl restart nina
sudo systemctl status nina
```

## Logs

```bash
journalctl -u nina -f          # Live
journalctl -u nina -n 50       # Last 50 lines
cat nina/nina_update_log.md    # Change history
cat nina/nina_problem_log.md   # Bug/fix history
```

## Guardian — MUST run before AND after every patch

```bash
cd nina && ./guardian
```

## Git Workflow

```bash
git status
git add <specific files>       # NEVER git add .
git commit -m "type: description (ID)"
git push origin main
```

## .env Key Variables

| Key | Required | Notes |
|-----|----------|-------|
| `TELEGRAM_BOT_TOKEN` | BLOCKER | Bot token from @BotFather |
| `AUTHORIZED_USER_ID` | BLOCKER | Your Telegram user ID |
| `JULES_API_KEY` | BLOCKER | Async builder access |
| `GROQ_API_KEY` | Recommended | Free tier, default cloud provider |
| `GEMINI_API_KEY` | Recommended | Free tier fallback |
| `EWS_PASSWORD` | **SET THIS** | Activates email triage, morning report, urgency nudge |
| `RAM_GUARD_GB` | Optional | Default 10.5 |
| `API_SECRET_KEY` | BLOCKER | API security |

## Provider Architecture — 19 Providers + 2 Local

**Priority:** Free first → Groq → Gemini → Cerebras → DeepSeek → Mistral → Together → Cohere → Fireworks → Perplexity → SambaNova → OpenRouter → xAI → OpenAI (paid, last resort)

| Tier | Providers |
|------|-----------|
| TIER 1 (keyless) | POLLINATIONS, CHUTES, HFPUBLIC |
| TIER 2 (keyed) | CEREBRAS, GROQ, GEMINI, MISTRAL, DEEPSEEK, TOGETHER, COHERE, FIREWORKS, XAI, PERPLEXITY, SAMBANOVA, HYPERBOLIC, NOVITA, OPENAI (gpt-4o-mini), ONEBRAIN |
| TIER 3 | OPENROUTER |
| LOCAL | LOCALFAST (qwen2.5:1.5b), LOCALHEAVY (qwen2.5:7b) |

- **Routing score:** `success_rate×0.4 + (1−latency/5000)×0.4 + not_near_limit×0.2`
- **CircuitBreaker:** CLOSED → OPEN (3 failures/120s) → HALF-OPEN (probe after 60s)
- **Sensitive tasks:** LOCAL only, no exceptions

## Thermal Guard

| Tier | CPU | GPU | Action |
|------|-----|-----|--------|
| WARN | 80°C | 80°C | Log warning only |
| GUARD | 90°C | 85°C | Force LOCALFAST, ban LOCALHEAVY |
| CRITICAL | 95°C | 90°C | Abort agent loop, notify Telegram |

## Codebase Structure

```
core/
  nina.py          NinaOS — orchestrator, startup/shutdown, morning report
  router.py        HybridRouter V4 — CircuitBreaker, composite scoring, parallel fan-out
  config.py        NinaConfig (Pydantic), RATELIMITS, load_config
  agent.py         AgentLoop — THINK-PLAN-ACT, thermal preflight, self-check pass
  memory.py        MemorySystem — ChromaDB + facts.json, build_context, remember/forget
  capabilities.py  CapabilityRegistry — per-tool health tracking
  hotreload.py     ConfigHotReload — watches .env every 60s, 18 reloadable fields

tools/
  ninaflash.py     Universe-Mode kernel — Nucleus with 100+ functions, local research/triage
  jules_api.py     Jules REST API — task dispatch (14 concurrent max)
  shell.py         Allowlist-gated shell, 10s timeout, 2000 char truncation
  web.py           DuckDuckGo search, user-agent rotation, exponential backoff
  browser.py       Playwright headless, text-only, 5000 char, SSRF-protected
  system.py        RAM/VRAM/CPU/disk/thermal, get_temps, get_ram_used_gb
  files.py         Workspace-scoped file ops, path traversal check on every call
  officemail.py    EWS/NTLM email fetch, urgency keyword scan, emailaccess.log
  search.py        Tavily → Serper → DuckDuckGo fallback chain
  gputuner.py      Dynamic GPU memory management, VRAM headroom adjustment
  upgradepipeline.py Gated patch — scan→sandbox→diff→approve→deploy

ninagate/
  main.py          API Proxy — rutas requests through priority cascade, port 8080

interfaces/
  telegram_interface.py  Security gate, 20 commands, NLP, streaming, flood control
  api.py                REST API

crons/
  manager.py       APScheduler — 13 jobs (morning report, heartbeat, thermal, backups, etc.)

guardianengine.py  Forensic engine — AST scan, baseline drift, service health
healthcheck.py     Test suite — import isolation, structural regression
idleloop.py        Idle upgrade proposal loop, 7-topic rotation, pings Telegram

main.py                   Entry point, asyncio event loop, SIGTERM/SIGINT shutdown
data/memory/facts.json    Persistent key-value personal facts store
AGENTS.md                 Agent operating law (canonical) — MANDATORY READ
docs/space/jules_backlog.md  Task registry — 83 READY optimization tasks
```

## Phase 1 Status

### Stage A — Stop Active Failures COMPLETE (v12.2)

### Stage B — Make NINA Smarter COMPLETE (v13.0)

- B-1 F-01 Self-check pass in core/agent.py — DONE
- B-2 F-02 Personal context injection — DONE
- B-3 F-03 System prompt rewrite — DONE

### Stage C — New Capabilities (PARTIAL)

- C-1 F-04 tools/finance.py — DONE
- C-2 F-05 tools/market.py — DONE
- C-3 F-06 Reminder engine — DONE
- C-4 F-07 Email triage — DONE (officemail.py)
- C-5 F-08 remember/recall — DONE

### Stage M — Optimization Offensive (v2.0/v2.1) — READY🚀

- M-1 🚀 MEGA-TASK: Throughput Maximizer (v2.0) — IN_PROGRESS (Jules)
- M-2 📉 MEGA-TASK: Token-Surgical Architecture (v2.1) — IN_PROGRESS (Jules)
- M-3 to M-12: Token-saving infrastructure — IN_PROGRESS (Jules)
- N to T: 71 Advanced optimization tasks — READY

## Next Steps — Priority Order

1. **Merge Optimization Batch 1:** Integrate Jules' PRs for M-01 to M-10.
2. **Implement Local Fast-Path:** Move boilerplate generation to local Ollama models.
3. **Surgical Context:** Implement `nf code symbol` to avoid full-file reads.
4. **Instruction Compression:** Refactor `AGENTS.md` to reduce token overhead.

---

*Last updated: 2026-06-11 — Version 13.0 integrated (Optimization Offensive launched)*
```

### nina_update_log.md
Last modified: 2026-06-11 23:29:13
Size: 74962 bytes
```markdown
# NINA v12.2 Update Log

**Machine:** ASUS VivoBook X530FN (aibony) · i5 8th Gen · 16GB RAM · MX150 2GB VRAM  
**OS:** Ubuntu 26.04 LTS · Python 3.14  
**Last updated:** 2026-06-06  
**Full history → exports/nina_update_log_archive_2026-05.md**

---

## Entry 094 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v4 automated run

**Files changed:** docs/space/nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 095 — 2026-06-06 · nina_sync.sh Step 8 rewritten — single fixed output nina_latest.md

**Triggered by:** User request to rewrite Step 8 of nina_sync.sh to output to a single fixed file and clear accumulated backups.

**Files changed:**
- `nina_sync.sh`

**What changed:**
- Rewrote the Step 8 docs export block to output to a single fixed path: `~/Downloads/nina_space_upload/nina_latest.md`.
- Added logic to run `nina_docs_export.sh` silently.
- Added logic to automatically remove old timestamped `nina_docs_backup*.md` files in `~/Downloads/nina_space_upload/` after copying the latest.
- Cleaned up old `nina_docs_backup*.md` files manually from the target directory during deployment.

**What was verified:**
- Bash syntax validation passed successfully (`bash -n`).
- Extraneous files cleared from `~/Downloads/nina_space_upload/`.

**Rollback path:**
- `git checkout HEAD -- nina_sync.sh nina_update_log.md`

---

## Entry 096 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v4 automated run

**Files changed:** docs/space/nina_update_log.md,nina_sync.sh,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 097 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v4 automated run

**Files changed:** docs/space/nina_update_log.md,nina_sync.sh,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 098 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v4 automated run

**Files changed:** docs/space/nina_update_log.md,nina_sync.sh,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 099 — 2026-06-06 · nina_sync.sh Step 8 — full master export (docs+code+shell+json) into nina_latest.md

**Triggered by:** User request to perform a full master export in Step 8.

**Files changed:**
- `nina_sync.sh`

**What changed:**
- Rewrote the Step 8 export block inside `nina_sync.sh` to generate a comprehensive backup (DOCS, PYTHON CODE, SHELL SCRIPTS, and JSON/CONFIG) in one consolidated file: `~/Downloads/nina_space_upload/nina_latest.md`.
- Corrected the find pattern to prune the virtual environment folder `.venv/` (preventing massive library file leakage and reducing backup size from 94MB to ~506KB).
- Verified the generated file size is 506,307 bytes.

**What was verified:**
- Bash syntax validation passed successfully (`bash -n`).
- Executed successfully and produced `nina_latest.md` with size 506,307 bytes.

**Rollback path:**
- `git checkout HEAD -- nina_sync.sh nina_update_log.md`

---

## Entry 100 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v4 automated run

**Files changed:** docs/space/nina_update_log.md,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 101 — 2026-06-06 · rclone Google Drive auto-upload wired into nina_sync.sh Step 8

**Triggered by:** User request to integrate rclone Google Drive automated backup uploading.

**Files changed:**
- `nina_sync.sh`

**What changed:**
- Installed `rclone v1.74.3` locally in `~/bin/rclone` to bypass sudo password prompt block.
- Configured a Google Drive remote `gdrive` using headless auth flow.
- Created `nina-backup` folder on Google Drive and verified connection.
- Tested and verified manual upload of `nina_latest.md` (509,041 bytes) successfully.
- Added `PATH` extension in `nina_sync.sh` to include `~/bin/`.
- Integrated `rclone copy` logic inside Step 8 block of `nina_sync.sh` to automatically push `nina_latest.md` to `gdrive:nina-backup/`.

**What was verified:**
- Bash syntax validation passed successfully (`bash -n`).
- Google Drive upload and connection verified.

**Rollback path:**
- `git checkout HEAD -- nina_sync.sh nina_update_log.md`

---

## Entry 102 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v4 automated run

**Files changed:** docs/space/nina_update_log.md,nina_sync.sh,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 103 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v4 automated run

**Files changed:** docs/space/nina_update_log.md,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 104 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v4 automated run

**Files changed:** docs/space/nina_update_log.md,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 105 — 2026-06-06 · DEV 5.9 — All Jules PRs superseded by live sync, pyflakes pre-existing advisory warnings noted, runtime verified

**Triggered by:** Live sync post-session verification

**What changed:**
- Checked out and verified smoke tests folder from origin branch `nina-j03-infrastructure-51527560572439502`.
- Installed `pytest` in virtual environment.
- Closed 6 stale open Jules pull requests (#11, #9, #12, #10, #8, #6) on GitHub as superseded by live sync or empty session.

**What was verified:**
- py_compile: PASS (all Python files syntax compiled successfully)
- pyflakes: Advisory non-blocking (pre-existing warnings in `guardian_engine.py` and `healthcheck.py` bypassed)
- pytest result: 10 passed tests in `tests/test_smoke.py`
- healthcheck result: Health: WARN (due to duplicate root logger handler warning)
- service status: nina.service is active (running) and fully operational

**Rollback path:**
- `git checkout HEAD -- nina_update_log.md tests/`

---

## Entry 106 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v4 automated run

**Files changed:** docs/space/nina_update_log.md,nina_update_log.md,tests/__init__.py,tests/test_smoke.py,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 107 — 2026-06-06 · D-13 REVERTED — nina_sync.sh hard block removed, D-12 soft warning retained

**Triggered by:** Manual policy reversion request.

**What changed:**
- Inspected `nina_sync.sh` to confirm the status of the D-13 hard block (which blocks runs if open Jules PR branches exist).
- Verified that the D-13 hard block is absent from `nina_sync.sh` and that the file passes shell syntax check.
- Confirmed that the D-12 soft warning block (which skips git push and warns the user when Jules PR branches are open) is retained intact in the `[6/8] Committing and pushing...` stage.

**What was verified:**
- `bash -n nina_sync.sh`: PASS
- `grep "exit 1" nina_sync.sh`: Returned nothing (no hard block present)
- `grep "JULES_BRANCHES" nina_sync.sh`: Returned the expected D-12 soft warning lines

**Rollback path:**
- `git checkout HEAD -- nina_update_log.md`

---

## Entry 108 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_update_log.md,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 109 — 2026-06-06 · D-07/D-08/D-09/D-10 MD file audit fixes — AGENTS dedup, nina_context stale items, error_register shell.allowlist closed, update_log renumbered

**Triggered by:** Manual MD files audit and cleanup request.

**What changed:**
- **FIX 1 (D-07):** Inspected `AGENTS.md` and confirmed Jules rules deduplication. Verified that grep count for "Do NOT pause for confirmation" is 1.
- **FIX 2 (D-08):** Inspected `docs/space/nina_context.md` and `nina_context.md`. Confirmed EWS/F-03/SSRF/cat-allowed items are in sync and updated. Verified that `core/logger.py` is marked as deleted in R-101.
- **FIX 3 (D-09):** Checked `docs/space/nina_error_register.md`. Verified that `shell.allowlist.regression` status is FIXED and mapped to R-97.
- **FIX 4 (D-10):** Created a backup of `logs/nina_update_log.md` and executed a Python script to dynamically renumber all entries after the first sequence break (from Entry 015 onwards) to be sequentially ascending. Verified line count is identical and head -40 is sequential.

**What was verified:**
- `grep -c "Do NOT pause for confirmation" AGENTS.md`: 1
- `grep "DELETED in R-101" docs/space/nina_context.md`: Verified
- `grep "shell.allowlist.regression" docs/space/nina_error_register.md`: Shows FIXED in R-97
- `wc -l logs/nina_update_log.md`: Identical before and after (1463 lines)
- `grep "^## Entry\|^--- Entry" logs/nina_update_log.md | head -40`: sequential numbers

**Rollback path:**
- `git checkout HEAD -- AGENTS.md nina_context.md docs/space/nina_context.md docs/space/nina_error_register.md && cp upgrades/backups/nina_update_log.bak.* logs/nina_update_log.md`

---

## Entry 109 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_update_log.md,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

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

## Entry 111 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,docs/space/AGENTS.md,docs/space/nina_update_log.md,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,jules_lock.txt,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 112 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 113 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

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

## Entry 115 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_update_log.md,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

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

## Entry 117 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_update_log.md,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 118 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

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

## Entry 120 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_update_log.md,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

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

## Entry 122 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_update_log.md,nina_sync.sh,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active


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

## Entry 032 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/capabilities.json,docs/space/facts.json,docs/space/nina_context.md,docs/space/nina_error_register.md,docs/space/nina_phase1_roadmap.md,docs/space/nina_problem_log.md,docs/space/nina_update_log.md,docs/space/nina_v12_blueprint.md,docs/space/requirements.txt,nina_sync.sh,nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,docs/space/nina_state.md,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active


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

## Entry 034 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_sync.sh,nina_update_log.md,tools/compact_exporter.py,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active


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

## Entry 036 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,docs/space/AGENTS.md,docs/space/nina_state.md,nina_update_log.md,tools/compact_exporter.py,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

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

## Entry 038 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

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

## Entry 040 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 041 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 042 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 043 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 044 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 045 — 2026-06-06 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 046 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 047 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,.jules_tasks/,append_log.py,append_log_d02.py,append_log_d03.py,docs/archive/,exports/,gen.py,nina_master_export.sh,nina_v12_blueprint.md,patch_telegram.py,shrink_roadmap.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 048 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md,nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 049 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 050 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md,nina_update_log.md,docs/space/WORKFLOW.md

**Verification:** git push OK, nina.service active

---

## Entry 051 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/compact_exporter.py

**Verification:** git push OK, nina.service active

---

## Entry 052 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt

**Verification:** git push OK, nina.service active

---

## Entry 053 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** WORKFLOW.md,docs/space/WORKFLOW.md,docs/space/nina_exporter_contract.md,exports/nina_latest.md,nina_sync.sh,nina_update_log.md,tools/compact_exporter.py

**Verification:** git push OK, nina.service active

---

## Entry 054 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 055 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 056 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 057 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 058 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt

**Verification:** git push OK, nina.service active

---

## Entry 059 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 060 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md,nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 061 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 062 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active
## Entry 063 — 2026-06-07 · feat(identity): B-3 F-03 — agentic identity directive in system prompt, AGENTS.md, nina_state.md

**Triggered by:** User request.

**Files changed:**
- `core/nina.py`
- `AGENTS.md`
- `docs/space/nina_state.md`

**What changed:**
- Added NINA agentic identity directive to SYSTEM_PROMPT_TEMPLATE in core/nina.py, AGENTS.md top section, and docs/space/nina_state.md identity block. NINA is now declared as autonomous agent not chatbot across all canonical files.

**What was verified:**
- py_compile + pyflakes on core/nina.py passed.

**Rollback path:**
- git checkout HEAD -- core/nina.py AGENTS.md docs/space/nina_state.md nina_update_log.md

---

---

## Entry 064 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,core/nina.py,docs/space/AGENTS.md,docs/space/nina_state.md,nina_sync.sh,nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service activating

---

## Entry 065 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active
## Entry 066 — 2026-06-07 · feat(cli): G-01 — add interfaces/cli_interface.py and bin/nina

**Triggered by:** User request.

**Files changed:**
- `interfaces/cli_interface.py`
- `bin/nina`

**What changed:**
- Created CLI interface. Accepts task from argv or stdin. Builds NinaConfig directly from dotenv (bypasses load_config Telegram guard). Instantiates HybridRouter, MemorySystem, AgentLoop with correct signatures. Created bin/nina shell wrapper. Did NOT touch main.py.

**What was verified:**
- py_compile + pyflakes passed. Smoke test ran.

**Rollback path:**
- rm interfaces/cli_interface.py bin/nina && git checkout HEAD -- nina_update_log.md

---

---

## Entry 067 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** bin/nina,data/model_cache.json,interfaces/cli_interface.py,nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 068 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service activating
## Entry 069 — 2026-06-07 · feat(ops): install aider-chat and configure OpenRouter

**Triggered by:** User request.

**Files changed:**
- `.aider.conf.yml`
- `nina-aider.sh`

**What changed:**
- Installed `aider-chat` (v0.86.2) and `audioop-lts` for Python 3.14 compatibility. Created `.aider.conf.yml` to set OpenRouter as default backend. Added `nina-aider.sh` wrapper script to export OpenRouter keys and launch aider.

**What was verified:**
- Verified `aider --version` runs correctly.

**Rollback path:**
- rm -f .aider.conf.yml nina-aider.sh && git checkout HEAD -- nina_update_log.md

---

---

## Entry 070 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** .aider.conf.yml,nina_aider.sh,nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service activating
## Entry 071 — 2026-06-07 · docs(policy): G-02 — register aider-chat in four-tool routing policy

**Triggered by:** User request.

**Files changed:**
- `AGENTS.md`
- `docs/space/nina_state.md`

**What changed:**
- Added aider-chat row to routing policy table. Updated Three-Tool to Four-Tool. Added Hard Routing Rules for aider sessions.

**What was verified:**
- grep confirmed aider not previously present before edit.

**Rollback path:**
- git checkout HEAD -- AGENTS.md docs/space/nina_state.md nina_update_log.md

---

---

## Entry 072 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,docs/space/AGENTS.md,docs/space/nina_state.md,nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service activating
## Entry 073 — 2026-06-07 · docs(policy): G-03 — make AGENTS.md tool-agnostic for IDE switching and update routing policy to four-tool

**Triggered by:** User request.

**Files changed:**
- `AGENTS.md`
- `docs/space/nina_state.md`

**What changed:**
- Added a tool-agnostic local executor header to the top of `AGENTS.md`. Revised all agy-specific terminology to reference `local executor` / `the local executor` to support seamless switching between IDEs (agy, Cursor, Claude Code, Cline, aider). Updated the summary model and loop in `docs/space/nina_state.md` to reflect the tool-agnostic four-tool model.

**What was verified:**
- Verified with grep and git diff. No Python files were changed.

**Rollback path:**
- git checkout HEAD -- AGENTS.md docs/space/nina_state.md nina_update_log.md

---

---

## Entry 074 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,docs/space/AGENTS.md,docs/space/nina_state.md,jules_lock.txt,nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service activating

---

## Entry 075 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/compact_exporter.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 076 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service activating
## Entry 077 — 2026-06-07 · docs(policy): G-04 — make NINA docs tool-agnostic for IDE switching and update routing policy to four-tool

**Triggered by:** User request.

**Files changed:**
- `AGENTS.md`
- `docs/space/nina_state.md`

**What changed:**
- Made the markdown documentation system work cleanly when switching between agy, Cursor, Claude Code, Cline, and aider. Refined existing docs so the active local tool is treated as the local executor.

**What was verified:**
- Verified via git diff and grep. No Python files were changed.

**Rollback path:**
- git checkout HEAD -- AGENTS.md docs/space/nina_state.md nina_update_log.md

---

---

## Entry 078 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service activating

---

## Entry 079 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service activating

---

## Entry 080 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** crons/backup_jobs.py,crons/manager.py,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 081 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 082 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,bin/ninaflash,tools/ninaflash.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 083 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,WORKFLOW.md,bin/ninaflash,docs/space/AGENTS.md,docs/space/WORKFLOW.md,tools/ninaflash.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active
## Entry 084 — 2026-06-07 · docs: rename agy references to ninaflash across the workspace

**Triggered by:** User request.

**Files changed:**
- `AGENTS.md`
- `docs/space/AGENTS.md`
- `docs/space/nina_state.md`
- `docs/space/jules_backlog.md`
- `docs/space/nina_exporter_contract.md`
- `docs/space/nina_error_register.md`
- `docs/space/agy_task_tracker.md` (renamed to `ninaflash_task_tracker.md`)
- `tools/ninaflash.py`
- `nina_sync.sh`
- `jules_lock.txt`

**What changed:**
- Renamed all occurrences of the word `agy` to `ninaflash` (matching the casing) in all active documentation and configuration files.
- Renamed the task tracker file to `ninaflash_task_tracker.md` and updated references to it in the sync script and backlog.
- Updated `tools/ninaflash.py` to support checking for both `agy only` and `ninaflash only` tags in backlog tasks.

**What was verified:**
- Verified syntax correctness and compile status of `tools/ninaflash.py`.
- Verified file layout and status using `git status`.

**Rollback path:**
- `git checkout HEAD -- AGENTS.md docs/space/AGENTS.md docs/space/nina_state.md docs/space/jules_backlog.md docs/space/nina_exporter_contract.md docs/space/nina_error_register.md tools/ninaflash.py nina_sync.sh jules_lock.txt && rm docs/space/ninaflash_task_tracker.md && git checkout HEAD -- docs/space/agy_task_tracker.md`

---
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
---

## Entry 085 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 086 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 087 — 2026-06-07 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 088 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 089 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 090 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 091 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 092 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 093 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 094 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 095 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 096 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 097 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 098 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 099 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 100 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** .gitignore,jules_lock.txt,tools/ninaflash.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 101 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/compact_exporter.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 102 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 103 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 104 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 105 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 106 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 107 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 108 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 109 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 110 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,jules_lock.txt,nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 111 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md,docs/space/jules_backlog.md,jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 112 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 113 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 114 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 115 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 116 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** jules_lock.txt,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 117 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 118 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** core/router.py,data/model_cache.json,docs/space/jules_backlog.md,docs/space/jules_task_tracker.md,jules_lock.txt,tests/test_router.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 119 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** core/config.py,core/router.py,jules_lock.txt,tests/test_router.py,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 120 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 121 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,docs/space/jules_task_tracker.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 122 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,docs/space/jules_task_tracker.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 123 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,docs/space/jules_task_tracker.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 124 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,docs/space/jules_task_tracker.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 125 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_task_tracker.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 126 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 127 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 128 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_state.md,nina.service,nina_context.md,nina_problem_log.md,tools/nina_dashboard.py,nina-dashboard.service,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 129 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_sync.sh,tools/compact_exporter.py,nina-dashboard.service,upgrades/.guardian_handoff.json,upgrades/guardian_baseline.json

**Verification:** git push OK, nina.service active

---

## Entry 130 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/nina_dashboard.py

**Verification:** git push OK, nina.service active

---

## Entry 131 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/tasks.json

**Verification:** git push OK, nina.service active

---

## Entry 132 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md,data/tasks.json

**Verification:** git push OK, nina.service active

---

## Entry 133 — 2026-06-08 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/tasks.json

**Verification:** git push OK, nina.service active

---

## Entry 134 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/tasks.json

**Verification:** git push OK, nina.service active

---

## Entry 135 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_sync.sh,data/tasks.json

**Verification:** git push OK, nina.service active

---

## Entry 136 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/tasks.json

**Verification:** git push OK, nina.service active

---

## Entry 137 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/tasks.json

**Verification:** git push OK, nina.service active

---

## Entry 138 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/ninaflash.py

**Verification:** git push OK, nina.service active

---

## Entry 139 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/ninaflash.py

**Verification:** git push OK, nina.service active

---

## Entry 140 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/ninaflash.py

**Verification:** git push OK, nina.service active

---

## Entry 141 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/ninaflash.py

**Verification:** git push OK, nina.service active

---

## Entry 142 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/ninaflash.py,kernel_generator.py,tools/kernel/

**Verification:** git push OK, nina.service active

---

## Entry 143 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** tools/ninaflash.py,kernel_generator.py,tools/kernel/

**Verification:** git push OK, nina.service active

---

## Entry 001 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md,docs/space/WORKFLOW.md

**Verification:** git push OK, nina.service active

---

## Entry 145 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 146 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** core/router.py,docs/logs/nina_update_log.md,docs/space/ninaflash_task_tracker.md,docs/space/jules_backlog.md,tests/test_router.py,nina_update_log.md

**Verification:** git push OK, nina.service active

---

## Entry 147 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/ninaflash_task_tracker.md,nina_update_log.md,repro_r77.py

**Verification:** git push OK, nina.service active

---

## Entry 148 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** ninagate/main.py,tools/ninaflash.py,nina_update_log.md,repro_r77.py

**Verification:** git push OK, nina.service active

---

## Entry 149 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md

**Verification:** git push OK, nina.service active

---

## Entry 150 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_sync.sh,data/circuit_state.json,nina_codebase_backup.sh,nina_docbase_backup.sh,nina_logbase_backup.sh

**Verification:** git push OK, nina.service active

---

## Entry 151 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/circuit_state.json,nina_codebase_backup.sh,nina_docbase_backup.sh,nina_logbase_backup.sh

**Verification:** git push OK, nina.service active

---

## Entry 152 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_sync.sh,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 153 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_codebase_backup.sh,nina_docbase_backup.sh,nina_logbase_backup.sh,nina_sync.sh,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 154 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 155 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 156 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 157 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 158 — 2026-06-09 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** bin/ninagate,data/circuit_state.json,generate_backups.sh

**Verification:** git push OK, nina.service active

---

## Entry 159 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** bin/ninagate,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 160 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** bin/ninagate,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 161 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_update_log.md,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 162 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 163 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/AGENTS.md,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 164 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_sync.sh,data/circuit_state.json,docs/space/claude_feed.md,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 165 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 166 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** core/memory.py,nina_update_log.md,pytest.ini,tests/test_finance.py,tests/test_finance_market.py,tests/test_memory.py,data/circuit_state.json,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 167 — 2026-06-10 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** nina_context.md,data/circuit_state.json,docs/space/AGENTS.md,docs/space/WORKFLOW.md,exports/nina_problem_log_archive.md,generate_backups.sh,ninagate_load_test.sh

**Verification:** git push OK, nina.service active

---

## Entry 168 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_repo_hygiene_dashboard.md,docs/space/AGENTS.md,docs/space/WORKFLOW.md

**Verification:** git push OK, nina.service active

---

## Entry 169 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_repo_hygiene_dashboard.md,docs/space/AGENTS.md,docs/space/WORKFLOW.md

**Verification:** git push OK, nina.service active

---

## Entry 170 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/nina_repo_hygiene_dashboard.md,nina_sync.sh

**Verification:** git push OK, nina.service active

---

## Entry 171 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/claude_feed.md,docs/space/nina_index.json,docs/space/nina_repo_hygiene_dashboard.md,nina_sync.sh,tools/validate_index.py

**Verification:** git push OK, nina.service active

---

## Entry 172 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/jules_backlog.md,nina_update_log.md

**Verification:** git push OK, nina.service activating

---

## Entry 173 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,docs/space/nina_repo_hygiene_dashboard.md,.gemini/

**Verification:** git push OK, nina.service activating

---

## Entry 174 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** ARCHITECTURE.md,README.md,docs/space/claude_feed.md,docs/space/nina_repo_hygiene_dashboard.md,nina_context.md,.gemini/

**Verification:** git push OK, nina.service activating

---

## Entry 175 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/claude_feed.md,docs/space/nina_repo_hygiene_dashboard.md,ninagate/main.py,tools/ninaflash.py,.gemini/,ninagate/quotas.json

**Verification:** git push OK, nina.service activating

---

## Entry 176 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,ARCHITECTURE.md,docs/space/nina_repo_hygiene_dashboard.md,.gemini/

**Verification:** git push OK, nina.service activating

---

## Entry 177 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/ninaflash.md,docs/router.md,docs/space/claude_feed.md,docs/space/nina_repo_hygiene_dashboard.md,.gemini/

**Verification:** git push OK, nina.service activating

---

## Entry 178 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,docs/space/claude_feed.md,docs/space/nina_repo_hygiene_dashboard.md,.gemini/

**Verification:** git push OK, nina.service activating

---

## Entry 179 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** ARCHITECTURE.md,docs/space/claude_feed.md,docs/space/nina_repo_hygiene_dashboard.md,.gemini/

**Verification:** git push OK, nina.service active

---

## Entry 180 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** ARCHITECTURE.md,CHANGELOG.md,README.md,bin/ninagate,core/agent.py,core/nina.py,dashboard/ninaui.html,docs/nina_proxy_usage.md,docs/ninaflash.md,docs/space/claude_feed.md,docs/space/nina_repo_hygiene_dashboard.md,nina_context.md,ninagate/README.md,ninagate/main.py,ninagate_load_test.sh,tools/nina_proxy.py,tools/ninaflash.py,.gemini/

**Verification:** git push OK, nina.service activating

---

## Entry 181 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** ARCHITECTURE.md,CHANGELOG.md,core/nina.py,docs/space/claude_feed.md,docs/space/nina_repo_hygiene_dashboard.md,tools/browser.py,tools/search.py,tools/system.py,.gemini/,data/router_cache.json,jules_mega_task.md

**Verification:** git push OK, nina.service active

---

## Entry 182 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/claude_feed.md,docs/space/nina_repo_hygiene_dashboard.md,tools/jules_api.py,.gemini/,data/router_cache.json,jules_mega_task.md

**Verification:** git push OK, nina.service active

---

## Entry 183 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,core/router.py,docs/space/claude_feed.md,docs/space/nina_repo_hygiene_dashboard.md,exports/nina_latest.md,ninagate/main.py,tools/jules_api.py,tools/ninaflash.py,.gemini/,core/utils.py,data/router_cache.json,docs/space/nina_megatask_index.md,jules_mega_task.md

**Verification:** git push OK, nina.service active

---

## Entry 184 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** ARCHITECTURE.md,WORKFLOW.md,docs/space/claude_feed.md,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md

**Verification:** git push OK, nina.service activating

---

## Entry 185 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,core/router.py,docs/space/nina_repo_hygiene_dashboard.md,ninagate/main.py,ninagate/providers.json,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service activating

---

## Entry 186 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** ARCHITECTURE.md,README.md,docs/nina_proxy_usage.md,docs/space/claude_feed.md,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service activating

---

## Entry 187 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/claude_feed.md,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service activating

---

## Entry 188 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/claude_feed.md,tools/doc_autogen.py,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service activating

---

## Entry 189 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** ARCHITECTURE.md,README.md,docs/space/claude_feed.md,tools/doc_autogen.py,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service activating

---

## Entry 190 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/claude_feed.md,tools/doc_autogen.py,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service active

---

## Entry 191 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/claude_feed.md,tools/doc_autogen.py,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service activating

---

## Entry 192 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** AGENTS.md,docs/space/claude_feed.md,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service activating

---

## Entry 193 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/claude_feed.md,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service active

---

## Entry 194 — 2026-06-11 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** docs/space/claude_feed.md,.gemini/,core/utils.py,data/router_cache.json,jules_mega_task.md,tools/nina_mcp_server.py

**Verification:** git push OK, nina.service activating

## Auto-doc patch — 2026-06-11
- Model: gemini-3-flash-preview, NinaGate: 8080, Providers: 19
```

### README.md
Last modified: 2026-06-11 23:29:13
Size: 10787 bytes
```markdown
# NINA — Neural Intelligent Network Assistant (v14.0)

## Overview
NINA is an autonomous agentic OS designed for private, local-first operation. It integrates with professional banking workflows while maintaining strict data residency.

## 2026-06-11: High-Throughput Release (v14.0)
This version introduces **NINA-OPT-001**, a unified optimization directive that offloads 90% of development turns to the local CPU. Using **NinaGate** and **NinaFlash**, NINA now performs surgical code extraction and automated maintenance with zero token overhead.

## Purpose
To transform AI from a reactive chatbot into a proactive operational partner that handles email, markets, and code development with minimal human intervention.

## Usage
Deploy NINA on a Linux machine via the provided systemd services. Use the `nf` (ninaflash) CLI for local execution and PR management.

*A self-hosted, self-developing autonomous AI OS running on Ubuntu 26.04.*

## What is NINA?

NINA is NOT a chatbot. It is an action-first autonomous agent that:
- Routes tasks across 20+ AI providers via HybridRouter V4
- Develops itself autonomously via Jules + ninaflash pipeline
- **Optimization Offensive:** v2.0/v2.1 architecture designed to reduce cloud token usage by 90%.
- **Active Pipeline:** 83 READY mega-tasks for autonomous optimization.
- Keeps all banking and sensitive data strictly on the local machine in Dhaka.

## Three-Tier Agent Model

This model is the heart of NINA's architecture:

| Agent | Role | Backend | Scope |
|---|---|---|---|
| Perplexity Enterprise Pro | Architect + Overwatch | Claude Sonnet 4.6 | Strategic direction, specs, post-execution review |
| Jules (jules.google.com) | Async Cloud Coder | Gemini 3.1 Pro | Multi-file feature builds, 14 concurrent session limit |
| ninaflash (nf) | Local Muscle | gemini-3-flash-preview | Local research, syntax fixing, PR merges, triage |

## ninaflash — The Local Muscle

ninaflash is NINA's local high-performance executor:
- CLI tool at `bin/nf` (v6.0+)
- **Surgical Intelligence:** Extract functions/symbols locally to save cloud tokens.
- **Auto-Hygiene:** Local syntax fixing and document auto-formatting.
- Commands:
  - `nf status` — Pulse heartbeat of git, env, and backlog.
  - `nf code outline` — Zero-token signature mapping.
  - `nf check code --fix` — Automated local linting/fixing.
  - `nf backlog summary` — High-density project state.

## Universe-Mode Kernel

The kernel architecture giving NINA near-infinite capability at zero cloud token cost:
- **Nucleus:** Strict 100-function core (`tools/ninaflash.py`) for high reliability.
- **Fast-Path:** Routing via `NinaGate` (port 8080) to local Ollama models.
- **Surgical Context:** Returning 40-line semantic chunks instead of full files.

## HybridRouter V4

The routing engine located in `core/router.py`:
- Routes across 20+ cloud providers (Groq, Gemini, Cerebras, DeepSeek, Mistral, OpenRouter, Together, Cohere, Fireworks, xAI, SambaNova, Hyperbolic, Novita, Perplexity, OpenAI, Pollinations, Chutes, and more)
- 2 local models via Ollama (qwen2.5:1.5b for fast tasks, qwen2.5:7b for heavy reasoning)
- CircuitBreaker pattern prevents cascading failures
- Weighted scoring: success rate × latency × rate limits
- Free-tier first routing philosophy (routing is handled automatically by HybridRouter V4 with free-tier priority)

## nina-mcp Extension

NINA features a native **Gemini CLI Extension** (`.gemini/extensions/nina/`) that provides:
- **MCP Server:** Local JSON-RPC server for tool execution.
- **Custom Slash Commands:** `/nf`, `/status`, `/sync` directly in Gemini CLI.
- **Native Intelligence:** Pre-packaged playbooks for architecture and operating laws.

## Guardian Gate

The safety pipeline in `guardian_engine.py`:
- AST (Abstract Syntax Tree) scan on every patch
- Baseline drift analysis against `upgrades/guardian_baseline.json`
- Syntax + linter checks (`py_compile` + `pyflakes`)
- Verification workflow: Verify → Log (`docs/logs/nina_update_log.md`) → Sync (`nina_sync.sh`)
- Single-instance locking via `jules_lock.txt` — prevents Jules and ninaflash from colliding

## Memory System

NINA's memory orchestrator in `core/memory.py`:
- **ChromaDB** — semantic/vector recall for episodic memory (what happened when)
- **facts.json** (`data/memory/facts.json`) — hardcoded personal identity anchor, prevents context drift

## Technical Stack

| Component | Detail |
|---|---|
| Runtime | Python 3.14, asyncio-based |
| OS | Ubuntu 26.04, systemd managed |
| Primary UI | Telegram bot (Gatekeeper) |
| CLI | `bin/nf` |
| Local Models | Ollama: qwen2.5:1.5b, qwen2.5:7b |
| Services | `nina.service`, `nina-dashboard.service` |
| Dev Stack | Perplexity + Jules + ninaflash (parallel) |

## Tool Quota Cascade (Daily)

| Tool | Model | Daily Quota | Reset |
|---|---|---|---|
| ninaflash (agy) | gemini-3-flash-preview | ~5h rolling | Rolling |
| Qwen Code CLI | Qwen3-Coder-480B | 2,000 req/day | Daily |
| Jules | Gemini 3.1 Pro | 100 tasks/day | Rolling 24h |
| Cursor Hobby | GPT-4o mini | 50 chat/month | Monthly |
| Ollama | Local | Unlimited | — |

Cascade order: `agy → Qwen Code → Jules (async) → Cursor → Ollama`

## Autonomous Development Loop

How NINA Builds Itself:
1. Perplexity drafts spec with precise requirements
2. Jules receives spec → builds async in cloud VM (no interaction after submit)
3. ninaflash handles urgent local fixes in parallel (separate worktree)
4. Jules opens PR when feature is complete
5. ninaflash runs Guardian lint/compile checks on the PR diff
6. ninaflash merges PR → runs `./nina_sync.sh` → deploys to systemd
7. Perplexity reviews result in new thread

## Project Structure

*Note: For the definitive inventory, canonical status, and lifecycle metadata of all governed files, see the [Repository Index](docs/space/nina_index.md).*

```
nina/
├── main.py                    # Entry point
├── guardian                   # Guardian watchdog script
├── guardian_engine.py         # Guardian AST + forensic engine (73KB)
├── healthcheck.py             # System health monitor
├── idleloop.py                # Background idle proposals
├── core/
│   ├── agent.py               # AgentLoop: THINK-PLAN-ACT + thermal guard
│   ├── config.py              # NinaConfig + rate limits
│   ├── memory.py              # ChromaDB + facts.json memory
│   ├── router.py              # HybridRouter V4 + CircuitBreaker
│   ├── nina.py                # NinaOS orchestrator
│   ├── capabilities.py        # Capability registry
│   └── hotreload.py           # Live config reload
├── tools/
│   ├── ninaflash.py             # Universe-Mode kernel (Nucleus: 1,001 functions)
│   ├── kernel/
│   │   ├── sector_000.py      # Neural Op-Code sectors (1,000 files)
│   │   └── sector_999.py      # 1,000,000 total op-codes
│   ├── browser.py             # Web browsing
│   ├── search.py              # Web search
│   ├── shell.py               # Shell execution (allowlisted)
│   ├── files.py               # File operations
│   ├── system.py              # System monitoring
│   ├── gputuner.py            # GPU management
│   ├── officemail.py          # EWS email (Exchange/NTLM)
│   └── upgradepipeline.py     # Self-upgrade system
├── interfaces/
│   ├── api.py                 # REST API (Phase 2)
│   └── telegram_interface.py  # Telegram bot + security gate
├── bin/
│   └── ninaflash                # ninaflash CLI entry point
├── crons/
│   ├── manager.py             # Cron job manager
│   └── backup_jobs.py         # Scheduled backups
├── dashboard/
│   └── nina-guardian.html     # Web dashboard
├── docs/
│   ├── ninaflash.md             # ninaflash architecture (NEW)
│   ├── router.md              # HybridRouter V4 deep-dive (NEW)
│   ├── guardian.md            # Guardian Gate pipeline (NEW)
│   ├── memory.md              # Memory system (NEW)
│   └── space/                 # Task tracker, backlog, context
├── upgrades/
│   └── guardian_baseline.json # Guardian integrity baseline
├── data/
│   └── memory/
│       └── facts.json         # Identity anchor (DO NOT MODIFY)
├── AGENTS.md                  # Agent operating law (canonical)
├── ARCHITECTURE.md            # System architecture overview (NEW)
├── CHANGELOG.md               # Version history
├── CONTRIBUTING.md            # Contribution guide
├── WORKFLOW.md                # Dev workflow
├── SECURITY.md                # Security policy
├── requirements.txt
├── jules_lock.txt             # Active file lock registry
├── nina.service               # systemd unit
└── nina-dashboard.service     # systemd dashboard unit
```

## Governance Status

NINA runs a strict, metadata-driven governance index. All agents and tools must consult this index.
- **[Operational Governance Dashboard](docs/space/nina_governance_dashboard.md)**: View live metrics, missing tests, and purge candidates.

- **Metadata Completeness:** 80.8% (Required: ≥75.0%)
- **Test Coverage Audit:** 32 Python files are missing dedicated tests (see `nf run validate-index` output).
## Installation

```bash
git clone https://github.com/aibony/nina.git
cd nina
./bin/install_governance.sh
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your keys
```

## Supported AI Providers

NINA integrates with multiple AI providers to ensure high availability and diverse model access. Routing is handled automatically by HybridRouter V4 with free-tier priority.

| Provider | Free Tier | Notes |
|---|---|---|
| Groq | ✅ | Fast inference, recommended default |
| Gemini | ✅ | Large context window |
| Cerebras | ✅ | High TPD allowance |
| DeepSeek | ✅ | Strong reasoning |
| Mistral | ✅ | 1 RPM on free tier |
| Together | ✅ | Many open models |
| Cohere | ✅ | Good for long context |
| Fireworks | ✅ | Fast open models |
| Perplexity | ✅ | Search-augmented |
| SambaNova | ✅ | High throughput |
| Hyperbolic | ✅ | Open model hosting |
| Novita | ✅ | Affordable inference |
| OpenRouter | ✅ | Multi-model gateway |
| xAI (Grok) | Paid | — |
| OpenAI | Paid | — |
| Pollinations | ✅ | Image generation |
| Chutes | ✅ | — |

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**M. Baizid Alam** · [onlybony@gmail.com](mailto:onlybony@gmail.com) · [github.com/aibony](https://github.com/aibony)
```

