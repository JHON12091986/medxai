# NINA Safety Rules — Universal (All Agents)
## updated: 2026-06-16
## source: ARCHITECTURE.md + nina_error_register.md

## High-Risk Files — Never Touch Without Explicit Spec
- .env
- interfaces/telegram_interface.py
- core/router.py
- main.py
- guardian_engine.py
- tools/shell.py
- ninagate/main.py

## Post-Edit — Always Run (every single file change)
python3 -m py_compile <file>
pyflakes <file>

## Post-Merge — No Exceptions
cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh

## Commit Prefix Convention
fix(scope):   bug fix, references ID from nina_error_register.md
feat(scope):  new capability
ops:          infrastructure, services, deployment
chore:        maintenance, cleanup
docs:         documentation only
sec:          security fix
infra:        system/environment level
core:         orchestrator or router level

## One File Per PR Rule
Never batch multiple task wires into one PR.
Each PR addresses exactly one Task ID.

## Merge Conflict Rule
Stop immediately. Do not resolve blindly.
Report to Perplexity (ARCHITECT role) before touching anything.

## Redundancy Check Before Any Fix
1. Check nina_error_register.md — if ID is marked FIXED, skip it.
2. Check jules_backlog.md — if identical scope is already READY, skip it.
3. Check nina_update_log.md last 5 entries — if fix already landed, skip it.

## Restricted Environment & Symlink Troubleshooting
If running in a restricted sandbox (like Google's Jules runner) where filesystem symlinks fail or checkout crashes:
1. Configure git to ignore symlinks during clone/checkout: `git config --global core.symlinks false`
2. Once checked out, run: `python3 tools/resolve_git_symlinks.py` to reconstruct/copy symlink contents on disk.

## Session Memory Rule
At the start of every session, read docs/context/nina_session_log.md (last 5 entries). At the end of every completed task, append a new entry using the standard format. Never edit or delete past entries.
