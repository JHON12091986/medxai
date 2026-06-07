---
name: nina-git
description: Git rules and commit conventions for the NINA repo. Load this for any git operations, commits, pushes, or file staging in ~/nina.
---

# NINA Git Policy

## The Hard Rules
- NEVER run `git add .` — always stage specific files only
- NEVER commit: `.env`, `data/memory/`, `logs/`, `*.bak*`, `*.save*`, `*.fix*`, `*.selfcheck*`
- NEVER commit without an ID in the message
- NEVER push a broken service — guardian must pass first

## Commit Format
```
type(scope): description (ID)
```
Types: `fix` | `feat` | `security` | `refactor` | `docs` | `chore`
Examples:
- `fix: wrap tool grammar in fallback guard (R-78)`
- `feat: add expenditure tracker tool (F-04)`
- `security: remove cat from shell allowlist (O-06)`

## Standard Git Sequence
```bash
cd ~/nina
git status
git add <specific files only>
git commit -m "type(scope): description (ID)"
git push origin main
```

## Before Every Push
- Guardian must pass
- nina.service must be active
- No secrets staged (`git status` check)
