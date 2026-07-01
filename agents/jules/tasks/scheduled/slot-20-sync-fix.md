# Slot 20 — SYNC-FIX: nina_sync.sh Deduplication Guard
**Tier:** GOVERN | **Priority:** 🔴 P1 (CRITICAL) | **Interval:** Every 12h (offset :30)
**Backlog ref:** Known bug — routing history duplication. Commit `f3a2559` fixed the data damage.
**Related audit check:** B2 + E2 in `.jules/tasks/daily_discoverability_wiring_audit.md`

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does nina_sync.sh already have a dedup guard before routing history append?
grep -n 'dedup\|last_entry\|DEDUP\|diff.*prev\|compare.*last\|already.*appended' nina_sync.sh | head -10

# SCAN 2: Find the routing history write block
grep -n 'Routing History\|routing_history\|NinaGate Routing' nina_sync.sh | head -10

# SCAN 3: Check the primer file for current bloat ratio
grep -c '\[2026-' nina_context.md 2>/dev/null || echo 'Count not available'

# SCAN 4: Prior commits fixing nina_sync.sh?
git log --oneline --all -- nina_sync.sh | head -10
```

**SKIP IF:** A dedup guard already exists — specifically, a bash block that reads the last N lines of the routing history section and compares against the new entry before appending.

---

## Task Execution

**Goal:** Add a deduplication guard to the routing history append section of `nina_sync.sh`.

**Read `nina_sync.sh` IN FULL first (22 KB).** Find the exact line range where routing history is appended (search for `Routing History` or the primer file write).

**The fix pattern:**
```bash
# Before appending, check if the last entry is identical to the new entry
LAST_ENTRY=$(tail -n 20 "$PRIMER_FILE" | grep -A5 '\[2026-' | tail -5)
NEW_ENTRY="[$(date '+%Y-%m-%d')]..." # whatever the new entry format is
if [ "$LAST_ENTRY" = "$NEW_ENTRY" ]; then
  echo "[SYNC] Routing history entry unchanged — skipping duplicate append"
else
  # append the new entry
fi
```

Adapt the exact pattern to match `nina_sync.sh`'s actual variable names and primer file path.

**Target files:** `nina_sync.sh` only

**Validation:**
```bash
bash -n nina_sync.sh  # syntax check
# Manual test: run nina_sync.sh twice, confirm primer file does NOT grow on second run
./guardian
```

**PR title:** `fix(sync): add dedup guard to routing history append in nina_sync.sh`
