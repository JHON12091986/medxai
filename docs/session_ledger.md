# Session Ledger

## Overview
Operational log of NINA dev sessions — one entry per session. Records what broke, what was fixed, and what the next action is.

## Purpose
Give ARCHITECT OVERWATCH and ninaflash instant orientation at the start of any session without reading the full CHANGELOG or error register.

## Usage
- **Append one row per session** at session end (or after a significant fix mid-session).
- **Read the latest row first** before starting any new work.
- **Never edit old rows** — append only.
- Full error detail → `docs/space/nina_error_register.md`
- Version history → `docs/CHANGELOG.md`

---

## Log

| # | Date (BDT) | Session Focus | Broke / Found | Fixed | Next Action |
|---|------------|---------------|---------------|-------|-------------|
| 001 | 2026-06-23 00:28 | Telegram silence debug | `TypeError: 'method' object is not iterable` — `classify_task(text, self._local_fast)` passed method ref as messages arg (`telegram_interface.py:474,752`); duplicate process PID 111639+112058 | Both fixed — call sites → `classify_task(text, [])`, service restarted | Verify NINA responds in Telegram; patch `OPENAI_API_KEY` dummy value |

---

## Gemini CLI Hallucination-Proof Workflow

> This section documents the `nf session` tooling that auto-generates preambles for Gemini CLI sessions.

### Before starting a Gemini CLI session
```bash
nf session start --tool gemini_cli --task HW-01
nf session preamble --tool gemini_cli
gemini -p "$(cat ~/nina/data/gemini_preamble.md)

YOUR ACTUAL TASK: ...
"
```

### During a session (log progress as you go)
```bash
nf session log --step 1 --action 'created tools/local_inference.py' --outcome success
nf session log --step 2 --action 'edited core/router.py import block' --outcome failure --detail 'hallucinated import path tools.inference_engine — does not exist'
```

### Mark a mistake explicitly
```bash
nf session log --step 2 --action 'import tools.inference_engine' --outcome failure --detail 'module does not exist, correct path is tools.local_inference'
```

### On session completion
```bash
nf session done --tool gemini_cli
```

### If Gemini crashes or wanders off
```bash
nf session preamble --tool gemini_cli
gemini -p "$(cat ~/nina/data/gemini_preamble.md)

Resume the task. Do not restart from scratch.
"
```

## How mistakes are remembered
Every `--outcome failure` is fingerprinted and stored in `data/session_ledger.json` under the `mistakes[]` array. On every re-run, `generate_preamble()` injects the top 5 most-seen mistakes into the prompt header. `seen_count` tracks recurrence — mistakes seen 3+ times are prioritized.

## Data files
- `~/nina/data/session_ledger.json` — human-readable JSON, safe to inspect/edit manually.
- `~/nina/data/gemini_preamble.md` — auto-generated, overwritten each session start.
