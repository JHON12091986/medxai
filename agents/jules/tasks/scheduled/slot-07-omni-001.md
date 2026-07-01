# Slot 07 — OMNI-001: Base Channel Adapter Interface
**Tier:** OMNI | **Priority:** P1 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → OMNI-001

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does base_adapter.py exist?
test -f interfaces/base_adapter.py && grep -n 'BaseChannelAdapter' interfaces/base_adapter.py

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'base.*adapter\|omni\|channel.*adapter' | head -5

# SCAN 3: CRITICAL — confirm telegram_interface.py is NOT touched
echo 'interfaces/telegram_interface.py is PROTECTED — never touch it'
```

**SKIP IF:** `interfaces/base_adapter.py` exists AND contains `class BaseChannelAdapter`

---

## Task Execution

**Goal:** Create `interfaces/base_adapter.py` with abstract base class `BaseChannelAdapter`.
- Use `abc.ABC` and `@abc.abstractmethod`
- Abstract methods: `async def send_message(self, chat_id, text, **kwargs)`, `async def receive_message(self)`
- Must NOT inherit from or modify `interfaces/telegram_interface.py`

**CRITICAL:** `interfaces/telegram_interface.py` is PROTECTED. Create a SEPARATE new file only.

**Target files:** `interfaces/base_adapter.py`, `tests/test_base_adapter.py`

**Validation:**
```bash
python3 -m py_compile interfaces/base_adapter.py tests/test_base_adapter.py
./venv/bin/pytest tests/test_base_adapter.py -v
./guardian
```

**PR title:** `feat(omni): introduce abstract base channel adapter`
