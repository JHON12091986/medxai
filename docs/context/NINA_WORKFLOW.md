# NINA Workflow — Jules Pipeline & Backlog Protocol
## updated: 2026-06-16

## Backlog Status Values
READY       → work can start immediately, no blockers
PENDING     → waiting on dependency or approval
IN-PROGRESS → Jules PR is open
DONE        → merged, nina_sync.sh ran, register updated

## juleslock.txt — How to Use
Before assigning any file to Jules or agy:
1. Read juleslock.txt
2. If target file appears in juleslock.txt → STOP, do not assign
3. Report the conflict to Perplexity

## Jules PR Merge Sequence — agy Performs This
1. python3 rule0_audit.py
2. python3 -m py_compile <changed file>
3. pyflakes <changed file>
4. Read juleslock.txt — target file must NOT be listed
5. Review the diff — confirm it matches the original spec exactly
6. Merge PR using agy (never GitHub UI, never manually)
7. ./nina_sync.sh
8. Update docs/space/nina_error_register.md — mark row FIXED or DONE
9. Update docs/space/jules_backlog.md — mark card DONE

## Jules Rules
- Jules does NOT merge its own PRs — agy always merges
- One PR per task wire — never bundle
- Fire-and-forget — do not wait interactively for Jules
- 100 tasks/day hard limit
- Always review diff before merge — never auto-approve without reading it

## idleloop → Jules Automatic Pipeline
idleloop.py generates proposal
  ↓ impact == High
_promote_to_backlog() appends READY card to jules_backlog.md
  ↓ Telegram alert sent to Bostami
Bostami approves
  ↓
Jules dispatched via ninajulesgithub.py
  ↓ PR opened
agy runs: rule0_audit + py_compile + pyflakes + lock check
  ↓ all pass
agy merges PR
  ↓
nina_sync.sh → Google Drive backup → git push
  ↓
nina_error_register.md updated → backlog card DONE

## Pipeline Stall Detection
If a READY card is older than 24 hours with no PR → alert Bostami via Telegram.
If no new PR in 48 hours → treat as WARN, diagnose ninajulesgithub.py.
