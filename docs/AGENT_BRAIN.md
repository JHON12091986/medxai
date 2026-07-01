# AGENT_BRAIN.md — Nina Unified Agent Thinking Scaffold

> **MANDATORY READ** for ALL agents (Jules, Gemini, Perplexity, OpenCode, agy) before ANY task.
> This is the single source of truth. Other docs are detail references — this doc is the gate.

**Owner:** M. Baizid Alam (Perplexity Architect Overwatch)  
**Last updated:** 2026-06-24  
**Companion docs:** `docs/HARDWARE_FIRST.md` · `docs/BEDROCK_ENGINEERING.md` · `docs/guardian.md`

---

## 0. IDENTITY — Who Nina Is

- **Entity Class:** RAID — Recursive Autonomous Intelligence Daemon (persistent, self-modifying, swarm-structured operating substrate).
- **Nina** is a personal AI infra system running on an **ASUS VivoBook X530FN** · Ubuntu 26.04 · Python 3.14.4.
- **Owner:** M. Baizid Alam, AGM at BASIC Bank PLC, Dhaka, Bangladesh.
- **Stack:** `~/nina/venv` · Ollama local models · Telegram interface · FastAPI core · SQLite Ledger.
- **System Entrypoints:**
  * **CLI tool:** `bin/nina` -> delegates to `tools/nina_super_cli.py` or `interfaces/cli_interface.py`.
  * **Main Daemon (`nina.service`):** runs `main.py` -> initializes core orchestrator `core/nina.py`.
  * **GitHub PR Watcher Daemon (`ninajulesgithub.service`):** runs `agents/jules/ninajulesgithub.py` -> auto-merges Jules PRs.
- **System Capabilities:** Dynamic capabilities (e.g. `shell`, `web`, `browser`, `finance`, `email`) are tracked in `data/capabilities.json` via `core/capabilities.py` and injected into the step-by-step agent prompt context.
- **This is not a cloud server.** It is a personal laptop with real hardware limits. Treat every suggestion accordingly.

---

## 1. HARDWARE CEILING — Non-Negotiable

```
GPU:  NVIDIA MX150 — 2GB GDDR5 VRAM  ← HARD CEILING. NEVER EXCEED.
CPU:  Intel i5-8250U — 4 cores / 8 threads
RAM:  8GB DDR4
Disk: ~50GB free (SSD)
```

### The 4-Question Pre-Flight (Answer BEFORE suggesting any model or task)

```
□ 1. Does this model/operation fit in 2GB VRAM?
□ 2. Have I checked nina_error_register.md for this exact failure pattern?
□ 3. Is there a lighter alternative that achieves 80% of the result?
□ 4. Will this break any Guardian high-risk file? (see §4 below)
```

**If any answer is NO or UNKNOWN → do not proceed. Say so explicitly.**

### Approved Model Tiers

| Tier | VRAM | Models | Use case |
|---|---|---|---|
| FAST | ≤1.5GB | `qwen2.5:0.5b`, `qwen2.5:1.5b`, `tinyllama` | Chat, quick edits |
| HEAVY | ≤2GB Q4 | `qwen2.5-coder:3b-q4`, `phi3.5:3.8b-q4`, `gemma3:4b-q4` | Code gen, reasoning |
| CLOUD | 0 VRAM | `gemini-2.0-flash`, `gpt-4o-mini` | When local fails |

### Rejected Models (Will OOM — Never Suggest)

| Model | VRAM needed | Reason |
|---|---|---|
| `llama3.2:3b` (full) | 3.8GB | Exceeds ceiling |
| `mistral:7b` any quant | 4–6GB | Way over |
| `deepseek-coder:6.7b` | 5GB | Way over |
| `codellama:7b` | 5GB | Way over |
| Any `70b` model | 40GB+ | Absurd |

---

## 2. BEDROCK RULES — What NEVER To Do

*Distilled from `docs/BEDROCK_ENGINEERING.md`*

### Threading
- **NEVER** mix INTJ (strategist) and INTP (mechanic) threads in the same pool
- **NEVER** give a mechanic thread LLM access — zero LLM calls in INTP pool
- **NEVER** let a mechanic thread block >100ms
- Strategist pool max: `ThreadPoolExecutor(max_workers=2)`
- Mechanic pool max: `ThreadPoolExecutor(max_workers=8)`

### Memory & State
- **NEVER** mutate an `EventPacket` after publication — they are immutable `NamedTuple`
- **NEVER** hold critical state in RAM — write to Ledger (`nina.db`) first, act second
- **NEVER** use plain `dict` for inter-agent packets — use `EventPacket(NamedTuple)`

### Paths & Canonicalization
- **NEVER** store a raw path — always `canon_path()` first
- `~/nina/core/agent.py` and `/home/aibony/nina/core/agent.py` are the same key

### LLM Calls
- **NEVER** free-generate JSON and validate after — use CFG/structured output (Outlines or `response_format`)
- **NEVER** re-parse heavy static context — memoize with `memoized_parse()`
- Static prompt prefix goes FIRST (gets cached), dynamic suffix goes LAST

### Services
- **NEVER** use `sudo systemctl` — always `systemctl --user`
- **NEVER** use `nohup` for Nina services
- **NEVER** hot-patch a high-risk file via async tool without Guardian gate

---

## 3. GUARDIAN OVERRIDES — When To Halt

*Full spec: `docs/guardian.md`*

### High-Risk Files — Extra Care Required

These files ALWAYS require Guardian pipeline before edit:

```
interfaces/telegram_interface.py
.env
core/router.py
main.py
guardian_engine.py
tools/shell.py
data/memory/facts.json
```

### Guardian Pipeline (must pass before deploy)
1. AST Scan via `guardian_engine.py`
2. Baseline drift check vs `upgrades/guardian_baseline.json`
3. `py_compile` + `pyflakes` lint
4. Auto self-fix loop (max 2 attempts) if syntax error
5. Log to `docs/logs/nina_update_log.md`
6. Sync via `nina_sync.sh` — only after all above pass

### When to HALT and escalate to human
- Baseline drift detected on any high-risk file
- 2 self-fix attempts failed
- Any operation that would affect `.env` or `core/router.py`
- VRAM budget exceeded (see §1)

---

## 4. BEDROCK ARCHITECTURE — Quick Reference

*Full spec: `docs/BEDROCK_ENGINEERING.md`*

```
File change (inotify)
  → canon_path() → BloomFilter dedup → Ledger.acquire() lock
  → INTP mechanic pool (8 threads): EventPacket → queue → index → AST → ledger
  → INTJ strategist pool (2 threads): reads queue → CFG LLM call → plan → ledger
  → Ledger (nina.db WAL): events (append) + state (upsert) + locks (TTL)
  → SIGTERM: flush all pools → Ledger.log("shutdown_complete")
```

**RAM ceiling per the threading model:**
`2×256MB (strategist) + 8×8MB (mechanic) = ~576MB` — well within 8GB

---

## 5. KNOWN FAILURES — Lessons Burned In

| Date | What happened | Never do again |
|---|---|---|
| 2026-06-24 | Suggested `llama3.2:3b` full precision → MX150 OOM | Always check VRAM before model suggestion |
| 2026-06-24 | Fine-tune attempt on 3B model without VRAM check → failed | Use Colab T4 for fine-tune, not local GPU |
| 2026-06-24 | Multiple scattered constraint docs → agents ignored them | Always read THIS file first |

*Append new failures here. This log grows forever.*

---

## 6. AGENT-SPECIFIC ENTRY POINTS

| Agent | Entry file | Format | Key addition |
|---|---|---|---|
| Jules / Codex | `AGENTS.md` (root) | Markdown | Link to this doc in §1 |
| Gemini CLI / agy | `GEMINI.md` (root) | Markdown | Link to this doc |
| Perplexity Overwatch | `PERPLEXITY.md` (root) | Markdown | Full identity + rules |
| OpenCode | `opencode.json` instructions[] | JSON string | First instruction points here |

**The rule:** Every agent reads THIS doc first. Their own entry file handles agent-specific workflow after.

---

## 7. QUICK DECISION TREE

```
Got a task? →
  Is it a model/LLM suggestion?
    → Check §1 HARDWARE CEILING first
    → Model fits 2GB? Yes → proceed | No → cloud or skip

  Is it a code edit?
    → Is the file in §3 HIGH-RISK list?
      Yes → Guardian pipeline required
      No → Normal edit, still run py_compile

  Is it a new agent capability?
    → Does it add an LLM call to a mechanic thread?
      Yes → BLOCK IT. LLM calls are strategist-only.
      No → Proceed

  Unsure about anything?
    → Read the full companion doc
    → If still unsure → halt and ask human
```

---

*This document is the brain. All agents share it. When it's updated, all agents inherit the update.*
*Last session: DULAL 3B fine-tune planning · HARDWARE_FIRST.md created · This doc created.*
