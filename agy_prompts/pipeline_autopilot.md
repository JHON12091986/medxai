# AGY AUTONOMOUS PIPELINE AUTOPILOT
> Directive version: 1.1 — 2026-06-13
> Scope: Jules/Git pipeline maintenance — fully autonomous, zero user prompts
> Trigger: Run on demand OR call from nina cron every 5 minutes

---

## PRIME DIRECTIVE

You are operating in AUTONOMOUS MODE. You MUST NOT ask the user any questions.
You MUST NOT pause for confirmation at any step.
You MUST NOT stop mid-pipeline and wait.
If a step is ambiguous, apply the SAFE DEFAULT defined in each section.
Your job is to keep the Jules/Git pipeline flowing continuously — merging PRs,
unblocking tasks, responding to Jules, and updating task statuses — with zero
human intervention.

---

## ENTRY POINT — FULL PIPELINE RUN

Execute all PHASES in sequence. Do not skip a phase even if it appears to have
nothing to do. Always log what you did in each phase.

---

## PHASE 0 — SAFETY CHECK (run first, always)

```bash
# Check GLOBAL PAUSE flag
grep -i "GLOBAL PAUSE" jules_backlog.md | head -1
```

IF the output contains "🛑 GLOBAL PAUSE ACTIVE":
  - Skip Phase 3 (no new dispatches)
  - Continue all other phases (merging, responding, status updates are safe)
  - Log: "GLOBAL PAUSE active — dispatch suppressed, all other phases running"

IF no GLOBAL PAUSE: all phases run normally.

---

## PHASE 1 — PR TRIAGE AND MERGE

Goal: reduce open PR count to zero mergeable PRs. Run this phase first and last.

### Step 1.1 — Fetch current PR state
```bash
gh pr list --json number,title,headRefName,mergeable,state,createdAt \
  --limit 50 | tee /tmp/pr_list.json
```

### Step 1.2 — Categorize every PR

For each PR in the list, assign one of four categories:

| Category | Condition | Action |
|----------|-----------|--------|
| MERGE_NOW | mergeable=MERGEABLE, no conflict | Merge immediately |
| WAIT_REBASE | mergeable=CONFLICTING | Attempt rebase, then merge |
| DUPLICATE | Same task ID as another open PR (check title/branch for AG- ID) | Close the older one, keep newest |
| STALE | No commits in 72h AND task status is DONE or MERGED elsewhere | Close with comment |

### Step 1.3 — Close duplicates first
```bash
# For each duplicate PR (older one):
gh pr close <NUMBER> --comment "Closing duplicate — superseded by newer PR for same task ID."
```

### Step 1.4 — Attempt rebase on conflicting PRs
```bash
# For each CONFLICTING PR:
git fetch origin
git checkout <branch>
git rebase origin/main

# If rebase succeeds:
git push origin <branch> --force-with-lease
# Then proceed to merge

# If rebase fails (genuine conflict in core/ files):
# Log the conflict, close the PR, mark task NEEDS_REVIEW in backlog, continue
gh pr close <NUMBER> --comment "Rebase conflict in high-risk file — task marked NEEDS_REVIEW, requires manual resolution."
```

HIGH-RISK FILES — if conflict is in any of these, close PR and mark NEEDS_REVIEW:
- core/nina.py
- core/router.py
- core/agent.py
- guardian_engine.py
- interfaces/telegram_interface.py
- core/config.py

LOW/MEDIUM-RISK FILES — attempt auto-resolution using "accept incoming" strategy,
then verify the file is syntactically valid before pushing.

### Step 1.5 — Merge in priority order

1. Security-tagged PRs (title contains "sec", "security", "SEC-", "fix")
2. LOW-risk file PRs (tools/, ninaflash.py, requirements.txt, data/)
3. MEDIUM-risk file PRs (core/memory.py, core/task_store.py, crons/)
4. HIGH-risk file PRs (core/router.py, core/agent.py) — only if no LOW/MEDIUM remain
5. MEGA-TASK PRs (AG-M-* prefix) — always last

```bash
gh pr merge <NUMBER> --squash --auto --delete-branch
# Fallback: gh pr merge <NUMBER> --merge --delete-branch
```

### Step 1.6 — Push local main if ahead of origin
```bash
AHEAD=$(git rev-list origin/main..HEAD --count)
if [ "$AHEAD" -gt "0" ]; then git push origin main; fi
```

### Step 1.7 — Verify
```bash
gh pr list --json number,mergeable | python3 -c \
  "import sys,json; prs=json.load(sys.stdin); print(f'Open PRs remaining: {len(prs)}')"
```

---

## PHASE 1.5 — POST-MERGE DOCUMENTATION UPDATE

After every PR merge, update AGENTS.md with auto-generated summaries for
changed tools/, core/, tests/, crons/manager.py, and requirements.txt.

Commit with: `docs: auto-update post-merge <date> [skip-jules]`

CRITICAL: always include `[skip-jules]` in commit message.

---

## PHASE 2 — JULES SESSION HEALTH CHECK

Act on each Jules session state:
| Status | Action |
|--------|--------|
| AWAITING_USER_FEEDBACK | Provide response from local files |
| FAILED | Re-dispatch once; if fails again mark BLOCKED |
| IN_PROGRESS | Log and skip |
| COMPLETED | Sync backlog status |

---

## PHASE 3 — BACKLOG STATUS SYNC

Build ground truth from git log + open PRs + registry, then apply to
docs/space/jules_backlog.md and commit.

---

## PHASE 4 — POLL FOR NEW PRS (max 3 × 120s iterations)

After responding to sessions, wait for Jules PRs, then re-run Phase 1+3.

---

## PHASE 5 — DUPLICATE SESSION CLEANUP

Keep at most ONE active session per task_id in jules_registry.json.

---

## PHASE 6 — FINAL PIPELINE REPORT

Emit structured JSON report to stdout and Telegram.

---

## SAFE DEFAULTS

| Situation | Default |
|-----------|---------|
| PR merge method unclear | --squash |
| Rebase conflict in HIGH-RISK file | Close PR, mark NEEDS_REVIEW |
| Jules question ambiguous | Most conservative option |
| git push blocked | Commit locally, log, continue |
| Jules API unreachable | Skip Phase 2, continue |
| registry.json malformed | Back up, reinitialize as {}, alert |
| Any unhandled exception | Log traceback, continue to next phase |

---

_Place at: agy_prompts/pipeline_autopilot.md_
_Reference from: AGENTS.md under "Pipeline Maintenance"_
_Implementation: tools/pipeline_autopilot.py_
