# Nina — Personal AI Infrastructure

> **Owner:** M. Baizid Alam · AGM, BASIC Bank PLC · Dhaka, Bangladesh  
> **Hardware:** ASUS VivoBook X530FN · Ubuntu 26.04 · NVIDIA MX150 (CUDA) · Ollama running  
> **Brain:** Perplexity AI (ARCHITECT OVERWATCH role) via GitHub MCP  
> **Repo:** `aibony/nina` · local at `~/nina`

---

## What is Nina?

Nina is a **Single Source of Truth (SSOT) / Super AI** personal infrastructure project.
It provides autonomous code hygiene, self-updating registry + index, AI-assisted
duplicate/dead-code detection, and a local+cloud inference routing layer (NinaGate).

---

## Quick Start — Dev Loop

```bash
cd ~/nina && git pull && python3 nina_debug.py && bash upload_debug_out.sh
```

See [`NDEV.md`](NDEV.md) for the full loop protocol.

---

## Key Directories

| Path | Purpose |
|---|---|
| `core/` | Task classifier, memory, orchestrator |
| `tools/` | OODA audit tools, dedup, registry sync, doc gen |
| `ninagate/` | OpenAI-compat inference proxy (localhost:8080/v1) |
| `git-hooks/` | pre-commit + pre-push OODA governance hooks |
| `scripts/nina_sync.sh` | OODA orchestrator — audit, symlink, registry, vulture |
| `data/` | dependency_graph.json, symbol_map.json, router_cache.json |
| `docs/space/` | All SSOT docs, indices, registries, roadmaps |
| `.cache/` | dedup_cache.json, semantic_embed_cache.json, hook stamps |

---

## Feature Discovery

Grep `NINA_FEATURE:` across the codebase to locate all registered capabilities:

```bash
grep -r 'NINA_FEATURE:' ~/nina --include='*.py' --include='*.sh' --include='*.md'
```

Full human-readable feature list: [`FEATURES.md`](FEATURES.md)

---

## Hook Architecture

```
git commit
  └─► pre-commit
        ├─ Re-entrancy guard (.cache/.precommit_running stamp)
        ├─ SSOT-only bypass  ← NEW 2026-06-21: skips audit when only regen files staged
        ├─ nina_sync.sh hooks  (symlink, registry check)
        └─ nina_sync.sh audit  (vulture, dedup, service health)

git push
  └─► pre-push
        ├─ update_index.py → auto-commit nina_index.json/md [--no-verify]
        └─ background log write (stamp-guarded: only if last entry >60s old)
```

**Convergence guarantee:** After a normal dev commit, the hook pipeline runs once.
The regen commit (index + log update) is SSOT-only so it exits the pre-commit
immediately — the repo settles in 2 commits total, not an infinite loop.

---

## Inference Stack

| Layer | Model | Use |
|---|---|---|
| **Local fast** | Ollama `localfast` | Short tasks, merge resolver <10 lines |
| **Local heavy** | Ollama `localheavy` | Larger reasoning tasks |
| **GPU embed** | Ollama `nomic-embed-text` | Semantic dedup (MX150 CUDA) |
| **Cloud cascade** | NinaGate → providers.json | Heavy inference, LLM verdict on near-dupes |

NinaGate endpoint: `http://localhost:8080/v1` (OpenAI-compat, Bearer `ninagate`)

---

## SSOT Artifacts (auto-generated, do not hand-edit)

- `docs/space/nina_index.json` / `nina_index.md` — full file index
- `docs/space/nina_file_registry.json` — file registry
- `docs/space/nina_repo_hygiene_dashboard.md` — hygiene report
- `nina_update_log.md` — push log (stamp-guarded)
- `data/dependency_graph.json` / `symbol_map.json`

---

## Session Log

| Date | Session | Key Changes |
|---|---|---|
| 2026-06-19 | NDEV protocol established | Loop, task.json, nina_debug.py v2 |
| 2026-06-21 | Convergence + GPU dedup | SSOT bypass guard, incremental hash dedup, semantic dedup (nomic-embed-text/MX150), NinaGate tool wiring, post-push stamp guard |

---

*See [`FEATURES.md`](FEATURES.md) for full capability registry. See [`docs/space/nina_future_roadmap.md`](nina_future_roadmap.md) for planned work.*
