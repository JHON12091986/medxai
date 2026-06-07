---
name: nina-ops
description: NINA's operational environment — how to run, check health, restart, and work with the Guardian. Load this for any operational tasks, service management, debugging, or deployment questions.
---

# NINA Operations Guide

## Quick Commands

### Start / Stop / Restart
```bash
# Recommended (with guardian watchdog — manages full service lifecycle)
cd ~/nina && ./guardian

# Direct (no watchdog)
cd ~/nina && source venv/bin/activate && python main.py

# Systemd service
sudo systemctl start nina
sudo systemctl stop nina
sudo systemctl restart nina
sudo systemctl status nina
```

### Check Logs
```bash
journalctl -u nina -f              # Live logs
journalctl -u nina -n 50           # Last 50 lines
cat ~/nina/nina_update_log.md      # Change history
cat ~/nina/docs/space/nina_error_register.md  # Bug/fix history
```

### Guardian Health Check
```bash
cd ~/nina && ./guardian
# MUST pass before any deploy
# MUST pass after any change to core/, tools/, interfaces/, main.py, .env
```

## Environment
```bash
cd ~/nina
source venv/bin/activate           # Python 3.14

# Key paths (all gitignored)
~/nina/.env                        # Secrets — NEVER commit
~/nina/data/memory/                # Personal data — gitignored
~/nina/logs/                       # Runtime logs — gitignored
~/nina/upgrades/                   # Upgrade pipeline — gitignored
```

## .env Key Variables
```
TELEGRAM_BOT_TOKEN=
AUTHORIZED_USER_ID=
GROQ_API_KEY=           # Free tier — recommended default
GEMINI_API_KEY=
OPENAI_API_KEY=         # Paid — use sparingly
EWS_USERNAME=           # BASIC Bank Exchange (webmail.basicbanklimited.com)
EWS_PASSWORD=           # ← Set this to unlock email triage with ZERO code changes
EWS_MY_EMAIL=
EWS_SHARED_EMAIL=
RAM_GUARD_GB=
IDLE_AUTO_APPROVE=
API_SECRET_KEY=
```
> **Quick unlock:** Set `EWS_PASSWORD` in `.env` → email triage, morning report email section, and urgency nudge all activate immediately. Zero code required.

## Provider Priority (free tier first)
`Groq → Gemini → Cerebras → DeepSeek → Mistral → Together → Cohere → Fireworks → Perplexity → SambaNova → Hyperbolic → Novita → OpenRouter → xAI → OpenAI (paid, last resort)`

## Local Models (Ollama)
- `qwen2.5:1.5b` → LOCALFAST (quick tasks, self-check pass, sensitive tasks)
- `qwen2.5:7b` → LOCALHEAVY (complex local reasoning)
- `nomic-embed-text` → embeddings for memory

## Guardian Pass Criteria
1. venv active, Python 3.14, all required packages present
2. `.env` validation passed (`TELEGRAM_CHAT_ID` warning acceptable)
3. Syntax check all tracked files OK
4. pyflakes — no issues
5. mypy — warnings non-blocking
6. `nina.service` active, no crash pattern
7. Telegram polling confirmed
8. APScheduler started (13 jobs)

## Telegram Commands (key ones)
| Command | Action |
|---------|--------|
| `status` | RAM, VRAM, CPU, thermal, provider health |
| `router` | Provider scores, latency, token counts |
| `logs` | Last 20 lines nina.log |
| `reset` | Clear session cache |
| `memory` | Show facts.json |
| `email` | Fetch BASIC Bank mailbox summary |
| `patch <url>` | Submit upgrade patch for review |
| `approve` | Deploy approved patch |
| `rollback` | Restore last backup |

## Common Issues
| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| "All providers unavailable" | camelCase/snake_case mismatch in router | Check `ClassifiedTask` field names — use `task.task_type` |
| Duplicate log handlers on restart | Missing `if not root.handlers` guard | S-05 in roadmap |
| Complex tasks crash silently | RAM guard `ram_guard_gb` typo | Fixed in v12.2 (A-1) |
| Telegram message dropped | Document check after empty-text guard | Check `telegraminterface.py` order |

## Git Workflow
```bash
cd ~/nina
git status
git add <specific files>           # NEVER git add .
git commit -m "type(scope): description (ID)"
git push origin main
```
**Never commit:** `.env`, `data/memory/`, `logs/`, `*.bak*`, `*.save*`, `*.fix*`, `*.selfcheck*`
