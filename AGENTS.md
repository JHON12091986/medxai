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
- Routes: SIMPLE → NinaFlash | MEDIUM → Gemini Flash | COMPLEX → Gemini Pro / Qwen3-Coder
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
1. CLASSIFY FIRST — Before any cloud call, classify the subtask.
   Mechanical tasks (rename, format, grep, boilerplate, docstrings, type hints) → NinaFlash always.
2. CHUNK LARGE TASKS — Break tasks > 2000 tokens into subtasks, tier each chunk separately.
3. COMPRESS CONTEXT — Strip comments, whitespace, unchanged file sections before sending to cloud.
   Send only the diff-relevant portion + minimal surrounding context.
4. SUMMARIZE BEFORE ESCALATE — NinaFlash summarizes file context first; only the summary + task
   goes to cloud. Never send a raw full file to cloud if NinaFlash can summarize it first.
5. CACHE PATTERNS — If NinaFlash already produced output for a repeating pattern
   (log format, error handler template), reuse it. Do not re-query cloud.

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
4. QUOTA AWARENESS — When Gemini Flash > 900 req today, shift medium tasks to
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
             ├─ YES → [NinaFlash: summarize] → [Gemini Flash: reason]
             └─ NO  → Gemini Pro / Qwen3-Coder-480B (full context, quality gate)

    Gemini Flash quota exhausted (> 900 req today)?
    └─ YES → Qwen Code CLI → then NinaFlash local fallback

    Network unavailable?
    └─ YES → NinaFlash unconditionally for all tasks

---

## PART 4 — HARDCODED RULES (never override, never skip)

1. HIGH-RISK FILES always require cloud LLM review regardless of task size:
   interfaces/telegram_interface.py | .env | core/router.py | main.py |
   guardian_engine.py | tools/shell.py
   → Escalate ALL changes to these files to at minimum Gemini Flash.

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

---

## PART 5 — SESSION-END AUTO-UPDATE PROTOCOL (mandatory, no user prompt needed)

At the END of every session, ALL coders (Gemini CLI, agy, Jules, Qwen Code) MUST:

### 5A. Capture Learnings
- Which cloud calls could have been NinaFlash? → label: OFFLOAD_OPPORTUNITY
- Which NinaFlash outputs needed cloud escalation and why? → label: ESCALATION_TRIGGER
- Which routing decisions were optimal? → label: ROUTING_WIN
- New file patterns affecting chunking strategy? → label: CONTEXT_HINT

### 5B. Append to AGENTS.md — "## NinaGate Routing History" section
```
### [2026-06-11] Session Update — [tool used]
- OFFLOAD_OPPORTUNITY: [task type] → route to NinaFlash next time
- ESCALATION_TRIGGER: [condition] → always route to [model]
- ROUTING_WIN: [pattern] confirmed efficient
- CONTEXT_HINT: [file/boundary] for optimal chunking
```

### 5C. Run Sync (mandatory, no exceptions)
cd ~/nina && ./nina_sync.sh
Snapshots updated AGENTS.md into nina_latest.md → auto-syncs to Google Drive
→ Perplexity ARCHITECT OVERWATCH picks up learnings in next thread.

---

## PART 6 — BOOTSTRAP CHECKLIST (Gemini CLI session start)

1. Verify NinaGate is active:
   curl -s http://localhost:8080/health || (cd ~/nina/ninagate && python3 ninagate.py &)

2. Verify NinaFlash (Ollama) is running:
   curl -s http://localhost:11434/api/tags | grep qwen || ollama pull qwen2.5-coder:7b

3. Route Gemini CLI through NinaGate:
   export GOOGLE_GEMINI_BASE_URL="http://localhost:8080/genai"
   export GEMINI_API_KEY="${GEMINI_API_KEY}"

4. Confirm .gemini/settings.json contains:
   { "context": { "fileName": ["AGENTS.md"] } }

---
## END NINA-OPT-001
## Maintained by nina_sync.sh — routing history appended automatically each session.
## NinaGate Routing History
<!-- Auto-appended by session-end protocol -->
