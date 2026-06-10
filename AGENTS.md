# NINA Agent Context

## Pre-Code Reasoning Scaffold (Mandatory)
- **Goal:** Safe, intentional code changes.
- **Restraint:** NEVER skip steps; NEVER write code before step 7.
- **Action:**
  1. RESTATE task in one sentence.
  2. LOCATE existing patterns (`grep -r "<keyword>" ~/nina/core ~/nina/tools ~/nina/interfaces`).
  3. CONSTRAINTS (Response < 2s, No new deps, Target i5-8265U/MX150).
  4. FAILURE MODE FIRST (Write error handler before happy path).
  5. MINIMAL SCOPE (Stop if >2 files).
  6. PATTERN CHECK (Follow existing repo styles).
  7. WRITE CODE.
  8. SELF-CHECK (`python3 -m py_compile <file> && pyflakes <file>`, `nf check code <file>`, hardware check).

## Local Executor Mandate
- **Goal:** Execute safe local changes and merge Jules PRs.
- **Restraint:** NEVER edit locked files (`juleslock.txt`); NEVER bundle unrelated changes.
- **Action:** Use `nf` (ninaflash) for workflows. Follow verify → log → sync. Consult `docs/space/nina_index.md` before touching governed files.

## Jules (Async Cloud Coder) Mandate
- **Goal:** Multi-file async PRs.
- **Restraint:** NEVER open code-only PRs; NEVER merge own PRs; NEVER pause for confirmation.
- **Action:** Always include `nina_update_log.md` and `docs/space/jules_backlog.md` updates. Stage specific files only (`git add <file>`). Run syntax checks.

## Key Directives (Goal-Restraint-Action)
- **Goal:** Ensure repo stability.
- **Restraint:** NEVER use `git add .`; NEVER touch `.env` or hardcode secrets.
- **Action:** Stage specific files. Route sensitive/banking paths locally. Verify lock state in `~/nina/jules_lock.txt` before edits.
- **Goal:** Pass Guardian Gate.
- **Restraint:** NEVER bundle unrelated changes; NEVER modify `.env`, `data/memory/facts.json`, `upgrades/guardian_baseline.json`.
- **Action:** Pass `python3 -m py_compile <file> && pyflakes <file>`. One purpose per patch.

## High-Risk Files (Local Only, No Direct Edit without Auth)
- `main.py`, `core/router.py`, `interfaces/telegram_interface.py`, `guardian_engine.py`, `tools/shell.py`, `.env`

## Pointers to Full Guides
- **Tool Routing & Workflow:** See `docs/agent-memory/workflow.md`
- **Patterns & Protocols (Logs, PR Merges):** See `docs/agent-memory/patterns.md`
- **Governance:** See `docs/space/nina_index.md`
