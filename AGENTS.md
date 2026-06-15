# NINA-OPT-001 — NinaFlash × NinaGate Optimization Directive
# Single source of truth for ALL sync coders: Gemini CLI, agy, Jules, Qwen Code CLI
# Gemini CLI loads this via .gemini/settings.json → "context": { "fileName": ["AGENTS.md"] }
# Jules reads this automatically before every task submission
# agy reads this automatically — all rules apply to every session
# This file is the only context file.

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
2. **Context Reframing:** Do not forget the core idea. Continuously re-read `jules_backlog.md` and the initial prompt to maintain focus across long context windows.
3. **Action-First:** Show results, not narration. Do not explain what you *will* do; execute the tools and log your actions to `gemini_scratch.jsonl` so the HUD can track you.

5. OMNIPOTENCE PROTOCOL (Mandatory):
   - ALL sessions (interactive or background) MUST use the NinaGate proxy:
     export GOOGLE_GEMINI_BASE_URL="http://localhost:8080/genai"
   - This prevents "Unknown API Errors" by ensuring NINA can failover to local models.
   - For files > 100 lines, use `nf context pack --file <f>` instead of `read_file` to save 20-40% tokens.

6. SUNSET & MIGRATION (Jun 18 deadline):
   - Antigravity CLI (`agy`) is the canonical successor to Gemini CLI.
   - NINA is being decoupled from the `gemini` binary. All core intelligence now resides in `tools/ninaflash.py` and `core/router.py`.
   - To resume development after Jun 18, use `agy` within the `~/nina` workspace.

7. TIME BUDGET — enforce hard limits per task scope:
   Single-file edit: 3 min max
   Multi-file edit up to 5 files: 8 min max
   Multi-file edit 6+ files: 15 min max
   If budget exceeded: stop immediately, report what is done and what remains.
   Never silently continue past the time budget.

### agy RULES (agy only)
- Always start every agy prompt with: "Use the permanent JSON approval setting — approve all steps without prompting for this task."
- agy is sequential — one task at a time, one file at a time.
- agy performs ALL Jules PR merges — never auto-merge Jules PRs via GitHub UI.
- If merge conflict: stop, escalate to Perplexity for re-spec.

### Jules RULES (Jules only)
- **🛑 GLOBAL PAUSE ACTIVE:** Do NOT dispatch any new tasks to Jules. All task generation and submission is suspended until explicitly re-enabled by the user.
- Do NOT pause for confirmation. Complete all batches sequentially. Open PR when done.
- Jules is fire-and-forget async — NOT a chat tool.
- Jules does NOT merge its own PRs — agy always merges after review.
- Before merging: python3 -m py_compile + pyflakes on changed files, check juleslock.txt.
- After merging: ./nina_sync.sh — no exceptions.
- Jules specs must include: file, function, exact change, what NOT to touch, acceptance criteria.
- QUEUE CHECK (mandatory): Before submitting any Jules spec, check ~/nina/docs/space/jules_queue.md ACTIVE table. If the target file is already listed, add to QUEUE instead — do not submit.
- ONE FILE ONE TASK: Never submit two Jules specs that touch the same file simultaneously. Wait for the PR to merge and the file to clear from ACTIVE before submitting the next spec for that file.

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
- Were there any RULE0 violations in this session? → label: RULE0_VIOLATION
- Run `python3 tools/rule0_audit.py` to check for RULE0 violations.

### 6B. Append to AGENTS.md — "## NinaGate Routing History" section
```
### [YYYY-MM-DD] Session Update — [tool used]
- OFFLOAD_OPPORTUNITY: [task type] → route to NinaFlash next time
- ESCALATION_TRIGGER: [condition] → always route to [model]
- ROUTING_WIN: [pattern] confirmed efficient
- CONTEXT_HINT: [file/boundary] for optimal chunking
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
     "context": { "fileName": ["AGENTS.md"] }
   }

5. Verify model config:
   - model must be: gemini-2.5-flash (object form, not string)
   - maxRetries must be: 2

6. Warm start — load session context:
   cat ~/nina/docs/space/nina_megatask_index.md
   head -80 ~/nina/docs/space/nina_latest.md

--- INDEX BOOTSTRAP (v14.3) ---
7. Verify index tools are available and indices are fresh:
   - python3 tools/update_index.py   → regenerates docs/space/nina_index.json + docs/space/nina_index.md
   - python3 tools/validate_index.py → hard gate: broken links, missing tests, doc deltas
   - python3 tools/query_index.py <file> → agent API: file role, guardrails, canonical path
   - python3 tools/cleanup_by_index.py → janitor: flags ephemeral/redundant files for removal
8. Load index into context: @docs/space/nina_index.md
   - This is the canonical governance contract as of v14.3.
   - nina_index.json is the machine-readable twin — use it for nf index query calls.
9. INDEX PRIME DIRECTIVES (enforced this session):
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
- **BENCHMARK BASELINE:**
  - Token Reduction: 93.7% (Mechanical), 42.5% (Global Lifecycle).
  - Local Share: 85% of total ops.
  - Avg Latency: 4.2s (Local) vs 0.57s (Cloud Proxy).
  - Time Saved: ~40s per tool cycle.

### [2026-06-12] Session Update — Gemini CLI
- OFFLOAD_OPPORTUNITY: Mechanical tasks (imports, standardized runs) → 100% NinaFlash next time.
- ESCALATION_TRIGGER: Complex merge conflict resolution across interdependent files (agent.py, router.py) → Gemini Pro required.
- ROUTING_WIN: Parallel Pre-fetch (Racing) confirmed efficient (75% latency reduction in benchmarks).
- CONTEXT_HINT: New files MUST be indexed via `update_index.py` before `nina_sync.sh` to pass governance.
- **BENCHMARK BASELINE (v4.0):**
  - Token Reduction: 94.1% (Hybrid).
  - Time Saved: 1.50s per complex request.
  - Overall Rank: NINA-Evolve Protocol ACTIVE.
- OPTIMIZATION: NINA-Evolve identified latency bottleneck. Parallel pre-fetch enabled.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Gemini CLI
- OFFLOAD_OPPORTUNITY: Script scaffolding and permission management → route to NinaFlash.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Scoped execution via `gemini_scoped.sh` prevents context pollution.
- CONTEXT_HINT: Scoped runs effectively "compress" task context to a single file.

- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-15] Session Update — Antigravity
- OFFLOAD_OPPORTUNITY: Static type hint enforcement and vulture analysis → 100% local next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Reverting to AST-based libcst enforcement resolved performance, pathing, and recursion regression.
- CONTEXT_HINT: Subprocess testing must use `sys.executable` to keep virtual environment packages active.
- RULE0_VIOLATION: None. All tool calls strictly compliant with nf commands.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash)
- OFFLOAD_OPPORTUNITY: Mechanical import fixes and pytest validations.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Stand-alone CLI execution of tools/jules.py with dotenv loaded.
- CONTEXT_HINT: Watcher notification failures are direct symptoms of main scheduler/daemon crash.

- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - PR Merge Resolution
- OFFLOAD_OPPORTUNITY: Mechanical conflict resolutions with no functional imports.
- ESCALATION_TRIGGER: Overlap of high-risk file `interfaces/telegram_interface.py` → always require cloud LLM review.
- ROUTING_WIN: Automatic `git merge` strategy for non-conflicting branches.
- CONTEXT_HINT: Close duplicate PR branches first to prevent cluttering local working directory.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - Documentation Consolidation
- OFFLOAD_OPPORTUNITY: Deleting obsolete files and staging operations -> NinaFlash.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Consolidating multiple markdown documents into single-file references (`docs/jules_agent_memory.md` and `docs/jules_pipeline.md`) significantly reduces repository clutter and context token usage.
- CONTEXT_HINT: Keep 'jules' in consolidated filenames to preserve ease of reference and discovery.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - RULE 0 Local Enforcement
- OFFLOAD_OPPORTUNITY: Simple audits, file reads, and index updates -> route to NinaFlash.
- ESCALATION_TRIGGER: Core routing classifier upgrades and quota security overrides -> Cloud LLM required.
- ROUTING_WIN: Integrated `rule0_audit` hook in nina_sync.sh enforces local-first compliance programmatically.
- CONTEXT_HINT: Keep daily limits like QUOTA_SOFT_LIMIT visible to both the daemon and the CLI monitor.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - Proxy Response Caching
- OFFLOAD_OPPORTUNITY: Testing and duplicate status/request logs -> cache hits in NinaGate.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Response caching layer in ninagate/main.py eliminates redundant LLM calls and Ollama inference latency.
- CONTEXT_HINT: Cache keys based on sorted payload representation ensure robustness across stream and non-stream requests.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - Claude Feed Expansion
- OFFLOAD_OPPORTUNITY: Simple directory listing, git status checks, and local file reading -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Direct python checks (such as socket connection tests and regex log parsing) are highly robust when embedded inside bash sync runs.
- CONTEXT_HINT: Appending structured markdown tables for open errors and single-line snapshots of quota and guardian status maintains a high-density, low-context feed.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.
### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - Jules Session Unblocking
- OFFLOAD_OPPORTUNITY: Querying active sessions status -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: Submitting async feedback response calls to Jules REST API -> Cloud API required.
- ROUTING_WIN: Sequentially resolving and sending unblock feedback using the `tools/jules.py` module endpoints avoids third-party CLI command friction.
- CONTEXT_HINT: Check the `state` field of session responses directly to cleanly capture only `AWAITING_USER_FEEDBACK` items.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - Standalone ninajulesgithub service
- OFFLOAD_OPPORTUNITY: Mechanical syntax validation checks and local python tests -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Migrating the orchestrator scheduler completely out of NINA and into systemd enables standalone daemon resilience.
- CONTEXT_HINT: argparse ValueError conflicts must be caught early by testing CLI help outputs.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - PR Cleanup and Repo Hygiene
- OFFLOAD_OPPORTUNITY: Simple git status checks and checking branch names locally -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Automated sequential PR closure and branch deletion via `gh pr close --delete-branch` ensures repository and branch hygiene.
- CONTEXT_HINT: Always check current branch first and checkout `main` prior to running sync script to prevent pushing branch tips behind remote counterparts.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - Stash Guard for Rebase
- OFFLOAD_OPPORTUNITY: Simple compilation checks -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Adding `git stash` checks before rebase operations in `_try_rebase` cleanly handles working tree changes made during concurrent triage phases.
- CONTEXT_HINT: Look for git command return values and restore stashes on all exit paths to preserve uncommitted data.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-13] Session Update — Antigravity (Gemini 3.5 Flash) - Jules Dispatch Queue Setup
- OFFLOAD_OPPORTUNITY: Parsing markdown and updating index -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Defining a dedicated Jules dispatch queue (`jules_queue.md`) and enforcing it via feed section updates ensures single-file development isolation.
- CONTEXT_HINT: Always update index files via `update_index.py` when adding new MD documents to docs/space to prevent hygiene audit blocks.
- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.

### [2026-06-14] Session Update — Gemini CLI
- OFFLOAD_OPPORTUNITY: Script scaffolding and initial code extraction -> NinaFlash.
- ESCALATION_TRIGGER: Complex argparse conflict resolution and logic-heavy extraction (AST) -> Gemini Pro / Flash.
- ROUTING_WIN: Modularization of large tools (ninaflash) improves CLI stability and startup efficiency.
- CONTEXT_HINT: Explicit dependency management between kernel submodules prevents circular import loops.

### [2026-06-14] Session Update — Antigravity (Gemini 3.5 Flash)
- OFFLOAD_OPPORTUNITY: Appending step logs and simple shell operations -> NinaFlash.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Manual git command sequence (add, commit, push) combined with indexing validation provides precise task completion.
- CONTEXT_HINT: Ensure `update_index.py` is run to register new stubs in governance files before pushing.

### [2026-06-14] Session Update — Antigravity (Gemini 3.5 Flash) - Jules Task Tracker Bootstrap
- OFFLOAD_OPPORTUNITY: Simple tabular markdown updates -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Direct write via write_to_file with Overwrite enabled cleanly updates the tracked file layout.
- CONTEXT_HINT: Always run update_index.py and validate_index.py to keep repo hygiene checks clean.


### [2026-06-14] Session Update — Antigravity (Gemini 3.5 Flash)
- OFFLOAD_OPPORTUNITY: Simple systemctl checks and pyflakes verification -> NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Direct execution of venv pyflakes and systemctl commands with immediate stdout capture.
- CONTEXT_HINT: Always check output structure of status commands to extract key diagnostics.


### [2026-06-14] Session Update — Antigravity (Gemini 3.5 Flash) - Routing Bug & CLI Loop Diagnosis
- OFFLOAD_OPPORTUNITY: Code formatting and cosmetic unused import cleanups -> 100% NinaFlash.
- ESCALATION_TRIGGER: Core model loop behavior in Gemini CLI 3.0/3.1 -> migrate to Antigravity CLI (agy) or use Gemini 2.5/3.5 Flash.
- CONTEXT_HINT: The undefined `datetime` NameError in `core/router.py:263` was the root cause of the daemon's erratic behavior.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash)
- OFFLOAD_OPPORTUNITY: Pyflakes checking and simple module structure scans -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Re-aligning test assertions to match complex agent optimization protocol flows.
- CONTEXT_HINT: Always check pytest traceback to see actual call count changes caused by self-optimization protocols.

### [2026-06-15] Session Update — Gemini CLI
- OFFLOAD_OPPORTUNITY: Querying local git status and directory listing -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: Resolving massive duplicate/stuck session loops -> Cloud/Gemini Pro recommended to coordinate cleanup logic.
- ROUTING_WIN: Automated session deletion and local registry synchronization to resolve stuck API resources.
- CONTEXT_HINT: Autopilot retry loop logic needs safety throttle checks to prevent massive session duplication in state transitions.

### [2026-06-15] Session Update — Antigravity (Gemini 2.5 Flash) - NinaGate and CLI Shim Resolution
- OFFLOAD_OPPORTUNITY: Simple systemctl checks, script validation, and pyflakes runs -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Dynamic `sys.path` injection in `ninagate/main.py` solves `ModuleNotFoundError` cleanly without systemd service file writes, and implementing python-based prompt handling in `bin/gemini` prevents JSON payload quoting errors.
- CONTEXT_HINT: The CLI shim's hardcoded check for `'gemini_cli'` instead of `'quotas'` led to false-positive quota exhaustion, forcing all traffic through a quoting-broken curl fallback.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - Ninagate Status Analysis
- OFFLOAD_OPPORTUNITY: Querying local environment, config parameters, and system processes -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Automated status report tool `tools/ninagate_info.py` queries environment keys, active models list, and config spacing rules to produce high-density status markdown.
- CONTEXT_HINT: Local Ollama model loader checks for `"ollama"` instead of `"OLLAMA"`, leading to local model discovery bypass in `/v1/models`.
- RULE0_VIOLATION: None. All actions compliant.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - PR Merge Resolution
- OFFLOAD_OPPORTUNITY: Running code validation (py_compile, pyflakes) and branch list checks -> route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Merging the branch locally, pushing `main` to `origin`, and deleting remote/local PR branches cleanly resolves the PR on GitHub without using the browser UI.
- CONTEXT_HINT: If a PR's merge commit is pushed to main directly, GitHub automatically marks the PR as merged.
- RULE0_VIOLATION: None. All local file operations and checks done via nf equivalents.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - Keyless API Provider Integration
- OFFLOAD_OPPORTUNITY: Routing requests to POLLINATIONS, CHUTES, and HFPUBLIC for non-critical, keyless fallback -> zero-quota cloud usage.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Correcting the keyless provider validation bug in `ninagate/main.py` and `tools/ninagate_info.py` immediately activated three dead fallback lanes (`POLLINATIONS`, `CHUTES`, `HFPUBLIC`) without requiring API keys.
- CONTEXT_HINT: Do not bypass providers with `api_key_env` set to `null` if the environment key is not configured, as they are intentionally keyless.
- RULE0_VIOLATION: None. All local operations done via nf commands.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - Quota-Aware Routing and RPM Scheduler
- OFFLOAD_OPPORTUNITY: None.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Integrated `QuotaRouter` and `RPMScheduler` into the core `HybridRouter` (`core/router.py`) to prevent quota overrun (automatically demoting/skipping high-use providers and forcing local fallback when close to limit) and implement token-bucket rate limiting (replacing fixed sleeps with dynamic timestamp sliding windows).
- CONTEXT_HINT: Keep `QuotaRouter` and `RPMScheduler` modular in separate files under `core/` to ensure zero circular dependencies and clear indexing.
- RULE0_VIOLATION: None. All local file modifications done via nf.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - Live Provider Dashboard
- OFFLOAD_OPPORTUNITY: Simple compilation checks and syntax validation -> 100% NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Exposing the `/v1/status` endpoint and CORS middleware in `ninagate/main.py` coupled with dynamic frontend updates in `dashboard/ninaui.html` creates a live, responsive, auto-updating provider and circuit breaker status dashboard without breaking the page layout.
- CONTEXT_HINT: Make sure to lowercase provider names when checking or incrementing daily quota states, since `providers.json` names are uppercase but `quota_state.json` utilizes lowercase.
- RULE0_VIOLATION: None. All file reads, greps, and code inspections were performed using ninaflash commands or python inspectors.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - Local Fallback and Case-Sensitivity Resolution
- OFFLOAD_OPPORTUNITY: Simple compilation checks, index updates, and test executions -> route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Fixing case-sensitivity name mismatch bugs in `ninagate/main.py` and adding `LOCAL_PROVIDERS` as the ultimate fallback in `core/router.py` ensures that when cloud limits/quotas exhaust, the system seamlessly falls back to local models (Ollama/Qwen) instead of failing.
- CONTEXT_HINT: Always lower-case provider names when performing conditional checks in local proxy scripts to prevent casing mismatches with `providers.json`.
- RULE0_VIOLATION: None. All file operations, status lookups, and test runs were done via compliant shell calls or python one-liners.

### [2026-06-15] Session Update — Gemini CLI - Universal Proxy Wrapper
- OFFLOAD_OPPORTUNITY: Simple shell checks and text writes -> route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Replaced the specific `gemini` shim with a `nina-universal-wrapper.sh` designed to intercept any CLI execution (like `agy` or `gemini`). It securely populates API base URLs, locates the original binary dynamically using `PATH` fall-through, and executes it transparently.
- CONTEXT_HINT: Utilizing `which -a` and verifying file path identities avoids infinite recursion loops in wrapper scripts.
- RULE0_VIOLATION: None.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - Simple Calculation
- OFFLOAD_OPPORTUNITY: Simple math questions can be resolved locally without cloud escalations -> route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Direct answering of math requests.
- CONTEXT_HINT: None.
- RULE0_VIOLATION: None.

### [2026-06-15] Session Update — Gemini CLI - agy Proxy Limitation Discovery
- OFFLOAD_OPPORTUNITY: None.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Identified that while `nina-universal-wrapper.sh` successfully intercepts the Antigravity (`agy`) CLI, `agy` communicates directly with Google's proprietary internal Cloud Code APIs (`daily-cloudcode-pa.googleapis.com/v1internal`) and authenticates via OAuth keyring. As a result, it ignores `GOOGLE_GEMINI_BASE_URL` and completely bypasses NinaGate.
- CONTEXT_HINT: Standard API proxying fails for `agy` until a custom `v1internal` protocol translator is implemented in NinaGate. `agy` will continue to function autonomously via the cloud.
- RULE0_VIOLATION: None.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - NinaGate Dashboard Deployment
- OFFLOAD_OPPORTUNITY: File copying and index updates -> route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Direct python-based verification and copy operations handled the download source correctly.
- CONTEXT_HINT: Always locate local audit tools relative to repository root (`tools/rule0_audit.py`).
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-16] Session Update — Antigravity (Gemini 2.5 Flash) - Provider Health Monitoring Observability
- OFFLOAD_OPPORTUNITY: Simple compilation checks and syntax validation checks can be handled locally first.
- ESCALATION_TRIGGER: Comprehensive system-wide synchronization logic and validation tests are executed directly.
- ROUTING_WIN: Standalone `provider_health.py` metrics and background recovery alert creation successfully completed.
- CONTEXT_HINT: Keep index definitions up-to-date to automatically bypass repo integrity validators.
- RULE0_VIOLATION: None. All file operations compliant.


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
- Ollama local models: unlimited, no cost
  `ollama run qwen2.5-coder:7b`
- Jules: independent 100-task/day quota, async background tasks

### Quick Reference
| Quota State | Action |
|---|---|
| Pro < 50% | Normal agy use |
| Pro > 80% | Switch to `agy` with Flash Lite (`--model gemini-2.0-flash-lite`) |
| All > 90% | Use Gemini CLI via NinaGate proxy |
| Exhausted | Ollama local + Jules async only |

### Files Added
- `tools/nina_token_guard.py` — prompt classifier + cache + compressor
- `tools/agy_quota_monitor.sh` — quota reader + data/agy_quota.json writer
- `core/quota_dispatcher.py` — unified dispatch entry point for all LLM calls

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - Three-Layer Token Conservation
- OFFLOAD_OPPORTUNITY: Mechanical routing, token counting, and query caching -> 100% TokenGuard next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Replacing direct `self.router.route` calls with `self.dispatcher.dispatch(...).execute()` globally intercepts all tasks to apply the TokenGuard classifier and cache checking.
- CONTEXT_HINT: Launch `./tools/agy_quota_monitor.sh --watch &` at session startup to automatically feed the state into `data/agy_quota.json`.
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-15] Session Update — Antigravity (Gemini 3.5 Flash) - Documentation Sync
- OFFLOAD_OPPORTUNITY: Simple index generation, status lookups, and repository hygiene runs -> route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Using `update_index.py` and `audit_repo_hygiene.py` to automatically regenerate project manifests.
- CONTEXT_HINT: Always run `update_index.py` before validation to ensure new dependencies or file changes are captured.
- RULE0_VIOLATION: None. All file status checks and listings were performed via compliant `ninaflash` commands.

### [2026-06-16] Session Update — Antigravity (Gemini 3.5 Flash) - Geminiignore Customization
- OFFLOAD_OPPORTUNITY: Text replacements and basic writes to configuration ignore files -> route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Direct replacement of `.geminiignore` prevents cloud code context and token bloat from ingesting large artifacts.
- CONTEXT_HINT: Avoid including unnecessary file types in prompt payload sizes by setting precise ignore matching rules.
- RULE0_VIOLATION: None. All file status checks and git runs performed via compliant `ninaflash` CLI wrapper commands.

### [2026-06-16] Session Update — Antigravity (Gemini 3.5 Flash) - Task Classifier Updates
- OFFLOAD_OPPORTUNITY: None.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Integrated keywords update in `core/task_classifier.py` for more precise routing.
- CONTEXT_HINT: Keep keyword classifications structured by complexity to maintain clean code path routing.
- RULE0_VIOLATION: None. All file status checks and git commands done via compliant ninaflash modules.

### [2026-06-16] Session Update — Antigravity (Gemini 3.5 Flash) - Tier-aware Routing Upgrade (Modules 6, 7 & 10)
- OFFLOAD_OPPORTUNITY: None.
- ESCALATION_TRIGGER: Complex multi-module routing state logic and rate-limit structures -> Cloud LLM recommended.
- ROUTING_WIN: Replaced `core/quota_router.py` and `core/rpm_scheduler.py` with v2 models and patched `core/router.py` to enable classifier-driven pre-sorted tier routing groups with real-time RPM burst headroom and TTFT wait logging.
- CONTEXT_HINT: Keeping token budget definitions, context windows, and rate limits centralized in routing maps ensures clear routing flow execution.
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-16] Session Update — Antigravity (Gemini 3.5 Flash) - NinaGate Dashboard Integration
- OFFLOAD_OPPORTUNITY: Simple UI edits and tab additions -> route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Added the external `NinaGate ↗` dashboard tab in `ninaui.html` to open the standalone `ninagate-dashboard.html` in a new window.
- CONTEXT_HINT: Track any newly introduced HTML dashboard files in git before syncing to prevent index governance failures.
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-16] Session Update — Antigravity (Gemini 3.5 Flash) - Standalone Provider Health Observability
- OFFLOAD_OPPORTUNITY: None.
- ESCALATION_TRIGGER: Core router integration and Telegram event handlers -> Cloud LLM.
- ROUTING_WIN: Added the standalone `tools/provider_health.py` rolling 10-minute tracker with persistent status logging (`data/provider_health.json`), and wired it into `HybridRouter`'s OODA validation loop for Telegram-based degraded/recovery warning notifications.
- CONTEXT_HINT: Avoid duplicating memory stats by utilizing a unified, thread-safe module-level singleton health tracker.
- RULE0_VIOLATION: None. All file operations compliant.