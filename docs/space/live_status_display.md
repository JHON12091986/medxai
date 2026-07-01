# Live Status Display — Nina Telegram Pipeline
**Feature:** Real-time per-request status messages in Telegram  
**Blueprint date:** 25 Jun 2026  
**Owner:** M. Baizid Alam  
**Status:** Pass 0 complete ✅ | Pass 1 pending ⏳

---

## Problem

Between `⏳ Thinking...` and the first streaming token, the user sees nothing.
For slow providers (GEMINI cold start, LOCAL model load, opencode 30-60s runs),
this black hole degrades trust and makes it impossible to tell if Nina is working
or hung.

---

## Solution Architecture

```
User sends message
        │
        ▼
TelegramInterface._stream_reply()
        │
        ├─► subscribe(_status_update)  ← registers callback in ContextVar
        │
        ▼
  router.route()  ──► await push(S.routing("GEMINI"))  ──► edits sent msg live
        │
        ├─► await push(S.generating("gemini-2.0-flash"))  ──► edits again
        │
        ▼
  first token arrives → streaming fills in final text
        │
        ▼
  unsubscribe(token)  ← always in finally block
```

---

## Files

| File | Status | Guardian? | Description |
|---|---|---|---|
| `core/status_bus.py` | ✅ Pass 0 | No | Async ContextVar push/subscribe bus |
| `core/status_stages.py` | ✅ Pass 0 | No | Canonical status string constants |
| `telemetry/status_adapter.py` | ✅ Pass 0 | No | JSONL audit trail bridge |
| `docs/space/live_status_display.md` | ✅ Pass 0 | No | This document |
| `interfaces/telegram_interface.py` | ⏳ Pass 1 | **YES** | Wire subscribe/unsubscribe in `_stream_reply` |
| `core/router.py` | ⏳ Pass 1 | **YES** | Wire `await push()` at routing decision points |
| `main.py` | ⏳ Pass 2 | **YES** | `attach()` status_adapter at startup |
| `tools/opencode.py` | ⏳ Pass 2 | No | Wire opencode step push calls |

---

## Pass 0 — Complete (this commit)

Brand-new files only.  Zero edits to existing files.  Zero Guardian risk.

- `core/status_bus.py` — the bus
- `core/status_stages.py` — the string constants
- `telemetry/status_adapter.py` — JSONL bridge
- This document

---

## Pass 1 — Guardian-gated edits (next)

### Pre-flight checklist (MANDATORY before any edit)
- [ ] Read `docs/guardian.md`
- [ ] Read full `interfaces/telegram_interface.py` (already done 25 Jun)
- [ ] Read full `core/router.py`
- [ ] Confirm no open GUARDIAN items in `docs/space/nina_error_register.md`

### Change 1 — `interfaces/telegram_interface.py`

Target method: `_stream_reply`  
Change type: Add 4 lines (import + subscribe + unsubscribe in finally)

```python
# ADD at top of file (with other imports):
from core.status_bus import subscribe as _sb_subscribe, unsubscribe as _sb_unsubscribe
from core.status_stages import S as _S

# INSIDE _stream_reply, AFTER `sent = await self._reply(update, "...")` line:
_sb_token = _sb_subscribe(
    lambda msg: self._edit_message(sent, msg)  # type: ignore[return-value]
)
try:
    # ... existing code unchanged ...
finally:
    _sb_unsubscribe(_sb_token)
```

**Falsification:** `_edit_message` returns a coroutine — lambda must `await` it.
Correct form:

```python
async def _status_update(msg: str) -> None:
    try:
        await self._edit_message(sent, msg)
    except Exception:
        pass

_sb_token = _sb_subscribe(_status_update)
```

### Change 2 — `core/router.py`

Target: provider selection block and fallback handler  
Change type: Add import + 4 `await push()` calls  

```python
# ADD import (top of file, after existing imports):
from core.status_bus import push as _status_push
from core.status_stages import S as _S

# At provider selection:
await _status_push(_S.routing(provider=selected_provider_name))

# Just before model call:
await _status_push(_S.generating(model=model_name))

# On fallback:
await _status_push(_S.fallback(from_provider=prev, to_provider=next_p))

# On provider error:
await _status_push(_S.error(provider=provider_name, reason=str(exc)[:80]))
```

**Grep before claim:** Before inserting, grep `core/router.py` for the actual
variable names used for provider/model at selection time.

---

## Pass 2 — Startup wiring + opencode steps (next after Pass 1)

### `main.py` — activate telemetry adapter

```python
# After NinaOS starts:
from telemetry.status_adapter import attach as _attach_status_tel
_attach_status_tel()
```

### `tools/opencode.py` — multi-step progress

```python
from core.status_bus import push as _status_push
from core.status_stages import S as _S

# Before each of the 5 opencode steps:
await _status_push(_S.opencode_step(n=1, total=5, label="NDEV reading"))
await _status_push(_S.opencode_step(n=2, total=5, label="OpenCode executing"))
await _status_push(_S.opencode_step(n=3, total=5, label="NinaGate validating"))
await _status_push(_S.opencode_step(n=4, total=5, label="Sync"))
await _status_push(_S.opencode_step(n=5, total=5, label="Upload"))
```

---

## Pass 3 — NinaGate circuit breaker status

`ninagate/circuit_breaker.py` is NOT Guardian-gated.  Wire:

```python
from core.status_bus import push as _status_push
from core.status_stages import S as _S
import asyncio

# On OPEN transition:
asyncio.ensure_future(_status_push(_S.circuit_open(provider=self.name)))

# On CLOSED recovery:
asyncio.ensure_future(_status_push(_S.circuit_closed(provider=self.name)))
```

`asyncio.ensure_future` is used here because `circuit_breaker.py` state
transitions may be synchronous — wraps the coroutine safely.

---

## What the User Sees (Full Journey)

```
You:   ask what is the SOFR rate today

Nina:  ⏳ Thinking...
Nina:  🔀 Routing → GEMINI
Nina:  🧠 gemini-2.0-flash · generating...
Nina:  The SOFR rate today is 5.31% as of...  ← streaming fills in
```

For opencode:
```
Nina:  ⚙️ OpenCode dispatching...
Nina:  ⚙️ [█░░░░] 1/5 · NDEV reading
Nina:  ⚙️ [██░░░] 2/5 · OpenCode executing
Nina:  ⚙️ [███░░] 3/5 · NinaGate validating
Nina:  ⚙️ [████░] 4/5 · Sync
Nina:  ⚙️ [█████] 5/5 · Upload
Nina:  ✅ OpenCode done · 42.3s
```

---

## Contingency Table

| Risk | Trigger | Safeguard |
|---|---|---|
| subscriber not set (CLI/tests) | `_STATUS_CB.get()` returns None | Silent no-op in `push()` |
| Telegram rate-limit on edit | `_edit_message` raises | try/except in `_status_update` lambda |
| Push hangs (network) | Telegram API slow | `asyncio.wait_for(timeout=2.0)` in push() |
| Concurrent requests overwrite | Two requests, same bot | ContextVar isolation — each Task has own subscriber |
| Router is synchronous | `await push()` in sync fn | `asyncio.ensure_future()` wrapper |
| telemetry.jsonl unwritable | FS permissions | try/except in `_write()`, logs warning, never raises |
| telemetry.jsonl grows forever | Long-running Nina | 10MB rotation to `.jsonl.1` in `_rotate_if_needed()` |
| Guardian blocks router.py edit | Pre-flight fails | Wire at `ninagate/circuit_breaker.py` instead (not gated) |
| status_adapter.attach() called twice | Startup re-init | Idempotent guard: `if _original_push is not None: return` |

---

## Testing Pass 0

Run from `~/nina` with venv active:

```bash
python - <<'EOF'
import asyncio
from core.status_bus import subscribe, unsubscribe, push
from core.status_stages import S

received = []

async def test():
    async def cb(msg): received.append(msg)
    tok = subscribe(cb)
    try:
        await push(S.routing("GEMINI"))
        await push(S.generating("gemini-2.0-flash"))
        await push(S.done("GEMINI", 430))
    finally:
        unsubscribe(tok)
    assert received == [
        "\U0001f500 Routing \u2192 GEMINI",
        "\U0001f9e0 gemini-2.0-flash \xb7 generating...",
        "\u2705 Done (GEMINI) \xb7 430ms",
    ], f"FAIL: {received}"
    print("PASS — all 3 status messages received correctly")

asyncio.run(test())
EOF
```

Expected output: `PASS — all 3 status messages received correctly`

---

## Jules Prompt — Pass 1

```
Task: Wire live status display into telegram_interface.py + core/router.py (Pass 1)

Pre-flight (MANDATORY — do not skip):
1. Read docs/guardian.md
2. Read interfaces/telegram_interface.py (full)
3. Read core/router.py (full)
4. Read core/status_bus.py (new, Pass 0)
5. Read core/status_stages.py (new, Pass 0)
6. Check docs/space/nina_error_register.md — no open GUARDIAN items

Change 1 — interfaces/telegram_interface.py → _stream_reply method:
  - Add import: from core.status_bus import subscribe as _sb_subscribe, unsubscribe as _sb_unsubscribe
  - Add import: from core.status_stages import S as _S
  - After `sent = await self._reply(update, "...")`: define async _status_update(msg) inner
    function that calls await self._edit_message(sent, msg) in try/except.
  - Call _sb_token = _sb_subscribe(_status_update)
  - Wrap the rest of _stream_reply body in try/finally: _sb_unsubscribe(_sb_token)
  - DO NOT change any existing logic — additive only.

Change 2 — core/router.py → provider selection + fallback + error paths:
  - Add imports: from core.status_bus import push as _status_push
  - Add import: from core.status_stages import S as _S
  - GREP for the actual variable names used at provider selection before inserting.
  - Insert await _status_push(S.routing(provider=...)) at provider selection.
  - Insert await _status_push(S.generating(model=...)) before model call.
  - Insert await _status_push(S.fallback(...)) at fallback trigger.
  - Insert await _status_push(S.error(...)) in the exception handler.
  - All push() calls must be in try/except — never let them crash routing.

Falsification check:
  - What if router.py is partially synchronous? → wrap push() in asyncio.ensure_future if needed.
  - What if _stream_reply is called from a non-async context? → It is already async, safe.
  - What if subscribe() is called but unsubscribe() is never reached? → The finally block ensures it.

Guardian rule: Both files are GUARDIAN-gated. Changes must be minimal, additive,
and reversible. No logic changes. No signature changes. Additive imports + 4-line
injections only.
```
