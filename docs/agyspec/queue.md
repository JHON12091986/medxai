# NINA agy Batch Queue
> State machine for autonomous agy loop execution.
> agy reads this file, picks next PENDING batch, executes, marks DONE, repeats.
> DO NOT manually edit status — run_batch.sh manages this automatically.

## Format
| # | File | Specs | Status | Completed |
|---|------|-------|--------|-----------|
| 1 | docs/agyspec/agy_batch_01.md | 12 | DONE | 2026-06-18 |
| 2 | docs/agyspec/agy_batch_02.md | 10 | PENDING | - |
| 3 | docs/agyspec/agy_batch_03.md | 10 | PENDING | - |
| 4 | docs/agyspec/agy_batch_04.md | 10 | PENDING | - |

## Loop Rules (for agy)
1. Read this file
2. Find first row where Status = PENDING
3. Read that batch file fully
4. Execute every ═══ block sequentially
5. Run: `cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh`
6. Update this file: change PENDING → DONE, add today's date
7. Commit: `docs(agyspec): mark batch_NN DONE`
8. Go to step 2 — continue until no PENDING rows remain
9. When all DONE: send Telegram message via nina_sync.sh
