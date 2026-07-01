# Slot 16 — PROVIDER-REG: Provider Registry Unification
**Tier:** OBS | **Priority:** P2 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 2 → ⚠️ Provider List Redundancy

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does providers.json have a 'tier' field?
grep -n '"tier"' ninagate/providers.json 2>/dev/null | head -5

# SCAN 2: Does router.py load from providers.json instead of hardcoded dicts?
grep -n 'providers.json\|load_providers\|from.*providers' core/router.py 2>/dev/null

# SCAN 3: Are PROVIDERS_TIER1/2/3 still hardcoded in router.py?
grep -n 'PROVIDERS_TIER1\|PROVIDERS_TIER2\|PROVIDERS_TIER3' core/router.py 2>/dev/null

# SCAN 4: Prior commit?
git log --oneline --all | grep -i 'provider.*registry\|provider.*json\|tier.*unif' | head -5
```

**SKIP IF:** `core/router.py` no longer contains `PROVIDERS_TIER1/2/3` hardcoded dicts AND `ninagate/providers.json` has `"tier"` field on each entry

---

## Task Execution

**Goal:** Make `ninagate/providers.json` the single canonical provider registry.
- Add `"tier": 1|2|3` to each entry in `ninagate/providers.json`
- In `core/router.py`: remove hardcoded tier dicts; add a loader that reads `providers.json` and builds tiers from the `"tier"` field
- Do NOT change any routing logic — only the data source
- Do NOT touch `.env`, `guardian_engine.py`, `interfaces/`, or tests outside the scope

**IMPORTANT:** Read `core/router.py` IN FULL first (42 KB). The tier dicts are likely in the first 200 lines. Only change the data source, not the algorithm.

**Target files:** `core/router.py`, `ninagate/providers.json`

**Validation:**
```bash
python3 -c "from core.router import Router; r=Router(); print(list(r.ALL_PROVIDERS.keys())[:5])"
./guardian
```

**PR title:** `feat(routing): unify provider registry to providers.json`
