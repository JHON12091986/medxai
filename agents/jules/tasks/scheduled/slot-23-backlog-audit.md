# Slot 23 — BACKLOG-AUDIT: Daily Backlog Health Audit
**Tier:** BACKLOG | **Priority:** P2 | **Interval:** Every 12h (offset :00)
**Purpose:** This is the META task — Jules audits the backlog itself and updates status fields.

---

## Idempotency Scan

This task always runs (it is the audit itself). No skip condition.
But it must NOT create duplicate audit report lines.

```bash
# Check if today's audit report already exists
test -f docs/audit/$(date +%Y-%m-%d)_backlog_health.md && echo 'ALREADY RAN TODAY — skip if same date'
```

**SKIP IF:** Today's report already exists AND was written in the last 6 hours.

---

## Task Execution

**Goal:** Produce `docs/audit/YYYY-MM-DD_backlog_health.md` with the following sections:

### Section 1: Status Count
Read `docs/space/jules_backlog.md`. Count items by status:
- DONE (Section 1)
- PARTIAL (Section 2)
- TODO-P1, TODO-P2, TODO-P3 (Section 3)
- NEEDS SPEC (Section 3)
- READY (scattered READY items)
- SURGICAL tasks total
- Phase I Batch tasks total
- IDLE placeholder entries (Suggestion 1 / 2 only)
- IDLE entries with real content

### Section 2: Slot Coverage Check
For each of the 24 slots in `00_SLOT_REGISTRY.md`, check:
- Has a PR been merged for this task? (`git log | grep <task_id>`)
- If yes: mark DONE in this report
- If no: mark PENDING

### Section 3: READY Items Not Yet in Slots
List any `READY` backlog items that do NOT have a corresponding slot in `00_SLOT_REGISTRY.md`. These are candidates for new slots or manual Jules runs.

### Section 4: Stale READY Items
List READY items where `Date Promoted` is >7 days ago with no PR. Flag as STALE.

### Section 5: Recommendations
List top 3 unblocked tasks that should be dispatched to Jules next.

**Target files:** `docs/audit/YYYY-MM-DD_backlog_health.md` (write only)

**Commit message:** `audit(backlog): daily health report YYYY-MM-DD`

**No code changes. Documentation only.**
