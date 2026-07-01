<<<<<<< HEAD
# 🦈 Tiburón Supremo Maximal AI - API de Scraping y Resumen con IA

## Características
- **Scraper inteligente** de cualquier URL.
- **Resumen automático** con modelo `facebook/bart-large-cnn` (corre en CPU/GPU).
- **Soporte técnico automático**: busca y resume soluciones para códigos de error.
- Endpoints REST documentados y listos para producción.

## Instalación (Windows / Linux / Mac)
1. Clona o descarga este proyecto.
2. Crea y activa un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows
=======
# NINA — Personal AI Infrastructure

> M. Baizid Alam · AGM, BASIC Bank PLC · Dhaka, Bangladesh
> ASUS VivoBook X530FN · Ubuntu 26.04 · Python 3.14.4 · `~/nina/venv`

NINA is a locally-hosted multi-agent AI orchestration system. She receives commands via Telegram, routes them to the right agent, and manages a persistent async OODA loop.

---

## Quick Start

```bash
cd ~/nina
source venv/bin/activate

# Check all services
systemctl --user status nina ninagate ninamcp

# Push changes (always use ngit)
ngit "your commit message"

# Manual sync / OODA health check
sync

# Run SSOT audit (do this first in any session)
.venv/bin/python tools/nina_ssot.py --report

# Run locally
python3 main.py
```

---

## Repo Structure

```
nina/
├── agents/          # All AI agents (agy, gemini, jules, ninamcp, opencode, perplexity)
├── core/            # Router, memory, OODA loop, token guard
├── interfaces/      # Telegram, CLI, API
├── ninagate/        # Reverse-proxy gateway (service — NOT an agent)
├── mcp/             # MCP tool definitions
├── config/          # Static config
├── scripts/         # Shell scripts (ngit.sh, nina_sync.sh)
├── bin/             # Binaries
├── tools/           # Python dev/ops utilities (nina_ssot.py, dedup, guardian, etc.)
├── data/            # Persistent data (registry, memory, graphs, nina_ssot.json)
├── runtime/         # Ephemeral runtime state (locks, cache, live state)
├── docs/            # Documentation (nina_ssot.md auto-generated here)
└── tests/           # Test suite
```

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for full system design and [`FOLDER_TREE.md`](./FOLDER_TREE.md) for the complete directory tree.

---

## Agents

| Agent | Path | Purpose |
|---|---|---|
| **NinaMCP** | `agents/ninamcp/` | MCP server — exposes Nina tools to OpenCode/Cursor |
| **OpenCode** | `agents/opencode/` | Local AI coding via OpenCode CLI |
| **agy** | `agents/agy/` | CrewAI multi-agent tasks |
| **Jules** | `agents/jules/` | GitHub PR coding agent |
| **Gemini CLI** | `agents/gemini/` | Gemini CLI integration |
| **Perplexity** | `agents/perplexity/` | Research & web search |

---

## Key Commands

```bash
# Push (always use ngit — fires sync automatically via post-push hook)
ngit "commit message"

# Services
systemctl --user restart nina
systemctl --user restart ninagate
systemctl --user restart ninamcp

# SSOT health audit
.venv/bin/python tools/nina_ssot.py --report

# Dispatch OpenCode task
python3 -c "from agents.opencode.tools.opencode_tool import dispatch; dispatch('your task here')"

# Wipe runtime state (safe)
rm -rf runtime/state/* runtime/locks/* runtime/cache/*
```

---

## SSOT System

`tools/nina_ssot.py` is the single authority on env vars, import chains, and symbol wiring.

```
nina_sync.sh
└── python tools/nina_ssot.py
     ├── exit 0 → sync continues
     └── exit 1 → sync BLOCKED — fix violations first
```

Outputs:
- `data/nina_ssot.json` — machine-readable truth
- `docs/nina_ssot.md` — human-readable report

---

## Documentation

- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — full system design, agent registry, governance rules
- [`FOLDER_TREE.md`](./FOLDER_TREE.md) — annotated directory tree
- [`docs/nina_ssot.md`](./docs/nina_ssot.md) — SSOT report (auto-generated)
- [`docs/space/NINA_UPDATE_LOG.md`](./docs/space/NINA_UPDATE_LOG.md) — change history
- [`docs/space/nina_session_brief.md`](./docs/space/nina_session_brief.md) — agent session context
- [`docs/space/FEATURES.md`](./docs/space/FEATURES.md) — feature registry
- [`docs/`](./docs/) — MEMORY, WORKFLOW, CHANGELOG, CONTRIBUTING, SECURITY
- [`opencode.json`](./opencode.json) — OpenCode MCP config
>>>>>>> cbb4b4dcd44382648448ba40737f237f25289730
