# NINA PR Resolver — Agent Reference

> **Created:** 2026-06-23 | **Author:** Perplexity Architect Overwatch  
> **Version:** 1.0.0 | **Status:** ACTIVE

This document is the canonical reference for `scripts/nina_pr_resolver.py` and the auto-merge pipeline. All coding agents (Jules, agy, opencode, Gemini) must read this before modifying any file in the PR pipeline.

---

## What It Does

`nina_pr_resolver.py` is called by `nina_sync.sh` A7 block whenever `OPEN_PRS > 0`. It evaluates every open PR against a decision matrix and either merges, rebases, or skips — one action per OODA cycle.

---

## Files Involved

| File | Role |
|---|---|
| `scripts/nina_pr_resolver.py` | Main resolver logic — evaluate + act |
| `scripts/nina_sync.sh` A7 block | Caller — invokes resolver instead of skip |
| `tools/surgical_merge.py` | Auto-rebase, verify_pr, and merge loop for open PRs |
| `tools/jules_dedup_guard.sh` | Pre-flight duplicate check; aborts Jules task if matching PR exists |
| `.github/workflows/jules_merge_guard.yml` | CI gate (runs full `tests/` suite on Jules PRs) + rollback tagger |
| `.github/workflows/duplicate_pr_check.yml` | Auto-labels duplicate PRs with `duplicate` label |
| `docs/space/pr_resolver_audit.md` | Append-only audit trail of every merge/skip decision |
| `docs/space/rollback_registry.md` | Auto-populated rollback tag registry (one entry per push to main) |

---

## Decision Matrix

| Condition | Verdict | Notes |
|---|---|---|
| `draft: true` | SKIP | GitHub draft PR |
| Label: `do-not-merge` | SKIP | Hard human override — never bypass |
| Label: `needs-review` | SKIP | Waiting for human review |
| Label: `wip` | SKIP | Work in progress |
| Label: `duplicate` | SKIP | Auto-set by `duplicate_pr_check.yml` |
| Label: `blocked` | SKIP | Manual block |
| `base != main` | SKIP | Only merge into main |
| `mergeable == null/UNKNOWN` | SKIP | GitHub still computing — retry next cycle |
| `mergeable == CONFLICTING` | SKIP + alert | Telegram alert fired |
| CI checks pending | SKIP | Wait for checks to complete |
| CI checks failing | SKIP + alert | Telegram alert fired |
| Branch > 10 commits behind | UPDATE_BRANCH | Rebase onto main, re-evaluate next cycle |
| Jules branch (`jules/` prefix) | MERGE | squash |
| Infra/repair keywords in title/body | MERGE | squash |
| Report/audit/chore keywords | MERGE | squash |
| No rule matched | SKIP | Logged only, no alert |

**ONE merge per OODA cycle.** After any merge or branch update, the script exits. The next cron run re-evaluates.

---

## Human Override

To prevent NINA from ever touching a PR, add the `do-not-merge` label on GitHub. The resolver checks this unconditionally before any other evaluation.

---

## Dry-Run Mode

```bash
python3 scripts/nina_pr_resolver.py --dry-run
```

Logs all decisions and writes to `pr_resolver_audit.md` with `Mode: DRY-RUN` marker. Does not merge or rebase anything.

---

## Audit Trail

Every decision (MERGE, SKIP, UPDATE_BRANCH) is appended to `docs/space/pr_resolver_audit.md`. Format:

```
## 2026-06-23 11:36 +06
- **MERGED** PR #360 | SHA: `549e93da`
- Reason: category=infra_repair
```

---

## CI Gate Coverage (`jules_merge_guard.yml`)

- **Trigger:** Any PR targeting `main` from a Jules branch
- **Test scope:** Full `tests/` directory (`pytest tests/ --tb=short -q`)
- **On failure:** Posts comment on PR + exits 1 (blocks merge)
- **On success:** PR is clear for auto-merge on next OODA cycle

---

## Rollback

Every push to `main` triggers `rollback-tagger` job in `jules_merge_guard.yml`. It:
1. Creates an annotated tag: `rollback/pr-{N}/{timestamp}`
2. Appends entry to `docs/space/rollback_registry.md`

To roll back to any point:
```bash
git checkout rollback/pr-360/20260623-113600
# or
git revert <SHA from rollback_registry.md>
```

---

## nina_sync.sh Integration (A7 block)

The A7 block in `nina_sync.sh` now reads:

```bash
if [[ "$OPEN_PRS" -gt 0 ]]; then
  log "open PRs detected ($OPEN_PRS) — running PR resolver…"
  PR_RESOLVER="$REPO_ROOT/scripts/nina_pr_resolver.py"
  if [[ -f "$PR_RESOLVER" ]]; then
    PY "$PR_RESOLVER" >> "$LOG" 2>&1 \
      && log "PR resolver complete" \
      || { alert "⚠️ PR resolver error — manual check needed"; log "PR resolver failed"; }
  else
    log "nina_pr_resolver.py not found — falling back to skip"
    alert "ℹ️ nina_sync skipped push — $OPEN_PRS open PR(s) pending review"
  fi
fi
```

---

## Contingency Coverage

| Contingency | Covered | How |
|---|---|---|
| Mergeable, no conflicts | ✅ | `mergeable == MERGEABLE` check |
| Conflicts with main | ✅ | `mergeable == CONFLICTING` → SKIP + alert |
| CI checks failing | ✅ | `conclusion == FAILURE` → SKIP + alert |
| CI checks pending | ✅ | `status == IN_PROGRESS` → SKIP |
| `do-not-merge` label | ✅ | Hard block, unconditional |
| `needs-review` label | ✅ | Hard block |
| `duplicate` label | ✅ | Set by `duplicate_pr_check.yml`, read here |
| Draft PR | ✅ | `draft: true` → SKIP |
| Multiple open PRs | ✅ | Oldest-first, one per cycle |
| Infra repair PR | ✅ | Keyword classification |
| Report-only PR | ✅ | Keyword classification |
| Jules PR | ✅ | Branch prefix detection |
| Stale branch (>10 behind) | ✅ | `UPDATE_BRANCH` verdict |
| mergeable still computing | ✅ | `null/UNKNOWN` → SKIP |
| Branch protection blocking | ✅ | GitHub enforces natively |
| Rollback after bad merge | ✅ | `rollback-tagger` workflow |

---

## Do NOT Modify

- `core/router.py` — not involved in PR resolution
- `.env` — resolver reads `config/telegram.cfg` only
- `guardian_engine.py` — not involved

---

## Version History

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-23 | Initial implementation — full contingency coverage |
