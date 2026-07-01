# NinaMCP — 3-Tier Relay System

ARCHITECT OVERWATCH diagnostic connectivity for aibony/nina.

## Tier Summary

| Tier | Name | Latency | Infra | Status |
|------|------|---------|-------|--------|
| P0 | GitHub Relay Bus | ~3-5s after alias run | Zero (uses existing repo) | ✅ Ready |
| P1 | Cloudflare Tunnel | Live (<100ms) | cloudflared (free) | 🔧 Setup required |
| P2 | GitHub Actions Relay | ~30-60s | GitHub-hosted runners | 🔧 Setup required |

## P0 — GitHub Relay Bus (Use TODAY)

Run aliases locally → they write structured JSON to `logs/nina_mcp_results/` → push → ARCHITECT reads via `get_file_contents`.

### Setup
```bash
# Add to ~/.bashrc or ~/.zshrc
source ~/nina/mcp/aliases.sh
```

### Usage
```bash
nina_exec scripts/nina_sync.sh audit   # run script, result in logs/nina_mcp_results/exec_result.json
nina_tail nina_sync                     # tail log, result in logs/nina_mcp_results/tail_result.json
nina_diff                               # git diff, result in logs/nina_mcp_results/diff_result.json
nina_search "router error"              # ollama semantic search, result in search_result.json
nina_status                             # full health snapshot in logs/nina_mcp_results/status_result.json
```

After each alias: ARCHITECT reads `logs/nina_mcp_results/<slot>.json` via GitHub MCP `get_file_contents`.

## P1 — Cloudflare Tunnel

See `mcp/cloudflare/setup.sh` — runs cloudflared as `systemctl --user` service.
Exposes `localhost:7432` at a persistent public URL.

## P2 — GitHub Actions Relay

Write a command file to `mcp/inbox/` → GitHub Action executes → result in `mcp/outbox/`.
ARCHITECT uses `create_or_update_file` to send commands, `get_file_contents` to read results.

See `.github/workflows/nina-mcp-relay.yml`.
