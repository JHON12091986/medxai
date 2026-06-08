# NINA Runbooks & Recovery

## Stale Branches
- Prune stale remote refs before checking for PRs or sync blocks.
- If a Jules branch is stale, local executor should coordinate re-planning or discarding rather than blind rebasing.

## NINA Sync Failure
- What to do when `nina_sync.sh` refuses to push: Check if there are open Jules PR branches. NINA Sync blocks pushes when Jules PRs are active. Merge or close the PR first.

## Local/Remote Drift
- Always use the local repository as the single source of truth for full code implementation.
- If local and remote diverge, rollback procedures should start from clean `main` in `~/nina` and rely on checked-in codebase state rather than `.latest.md` snapshot.
