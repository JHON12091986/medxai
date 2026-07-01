# Slot 21 — SURGICAL-DOCS: P-Series Documentation Tasks
**Tier:** BACKLOG | **Priority:** P3 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 4 → P-12, P-14, P-18, P-26, P-28

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Check which doc files already exist
test -f docs/space/jules_weekly_audit.md && echo 'P12: DONE'
test -f docs/space/perplexity_handoff.md && echo 'P14: DONE'
test -f docs/space/perplexity_request_template.md && echo 'P18: DONE'
test -f docs/space/nina_dashboard.html && echo 'P26: DONE'
test -f docs/space/nina_runbook.md && echo 'P28: DONE'

# SCAN 2: Prior commits for these docs?
git log --oneline --all -- docs/space/ | grep -i 'audit\|handoff\|runbook\|dashboard\|template' | head -10
```

**SKIP** any individual file that already exists with real content (>10 lines).
**Only create the MISSING ones.**

---

## Task Execution

Create any missing documentation files:

**P-12: `docs/space/jules_weekly_audit.md`**
First weekly audit table: columns = `PR#`, `Task ID`, `Status`, `Lines Changed`, `Guardian Pass`, `Notes`
Seed with data from recent merged PRs #195-#225.

**P-14: `docs/space/perplexity_handoff.md`**
Template for handing diagnosis tasks to Perplexity. Include: problem description field, files involved, error message, what was already tried, expected vs actual behavior.

**P-18: `docs/space/perplexity_request_template.md`**
Shorter template — the actual message text to paste to Perplexity. Include: repo context block, file listing, the question.

**P-26: `docs/space/nina_dashboard.html`**
Static HTML with auto-refresh (30s). Shows: last 5 guardian runs, open PR count, last sync timestamp, provider health (reads `data/provider_health.json` if exists).

**P-28: `docs/space/nina_runbook.md`**
Incident response runbook: sections = Service Down, High CPU, Router Failure, Jules Loop, Sync Failure, EWS Blocked.

**Target files:** only the missing files listed above in `docs/space/`

**Validation:**
```bash
# Each file must be >10 lines
for f in docs/space/jules_weekly_audit.md docs/space/perplexity_handoff.md docs/space/nina_runbook.md; do
  [ -f "$f" ] && wc -l "$f"
done
./guardian
```

**PR title:** `docs: add jules weekly audit, handoff templates, runbook, dashboard`
