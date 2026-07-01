# ngit + sync Architecture

_SSoT for Nina git transport, OODA brain, and PR lifecycle split._
_Last updated: 2026-06-23 | Author: M. Baizid Alam_
_Status: **LIVE** ✔_

---

## TL;DR

```
You type:  ngit "fix: something"          ← the only command you need
               │
               ▼
           pure git transport (ngit.sh)
           stage → commit → pull → push --no-verify
               │
               ▼  post-push hook fires automatically
               ▼
           OODA brain (nina_sync.sh) runs in background
           detects delta → runs only needed audits
               │
               ▼  if open PRs exist
               ▼
           PR resolver (nina_pr_resolver.py)
           evaluates → merges / rebases / closes / rescues
               │
               ▼  post-resolver reconcile (A7 v10.5)
               ▼
           fetch → rebase local → push
               │
               ▼
           Telegram alert
```

**You only ever type two commands:**

| Command | When |
|---|---|
| `ngit "message"` | You made changes |
| `sync` | Manual health check / after external pull |

---

## Single Responsibility Split

### `ngit` — Pure Git Transport (`scripts/ngit.sh`)

**One job: get your local commits to remote.**

- Stage all → commit → pull (autostash) → push `--no-verify`
- Both stage-1 and stage-2 pushes use `--no-verify` — hooks never fire
- Untrack secrets (`.env`, `.env.local`) and gitignored-but-cached files
- Offline detection → local commit only, clean exit
- Log: `runtime/logs/ngit.log`

**Does NOT:** run OODA, audits, index regen, Telegram, service restart, touch GitHub PRs.

---

### `sync` — OODA Brain (`scripts/nina_sync.sh` v10.5)

**One job: maintain repo hygiene and Nina health.**

- Full OODA: Observe → Orient → Decide → Act
- Delta-detects what changed (only runs needed steps)
- Dead code scan (vulture), dedup, symlinks, registry orphans, INTJ/INTM drift
- Service restart if `.py` changed
- Telegram alerts on every event
- Commits + pushes artefacts with `--no-verify`
- Log: `runtime/logs/nina_sync.log`

**A7 (v10.5 — post-resolver reconcile):**
After `nina_pr_resolver.py` exits, `nina_sync.sh` A7 re-fetches `origin/main`,
rebases local artefact commits on top, then pushes. This closes the gap where
local would stay permanently ahead of a changed remote after a PR merge.

```
A7 flow (v10.5):
  resolver exits (merged / updated-branch / skipped)
      │
      ▼
  git fetch origin main         ← pick up whatever resolver changed on GitHub
      │
      ▼
  git rebase origin/main        ← put local A6 artefact commit on top
      │
      ▼
  git push --no-verify          ← local fully synced, not stuck ahead
```

**Triggered by:** `sync` (manual), post-push hook (auto after ngit), cron, systemd.

---

### `nina_pr_resolver.py` — PR Surgeon (`scripts/nina_pr_resolver.py` v2.0)

**One job: resolve open GitHub PRs autonomously. GitHub-side only. Never touches local git files.**

| Verdict | Condition | Action |
|---|---|---|
| `CLOSE_DUPLICATE` | Title similarity ≥85% (SequenceMatcher) | Close older PR, delete branch |
| `SKIP` | Draft / do-not-merge / blocked label | Log and move on |
| `CLOSE_CONFLICTING` | `mergeable=CONFLICTING` | Cherry-pick pure-add files → close PR → delete branch |
| `SKIP` | `mergeable=UNKNOWN/null` | Wait for GitHub to recompute |
| `SKIP` | CI pending | Wait for checks |
| `SKIP` | CI failing | Alert + wait |
| `UPDATE_BRANCH` | Branch >10 commits behind main (real `rev-list` count) | `gh pr update-branch --rebase` |
| `MERGE` | Category: `jules_task` / `infra_repair` / `report_only` | Squash-merge + delete branch |
| `SKIP` | No rule matched | Human review needed |

**Safety guarantees:**
- ONE merge/close per invocation (exits after first action)
- `do-not-merge` label = unconditional human override
- `mergeable=null/UNKNOWN` = always SKIP (never merge a PR GitHub hasn’t computed)
- Branch deletion always attempted after merge or close (never deletes `main`/`master`/`develop`/`dev`)
- `--dry-run` flag available for safe testing
- Audit trail: `docs/space/pr_resolver_audit.md` (append-only)

**Does NOT:** run `git push`, modify local files, run audits, restart services.

---

## Why Not Merge All Three?

| | `ngit` | `sync` | `resolver` |
|---|---|---|---|
| **Speed** | ~20s | ~60s | ~10s |
| **Scope** | local git | local hygiene | GitHub API |
| **Blocking?** | You wait | Async background | Async via A7 |
| **Owns push?** | Yes (your commits) | Yes (artefacts + post-resolver) | No |
| **Knows PRs?** | No | Count only (OBSERVE) | Yes, full lifecycle |

Separating them means:
- `ngit` is always instant — no audit ever blocks your push
- `sync` handles hygiene async, never races with ngit
- `resolver` handles GitHub surgery in isolation — no local state pollution

---

## Hook Architecture

| Hook | Fires when | Does |
|---|---|---|
| `pre-commit` | Direct `git commit` (Cursor, agy, Jules) | OODA audit in background |
| `pre-push` | Manual `git push` without `--no-verify` | Governance audit in background |
| `post-push` | **After every successful push** | Fires `nina_sync.sh post-push` in background |

**ngit bypasses all hooks** via `--no-verify`. OODA still runs via `post-push` automatically.

---

## git autostash

```bash
git config pull.autostash true
```

Prevents `cannot pull with rebase: You have unstaged changes` errors.
Git automatically stashes dirty files before rebase, pops them after.
Set once per machine. Already set on VivoBook.

---

## Aliases (`config/.bashrc_nina`)

```bash
alias ngit='bash ~/nina/scripts/ngit.sh'           # git transport
alias sync='bash ~/nina/scripts/nina_sync.sh all'  # OODA brain
alias npush='bash ~/nina/scripts/ngit.sh'          # legacy muscle memory

alias nstart='systemctl --user start nina'
alias nstop='systemctl --user stop nina'
alias nrestart='systemctl --user restart nina'
alias nstatus='systemctl --user status nina'
alias nlog='journalctl --user -u nina -f'

alias ngit-log='tail -f ~/nina/runtime/logs/ngit.log'
alias sync-log='tail -f ~/nina/runtime/logs/nina_sync.log'
alias resolver-log='grep pr_resolver ~/nina/logs/nina_sync.log | tail -30'
```

Setup (one-time):
```bash
echo 'source ~/nina/config/.bashrc_nina' >> ~/.bashrc
git -C ~/nina config pull.autostash true
source ~/.bashrc
```

---

## Full Flow Diagram

```
┌──────────────────────────────────────────────────────┐
│ YOU EDITED FILES                                     │
│                                                      │
│  ngit "fix: something"                               │
│   ├ stage all (excl .push_in_flight, .env)           │
│   ├ commit                                           │
│   ├ pull --rebase (autostash dirty files)            │
│   ├ push --no-verify  [stage 1]                      │
│   └ push --no-verify  [stage 2, if hook left commits] │
│                                                      │
│  ✔ Done in ~20s                                      │
└──────────────────────────────────────────────────────┘
               │ post-push hook fires
               ▼
┌──────────────────────────────────────────────────────┐
│ OODA BRAIN (background, non-blocking)                │
│                                                      │
│  sync (nina_sync.sh v10.5)                           │
│   ├ OBSERVE: fetch, git state, open_prs count        │
│   ├ ORIENT:  delta SHA diff (what actually changed)  │
│   ├ DECIDE:  which audits are needed                 │
│   ├ ACT A0-A6: symlinks, registry, dedup, dead code, │
│   │            INTJ/INTM drift, backup, commit       │
│   └ ACT A7: PR resolver → reconcile → push           │
│        │                                             │
│        ├ if open PRs: run nina_pr_resolver.py         │
│        │   ├ CLOSE_DUPLICATE (title sim ≥85%)         │
│        │   ├ CLOSE_CONFLICTING (cherry-pick + close)  │
│        │   ├ UPDATE_BRANCH (>10 commits behind)       │
│        │   └ MERGE (squash) → delete branch          │
│        └ fetch → rebase → push (reconcile v10.5)     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ EXTERNAL CHANGES (Jules / agy / Gemini pushed)       │
│                                                      │
│  sync                                                │
│   ├ pulls latest                                     │
│   ├ detects changed files                            │
│   ├ restarts service if .py changed                  │
│   └ Telegram: ✔ done                                 │
└──────────────────────────────────────────────────────┘
```

---

## Related Files

| File | Role |
|---|---|
| `scripts/ngit.sh` | Pure transport implementation |
| `scripts/nina_sync.sh` | OODA brain v10.5 — orchestrator + post-resolver reconcile |
| `scripts/nina_pr_resolver.py` | PR surgeon v2.0 — GitHub-side lifecycle manager |
| `config/.bashrc_nina` | All aliases incl. `resolver-log` |
| `config/README.md` | Setup instructions |
| `git-hooks/post-push` | Fires sync after push |
| `git-hooks/pre-commit` | Fires OODA on direct commits |
| `git-hooks/pre-push` | Governance for external pushes |
| `runtime/logs/ngit.log` | ngit run log |
| `logs/nina_sync.log` | sync/OODA/resolver run log |
| `docs/space/pr_resolver_audit.md` | Append-only PR resolution audit trail |
