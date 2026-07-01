# Slot 05 — SAND-002: Environment Variable Stripper and Guard
**Tier:** INFRA | **Priority:** P1 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → SAND-002
**Dependency:** SAND-001 (Slot 04) must be DONE first

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does sanitize_sandbox_env exist?
grep -n 'sanitize_sandbox_env' tools/sandboxed_shell.py 2>/dev/null

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'sandbox.*env\|env.*strip\|sanitize.*sandbox' | head -5

# SCAN 3: Dependency check
grep -n 'class ResourceLimiter' tools/sandboxed_shell.py 2>/dev/null || echo 'DEPENDENCY NOT MET'
```

**SKIP IF:** `sanitize_sandbox_env` already exists in `tools/sandboxed_shell.py`

---

## Task Execution

**Goal:** Add `sanitize_sandbox_env(env_dict: dict) -> dict` to `tools/sandboxed_shell.py`. Strips all keys matching `*API_KEY*`, `*TOKEN*`, `*SECRET*`, `*PASSWORD*`, `*DB_*`. Keeps only whitelisted keys: `PATH`, `LANG`, `PYTHONPATH`, `HOME`, `USER`.

**Target files:** `tools/sandboxed_shell.py`, `tests/test_sandboxed_shell.py`

**Validation:**
```bash
python3 -m py_compile tools/sandboxed_shell.py
./venv/bin/pytest tests/test_sandboxed_shell.py -v
./guardian
```

**PR title:** `feat(sandbox): configure safe environmental stripper`
