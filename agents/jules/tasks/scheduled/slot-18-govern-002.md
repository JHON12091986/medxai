# Slot 18 — GOVERN-002: Crons Manager Hardening
**Tier:** GOVERN | **Priority:** P2 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 4 → SURGICAL: B-009, B-011, P-37

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: What jobs already exist in crons/manager.py?
grep -n 'stale_pr_cleanup\|jules_audit\|nina_healthcheck\|add_job\|scheduler.add' crons/manager.py | head -20

# SCAN 2: Prior commits to crons/manager.py?
git log --oneline --all -- crons/manager.py | head -5

# SCAN 3: Current line count
wc -l crons/manager.py
```

**SKIP IF:** All 3 jobs already registered: `stale_pr_cleanup` (24h), `jules_audit` (weekly), `nina_healthcheck` (6h)

**PARTIAL:** Add only the missing jobs.

---

## Task Execution

Read `crons/manager.py` FIRST. Understand existing APScheduler setup. Add ONLY the jobs that are missing:

1. **`stale_pr_cleanup`** — every 24h with 15min jitter. Closes PRs open >72h with no activity.
2. **`jules_audit`** — every Monday 08:00. Queries Jules API for task success rates, writes to `docs/space/jules_weekly_audit.md`.
3. **`nina_healthcheck`** — every 6h. Runs `healthcheck.py` and writes result to `nina_state.json`.

**Target files:** `crons/manager.py` only

**Validation:**
```bash
python3 -m py_compile crons/manager.py
pyflakes crons/manager.py
./guardian
```

**PR title:** `feat(crons): add stale_pr_cleanup, jules_audit, nina_healthcheck jobs`
