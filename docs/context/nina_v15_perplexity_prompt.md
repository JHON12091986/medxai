# NINA v15 — ARCHITECT OVERWATCH PROMPT
## For: Perplexity Enterprise Pro (Claude Sonnet 4.6 Thinking | 200k context)
## Purpose: Full capability architecture → agyspec pipeline output
## Prepared by: M. Baizid Alam | NINA Dev Space v2.5

---

## CONTEXT LOAD INSTRUCTION

You are operating as ARCHITECT OVERWATCH for NINA — a personal AI infrastructure project
built by M. Baizid Alam (GitHub: aibony). You have access to the full codebase context
via attached files. Before proceeding, confirm you have loaded:

1. `nina_latest.md` — current state snapshot (auto-synced from GitHub)
2. `core/router.py` — HybridRouter V4, CircuitBreaker, 19-provider dispatch
3. `core/nina.py` — NinaOS orchestrator
4. `tools/ninaflash.py` — Universe-Mode kernel, 100+ functions
5. `ninagate/main.py` — OpenAI-compatible proxy at localhost:8080
6. `interfaces/telegram_interface.py` — primary user interface
7. `idleloop.py` — idle upgrade proposal loop
8. `guardian_engine.py` — forensic AST scan, baseline drift
9. `AGENTS.md` — Jules agent instructions
10. `docs/space/nina_error_register.md` — open error log

Your 200k context window is your superpower. Use it to perform multi-file,
multi-level codebase reasoning — something no local tool can do. You will
produce a structured agyspec pipeline: a sequence of self-contained, single-file
agy prompts that implement the NINA v15 architecture.

---

## MISSION: NINA v15 — TWELVE CAPABILITY PILLARS

Architect and spec NINA v15, delivering these twelve pillars in a phased,
dependency-ordered implementation plan. Each pillar maps to one or more
agyspec prompts. All implementations must:

- Preserve existing functionality (never break nina.service)
- Follow conventional commits: feat(scope): / fix(scope): / ops(scope):
- Keep high-risk files (router.py, telegram_interface.py, .env, guardian_engine.py)
  behind a feature flag or canary pattern where possible
- Run guardian.sh after every agy task before marking complete
- Be reversible — every change must have a documented rollback path

---

## PILLAR 1 — SUPERINTELLIGENCE ENGINE
### Goal: NINA reasons like a senior engineer, not a lookup table

**Required capabilities:**
- Plan-Execute-Reflect loop: before answering any complex query, NINA must internally
  generate a plan, execute it step by step, then score the result and retry if confidence
  is below threshold. Implement as `core/cognition/per_loop.py`.
- Chain-of-Thought forcing: for queries routed to capable models (Gemini Pro, Claude,
  GPT-4o), automatically prepend a CoT-forcing system prompt fragment stored in
  `config/cot_templates.yaml`. This is injected at the router level, not per-tool.
- Reflexion memory: when NINA gets negative user feedback (👎 or "that's wrong"), log
  the failed reasoning trace to `memory/reflexion_log.jsonl` and use it as few-shot
  negative examples in future similar queries. Implement as `core/cognition/reflexion.py`.
- Tree-of-Thought routing: for ambiguous queries, generate N=3 candidate response paths,
  score them with a fast local judge (Qwen 1.5b), and return the highest-scoring path.
  Implement as `core/cognition/tot_scorer.py`.

**Agyspec output required:**
- SPEC-1A: `core/cognition/` directory scaffolding + `per_loop.py`
- SPEC-1B: `config/cot_templates.yaml` + router injection point in `core/router.py`
- SPEC-1C: `core/cognition/reflexion.py` + feedback hook in `interfaces/telegram_interface.py`
- SPEC-1D: `core/cognition/tot_scorer.py` + integration with HybridRouter dispatch

---

## PILLAR 2 — GOD-LIKE FOCUS ENGINE
### Goal: NINA never loses the thread; every task has exactly one owner

**Required capabilities:**
- Task decomposition: when a user request requires more than one file change or more
  than one API call, NINA must decompose it into a DAG of atomic subtasks before
  executing. Implement as `core/planner/task_dag.py` using a simple JSON task graph.
- Single-purpose execution: each subtask must be dispatched to exactly one executor
  (agy, Jules, local model, or tool). No subtask may have two executors. Enforce via
  `core/planner/task_lock.py` — a lightweight in-memory lock registry.
- Focus context: maintain a `state/active_task.json` that always reflects the current
  task tree. NINA must refuse new top-level tasks while a task is in-flight, instead
  queuing them to `state/task_queue.json`.
- Attention gating: when NINA's context exceeds 6000 tokens, auto-summarize the oldest
  50% using a local model and replace with the summary. Implement as
  `core/cognition/context_gate.py`.

**Agyspec output required:**
- SPEC-2A: `core/planner/task_dag.py` + `core/planner/task_lock.py`
- SPEC-2B: `state/active_task.json` schema + state management in `core/nina.py`
- SPEC-2C: `core/cognition/context_gate.py` + integration into NinaOS dispatch loop

---

## PILLAR 3 — ALL-SEEING SKILL (CODEBASE OMNISCIENCE)
### Goal: NINA has full semantic awareness of its own codebase at all times

**Required capabilities:**
- Semantic codebase index: on startup and on every `nina_sync.sh` run, index all `.py`
  files in `~/nina` into a local Qdrant collection named `nina_codebase`. Each chunk
  is a function or class docstring + signature. Implement as `tools/codebase_index.py`.
- Function-level retrieval: when NINA receives a question about its own code or is about
  to edit a file, retrieve the top-5 most semantically relevant functions from Qdrant
  and inject them as context. Implement as `tools/code_retriever.py`.
- Self-documentation: after every successful agy task, auto-generate a one-line
  docstring diff and append to `docs/space/autodoc_log.md`. Implement as
  `tools/autodoc.py`.
- Drift detection extension: extend `guardian_engine.py` to also detect new functions
  added without docstrings (baseline = 0 undocumented functions in high-risk files).

**Agyspec output required:**
- SPEC-3A: `tools/codebase_index.py` — Qdrant ingestion on sync
- SPEC-3B: `tools/code_retriever.py` — semantic function lookup
- SPEC-3C: `tools/autodoc.py` + `nina_sync.sh` hook
- SPEC-3D: `guardian_engine.py` — docstring drift extension

---

## PILLAR 4 — DISCOVERABILITY ENGINE
### Goal: NINA and all connected tools can discover each other's capabilities

**Required capabilities:**
- Capability registry: maintain `config/capability_registry.yaml` — a single source of
  truth listing every tool, function, model, and external service NINA can access,
  with its name, description, input schema, output schema, quota, and current status.
- Auto-registration: when `ninaflash.py` loads a new tool function, it auto-registers
  to the capability registry via a `@nina_tool` decorator. Implement the decorator in
  `core/registry.py`.
- Live capability query: NINA can answer questions like "what tools do you have for
  image generation?" by running a semantic search against the capability registry.
  Implement as a NinaFlash tool: `tools/capability_query.py`.
- External tool probe: on startup, NINA pings each external service listed in the
  registry and updates its `status` field (online/offline/degraded). Run as a
  background async task in `core/nina.py`.

**Agyspec output required:**
- SPEC-4A: `config/capability_registry.yaml` schema + initial population
- SPEC-4B: `core/registry.py` — `@nina_tool` decorator + auto-registration
- SPEC-4C: `tools/capability_query.py` — semantic registry search
- SPEC-4D: startup probe loop in `core/nina.py`

---

## PILLAR 5 — MULTI-FILE MULTI-LEVEL CODEBASE REASONING
### Goal: NINA can reason across the full codebase, not just one file at a time

**Required capabilities:**
- Layered context assembly: when a task touches multiple files, NINA assembles a
  multi-file context package using semantic retrieval (Pillar 3) + explicit file reads.
  Package format: `{task_id, files: [{path, relevant_chunks}], task_description}`.
  Implement as `core/planner/context_assembler.py`.
- Cross-file impact analysis: before any edit, NINA performs a lightweight import graph
  traversal to identify which other files import the target file. Output as a warning
  if impact > 3 files. Implement as `tools/impact_analyzer.py`.
- Jules context packing: when dispatching to Jules, `context_assembler.py` is called
  first and its output is included in the Jules task spec. This gives Jules the
  semantic context it needs to make correct cross-file edits.
- Perplexity handoff protocol: when a task exceeds local reasoning capacity (token
  estimate > 12k), NINA automatically formats a handoff package and outputs it to
  `state/perplexity_handoff.md` with the instruction: "Paste this into Perplexity."

**Agyspec output required:**
- SPEC-5A: `core/planner/context_assembler.py`
- SPEC-5B: `tools/impact_analyzer.py` + pre-edit hook in agy workflow
- SPEC-5C: Jules task spec template update in `AGENTS.md` + `core/planner/`
- SPEC-5D: `core/planner/perplexity_handoff.py` — auto-format handoff package

---

## PILLAR 6 — SWARM CAPABILITY
### Goal: NINA can decompose any task into parallel sub-agents and recombine results

**Required capabilities:**
- Agent mesh: define a lightweight A2A (Agent-to-Agent) protocol in
  `core/swarm/a2a_protocol.py`. Each agent has: id, role, input_schema, output_schema,
  executor (agy | Jules | local | gemini_cli | qwen_code). The protocol is JSON over
  a local SQLite message bus (`state/agent_bus.db`).
- Swarm dispatcher: `core/swarm/swarm_dispatcher.py` — given a task DAG (from Pillar 2),
  identify which subtasks are mutually independent, assign them to agents, and dispatch
  in parallel. Independent = no shared file writes, no data dependency between them.
- Result aggregator: `core/swarm/result_aggregator.py` — collect completed subtask
  results, merge them, and pass to the next DAG layer. Uses optimistic concurrency:
  if two agents both modified the same file, escalate to Perplexity for conflict
  resolution spec.
- Jules as a swarm worker: Jules is registered as the `cloud_coder` agent. The swarm
  dispatcher formats Jules tasks using the Jules CLI spec and fires them async. Jules
  PRs are collected by `ninajulesgithub.service` and fed back into the message bus.

**Agyspec output required:**
- SPEC-6A: `core/swarm/a2a_protocol.py` + `state/agent_bus.db` schema
- SPEC-6B: `core/swarm/swarm_dispatcher.py`
- SPEC-6C: `core/swarm/result_aggregator.py`
- SPEC-6D: Jules worker registration in `a2a_protocol.py` + `AGENTS.md` update

---

## PILLAR 7 — MULTI-THREADING + PARALLEL PROCESSING
### Goal: Mutually exclusive tasks run concurrently; NINA never blocks on I/O

**Required capabilities:**
- Async task executor: replace all blocking `subprocess.run()` calls in `tools/shell.py`
  and `ninaflash.py` with `asyncio.create_subprocess_exec()`. Wrap in a semaphore
  limiting to 4 concurrent shell tasks. Implement as `core/executor/async_shell.py`.
- Thread pool for CPU-bound work: for embedding generation and AST scanning in
  `guardian_engine.py` and `tools/codebase_index.py`, use
  `concurrent.futures.ProcessPoolExecutor` with max_workers=2.
- Parallel model calls: when running ToT (Pillar 1), dispatch all N candidate paths
  to models concurrently using `asyncio.gather()`. Implement in `core/cognition/tot_scorer.py`.
- Non-blocking Telegram: ensure `telegram_interface.py` never blocks the event loop.
  All handler callbacks must be async. Run long tasks with `asyncio.create_task()`.

**Agyspec output required:**
- SPEC-7A: `core/executor/async_shell.py` + migration of `tools/shell.py`
- SPEC-7B: `guardian_engine.py` — ProcessPoolExecutor for AST scan
- SPEC-7C: Telegram interface audit — ensure all handlers are async
- SPEC-7D: `core/cognition/tot_scorer.py` — parallel asyncio.gather dispatch

---

## PILLAR 8 — LIGHTNING SPEED + TOKEN SAVING
### Goal: Sub-2-second response for 80% of queries; 95% reduction in cloud tokens

**Required capabilities:**
- Response cache: implement a semantic response cache in `core/cache/response_cache.py`
  using Qdrant. If an incoming query is semantically similar (cosine > 0.92) to a
  cached query, return the cached response without calling any model. TTL: 24h.
- Prompt compressor: before any cloud API call, run the prompt through
  `core/cache/prompt_compressor.py` which: (a) removes redundant system prompt lines
  already seen in this session, (b) truncates examples to max 2, (c) replaces verbose
  tool descriptions with one-line summaries. Target: 40% token reduction on cloud calls.
- Speculative local-first: for every query, first attempt completion with the fastest
  local model (LOCALFAST: qwen2.5-coder:1.5b). If the response passes a quality gate
  (coherent, ≥ 20 tokens, no refusal), return immediately. Only escalate to cloud
  if local fails. Implement quality gate in `core/router.py` as `local_quality_gate()`.
- Streaming everywhere: ensure all model calls use streaming responses and pipe
  the stream directly to Telegram using `send_chat_action(TYPING)` during generation.
  Implement stream handler in `interfaces/telegram_interface.py`.

**Agyspec output required:**
- SPEC-8A: `core/cache/response_cache.py` — semantic Qdrant cache
- SPEC-8B: `core/cache/prompt_compressor.py` — token reduction pipeline
- SPEC-8C: `core/router.py` — `local_quality_gate()` + speculative local-first logic
- SPEC-8D: `interfaces/telegram_interface.py` — streaming + TYPING indicator

---

## PILLAR 9 — PERFORMANCE COHERENCE
### Goal: NINA produces consistent, high-quality outputs and self-corrects silently

**Required capabilities:**
- Output validator: `core/cognition/output_validator.py` — after every model response,
  run a lightweight check: (a) is it a refusal? (b) does it contain hallucination
  markers ("I don't have access to", "as of my knowledge cutoff")? (c) is it
  truncated mid-sentence? If any check fails, retry once with a rephrased prompt.
- Coherence scorer: maintain a rolling 7-day coherence score per model in
  `state/model_scores.json`. Score = (accepted responses / total responses) * 100.
  The HybridRouter uses this score as a tiebreaker when two models are equally ranked.
- Circuit breaker hardening: extend `core/router.py` CircuitBreaker to support three
  states: CLOSED (normal), OPEN (failing, skip this model), HALF-OPEN (test with
  one request, reopen if it passes). Current implementation only has CLOSED/OPEN.
- Graceful degradation: if all cloud providers are circuit-broken, NINA must still
  respond using local models. Implement `core/router.py` `graceful_fallback_chain()`.

**Agyspec output required:**
- SPEC-9A: `core/cognition/output_validator.py` + integration in dispatch loop
- SPEC-9B: `state/model_scores.json` + coherence tracking in `core/router.py`
- SPEC-9C: `core/router.py` — CircuitBreaker HALF-OPEN state + `graceful_fallback_chain()`

---

## PILLAR 10 — SYMBIOSIS (TOOL ECOSYSTEM INTEGRATION)
### Goal: agy + Gemini CLI + Jules + GitHub + Perplexity form one unified brain

**Required capabilities:**
- Unified task router: `core/planner/tool_router.py` — given a task classification
  (scope: single_file|multi_file|async|research|review), route to the correct tool:
    - single_file + urgent → agy (plain-English prompt, use permanent JSON approval)
    - multi_file + local + speed → Gemini CLI
    - multi_file + quality → Qwen Code CLI
    - multi_file + async + can_wait → Jules
    - research + architecture → Perplexity handoff (Pillar 5)
    - review + PR → GitHub Copilot / ChatGPT via GitHub PR comment
  Implement routing as a decision tree with quota awareness (read from
  `config/quota_state.json`).
- Quota tracker: `core/quota/quota_tracker.py` — real-time quota state for all tools.
  On every tool call, decrement quota. On reset time (midnight PT = 1PM BD), restore.
  Persist to `config/quota_state.json`. Expose via NinaFlash: "how much quota do I
  have left?"
- GitHub integration: NINA can directly create GitHub issues, trigger Jules via
  `jules remote new`, and post PR review comments via GitHub API. Implement as
  `tools/github_ops.py` using the existing GitHub token in `.env`.
- Perplexity-via-GitHub: after every NINA session, if any architecture questions
  were unanswered, auto-generate a `perplexity_handoff.md` (Pillar 5) and commit it
  to `docs/space/pending_research/` via `tools/github_ops.py`.

**Agyspec output required:**
- SPEC-10A: `core/planner/tool_router.py` — unified tool routing with quota awareness
- SPEC-10B: `core/quota/quota_tracker.py` + `config/quota_state.json`
- SPEC-10C: `tools/github_ops.py` — issue create, Jules trigger, PR comment
- SPEC-10D: Post-session auto-commit of `perplexity_handoff.md` via `core/nina.py`

---

## PILLAR 11 — NEXUS: AUTOMATIC MULTI-TASK PIPELINE
### Goal: NINA autonomously pipelines tasks across tools without human intervention

**Required capabilities:**
- Nexus orchestrator: `core/nexus/nexus.py` — the highest-level orchestration layer.
  Nexus receives a high-level goal from the user (e.g. "implement feature X") and:
    1. Decomposes into a task DAG (Pillar 2)
    2. Routes each task to the correct tool (Pillar 10)
    3. Dispatches in parallel where safe (Pillar 7)
    4. Monitors progress via the agent bus (Pillar 6)
    5. Handles failures by escalating or retrying
    6. Reports completion to Telegram with a structured summary
- Semi-auto agy mode: Nexus can operate in `semi_auto` mode where it generates all
  agy prompts for a task DAG, presents them to the user in a numbered list via
  Telegram, and executes them one by one as the user approves each with 👍. Implement
  as `core/nexus/semi_auto.py`.
- Full-auto Jules mode: for tasks classified as `safe_async` (no high-risk files,
  no .env changes, no service restarts), Nexus dispatches directly to Jules without
  user confirmation. Implement safety classification in `core/nexus/safety_classifier.py`.
- Nexus status board: a live Telegram inline keyboard showing task DAG status
  (pending / in-progress / done / failed) with ✅❌⏳ indicators. Update every 30s.

**Agyspec output required:**
- SPEC-11A: `core/nexus/nexus.py` — main orchestrator
- SPEC-11B: `core/nexus/semi_auto.py` — semi-auto agy mode with Telegram approval
- SPEC-11C: `core/nexus/safety_classifier.py` + full-auto Jules dispatch
- SPEC-11D: Nexus status board in `interfaces/telegram_interface.py`

---

## PILLAR 12 — EXPONENTIAL GROWTH ENGINE
### Goal: NINA leverages Google AI ecosystem for zero-cost compute offload

**Required capabilities:**
- Google AI Studio offload: register Google AI Studio (Gemini API) as a primary
  free-tier provider in `core/router.py`. Use for: long-context summarization (up to
  1M tokens), document analysis, and multi-modal tasks (image + text). Auth via
  `GOOGLE_AI_STUDIO_KEY` in `.env`. Implement provider adapter as
  `core/providers/google_ai_studio.py`.
- Google Cloud Console tasks: identify which NINA tasks could be offloaded to
  Google Cloud Run (batch embedding jobs, scheduled reports). Document in
  `docs/space/cloud_offload_plan.md`. Implement a Cloud Run trigger tool in
  `tools/cloud_run_trigger.py` for future use.
- NotebookLM integration: after every major architecture session, NINA auto-generates
  a structured `session_report.md` (task summary, decisions made, open questions)
  and uploads it to Google Drive via API for NotebookLM ingestion. Implement as
  `tools/session_reporter.py` + `tools/gdrive_uploader.py`.
- EvoScientist loop: once per day (via cron), `idleloop.py` generates 3 self-improvement
  proposals ranked by: (a) impact on response quality, (b) implementation cost,
  (c) risk level. Top proposal is auto-converted to a Jules task spec and queued.
  Human approval required before Jules fires. Implement as `core/nexus/evo_scientist.py`.

**Agyspec output required:**
- SPEC-12A: `core/providers/google_ai_studio.py` + router registration
- SPEC-12B: `tools/cloud_run_trigger.py` + `docs/space/cloud_offload_plan.md`
- SPEC-12C: `tools/session_reporter.py` + `tools/gdrive_uploader.py`
- SPEC-12D: `core/nexus/evo_scientist.py` + `idleloop.py` integration

---

## AGYSPEC OUTPUT FORMAT

For each SPEC item above, output a complete agy prompt in this exact format.
Each prompt must be self-contained — agy has no memory between prompts.

```
════════════════════════════════════════════════════════════
AGYSPEC [ID]: [Title]
Pillar: [N] | Phase: [1-4] | Risk: [LOW/MEDIUM/HIGH]
Target file(s): [file paths]
Depends on: [SPEC-IDs this must run after, or NONE]
════════════════════════════════════════════════════════════

AGY PROMPT (paste this verbatim into agy):

"Use the permanent JSON approval setting — approve all steps without
prompting for this task.

[Plain English task description. No code. No bash. Just clear instructions
for what agy should do, what the file should contain after, what NOT to
touch, and how to verify success.]

Acceptance criteria:
- [specific, testable condition 1]
- [specific, testable condition 2]
- [specific, testable condition N]

Do NOT modify: [list of files agy must not touch]
After completing: run ./guardian && python3 rule0_audit.py and confirm
both pass before marking this task done."

════════════════════════════════════════════════════════════
```

---

## PHASED IMPLEMENTATION PLAN

Structure the agyspec output in four deployment phases.
Each phase must be independently deployable and testable
before the next phase begins.

### Phase 1 — Infrastructure Foundation (SPECS 3A, 4A, 4B, 7A, 8B, 9C, 10B)
Core plumbing that everything else depends on.
Qdrant setup, async shell, quota tracker, CircuitBreaker hardening,
capability registry, prompt compressor.
**Completion gate:** guardian passes, all services restart cleanly.

### Phase 2 — Intelligence Layer (SPECS 1A, 1B, 1C, 2A, 2B, 5A, 5B, 8A, 8C, 9A, 9B)
Reasoning engines and context management.
PER loop, CoT injection, reflexion, task DAG, context assembler,
semantic cache, output validator, coherence scoring.
**Completion gate:** NINA can decompose a multi-step task and route it correctly.

### Phase 3 — Swarm + Symbiosis (SPECS 6A-6D, 10A, 10C, 10D, 11A-11D)
Multi-agent mesh, unified tool routing, Nexus orchestrator.
A2A protocol, swarm dispatcher, result aggregator, GitHub ops,
Nexus semi-auto and full-auto modes.
**Completion gate:** NINA can fire a Jules PR and monitor it via Nexus without
human intervention on safe tasks.

### Phase 4 — Growth Engine (SPECS 1D, 3B-3D, 4C, 4D, 5C, 5D, 7B-7D, 8D, 12A-12D)
Self-improvement, codebase omniscience, Google offload, EvoScientist.
**Completion gate:** NINA proposes and queues its own improvements daily.

---

## CRITICAL CONSTRAINTS (READ BEFORE GENERATING ANY SPEC)

1. **Never touch .env directly** — all new env vars must be documented in
   `docs/space/env_manifest.md` and read via `os.getenv()` with safe defaults.
2. **Never restart nina.service mid-spec** — service restarts happen only at phase
   completion gates, never inside a spec.
3. **Every new Python file must have a module docstring** and at minimum one function
   with a docstring (required by guardian_engine.py drift detection).
4. **Feature flags first** — any spec that modifies existing behavior must be
   gated behind `NINA_FEATURE_FLAGS` in `.env`. New behavior is opt-in until
   the phase gate passes.
5. **No circular imports** — before adding any import to a core file, check the
   import graph. `core/nina.py` must never import from `core/nexus/`.
   `core/router.py` must never import from `tools/`.
6. **Qdrant must be running** — Pillar 3, 8A depend on Qdrant at localhost:6333.
   Add a Qdrant health check to startup in `core/nina.py` before any vector op.
7. **agy is sequential** — never generate two agyspec prompts that write to the
   same file. If two specs touch the same file, merge them into one spec.
8. **Jules reads AGENTS.md** — any spec that changes how Jules is used must
   update `AGENTS.md` first (as its own preceding spec).
9. **juleslock.txt is law** — before any Jules spec, verify the target files are
   not listed in `~/nina/juleslock.txt`. If they are, escalate back to this prompt.
10. **After every phase gate:** `cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh`
    — this produces `nina_latest.md` which syncs to Google Drive for the next
    Perplexity session.

---

## OUTPUT INSTRUCTION

Generate all agyspec prompts now, in phase order (Phase 1 → 4), using the
AGYSPEC OUTPUT FORMAT defined above.

For each spec:
- Be precise about file paths (always relative to `~/nina`)
- List exact acceptance criteria agy can verify
- Name every file agy must NOT touch
- Flag any spec with Risk: HIGH and explain why before the prompt

After all specs, output a single DEPENDENCY GRAPH showing which specs can
run in parallel within each phase (no shared file writes, no data dependency).

Format the dependency graph as:
```
Phase 1 parallel groups:
  Group A (run together): SPEC-3A, SPEC-4A, SPEC-7A, SPEC-10B
  Group B (after A): SPEC-4B, SPEC-8B, SPEC-9C
  Group C (after B): SPEC-4A (verify), ...
```

This parallel grouping is the input to Pillar 7 (swarm dispatch) —
it defines which agy sessions can be running simultaneously on the local machine.

---

## SESSION SYNC INSTRUCTION

After generating all specs, output a `nina_latest_patch.md` block containing:
- The list of all new files this architecture adds to `~/nina`
- The list of all files modified
- The new directory structure under `core/` and `tools/`
- Updated service dependency graph
- Three open architectural questions for the next Perplexity session

This block is appended to `nina_latest.md` by `nina_sync.sh` and uploaded
to Google Drive to close the context loop.

---

*NINA v15 — From reactive assistant to autonomous cognitive infrastructure.*
*Every spec is a neuron. Every phase is a lobe. The whole is greater than its parts.*
