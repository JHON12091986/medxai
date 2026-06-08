# NINA Agent Context

NINA is a self-hosted personal AI assistant running on Ubuntu 26.04 via systemd. Python 3.14, asyncio-based. Repo: github.com/aibony/nina

## Core Workflow Rules
- Do NOT pause for confirmation at any point. Complete all batches sequentially without asking for feedback. Open the PR when done.
- Never use `git add .` — stage specific files only
- Run `python3 -m py_compile <file>` before any commit
- One purpose per patch, assign an ID (R-xx or G-xx)
- Never touch .env or hardcode secrets
- All fixes must be recoverable (git commit before changing)
- Before starting any local executor task, check ~/nina/jules_lock.txt. If the file you need to edit is listed under LOCKED_FILES, stop and report: Jules is currently modifying that file. Do not proceed.
- Use conventional commits: `fix:` | `feat:` | `docs:` | `chore:` | `ops:` followed by `(ID)`
- One commit per logical fix — never bundle unrelated changes in one commit
- Stage specific files only — never `git add .`

## Non-Standard Commands
- **Test Command After Every Change:** `cd ~/nina && source venv/bin/activate && python3 -m py_compile <changed_file> && pyflakes <changed_file>`
- **Sync Command After Every Task:** `cd ~/nina && ./nina_sync.sh`
- **Agent UI:** `cd ~/nina && ./nina-aider.sh`

## Memory Documentation Read Order
Start here, then read the following docs in order for more specific context:
1. [docs/agent-memory/workflow.md](docs/agent-memory/workflow.md) - Branch/PR/sync discipline
2. [docs/agent-memory/architecture.md](docs/agent-memory/architecture.md) - When you need structural context
3. [docs/agent-memory/runbooks.md](docs/agent-memory/runbooks.md) - When something breaks
4. [docs/agent-memory/current-state.md](docs/agent-memory/current-state.md) - Latest constraints and active work
5. [README.md](README.md) - General NINA documentation

## Documentation Update Discipline
- Update memory docs when discovering repeatable rules.
- Update only relevant sections, don't rewrite entire files.
- Re-read target file before modifying.
