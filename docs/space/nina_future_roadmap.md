# Nina Future Roadmap

> Living document — updated each session by Perplexity ARCHITECT OVERWATCH.
> Status: ✅ DONE · 🔄 IN PROGRESS · 📋 PLANNED · 💡 IDEA

---

## Recently Completed (2026-06-21)

| Item | Status | Notes |
|---|---|---|
| SSOT-only convergence guard in pre-commit | ✅ DONE | Breaks dirty-loop; regen-only commits skip audit |
| Incremental hash-cache duplicate scanner | ✅ DONE | `tools/dedup_scan.py`; <1s incremental runs |
| Semantic dedup via Ollama + MX150 CUDA | ✅ DONE | `tools/semantic_dedup.py`; `nomic-embed-text` |
| Post-push log stamp guard (60s) | ✅ DONE | Prevents double-write re-dirty |
| NinaGate tool wiring helper | ✅ DONE | `ninagate_complete()` usable in any tool |
| Doc sweep: FEATURES, NDEV, README, UPDATE_LOG | ✅ DONE | All updated 2026-06-21 |

---

## In Progress

| Item | Status | Notes |
|---|---|---|
| Jules backlog sprint P1 | 🔄 IN PROGRESS | See `jules_backlog.md` + `jules_batch_plan_p1.md` |
| Guardian incremental AST | 🔄 IN PROGRESS | `tools/_guardian_incremental.py` |
| Benchmark routing telemetry | 🔄 IN PROGRESS | `data/router_telemetry.jsonl` |

---

## Next Priorities

| Priority | Item | Rationale |
|---|---|---|
| P1 | Dead-code salvage via semantic dedup LLM verdict | Use NinaGate to classify near-dupe pairs as: keep-both / merge / delete-one |
| P1 | `.cache/` added to `.gitignore` | Dedup caches should not be committed |
| P2 | OODA audit time budget flag | `nina_sync.sh audit --max-seconds 30` to skip expensive steps on fast commits |
| P2 | Semantic dedup integrated into OODA pipeline | Run after hash dedup pass inside `nina_sync.sh` |
| P3 | `nomic-embed-text` swap to `mxbai-embed-large` | Larger context window (512 → 8192 tokens) for better `.md` similarity |
| P3 | NinaGate streaming support | Stream tokens back to terminal for interactive use |
| P3 | Context graph temporal dashboard | HTML view of `nina_graph_delta.py` `--since` queries |
| 💡 | Hermes time-sensing integration | See `hermes_and_time_sensing_blueprint.md` |
| 💡 | 5-wire symbiosis layer | See `nina_5wire_symbiosis_spec.md` |

---

## Architecture Invariants (never regress)

- Pre-commit exits 0 on SSOT-only staged files (convergence guard)
- `.cache/` stamps and dedup caches survive between commits
- NinaGate `providers.json` hot-reloads without service restart
- All features registered with `NINA_FEATURE:` tag in source
- `FEATURES.md` is the human-readable feature registry — kept in sync each session

---

*Roadmap maintained by Perplexity ARCHITECT OVERWATCH. Updated: 2026-06-21.*
