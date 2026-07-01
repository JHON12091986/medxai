# agy Core — Always Loaded (~180 tokens)

## Opening Line (mandatory — copy-paste to start EVERY prompt)
```
Permanent approval mode active — all steps pre-approved, no confirmation needed.
```

## Pre-flight (run before EVERY task)
1. `git branch --show-current` — must be `main`. If not, STOP.
2. `cat ~/nina/juleslock.txt` — target file must NOT be locked.
3. Target file must NOT be in the protected list (see `agy_prompt_rules.md`).
4. `git status` — working tree must be clean.
5. Read last 5 entries of `~/nina/agy_session.md`.
6. Read target file rows from `~/nina/nina_codemap.md`.

If any check fails: STOP and report. Do not proceed.

## Scope Sandbox (mandatory — declare before every task)
```
SCOPE: <path/to/target_file.py>          ← the ONLY file agy may edit
ALLOWED_READS: <file1, file2 or "codemap + session only">
OUT_OF_SCOPE: <explicit list of files NOT to touch>
```
If the task requires touching a file outside SCOPE without a Multi-File Protocol, STOP and report.

## Observe Loop (mandatory — before every commit)
After completing the edit, run:
```
OBSERVE:
1. git diff HEAD              ← read your own diff line by line
2. Acceptance criteria met:  yes / no
3. Unintended changes:       none / describe
4. Verdict:                  COMMIT / FIX FIRST
```
Do not commit until Verdict is COMMIT.

## Session Journal (mandatory — after every commit)
Append to `~/nina/agy_session.md`:
```markdown
## <TASK_ID> | <file>
Changed: <what changed>
Did NOT touch: <explicit list>
Side effects: <none / describe>
Rollback SHA: <previous commit sha>
```

## Commit Format
`fix(scope): description (nina-YYYYMMDD-NNN)`
`feat(scope): description (nina-YYYYMMDD-NNN)`
`docs:` / `chore:` / `ops:`

---
> Full rules: `agy_prompt_rules.md` | Multi-file: `agy_prompt_multifile.md` | Anti-patterns: `agy_antipatterns.md`
