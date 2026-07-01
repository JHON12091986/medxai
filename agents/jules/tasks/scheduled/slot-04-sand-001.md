# Slot 04 — SAND-001: Safe Subshell Resource Guard
**Tier:** INFRA | **Priority:** P1 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → SAND-001

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does sandboxed_shell.py exist with ResourceLimiter?
test -f tools/sandboxed_shell.py && grep -n 'ResourceLimiter' tools/sandboxed_shell.py

# SCAN 2: Any prior commit?
git log --oneline --all | grep -i 'sandbox\|resource.*limit\|sandboxed_shell' | head -5

# SCAN 3: Test file?
test -f tests/test_sandboxed_shell.py && echo EXISTS

# SCAN 4: Ensure we are NOT touching tools/shell.py (protected)
echo 'tools/shell.py is PROTECTED — never touch it'
```

**SKIP IF:** `tools/sandboxed_shell.py` exists AND contains `class ResourceLimiter`

---

## Task Execution

**Goal:** Create `tools/sandboxed_shell.py` with a `ResourceLimiter` context manager using Python's UNIX `resource` module.
- Max virtual memory: 512 MB
- Max CPU time: 5 seconds
- Max file write size: 10 MB

**CRITICAL:** `tools/shell.py` is PROTECTED. Create a NEW file `tools/sandboxed_shell.py`. Do NOT modify `tools/shell.py` in any way.

**Target files:** `tools/sandboxed_shell.py`, `tests/test_sandboxed_shell.py`

**Validation:**
```bash
python3 -m py_compile tools/sandboxed_shell.py tests/test_sandboxed_shell.py
./venv/bin/pytest tests/test_sandboxed_shell.py -v
./guardian
```

**PR title:** `feat(sandbox): implement safe subshell resource limits`
