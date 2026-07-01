# Slot 09 — OMNI-003: Standardize Message Parser and Dispatcher
**Tier:** OMNI | **Priority:** P1 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → OMNI-003
**Dependency:** OMNI-002 (Slot 08) must be DONE first

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does adapter_parser.py exist?
test -f interfaces/adapter_parser.py && grep -n 'UnifiedMessage' interfaces/adapter_parser.py

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'adapter.*parser\|unified.*message\|adapter_parser' | head -5

# SCAN 3: Dependency check
grep -n 'class.*BaseChannelAdapter\|TUIAdapter' interfaces/ -r 2>/dev/null | head -3 || echo 'DEPENDENCY NOT MET'
```

**SKIP IF:** `interfaces/adapter_parser.py` exists AND contains `UnifiedMessage` dataclass

---

## Task Execution

**Goal:** Create `interfaces/adapter_parser.py` with `UnifiedMessage` dataclass (fields: `sender_id`, `chat_id`, `timestamp`, `text`, `metadata`) and a `parse_event(raw_dict) -> UnifiedMessage` function that tolerates missing or extra fields.

**Target files:** `interfaces/adapter_parser.py`, `tests/test_adapter_parser.py`

**Validation:**
```bash
python3 -m py_compile interfaces/adapter_parser.py tests/test_adapter_parser.py
./venv/bin/pytest tests/test_adapter_parser.py -v
./guardian
```

**PR title:** `feat(omni): standardize messaging adapter formats`
