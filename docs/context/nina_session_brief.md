# NINA Session Brief

> **Read this first** at the start of every new agent session (Perplexity, Claude, Jules, Gemini, agy).  
> **Location**: `docs/context/nina_session_brief.md`  
> **Last updated**: **2026-06-24**

---

## Current State

| Component | Status | Notes |
|-----------|--------|-------|
| `core/agent.py` | ✅ Running | Main async loop; KG wired |
| `core/reasoning.py` (`ReasoningKernel`) | ✅ Live | Primary reasoning path |
| `core/goal_manager.py` | ✅ Implemented | SQLite-backed, full state machine, async API |
| `core/knowledge_graph.py` | ✅ Wired | Injected into agent context on every cycle |
| `core/memory_indexer.py` | 🔧 Stub | Needs full implementation |
| `core/context_builder.py` | 🔧 Stub | Used by agent; needs enrichment logic |
| `core/emotion_engine.py` | 🔧 Stub | Placeholder only |
| `core/time_sense.py` | 🔧 Stub | Hermes time-sensing; partial |
| `tools/nina_ssot.py` | ✅ Live | 4-phase SSOT engine — run `--report` after sync |
| `data/nina_ssot.json` | ⏳ PENDING | Skeleton; overwritten on first real run |
| `docs/nina_ssot.md` | ⏳ PENDING | Template; overwritten on first real run |
| `archive/orphan_cognitive/` | 🗄️ Archived | Old `cognitive/` + `cognition/` dirs; history preserved |
| `reasoning_engine.ORPHAN.py` | 🚫 Dead | Old stub — do NOT edit; use `core/reasoning.py` |

---

## What Was Completed (2026-06-24)

1. **`docs/HARDWARE_FIRST.md` created** — MX150 2GB VRAM constraint documented permanently for all agents
2. **`docs/space/` reorganization** — 5 files moved to appropriate subdirs:
   - `rollback_registry.md` → `docs/ops/` (pruned to last 20 entries)
   - `relay_activity_log.md` → `docs/logs/`
   - `nexus_matrix.md` → `docs/context/` (Hardware Gate added to pipeline)
   - `nina_session_brief.md` → `docs/context/` (this file)
   - `nina_dashboard.html` → `interfaces/`
3. **NEXUS pipeline updated** — Hardware Gate check inserted at step 3 of assimilation pipeline

---

## What Was Completed (2026-06-23)

1. **`tools/nina_ssot.py` pushed** — 4-phase SSOT engine: DISCOVER → ANALYSE → WRITE → ENFORCE
2. **`data/nina_ssot.json` pushed** — bootstrap skeleton with `"health": "PENDING"`
3. **`docs/nina_ssot.md` pushed** — human-readable report template
4. **SSOT absorbs** `dependency_mapper.py`, `symbol_mapper.py`, `nina_wiring_audit.py`, `ssot_registry.py` as sub-calls
5. **`nina_sync.sh` integration** — SSOT runs on every sync; exit 1 blocks sync if violations found

---

## What Was Completed (2026-06-22)

1. **Orphan cognitive layers archived** — `git mv` to `archive/orphan_cognitive/`
2. **Dead reasoning engine renamed** — `reasoning_engine.ORPHAN.py`
3. **`goal_manager.py` fully implemented** — states, dependencies, priority queue, async wrappers, singleton
4. **`knowledge_graph.py` wired into `agent.py`** — context injection with graceful fallback
5. **ngit + sync architecture** — transport/OODA split; `post-push` hook fires sync automatically

---

## Active Priorities (Next Session)

- [ ] **Run SSOT first**: `.venv/bin/python tools/nina_ssot.py --report` — get health baseline
- [ ] Fix `TELEGRAMCHATID` alias violation revealed by SSOT
- [ ] Implement `memory_indexer.py` (vector store integration, `store()` + `recall()` methods)
- [ ] Enrich `context_builder.py` (multi-source context fusion)
- [ ] `emotion_engine.py` — stub that returns neutral valence minimum
- [ ] Test full agent loop end-to-end: goal → reasoning → KG → response
- [ ] `nina_error_register.md` — clear resolved entries from 2026-06-22 sprint
- [ ] Fine-tune DULAL model: benchmark Qwen2.5-3B vs Gemma3-1B on MX150, then fine-tune winner

---

## Rules for All Agents

1. **Always read this file + `nina_error_register.md` + `jules_backlog.md` before any code change.**
2. **Always check `docs/HARDWARE_FIRST.md` before suggesting any model or heavy computation.**
3. **Live code lives in `core/`.** `archive/` is read-only history. Never import from `archive/`.
4. **`reasoning_engine.ORPHAN.py` is dead.** The live engine is `core/reasoning.py`.
5. **`goal_manager` singleton:** `from core.goal_manager import goal_manager`
6. **KG is already wired** — do not add duplicate `knowledge_graph` injection in `agent.py`.
7. All service starts: `systemctl --user` only. Never `sudo systemctl` or `nohup`.
8. **SSOT is the authority** — before touching any env var or import chain, run `tools/nina_ssot.py --report`.

---

## Key File Map

```
nina/
├── core/
│   ├── agent.py            ← MAIN LOOP (KG wired here)
│   ├── reasoning.py        ← ReasoningKernel (LIVE)
│   ├── goal_manager.py     ← GoalManager + singleton (LIVE)
│   ├── knowledge_graph.py  ← KnowledgeGraph (wired)
│   ├── memory_indexer.py   ← STUB — needs impl
│   ├── context_builder.py  ← STUB — needs enrichment
│   └── emotion_engine.py   ← STUB
├── tools/
│   ├── nina_ssot.py        ← SSOT engine (LIVE) — run: .venv/bin/python tools/nina_ssot.py --report
│   ├── dependency_mapper.py
│   ├── symbol_mapper.py
│   ├── nina_wiring_audit.py
│   └── ssot_registry.py
├── data/
│   ├── nina_goals.db       ← SQLite goal store (auto-created)
│   └── nina_ssot.json      ← SSOT machine truth (PENDING first run)
├── docs/
│   ├── HARDWARE_FIRST.md   ← MX150 2GB constraint — READ BEFORE ANY MODEL SUGGESTION
│   ├── nina_ssot.md        ← SSOT human report (PENDING first run)
│   ├── context/
│   │   ├── nina_session_brief.md  ← THIS FILE
│   │   └── nexus_matrix.md        ← NEXUS discovery matrix
│   ├── ops/
│   │   └── rollback_registry.md   ← Rollback checkpoints
│   └── logs/
│       └── relay_activity_log.md  ← Session audit trail
├── interfaces/
│   └── nina_dashboard.html        ← Live dashboard UI
└── docs/space/
    ├── nina_error_register.md  ← Active errors (SSOT)
    ├── jules_backlog.md        ← Jules task queue (SSOT)
    └── [other space docs]
```

---

## Four Pillars — Implementation Status

| Pillar | Module | Status |
|--------|--------|--------|
| Memory Persistence | `core/memory_indexer.py` | 🔧 Stub |
| Reasoning Kernel | `core/reasoning.py` | ✅ Live |
| Goal Manager | `core/goal_manager.py` | ✅ Live |
| Knowledge Graph | `core/knowledge_graph.py` | ✅ Wired |

---

## SSOT Health

> Run `.venv/bin/python tools/nina_ssot.py --report` to populate this section.

```
Health:     PENDING (first run required)
Violations: unknown
Last run:   never
```
