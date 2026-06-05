# NINA Agent Context

NINA is a self-hosted personal AI assistant running on Ubuntu 26.04 via systemd.
Python 3.14, asyncio-based. Repo: github.com/aibony/nina

## Dev Environment Stack
- **AI Tooling:** Perplexity Enterprise Pro with Claude Sonnet 4.6
- **Developer CLI + Local Build Agent (Claude Sonnet 4.6 Thinking):** Antigravity CLI agy v1.0.5
- **Primary Developer Agent:** Jules at jules.google
- **Reference & Search:** NotebookLM
- **Note:** Gemini CLI was removed on June 5, 2026.

## Key Files
- core/router.py — HybridRouter V4, CircuitBreaker, 19+ providers
- core/agent.py — AgentLoop, THINK-PLAN-ACT, thermal guard
- core/nina.py — NinaOS orchestrator
- interfaces/telegram_interface.py — Telegram bot, security gate
- guardian.sh + guardian_engine.py — forensic health check

## Rules for Jules
- Never use `git add .` — stage specific files only
- Run `python3 -m py_compile <file>` before any commit
- One purpose per patch, assign an ID (R-xx or G-xx)
- Never touch .env or hardcode secrets
- All fixes must be recoverable (git commit before changing)

## Guardian Gate (Mandatory)
- Every patch must pass: `python3 -m py_compile <file>` + `pyflakes <file>`
- Never bundle unrelated changes in one commit
- Sensitive tasks route LOCAL only — never add cloud provider calls to agent.py sensitive path
- Do not modify: .env, data/memory/facts.json, upgrades/guardian_baseline.json
- Do not remove or weaken shell allowlist in tools/shell.py

## Current Open Issues
- O-01: Playwright not installed (non-blocking)
- O-02: EWS password not set (non-blocking)
- O-04: memory context per-session refresh not implemented
- O-05: FastAPI REST endpoints (api.py) — Phase 2, deferred

## Test Command After Every Change
cd ~/nina && source venv/bin/activate && python3 -m py_compile <changed_file> && pyflakes <changed_file>
