# agy Prompt Rules

## Opening Line (mandatory — copy-paste this to start every agy prompt)
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.
```

## Pre-flight Checklist (run before EVERY task)
1. `cat ~/nina/juleslock.txt` — confirm target file is NOT locked
2. Confirm target file is NOT in the protected list below
3. `git status` → confirm working tree is clean before starting
If any check fails: STOP and report. Do not proceed.

## Core Rules
- Plain English only — never raw bash or code in the prompt
- One task, one file at a time — sequential, never parallel
- agy performs ALL Jules PR merges — never use GitHub UI
- Pre-merge: `python3 rule0_audit.py` + `pyflakes` on changed files + check `juleslock.txt`
- Post-merge: `./nina_sync.sh` — no exceptions
- Merge conflict? Stop — escalate to Perplexity, no blind resolution

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
Task: <plain English description of the single change>
Do NOT touch: <list any files or functions to leave alone>
Acceptance: <one-line check — what should be true when done>
```

## Dry-Run / Diagnostic Template (read-only — make NO edits)
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.

Mode: DRY-RUN — read and report only. Zero file edits. Zero commits.
Task: <plain English description of what to inspect/audit>
Report: <what to output — e.g. list of issues, log lines, diff preview>
```
Use this when grepping logs, auditing files, or scanning for issues.

## Commit Format
- `fix(scope): description (ID)`
- `feat(scope): description (ID)`
- `docs: description`
- `chore: description`
- `ops: description`
