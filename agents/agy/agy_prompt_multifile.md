# agy Multi-File Protocol — Load Only When Needed (~250 tokens)

> Only load this file when a task explicitly requires touching more than one file.
> Default mode is always single-file (see `agy_prompt_core.md` + `agy_prompt_rules.md`).

## When to Use
- Explicit instruction from Perplexity specifying multiple files
- Impact radius check shows callers must be updated alongside the target
- Never self-escalate to multi-file without reporting first

## Protocol
```
Mode: MULTI-FILE
SCOPE: [file_A, file_B, file_C]     ← ordered deepest dependency first
OUT_OF_SCOPE: <everything else — explicit list>
Dependency order rationale: <why this order>

Step 1: DRY-RUN all files — confirm no conflicts, no locked files
Step 2: Edit deepest dependency → OBSERVE loop → commit
Step 3: Edit next layer → OBSERVE loop → commit
Step 4: Edit top-level file → OBSERVE loop → commit
Rollback plan: if any step fails, revert in reverse order using rollback SHAs
```

## Dependency Order Rule
Always edit deepest first (fewest callers), top-level last (most callers).
Never edit a caller before the thing it calls.

## Observe Loop — Applies to Every Step
After each file edit:
```
OBSERVE (step N):
1. git diff HEAD              ← read your own diff
2. Acceptance criteria met:  yes / no
3. Unintended changes:       none / describe
4. Cross-file consistency:   <does this edit align with previous step commits?>
5. Verdict:                  COMMIT STEP N / FIX FIRST
```
Do not advance to the next step until the current step's verdict is COMMIT.

## Rollback Order
If step N fails: revert step N → revert step N-1 → ... → revert step 1.
Use rollback SHAs recorded in `agy_session.md`.
Never skip a revert step — partial rollback leaves the codebase in an inconsistent state.
