# Slot 11 — PERF-001: Byte-Compilation and Cache Automation
**Tier:** PERF | **Priority:** P2 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → PERF-001

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does compile_extensions.py exist?
test -f tools/compile_extensions.py && grep -n 'compile_hotpaths' tools/compile_extensions.py

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'compile.*ext\|byte.*compil\|compile_hotpaths' | head -5

# SCAN 3: Is there already a py_compile-based utility elsewhere?
grep -rn 'py_compile\|compile_hotpaths' tools/ 2>/dev/null | grep -v '__pycache__'
```

**SKIP IF:** `tools/compile_extensions.py` exists AND contains `compile_hotpaths`

---

## Task Execution

**Goal:** Create `tools/compile_extensions.py` with `compile_hotpaths(directory: str) -> List[str]`.
- Uses Python's `py_compile` module to compile all `.py` files in the given directory
- Returns list of compiled `.pyc` paths
- Any `py_compile.PyCompileError` is caught per-file — does NOT stop execution
- Graceful degradation: if compilation fails, source import still works

**Target files:** `tools/compile_extensions.py`, `tests/test_compile_extensions.py`

**Validation:**
```bash
python3 -m py_compile tools/compile_extensions.py tests/test_compile_extensions.py
./venv/bin/pytest tests/test_compile_extensions.py -v
./guardian
```

**PR title:** `feat(perf): establish automatic byte-compilation utilities`
