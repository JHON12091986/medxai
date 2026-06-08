# NINA Runbooks & Recovery

## Stale Branches
- Prune stale remote refs before checking for PRs or sync blocks.
- If a Jules branch is stale, local executor should coordinate re-planning or discarding rather than blind rebasing.

## NINA Sync Failure
- What to do when `nina_sync.sh` refuses to push: Check if there are open Jules PR branches. NINA Sync blocks pushes when Jules PRs are active. Merge or close the PR first.

## Local/Remote Drift
- Always use the local repository as the single source of truth for full code implementation.
- If local and remote diverge, rollback procedures should start from clean `main` in `~/nina` and rely on checked-in codebase state rather than `.latest.md` snapshot.

---

## Surgical Merge Recovery

If a Jules PR was merged without surgical steps and caused a regression:

1. Identify what was overwritten:
   git log --oneline -10
   git diff HEAD~1 HEAD -- AGENTS.md nina_sync.sh nina_update_log.md

2. Recover from Google Drive backup:
   rclone copy gdrive:nina-backup/nina_latest.md ~/nina/docs/space/
   Or restore from: /tmp/*.bak (if the session is still active)

3. Restore manually if no backup available:
   git show HEAD~1:AGENTS.md > ~/nina/AGENTS.md
   git add AGENTS.md
   git commit -m "fix(agents): rollback regression from stale Jules PR"
   git push origin main

4. Run nina_sync.sh to re-sync state:
   cd ~/nina && ./nina_sync.sh

5. Add the regressed rule as an explicit "do not touch" note to
   docs/agent-memory/architecture.md for future Jules tasks.
