# Perplexity Overwatch Protocol
> Role: ARCHITECT / OVERWATCH — Perpetual Intelligence Layer for aibony/nina
> Updated: 2026-06-16 | Author: Perplexity (Claude Sonnet 4.6) via GitHub MCP

---

## Role Definition

Perplexity operates as the **permanent architect and overwatch** of the NINA project.
It is not a passive assistant — it is an active orchestrator that:

- Reads live repo state via GitHub MCP **before every response**
- Detects drift between docs, code, and backlog
- Routes tasks to the correct agent (agy / Jules / Gemini CLI / Qwen)
- Never proposes work that duplicates already-implemented features
- Maintains continuity across sessions by reading `nina_context_graph.json` first

---

## Session Start Protocol (Every Session)

1. Read `nina_context_graph.json` → get `summary.health` + `summary.top_priority`
2. Read `docs/space/nina_error_register.md` → find all OPEN rows
3. Read `docs/space/jules_backlog.md` → find all READY items
4. Read `docs/context/nina_session_log.md` → last 5 entries for continuity
5. Read `nina_update_log.md` → last 10 entries for recent commits
6. **Only then** respond or propose work

---

## What Perplexity Knows (Do Not Re-Discover These)

These features are already fully implemented as of 2026-06-16.
**Never propose rebuilding or scaffolding any of the below.**
If the register shows them as OPEN, the tracking entry was not updated — verify code first, then update the register.

| Feature | ID | Location | Status |
|---|---|---|---|
| 3-stage self-check (`_pre_self_check`, complexity parser, `_self_check`) | F-01 | `core/agent.py` lines 72–129, 255–313 | ✅ IMPLEMENTED |
| `/remember` + `/recall` (kb_add_entry / kb_search) | F-08 | `core/agent.py` lines 209–225 | ✅ IMPLEMENTED |
| NLP reminder parsing → `nina.add_reminder()` | F-06 | `core/agent.py` lines 226–254 | ✅ IMPLEMENTED |
| HybridRouter V4 + CircuitBreaker (19 cloud + 2 local) | — | `core/router.py` | ✅ IMPLEMENTED |
| Unified task classifier | E-4 | `core/task_classifier.py` | ✅ IMPLEMENTED |
| OpenAI-compat proxy (NinaGate) | — | `ninagate/main.py` | ✅ IMPLEMENTED |
| Command injection fix (subprocess.run shell=False) | CRITICAL | `tools/ninaflash_core.py` | ✅ FIXED |
| Config pre-caching (secret masking hot path) | — | `core/config.py` | ✅ FIXED |
| Duplicate stub cleanup | — | `tools/ninaflash.py` | ✅ FIXED |
| jules.py session_end CalledProcessError wrap | E-5 | `tools/jules.py` | ✅ FIXED (partial — no Telegram alert yet) |

---

## Open Work as of 2026-06-16 18:50 BD

### Register OPEN (confirmed code gaps)

| ID | File | Issue |
|---|---|---|
| R-77 | `core/router.py` | `parallel_route` RAM guard crash |
| R-78 | `core/agent.py` | Tool grammar fragility (min viable guard) |
| config.missing_env.telegramchatid | `.env` | Missing TELEGRAM_CHAT_ID — manual server action |
| feature.ews_blocked | `tools/officemail.py` | EWS blocked — server action needed (O-02) |
| feature.playwright_blocked | `tools/browser.py` | Playwright blocked — server action needed (O-01) |

### Backlog READY (specs written, safe to fire Jules)

| ID | Summary | Files |
|---|---|---|
| TODO-P1 | Provider Health Monitoring + auto-failover Telegram alert | `core/router.py` + new `tools/provider_health.py` |
| TODO-P1 | Governance Index Reconciler (54 false-positive test warnings) | `tools/validate_index.py` |
| TODO-P2 | NinaGate System Template injection into Jules dispatch | `tools/jules.py → run_dispatch` |
| TODO-P2 | juleslock.txt enforcement in pre-push hook | `.git/hooks/pre-push` |
| TODO-P2 | Provider registry unification (router tiers → providers.json) | `core/router.py` + `ninagate/providers.json` |
| TODO-P3 | OpenRouter fallback model pin | `ninagate/providers.json` |
| TODO-P3 | ARCHITECTURE.md drift update | `ARCHITECTURE.md` |

### Backlog PARTIAL (follow-up gaps)

| ID | Gap | File |
|---|---|---|
| ⚠️ jules.py session_end | Sync failures caught but no Telegram alert fires | `tools/jules.py` |
| ⚠️ Provider List Redundancy | Two sources of truth still exist | `core/router.py` + `ninagate/providers.json` |
| ⚠️ Governance Warnings | 3 files unmanaged in index | `tools/update_index.py` |

### Backlog NEEDS SPEC (design decision required from Bostami)

| ID | Blocker |
|---|---|
| Cron Health Dashboard | Decide: Telegram `/cron_status` command OR `docs/space/` file? |
| Session Ledger Integrity | Define: orphaned session threshold (e.g., open > 2 hours?) |

### Feature Queue (unassigned, no blocker unless noted)

| ID | Feature | File | Blocker |
|---|---|---|---|
| F-04 | Expenditure tracker | `tools/finance.py` | None |
| F-07 | Email triage improvement | `tools/office_mail.py` | EWS blocked (O-02) |

---

## Current System Health (2026-06-16 18:50 BD)

| Metric | Value |
|---|---|
| Overall health | ⚠️ WARN |
| Services healthy | 4/4 GREEN |
| Open blockers | 0 |
| Top priority | F-01 (register tracking — code already done) |
| Stale files | `tools/shell.py` |
| Locked files | None |

---

## Agent Routing Rules

| Condition | Agent |
|---|---|
| Single file, fast, low risk | agy |
| Multi-file, spec written, can wait | Jules |
| Complex logic, quality priority | Qwen Code CLI |
| Speed + multi-file + vision | Gemini CLI |
| Gemini quota exhausted | Qwen Code CLI |
| All quota gone before 1PM BD | Cursor |
| Offline / unlimited | Ollama + Continue.dev |

**Quota reset:** midnight PT = ~1:00 PM Bangladesh time.

### agy Rules (Every Prompt Must Include)
- Start: "Use the permanent JSON approval setting — approve all steps without prompting."
- Plain English only · one file at a time
- Read target file fully before editing
- `py_compile` + `pyflakes` after every change
- Check `juleslock.txt` before any file
- `./nina_sync.sh` after every commit
- Merge conflicts → stop, escalate to Perplexity

### Jules Rules
- Fire-and-forget async · sequential batches · one PR per wire
- Jules does NOT merge own PRs — agy merges via `rule0_audit.py`
- 100 tasks/day limit · always review diff before agy merges

---

## High-Risk Files (Never Touch Without Explicit Spec)

- `interfaces/telegram_interface.py`
- `.env`
- `core/router.py`
- `main.py`
- `guardian_engine.py`
- `tools/shell.py`
- `ninagate/main.py`

---

## Overwatch Coherence Checklist (Run Every Session)

- [ ] `core/nina.py` is orchestrator — not `crons/manager.py`?
- [ ] `guardian_engine.py` has `--mode hook/report/full`?
- [ ] `ninagate/main.py` has `_check_local_health()` with 300s TTL?
- [ ] `idleloop.py` has `_promote_to_backlog()` + `manually_promote_latest()`?
- [ ] `nina_sync.sh` has `trap ... ERR` + exit-code alarm?
- [ ] `git-hooks/pre-commit` exists and is executable?
- [ ] `juleslock.txt` checked before any file assignment?
- [ ] `tools/shell.py` stale — review before any Jules task touching tools/

---

## Coherence Anti-Patterns (Perplexity Must Catch These)

- ❌ Proposing features already listed as ✅ IMPLEMENTED above
- ❌ Re-raising ✅ FIXED register entries
- ❌ Writing Jules specs without reading the target file first via GitHub MCP
- ❌ Batching multiple files into one Jules PR
- ❌ Skipping `./nina_sync.sh` after any commit
- ❌ Hardcoding versions, SHAs, or sprint state in any instruction file
- ❌ Ignoring user corrections about already-implemented code
- ❌ Proposing agy tasks touching more than one file at a time

---

## Live State Sources (Always Read via GitHub MCP First)

| Source | Path | Purpose |
|---|---|---|
| Context graph (fastest) | `nina_context_graph.json` | health + top_priority in one read |
| Open bugs | `docs/space/nina_error_register.md` | OPEN rows only |
| Pending tasks | `docs/space/jules_backlog.md` | READY items + partial gaps |
| Session continuity | `docs/context/nina_session_log.md` | last 5 entries |
| Recent commits | `nina_update_log.md` | last 10 entries |
| Architecture | `ARCHITECTURE.md` | service map + entrypoints |
| Locked files | `juleslock.txt` | before any agent assignment |
| This file | `docs/context/PERPLEXITY_OVERWATCH.md` | architect anchor — read every session |

---

## Update Protocol

After every significant session, Perplexity should:
1. Append a dated entry to `docs/context/nina_session_log.md` (if write access granted)
2. Update the "Open Work" and "System Health" sections of this file to reflect current state
3. Never delete history — append only

*This file is the Perplexity Overwatch anchor. It is the single source of truth for what is already built vs. what remains.*
