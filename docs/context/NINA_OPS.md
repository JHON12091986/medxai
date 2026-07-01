# NINA Ops — Service Map & Commands
## updated: 2026-06-16
## source: ARCHITECTURE.md

## 4 systemd Services
nina.service              → main.py → core/nina.py (NinaOS orchestrator)
ninagate.service          → ninagate/main.py (OpenAI-compatible proxy, localhost:8080)
ninajulesgithub.service   → ninajulesgithub.py (Jules PR watcher + dispatch)
nina-dashboard.service    → dashboard/ (web UI)

## Restart Rules
Safe (default):
  sudo systemctl restart nina.service
  sudo systemctl status nina.service   ← confirm Active: running within 30s

Full restart (only when explicitly instructed by Bostami):
  sudo systemctl restart nina.service ninagate.service ninajulesgithub.service

NEVER restart ninagate.service or ninajulesgithub.service without explicit instruction.

## Health Check
sudo systemctl status nina.service
sudo journalctl -u nina.service -n 50 --no-pager

## Guardian Modes
cd ~/nina && ./guardian --mode report   ← read-only, safe anytime
cd ~/nina && ./guardian --mode full     ← deep AST scan, use carefully
cd ~/nina && ./guardian --mode hook     ← git hook mode

## Key Paths
repo:         ~/nina
venv:         source ~/nina/venv/bin/activate
agy:          ~/.local/bin/agy
sync:         cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh
register:     ~/nina/docs/space/nina_error_register.md
backlog:      ~/nina/docs/space/jules_backlog.md
context:      ~/nina/docs/context/
