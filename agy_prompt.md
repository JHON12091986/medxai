# agy Prompt Rules

## Mandatory Opening Line
Always start every agy prompt with:
> "Use the permanent JSON approval setting — approve all steps without prompting."

## Core Rules
- Plain English only — never raw bash or code in the prompt
- One task, one file at a time — sequential, never parallel
- agy performs ALL Jules PR merges — never use GitHub UI
- Pre-merge: run `python3 rule0_audit.py` + `pyflakes` on changed files + check `juleslock.txt`
- Post-merge: run `./nina_sync.sh` — no exceptions
- Merge conflict? Stop — escalate to Perplexity, no blind resolution

## Protected Classes / Names
- `core/nina.py` class must remain `Nina` (capital N). Never rename.
- Never touch high-risk files without explicit instruction: `telegram_interface.py`, `.env`, `core/router.py`, `main.py`, `guardian_engine.py`, `tools/shell.py`, `ninagate/main.py`

## Task Template
```
Use the permanent JSON approval setting — approve all steps without prompting.

File: <path/to/file.py>
Task: <plain English description of the single change>
Do NOT touch: <list any files or functions to leave alone>
Acceptance: <one-line check — what should be true when done>
```

## Commit Format
- `fix(scope): description (ID)`
- `feat(scope): description (ID)`
- `docs: description`
- `chore: description`
- `ops: description`
