#!/usr/bin/env bash
# move_root_strays.sh v3 — archive + relocate forbidden root files
# Safe to run multiple times (idempotent). Does NOT commit.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

mkdir -p docs/generated docs/audit data/reports data/graphs data/logs archive/root_strays logs

archive_and_move() {
  local src="$1" dst="$2" arc="$3"
  if [ -f "$ROOT/$src" ]; then
    cp "$ROOT/$src" "$ROOT/$arc" 2>/dev/null || true
    mv "$ROOT/$src" "$ROOT/$dst"
    echo "  archived+moved: $src → $dst"
  fi
}

move_if_exists() {
  local src="$1" dst="$2"
  if [ -f "$ROOT/$src" ]; then
    mv "$ROOT/$src" "$ROOT/$dst"
    echo "  moved: $src → $dst"
  fi
}

echo "📦 Archiving + relocating forbidden root files..."

archive_and_move nina_md_audit.md            docs/generated/nina_md_audit.md            archive/root_strays/nina_md_audit.md
archive_and_move nina_sh_py_audit.md         docs/generated/nina_sh_py_audit.md         archive/root_strays/nina_sh_py_audit.md
archive_and_move "nina_non-sh-py-md_audit.md" "docs/generated/nina_non-sh-py-md_audit.md" "archive/root_strays/nina_non-sh-py-md_audit.md"
archive_and_move bench_report.md             docs/generated/bench_report.md             archive/root_strays/bench_report.md
archive_and_move agy_session.md              docs/generated/agy_session.md              archive/root_strays/agy_session.md
archive_and_move nina_commit_index.md        docs/generated/nina_commit_index.md        archive/root_strays/nina_commit_index.md

move_if_exists efficiency_report.json        data/reports/efficiency_report.json
move_if_exists call_graph_test.json          data/graphs/call_graph_test.json

# nina_update_log.md — merge into logs/, then REMOVE from root
if [ -f "$ROOT/nina_update_log.md" ]; then
  echo "  merging nina_update_log.md into logs/ ..."
  mkdir -p "$ROOT/logs"
  cp "$ROOT/nina_update_log.md" "$ROOT/archive/root_strays/nina_update_log.$(date +%Y%m%d%H%M).md" 2>/dev/null || true
  if [ ! -s "$ROOT/logs/nina_update_log.md" ]; then
    cp "$ROOT/nina_update_log.md" "$ROOT/logs/nina_update_log.md"
    echo "    copied to logs/nina_update_log.md"
  else
    cat "$ROOT/nina_update_log.md" >> "$ROOT/logs/nina_update_log.md"
    echo "    appended to logs/nina_update_log.md"
  fi
  rm "$ROOT/nina_update_log.md"
  echo "    removed from root ✅"
fi

echo ""
echo "✅ Done. Stage and commit:"
echo "   git add -A && git commit -m 'chore: relocate + archive forbidden root strays'"
