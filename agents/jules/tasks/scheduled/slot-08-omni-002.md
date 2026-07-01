# Slot 08 — OMNI-002: TUI Channel Mock Adapter
**Tier:** OMNI | **Priority:** P1 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → OMNI-002
**Dependency:** OMNI-001 (Slot 07) must be DONE first

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does tui_adapter.py exist?
test -f interfaces/tui_adapter.py && grep -n 'TUIAdapter\|TuiAdapter' interfaces/tui_adapter.py

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'tui.*adapter\|tui_adapter' | head -5

# SCAN 3: Dependency check
grep -n 'class BaseChannelAdapter' interfaces/base_adapter.py 2>/dev/null || echo 'DEPENDENCY NOT MET'
```

**SKIP IF:** `interfaces/tui_adapter.py` exists AND contains a class inheriting `BaseChannelAdapter`

---

## Task Execution

**Goal:** Create `interfaces/tui_adapter.py` inheriting `BaseChannelAdapter`. Uses an in-memory `asyncio.Queue` to buffer sent messages. `receive_message()` reads from the queue. Safe for test pipelines — no I/O.

**Target files:** `interfaces/tui_adapter.py`, `tests/test_tui_adapter.py`

**Validation:**
```bash
python3 -m py_compile interfaces/tui_adapter.py tests/test_tui_adapter.py
./venv/bin/pytest tests/test_tui_adapter.py -v
./guardian
```

**PR title:** `feat(omni): build standalone tui mock channel adapter`
