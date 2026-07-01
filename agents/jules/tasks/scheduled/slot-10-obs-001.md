# Slot 10 — OBS-001: Provider Health Observability Tracker
**Tier:** OBS | **Priority:** P1 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → OBS-001
Also covers: Section 3 → 🔴 TODO-P1 Provider Health Monitoring

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does provider_health.py exist?
test -f tools/provider_health.py && grep -n 'ProviderHealthTracker' tools/provider_health.py

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'provider.*health\|health.*tracker\|provider_health' | head -5

# SCAN 3: Check existing router — does it ALREADY have health tracking?
grep -n 'health_summary\|HealthTracker\|rolling.*window' core/router.py 2>/dev/null

# SCAN 4: data/provider_health.json existence
test -f data/provider_health.json && echo 'JSON EXISTS — health system may already be running'
```

**SKIP IF:** `tools/provider_health.py` exists AND contains `ProviderHealthTracker`
**SKIP IF:** `core/router.py` already contains a `health_summary()` method (already implemented inline)

---

## Task Execution

**Goal:** Create `tools/provider_health.py` with `ProviderHealthTracker` class.
- Rolling 10-minute window of last 20 calls per provider
- Records: success/failure, latency ms, last error message
- `health_summary() -> dict` returns per-provider stats
- Persists to `data/provider_health.json` on every update
- Does NOT modify `core/router.py` — observability only
- When provider fails 3 consecutive times → send Telegram alert via `interfaces/telegram_interface.py`
  (import it read-only; do NOT modify it)

**CRITICAL:** `core/router.py` is PROTECTED. This is an observability-only module.

**Target files:** `tools/provider_health.py`, `tests/test_provider_health.py`

**Validation:**
```bash
python3 -m py_compile tools/provider_health.py tests/test_provider_health.py
./venv/bin/pytest tests/test_provider_health.py -v
./guardian
```

**PR title:** `feat(observability): add rolling provider health tracker`
