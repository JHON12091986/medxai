# Slot 15 — OBS-003: System Template Injection into Jules Dispatch
**Tier:** OBS | **Priority:** P2 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → OBS-003
Also covers: Section 3 → 🟠 TODO-P2 NinaGate System Template Wire

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does tools/jules.py already prepend system_templates?
grep -n 'system_templates\|NINA CONTEXT\|ninagate.*system' tools/jules.py 2>/dev/null

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'system.*template\|jules.*dispatch\|template.*inject' | head -5

# SCAN 3: Does ninagate/system_templates.json exist?
test -f ninagate/system_templates.json && echo 'SOURCE FILE EXISTS'
```

**SKIP IF:** `tools/jules.py` already loads `system_templates.json` and prepends it to dispatch payload

---

## Task Execution

**Goal:** Update `tools/jules.py` to prepend NINA system template to every Jules dispatch.
- Read `ninagate/system_templates.json` at dispatch runtime (not import time)
- Prepend as `[NINA CONTEXT]\n{system_content}\n\n[TASK]\n{prompt}`
- Total prompt length capped at 8000 chars — truncate system template from bottom if needed

**Read `tools/jules.py` FIRST** — it has session management logic; only modify the dispatch/prompt-building section.

**Target files:** `tools/jules.py`, `tests/test_jules_dispatch.py`

**Validation:**
```bash
python3 -m py_compile tools/jules.py
./venv/bin/pytest tests/test_jules_dispatch.py -v
./guardian
```

**PR title:** `feat(governance): append system templates to jules dispatch`
