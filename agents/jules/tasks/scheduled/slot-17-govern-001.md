# Slot 17 — GOVERN-001: Jules Guard Hardening
**Tier:** GOVERN | **Priority:** P2 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 4 → SURGICAL: B-007, P-27, P-31, P-34, P-36, P-38

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Current state of jules_guard.py
wc -l core/jules_guard.py
grep -n 'def ' core/jules_guard.py | head -20

# SCAN 2: Which of the required functions already exist?
grep -n 'detect_loop\|validate_task_spec\|requires_human_action\|check_before_jules_submit\|append_audit\|rate_limit' core/jules_guard.py

# SCAN 3: Prior commits adding to jules_guard?
git log --oneline --all -- core/jules_guard.py | head -10
```

**SKIP IF:** All 5 required functions already present: `detect_loop`, `validate_task_spec`, `check_before_jules_submit`, `append_audit`, and rate-limiting logic.

**PARTIAL:** If some are present but not all — implement only the MISSING ones.

---

## Task Execution

Read `core/jules_guard.py` FIRST (8 KB). Add any missing functions:

1. **`detect_loop(error_id: str) -> bool`** — checks if same error_id has been attempted >3 times in past 24h. Reads from `nina_state.json`. Sends Telegram alert on loop detection.
2. **`validate_task_spec(task: str) -> dict`** — enforces: single file target, line numbers present, <500 words, no secrets in task text.
3. **`check_before_jules_submit(error_id: str, open_prs: list) -> bool`** — returns True if task should be skipped (duplicate PR open, loop detected, or already done).
4. **`append_audit(entry: dict)`** — appends JSON line to `docs/space/nina_audit_log.jsonl`.
5. **Rate limit logic** — max 10 Jules dispatches per day using `nina_state.json` counter.

**Target files:** `core/jules_guard.py` only

**Validation:**
```bash
python3 -m py_compile core/jules_guard.py
pyflakes core/jules_guard.py
./guardian
```

**PR title:** `feat(govern): harden jules_guard with loop detection, task validation, rate limits`
