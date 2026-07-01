# Task: Git Recon — Unpulled Commits

## Objective
Perform a reconnaissance of the `~/nina` repository.
Find all commits that exist on `origin/main` (GitHub) but have NOT been pulled to the local machine yet.
Report what changed, in which files, and give a risk assessment.

## Steps

1. Run `git fetch origin` to update remote refs without merging.
2. Run `git log HEAD..origin/main --oneline` to list unpulled commits.
3. For each unpulled commit, run `git show --stat <sha>` to see what files changed.
4. Summarize findings as a structured report:
   - Number of unpulled commits
   - Files changed (grouped by module: ninagate/, core/, opencode/, etc.)
   - Any changes that touch running services (ninagate/main.py, systemd units, config)
   - Risk level: LOW / MEDIUM / HIGH with reasoning
5. If there are unpulled commits that touch a running service, recommend: pull now or wait.

## Output Format

```
=== NINA GIT RECON REPORT ===
Date: <timestamp>
Branch: main
Unpulled commits: <N>

COMMITS:
  <sha> <message>
  ...

FILES CHANGED:
  ninagate/  : <N files>
  core/      : <N files>
  opencode/  : <N files>
  other/     : <N files>

RISK: LOW | MEDIUM | HIGH
REASON: <one line>
RECOMMENDATION: pull now | wait for maintenance window
=============================
```

## Context
- Working directory: `~/nina`
- Active services: ninagate (port 8080), nina-telegram, nina-mcp
- Pull is safe only if ninagate/main.py is NOT changed (or you are ready to restart)
