# Known Git / Health Issues

## Active

### WARN-001 — Wiring Audit: `tools/merge_resolver.py:184`
- **Status**: Persistent, non-blocking
- **Symptom**: `health=WARN | top_priority=todo.tools_merge_resolver_py_184` in every post-commit output
- **Cause**: `nina_wiring_audit.py` detects an unresolved TODO or broken reference at line 184 of `tools/merge_resolver.py`
- **Impact**: `health=WARN` (not ERROR) — does not block PRs or pushes
- **Resolution**: Fix the TODO/wiring at `tools/merge_resolver.py:184` and re-run `python3 nina_wiring_audit.py`
- **Owner**: Human / next Jules task

### WARN-002 — Missing Tests (16 files)
- **Status**: Persistent, non-blocking
- **Symptom**: 16 `⚠️ Test Coverage` warnings on every pre-push
- **Files**: `core/agy_briefing.py`, `core/cache/prompt_compressor.py`, `core/cognition/*`, `core/executor/async_shell.py`, `core/planner/*`, `core/quota/quota_tracker.py`, `core/task_manager/*`, `tools/guardian_engine.py`
- **Impact**: Metadata Quality Score capped at 80%
- **Resolution**: Create stub test files for each. Jules backlog task recommended.
- **Owner**: Jules backlog

## Resolved

| Issue | Resolution | Date |
|---|---|---|
| 24 stale Jules branches accumulated | Mass-deleted via `git push origin --delete` | 2026-06-20 |
| `provider_metrics.db` always dirty | Added to `.gitignore` | 2026-06-20 |
| `nina_context_graph.json` tracked by mistake | `git rm --cached` + `.gitignore` | 2026-06-20 |
| `post-commit` auto-commit block after `exit 0` (dead code) | Moved before `exit 0` via GitHub MCP | 2026-06-20 |
| Branch index stale after `scripts/` refactor | `python3 tools/update_index.py` on PR branch | 2026-06-20 |
| `git-hooks/pre-commit` not executable | `chmod +x` + reinstalled | 2026-06-20 |
