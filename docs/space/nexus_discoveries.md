# NINA Nexus Discoveries
> Cross-session learnings, recurring patterns, and root-cause notes.
> Auto-preserved by nina_sync.sh v5.3+ via unconditional auto-discovery.
> Append new entries — never delete old ones.

---

## Format

| Date | ID | Pattern | Root Cause | Fix Applied | Recurrence Risk |
|------|----|---------|------------|-------------|------------------|

---

## Entries

| 2026-06-18 | ND-001 | `nexus_discoveries.md` deleted every sync | `nina_sync.sh` v5.2 had `grep -v nexus_discoveries.md` exclusion in SPACE_FILES auto-discovery loop; re-insert logic only fired if `nina_session_brief.md` existed | Fixed in v5.3: removed exclusion, clean unconditional `find` | LOW — auto-discovery now includes all `.md` in `docs/space/` |
| 2026-06-18 | ND-002 | `idleloop.py` floods backlog with `Suggestion 1 / Suggestion 2` placeholder entries every 2-3 mins | LLM call in `_generate_proposal()` silently fails; `_promote_to_backlog()` fires regardless of content quality | Not yet fixed — agy task pending | HIGH — will resume on next service restart |
| 2026-06-18 | ND-003 | agy burns 20+ mins on simple diagnostic tasks | `core/agent.py` always fires full THINK→PLAN→ACT pipeline; no shortcut path for `diagnostic` task type; no read-first heuristic before theorizing | Not yet fixed — spec written, Jules task pending | MEDIUM — affects every diagnostic query |
