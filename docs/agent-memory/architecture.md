# NINA Architecture

## Module Boundaries
- `core/`: Core orchestrator (`nina.py`), Agent loop (`agent.py`), Provider routing (`router.py`), Memory and capabilities.
- `tools/`: Executable actions (browsing, shell execution, system monitoring, file operations).
- `interfaces/`: External endpoints (Telegram bot, REST API).
- `crons/`: Scheduled jobs and managers.

## High-Risk / No-Touch Files
The following files default to local executor or manual local handling unless explicitly authorized. Never touch without explicit instruction:
- `interfaces/telegram_interface.py`
- `.env`
- `core/router.py`
- `main.py`
- `guardian_engine.py`
- `tools/shell.py`
- Any systemd unit files
- `nina_sync.sh` (unless documentation comments only)

## Tool Locations
- Dashboard: `dashboard/nina-guardian.html`
- Sync tool: `nina_sync.sh`
- Architect/CLI Toolset: `bin/ninaflash`
