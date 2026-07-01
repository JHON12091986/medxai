# NINA agy Batch — Prompt #1 | Multi-Loop Fix Pack
> Feed this entire file to agy. Each ═══ block is one independent task.
> Run sequentially. After ALL tasks: `cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh`
> Update docs/agyspec/spec_log.md with PASS/FAIL for each spec after the batch.

═══════════════════════════════════════════════════════════════════════════════
SPEC-01 | fix(sync): protect nexus_discoveries.md from deletion by post_task_hook
ID: E-nexus-01 | Type: bug | Risk: LOW | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read tools/post_task_hook.py fully before making any changes.

FIND in tools/post_task_hook.py any block that iterates over docs/space/ files
and deletes, overwrites, or recreates them — look for `shutil.rmtree`,
`os.remove`, `open(path, 'w')` writing empty content, or `Path(...).unlink()`
on .md files under docs/space/.

IF such a deletion/overwrite block exists:
REPLACE the deletion call with a guard — insert BEFORE any unlink/remove/open-w
call on docs/space/ files:
```python
# SPEC-01: never delete docs/space/*.md files that are persistent cross-session state
PROTECTED_SPACE_FILES = {
    "nexus_discoveries.md",
    "nina_session_log.md",
    "claude_feed.md",
}
if Path(target).name in PROTECTED_SPACE_FILES:
    continue  # skip deletion of protected space files
```
Use the exact loop variable name present in the file (may not be `target`).

IF no deletion block exists:
Create docs/space/nexus_discoveries.md with:
```
# NINA Nexus Discoveries
> Cross-session learnings, recurring patterns, and root-cause findings.
> Updated by idleloop and manually by Bostami.
```
then git add docs/space/nexus_discoveries.md.

DO NOT TOUCH: nina_sync.sh, compact_exporter.py, core/agent.py, .env

After editing: python3 -m py_compile tools/post_task_hook.py
Commit: fix(sync): guard nexus_discoveries.md from post_task_hook deletion (E-nexus-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-02 | fix(agent): diagnostic fast-path injects real context not empty string
ID: AGY-DIAG-01 | Type: perf+bug | Risk: MEDIUM | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/agent.py fully before making any changes.

FIND in `_inner` method the DIAGNOSTIC fast-path block:
```python
        task_type_str_inner = (getattr(task, "task_type", "") or "").lower()
        if task_type_str_inner == "diagnostic":
            system_frame = ReasoningKernel.get_system_frame(goal, locals().get('base_context', ''), mode="diagnostic")
```

The bug: `locals().get('base_context', '')` evaluates BEFORE `base_context` is
assigned (~40 lines below). This injects empty string into the diagnostic context.

REPLACE the entire `if task_type_str_inner == "diagnostic":` block (from the
`if` line through the `return await plan.execute()`) with:
```python
        if task_type_str_inner == "diagnostic":
            # Build minimal context first (n=10, char_budget=3500 for speed)
            _diag_context = await self.memory.build_context(goal, n=10, char_budget=3500)
            system_frame = ReasoningKernel.get_system_frame(goal, _diag_context, mode="diagnostic")
            system_frame = (
                "[DIAGNOSTIC MODE — read before theorizing]\n"
                "Step 1: git log --all --full-history -- <suspected_file>\n"
                "Step 2: Check nina_error_register.md for matching OPEN rows\n"
                "Step 3: Read the actual file/script before forming any hypothesis\n\n"
            ) + system_frame
            msgs = [{"role": "user", "content": system_frame}] + session_history.copy()
            plan = self.dispatcher.dispatch(goal, context=str(msgs))
            return await plan.execute()
```

DO NOT TOUCH: _self_check, run(), circuit_breaker, _CHAINED_RE, F-08 command routing block, .env

After editing: python3 -m py_compile core/agent.py
Commit: fix(agent): diagnostic fast-path injects real context not empty string (AGY-DIAG-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-03 | fix(agent): elevate read-first check to priority 1 in Critic prompt
ID: AGY-CRITIC-01 | Type: quality | Risk: LOW | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/agent.py fully before making any changes.

FIND in `_self_check` method the variable `critic_prompt` assignment.
It currently contains the string fragment:
```
"- Read-first: Did the solution read/check the actual file or git history BEFORE theorizing? "
```

REPLACE the entire `critic_prompt = (` assignment (from opening paren to
closing paren) with:
```python
            critic_prompt = (
                f"Goal: {goal}\n\n"
                f"Verification Plan:\n{plan_str}\n\n"
                f"Current Draft:\n{current_draft[:_draft_limit]}\n\n"
                "You are NINA's cognitive Critic. Evaluate the draft in this EXACT order:\n\n"
                "CHECK 1 — READ-FIRST (HIGHEST PRIORITY):\n"
                "Did the solution read the actual file, run git log, or check "
                "nina_error_register.md BEFORE forming a hypothesis? "
                "If it theorized without reading source → output REVISE immediately.\n\n"
                "CHECK 2 — IMPORTS: Missing or invalid modules?\n"
                "CHECK 3 — SAFETY: Destructive commands, leaked secrets, harmful actions?\n"
                "CHECK 4 — LOGIC: Contradictions or incorrect reasoning?\n\n"
                f"Detected programmatic issues: {critic_issues if critic_issues else 'None'}\n\n"
                "Output PASS only if ALL four checks pass.\n"
                "Otherwise output REVISE: <specific corrective feedback starting with which CHECK failed>."
            )
```

DO NOT TOUCH: planner_prompt, generator_prompt, verifier_prompt, _self_check signature, run(), .env

After editing: python3 -m py_compile core/agent.py
Commit: fix(agent): elevate read-first check to priority 1 in Critic (AGY-CRITIC-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-04 | perf(agent): skip System2 blueprint for SIMPLE/non-research tasks
ID: AGY-SYS2-01 | Type: perf | Risk: MEDIUM | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/agent.py fully before making any changes.

FIND in `_inner` the System 2 Thinking block opening:
```python
        # 2. System 2 Thinking (Pre-Compute Planning Blueprint)
        blueprint = ""
        if self._should_self_check(task):
```

REPLACE only the condition line `if self._should_self_check(task):` with:
```python
        # 2. System 2 Thinking — SPEC-04: only COMPLEX/MASSIVE or coding/research tasks
        # Saves ~3000 tokens on SIMPLE queries that don't need a planning blueprint
        _s2_complexity = (getattr(task, "complexity", "") or "").upper()
        _s2_task_type = (getattr(task, "task_type", "") or "").lower()
        _s2_eligible = (
            _s2_complexity in ("COMPLEX", "MASSIVE")
            or _s2_task_type in ("coding", "research")
        ) and self._should_self_check(task)
        if _s2_eligible:
```

Leave ALL code inside the blueprint block unchanged — only the `if` guard changes.
The `blueprint = ""` line stays on its own line above the new condition.

DO NOT TOUCH: _self_check(), _should_self_check(), run(), DIAGNOSTIC fast-path block, .env

After editing: python3 -m py_compile core/agent.py
Commit: perf(agent): skip System2 blueprint for non-COMPLEX tasks — save ~3000 tokens (AGY-SYS2-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-05 | fix(idleloop): quality gate — reject placeholder proposals from backlog
ID: IDLE-QUAL-01 | Type: bug | Risk: LOW | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read idleloop.py fully before making any changes.

FIND the method `_promote_to_backlog` (or whichever method writes a new entry
to jules_backlog.md based on a proposal). Identify the local variable that
holds the proposal analysis text — it may be named `analysis`, `brief`,
`content`, `proposal_text`, or similar.

FIND the line that opens jules_backlog.md for writing/appending inside that method.

IMMEDIATELY BEFORE that open() call, insert:
```python
        # SPEC-05: quality gate — reject placeholder/trivially short proposals
        _REJECT_PATTERNS = {"todo", "placeholder", "lorem", "example proposal", "n/a", "tbd"}
        _qa_text = str(<ANALYSIS_VAR>).lower().strip()  # substitute real variable name
        _is_low_quality = (
            len(_qa_text) < 80
            or any(pat in _qa_text for pat in _REJECT_PATTERNS)
            or _qa_text.count("example") > 2
        )
        if _is_low_quality:
            logger.info(f"idleloop: quality gate rejected proposal (len={len(_qa_text)})")
            return False
```
Substitute `<ANALYSIS_VAR>` with the exact variable name in the method.

DO NOT TOUCH: manually_promote_latest(), topic loop, scheduler, .env

After editing: python3 -m py_compile idleloop.py
Commit: fix(idleloop): quality gate rejects placeholder proposals (IDLE-QUAL-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-06 | feat(agent): inject nexus_discoveries.md into base_context every call
ID: NEXUS-CTX-01 | Type: feature | Risk: LOW | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/agent.py fully before making any changes.

FIND in `_inner` the exact line:
```python
        base_context = await self.memory.build_context(goal, n=n_docs, char_budget=char_budget)
```

IMMEDIATELY AFTER that line, insert:
```python
        # SPEC-06: inject nexus_discoveries.md as persistent cross-session reasoning layer
        _nexus_path = Path("docs/space/nexus_discoveries.md")
        _nexus_inject = ""
        if _nexus_path.exists():
            try:
                _nexus_raw = _nexus_path.read_text(encoding="utf-8", errors="ignore")
                if len(_nexus_raw.strip()) > 50:
                    _nexus_inject = (
                        f"\n\n[NEXUS DISCOVERIES — accumulated cross-session learnings]\n"
                        f"{_nexus_raw[:2000]}"
                    )
            except Exception as _ne:
                logger.warning(f"nexus_inject_failed: {_ne}")
        base_context = base_context + _nexus_inject
```

DO NOT TOUCH: enriched_context block, past_reflections_str, _self_check, router.py, .env

After editing: python3 -m py_compile core/agent.py
Commit: feat(agent): inject nexus_discoveries.md into base_context every session (NEXUS-CTX-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-07 | fix(shell): remove cat from allowlist — O-06 CRITICAL security fix
ID: O-06 | Type: security | Risk: HIGH | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read tools/shell.py fully before making any changes.

FIND the allowlist/denylist variable — likely named `ALLOWED_COMMANDS`,
`SAFE_COMMANDS`, `COMMAND_ALLOWLIST`, or a similar set/list constant.

IF 'cat' appears in an allowlist set or list:
  REMOVE 'cat' from the allowlist.

FIND (or create) the denylist — likely named `BLOCKED_COMMANDS` or similar.
ADD 'cat' to the denylist.

FIND the block that returns an error when a blocked command is attempted.
REPLACE the return message with:
```python
            return f"[SHELL BLOCKED] '{cmd_base}' is not permitted (security: O-06). Use the read_file tool to read file contents instead."
```
where `cmd_base` is the actual variable name holding the parsed command base.

IF there is no explicit denylist (only allowlist):
  Ensure 'cat' is not in the allowlist. That is sufficient.

DO NOT TOUCH: allowlist entries for git, python3, bash, ls, grep, find, .env, guardian_engine.py

After editing: python3 -m py_compile tools/shell.py
Commit: fix(shell): remove cat from allowlist — O-06 secret-leak prevention (O-06) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-08 | fix(ninagate): add/restore 300s TTL cache on _check_local_health
ID: GATE-TTL-01 | Type: bug | Risk: MEDIUM | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read ninagate/main.py fully before making any changes.

FIND `_check_local_health` function definition in ninagate/main.py.
Check whether a TTL/cache of 300 seconds exists. If absent or wrong:

IMMEDIATELY BEFORE the function definition, insert (if not already present):
```python
# SPEC-08: 300s TTL cache — prevents hammering Ollama health endpoint every request
_local_health_cache: dict = {"result": None, "ts": 0.0}
_LOCAL_HEALTH_TTL = 300.0
```

At the START of the function body (first line after def ... :), insert:
```python
    import time as _time
    _now = _time.monotonic()
    if _local_health_cache["result"] is not None and (_now - _local_health_cache["ts"]) < _LOCAL_HEALTH_TTL:
        return _local_health_cache["result"]
```

BEFORE each `return <result>` statement in the function body (not exception
paths), insert:
```python
    _local_health_cache["result"] = <result_variable_name>
    _local_health_cache["ts"] = _time.monotonic()
```
Using the actual variable being returned.

DO NOT TOUCH: routing logic, provider cascade, auth/token handling, .env

After editing: python3 -m py_compile ninagate/main.py
Commit: fix(ninagate): add 300s TTL cache to _check_local_health (GATE-TTL-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-09 | fix(sync): auto-recreate nexus_discoveries.md if missing or empty
ID: E-nexus-02 | Type: reliability | Risk: LOW | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read nina_sync.sh fully before making any changes.

FIND the block labeled `[2/8] Mirror to docs/space/...`:
```bash
echo "[2/8] Mirror to docs/space/..."
```

AFTER the for-loop that copies SPACE_FILES and BEFORE the `[3/8]` echo block,
insert:
```bash
# SPEC-09: ensure nexus_discoveries.md always exists — recreate if deleted or empty
_NEXUS="$NINA/docs/space/nexus_discoveries.md"
if [ ! -f "$_NEXUS" ] || [ ! -s "$_NEXUS" ]; then
  echo "  ⚠  nexus_discoveries.md missing or empty — recreating skeleton"
  if [ "$DRY_RUN" = false ]; then
    cat > "$_NEXUS" << 'NEXUSEOF'
# NINA Nexus Discoveries
> Cross-session learnings, recurring patterns, and root-cause findings.
> Updated by idleloop promotions and manually by Bostami.
> Format: ## YYYY-MM-DD | Finding | Root Cause | Fix Applied

NEXUSEOF
    git add "$_NEXUS"
  fi
else
  echo "  ✓ nexus_discoveries.md present ($(wc -l < "$_NEXUS") lines)"
fi
```

DO NOT TOUCH: SPACE_FILES auto-discovery loop, [1/8] block, [3/8] backup cleanup, compact_exporter.py, .env

After editing: bash -n nina_sync.sh
Commit: fix(sync): auto-recreate nexus_discoveries.md when missing or empty (E-nexus-02) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-10 | feat(idleloop): mirror High-impact promotions to nexus_discoveries.md
ID: NEXUS-LOOP-01 | Type: feature | Risk: LOW | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read idleloop.py fully before making any changes.

FIND `_promote_to_backlog` method. Locate the final successful-write path —
the code immediately after the backlog write success (after the logger.info or
return True that confirms promotion succeeded).

AFTER that success confirmation, insert:
```python
        # SPEC-10: mirror promotion to nexus_discoveries.md for cross-session agent reasoning
        try:
            from pathlib import Path as _NPath
            from datetime import datetime as _Ndt
            _nexus = _NPath("docs/space/nexus_discoveries.md")
            if _nexus.exists():
                _ndate = _Ndt.now().strftime("%Y-%m-%d")
                # Use actual local variable names from this method for topic and analysis text:
                _ntopic = str(topic)[:60] if 'topic' in dir() else "unknown"
                _nanalysis = str(analysis)[:200].replace("\n", " ") if 'analysis' in dir() else ""
                _nentry = (
                    f"\n## {_ndate} | {_ntopic}\n"
                    f"> Auto-promoted from idleloop (High impact)\n"
                    f"> {_nanalysis}\n"
                )
                with open(_nexus, "a", encoding="utf-8") as _nf:
                    _nf.write(_nentry)
        except Exception:
            pass  # non-fatal — never block promotion
```
Substitute `topic` and `analysis` with actual local variable names in the method.

DO NOT TOUCH: manually_promote_latest(), topic loop, scheduler, jules_backlog.md write logic, .env

After editing: python3 -m py_compile idleloop.py
Commit: feat(idleloop): mirror High promotions to nexus_discoveries.md (NEXUS-LOOP-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-11 | perf(router): add diagnostic to STEP_BUDGETS with budget=3
ID: ROUTER-DIAG-01 | Type: perf | Risk: LOW | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read core/router.py fully before making any changes.

FIND `STEP_BUDGETS` dict in core/router.py.

IF `"diagnostic"` is NOT already a key:
  ADD immediately after the `"research"` entry (or at end of dict):
  ```python
      "diagnostic": 3,   # SPEC-11: max 3 steps for root-cause queries — fast path
  ```

FIND `DEFAULT_MAX_STEPS` constant. Add comment if not present:
  ```python
  DEFAULT_MAX_STEPS = <existing_value>  # diagnostic overrides via STEP_BUDGETS["diagnostic"]=3
  ```
  Do NOT change the numeric value.

DO NOT TOUCH: HybridRouter class body, CircuitBreaker, provider cascade, any API keys, .env

After editing: python3 -m py_compile core/router.py
Commit: perf(router): add diagnostic task type to STEP_BUDGETS with budget=3 (ROUTER-DIAG-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
SPEC-12 | docs(agyspec): create spec registry README and spec_log
ID: DOCS-AGYSPEC-01 | Type: doc | Risk: ZERO | Prompt #1
═══════════════════════════════════════════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.

Create docs/agyspec/ directory if not present.

Verify docs/agyspec/README.md and docs/agyspec/spec_log.md exist (they were
created by the Perplexity commit that delivered this batch file).

IF they exist: git add docs/agyspec/ and proceed.
IF they are missing: create them with the content from the Perplexity session
that generated this batch, then git add docs/agyspec/.

Update docs/agyspec/spec_log.md — set today's date in the Date column for
all 12 rows (SPEC-01 through SPEC-12), keeping Result as PENDING until
each spec actually runs.

DO NOT TOUCH: any other file outside docs/agyspec/

After editing: echo "docs only — no py_compile"
Commit: docs(agyspec): initialize spec registry with Prompt #1 batch (DOCS-AGYSPEC-01) | Prompt #1

═══════════════════════════════════════════════════════════════════════════════
POST-BATCH FINAL STEP (run after ALL 12 specs above are complete)
═══════════════════════════════════════════════════════════════════════════════

cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh

Then update docs/agyspec/spec_log.md with PASS/FAIL for each spec.
