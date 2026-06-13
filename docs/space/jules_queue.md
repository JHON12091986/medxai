# Jules Dispatch Queue
> One active Jules task per file at a time. Check this before submitting any Jules spec.

## Rules
- Before submitting a Jules spec: check ACTIVE column — if target file is listed, wait.
- After PR merges: move row from ACTIVE to COMPLETED and clear the file from the lock.
- Never submit two specs touching the same file simultaneously.

## ACTIVE (in-flight Jules tasks)
| File | Task ID | Jules Session | PR # | Submitted |
|------|---------|---------------|------|-----------|
| _empty_ | — | — | — | — |

## QUEUE (waiting — do not submit yet)
| File | Task ID | Blocked By | Priority |
|------|---------|------------|----------|
| _empty_ | — | — | — |

## COMPLETED (merged PRs — for reference)
| File | Task ID | PR # | Merged |
|------|---------|------|--------|
| ninaflash.py | AG-N-01 | — | 2026-06-13 |
| ninaflash.py | AG-N-02 | — | 2026-06-13 |
