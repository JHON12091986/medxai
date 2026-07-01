# Universal agy Prompt Stack — Remaining Tasks
## updated: 2026-06-16

This file houses the canonical, ready-to-execute `agy` prompts for the remaining task pipeline. Run them in the designated execution order.

---

## Execution Order Summary

```
RIGHT NOW
  Prompt 1  → CTX-002          Session memory           ZERO risk (COMPLETED)
  Prompt 2  → PIPE-JULES-001A  Diagnose Jules           ZERO risk (COMPLETED)
  Prompt 3  → PIPE-JULES-001B  Repair Jules             MEDIUM (COMPLETED)
  Prompt 4  → PIPE-JULES-001C  Stall watchdog           LOW (COMPLETED)
  Prompt 5  → PIPE-JULES-001D  Validate pipeline        ZERO (COMPLETED)
  Prompt 10 → POST-MERGE-SYNC  After every merge        ZERO (COMPLETED)

AFTER PIPELINE CONFIRMED HEALTHY
  Prompt 6  → R-77             RAM guard crash          MEDIUM
  Prompt 10 → sync
  Prompt 7  → R-78             Grammar guard            LOW
  Prompt 10 → sync
  Prompt 8  → config           TELEGRAMCHATID           ZERO
  Prompt 10 → sync

AFTER ALL BUGS FIXED
  Prompt 9  → BATCH-FEATURES   Add F-01,F-04–F-08 READY LOW
  Prompt 10 → sync
  ↓
  Jules picks them up automatically
  agy merges each PR
  Prompt 10 after each merge
  ↓
  NINA self-improves from here
```

---

## PROMPT 1 — CTX-002: Universal Session Memory (COMPLETED)

```
Use the permanent JSON approval setting — approve all steps without prompting.

Read these files fully before creating anything:
- docs/context/NINA_AGENT_PRIMER.md
- docs/context/NINA_RULES.md
- nina_update_log.md

Task type: ops
Task ID: CTX-002
Risk: ZERO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — Create docs/context/nina_session_log.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Create docs/context/nina_session_log.md with this exact structure:

# NINA Session Log — Universal Agent Memory
## append-only | newest entry at top | max 20 entries retained
## all agents read last 5 entries at session start
## all agents append one entry after every completed task

---
## Session 2026-06-16 | Agent: agy | Task: CTX-001
Status: COMPLETE
Done: Created docs/context/ universal layer — NINA_RULES, NINA_WORKFLOW,
      NINA_OPS, NINA_AGENT_PRIMER. Wired agy skills, GEMINI.md, AGENTS.md,
      .cursor/rules. Upgraded nina_sync.sh with stat -L. Documented in
      ARCHITECTURE.md Section 12.
Commit: ops(context): create universal agent context layer — CTX-001
nina_sync.sh: PASS
Notes: .cursor/rules uses file copies not symlinks (Cursor requirement).
       Symlinks verified for agy, Gemini CLI, Qwen Code.
Next: CTX-002 (session memory), then PIPE-JULES-001A (Jules pipeline fix)
---

Seed with the actual CTX-001 entry above. Read nina_update_log.md
to add any additional real entries from today if present.
Do not invent entries.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — Update docs/context/NINA_AGENT_PRIMER.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Find the section: ## Session Start — Always Do This First
Add one item to the existing numbered list (after existing items):
  Read docs/context/nina_session_log.md — last 5 entries
  → what changed last session, what is in-flight, what to skip

Do not change any other line in this file.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — Update docs/context/NINA_RULES.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Append this new section at the end of the file:

## Session Memory Rule
At the start of every session: read docs/context/nina_session_log.md
(last 5 entries) before any task.
At the end of every completed task: append one entry using the standard
format defined in nina_session_log.md.
Never edit or delete past entries — this file is append-only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — Update .cursor/rules/nina-rules.mdc
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Append one line at the end of the file:
Session memory: read docs/context/nina_session_log.md
(last 5 entries) before any task.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DO NOT TOUCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.env | interfaces/telegram_interface.py | core/router.py | main.py
guardian_engine.py | tools/shell.py | ninagate/main.py
Any Python source file
docs/space/nina_error_register.md | docs/space/jules_backlog.md

No py_compile needed — Markdown only.

Commit: ops(context): add universal session memory log (CTX-002)
Then run: ./nina_sync.sh
```

---

## PROMPT 2 — PIPE-JULES-001A: Diagnose Jules Pipeline (COMPLETED)

```
Use the permanent JSON approval setting — approve all steps without prompting.

Read these files fully before doing anything:
- idleloop.py
- ninajulesgithub.py
- docs/space/jules_backlog.md
- juleslock.txt
- docs/context/nina_session_log.md (last 5 entries)

Task type: ops
Task ID: PIPE-JULES-001A
Risk: ZERO — diagnosis only, no code changes

Goal: Find the exact break point in the Jules automatic pipeline
that is causing: no new tasks → no PRs → no upgrade loop.

Trace this full pipeline in code:
1. idleloop.py — is it generating proposals to data/proposals/?
2. idleloop.py — is _promote_to_backlog() present and callable?
3. docs/space/jules_backlog.md — are there READY entries present?
4. ninajulesgithub.py — is it reading jules_backlog.md correctly?
5. ninajulesgithub.py — is it parsing READY status correctly?
6. ninajulesgithub.py — is it dispatching to Jules API correctly?
7. ninajulesgithub.py — is it polling for new PRs correctly?
8. juleslock.txt — is there a stale lock blocking any file?

Identify the exact break point. It will be one of:
A. proposals not generating
B. _promote_to_backlog() missing or broken
C. READY entries exist but dispatcher never reads them
D. dispatcher fires but Jules API call fails
E. Jules API succeeds but PR polling never detects result
F. stale lock blocking the whole chain
G. ninajulesgithub.service is not running

Do NOT fix anything yet.
Do NOT modify any file.

Report:
- Break point letter (A through G)
- Exact function names involved
- Exact file and line range
- Smallest safe fix (one sentence)

Validation:
python3 -m py_compile idleloop.py
python3 -m py_compile ninajulesgithub.py

No commit.
```

---

## PROMPT 3 — PIPE-JULES-001B: Repair Jules Pipeline (COMPLETED)

```
Use the permanent JSON approval setting — approve all steps without prompting.

Read these files fully before making any changes:
- idleloop.py
- ninajulesgithub.py
- docs/space/jules_backlog.md
- juleslock.txt

Task type: ops
Task ID: PIPE-JULES-001B
Risk: MEDIUM

Apply the fix identified in PIPE-JULES-001A diagnosis.

General repair rules (apply whichever is relevant):

If break is in idleloop.py (proposal promotion):
- Repair _promote_to_backlog() to correctly append READY card
  to docs/space/jules_backlog.md
- Use the exact card format already present in jules_backlog.md
- Guard against duplicate READY cards for the same task ID
- Use asyncio.to_thread for all file writes

If break is in ninajulesgithub.py (dispatch or polling):
- Repair the READY task detection logic
- Ensure status string matching is case-insensitive
- Ensure the Jules API dispatch payload is correctly formed
- Ensure PR polling retries at least 3 times with 60s intervals
  before marking as failed
- On dispatch failure: log WARNING, send Telegram alert,
  do NOT crash the service

If break stale lock in juleslock.txt:
- Add a lock-age guard: if a lock entry is older than 48 hours
  with no corresponding open PR, log WARNING and skip it
  (do NOT silently delete locks)

For all cases — add these log lines:
INFO:  "Jules pipeline: proposal detected — <task_id>"
INFO:  "Jules pipeline: promoted to READY — <task_id>"
INFO:  "Jules pipeline: dispatched to Jules — <task_id>"
INFO:  "Jules pipeline: PR detected — <pr_url>"
WARN:  "Jules pipeline: stall detected — <task_id> age <hours>h"
WARN:  "Jules pipeline: dispatch failed — <task_id> reason <err>"
WARN:  "Jules pipeline: lock conflict — <file> blocked by <lock>"

Do NOT touch:
.env | interfaces/telegram_interface.py | core/router.py | main.py
guardian_engine.py | tools/shell.py | ninagate/main.py | core/nina.py

After editing run:
python3 -m py_compile idleloop.py
python3 -m py_compile ninajulesgithub.py
pyflakes idleloop.py
pyflakes ninajulesgithub.py

Commit: ops(jules-pipeline): restore READY-to-PR automatic flow (PIPE-JULES-001B)
Then run: ./nina_sync.sh
Then run: sudo systemctl restart ninajulesgithub.service
Then run: sudo systemctl status ninajulesgithub.service
```

---

## PROMPT 4 — PIPE-JULES-001C: Add Stall Watchdog (COMPLETED)

```
Use the permanent JSON approval setting — approve all steps without prompting.

Read these files fully before making any changes:
- ninajulesgithub.py
- crons/manager.py
- docs/space/jules_backlog.md

Task type: ops
Task ID: PIPE-JULES-001C
Risk: LOW

Goal: Add a watchdog so Jules pipeline stalls trigger a Telegram
alert and never go silent again.

Changes to make:

In ninajulesgithub.py — add function check_pipeline_health():
1. Read docs/space/jules_backlog.md
2. Find any READY entry where the card's date is older than 24 hours
3. Find any IN-PROGRESS entry older than 48 hours with no open PR
4. For each stall found:
   - Log WARNING: "Jules pipeline stall: <task_id> age <hours>h"
   - Send one Telegram alert via existing notification path
   - Rate-limit: track alerted task IDs in data/pipeline_alerts.json
     (create if absent) — only alert once per task_id per 12h window
5. If no stalls: log INFO "Jules pipeline: healthy"
6. Return list of stalled task IDs (empty list if healthy)

In crons/manager.py — register check_pipeline_health():
- Follow exact pattern of existing cron jobs
- Interval: every 2 hours
- Job ID: "jules_pipeline_health"
- Do not duplicate if job ID already exists

Do NOT touch:
.env | interfaces/telegram_interface.py | core/router.py | main.py
guardian_engine.py | tools/shell.py | ninagate/main.py | core/nina.py

After editing run:
python3 -m py_compile ninajulesgithub.py
python3 -m py_compile crons/manager.py
pyflakes ninajulesgithub.py
pyflakes crons/manager.py

Commit: ops(jules-pipeline): add stall watchdog with Telegram alerting (PIPE-JULES-001C)
Then run: ./nina_sync.sh
```

---

## PROMPT 5 — PIPE-JULES-001D: End-to-End Pipeline Validation (COMPLETED)

```
Use the permanent JSON approval setting — approve all steps without prompting.

Read these files fully before doing anything:
- idleloop.py
- ninajulesgithub.py
- docs/space/jules_backlog.md
- juleslock.txt

Task type: review
Task ID: PIPE-JULES-001D
Risk: ZERO

Goal: Validate the full Jules pipeline end-to-end after the repair.

Steps:
1. Add one temporary TEST-001 card to docs/space/jules_backlog.md
   using the exact current card format — Status: READY
2. Run ninajulesgithub.py dispatch logic manually (dry-run if
   a --dry-run flag exists, otherwise trace the code path)
3. Confirm TEST-001 is detected as READY
4. Confirm lock check passes
5. Confirm dispatch payload is correctly formed
6. Report the last successful stage reached
7. Remove TEST-001 card from jules_backlog.md
8. Report overall: PASS or FAIL with exact failure point

Do NOT actually submit to Jules API unless Bostami explicitly says so.
Do NOT leave TEST-001 in jules_backlog.md after validation.

No commit unless code changed.
```

---

## PROMPT 6 — R-77: RAM Guard Crash Fix

```
Use the permanent JSON approval setting — approve all steps without prompting.

Read core/router.py fully before making any changes.

Task type: bug
Task ID: R-77
Risk: MEDIUM

In core/router.py, find the parallel_route method.
Find the RAM availability check inside it.

Change:
1. Wrap the RAM check in try/except (catch MemoryError, OSError,
   AttributeError, Exception as last resort)
2. On any exception: log WARNING via existing logger —
   "parallel_route: RAM check failed (<err>), falling back to
   single-provider route"
3. Set parallel execution to False and fall through to the
   standard single-provider route path
4. The fallback MUST return a valid response — never raise
   RuntimeError or re-raise to the caller
5. Do not change logic for routes that pass the RAM check

Do NOT touch:
.env | interfaces/telegram_interface.py | main.py
guardian_engine.py | tools/shell.py | ninagate/main.py
core/nina.py | core/agent.py

After editing run:
python3 -m py_compile core/router.py
pyflakes core/router.py

Commit: fix(router): guard parallel_route RAM check with safe fallback (R-77)
Then run: ./nina_sync.sh
Then run: sudo systemctl restart nina.service
Then run: sudo systemctl status nina.service
```

---

## PROMPT 7 — R-78: Tool Grammar Fragility Guard

```
Use the permanent JSON approval setting — approve all steps without prompting.

Read core/agent.py fully before making any changes.

Task type: bug
Task ID: R-78
Risk: LOW

In core/agent.py, find the tool dispatch method — the function
that receives the raw LLM tool-call string or dict and routes it
to the correct tool function.

Change:
1. Before attempting to parse or dispatch, add input sanitization:
   a. Strip leading/trailing whitespace from string inputs
   b. Wrap the parse step in try/except —
      catch: ValueError, KeyError, TypeError, json.JSONDecodeError
   c. On any parse exception:
      - Log WARNING via existing logger with raw input truncated
        to 200 chars: "tool dispatch: malformed input — <input[:200]>"
      - Return user-safe fallback string:
        "I wasn't able to run that tool — please rephrase your request."
2. Guard must NOT alter behavior for well-formed inputs
3. Do not add new imports unless strictly necessary
   (json is already stdlib)

Do NOT touch:
.env | interfaces/telegram_interface.py | core/router.py | main.py
guardian_engine.py | tools/shell.py | ninagate/main.py | core/nina.py

After editing run:
python3 -m py_compile core/agent.py
pyflakes core/agent.py

Commit: fix(agent): add grammar guard at tool dispatch entry point (R-78)
Then run: ./nina_sync.sh
```

---

## PROMPT 8 — config: TELEGRAMCHATID Validation

```
Use the permanent JSON approval setting — approve all steps without prompting.

Read core/config.py fully before making any changes.

Task type: bug
Task ID: config.missing_env.telegramchatid
Risk: ZERO

In core/config.py, find the section that validates required
environment variables at startup.

Change:
1. Add TELEGRAMCHATID to the validation block using the same
   pattern already used for TELEGRAM_BOT_TOKEN and AUTHORIZED_USER_ID
2. If missing or empty: log WARNING (NOT a blocker — non-blocking)
   "config: TELEGRAMCHATID not set — some notification features
   may be unavailable"
   Do NOT raise SystemExit or halt startup
3. Expose as config attribute using existing attribute pattern:
   self.telegram_chat_id = os.getenv("TELEGRAMCHATID", "")

Do NOT touch:
.env | interfaces/telegram_interface.py | core/router.py | main.py
guardian_engine.py | tools/shell.py | ninagate/main.py

After editing run:
python3 -m py_compile core/config.py
pyflakes core/config.py

Commit: fix(config): add non-blocking TELEGRAMCHATID validation (config.missing_env.telegramchatid)
Then run: ./nina_sync.sh
```

---

## PROMPT 9 — Batch Jules Dispatch: F-01, F-04–F-08

```
Use the permanent JSON approval setting — approve all steps without prompting.

Read these files before dispatching:
- docs/space/jules_backlog.md
- juleslock.txt
- docs/context/NINA_WORKFLOW.md

Task type: ops
Task ID: BATCH-FEATURES-001
Risk: LOW

Goal: Add all 6 open feature task cards to jules_backlog.md
as READY so the Jules pipeline picks them up automatically.

Add the following 6 cards to docs/space/jules_backlog.md using
the exact card format already present in the file.
Append after the last existing entry. One card per task.
Do not modify any existing card.

Card 1:
  ID: F-01 | Status: READY | Type: feature
  Title: Agent self-check pass for complex tasks
  File: core/agent.py
  Impact: High | Source: nina_error_register.md
  Acceptance: complex tasks log self-check intent before dispatch;
  ambiguous tasks return clarification prompt

Card 2:
  ID: F-04 | Status: READY | Type: feature
  Title: Expenditure tracker tool
  File: tools/finance.py (create new)
  Impact: Medium | Source: nina_error_register.md
  Acceptance: add_expense / get_expenses / get_total /
  delete_last_expense all functional; data stored in
  data/finance_log.json

Card 3:
  ID: F-05 | Status: READY | Type: feature
  Title: DSE/CSE share market monitor with Telegram alerts
  File: tools/market.py (create new)
  Impact: Medium | Source: nina_error_register.md
  Acceptance: watchlist CRUD works; check_alerts() fires Telegram
  on threshold breach; cron runs every 30min on weekdays 10:00-14:30 BD

Card 4:
  ID: F-06 | Status: READY | Type: feature
  Title: Proactive reminder engine
  File: core/nina.py, crons/manager.py
  Impact: High | Source: nina_error_register.md
  Acceptance: add_reminder and check_reminders work; cron fires
  every 60s; /remind me intent routes correctly

Card 5:
  ID: F-07 | Status: READY | Type: feature
  Title: Email triage and daily digest
  File: tools/office_mail.py
  Impact: Medium | Source: nina_error_register.md
  Acceptance: triage_email() returns URGENT/NORMAL/LOW;
  get_daily_digest() returns formatted summary; tool registered

Card 6:
  ID: F-08 | Status: READY | Type: feature
  Title: /remember and /recall personal knowledge base
  File: core/memory.py, core/agent.py
  Impact: High | Source: nina_error_register.md
  Acceptance: /remember stores to data/personal_kb.json;
  /recall returns matching entries; routed via agent.py
  without touching telegram_interface.py

Do NOT touch:
.env | interfaces/telegram_interface.py | core/router.py | main.py
guardian_engine.py | tools/shell.py | ninagate/main.py

No py_compile needed — Markdown only.

Commit: ops(backlog): add F-01 F-04 F-05 F-06 F-07 F-08 as READY for Jules (BATCH-FEATURES-001)
Then run: ./nina_sync.sh
```

---

## PROMPT 10 — Post-Every-Merge Sync (Mandatory After Each PR)

```
Use the permanent JSON approval setting — approve all steps without prompting.

Task type: ops
Task ID: POST-MERGE-SYNC
Risk: ZERO

Run this exact sequence after every merged PR — no exceptions:

1. cd ~/nina
2. python3 rule0_audit.py
   → if any error: STOP, report, do not continue
3. ./nina_sync.sh
   → if exit code non-zero: STOP, report the error
4. sudo systemctl restart nina.service
5. sudo systemctl status nina.service
   → confirm Active: running within 30 seconds
   → if not running: sudo journalctl -u nina.service -n 50 --no-pager
6. Append session log entry to docs/context/nina_session_log.md:

---
## Session <ISO datetime> | Agent: agy | Task: <TASK-ID>
Status: COMPLETE
Done: <one line summary of what changed>
Commit: <exact commit message>
nina_sync.sh: PASS
Notes: <anything next agent needs to know, or "none">
Next: <next recommended task ID>
---

Do NOT restart ninagate.service or ninajulesgithub.service
unless explicitly instructed by Bostami.

Do NOT touch:
.env | interfaces/telegram_interface.py | core/router.py | main.py
guardian_engine.py | tools/shell.py | ninagate/main.py
```
