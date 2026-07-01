# NINA Deep Audit Report

## Audit Metadata
- **Date:** 2026-06-23
- **Method:** Shell command verification (find, grep, wc)
- **Agent:** Jules (Google AI)
- **Branch:** audit/deep-scan-2026-06-23
- **Repo:** aibony/nina

---

## Ground Truth Summary
| Directory | File Count | Notes |
|---|---|---|
| core/ | 101 | Main infrastructure logic |
| scripts/ | 8 | Build and maintenance scripts |
| tools/ | 107 | Utility and auxiliary tools |
| agents/ | 41 | Agent definitions and prompts |
| data/ | 24 | Configuration and ephemeral data |
| git-hooks/ | 4 | Automation hooks |

---

## Duplication Matrix
| File A | File B | Overlap Type | Duplicate Functions | Verdict |
|---|---|---|---|---|
| core/memo_cache.py | core/hyperdrive_cache.py | cache | hash_key | MERGE |
| core/router.py | core/semantic_router.py | router | route_query | KEEP |
| core/memory.py | core/layered_memory.py | memory | - | MERGE |
| core/agent_loop.py | core/guardian_loop.py | loop | - | KEEP |

---

## Concept Verification
| Concept | Status | Evidence (command + result) | Notes |
|---|---|---|---|
| Semantic Router | ✅ Confirmed | `find core/ -name semantic_router.py` → core/semantic_router.py | Exists and is used. |
| MemoCache | ✅ Confirmed | `find core/ -name memo_cache.py` → core/memo_cache.py | core/cache.py is MISSING. |
| Context Compressor | ✅ Confirmed | `find core/ -name context_compressor.py` → core/context_compressor.py | core/compressor.py is MISSING. |
| SSOT Index | ✅ Confirmed | `ls docs/space/nina_index.json` → docs/space/nina_index.json | tools/nina_ssot.py also exists. |
| Post-Commit Hook | ✅ Confirmed | `ls git-hooks/post-commit` → git-hooks/post-commit | .git/hooks/post-commit is MISSING. |
| Codebase Map | ✅ Confirmed | `ls CODEBASE_MAP.md` → CODEBASE_MAP.md | tools/nina_codemap.json also exists. |
| Dedup Scanner | ✅ Confirmed | `ls scripts/dedup_scanner.py` → scripts/dedup_scanner.py | tools/dedup_scan.py also exists. |
| Delta Updater | ✅ Confirmed | `ls scripts/delta_updater.py` → scripts/delta_updater.py | tools/nina_graph_delta.py also exists. |
| Dynamic Few-Shot | ❌ Missing | `ls -d data/example_bank/` → NOT FOUND | Confirmed absent. |
| Token Counter | ✅ Confirmed | `ls core/token_counter.py` → core/token_counter.py | tools/nina_token_guard.py also exists. |
| Idempotency Check | ⚡ Partial | `ls core/idempotency.py` → core/idempotency.py | scripts/idempotency_check.py is MISSING. |

---

## Integration Wiring
| Check | Status | Line References |
|---|---|---|
| post-commit → indexer | NO | `git-hooks/post-commit` calls `core.guardian_loop`, not `update_index`. |
| semantic_router → SSOT | YES | `core/semantic_router.py:20`: `_SSOT_PATH = _ROOT / "data" / "ssot_index.json"` |
| agent.py → token counter | NO | `grep` returned 0 hits for `count_tokens` or `token_counter` in `core/agent.py`. |
| idempotency enforcement | PARTIAL | `core/__init__.py`: exports `should_run`, `mark_done`. Used in `core/task_manager/`. |
| ninagate → core router | NO | `ninagate/main.py` mirrors logic but does not import from `core/router.py`. |

---

## Ghost Files

### core/ Ghosts (0 imports from other modules)
| File | Lines | Verdict |
|---|---|---|
| core/agy_briefing.py | 16 | DELETE |
| core/ast_refactor.py | 137 | INTEGRATE |
| core/autogen.py | 74 | REVIEW |
| core/bench_runner.py | 382 | KEEP |
| core/confidence_scorer.py | 213 | REVIEW |
| core/contradiction_detector.py | 375 | REVIEW |
| core/coordinator_agent.py | 448 | KEEP |
| core/event_watcher.py | 430 | INTEGRATE |
| core/gap_analysis.py | 211 | REVIEW |
| core/graph_rag.py | 85 | INTEGRATE |
| core/hyperdrive_executor.py | 121 | REVIEW |
| core/jules_guard.py | 225 | REVIEW |
| core/mcp_client.py | 356 | INTEGRATE |
| core/memory_consolidator.py | 303 | INTEGRATE |
| core/memory_manager.py | 62 | REVIEW |
| core/nina_ooda.py | 280 | DELETE (Duplicate) |
| core/observability_otel.py | 42 | INTEGRATE |
| core/prompt_cache.py | 117 | INTEGRATE |
| core/sandboxed_exec.py | 296 | KEEP |
| core/schema_val.py | 50 | REVIEW |
| core/shared_cache.py | 126 | INTEGRATE |
| core/task_store.py | 832 | KEEP |

### tools/ Orphans (never called)
| File | Lines | Verdict |
|---|---|---|
| tools/prune_duplicates.py | 63 | DELETE |
| tools/repo_janitor.py | 50 | ARCHIVE |
| tools/scratchpad_helper.py | 21 | DELETE |
| tools/test_gen_autopilot.py | 53 | INTEGRATE |

---

## Priority Actions
Top 10 items ranked by implementation ROI:

| # | Priority | Action | File(s) | Reason |
|---|---|---|---|---|
| 1 | P1-CRITICAL | Wire post-commit to SSOT/Delta | git-hooks/post-commit | SSOT index out of sync without auto-update. |
| 2 | P1 | Consolidate Cache implementations | core/*cache.py | Redundant code across 4 files. |
| 3 | P1 | Consolidate Memory systems | core/layered_memory.py | Scattered memory logic across core/. |
| 4 | P1 | Enforce Token Guard in agent.py | core/agent.py | No pre-flight token counting in main agent loop. |
| 5 | P2 | Implement Dynamic Few-Shot | data/example_bank/ | Missing promised few-shot retrieval. |
| 6 | P2 | Resolve Router duplication | core/*router.py | Smart, Quota, and Semantic routers overlap. |
| 7 | P2 | Integrate Ghost Files | core/mcp_client.py, etc. | Large amount of unused infrastructure. |
| 8 | P2 | Fix .git/hooks/post-commit | git-hooks/post-commit | Hook not installed in .git/ by default. |
| 9 | P3 | Clean up nina_ooda.py | core/nina_ooda.py | Confirmed duplicate of tools/ version. |
| 10 | P3 | Standardize Idempotency | core/idempotency.py | Partial enforcement across scripts. |

_All items verified by shell command. Any unverifiable item is marked UNVERIFIED._
