---
name: nina-phase1-roadmap
description: NINA's Phase 1 development roadmap — active priorities, staged tasks, and what's explicitly deferred.
version: 1.1
updated: 2026-06-04
---

# NINA Phase 1 Roadmap

## The Five Real-World Targets
| ID | Target | What NINA does |
|----|--------|----------------|
| T-1 | Expenditure tracker | Log, store, recall, analyze personal spending locally |
| T-2 | Email intelligence | Read BASIC Bank mailboxes, structured triage with urgency flags |
| T-3 | Share market alerts | Monitor DSE/CSE, push Telegram alerts on threshold breaches |
| T-4 | Proactive reminders | Watch context, nudge without being asked |
| T-5 | Personal context memory | Know habits, routines, priorities — inject into every response |

## Stage A — Stop Active Failures COMPLETE (v12.2)
- A-1 R-77 Fix parallel-route RAM guard crash — core/router.py
- A-2 D-01 Delete core/logger.py — deprecated, duplicate log handlers
- A-3 R-78 Fix tool grammar fragility — TOOL/FINAL parse fallback — core/agent.py
- R-01 to R-78 — 65 total issues resolved

## Stage B — Make NINA Smarter (PARTIAL)
- B-1 F-01 Self-check pass — core/agent.py — DONE
- B-2 F-02 Personal context injection — facts.json + core/memory.py — DONE 2026-06-04
  - data/memory/facts.json populated (name, role, bank, language, timezone, domains, style, github, project)
  - core/memory.py patched — Owner block injected at top of build_context() before semantic recall
  - Rollback: upgrades/backups/memory.py.bak.20260604
- B-3 F-03 System prompt rewrite — remove duplicate Available tools line, add tone calibration — core/nina.py — NOT DONE

## Stage C — New Capabilities (NOT STARTED)
- C-1 F-04 Expenditure tracker — tools/finance.py — SQLite ledger, NLP entry, weekly summary, threshold alert
- C-2 F-05 Share market monitor — tools/market.py — cron DSE/CSE, 2h polling 10:00-14:30 Dhaka, 1% threshold Telegram alert
- C-3 F-06 Proactive reminder engine — data/reminders.json — heartbeat cron checks every 15min
- C-4 F-07 Email triage improvement — structured sender/subject/received/urgency_flag output
  - Keywords: LC, SWIFT, MT103, urgent, deadline, Bangladesh Bank
- C-5 F-08 Personal knowledge base — /remember /recall commands — core/memory.py

## Stage D — Stability Hardening (parallel with C, one per session)
- O-06 CRITICAL — Remove cat from shell allowlist — tools/shell.py — path traversal risk
- S-01 SSRF fix — replace substring check with ipaddress module — tools/browser.py
- S-02 Wrap memory file IO in asyncio.to_thread — core/memory.py
- S-04 Model version override dict in NinaConfig — core/config.py

## Current Priority Queue (do in this order)
1. O-06 CRITICAL — remove cat from shell allowlist — tools/shell.py
2. B-3 F-03 — system prompt rewrite — core/nina.py
3. S-01 — SSRF ipaddress fix — tools/browser.py
4. C-1 F-04 — tools/finance.py SQLite expense ledger
5. C-2 F-05 — tools/market.py DSE/CSE alerts
6. Quick unlock: Set EWS_PASSWORD in .env — email features activate with zero code

## Explicitly Deferred (not Phase 1)
- FastAPI interfaces/api.py — Telegram is sufficient
- Prometheus/Grafana — Guardian logs are enough
- 3-tier memory (episodic/semantic/working) — B-2 fixes the real problem
- Full test suite — valuable, not Phase 1 priority
- REST API, dashboards — Phase 2

## One-Line Test for Every Feature
Does this make NINA more like an extension of me, or just more like a chatbot?

## Long-Term Arc
| Phase | What Gets Built |
|-------|----------------|
| Phase 1 (now) | 5 real-world targets: expenditure, email, market alerts, reminders, personal memory |
| Phase 2 | Voice interface over Telegram — NINA speaks back |
| Phase 3 | Multi-agent mode — NINA spawns sub-agents for parallel research |
| Phase 4 | Open-source release — others run their own NINA |
| Phase 5 | Self-improvement — idle loop generates, tests, and proposes its own upgrades |
