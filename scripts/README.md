# scripts/

All operational shell scripts for NINA.

| Script | Purpose |
|--------|---------|
| `nina_sync.sh` | Main OODA-loop autonomous sync — pull, audit, backup, commit, push |
| `generate_backups.sh` | Unified backup: claude feed + full snapshot (age-guarded 6h, called by A5.5) |
| `nina_cleanup.sh` | Safe duplicate + oneshot cleanup |
| `nina_audit.sh` | Run all audit tools |
| `nina_export.sh` | Export docs/space snapshot |
| `nina_aider.sh` | Launch aider with NINA context |
| `agy_task.sh` | Generate AGY task prompt (tiered, AST context) |
| `agy_verify.sh` | Post-task verify (compile + pyflakes + guardian drift) |
| `agy_watchdog.sh` | Watchdog for stuck tasks |
| `gen_codemap.sh` | Regenerate CODEBASE_MAP.md |
| `gemini_monitor.sh` | Gemini task monitor |
| `install_hooks.sh` | Install git hooks |
| `move_root_strays.sh` | Move stray root files to correct dirs |
| `deploy_services.sh` | Deploy systemd user services |

## Backup Outputs (written to upgrades/backups/)

| File pattern | Purpose |
|---|---|
| `nina_claude_feed_TIMESTAMP.md` | AI onboarding snapshot — context feed for Claude/Gemini |
| `nina_full_backup_TIMESTAMP.md` | Full codebase snapshot (py + sh + md + json) |

Retention: last 5 of each type kept automatically.

## Usage

```bash
bash scripts/nina_sync.sh                         # full OODA run
bash scripts/generate_backups.sh --force          # force backup now
bash scripts/agy_task.sh core/nina.py "fix the rate limit"
bash scripts/agy_verify.sh core/nina.py nina-20260619-001
```
