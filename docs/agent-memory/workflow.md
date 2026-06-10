# NINA Agent Workflow

## Branch and PR Discipline
- **No direct commits to main.** `main` is the production-truth desk and must stay clean.
- Every active local executor or Jules task gets its own worktree/branch.
- Local executor default territory: `docs/space/*.md`, `AGENTS.md`, `nina_context.md`, `*.sh`, and single-file hotfixes on files not claimed by Jules.
- Jules default territory: multi-file work in `core/*.py`, `tools/*.py`, `interfaces/*.py`, `tests/*.py`.
- Shared but sequential only: `requirements.txt`, `data/*.json`.
- Forbidden parallel territory: `.env`, secrets, lock-sensitive runtime files.

## Sync Behavior
- **NINA Sync blocking:** Must block/defer pushes when Jules PR branches are open; prune stale remote refs before checking.
- The local executor runs `./nina_sync.sh` to deploy and export after every Jules PR merge.

## Rebase-Before-Work Rules
- Always rebase on origin/main before starting Jules tasks: `git fetch origin && git rebase origin/main`.

## Agent Coordination
- Local agents and Jules must NEVER edit the same file simultaneously.
- `jules_lock.txt` must always be read from and updated at the main worktree path: `~/nina/jules_lock.txt`.
- Per-task file territory must be explicit before parallel work begins.

---

## Surgical Merge Protocol (Mandatory for Jules PRs)

Jules is an async cloud agent that clones the repo at task-start time.
By the time Jules opens its PR, your local main may have moved ahead.
Merging Jules PRs blindly will frequently overwrite critical files
(AGENTS.md, nina_sync.sh, nina_update_log.md, high-risk tools).

**Use surgical merge whenever a Jules PR touches any critical file.**

### Critical files (always restore after a Jules PR merge):
- AGENTS.md
- nina_sync.sh
- nina_update_log.md
- tools/nina_dashboard.py
- tools/ninaflash.py
- interfaces/telegram_interface.py
- core/router.py
- main.py
- guardian_engine.py

### Surgical merge procedure (do this every time):
1. Backup critical files from current main BEFORE merging:
   cp ~/nina/AGENTS.md /tmp/AGENTS.md.bak
   cp ~/nina/nina_sync.sh /tmp/nina_sync.sh.bak
   cp ~/nina/nina_update_log.md /tmp/nina_update_log.md.bak

2. Inspect the PR diff before merging:
   gh pr diff <PR_NUMBER> --stat
   Identify which files the PR changes vs which are regressions.

3. Merge the PR:
   gh pr merge <PR_NUMBER> --squash --delete-branch
   git pull origin main

4. Immediately restore any critical files that regressed:
   cp /tmp/AGENTS.md.bak ~/nina/AGENTS.md
   cp /tmp/nina_sync.sh.bak ~/nina/nina_sync.sh
   (only restore files that Jules incorrectly reverted)

5. Commit the restoration:
   git add <restored-files>
   git commit -m "fix(<scope>): restore <file> after PR #<N> surgical merge"
   git push origin main

6. Run nina_sync.sh:
   cd ~/nina && ./nina_sync.sh

### When to use normal merge (no surgical steps needed):
- PR was based on very recent main (< 30 minutes old)
- PR only touches files Jules "owns": core/*.py, tools/*.py, tests/*.py
- PR does NOT touch any critical file in the list above
- gh pr view shows mergeable_state: clean

### Rule to encode for all agents:
"Never merge a Jules PR that touches AGENTS.md, nina_sync.sh, or
nina_update_log.md without first backing up the current main version
and restoring it if the merge introduces a regression."
