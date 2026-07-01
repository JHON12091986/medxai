# agy Rules — Load for Standard Tasks (~600 tokens)

> Pre-flight + Scope Sandbox + Observe Loop are in `agy_prompt_core.md` (always loaded first).

## Core Rules
- Plain English only — never raw bash or code in the prompt
- One task, one file at a time — sequential, never parallel
- **Atomic commits:** one logical change = one commit. Never bundle unrelated edits.
- **Idempotency:** every task must be safe to run twice. Use guarded changes (`if not already X, do X`).
- agy performs ALL Jules PR merges — never use GitHub UI
- Pre-merge: DRY-RUN on all changed files → `python3 rule0_audit.py` → `py_compile` → `pyflakes` → `agy_impact_check.py` → check `juleslock.txt`
- Post-merge: `./nina_sync.sh` — no exceptions. Non-zero exit → STOP and report.
- After merge + sync: remove file from `juleslock.txt`, append to `agy_session.md`
- Merge conflict? STOP — escalate to Perplexity. No blind resolution.
- Task needs >3 reads + 1 write without Multi-File Protocol? STOP — escalate to Gemini CLI or Qwen.

## Reasoning Protocol (chain-of-thought — mandatory)
Before ANY edit:
```
PLAN:
1. What I will change: <specific line/function/value>
2. What I will NOT touch: <explicit list>
3. How I will verify: <compile/pyflakes/acceptance check>
```
Do not proceed until the plan is written.

## Dependency Tracing (mandatory for core/ and interfaces/)
```
DEPENDENCY CHECK:
- Files that import <target_file>: <list>
- Files that <target_file> imports: <list>
- Impact radius: <which callers are affected>
- Verdict: safe to proceed / requires multi-file protocol
```
Impact radius > 2 callers → switch to Multi-File Protocol.

## Impact Radius Declaration (mandatory before every edit)
```
IMPACT RADIUS:
- Function being changed: <name>
- Known callers: <list from codemap or grep>
- Caller signatures still valid after change: yes / no
- Side effects on other files: <none / describe>
```
Callers break → fix them in the same task or STOP.

## Self-Review Step (mandatory before commit)
After edit, re-read changed lines and confirm they match acceptance criteria. Fix if not. Never commit without self-review.

## Protected Classes / Names
- `core/nina.py` class must remain `Nina` (capital N). Never rename.

## Protected Files — never touch without explicit instruction
```
interfaces/telegram_interface.py
.env
core/router.py
main.py
guardian_engine.py
tools/shell.py
ninagate/main.py
```

## Locked Files — never touch under any circumstances
```
tools/ninasync.py
tests/test_ninasync.py
.ninaignore
requirements.txt
```

## Standard Task Template
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.

SCOPE: <path/to/file.py>
OUT_OF_SCOPE: <everything else>

File: <path/to/file.py>
Do NOT touch: <list>
Task: <plain English description>
Acceptance: <one-line check>
Post-task verify: `python3 -m py_compile <file>` + `pyflakes <file>` + `python3 agy_impact_check.py <file>` — zero errors
Then run OBSERVE loop before committing.
```

## Hot-Path Templates

### PATCH
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.
Mode: PATCH
SCOPE: <file> | OUT_OF_SCOPE: everything else
File: <file>
Do NOT touch: everything except the single target value
Change: replace <old_value> with <new_value> — nothing else
Acceptance: grep confirms new value present, old absent
Post-task verify: `py_compile <file>` — zero errors. Then OBSERVE loop.
```

### INJECT
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.
Mode: INJECT
SCOPE: <file> | OUT_OF_SCOPE: all existing functions
File: <file>
Do NOT touch: all existing functions — append only
Inject: new function `<name>` after line ~<N>: <description>
Acceptance: function exists, all existing functions unchanged, file compiles
Post-task verify: `py_compile` + `pyflakes`. Then OBSERVE loop.
```

### RENAME
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.
Mode: RENAME
SCOPE: <file> | OUT_OF_SCOPE: logic, imports, other symbols
File: <file>
Rename: `<old_name>` → `<new_name>` in this file only
Verify: grep confirms zero occurrences of `<old_name>` remain
Post-task verify: `py_compile` + `pyflakes`. Then OBSERVE loop.
```

## Dry-Run Template
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.
Mode: DRY-RUN — read and report only. Zero file edits. Zero commits.
Task: <what to inspect>
Report: <what to output>
```
Mandatory before any Jules PR merge.

## Rollback Template
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.
Mode: ROLLBACK
File: <file>
Revert: change introduced in commit <sha>
Do NOT touch: <any other files>
Verify: file matches pre-commit state, py_compile passes, guardian reports no drift
```
