# Slot 14 — OBS-002: Test-Exempt Classifications in Governance Validation
**Tier:** OBS | **Priority:** P2 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → OBS-002
Also covers: Section 3 → 🔴 TODO-P1 Governance Index Auto-Update

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does validate_index.py already handle test_exempt?
grep -n 'test_exempt\|test_exempt.*true\|exemp' tools/validate_index.py 2>/dev/null

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'test.*exempt\|validate.*index\|governance.*exempt' | head -5

# SCAN 3: Current warning count in validate_index
python3 tools/validate_index.py 2>&1 | tail -5 || echo 'Script not runnable standalone'
```

**SKIP IF:** `tools/validate_index.py` already processes `test_exempt: true` flag without emitting warnings

---

## Task Execution

**Goal:** Update `tools/validate_index.py` to recognise `"test_exempt": true` in governance index entries and suppress the test coverage warning for those files.

**Read `tools/validate_index.py` FIRST** — understand its current structure before modifying.

**Target files:** `tools/validate_index.py`, `tests/test_validate_index.py`

**Validation:**
```bash
python3 -m py_compile tools/validate_index.py
./venv/bin/pytest tests/test_validate_index.py -v
./guardian
```

**PR title:** `feat(governance): support test_exempt files in index validation`
