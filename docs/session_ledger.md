# Gemini CLI Hallucination-Proof Workflow

## Overview
The Session Continuity Ledger prevents repeated mistakes across Gemini CLI re-runs.

## Typical workflow

### Before starting a Gemini CLI session:
nf session start --tool gemini_cli --task HW-01
nf session preamble --tool gemini_cli
# Then run Gemini with preamble injected:
gemini -p "$(cat ~/nina/data/gemini_preamble.md)

YOUR ACTUAL TASK: ...
"

### During a Gemini CLI session (log progress as you go):
nf session log --step 1 --action 'created tools/local_inference.py' --outcome success
nf session log --step 2 --action 'edited core/router.py import block' --outcome failure --detail 'hallucinated import path tools.inference_engine — does not exist'

### Mark a mistake explicitly to protect future runs:
nf session log --step 2 --action 'import tools.inference_engine' --outcome failure --detail 'module does not exist, correct path is tools.local_inference'

### When session completes successfully:
nf session done --tool gemini_cli

### If Gemini crashes or wanders off:
# Just re-run — the preamble will automatically be present next time:
nf session preamble --tool gemini_cli
gemini -p "$(cat ~/nina/data/gemini_preamble.md)

Resume the task. Do not restart from scratch.
"

## How mistakes are remembered
Every failure logged via 'nf session log --outcome failure' is fingerprinted and stored
in data/session_ledger.json under the mistakes[] array. On every subsequent re-run,
generate_preamble() injects the top 5 most-seen mistakes into the prompt header.
The seen_count field tracks recurrence — mistakes seen 3+ times are prioritized.

## Data file
~/nina/data/session_ledger.json — human-readable JSON, safe to inspect/edit manually.
~/nina/data/gemini_preamble.md — auto-generated, overwritten each session start.
