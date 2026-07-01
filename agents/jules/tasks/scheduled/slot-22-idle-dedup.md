# Slot 22 — IDLE-DEDUP: IdleLoop Entry Deduplication in jules_backlog.md
**Tier:** BACKLOG | **Priority:** P2 | **Interval:** Every 12h (offset :30)
**Problem:** `docs/space/jules_backlog.md` has massive IDLE-* entry bloat — dozens of near-identical entries for the same topics (telegram_interface, config_robustness, provider_routing, etc.) with placeholder `Suggestion 1 / Suggestion 2` content.

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Count total IDLE- entries
grep -c '^### IDLE-' docs/space/jules_backlog.md

# SCAN 2: Count per topic
grep 'Topic:' docs/space/jules_backlog.md | sort | uniq -c | sort -rn | head -10

# SCAN 3: Count placeholder entries (Suggestion 1 / Suggestion 2 with no real content)
grep -c 'Suggestion 1' docs/space/jules_backlog.md

# SCAN 4: Prior cleanup commits?
git log --oneline --all -- docs/space/jules_backlog.md | grep -i 'dedup\|clean\|prune\|idle' | head -5
```

**SKIP IF:** `grep -c 'Suggestion 1' docs/space/jules_backlog.md` returns 0 (all placeholders already resolved or removed)

---

## Task Execution

**Goal:** Deduplicate `IDLE-*` entries in `docs/space/jules_backlog.md`.

**Rules:**
1. For each topic (e.g., `telegram_interface`, `config_robustness`), keep at most **2 IDLE entries** — the one with the most detailed `Analysis` section + the most recent one.
2. Remove all entries where `Analysis` is literally `- Suggestion 1\n- Suggestion 2` with no real content.
3. Keep all entries with real multi-line Analysis content (like IDLE-20260618-1017 provider_routing which has actual scenario descriptions).
4. Do NOT touch any non-IDLE section of the backlog (Sections 1-5, SURGICAL tasks, VAULT/OMNI/PERF/SAND/OBS tasks).
5. Preserve the exact markdown structure of entries that are kept.

**Read the full backlog BEFORE making changes.** The backlog is ~600 lines — understand the structure.

**Target files:** `docs/space/jules_backlog.md` only

**Validation:**
```bash
# After cleanup, placeholder count should be 0 or very low
grep -c 'Suggestion 1' docs/space/jules_backlog.md
# IDLE entry count should be <20
grep -c '^### IDLE-' docs/space/jules_backlog.md
./guardian
```

**PR title:** `chore(backlog): deduplicate IDLE placeholder entries`
