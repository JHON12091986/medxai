# NINA agy Batch 04 — Observability, Tools, Hardening
> Execute every ═══ block sequentially. One file at a time.
> After ALL specs: cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh
> Then run: bash ~/nina/docs/agyspec/run_batch.sh (to get next batch)

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-01 | feat(tools): add ninagate_status tool for agent self-monitoring
ID: NGS-TOOL-01 | Type: feature | Risk: LOW | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Check if tools/ninagate_status.py exists. If yes, skip this spec.

IF it does NOT exist, CREATE tools/ninagate_status.py:
```python
"""ninagate_status tool — agent can check if ninagate proxy is healthy."""
import logging
import socket

logger = logging.getLogger("nina.tools.ninagate_status")

class NinagateStatusTool:
    name = "ninagate_status"
    description = "Check if the ninagate OpenAI-compatible proxy is running on localhost:8080."

    async def run(self, _: str = "") -> str:
        try:
            with socket.create_connection(("127.0.0.1", 8080), timeout=1.0):
                return "ninagate: UP (localhost:8080 reachable)"
        except OSError:
            return "ninagate: DOWN (localhost:8080 not reachable — run: sudo systemctl start ninagate.service)"
```

THEN register in core/nina.py or wherever tools dict is built:
```python
    from tools.ninagate_status import NinagateStatusTool
    tools["ninagate_status"] = NinagateStatusTool()
```

DO NOT TOUCH: ninagate/main.py, core/agent.py tool dispatch, .env

After editing: python3 -m py_compile tools/ninagate_status.py
Commit: feat(tools): add ninagate_status health-check tool (NGS-TOOL-01) | Batch 04

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-02 | fix(idleloop): add startup delay to prevent boot-time spam
ID: IDLE-DELAY-01 | Type: reliability | Risk: LOW | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read idleloop.py fully before making any changes.

FIND the class or function that starts the idle topic loop.
Locate the FIRST iteration of the loop — where it calls the LLM for the first
proposal after startup.

ADD a startup delay BEFORE the first iteration:
```python
        # IDLE-DELAY-01: 90s startup delay — let nina.service fully initialize
        # before firing the first LLM proposal call
        logger.info("idleloop: waiting 90s startup delay before first proposal")
        await asyncio.sleep(90)
```
Insert this ONCE at the start of the loop's run method, not inside the recurring
iteration. If a startup delay already exists and is >= 60s, skip this spec.

DO NOT TOUCH: _promote_to_backlog, topic list, manually_promote_latest, .env

After editing: python3 -m py_compile idleloop.py
Commit: fix(idleloop): add 90s startup delay before first proposal (IDLE-DELAY-01) | Batch 04

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-03 | fix(wiring_audit): make nina_wiring_audit.py exit 0 on warnings
ID: WIRE-EXIT-01 | Type: reliability | Risk: LOW | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read nina_wiring_audit.py fully before making any changes.

FIND any `sys.exit(1)` or `raise SystemExit(1)` calls.
IF they fire on non-critical warnings (missing optional files, minor mismatches):
  CHANGE to `sys.exit(0)` — only true wiring failures (missing core files,
  broken imports) should exit non-zero.

FIND the final summary print/log. ADD:
```python
    # WIRE-EXIT-01: always exit 0 unless critical wiring broken
    if critical_errors:  # use actual error tracking variable name
        sys.exit(1)
    else:
        sys.exit(0)
```
If no `critical_errors` variable exists, wrap the entire audit in try/except
and only sys.exit(1) on uncaught exceptions.

DO NOT TOUCH: audit logic, file checks, import verification, .env

After editing: python3 -m py_compile nina_wiring_audit.py
Commit: fix(wiring_audit): exit 0 on warnings — only exit 1 on critical errors (WIRE-EXIT-01) | Batch 04

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-04 | fix(context_graph): add null-check before accessing summary.health
ID: CTX-GRAPH-01 | Type: bug | Risk: LOW | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read nina_context_graph.py fully before making any changes.

FIND where `summary["health"]` or `summary.health` or `data["summary"]["health"]`
is accessed.

WRAP with null-check:
```python
        # CTX-GRAPH-01: safe access — summary may be absent in fresh repos
        _summary = data.get("summary") or {}
        _health = _summary.get("health", "unknown")
        _top_priority = _summary.get("top_priority", "none")
```
Replace all direct dict accesses on `summary` with the safe versions above.

ALSO FIND the file-write for nina_context_graph.json. Wrap in try/except:
```python
        try:
            Path("nina_context_graph.json").write_text(
                json.dumps(graph, indent=2), encoding="utf-8"
            )
        except Exception as _cge:
            print(f"WARN: context graph write failed: {_cge}")
```

DO NOT TOUCH: graph construction logic, commit index calls, .env

After editing: python3 -m py_compile nina_context_graph.py
Commit: fix(context_graph): null-check summary.health and safe file write (CTX-GRAPH-01) | Batch 04

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-05 | fix(session_brief): handle missing logs dir gracefully
ID: SESSION-BRIEF-01 | Type: reliability | Risk: LOW | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read tools/session_brief.py fully before making any changes.

FIND any `open(...)` or `Path(...).read_text()` call that reads from `logs/`.
Wrap each with:
```python
        try:
            # SESSION-BRIEF-01: graceful fallback if logs dir missing
            content = Path(log_path).read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            content = "(log not found)"
        except Exception as _sbe:
            content = f"(log read error: {_sbe})"
```
Substitute `log_path` with the actual variable name.

ALSO ensure the script ends with `sys.exit(0)` regardless of errors —
its failure must never break nina_sync.sh step [8/8].

FIND any bare `raise` or unhandled exception paths and wrap in:
```python
    except Exception as _e:
        print(f"session_brief: non-fatal error: {_e}")
        sys.exit(0)
```

DO NOT TOUCH: output format, Telegram send logic, .env

After editing: python3 -m py_compile tools/session_brief.py
Commit: fix(session_brief): graceful fallback for missing log files (SESSION-BRIEF-01) | Batch 04

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-06 | fix(doc_autogen): prevent overwriting manually-edited docs
ID: DOCGEN-01 | Type: reliability | Risk: LOW | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read tools/doc_autogen.py fully before making any changes.

FIND any `open(path, 'w')` or `Path(path).write_text(...)` call that writes to
docs/space/ files or other markdown docs.

BEFORE each write, ADD a mtime guard:
```python
        # DOCGEN-01: skip overwrite if file was manually edited within last 24h
        import time as _dtime
        _doc_path = Path(path)  # use actual path variable
        _24H = 86400
        if _doc_path.exists():
            _age = _dtime.time() - _doc_path.stat().st_mtime
            if _age < _24H:
                logger.info(f"doc_autogen: skipping {_doc_path.name} — edited {_age/3600:.1f}h ago")
                continue  # skip this file in the loop
```
If not in a loop, use `pass` or a conditional block instead of `continue`.

DO NOT TOUCH: template logic, section content generation, .env

After editing: python3 -m py_compile tools/doc_autogen.py
Commit: fix(doc_autogen): skip overwrite of manually-edited docs within 24h (DOCGEN-01) | Batch 04

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-07 | fix(surgical_merge): add dry-run guard before any git merge
ID: MERGE-DRY-01 | Type: safety | Risk: HIGH | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read tools/surgical_merge.py fully before making any changes.

FIND any `git merge`, `git rebase`, or `subprocess.run(["git", "merge", ...])` call.

BEFORE every merge/rebase call, ADD a conflict pre-check:
```python
        # MERGE-DRY-01: dry-run check before merge — abort if conflicts predicted
        import subprocess as _sp
        _dry = _sp.run(
            ["git", "merge", "--no-commit", "--no-ff", branch_name],  # use actual branch var
            capture_output=True, text=True
        )
        if _dry.returncode != 0 or "CONFLICT" in _dry.stdout + _dry.stderr:
            _sp.run(["git", "merge", "--abort"], capture_output=True)
            logger.warning(f"surgical_merge: dry-run predicted conflict on {branch_name} — skipping")
            continue  # skip to next PR
        _sp.run(["git", "merge", "--abort"], capture_output=True)  # reset dry-run state
```
Substitute `branch_name` with the actual branch variable.
Then proceed with the real merge.

DO NOT TOUCH: PR listing logic, auth, git push, .env

After editing: python3 -m py_compile tools/surgical_merge.py
Commit: fix(surgical_merge): dry-run conflict check before every git merge (MERGE-DRY-01) | Batch 04

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-08 | fix(compact_exporter): cap nina_latest.md at 200KB
ID: EXPORT-CAP-01 | Type: reliability | Risk: LOW | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read tools/compact_exporter.py fully before making any changes.

FIND the final write of nina_latest.md:
```python
open(output_path, 'w').write(content)
```
or
```python
Path(output_path).write_text(content)
```

BEFORE the write, ADD a size cap:
```python
        # EXPORT-CAP-01: cap nina_latest.md at 200KB — Perplexity Space upload limit
        _MAX_EXPORT_BYTES = 200_000
        if len(content.encode('utf-8')) > _MAX_EXPORT_BYTES:
            _lines = content.splitlines()
            _truncated = []
            _size = 0
            for _line in _lines:
                _lsize = len(_line.encode('utf-8')) + 1
                if _size + _lsize > _MAX_EXPORT_BYTES:
                    _truncated.append("\n---\n_[truncated at 200KB limit]_")
                    break
                _truncated.append(_line)
                _size += _lsize
            content = "\n".join(_truncated)
            logger.info(f"compact_exporter: truncated to {len(content)} chars")
```

DO NOT TOUCH: section collection logic, rclone upload, diff generation, .env

After editing: python3 -m py_compile tools/compact_exporter.py
Commit: fix(compact_exporter): cap nina_latest.md at 200KB (EXPORT-CAP-01) | Batch 04

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-09 | feat(tools/market): stub DSE/CSE with clear placeholder error
ID: F-05-STUB | Type: feature | Risk: LOW | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read tools/market.py fully before making any changes.

FIND the function that fetches DSE or CSE price data.
Locate where it returns dummy/placeholder prices.

REPLACE the dummy return with a clear stub message:
```python
        # F-05-STUB: real DSE/CSE API not yet integrated (O-01 blocked by Playwright)
        # Return a clear message so the agent knows to tell the user
        return (
            "[MARKET DATA UNAVAILABLE] DSE/CSE live price API not yet connected.\n"
            "Status: O-01 (Playwright install pending — server action required by Bostami).\n"
            "Workaround: check https://dsebd.org manually."
        )
```

DO NOT TOUCH: any existing API key handling, HTTP client setup, .env

After editing: python3 -m py_compile tools/market.py
Commit: feat(market): replace dummy prices with clear stub message (F-05-STUB) | Batch 04

═══════════════════════════════════════════════════════════════════════════════
SPEC-B04-10 | docs(agyspec): update queue.md — mark batch 04 DONE
ID: QUEUE-UPDATE-04 | Type: doc | Risk: ZERO | Batch 04
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read docs/agyspec/queue.md fully.

UPDATE queue.md:
- Set batch 04 row Status to DONE, add today's date in Completed column

Also append to docs/agyspec/run_log.md:
```
| <today's date> | Batch 04 complete | 10 specs | DONE | All 4 batches finished |
```

Commit: docs(agyspec): mark batch 04 DONE — all batches complete (QUEUE-UPDATE-04) | Batch 04
