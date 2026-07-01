# Slot 01 — VAULT-001: Scoped Credential Vault Engine
**Tier:** INFRA | **Priority:** P1 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → VAULT-001

---

## Idempotency Scan (RUN FIRST — before any code change)

```bash
# SCAN 1: Does the target file already exist with real content?
test -f core/vault.py && wc -l core/vault.py

# SCAN 2: Does it contain the required class?
grep -n 'class CredentialVault' core/vault.py 2>/dev/null

# SCAN 3: Any prior Jules PR or commit implementing this?
git log --oneline --all | grep -i 'vault' | head -10

# SCAN 4: Grep for the core method signature
grep -n 'get_secret' core/vault.py 2>/dev/null

# SCAN 5: Check backlog status
grep -A2 'VAULT-001' docs/space/jules_backlog.md | grep -i 'status'
```

**SKIP IF:** Any of the following is true:
- `core/vault.py` exists AND contains `class CredentialVault` AND contains `get_secret`
- `git log` shows a commit with 'vault' that added `core/vault.py`
- Backlog shows status: DONE or IN_PROGRESS by another agent

**IF SKIP:** Log to `docs/audit/scheduler_skip_log.md` and exit.

---

## Task Execution (only if scan shows NOT IMPLEMENTED)

**Goal:** Implement a thread-safe `CredentialVault` class in `core/vault.py` with `get_secret(key, default=None)` and unit tests in `tests/test_vault.py`.

**Target files:** `core/vault.py`, `tests/test_vault.py`

**Protected files (NEVER TOUCH):**
`core/router.py`, `core/nina.py`, `guardian_engine.py`, `main.py`, `.env`,
`interfaces/telegram_interface.py`, `tools/shell.py`, `ninagate/main.py`

**Dependency:** None

**Validation:**
```bash
python3 -m py_compile core/vault.py tests/test_vault.py
pyflakes core/vault.py tests/test_vault.py
./venv/bin/pytest tests/test_vault.py -v
./guardian
```

**PR title:** `feat(vault): implement scoped credential vault engine`

**Acceptance criteria:**
- `CredentialVault` is thread-safe (use `threading.Lock`)
- `get_secret(key, default=None)` retrieves from internal dict or falls back to `os.environ`
- Unit tests cover: retrieval, fallback, concurrent access
- `./guardian` passes before PR is opened
