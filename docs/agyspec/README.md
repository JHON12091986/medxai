# NINA agy Spec Registry
> All agy batch specs live here. The system is **self-driving** — you give agy
> ONE prompt and it loops through all PENDING batches autonomously via `run_batch.sh`.
> Each `═══` block inside a batch file = one atomic task (one file, one commit).

---

## How the Self-Driving Loop Works

### Step 1 — Perplexity writes new batches
Tell Perplexity (NINA Space): *"write a batch for X"* or *"write batches from open errors"*.
Perplexity reads the live repo (GitHub MCP), writes `agy_batch_NN.md` with dense specs,
adds a PENDING row to `queue.md`, and pushes in one commit. No manual spec writing needed.

### Step 2 — You give agy ONE prompt (copy-paste, walk away)
```
Use the permanent JSON approval setting — approve all steps without prompting.

Read ~/nina/docs/agyspec/run_batch.sh fully using TOOL:shell.
Then execute the script using TOOL:shell:
  bash ~/nina/docs/agyspec/run_batch.sh

Follow all instructions the script outputs. For each batch file shown:
  - Read it fully
  - Execute every ═══ spec block one at a time
  - py_compile after each file
  - Commit each change
  - Run: cd ~/nina && python3 rule0_audit.py && ./nina_sync.sh
  - Then run the script again to get the next batch
  - Continue until script outputs: ALL BATCHES COMPLETE
```

### Step 3 — agy self-loops via run_batch.sh
`run_batch.sh` reads `queue.md`, finds the next PENDING batch, outputs its contents,
instructs agy to execute all specs, then agy re-runs the script to pick up the next batch.
Loop ends when queue.md has no PENDING rows.

---

## File Map

| File | Purpose |
|------|---------|
| `README.md` | This file — system overview for Perplexity and humans |
| `queue.md` | State machine — tracks PENDING/DONE per batch |
| `run_batch.sh` | Shell script agy executes to self-loop through all batches |
| `agy_batch_NN.md` | Dense spec files — each `═══` block is one atomic task |
| `spec_log.md` | Historical log of completed specs (agy updates after each batch) |
| `run_log.md` | Auto-generated run log (agy appends after each batch) |

---

## Batch Index

| File | Specs | Status | Theme |
|------|-------|--------|-------|
| `agy_batch_01.md` | 12 | DONE | Diagnostic fast-path, nexus guard, System2 cap, shell O-06, idleloop quality gate, nexus injection, ninagate TTL |
| `agy_batch_02.md` | 10 | PENDING | Memory context budget, dedup, ChromaDB fallback, task lock, crons, SSRF guard, config validation, read_file tool, guardian mode, sync exit |
| `agy_batch_03.md` | 10 | PENDING | Router jitter, provider logging, atomic quota write, circuit breaker reset, empty response guard, ninagate tracing, Telegram rate limit, scratchpad bound, sycophancy filter, queue update |
| `agy_batch_04.md` | 10 | PENDING | ninagate_status tool, idleloop startup delay, wiring audit exit, context graph null-check, session_brief fallback, doc_autogen guard, merge dry-run, export cap, market stub, queue update |

---

## Adding More Batches (For Perplexity)

When Bostami asks for a new batch:
1. Read `queue.md` to get the next batch number (last row + 1)
2. Read the target files via GitHub MCP — NEVER write specs from memory
3. Check `nina_error_register.md` OPEN rows + `jules_backlog.md` READY items first
4. Write `agy_batch_NN.md` with dense specs (10 specs per file is the sweet spot)
5. Add a PENDING row to `queue.md`
6. Push both files in one commit
7. Tell Bostami to paste the ONE agy prompt above

**Spec format inside each batch file:**
```
═══════════════════════════════════════════
SPEC-BNN-XX | type(scope): description
ID: SHORT-ID | Type: bug/fix/feat | Risk: LOW/MEDIUM/HIGH | Batch NN
═══════════════════════════════════════════

Use the permanent JSON approval setting — approve all steps without prompting.
Read <file> fully before making any changes.
[precise surgical change with real variable names]
DO NOT TOUCH: [explicit exclusion list]
After editing: python3 -m py_compile <file>
Commit: type(scope): summary (ID) | Batch NN
```

---

## Naming Convention
`agy_batch_NN.md` — zero-padded number, one theme per file.
Next batch to create: check `queue.md` last row and increment.
