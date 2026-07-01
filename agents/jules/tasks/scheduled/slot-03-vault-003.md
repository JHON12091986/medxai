# Slot 03 — VAULT-003: Wire Vault Loader to Config Registry
**Tier:** INFRA | **Priority:** P1 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → VAULT-003
**Dependency:** VAULT-002 (Slot 02) must be DONE first

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does config.py already import CredentialVault?
grep -n 'CredentialVault\|from core.vault\|from core import vault' core/config.py 2>/dev/null

# SCAN 2: Any prior commit wiring vault to config?
git log --oneline --all | grep -i 'config.*vault\|vault.*config' | head -5

# SCAN 3: Test file exists?
test -f tests/test_config_vault.py && echo EXISTS

# SCAN 4: Dependency check
grep -n 'mask_sensitive_data' core/vault.py 2>/dev/null || echo 'DEPENDENCY NOT MET'
```

**SKIP IF:** `core/config.py` already imports `CredentialVault` AND `tests/test_config_vault.py` exists

---

## Task Execution

**Goal:** Update `core/config.py` to optionally load config via `CredentialVault.get_secret` with graceful `os.environ` fallback if vault is absent.

**Target files:** `core/config.py`, `tests/test_config_vault.py`

**IMPORTANT:** Read `core/config.py` IN FULL before making any change. It is 9 KB with Pydantic models — do NOT restructure it, only add the vault integration as an optional layer.

**Protected files:** same as Slot 01, plus `core/config.py` must NOT have its Pydantic model signatures changed.

**Validation:**
```bash
python3 -m py_compile core/config.py tests/test_config_vault.py
./venv/bin/pytest tests/test_config_vault.py -v
python3 -c "from core.config import NinaConfig; print('config OK')"
./guardian
```

**PR title:** `feat(config): integrate credential vault loader`
