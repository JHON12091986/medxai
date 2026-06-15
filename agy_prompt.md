# agy Prompt Rules

## Opening Line (mandatory — copy-paste this to start every agy prompt)
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.
```

## Pre-flight Checklist (run before EVERY task)
1. `git branch --show-current` — confirm you are on `main`. If not, STOP and report.
2. `cat ~/nina/juleslock.txt` — confirm target file is NOT locked
3. Confirm target file is NOT in the protected list below
4. `git status` → confirm working tree is clean before starting

If any check fails: STOP and report. Do not proceed.

## Core Rules
- Plain English only — never raw bash or code in the prompt
- One task, one file at a time — sequential, never parallel
- **Atomic commits:** one logical change = one commit. Never bundle unrelated edits.
- **Idempotency:** every task must be safe to run twice. If run again on an already-patched file, it must produce no diff. Write guarded changes (`if not already X, do X`), never blind appends.
- agy performs ALL Jules PR merges — never use GitHub UI
- Pre-merge: always run DRY-RUN diagnostic on changed files first, then `python3 rule0_audit.py` + `python3 -m py_compile <file>` + `pyflakes <file>` + check `juleslock.txt`
- Post-merge: `./nina_sync.sh` — no exceptions. If `nina_sync.sh` exits non-zero, STOP and report the exact error. Do not proceed with the next task.
- After successful merge + sync: remove the target file's entry from `juleslock.txt`
- Merge conflict? Stop — escalate to Perplexity, no blind resolution
- If a task requires more than 3 file reads + 1 write, it is multi-file scope — STOP and escalate to Gemini CLI or Qwen Code CLI

## Reasoning Protocol (chain-of-thought — mandatory)
Before making ANY edit, output a 3-line plan inside the response:
```
PLAN:
1. What I will change: <specific line/function/value>
2. What I will NOT touch: <explicit list>
3. How I will verify: <compile/pyflakes/acceptance check>
```
Do not proceed with the edit until the plan is written.

## Self-Review Step (mandatory before every commit)
After completing the edit, re-read the changed lines and confirm they match the acceptance criteria before committing. If they do not match, fix and re-read again. Never commit without self-review.

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

File: <path/to/file.py>
Do NOT touch: <list any files or functions to leave alone>   ← keep this high
Task: <plain English description of the single change>
Acceptance: <one-line check — what should be true when done>
Post-task verify: run `python3 -m py_compile <file>` + `pyflakes <file>` — confirm zero errors before committing
```

## Hot-Path Templates

### PATCH — single value/config change (lowest risk)
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.

Mode: PATCH
File: <path/to/file.py>
Do NOT touch: everything except the single target value
Change: on line ~<N>, replace <old_value> with <new_value> — nothing else
Acceptance: grep confirms new value present, old value absent
Post-task verify: `python3 -m py_compile <file>` — zero errors
```

### INJECT — add new function without touching existing ones
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.

Mode: INJECT
File: <path/to/file.py>
Do NOT touch: all existing functions — append only
Inject: a new function `<name>` after line ~<N> with the following behaviour: <description>
Acceptance: function exists, all existing functions unchanged, file compiles
Post-task verify: `python3 -m py_compile <file>` + `pyflakes <file>`
```

### RENAME — safe symbol rename with grep verification
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.

Mode: RENAME
File: <path/to/file.py>
Do NOT touch: logic, imports, other symbols
Rename: `<old_name>` → `<new_name>` in this file only
Verify: grep confirms zero occurrences of `<old_name>` remain, file compiles
Post-task verify: `python3 -m py_compile <file>` + `pyflakes <file>`
```

## Dry-Run / Diagnostic Template (read-only — make NO edits)
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.

Mode: DRY-RUN — read and report only. Zero file edits. Zero commits.
Task: <plain English description of what to inspect/audit>
Report: <what to output — e.g. list of issues, log lines, diff preview>
```
Use this when grepping logs, auditing files, or scanning for issues.
**Mandatory before any Jules PR merge:** run DRY-RUN on all changed files before executing the merge.

## Rollback Template
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.

Mode: ROLLBACK
File: <path/to/file.py>
Revert: the change introduced in commit <sha>
Do NOT touch: <any other files>
Verify: file matches pre-commit state, `python3 -m py_compile <file>` passes, guardian reports no drift
```
Use when a post-merge break is detected and the change needs to be undone immediately.

## Commit Format
- `fix(scope): description (ID)`
- `feat(scope): description (ID)`
- `docs: description`
- `chore: description`
- `ops: description`

**Task ID format:** `nina-YYYYMMDD-NNN` where NNN is a 3-digit sequence for the day (e.g. `nina-20260616-001`).
Increment NNN for each task within the same day. Include the ID in every commit message.
