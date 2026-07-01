# Nina Runbook — Single Source of Truth
_auto-maintained · last updated by OODA loop_

## One Command to Rule All
```bash
bash scripts/nina_sync.sh
```
This is the ONLY command any agent (Jules, agy, Gemini, Cursor, OpenCode, Perplexity, cron) needs to call. It runs a full OODA loop and handles everything below automatically.

## OODA Loop Phases

| Phase | What happens |
|---|---|
| **OBSERVE** | Snapshot SHA, count open PRs, dirty files, stash depth |
| **ORIENT** | Safe-pull (stash→rebase×3→pop), hooks reinstall, detect what changed |
| **DECIDE** | Flag: need index regen? doc audit? dead-code scan? dup check? service restart? |
| **ACT** | Execute only flagged actions → commit artefacts → push → restart service |

## Modes
```bash
bash scripts/nina_sync.sh            # full OODA (default)
bash scripts/nina_sync.sh pull-only  # safe pull + hooks, no push
bash scripts/nina_sync.sh push-only  # commit + push, skip pull
bash scripts/nina_sync.sh audit      # deep scan (dead-code + dups), no push
bash scripts/nina_sync.sh hooks      # reinstall git hooks only
```

## What Gets Automated on Every Run
- Git hooks reinstalled (pre-commit, pre-push)
- Safe pull with 3-retry rebase + stash pop
- `nina_index.json` + `nina_index.md` regenerated if any `.py/.md/.json/.sh` changed
- `nina_repo_hygiene_dashboard.md` rewritten (stale docs, large files, open PRs)
- Dead-code scan via `vulture` (weekly, or `audit` mode)
- Duplicate file hash scan (weekly, or `audit` mode)
- All artefacts auto-staged + committed with `--no-verify`
- Push skipped if open PRs exist (Telegram alert sent)
- `nina.service` restarted if `.py` or `.service` files changed
- Crash trap → Telegram alert on any `ERR`

## Contingency Table

| Scenario | Handled by |
|---|---|
| Dirty index from any agent | Auto-stash before pull |
| Stash pop conflict | `checkout --` + `stash drop` |
| Pull fails 3× | Alert + continue with local state |
| Push rejected (remote ahead) | Pull-rebase + retry once |
| Stash pile-up (>20) | `git stash clear` auto |
| `nina.service` unresponsive | `systemctl --user restart` |
| Open PRs during push | Skip push + Telegram alert |
| `update_index.py` not found | Warning only, non-fatal |
| `vulture` not installed | Warning only, skip scan |
| Crash anywhere | ERR trap → Telegram alert |
| PYTHONPATH wrong | Injected via `PY()` helper |
| Duplicate Jules PR dispatch | `tools/jules_dedup_guard.sh` + pre-flight check in `tools/jules.py` |
| Hooks missing post-clone | Phase 0 reinstalls always |

## Agents — Who Does What

| Agent | Role | Calls sync? |
|---|---|---|
| **Baizid** | Owner / final decisions | `bash scripts/nina_sync.sh` |
| **Jules** | Code implementation via PRs | Perplexity triggers sync post-merge |
| **agy** | Autonomous task runner | Calls sync after each task |
| **Gemini** | Spec & design | Perplexity triggers sync after writes |
| **Cursor/OpenCode** | Local IDE edits | `bash scripts/nina_sync.sh` before close |
| **Perplexity** | Architect Overwatch | Read-only via GitHub MCP; triggers sync via instruction |
| **cron/systemd** | Scheduled | `OnCalendar=*:0/30` → `nina_sync.sh` |

## Service Management
```bash
systemctl --user status nina.service
systemctl --user restart nina.service
journalctl --user -u nina.service -f
```
NEVER use `sudo systemctl` — always `systemctl --user`.

## Logs
```
logs/nina_sync.log          # per-run OODA trace
logs/dead_code_report.txt   # vulture output (weekly)
logs/duplicate_files.txt    # md5 dup scan (weekly)
```
