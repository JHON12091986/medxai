# NINA Parallel Workflow — Human-Readable Guide
# Last updated: 2026-06-07

---

## The 3-Tool Operating Model

NINA uses three tools running IN PARALLEL as the standard operating mode.
Each tool has a fixed role and execution mode — they do not overlap.

| Tool                    | Role                  | Mode                                      |
|-------------------------|-----------------------|-------------------------------------------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Active throughout the session             |
| Google Jules            | ASYNC CLOUD CODER     | Fire-and-forget — builds features via PRs |
| Antigravity CLI (agy)   | LOCAL MUSCLE          | Sync executor — merges, deploys, fixes    |

---

## The Full Parallel Loop (Step-by-Step)

1. **Perplexity** diagnoses the issue and writes a precise task spec
2. **Jules** receives the spec → builds in cloud async (no interaction after submit)
3. **agy** handles any urgent local fixes in parallel, on its own worktree
4. **Jules** opens a PR when its build is complete
5. **agy** reviews the Jules PR diff, runs lint + compile checks, merges to `main`
6. **agy** runs `./nina_sync.sh` to deploy and export
7. **Perplexity** reviews the result (attach `nina_latest.md` to a new thread)

---

## Key Distinctions

- **agy is NOT just a fixer** — it is the local merge and deploy executor
- **Jules does NOT merge its own PRs** — agy always performs the merge after review
- **Perplexity is NOT idle during coding** — it remains available for unblocking and mid-task review

---

## agy as Merge Executor (Mandatory Rule)

- agy is responsible for ALL Jules PR merges — never auto-merge via the GitHub UI
- **Before every merge:**
  1. Check `jules_lock.txt` — confirm no conflict
  2. Run `python3 -m py_compile <changed_file>` on every `.py` file in the PR
  3. Run `pyflakes <changed_file>` on the same files
  4. Review the PR diff for high-risk file touches
- **After every merge:** run `./nina_sync.sh` — no exceptions
- **If merge conflict:** stop, report to Perplexity for re-spec; do not attempt blind resolution

---

## Branch Lanes

| Branch Pattern              | Purpose                                              |
|-----------------------------|------------------------------------------------------|
| `main`                      | Production truth — review, merge, sync only          |
| `agy/<task-id>-<slug>`      | Local docs, shell, single-file hotfixes, policy work |
| `jules/<task-id>-<slug>`    | Multi-file features, refactors, async PR builds      |
| `review/<id>` *(optional)*  | Isolated test/review/merge prep                      |

---

## Territory Rules

| Owner | Default Files                                                     |
|-------|-------------------------------------------------------------------|
| agy   | `docs/space/*.md`, `AGENTS.md`, `nina_context.md`, `*.sh`, hotfixes on unlocked files |
| Jules | `core/*.py`, `tools/*.py`, `interfaces/*.py`, `tests/*.py`        |
| Sequential only | `requirements.txt`, `data/*.json`                      |
| Never parallel  | `.env`, secrets, lock-sensitive runtime files           |

---

## Session Start Checklist

1. Start from clean `main` in `~/nina`
2. Run `./nina_sync.sh`
3. Read `jules_lock.txt` — confirm no locked files conflict with your task
4. Create branch + worktree for each parallel task
5. Record claimed files in `~/nina/jules_lock.txt`
6. Launch agy and Jules only after territories are confirmed non-overlapping

---

## Session Close Checklist

1. agy commits only its branch/worktree
2. Jules opens PR only from its branch/worktree
3. agy reviews and merges PRs one at a time into `main`
4. Pull updated `main` into remaining worktrees before further edits
5. Run `./nina_sync.sh` from `main`
6. Clear `jules_lock.txt` (`JULES_TASK=`, `LOCKED_FILES=`)
7. Delete finished worktrees and review branches
