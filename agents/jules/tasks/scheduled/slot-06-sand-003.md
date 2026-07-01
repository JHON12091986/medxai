# Slot 06 — SAND-003: Sandboxed Exec Wrapper
**Tier:** INFRA | **Priority:** P1 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → SAND-003
**Dependency:** SAND-002 (Slot 05) must be DONE first

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does sandbox_exec.py exist with run_sandboxed?
test -f tools/sandbox_exec.py && grep -n 'run_sandboxed' tools/sandbox_exec.py

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'sandbox_exec\|run_sandboxed' | head -5

# SCAN 3: Dependency check
grep -n 'sanitize_sandbox_env' tools/sandboxed_shell.py 2>/dev/null || echo 'DEPENDENCY NOT MET'
```

**SKIP IF:** `tools/sandbox_exec.py` exists AND contains `run_sandboxed`

---

## Task Execution

**Goal:** Create `tools/sandbox_exec.py` with `run_sandboxed(command: List[str]) -> subprocess.CompletedProcess`. Uses `ResourceLimiter` and `sanitize_sandbox_env` from `tools/sandboxed_shell.py`. Uses `subprocess.run(shell=False)` with timeout=10.

**Target files:** `tools/sandbox_exec.py`, `tests/test_sandbox_exec.py`

**Validation:**
```bash
python3 -m py_compile tools/sandbox_exec.py tests/test_sandbox_exec.py
./venv/bin/pytest tests/test_sandbox_exec.py -v
./guardian
```

**PR title:** `feat(sandbox): implement sandboxed command wrapper`
