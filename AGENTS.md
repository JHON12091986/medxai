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
- Do NOT pause for confirmation at any point. Complete all batches sequentially without asking for feedback. Open the PR when done.
- Proceed immediately to the next batch without waiting for approval.
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

## Mandatory Rules — After Every Code Change (agy)

- Run `python3 -m py_compile <file>` + `pyflakes <file>` on every changed file before committing
- Use conventional commits: `fix:` | `feat:` | `docs:` | `chore:` | `ops:` followed by `(ID)`
- One commit per logical fix — never bundle unrelated changes in one commit
- Stage specific files only — never `git add .`

## Mandatory Rules — After Every Task (agy close)

- Append a log entry to `nina_update_log.md` using **Python only** — never heredoc, never bash echo
  - Auto-detect the next entry number from the file
  - Include: entry number, date, title, what changed, what was verified, rollback path
- Run `cd ~/nina && ./nina_sync.sh` — no exceptions
- Before inserting any content into a file, grep the target file to confirm that content does not already exist. If it does, skip the insertion.

## High-Risk Files — Never Touch Without Explicit Instruction in the Prompt

- `interfaces/telegram_interface.py`
- `.env`
- `core/router.py`
- `main.py`
- `guardian_engine.py`
- `tools/shell.py`

## Never Do

- Write log entries with heredoc (`<< 'EOF'`) or direct `bash echo >>` — always use Python
- Auto-merge Jules PRs — all Jules PRs require explicit review and approval
- Bundle multiple unrelated fixes in one commit
