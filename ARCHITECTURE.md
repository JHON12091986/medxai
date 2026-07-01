# NINA Architecture

> Version: **v14.5** | Updated: 2026-06-22
> Owner: M. Baizid Alam | ASUS VivoBook X530FN · Ubuntu 26.04 · Python 3.14.4

---

## §1 Overview

NINA is a personal AI infrastructure system — a multi-agent orchestration platform running locally at `~/nina` on Ubuntu. She receives commands via Telegram, routes them to the right agent or tool, and manages a persistent async loop.

```
User (Telegram)
     │
     ▼
 interfaces/telegram_bot.py
     │
     ▼
 core/router.py  ──►  NinaGate  ──►  agents/ninamcp/   (MCP tools)
     │                               agents/agy/        (CrewAI tasks)
     │                               agents/jules/      (GitHub coding)
     │                               agents/opencode/   (local coding)
     │                               agents/gemini/     (Gemini CLI)
     │                               agents/perplexity/ (research)
     ▼
 core/ooda.py  (Observe → Orient → Decide → Act loop)
     │
     ▼
 core/memory.py  ──►  data/memory/
```

---

## §2 Directory Structure

| Directory | Role | Ephemeral? |
|---|---|---|
| `agents/` | All external AI agent integrations | No |
| `agents/ninamcp/` | NinaMCP server — MCP protocol bridge | No |
| `agents/opencode/` | OpenCode agent + dispatch tool | No |
| `agents/agy/` | CrewAI-based agy agent | No |
| `agents/jules/` | Jules (Google AI) coding agent | No |
| `agents/gemini/` | Gemini CLI agent | No |
| `agents/perplexity/` | Perplexity research integration | No |
| `core/` | Router, memory, OODA, token guard | No |
| `agent/` | Nina's own agent loop | No |
| `interfaces/` | Telegram, CLI, API | No |
| `ninagate/` | Reverse-proxy gateway service | No |
| `mcp/` | MCP tool definitions | No |
| `config/` | Static config | No |
| `scripts/` | Shell scripts (nina_sync, ensure_env, etc.) | No |
| `bin/` | Binaries (guardian) | No |
| `tools/` | Python dev/ops utilities | No |
| `data/` | Persistent data — registry, memory, graphs | No |
| `runtime/` | Live ephemeral state — **do NOT edit manually** | **Yes** |
| `runtime/state/` | Live JSON state (OODA, Jules, sessions) | Yes |
| `runtime/locks/` | Lock files (.lock) | Yes |
| `runtime/cache/` | Cache files | Yes |
| `runtime/logs/` | Runtime logs, telemetry, gemini scratch | Yes |
| `docs/` | Documentation | No |
| `logs/` | Historical audit logs | No |

---

## §3 Agent Registry

| Agent | Location | Trigger | Model | Gateway |
|---|---|---|---|---|
| **NinaMCP** | `agents/ninamcp/` | MCP calls from OpenCode/Cursor | — | direct |
| **OpenCode** | `agents/opencode/` | `opencode:` Telegram prefix | Claude / GPT | NinaGate |
| **agy** | `agents/agy/` | `agy:` Telegram prefix | Gemini Pro | NinaGate |
| **Jules** | `agents/jules/` | GitHub PR/issue triggers | Gemini 2.5 | GitHub API |
| **Gemini CLI** | `agents/gemini/` | `gemini:` Telegram prefix | Gemini 2.5 | NinaGate |
| **Perplexity** | `agents/perplexity/` | `perplexity:` prefix | sonar-pro | NinaGate |

---

## §4 NinaGate

NinaGate (`ninagate/`) is a FastAPI reverse proxy that brokers all outbound AI calls. It handles:
- API key rotation
- Rate limiting & token budget enforcement
- Session tracking (`runtime/state/ninagate_sessions.json`)
- Provider health monitoring (`runtime/state/provider_health.json`)

NinaGate is a **service**, not an agent — it stays at repo root, not under `agents/`.

```bash
systemctl --user status ninagate
systemctl --user restart ninagate
```

---

## §5 OpenCode Integration

OpenCode (`agents/opencode/`) provides local AI coding capability:

```
agents/opencode/
├── tools/
│   └── opencode_tool.py    # dispatch(task) → runs opencode CLI subprocess
├── tasks/
│   └── TASK_TEMPLATE.md    # task spec format
├── prompts/
│   └── system_prompt.md    # Nina context injected into OpenCode
└── logs/                   # run logs (also mirrored to runtime/logs/opencode/)
```

The `opencode.json` at repo root configures NinaMCP as an MCP provider for OpenCode — giving it full Nina tool access.

Dispatch pattern:
```python
from agents.opencode.tools.opencode_tool import dispatch_async
result = await dispatch_async("implement X in core/router.py")
```

---

## §6 Runtime State

All ephemeral runtime files live under `runtime/`. This directory is **never edited manually** and can be wiped cleanly:

```bash
rm -rf runtime/state/* runtime/locks/* runtime/cache/*
# DO NOT wipe runtime/logs/ — they are audit trail
```

| Subdirectory | Contents |
|---|---|
| `runtime/state/` | ooda_state, jules_watchdog, ninagate_sessions, provider_health, session_* |
| `runtime/locks/` | nina.lock, ninajulesgithub.lock, juleslock.txt |
| `runtime/cache/` | router_cache, model_cache, token_guard_cache |
| `runtime/logs/` | telemetry.jsonl, gemini_scratch.jsonl, opencode run logs |

---

## §7 Data (Persistent)

`data/` holds permanent reference data that survives restarts:

| File | Purpose |
|---|---|
| `data/symbol_map.json` | Codebase symbol index (372KB) |
| `data/dependency_graph.json` | Module dependency graph |
| `data/capabilities.json` | Nina capability registry |
| `data/jules_registry.json` | Jules task history (61KB) |
| `data/healthcheck_registry.txt` | Service health definitions |
| `data/memory/` | Long-term memory store |
| `data/graphs/` | Graph data |
| `data/plans/` | Planning artifacts |
| `data/reports/` | Generated reports |

---

## §8 Key Services

```bash
# Nina main service
systemctl --user status nina
systemctl --user restart nina

# NinaGate proxy
systemctl --user status ninagate
systemctl --user restart ninagate

# NinaMCP server
systemctl --user status ninamcp
systemctl --user restart ninamcp

# Sync + push to GitHub
bash scripts/nina_sync.sh
```

---

## §9 Governance Rules (Non-Negotiable)

1. **Always read live repo via GitHub MCP** before any answer — never assume from memory
2. **Before any fix**: read `docs/nina_error_register.md` + `docs/jules_backlog.md` + target file
3. **Never use `sudo systemctl`** — use `systemctl --user` only
4. **Runtime files** are ephemeral — never commit lock files or cache to main data
5. **All file reads/writes** via GitHub MCP only (from Architect Overwatch context)
6. **Bash scripts** only for: `systemctl`, `nina_sync.sh`, compile checks, log tailing

---

## §10 OODA Loop

Nina operates on a continuous Observe → Orient → Decide → Act loop managed by `core/ooda.py`. State is persisted to `runtime/state/ooda_state.json`.

---

## §11 Memory Architecture

```
Short-term:  runtime/state/session_memory.jsonl   (current session)
Long-term:   data/memory/                          (persisted across restarts)
Shared:      data/crew_shared_memory.json          (multi-agent shared context)
```

---

## §12 Scripts & Binaries

| Path | Purpose |
|---|---|
| `scripts/nina_sync.sh` | Sync, regenerate indices, push to GitHub |
| `scripts/ensure_env.sh` | Verify venv + env vars before service start |
| `scripts/nina_test_mcp.sh` | Test NinaMCP endpoints |
| `bin/guardian` | Guardian binary (process watchdog) |
| `nina_cleanup_sprint.sh` | Root-level cleanup script (pending move to scripts/) |
