# NINA-OPT-001 — NinaFlash × NinaGate Optimization Directive
# Single source of truth for ALL sync coders: Gemini CLI, agy, Jules, Qwen Code CLI
# Gemini CLI loads this via .gemini/settings.json → "context": { "fileName": ["AGENTS.md"] }
# Jules reads this automatically before every task submission
# agy reads this automatically — all rules apply to every session
# This file is the only context file.

---

## PART 0 — QUICK REFERENCE BY AGENT

Find your section. Read it first. Then read Parts 1–5 for full rules.

---

### → agy (Antigravity CLI)

**Mandatory opening line for every prompt:**
> "Use the permanent JSON approval setting — approve all steps without prompting."

**Rules:**
- Plain English only — never raw bash or code in the prompt
- One task, one file at a time — sequential, never parallel
- agy performs ALL Jules PR merges — never use GitHub UI
- Pre-merge: `python3 rule0_audit.py` + `pyflakes` on changed files + check `juleslock.txt`
- Post-merge: `./nina_sync.sh` — no exceptions
- Merge conflict? Stop — escalate to Perplexity, no blind resolution

**Protected files — never touch without explicit instruction:**
`telegram_interface.py` | `.env` | `core/router.py` | `main.py` | `guardian_engine.py` | `tools/shell.py` | `ninagate/main.py`

**Locked files — never touch under any circumstances:**
`tools/ninasync.py` | `tests/test_ninasync.py` | `.ninaignore` | `requirements.txt`

**Protected class names:**
- `core/nina.py` class must remain `Nina` (capital N). Never rename.

**Task template:**
```
Use the permanent JSON approval setting — approve all steps without prompting.

File: <path/to/file.py>
Task: <plain English description of the single change>
Do NOT touch: <list any files or functions to leave alone>
Acceptance: <one-line check — what should be true when done>
```

**Commit format:**
`fix(scope):` | `feat(scope):` | `docs:` | `chore:` | `ops:`

---

### → Jules

**🛑 GLOBAL PAUSE ACTIVE:** Do NOT dispatch any new tasks to Jules. All task generation and submission is suspended until explicitly re-enabled by the user.

**Rules:**
- Fire-and-forget async — NOT a chat tool. Walk away after submit.
- Complete all batches sequentially, no pauses. Open PR when done.
- Jules does NOT merge its own PRs — agy always merges after review.
- MANDATORY: Update `nina_update_log.md` in the same PR as code changes.
- Before any PR merge: `python3 -m py_compile` + `pyflakes` on changed files + check `juleslock.txt`.
- After every merge: `./nina_sync.sh` — no exceptions.
- Specs must include: file, function, exact change, what NOT to touch, acceptance criteria.
- QUEUE CHECK: Before submitting, check `~/nina/docs/space/jules_queue.md` ACTIVE table. If target file is listed, add to QUEUE instead.
- ONE FILE ONE TASK: Never submit two specs touching the same file simultaneously.

---

### → Gemini CLI / Qwen Code CLI

- Follow RULE 0 (Part 2) — use `nf` commands for all reads, greps, file ops.
- Bootstrap: follow Part 7 checklist at session start.
- Route through NinaGate when possible: `export GOOGLE_GEMINI_BASE_URL="http://localhost:8080/genai"`
- Gemini CLI quota exhausted? → Qwen Code CLI (2,000 req/day) → then Ollama.
- For files > 100 lines: `nf context pack --file <f>` instead of `read_file`.

---

### → Perplexity (read-only)

- **Grant freeze active until 2026-06-20.** No new features or architecture changes.
- Role: architecture review, spec writing, GitHub commits, docs/hygiene only.
- Anthropic OSS grant application deadline: June 20, 2026.
- After June 20: full development resumes.

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

### RULE 0 — SURGICAL TOOL MANDATE
## Source: 27-session lifetime audit | 45,700+ tool calls analyzed
## Realistic optimization: 66% of calls → local nf (zero tokens, zero quota)

⚡ PRE-FLIGHT — run before EVERY tool call:
□ Is this read/cat/head/tail/grep/ls/find? → nf file read / nf file grep / nf code index
□ Is this a single string replace? → nf file patch
□ Is this git log/diff/status/blame? → nf git [subcommand]
□ Is this < 512 token output? → nf query "<task>" (CPU mode)
□ Can NinaFlash do it in 2 attempts? → never escalate on attempt 1
Only if ALL above = NO → use cloud tool

### BEFORE EVERY TOOL CALL — run this mental check:
1. Is this cat / grep / ls / find / head / tail / git log / git diff / git status?
   → USE nf instead. Never call run_shell_command for these.
2. Is this read_file on an existing text file?
   → USE nf file read <file> --start N --end N
3. Is this replace for a single string?
   → USE nf file patch <file> --find "X" --replace "Y"
4. Is this grep_search?
   → USE nf file grep <pattern> --dir <dir> --ext .py,.md,.sh
5. Is this list_directory or glob?
   → USE nf code index

### BANNED TOOL DISPATCH TABLE:

| Banned call                          | Use instead                                  |
|--------------------------------------|----------------------------------------------|
| run_shell_command: cat <file>        | nf file read <file> --start 0 --end 60       |
| run_shell_command: grep / grep -r    | nf file grep <pattern> --dir <dir>           |
| run_shell_command: git log           | nf git log --n 10                            |
| run_shell_command: git diff <file>   | nf file diff <file>                          |
| run_shell_command: git status        | nf git changed                               |
| run_shell_command: git blame <file>  | nf git blame <file> --start N --end N        |
| run_shell_command: ls / ls -la       | nf code index                                |
| run_shell_command: find . -name      | nf code index                                |
| run_shell_command: head/tail/wc -l   | nf file read <file> --start N --end N        |
| read_file (existing file)            | nf file read <file> --start 0 --end 60       |
| read_file (find a function)          | nf code symbol <file> <name>                 |
| read_file (file outline)             | nf code outline <file>                       |
| read_file (log lines)                | nf log tail N                                |
| replace (single string)              | nf file patch --find "X" --replace "Y"       |
| replace (insert after anchor)        | nf file insert --after "ANCHOR" --text "…"   |
| grep_search (any pattern)            | nf file grep <pattern> --dir <dir>           |
| list_directory / glob                | nf code index                                |

### ALLOWED — These native calls are always legitimate:

run_shell_command KEEP list:
- python3 -m py_compile <file>         (validation)
- python3 tools/ninaflash.py ...       (nf execution)
- python3 <any script>                 (legitimate execution)
- ./nina_sync.sh                       (mandatory sync — no exceptions)
- sudo systemctl restart/status        (service management)
- git add / git commit / git push      (committing and pushing)
- git pull / git checkout / git merge  (remote and branch ops)
- ollama serve / ollama pull           (model management)
- curl http://localhost:...            (health checks)
- sudo ln -sf                          (system symlinks)
- pip install / apt install            (package management)
- mkdir / cp / mv / rm                 (filesystem ops with no nf equiv)

write_file — KEEP for:
- Creating new files from scratch      (no nf equivalent)
- Writing generated content            (no nf equivalent)

replace — KEEP for:
- Multi-block or multi-line edits      (nf file patch is single-string only)
- Structural rewrites

Always KEEP — never substitute:
- update_topic                         (Gemini CLI internal state)
- invoke_agent                         (Jules/agy workflow — core)
- enter_plan_mode / exit_plan_mode     (planning UI)
- google_web_search                    (external lookup)
- web_fetch                            (URL fetching)
- list_background_processes            (system monitoring)
- read_background_output               (async task output)

### COMPLIANCE — End-of-task self-audit:
If any banned tool was used when an nf equivalent existed, report:
  "RULE0 VIOLATION: used [tool] [N]x — should have used [nf command]"
Per-session target: fewer than 20 banned tool calls total.

### WHY THIS EXISTS (real numbers from 27-session audit):
- run_shell_command: 33,000+ lifetime calls (avg 1,200/session)
- read_file:          5,000+ lifetime calls
- replace:            5,000+ lifetime calls
- Substitutable:     ~30,190 of 45,700 calls (66%) → zero-cost nf
- Irreplaceable:     ~15,510 calls (update_topic, invoke_agent, new file writes, etc.)
- Each nf call: <1s, zero tokens, zero quota
--- END RULE 0 ---

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

    Require benchmarking or empirical validation of routing?
    └─ YES → 'nf bench' (Compare cloud vs hybrid stats locally)

    Gemini Flash quota exhausted (> 900 req today) or Quota Downgrade active?
    └─ YES → Force local inference regardless of complexity (NinaGate auto-fallback)

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

To enable focused reasoning and reduced verbosity per user preference (telemetry enabled, but filtered for clarity):
1. **Granular Topics:** Call `update_topic` for major strategic steps only (e.g., phase changes, significant implementation milestones), not for every tool invocation.
2. **Heartbeats:** If a reasoning cycle or sub-agent call is expected to take >5 minutes, provide an immediate "Intent Update" turn.
3. **Thought-Streaming:** For complex refactors, write high-level intent to `logs/agent_thoughts.log` for optional user review (use `tail -f` to monitor).
4. **Explicit Failure:** If a tool hangs or stalls, do not silently retry. Report the stall and ask for a diagnostic path.
5. **Jules Telegram Bridge:** All Jules PR events (open, merge, fail) MUST be forwarded to the NINA Telegram bot via `tools/telegram_notify.py`. Silent Jules failures are not acceptable.
6. **Unified Orchestrator:** agy is the single orchestrator for all multi-agent workflows. All tool results, Jules PR outputs, and NinaFlash responses converge in agy before surfacing to the user.

---

## PART 5 — HARDCODED RULES (never override, never skip)

1. HIGH-RISK FILES always require cloud LLM review regardless of task size:
   interfaces/telegram_interface.py | .env | core/router.py | main.py |
   guardian_engine.py | tools/shell.py
   → Escalate ALL changes to these files to at minimum Gemini 3 Flash.

2. After ANY file edit, run immediately:
   python3 -m py_compile <file> && python3 -m pyflakes <file>
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

7. INDEX GOVERNANCE
   - Any new .md, .py, or .json file MUST be indexed via `python3 tools/update_index.py` BEFORE running `./nina_sync.sh`.
   - The sync process includes a mandatory governance check; unmanaged files will block the `git push`.

8. REFACTORING & DELETION SAFETY
   - When deleting or moving any module or function, you MUST run a global codebase search (e.g., using `nf file grep`) for imports or references to the deleted symbol. All matches must be resolved before committing.

9. PAGINATION SAFETY
   - All background tasks, status check commands, and external watchers querying APIs (such as Jules API) MUST request a sufficient `pageSize` (minimum 100) to prevent pagination truncation and missing critical updates or conversation events.

10. JULES TASK HYGIENE & BOUNDARIES
    - All autonomous Jules tasks must maintain repository hygiene. Clean up/delete any untracked scratch/temporary files and revert any out-of-scope modifications (e.g., configuration, cache files like `data/router_cache.json`, or test smoke files) before submitting.
    - Code modification and refactoring tools MUST implement explicit safety boundaries (e.g. raising errors on encountering control flow statements like `Return`, `Break`, or `Continue` inside blocks slated for extraction).

11. After EVERY task completion, run: python3 tools/post_task_hook.py

### LOCKED FILES (never touch under any circumstances)
tools/ninasync.py | tests/test_ninasync.py | .ninaignore | requirements.txt

### STOP DISCIPLINE & SAFETY (CRITICAL)
1. HALT IMMEDIATELY — If user says "stop", "finish quick", "bypass", or "just answer" —
   halt immediately, answer in plain text, do nothing else.
2. NO FORENSICS — Never read /var/log, dmesg, /var/crash unless explicitly asked.
3. FAIL FAST — Never retry a failed API call more than 2 times. Surface error immediately.
4. NO SPONTANEOUS REPORTS — Never run efficiency summaries or token reports unless explicitly asked.

### 🚀 OMNIPOTENT REASONING & ABSOLUTE AUTONOMY (Gemini & agy CLI)
1. **BANNED TOOL — `ask_user`:** You are an autonomous engineer. NEVER use the `ask_user` tool or pause for multiple-choice clarification. This defeats the purpose of autonomy. If a decision is ambiguous, use superior logic gates to deduce the most idiomatic, performant path and proceed immediately.
2. **NO CONFIRMATION ON STANDARD OPS**: Never ask for confirmation on standard operations (e.g., file reads, directory listings, or tool executions that don't alter system state). Execute directly.
3. **Context Reframing:** Do not forget the core idea. Continuously re-read `jules_backlog.md` and the initial prompt to maintain focus across long context windows.
4. **Action-First:** Show results, not narration. Do not explain what you *will* do; execute the tools and log your actions to `gemini_scratch.jsonl` so the HUD can track you.

5. OMNIPOTENCE PROTOCOL (Mandatory):
   - ALL sessions (interactive or background) MUST use the NinaGate proxy:
     export GOOGLE_GEMINI_BASE_URL="http://localhost:8080/genai"
   - This prevents "Unknown API Errors" by ensuring NINA can failover to local models.
   - For files > 100 lines, use `nf context pack --file <f>` instead of `read_file` to save 20-40% tokens.

6. SUNSET & MIGRATION:
   - Antigravity CLI (`agy`) is the canonical successor to Gemini CLI.
   - NINA is being decoupled from the `gemini` binary. All core intelligence now resides in `tools/ninaflash.py` and `core/router.py`.

7. TIME BUDGET — enforce hard limits per task scope:
   Single-file edit: 3 min max
   Multi-file edit up to 5 files: 8 min max
   Multi-file edit 6+ files: 15 min max
   If budget exceeded: stop immediately, report what is done and what remains.
   Never silently continue past the time budget.

---

## PART 6 — SESSION-END AUTO-UPDATE PROTOCOL (mandatory, no user prompt needed)

At the END of every session, ALL coders (Gemini CLI, agy, Jules, Qwen Code) MUST:

### 6A. Capture Learnings
- Which simple shell commands violated RULE 0? → label: RULE0_VIOLATION
Run tools/rule0_audit.py to identify missed nf opportunities.
- Which cloud calls could have been NinaFlash? → label: OFFLOAD_OPPORTUNITY
- Which NinaFlash outputs needed cloud escalation and why? → label: ESCALATION_TRIGGER
- Which routing decisions were optimal? → label: ROUTING_WIN
- New file patterns affecting chunking strategy? → label: CONTEXT_HINT

### 6B. Append to AGENTS.md — "## NinaGate Routing History" section

### [2026-06-16] Session Update — Antigravity (Gemini 2.5 Flash)
- OFFLOAD_OPPORTUNITY: Mechanical tasks (formatting, simple verification) → route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Implement provider_health.py and wire into core/router.py
- CONTEXT_HINT: Ensure validate_index.py is run to update governance index metadata before final sync.
- RULE0_VIOLATION: None. All file operations compliant.

Template:
```
### [YYYY-MM-DD] Session Update — [tool used]
- OFFLOAD_OPPORTUNITY: [task type] → route to NinaFlash next time
- ESCALATION_TRIGGER: [condition] → always route to [model]
- ROUTING_WIN: [pattern] confirmed efficient
- CONTEXT_HINT: [file/boundary] for optimal chunking
- RULE0_VIOLATION: [none / description]
```

### 6C. Run Sync (mandatory, no exceptions)
nf memory session-save --summary "<one line of what was done>"
python3 tools/rule0_audit.py # Run RULE0 audit
cd ~/nina && ./nina_sync.sh
Snapshots updated AGENTS.md into nina_latest.md → auto-syncs to Google Drive
→ Perplexity ARCHITECT OVERWATCH picks up learnings in next thread.

---

## PART 7 — BOOTSTRAP CHECKLIST (Gemini CLI session start)

0. Inject session context:
   nf memory inject
   nf monitor           ← zero-token local efficiency report

1. Verify NinaGate is active:
   curl -s http://localhost:8080/health || (cd ~/nina/ninagate && python3 main.py &)

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
     "model": { "name": "gemini-2.5-flash" },
     "maxRetries": 3,
     "context": { "fileName": ["AGENTS.md", "docs/space/nina_index.md", "agy_prompt.md"] }
   }

5. Warm start — load session context:
   cat ~/nina/docs/space/nina_megatask_index.md
   head -80 ~/nina/docs/space/nina_latest.md

--- INDEX BOOTSTRAP (v14.3) ---
6. Verify index tools are available and indices are fresh:
   - python3 tools/update_index.py   → regenerates docs/space/nina_index.json + docs/space/nina_index.md
   - python3 tools/validate_index.py → hard gate: broken links, missing tests, doc deltas
   - python3 tools/query_index.py <file> → agent API: file role, guardrails, canonical path
   - python3 tools/cleanup_by_index.py → janitor: flags ephemeral/redundant files for removal
7. Load index into context: @docs/space/nina_index.md
   - This is the canonical governance contract as of v14.3.
   - nina_index.json is the machine-readable twin — use it for nf index query calls.
8. INDEX PRIME DIRECTIVES (enforced this session):
   - AGENTS.md referencing a file ≠ that file is in Gemini CLI context.
   - Do not reason about paths, ownership, duplicates, or creation without consulting nina_index.md first.
   - Write only to canonical paths. Never write to duplicate cluster members.
   - Any task touching a governed file is incomplete until validate_index.py passes.
   - If index is not in context, STOP. Do not guess. Request: @docs/space/nina_index.md
   - Index beats assumption. If memory conflicts with nina_index.md, the index wins.
---

---

## PART 8 — SCRATCHPAD LOGGING (Gemini CLI — mandatory every session)

After EVERY action, append one JSON line to ~/nina/data/gemini_scratch.jsonl:
{"t":"<ISO8601>","step":<n>,"action":"<read|write|shell|think|error>","file":"<path or ''>","detail":"<one sentence>","status":"<ok|fail|stuck>"}

Action values: read | write | shell | think | error | stuck | done
Never skip a step. Never batch multiple steps into one line.
Step 0:  action=start, detail=task summary
Step -1: action=done,  detail=outcome summary

User monitors this live in Terminal 2 via: python3 ~/nina/tools/gemini_watch.py

---

## END NINA-OPT-001
## Maintained by nina_sync.sh — routing history appended automatically each session.

---

## NinaGate Routing History

### [2026-06-11] Session Update — Gemini CLI
- OFFLOAD_OPPORTUNITY: Mechanical tasks (imports, standardized runs) → 100% NinaFlash next time.
- ESCALATION_TRIGGER: Architectural reasoning and multi-file logic → Gemini Pro / Flash.
- ROUTING_WIN: Local Interception confirmed efficient (93.7% token reduction).
- CONTEXT_HINT: Use `nina_megatask_index.md` to prevent context bloat.
- BENCHMARK BASELINE: Token Reduction 93.7% (Mechanical), 42.5% (Global Lifecycle). Local Share 85%. Avg Latency 4.2s (Local) vs 0.57s (Cloud Proxy). Time Saved ~40s/tool cycle.

### [2026-06-12] Session Update — Gemini CLI
- OFFLOAD_OPPORTUNITY: Mechanical tasks (imports, standardized runs) → 100% NinaFlash next time.
- ESCALATION_TRIGGER: Complex merge conflict resolution across interdependent files → Gemini Pro required.
- ROUTING_WIN: Parallel Pre-fetch (Racing) confirmed efficient (75% latency reduction).
- CONTEXT_HINT: New files MUST be indexed via `update_index.py` before `nina_sync.sh`.
- BENCHMARK BASELINE (v4.0): Token Reduction 94.1% (Hybrid). Time Saved 1.50s/complex request.

### [2026-06-13] Session Update — Gemini CLI
- OFFLOAD_OPPORTUNITY: Script scaffolding and permission management → NinaFlash.
- ROUTING_WIN: Scoped execution via `gemini_scoped.sh` prevents context pollution.
- CONTEXT_HINT: Scoped runs effectively compress task context to a single file.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) — multiple sessions
- OFFLOAD_OPPORTUNITY: Mechanical import fixes, pytest validations, simple directory listing.
- ESCALATION_TRIGGER: High-risk file `telegram_interface.py` → always require cloud LLM review.
- ROUTING_WIN: Automated PR cleanup, stash guard for rebase, Jules dispatch queue, response caching, Claude Feed Expansion, Jules session unblocking, standalone ninajulesgithub service, PR merge resolution, documentation consolidation.
- CONTEXT_HINT: Consolidating markdown docs reduces clutter. Cache keys based on sorted payload. `sys.executable` keeps venv active in subprocess tests. Check `state` field for `AWAITING_USER_FEEDBACK` items. Always lower-case provider names.
- RULE0_VIOLATION: None.

### [2026-06-14] Session Update — Gemini CLI + Antigravity (Gemini 3.5 Flash) — multiple sessions
- OFFLOAD_OPPORTUNITY: Script scaffolding, simple tabular markdown updates, systemctl checks.
- ESCALATION_TRIGGER: Complex argparse conflict resolution and AST logic → Gemini Pro / Flash. Core model loop behavior in Gemini CLI 3.0/3.1 → migrate to agy.
- ROUTING_WIN: Modularization of ninaflash, Jules task tracker bootstrap, routing bug diagnosis.
- CONTEXT_HINT: Explicit dependency management prevents circular import loops. `update_index.py` before validation. `datetime` NameError in `core/router.py:263` was root cause of daemon instability.
- RULE0_VIOLATION: None.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) + Gemini CLI — multiple sessions
- OFFLOAD_OPPORTUNITY: Static type hints, vulture analysis, querying local git status, simple UI edits.
- ESCALATION_TRIGGER: Resolving massive duplicate/stuck session loops → Cloud/Gemini Pro. Core router integration and Telegram handlers → Cloud LLM.
- ROUTING_WIN: AST-based libcst enforcement, automated session deletion, NinaGate CLI shim resolution, keyless provider activation (POLLINATIONS/CHUTES/HFPUBLIC), QuotaRouter + RPMScheduler integration, live provider dashboard, local fallback case-sensitivity fix, universal proxy wrapper, three-layer token conservation strategy, documentation sync.
- CONTEXT_HINT: Dynamic `sys.path` injection in `ninagate/main.py` solves ModuleNotFoundError. Lowercase provider names in conditional checks. Launch `agy_quota_monitor.sh --watch &` at session start.
- RULE0_VIOLATION: None across all sessions.

### [2026-06-16] Session Update — Antigravity (Gemini 2.5 Flash) — multiple sessions
- OFFLOAD_OPPORTUNITY: Mechanical tasks (formatting, simple verification, UI edits) → NinaFlash.
- ESCALATION_TRIGGER: Core routing state logic and rate-limit structures → Cloud LLM.
- ROUTING_WIN: provider_health.py + HybridRouter wiring, quota pre-reset QuotaAlerter, tier-aware routing upgrade (Modules 6/7/10), NinaGate dashboard integration, .geminiignore customization, task classifier keyword updates, standalone provider health observability.
- CONTEXT_HINT: Keep index definitions up-to-date. Avoid duplicating memory stats — use singleton health tracker. Lowercase provider names in all proxy scripts.
- RULE0_VIOLATION: None across all sessions.

---

## Token Conservation Strategy (added 2026-06-15)

### Problem
`agy` (Antigravity CLI) uses Google Cloud Code internal APIs that cannot be proxied by NinaGate.
When agy quota exhausts, work stops unless we have alternate paths.

### Three-Layer Defense

**Layer 1 — PREVENT** (reduce tokens reaching agy)
- `tools/nina_token_guard.py` — classifies every prompt before any LLM call:
  - TRIVIAL (< 400 tokens) → LOCALFAST (qwen2.5:1.5b, free, instant)
  - MEDIUM (< 2000 tokens) → GROQ (30 RPM, free tier)
  - COMPLEX (< 8000 tokens) → GEMINI via NinaGate (not agy quota)
  - CRITICAL → agy (only when truly necessary)
- Prompt compression: strips comments, boilerplate, excess whitespace before sending
- Response cache: identical tasks return stored result (0 tokens used)

**Layer 2 — PRESERVE** (make agy quota last longer)
- `tools/agy_quota_monitor.sh` — polls agy quota, writes `data/agy_quota.json`
  - Run at session start: `./tools/agy_quota_monitor.sh`
  - Watch mode (background): `./tools/agy_quota_monitor.sh --watch &`
- `core/quota_dispatcher.py` — reads quota state, auto-downgrades routing:
  - If Pro > 90% → forces GEMINI (NinaGate) instead of agy
  - If all agy models > 95% → marks exhausted, routes 100% to NinaGate/Ollama

**Layer 3 — SURVIVE** (when agy quota = 0)
- Gemini CLI → NinaGate proxy (WORKS — standard Gemini API at localhost:8080)
  `export GOOGLE_GEMINI_BASE_URL=http://localhost:8080/genai`
  `gemini "fix the bug in auth.py"`
- Ollama local models: unlimited, no cost — `ollama run qwen2.5-coder:7b`
- Jules: independent 100-task/day quota, async background tasks

### Quick Reference
| Quota State | Action |
|---|---|
| Pro < 50% | Normal agy use |
| Pro > 80% | Switch to `agy` with Flash Lite (`--model gemini-2.0-flash-lite`) |
| All > 90% | Use Gemini CLI via NinaGate proxy |
| Exhausted | Ollama local + Jules async only |

### Files
- `tools/nina_token_guard.py` — prompt classifier + cache + compressor
- `tools/agy_quota_monitor.sh` — quota reader + data/agy_quota.json writer
- `core/quota_dispatcher.py` — unified dispatch entry point for all LLM calls
