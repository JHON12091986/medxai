# Slot 02 — VAULT-002: Secure Getter Integration and Env Masking
**Tier:** INFRA | **Priority:** P1 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → VAULT-002
**Dependency:** VAULT-001 (Slot 01) must be DONE first

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does mask_sensitive_data exist in vault.py?
grep -n 'mask_sensitive_data' core/vault.py 2>/dev/null

# SCAN 2: Any prior commit for vault masking?
git log --oneline --all | grep -i 'vault.*mask\|mask.*vault\|env.*mask' | head -5

# SCAN 3: Does test file cover masking?
grep -n 'mask\|MASKED' tests/test_vault.py 2>/dev/null

# SCAN 4: Check dependency — VAULT-001 must exist first
grep -n 'class CredentialVault' core/vault.py 2>/dev/null || echo 'DEPENDENCY NOT MET'
```

**SKIP IF:** `mask_sensitive_data` already exists in `core/vault.py`
**BLOCK IF:** `class CredentialVault` does NOT exist in `core/vault.py` (dependency unmet — log and exit)

---

## Task Execution

**Goal:** Add `mask_sensitive_data(env_dict) -> dict` to `core/vault.py` using regex to identify sensitive keys (`*_API_KEY`, `*TOKEN*`, `*SECRET*`, `*PASSWORD*`) and replace values with `[MASKED]`.

**Target files:** `core/vault.py`, `tests/test_vault.py`

**Protected files:** same as Slot 01

**Validation:**
```bash
python3 -m py_compile core/vault.py tests/test_vault.py
./venv/bin/pytest tests/test_vault.py -v
./guardian
```

**PR title:** `feat(vault): secure env masking for credential vault`
