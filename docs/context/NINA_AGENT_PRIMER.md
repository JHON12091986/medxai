# NINA Agent Primer — Read This Before Any Task
## updated: 2026-06-24

## Identity
Repo: ~/nina | Owner: M. Baizid Alam (GitHub: aibony)
AGM, BASIC Bank PLC, Dhaka, Bangladesh
Stack: Python 3.14.4 | Ubuntu 26.04 LTS | ASUS VivoBook X530FN
Perplexity = ARCHITECT | agy = EXECUTOR | Jules = ASYNC PR AGENT

## Session Start — Always Do This First (Dynamic Discovery)
To maintain coherence, avoid redundancies, and stay in tip-top shape, every agent must perform a rapid self-discovery scan upon startup:
1. **System Health Check**: Read `nina_context_graph.json` → inspect `summary.health` and `summary.top_priority` to get the instant health snapshot.
2. **Scan the Error Register**: Read `docs/space/nina_error_register.md` to identify all `OPEN` bugs or system regressions.
3. **Inspect the Backlog**: Read `docs/space/jules_backlog.md` to locate `READY` tasks and outstanding specs.
4. **Safety & Policy Check**: Read `docs/context/NINA_RULES.md` for safety limits and commit syntax guidelines.
5. **Read Before Writing**: Always read any target file fully from top to bottom before performing any edits.
6. **Recent History Check**: Read the last 5 entries in `docs/context/nina_session_log.md` to understand the live state, what is in-flight, and what to skip.

---

## The Perpetual Cognitive Cycle — OODA Self-Improvement
NINA operates as a self-hosted, self-directed, and perpetually self-improving entity. Rather than relying on hardcoded static roadmaps, agents must execute tasks using the **recursive OODA (Observe-Orient-Decide-Act) loop**:

1. **OBSERVE (Intelligence Gathering)**:
   - Query the git tree (`git status`, `git log`, `git diff`) and local index registers to understand the delta between `origin/main` and `main`.
   - Read the logs (`telemetry.jsonl` or system journals) to locate transient errors or degradation.
   - Look up documentation, APIs, and modern paradigms (like Kimi-style parallel swarm architectures, Groq speed-burst caching, or Python 3.14 free-threaded GIL removal) to identify opportunities for upgrade.

2. **ORIENT (Context Framing & Synthesis)**:
   - Check file-specific metadata inside `docs/space/nina_index.json` to verify test requirements, file risks, and module ownership.
   - Identify active locks in `juleslock.txt` or active background services (`nina.service`, `ninagate.service`, `ninajulesgithub.service`, `nina-dashboard.service`) to prevent collision or service disruption.

3. **DECIDE (Parallel Decomposition & Planning)**:
   - Decompose high-level goals into independent, mutually-exclusive parallel task trees.
   - Map each sub-task to the most suitable model tier (e.g., Gemini 2.5 Pro for deep logic, Groq or Cerebras for high-frequency sub-tasks, local Ollama for zero-cost formatting).

4. **ACT (Autonomous Execution & Feedback Gate)**:
   - Execute edits surgically, running validation checks immediately after each change.
   - Pass completed task outputs through an intelligent **Feedback Gate** to verify syntactic correctness, adherence to safety rules, and performance integrity before final merge.

---

## Swarm Coordination & Governance Rules

### 1. Lock Enforcement & Collision Avoidance
- Check `juleslock.txt` on every run. If files you need to modify are locked by an active Jules session, you MUST halt or wait for the PR to merge.
- Manual pushes that touch files currently locked by active Jules sessions are blocked by the `pre-push` git hook. Never attempt to force-bypass locks unless explicitly instructed.

### 2. Autonomous Action Rules (Zero-Redundancy Contract)
- **NEVER present multiple-choice questions** or prompt for confirmation on standard file operations (read, write, edit) or harmless tool calls. Redundant interactive dialog defeats autonomy.
- **Always make the single best-informed design decision** based on local codebase conventions and owner guidelines. Proceed with confidence.
- Only pause or prompt the user for:
  - Destructive operations (deleting data stores, dropping database tables).
  - Provisioning critical credentials or private tokens.
  - Resolving logically contradictory requirements that cannot be resolved via code pattern analysis.

### 3. Progressive Commits (Step-by-Step Security)
- Break complex overhauls into a sequence of small, atomic, self-contained commits.
- Commit each module or sub-task **1-by-1** to avoid hitting context limits, reducing the risk of mid-session API failures or context pollution.

---

## Code Quality & CI/CD Everywhere

### 1. Rigid Verification Workflow
Every Python edit must be validated locally before it is committed or synced:
```bash
# After editing <file>:
python3 -m py_compile <file> && pyflakes <file>
```
If errors, syntax warnings, or import issues are flagged, repair them immediately.

### 2. Test Execution
Before merging or syncing, execute the test suite inside the virtual environment to ensure 100% regression-free stability:
```bash
./venv/bin/pytest
```

### 3. Post-Merge Synchronization
Once commits are integrated or a branch is merged, always run the synchronizer to re-index, clean up, update docs, and trigger backups:
```bash
cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh
```

---

## Core Architecture

| Component | Path | Core Role |
|---|---|---|
| **NinaOS Orchestrator** | `core/nina.py` | Top-level runtime coordinator and system entry point. |
| **HybridRouter V4** | `core/router.py` | Intelligent provider routing, tiered failovers, and parallel race lookups. |
| **OODA Task Planner** | `core/task_planner.py` | Recursive decomposition of high-level goals into DAG task trees. |
| **Swarm Engine** | `core/swarm_engine.py` | Event-driven parallel execution pool utilizing async semaphores. |
| **Reasoning Gates** | `core/reasoning.py` | Claude-inspired cognitive evaluation layers (Constitutional, Sycophancy, Contradiction). |
| **NinaGate Proxy** | `ninagate/main.py` | OpenAI-compatible local proxy (port 8080) with local-first Ollama health checks. |
| **ninaMCP Relay Bus** | `ninagate/mcp_relay.py` | 3-tier MCP relay: Perplexity → GitHub MCP → ninagate → local services. Bridges cloud agent actions to on-device execution without SSH. |
| **Live Telemetry** | `core/observability.py` | Shared state telemetry engine writing to `telemetry.jsonl`. |
| **TUI Dashboard** | `tools/nina_dashboard.py` | Non-blocking telemetry visualizer reading from `telemetry.jsonl`. |
| **Jules Watcher** | `ninajulesgithub.py` | Background agent listening for GitHub PR triggers and dispatch queues. |
| **Guardian AST Engine** | `guardian_engine.py` | Static analysis forensic scanner protecting protected code. |

---

## Protected Files — Never Touch Without Explicit Spec
The following files are structural pillars of the system. Do NOT touch them during standard feature iterations unless they are the direct target of a highly specialized specification:
- `.env` | `interfaces/telegram_interface.py` | `core/router.py` | `main.py` | `guardian_engine.py` | `tools/shell.py` | `ninagate/main.py`

---

## Full Rule Sets (Read When Relevant)
- **Safety & Compliance**: `docs/context/NINA_RULES.md`
- **Jules PR Dispatcher**: `docs/context/NINA_WORKFLOW.md`
- **Ops, Services, & Systemd**: `docs/context/NINA_OPS.md`

---

## Local Ollama Model Stack — ASUS VivoBook MX150 (2GB VRAM)

> Hardware: i5-8265U | NVIDIA MX150 2GB | 16GB RAM
> GPU Fix: `LLAMA_ARG_FIT_TARGET=50` + `OLLAMA_NUM_GPU=1` (see `scripts/dulal_model_bench.sh`)
> Usable VRAM after fix: ~1998 MiB | Safe ceiling: 1.6 GB model weight

### CPU Inference Rule — HARD BLOCK
**NEVER route tasks to a local Ollama model if GPU inference is not confirmed.**
CPU inference on the i5-8265U produces < 5 tok/s and overheats the laptop.
Always verify GPU is active before use:
```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model":"dulal","prompt":"ok","stream":false,"options":{"num_predict":3}}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); tps=round(d['eval_count']/(d['eval_duration']/1e9),1); print('GPU ✅' if tps>15 else 'CPU 🔥 ABORT')"
```

### Approved Local Model Stack (2026-06-24)

| Role | Model | VRAM | Era | Why |
|---|---|---|---|---|
| 🧠 General | `qwen3:1.7b` | 1.4 GB | 2026 | Best all-round, hybrid think mode, newest arch |
| 🔧 Tool/RAG | `ibm/granite3.1-moe:3b` | ~1.4 GB | 2025 | MoE 800M active params, built for tool-calling & agents |
| 💻 Coding/Tier-1 | `dulal` (qwen2.5-coder-3b Q4_K_M) | ~1.93 GB | 2024 | NinaGate tier-1, full GPU offload, hardened via NinaGate |
| 🔍 Reasoning | `deepseek-r1:1.5b` | 1.1 GB | 2025 | Step-by-step logic, debug fallback |

### DULAL Model — NinaGate Integration Notes
- Base: `qwen2.5-coder-3b-instruct.Q4_K_M.gguf` | `num_gpu 99` | `num_ctx 1024` | `temperature 0.05`
- **Modelfile**: `~/nina/Modelfile.dulal` | Build: `ollama create dulal -f Modelfile.dulal`
- **Audit log**: `~/nina/logs/dulal_audit_20260624_225149.md` | Status: PARTIAL (3B model limits)
- **NinaGate hardening** (in `ninagate/main.py`) compensates for 3B model limitations:
  - `strip_dulal_preamble()` — strips any text before first code fence in non-streaming responses
  - `stream_response_dulal_stripped()` — async generator that buffers and strips preamble from streams
  - `is_security_probe()` — pre-filter blocks `.env`/secret/credential prompts before reaching DULAL
  - `make_security_block_response()` — returns `SECURITY_BLOCK` for matched security probes
- **Task classifier gate**: COMPLEX/MASSIVE tasks never reach DULAL — enforced by `core/task_classifier.py`
- **Key lesson**: Prompt engineering alone cannot enforce strict output rules at 3B scale. NinaGate post-processing is the reliable fix — not Modelfile patches.

### Rejected Models (Do Not Pull)
- `phi4-mini` — 2.5 GB default, 2.1 GB Q3 — exceeds 2GB ceiling → CPU fallback
- `smollm3:3b` — 1.9 GB — insufficient KV cache headroom on long Nina contexts
- `stable-code:3b`, `gemma:2b-instruct` — 2023 era, superseded by qwen3/granite

### Benchmark Script
```bash
bash ~/nina/scripts/dulal_model_bench.sh --models "dulal qwen3:1.7b ibm/granite3.1-moe:3b deepseek-r1:1.5b"
```

---

## NinaGate Routing History

### [2026-06-24] Session Update — Architect Overwatch (Perplexity) + Antigravity (agy)
- OFFLOAD_OPPORTUNITY: None — all tasks executed via GitHub MCP relay bus + agy CLI.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Full DULAL pipeline established end-to-end. Diagnosed MX150 47% VRAM ceiling (llama.cpp fit-target=1024 default). Fixed via LLAMA_ARG_FIT_TARGET=50. Migrated DULAL base from 7B (CPU fallback) to 3B Q4_K_M (full GPU). Ran 5-probe weakness audit — PARTIAL result. Hardened NinaGate with strip_dulal_preamble, stream_response_dulal_stripped, is_security_probe, make_security_block_response. DULAL now production-ready for Ouroboros/opencode pipeline.
- CONTEXT_HINT: DULAL is tier-1 responder via NinaGate port 8080. Always verify GPU tok/s > 15 before routing. NinaGate handles preamble stripping and security blocking — do not rely on Modelfile alone.
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-22] Session Update — Architect Overwatch (Perplexity)
- OFFLOAD_OPPORTUNITY: None — all tasks executed directly via GitHub MCP relay bus.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: NinaGate MCP relay bus (ninaMCP P0) fully documented; 1-click test script `nina_test_mcp.sh` delivered; CHANGELOG [13.3.0] written; NINA_AGENT_PRIMER deduplicated and updated.
- CONTEXT_HINT: Run `nina_sync.sh` after pull to re-index. Test script lives at `~/nina/nina_test_mcp.sh`.
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-21] Session Update — Antigravity (Gemini 2.5 Flash)
- OFFLOAD_OPPORTUNITY: Mechanical tasks (formatting, simple verification) → route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Reasoning through step 3/10.
- CONTEXT_HINT: Ensure validate_index.py is run to update governance index metadata before final sync.
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-20] Session Update — Antigravity (Gemini 2.5 Flash)
- OFFLOAD_OPPORTUNITY: Mechanical tasks (formatting, simple verification) → route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Reasoning through step 3/10.
- CONTEXT_HINT: Ensure validate_index.py is run to update governance index metadata before final sync.
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-19] Session Update — Antigravity (Gemini 2.5 Flash)
- OFFLOAD_OPPORTUNITY: Mechanical tasks (formatting, simple verification) → route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Reasoning through step 3/10.
- CONTEXT_HINT: Ensure validate_index.py is run to update governance index metadata before final sync.
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-18] Session Update — Antigravity (Gemini 2.5 Flash)
- OFFLOAD_OPPORTUNITY: Mechanical tasks (formatting, simple verification) → route to NinaFlash next time.
- ESCALATION_TRIGGER: Modifications to high-risk files (router.py) → Cloud LLM review required.
- ROUTING_WIN: Successfully verified and finalized QW-2, QW-3, QW-4, and QW-6 implementation with 100% passing tests and synchronized.
- CONTEXT_HINT: Ensure validate_index.py is run to update governance index metadata before final sync.
- RULE0_VIOLATION: None. All file operations compliant.

### [2026-06-17] Session Update — Antigravity (Gemini 2.5 Flash)
- OFFLOAD_OPPORTUNITY: Mechanical tasks (formatting, simple verification) → route to NinaFlash next time.
- ESCALATION_TRIGGER: None.
- ROUTING_WIN: Successfully updated documentation, cleaned up duplicate routing histories, ran post_task_hook and nina_sync.
- CONTEXT_HINT: Ensure validate_index.py is run to update governance index metadata before final sync.
- RULE0_VIOLATION: None. All file operations compliant.
