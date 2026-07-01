# Slot 19 — GOVERN-003: GitHub Workflows Hardening
**Tier:** GOVERN | **Priority:** P2 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 4 → SURGICAL: B-010, P-29, P-32, P-35

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Which workflow files already exist?
ls .github/workflows/ 2>/dev/null

# SCAN 2: Do the specific ones exist?
test -f .github/workflows/duplicate_pr_check.yml && echo 'DUPE CHECK EXISTS'
test -f .github/workflows/dead_branch_cleanup.yml && echo 'DEAD BRANCH EXISTS'
test -f .github/workflows/jules_merge_guard.yml && echo 'MERGE GUARD EXISTS'

# SCAN 3: Does pre-merge test gate exist in jules_merge_guard?
grep -n 'pytest\|test.*gate\|pre.*merge' .github/workflows/jules_merge_guard.yml 2>/dev/null | head -5

# SCAN 4: Prior commits?
git log --oneline --all -- .github/workflows/ | head -10
```

**SKIP IF:** All 3 workflow files exist AND `jules_merge_guard.yml` contains a pytest gate.

**PARTIAL:** Create only missing workflow files.

---

## Task Execution

Create any missing workflow files:

1. **`duplicate_pr_check.yml`** — triggers on PR open. Checks for existing open PRs with >80% similar title (fuzzy match). Comments on PR if duplicate found.
2. **`dead_branch_cleanup.yml`** — runs weekly. Deletes branches with no commits in 14 days and no open PR.
3. **`jules_merge_guard.yml`** — runs on PR merge. Requires: `pytest` passes, `./guardian` passes, rollback tag created.

**Target files:** `.github/workflows/duplicate_pr_check.yml`, `.github/workflows/dead_branch_cleanup.yml`, `.github/workflows/jules_merge_guard.yml`

**Validation:**
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/duplicate_pr_check.yml'))"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/jules_merge_guard.yml'))"
./guardian
```

**PR title:** `ci: add duplicate PR check, dead branch cleanup, merge guard workflows`
