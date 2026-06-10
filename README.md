# NINA — Neural Intelligent Network Assistant

*A self-hosted, self-developing autonomous AI OS running on Ubuntu 26.04.*

## What is NINA?

NINA is NOT a chatbot. It is an action-first autonomous agent that:
- Routes tasks across 20+ AI providers via HybridRouter V4
- Develops itself autonomously via Jules + ninaflash pipeline
- Manages email (EWS), monitors markets (DSE/CSE), handles finance, and self-repairs
- Keeps all banking and sensitive data strictly on the local machine in Dhaka

## Three-Tier Agent Model

This model is the heart of NINA's architecture, employing three parallel agents:

| Agent | Role | Backend | Scope |
|---|---|---|---|
| Perplexity Enterprise Pro | Architect + Overwatch | Claude Sonnet 4.6 | Strategic direction, specs, post-execution review |
| Jules (jules.google.com) | Async Cloud Coder | Gemini 3.1 Pro | Multi-file feature builds, submits PRs |
| ninaflash (Antigravity CLI) | Local Executor | Gemini Flash | Hotfixes, PR merges, deploys, syncs |

Jules builds features asynchronously in the cloud. ninaflash reviews and merges Jules' PRs locally. Perplexity architects before and reviews after. Nobody does manual coding.

## ninaflash — The Local Executor

ninaflash is NINA's local muscle:
- CLI tool at `bin/nf` (Antigravity CLI, v1.0.5)
- Powered by Claude Sonnet 4.6 Thinking
- Commands:
  - `nf status` — checks locks, git workspace, backlog
  - `nf pr merge <PR>` — lint check → merge → sync → backlog update
  - `nf dispatch <TASK_ID>` — locks files → IN_PROGRESS → sends to Jules API
  - `nf aider <TASK_ID>` — launches aider with task context
  - `nf doctor` — finds latest Python traceback in logs
  - `nf ninaloop` — activates continuous autonomous developer loop

## Universe-Mode Kernel (ninaflash v8.0)

The kernel architecture giving ninaflash near-infinite capability at zero cloud token cost:
- **Nucleus:** 1,001 core functions (`tools/ninaflash.py`)
- **Synapses:** 1,000,000 specialized Neural Op-Codes across 1,000 sector files (`tools/kernel/sector_000.py` → `sector_999.py`)
- **Omniscient Dispatcher:** Dynamic on-demand sector loader — executes any op-code without loading all sectors into memory
- Purpose: Gives ninaflash near-infinite local skill capability at zero cloud token cost

## HybridRouter V4

The routing engine located in `core/router.py`:
- Routes across 19+ cloud providers (Groq, Gemini, Cerebras, DeepSeek, Mistral, OpenRouter, Together, Cohere, Fireworks, xAI, SambaNova, Hyperbolic, Novita, Perplexity, OpenAI, Pollinations, Chutes, and more)
- 2 local models via Ollama (qwen2.5:1.5b for fast tasks, qwen2.5:7b for heavy reasoning)
- CircuitBreaker pattern prevents cascading failures
- Weighted scoring: success rate × latency × rate limits
- Free-tier first routing philosophy (routing is handled automatically by HybridRouter V4 with free-tier priority)

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
| ninaflash (agy) | Gemini Flash | ~5h rolling | Rolling |
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
