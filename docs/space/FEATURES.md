# NINA Feature Registry

_Governed artifact. Every shipped feature documented here._
_Last updated: 2026-06-23_

---

## Feature Index

### Post-Resolver Git Reconcile (v1.0)
- **File:** `scripts/nina_sync.sh` (A7 block, v10.5)
- **Tag:** `NINA_FEATURE: post-resolver-reconcile v1.0`
- **What it fixes:** Before v10.5, after `nina_pr_resolver.py` merged a PR, local was
  permanently stuck ahead of the changed `origin/main`. No push ever happened.
- **How:** After resolver exits, A7 does: `git fetch origin main` → `git rebase origin/main`
  → `git push --no-verify`. 2-attempt retry loop with re-fetch between attempts.
- **Scope:** `nina_sync.sh` only — resolver never touches local git.

### PR Resolver v2.0 — CONFLICTING Handler
- **File:** `scripts/nina_pr_resolver.py`
- **Tag:** `NINA_FEATURE: pr-resolver-conflicting-handler v2.0`
- **Verdict:** `CLOSE_CONFLICTING`
- **What it does:** When `mergeable=CONFLICTING`, extracts pure-add files (`git diff --name-status A`)
  from the conflicting branch directly to main (no merge needed), commits them as
  `chore(rescue): cherry-pick pure-adds from conflicting PR #N`, then closes the PR
  and deletes the branch. No work is lost; no manual conflict resolution required.

### PR Resolver v2.0 — Duplicate PR Detection
- **File:** `scripts/nina_pr_resolver.py`
- **Tag:** `NINA_FEATURE: pr-resolver-duplicate-detection v2.0`
- **What it does:** Before per-PR evaluation, runs a duplicate pass using
  `difflib.SequenceMatcher` at 85% title similarity. Older PR closed with comment
  pointing to newer PR number. Branch deleted. PR list refreshed before evaluation.

### PR Resolver v2.0 — Branch Deletion
- **File:** `scripts/nina_pr_resolver.py`
- **Tag:** `NINA_FEATURE: pr-resolver-branch-deletion v2.0`
- **What it does:** After every `MERGE`, `CLOSE_CONFLICTING`, and `CLOSE_DUPLICATE`,
  calls `gh api --method DELETE /repos/{nwo}/git/refs/heads/{branch}`.
  Never deletes protected branches (`main`, `master`, `develop`, `dev`).

### PR Resolver v2.0 — Real commits_behind
- **File:** `scripts/nina_pr_resolver.py`
- **Tag:** `NINA_FEATURE: pr-resolver-real-commits-behind v2.0`
- **What it fixes:** Old code used `len(pr["commits"])` which is always the PR’s own
  commit count, not how far behind main the branch is.
- **How:** `git rev-list --count origin/main..origin/{head}` after fetching the branch.
  Falls back to commits array if fetch fails.

### post-push Log Stamp Guard (v1.0)
- **File:** `scripts/nina_sync.sh`
- **Tag:** `NINA_FEATURE: post-push-log-stamp-guard v1.0`
- **Effect:** `nina_update_log.md` is only appended if last entry is >60 seconds old — prevents double-write that re-dirtied the repo on next commit.

### ngit Transport + OODA Split (v1.0)
- **File:** `scripts/ngit.sh`
- **Tag:** `NINA_FEATURE: ngit-transport-split v1.0`
- **Usage:** `ngit "commit message"`
- **Effect:** Pure git transport (~20s). No hooks, no audits. OODA fires via post-push hook asynchronously.

### PR Auto-Resolver v1.0 (baseline)
- **File:** `scripts/nina_pr_resolver.py`
- **Tag:** `NINA_FEATURE: pr-auto-resolver v1.0`
- **Effect:** A7 calls resolver when `OPEN_PRS > 0`. Evaluates oldest-first.
  Verdicts: MERGE (squash) / UPDATE_BRANCH (rebase) / SKIP. One action per OODA cycle.
  Audit trail: `docs/space/pr_resolver_audit.md`.

### SSOT Registry v1.0
- **File:** `docs/space/nina_file_registry.json` + `tools/ssot_registry.py`
- **Tag:** `NINA_FEATURE: ssot-registry v1.0`
- **Effect:** Every file registered with purpose/ssot/symlinks/consumers/ast_exports/intj|intm/redundancy tuple.
  Orphan check, semantic dedup, INTJ/INTM drift detection on every OODA cycle.

### Idempotency Guards v1.0
- **File:** `scripts/nina_sync.sh` (`write_if_changed`)
- **Tag:** `NINA_FEATURE: idempotency-guards v1.0`
- **Effect:** All OODA artefact writes are hash-gated — file only updated if content changed.
  Prevents git dirty loop from artefact regeneration.

### NinaGate v1.0
- **File:** `tools/ninagate/main.py`
- **Tag:** `NINA_FEATURE: ninagate v1.0`
- **Effect:** OpenAI-compatible FastAPI gateway on port 8080.
  Ollama-local primary, cloud fallback. Used by MCP P0 bus.

### ninaMCP P0 GitHub Relay Bus
- **File:** `mcp/aliases.sh`
- **Tag:** `NINA_FEATURE: ninamcp-p0-relay v1.0`
- **Effect:** `nina_exec`, `nina_tail`, `nina_diff`, `nina_search`, `nina_status` aliases.
  Perplexity/Jules can execute NINA shell commands via GitHub MCP → file write → NINA poll.
