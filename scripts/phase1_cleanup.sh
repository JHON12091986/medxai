#!/bin/bash
set -e
cd ~/nina

# --- Phase 1: Delete junk ---
git rm commit_message.txt

# --- Phase 1: Delete old dot dirs (check + remove) ---
git rm -r .agy/ .gemini/ .jules/

# --- Phase 1: Move auto-generated strays ---
mkdir -p data/logs data/graphs docs/generated

git mv nina_update_log.md data/logs/
git mv telemetry.jsonl data/logs/
git mv nina_context_graph.json data/graphs/
git mv nina_commit_index.md docs/generated/
git mv nina_context.md docs/generated/
git mv nina_md_audit.md docs/generated/
git mv nina_sh_py_audit.md docs/generated/
git mv nina_non_sh_py_md_audit.md docs/generated/
git mv agy_session.md docs/generated/
git mv bench_report.md docs/generated/

# --- Commit ---
git add -A
git commit -m "cleanup: Phase 1 — delete stale dot dirs, move auto-generated strays out of root

- Deleted: .agy/, .gemini/, .jules/ (superseded by agy/, gemini/, jules/)
- Deleted: commit_message.txt (runtime junk)
- Moved: nina_update_log.md → data/logs/
- Moved: telemetry.jsonl → data/logs/
- Moved: nina_context_graph.json → data/graphs/
- Moved: nina_commit_index.md, nina_context.md, *_audit.md, agy_session.md, bench_report.md → docs/generated/"

git push
