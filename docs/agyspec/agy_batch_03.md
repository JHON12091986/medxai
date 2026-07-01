# NINA agy Batch 03 — Router + Quota + Circuit Breaker
> Execute every ═══ block sequentially. One file at a time.
> After ALL specs: cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh
> Then run: bash ~/nina/docs/agyspec/run_batch.sh (to get next batch)

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-01 | fix(router): add jitter to retry backoff to prevent thundering herd
ID: ROUTER-JITTER-01 | Type: reliability | Risk: LOW | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/router.py fully before making any changes.

FIND any retry loop or backoff logic. Look for `asyncio.sleep`, `time.sleep`,
or exponential backoff patterns:
```python
await asyncio.sleep(delay)
```
or
```python
delay = base * (2 ** attempt)
```

FOR EACH sleep/backoff call, ADD jitter:
```python
        import random as _random
        # ROUTER-JITTER-01: add ±25% jitter to prevent thundering herd
        _jitter = delay * _random.uniform(0.75, 1.25)
        await asyncio.sleep(_jitter)
```
Replace the `await asyncio.sleep(delay)` with `await asyncio.sleep(_jitter)`.

IF no retry/sleep exists: ADD a module-level utility:
```python
async def _backoff_sleep(base_delay: float, attempt: int) -> None:
    """ROUTER-JITTER-01: exponential backoff with ±25% jitter."""
    import random as _r
    delay = min(base_delay * (2 ** attempt), 30.0)  # cap at 30s
    jittered = delay * _r.uniform(0.75, 1.25)
    await asyncio.sleep(jittered)
```

DO NOT TOUCH: provider cascade order, HybridRouter class signature, CircuitBreaker thresholds, .env

After editing: python3 -m py_compile core/router.py
Commit: fix(router): add ±25% jitter to retry backoff (ROUTER-JITTER-01) | Batch 03

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-02 | fix(router): log provider name on every dispatch for quota tracking
ID: ROUTER-LOG-01 | Type: observability | Risk: LOW | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/router.py fully before making any changes.

FIND the `route` or `dispatch` method that selects a provider and sends a request.
Locate the line where the provider is chosen (e.g., `provider = self.providers[idx]`).

IMMEDIATELY AFTER provider selection, add:
```python
        logger.info(
            f"router_dispatch provider={getattr(provider, 'name', str(provider))} "
            f"task={getattr(task, 'task_type', 'unknown')} "
            f"tier={getattr(task, 'tier', 'unknown')}",
            extra={"log": "router.log"}
        )
```
Use the actual provider variable name.

ALSO FIND where a provider failure is caught. ADD after the exception:
```python
        logger.warning(
            f"router_provider_failed provider={getattr(provider, 'name', str(provider))} "
            f"err={type(e).__name__}: {str(e)[:80]}",
            extra={"log": "router.log"}
        )
```

DO NOT TOUCH: provider cascade, CircuitBreaker, HybridRouter.__init__, .env

After editing: python3 -m py_compile core/router.py
Commit: fix(router): log provider name on every dispatch for quota tracking (ROUTER-LOG-01) | Batch 03

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-03 | fix(quota): persist quota_state.json atomically with tmp+rename
ID: QUOTA-ATOMIC-01 | Type: reliability | Risk: LOW | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Search for quota_state.json write in: core/router.py, core/quota_dispatcher.py,
tools/quota_manager.py — read whichever file contains the write.

FIND: `open(...quota_state.json..., 'w')` or `Path(...).write_text(json.dumps(...))`.

REPLACE with atomic write (tmp + rename):
```python
        # QUOTA-ATOMIC-01: atomic write — prevents corrupt quota_state.json on crash
        import tempfile as _tf, os as _os
        _quota_path = Path("data/quota_state.json")  # use actual path variable
        _tmp_fd, _tmp_path = _tf.mkstemp(
            dir=_quota_path.parent, prefix=".quota_tmp_", suffix=".json"
        )
        try:
            with _os.fdopen(_tmp_fd, 'w', encoding='utf-8') as _tf_out:
                import json as _json
                _json.dump(_quota_data, _tf_out, indent=2)  # use actual data variable name
            _os.replace(_tmp_path, _quota_path)
        except Exception as _qe:
            _os.unlink(_tmp_path)
            logger.warning(f"quota_save_failed: {_qe}")
```
Substitute `_quota_path` and `_quota_data` with actual variable names.

DO NOT TOUCH: quota read path, provider cascade, .env

After editing: python3 -m py_compile <file_that_was_changed>
Commit: fix(quota): atomic tmp+rename write for quota_state.json (QUOTA-ATOMIC-01) | Batch 03

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-04 | fix(circuit_breaker): reset consecutive_failures on provider switch
ID: CB-RESET-01 | Type: bug | Risk: MEDIUM | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/circuit_breaker.py fully before making any changes.

FIND the `BehavioralCircuitBreaker` class.
FIND `record_failure` method and `consecutive_failures` counter.

FIND where the circuit breaker switches from OPEN→CLOSED or provider changes.
If there is a `reset()` or `record_success()` method:

INSIDE `record_success`, ensure consecutive_failures resets:
```python
    def record_success(self) -> None:
        self.consecutive_failures = 0  # CB-RESET-01
        self.state = "CLOSED"
```
If this line already exists — skip.

ALSO FIND `_inner` in core/agent.py — locate:
```python
        self.circuit_breaker.consecutive_failures = 0
```
Verify this line exists at the START of `_inner` (session reset). If missing, ADD it
after `self.circuit_breaker.session_cost = 0.0`.

DO NOT TOUCH: cost_limit, max_tool_calls_per_run, BehavioralCircuitBreaker.__init__, .env

After editing: python3 -m py_compile core/circuit_breaker.py && python3 -m py_compile core/agent.py
Commit: fix(circuit_breaker): reset consecutive_failures on success and session start (CB-RESET-01) | Batch 03

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-05 | fix(router): handle empty string response from provider gracefully
ID: ROUTER-EMPTY-01 | Type: bug | Risk: LOW | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/router.py fully before making any changes.

FIND where provider response is returned after a successful API call.
Look for: `return response` or `return text` or `return content`.

BEFORE each such return (inside provider execute methods), insert:
```python
        # ROUTER-EMPTY-01: reject empty/whitespace responses — treat as failure
        if not response or not str(response).strip():
            raise ValueError(f"provider returned empty response")
```
where `response` is the actual variable being returned.

This forces the router to try the next provider instead of returning an empty
string to the agent loop.

DO NOT TOUCH: error logging, provider cascade order, CircuitBreaker, .env

After editing: python3 -m py_compile core/router.py
Commit: fix(router): reject empty provider responses and cascade to next (ROUTER-EMPTY-01) | Batch 03

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-06 | fix(ninagate): add request_id header for tracing
ID: GATE-TRACE-01 | Type: observability | Risk: LOW | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read ninagate/main.py fully before making any changes.

FIND the main request handler (the FastAPI/Starlette route that handles POST
requests to `/v1/chat/completions` or similar).

AT THE START of the handler, ADD:
```python
    # GATE-TRACE-01: inject request_id for end-to-end tracing
    import uuid as _uuid
    _req_id = request.headers.get("X-Request-ID") or str(_uuid.uuid4())[:8]
    logger.info(f"ninagate_request req_id={_req_id} model={body.get('model','?')}")
```
where `request` and `body` are the actual parameter names.

AT THE END of the handler (before return), ADD:
```python
    logger.info(f"ninagate_response req_id={_req_id} tokens={len(str(response))//4}")
```

DO NOT TOUCH: _check_local_health, routing logic, auth, .env

After editing: python3 -m py_compile ninagate/main.py
Commit: fix(ninagate): add request_id tracing header on every request (GATE-TRACE-01) | Batch 03

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-07 | fix(telegram): add rate-limit guard — max 20 msgs/minute per user
ID: TG-RATELIMIT-01 | Type: security | Risk: MEDIUM | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read interfaces/telegram_interface.py fully before making any changes.

FIND the message handler (likely decorated with `@dp.message_handler` or
`router.message` or similar). Locate where incoming messages are processed
BEFORE being dispatched to the agent.

ADD at module level (near top of file, after imports):
```python
# TG-RATELIMIT-01: per-user rate limit — max 20 messages per 60 seconds
from collections import deque as _deque
import time as _rtime
_USER_MSG_TIMES: dict = {}
_RATE_LIMIT_MAX = 20
_RATE_LIMIT_WINDOW = 60.0

def _is_rate_limited(user_id: int) -> bool:
    now = _rtime.monotonic()
    if user_id not in _USER_MSG_TIMES:
        _USER_MSG_TIMES[user_id] = _deque()
    dq = _USER_MSG_TIMES[user_id]
    while dq and (now - dq[0]) > _RATE_LIMIT_WINDOW:
        dq.popleft()
    if len(dq) >= _RATE_LIMIT_MAX:
        return True
    dq.append(now)
    return False
```

INSIDE the message handler, BEFORE dispatching to agent, ADD:
```python
        if _is_rate_limited(message.from_user.id):
            await message.reply("⏳ Slow down — max 20 messages per minute.")
            return
```
where `message` is the actual parameter name.

DO NOT TOUCH: auth gate (AUTHORIZED_USER_ID check), agent dispatch, .env

After editing: python3 -m py_compile interfaces/telegram_interface.py
Commit: fix(telegram): add 20msg/min rate limit guard per user (TG-RATELIMIT-01) | Batch 03

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-08 | fix(agent): scratchpad bounded to last 5 entries — prevent O(n²)
ID: AGENT-SCRATCH-01 | Type: perf | Risk: LOW | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/agent.py fully before making any changes.

FIND in `_inner` the `scratchpad` list.
Locate where items are appended:
```python
            scratchpad.append(f"[{tname}] -> {str(res)[:300]}")
```

AFTER each `scratchpad.append(...)` call, ADD a trim:
```python
            # AGENT-SCRATCH-01: bound scratchpad to last 8 entries — prevent O(n²) context
            if len(scratchpad) > 8:
                scratchpad = scratchpad[-8:]
```

ALSO FIND where scratchpad is used in step_prompt:
```python
        _raw_step = f"[Step {step}/{max_steps}] Scratchpad:\n{chr(10).join(scratchpad[-3:])}"
```
Change `scratchpad[-3:]` to `scratchpad[-5:]` — gives slightly more context
without blowing the budget.

DO NOT TOUCH: trace list, _mission_summaries, run(), _self_check, .env

After editing: python3 -m py_compile core/agent.py
Commit: perf(agent): bound scratchpad to last 8 entries, use [-5:] in step_prompt (AGENT-SCRATCH-01) | Batch 03

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-09 | fix(agent): filter_sycophancy should strip leading filler phrases
ID: AGENT-SYCO-01 | Type: quality | Risk: LOW | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/reasoning.py fully before making any changes.

FIND `filter_sycophancy` in `ReasoningKernel` class.
Inspect the current list of filtered phrases.

ADD these phrases to the filter list if not already present:
```python
    _SYCOPHANCY_PREFIXES = [
        # existing entries stay — append only:
        "Certainly! ",
        "Of course! ",
        "Great question! ",
        "Absolutely! ",
        "Sure thing! ",
        "Happy to help! ",
        "I'd be happy to ",
        "I'd be glad to ",
        "As an AI language model, ",
        "As an AI, ",
        "As NINA, ",
    ]
```
Merge with existing list — do not replace, only extend.

FIND the stripping logic. Ensure it strips case-insensitively:
```python
    @staticmethod
    def filter_sycophancy(text: str) -> str:
        if not text:
            return text
        for prefix in ReasoningKernel._SYCOPHANCY_PREFIXES:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].lstrip()
        return text
```
If the method already exists, only ADD the missing prefixes to the list.

DO NOT TOUCH: validate_output, extract_thinking, get_system_frame, .env

After editing: python3 -m py_compile core/reasoning.py
Commit: fix(reasoning): extend sycophancy filter with 10 more filler prefixes (AGENT-SYCO-01) | Batch 03

═══════════════════════════════════════════════════════════════════════════════
SPEC-B03-10 | docs(agyspec): update queue.md — mark batch 02 and 03 IN_PROGRESS
ID: QUEUE-UPDATE-03 | Type: doc | Risk: ZERO | Batch 03
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read docs/agyspec/queue.md fully.

UPDATE queue.md:
- Set batch 02 row Status to DONE, add today's date in Completed column
- Set batch 03 row Status to DONE, add today's date in Completed column

Commit: docs(agyspec): mark batch 02+03 DONE in queue (QUEUE-UPDATE-03) | Batch 03
