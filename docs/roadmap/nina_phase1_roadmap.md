# NINA Phase 1 — Development Trajectory

**Document type:** Actionable development roadmap
**Scope:** Phase 1 only — what to build, in what order, and why
**Based on:** SWOT analysis, codebase backup, blueprint, master prompt, development policy, and owner Q&A session
**Owner:** M. Baizid Alam — BASIC Bank, Dhaka
**Date:** 2026-05-24

---

## The Core Insight

NINA's purpose is not to compete with Gemini on general knowledge. NINA's purpose is to do things Gemini **cannot** do: act inside your environment, remember your personal context, monitor your real-world signals, and take multi-step action autonomously over Telegram — from a laptop in Dhaka that never sleeps.

The goal for Phase 1 is not "implement every blueprint item." It is to make NINA reliably useful as a **personal operator** for five specific real-world tasks you care about.

---

## The Five Real-World Targets

These come directly from the owner's stated needs:

| # | Target | What NINA does that Gemini cannot |
|---|--------|----------------------------------|
| T-1 | Track personal expenditure | Reads, stores, recalls and analyzes *your* spending data locally |
| T-2 | Email intelligence | Reads *your* BASIC Bank mailboxes, gives subject/sender triage |
| T-3 | Share market alerts | Monitors DSE/CSE and notifies you via Telegram on developments |
| T-4 | Proactive reminders | Watches your context and nudges you without being asked |
| T-5 | Personal context memory | Knows your habits, routines, priorities, and refers to them |

None of these require a dashboard. None require a REST API. All are deliverable over Telegram. All require fixing current weaknesses first.

---

## Phase 1 Roadmap

Ordered strictly: fix crashes first, then smarter reasoning, then new capabilities.

---

### Stage A — Stop Active Failures (Do First, ~1–2 sessions)

These are breaking issues. Nothing else matters until these are resolved.

#### A-1 · Fix `parallel_route` RAM guard crash
- **ID:** R-77
- **File:** `core/router.py`
- **Change:** `self.config.ramguardgb` → `self.config.ram_guard_gb`

#### A-2 · Delete `core/logger.py`
- **ID:** D-01
- **File:** `core/logger.py`
- **Change:** Delete file. Confirm no other module imports it.

#### A-3 · Fix tool grammar fragility (minimum viable guard)
- **ID:** R-78
- **File:** `core/agent.py`
- **Change:** Wrap `TOOL:` / `FINAL:` parsing in a fallback: if neither marker found after all steps, return a graceful "I couldn't complete this" message rather than crashing or silently returning empty string.


### Stage B — Make NINA Smarter (Core Priority, ~2–3 sessions)

NINA feels dumb because she doesn't understand *you*. Better reasoning quality comes from better context injection and a self-check pass before sending answers.

#### B-1 · Self-check pass for complex tasks
- **ID:** F-01
- **File:** `core/agent.py`
- **Change:** After the final answer is formed for task types `research`, `coding`, `sensitive`, `document` — run one additional local model pass asking: "Is this answer complete, accurate and relevant to the original question? If not, revise it." Return the revised answer.

#### B-2 · Personal context injection into every prompt
- **ID:** F-02
- **File:** `core/memory.py`, `core/nina.py`
- **Change:** Add a dedicated `personal_context` section to `facts.json` with structured keys: `occupation`, `employer`, `priorities`, `working_hours`, `personal_habits`, `current_goals`. Inject this as a fixed top section in `build_context()` before semantic recall results — so every single NINA response is grounded in who you are.

#### B-3 · Response tone calibration in system prompt
- **ID:** F-03
- **File:** `core/nina.py` (SYSTEM_PROMPT_TEMPLATE)
- **Change:** Remove the duplicate `Available tools:` section. Add explicit tone calibration: direct, peer-level, not overly formal, proactively flags risk, uses Bangla or English based on your register.


### Stage C — New Capabilities (High Value, ~3–5 sessions)

Only build capabilities that serve the five real-world targets. Everything else waits.

#### C-1 · Expenditure tracker tool
- **ID:** F-04
- **File:** `tools/finance.py` (new)
- **Change:** A simple local tool that can:

#### C-2 · Share market monitor (DSE/CSE alerts)
- **ID:** F-05
- **File:** `tools/market.py` (new) + `crons/manager.py`
- **Change:**

#### C-3 · Proactive reminder engine
- **ID:** F-06
- **File:** `core/nina.py` + `data/reminders.json`
- **Change:**

#### C-4 · Email triage improvement
- **ID:** F-07
- **File:** `tools/office_mail.py`
- **Change:**

#### C-5 · Personal knowledge base (`/remember` and `/recall`)
- **ID:** F-08
- **File:** `core/memory.py` + Telegram command handler
- **Change:**


### Stage D — Stability Hardening (Ongoing, parallel with C)

Do one of these per session alongside Stage C work.

| ID | Change | File | Why |
|----|--------|------|-----|
| S-01 | Fix SSRF substring → `ipaddress` module | `tools/browser.py` | Security debt, Guardian flags it |
| S-02 | Wrap memory file I/O in `asyncio.to_thread` | `core/memory.py` | Blocking I/O in async path causes slow replies |
| S-03 | Fix `ResponseCache.purge_expired` dict mutation | `core/router.py` | RuntimeError during cache purge under load |
| S-04 | Add model version override dict to `NinaConfig` | `core/config.py` | Hardcoded model strings go stale silently |
| S-05 | Add `if not root.handlers` guard in logger setup | `core/nina.py` | Prevents duplicate log handlers on restart |

---

## What Is Explicitly Out of Phase 1

These are not blocked forever — they are just not needed to achieve the five real-world targets.

| Item | Reason to defer |
|------|----------------|
| FastAPI / `interfaces/api.py` | No external automation needed in Phase 1. Telegram is sufficient. |
| Prometheus / Grafana metrics | Explicitly not needed. Guardian + logs is enough. |
| 3-tier memory (episodic/semantic/working) | Overkill for current usage. B-2 personal injection fixes the real problem. |
| Token cost tracking per provider | No budget pressure on free models. |
| Full test suite | Valuable long-term, not Phase 1 priority. |
| Provider YAML consolidation | Low user-impact. Schedule as D-series debt ticket. |

---

## Development Rules for This Phase

These are not the full policy — just the minimum that keeps NINA stable:

1. **One change per session.** Do not stack fixes.
2. **Run Guardian before and after every change** that touches `core/`, `tools/`, or `interfaces/`.
3. **Every change needs a runtime proof** — not just "it didn't crash on import."
4. **If Guardian shows a new BLOCKER after your change, roll back first, investigate second.**
5. **Log the ID, file, and outcome** the same day, even if just in a text note.

---

## Sequence Summary

```
Week 1   A-1 A-2 A-3          (stop crashes and fragility)
Week 2   B-1 B-2 B-3          (smarter reasoning and context)
Week 3   C-1 C-3              (expenditure tracker + reminder engine)
Week 4   C-4 C-2              (email triage improvement + market alerts)
Week 5   C-5 + D-series       (personal knowledge base + stability hardening)
```

This is a guide, not a contract. If something blocks you, skip it and move to the next. If something is easier than expected, pull the next item forward.

---

## What NINA Looks Like After Phase 1

- She does not crash on complex tasks
- She understands who you are and responds accordingly
- She monitors your email and flags what matters
- She watches the share market and pushes alerts to your Telegram
- She tracks your spending and summarizes it on demand
- She reminds you of things without being asked
- She remembers personal facts you teach her

None of these are things you can get from Gemini on your phone. All of them run on your laptop in Dhaka.
