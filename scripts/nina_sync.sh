#!/usr/bin/env bash
# =============================================================================
# nina_sync.sh  v10.5  —  OODA-loop autonomous sync  (SSOT SNAKE EDITION)
# Observe → Orient → Decide → Act  →  hook reinstall  →  repeat 🐍
#
# NEW in v10.5:
#   • A7 post-resolver reconcile — after PR resolver exits, nina_sync re-fetches
#     origin/main, rebases local commits on top, then pushes. Closes the gap
#     where local stayed permanently ahead of a changed origin after a merge.
#
# NEW in v10.4:
#   • A7 PR resolver — calls scripts/nina_pr_resolver.py when open PRs exist
#     instead of silently skipping push. Fully automatic merge pipeline.
#
# NEW in v10.3:
#   • A3 dead-code scan uses PY() helper (venv python3) — fixes "vulture not
#     installed" false negative when system python3 lacks the venv packages
#
# NEW in v10.2:
#   • Vulture now uses vulture_whitelist.py — false positives suppressed
#   • Dead-code scan excludes upgrades/backups/ and archive/ dirs
#   • GIT_PUSH_IN_FLIGHT guard also checks .push_in_flight file
#   • post-push mode now triggers registry sync (fixes orphan accumulation)
#
# NEW in v10.1:
#   • A5.5 backup fully inlined — no generate_backups.sh delegation
#   • NEED_BACKUP DECIDE flag (consistent with all other steps)
#   • Inline 6h age guard via backups/.last_backup_ts stamp file
#   • write_if_changed on claude_feed + repo_manifest outputs
#   • No external writes to nina_update_log.md (dirty loop fix)
#
# NEW in v10.0:
#   • SSOT Registry (docs/space/nina_file_registry.json) — every file has a
#     tuple: path/purpose/ssot/symlinks/consumers/ast_exports/intj|intm/redundancy
#   • Idempotency guards on every ACT step (hash-gated writes)
#   • Symlink audit  (A0.5) — broken/dangling symlinks flagged
#   • Semantic AST index  (A1.5) — docstrings extracted per .py file
#   • Registry orphan check  (A2.5) — files not in registry = undiscoverable
#   • INTJ/INTM drift check  (A3.5) — mirrors verified against source
#   • Dedup on EVERY run (not weekly only) with semantic layer
#   • git hook chains back into audit mode → snake never breaks
#
# Safe for: Baizid direct, Jules PR merge, agy push, Cursor/OpenCode edit,
#           Gemini patch, Perplexity-triggered, cron, systemd OnCalendar
# =============================================================================
set -euo pipefail

# ── GIT_PUSH_IN_FLIGHT guard (prevents SHA race during push/amend) ──
if [[ "${GIT_PUSH_IN_FLIGHT:-}" == "1" ]]; then
  echo "[nina_sync] Push in flight — OODA skipped to prevent SHA race."
  exit 0
fi
# Also check file-based flag (set by ngit)
REPO_ROOT_EARLY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." ; pwd)"
if [[ -f "$REPO_ROOT_EARLY/.push_in_flight" ]]; then
  echo "[nina_sync] .push_in_flight present — OODA skipped."
  exit 0
fi
IFS=$'\n\t'

# ── paths ────────────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." ; pwd)"
LOG="$REPO_ROOT/logs/nina_sync.log"
REGISTRY="$REPO_ROOT/docs/space/nina_file_registry.json"
PY()  { PYTHONPATH="$REPO_ROOT" "$REPO_ROOT/venv/bin/python3" "$@"; }
TS()  { date '+%Y-%m-%d %H:%M:%S'; }
mkdir -p "$REPO_ROOT/logs" "$REPO_ROOT/.cache"

# ── Telegram alert (non-blocking) ────────────────────────────────────────────
alert() {
  local msg="[nina_sync v10.5] $1"
  (
    cfg="$REPO_ROOT/config/telegram.cfg"
    [[ -f "$cfg" ]] && source "$cfg"
    [[ -n "${TELEGRAM_TOKEN:-}" && -n "${TELEGRAM_CHAT:-}" ]] &&
      curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
           -d chat_id="$TELEGRAM_CHAT" -d text="$msg" > /dev/null 2>&1 || true
  ) &
}

# ── trap ERR ─────────────────────────────────────────────────────────────────
trap 'alert "❌ CRASH at line $LINENO — $BASH_COMMAND" ; echo "$(TS) CRASH line $LINENO" >> "$LOG"' ERR

log()  { echo "$(TS)  $*" | tee -a "$LOG"; }
sep()  { echo "$(TS)  ── $* ──" | tee -a "$LOG"; }

# ── idempotency guard: write file only if content changed ────────────────────
write_if_changed() {
  local dst="$1"
  local src="$2"   # temp file with new content
  if [[ ! -f "$dst" ]] || ! diff -q "$src" "$dst" > /dev/null 2>&1; then
    cp "$src" "$dst"
    echo "changed"
  else
    echo "unchanged"
  fi
  rm -f "$src"
}

# ── args ─────────────────────────────────────────────────────────────────────
MODE="${1:-all}"   # all | pull-only | push-only | hooks | audit | post-push

# =============================================================================
# PHASE 0 — HOOKS (always, takes <1 s)
# =============================================================================
_install_hooks() {
  local pre_commit_src="$REPO_ROOT/git-hooks/pre-commit"
  local pre_push_src="$REPO_ROOT/git-hooks/pre-push"

  local NEW_HOOK
  NEW_HOOK=$(cat <<'HOOK'
#!/usr/bin/env bash
# nina pre-commit hook — SSOT snake: every commit re-enters OODA
REPO_ROOT=$(git rev-parse --show-toplevel)
[[ -f "$REPO_ROOT/.push_in_flight" ]] && exit 0
bash "$REPO_ROOT/scripts/nina_sync.sh" hooks
bash "$REPO_ROOT/scripts/nina_sync.sh" audit
HOOK
)
  mkdir -p "$REPO_ROOT/git-hooks"
  if [[ ! -f "$pre_commit_src" ]] || [[ "$(cat "$pre_commit_src")" != "$NEW_HOOK" ]]; then
    printf '%s\n' "$NEW_HOOK" > "$pre_commit_src"
    chmod +x "$pre_commit_src"
  fi

  for h in pre-commit pre-push post-push; do
    src="$REPO_ROOT/git-hooks/$h"
    dst="$REPO_ROOT/.git/hooks/$h"
    [[ -f "$src" ]] && { cp "$src" "$dst"; chmod +x "$dst"; }
  done
  log "hooks installed"
}
_install_hooks
[[ "$MODE" == "hooks" ]] && exit 0

# =============================================================================
# ██████  OBSERVE  ████████████████████████████████████████████████████████████
# =============================================================================
sep "OBSERVE"
cd "$REPO_ROOT"

LAST_SYNC_SHA=$(git rev-parse HEAD 2>/dev/null || echo "none")

git fetch origin main --quiet 2>/dev/null || true
LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "none")
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "none")
BASE=$(git merge-base HEAD origin/main 2>/dev/null || echo "none")

if   [[ "$LOCAL" == "$REMOTE" ]]; then SYNC_STATE="up-to-date"
elif [[ "$LOCAL" == "$BASE"   ]]; then SYNC_STATE="behind"
elif [[ "$REMOTE" == "$BASE"  ]]; then SYNC_STATE="ahead"
else                                    SYNC_STATE="diverged"
fi

if command -v gh &>/dev/null; then
  OPEN_PRS=$(gh pr list --state open --json number --jq 'length' 2>/dev/null || echo "0")
else
  ALL_PR_HEADS=$(git ls-remote origin 'refs/pull/*/head' 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/pull/||;s|/head||' | sort -n)
  ALL_PR_MERGES=$(git ls-remote origin 'refs/pull/*/merge' 2>/dev/null \
    | awk '{print $2}' | sed 's|refs/pull/||;s|/merge||' | sort -n)
  OPEN_PRS=$(comm -23 <(echo "$ALL_PR_HEADS") <(echo "$ALL_PR_MERGES") | wc -l | tr -d ' ')
fi

DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
STASH_DEPTH=$(git stash list 2>/dev/null | wc -l | tr -d ' ')
log "sha=$LAST_SYNC_SHA state=$SYNC_STATE open_prs=$OPEN_PRS dirty=$DIRTY stash_depth=$STASH_DEPTH"

[[ "$STASH_DEPTH" -gt 20 ]] && { git stash clear; log "stash pile-up cleared"; }

# ── OBSERVE: file system snapshot for registry diff ──────────────────────────
FS_SNAPSHOT=$(mktemp)
find "$REPO_ROOT" \
  -not -path '*/.git/*' \
  -not -path '*/venv/*' \
  -not -path '*/.venv/*' \
  -not -path '*/.aider*' \
  -not -path '*/.mypy_cache/*' \
  -not -path '*/.pytest_cache/*' \
  -not -path '*/__pycache__/*' \
  -not -path '*/logs/*' \
  -not -path '*/.cache/*' \
  -not -name '*.pyc' \
  -not -name '*.log' \
  -type f -o -type l 2>/dev/null \
  | sed "s|$REPO_ROOT/||" | sort > "$FS_SNAPSHOT" || true
FS_COUNT=$(wc -l < "$FS_SNAPSHOT" | tr -d ' ')
log "fs_snapshot: $FS_COUNT files/symlinks discovered"

# =============================================================================
# ██████  ORIENT  █████████████████████████████████████████████████████████████
# =============================================================================
sep "ORIENT"

if [[ "$MODE" != "push-only" && "$MODE" != "audit" && "$MODE" != "post-push" ]]; then
  if [[ "$SYNC_STATE" == "behind" || "$SYNC_STATE" == "diverged" ]]; then
    STASH_MSG="nina_sync_$(date +%s)"
    git stash push -u -m "$STASH_MSG" 2>/dev/null || true
    PULL_OK=false
    for attempt in 1 2 3; do
      if git pull --rebase origin main >> "$LOG" 2>&1; then
        PULL_OK=true; break
      else
        log "pull attempt $attempt failed — aborting rebase"
        git rebase --abort 2>/dev/null || true
        sleep 3
      fi
    done
    $PULL_OK || { alert "⚠️ pull failed 3× — manual fix needed"; log "pull failed; continuing"; }
    if git stash list | grep -q "$STASH_MSG"; then
      git stash pop 2>/dev/null \
        || { git checkout -- . 2>/dev/null || true; git stash drop 2>/dev/null || true; }
    fi
  else
    log "sync_state=$SYNC_STATE — pull skipped"
  fi
fi

NEW_SHA=$(git rev-parse HEAD 2>/dev/null || echo "none")
CHANGED_FILES=$(git diff --name-only "$LAST_SYNC_SHA" "$NEW_SHA" 2>/dev/null || echo "")
CHANGED_COUNT=$(printf "%s\n" "$CHANGED_FILES" | grep -c . 2>/dev/null || true)
CHANGED_COUNT=${CHANGED_COUNT:-0}
log "new_sha=$NEW_SHA changed=$CHANGED_COUNT files"

# =============================================================================
# ██████  DECIDE  █████████████████████████████████████████████████████████████
# =============================================================================
sep "DECIDE"

NEED_INDEX=false
NEED_SEMANTIC_INDEX=false
NEED_DOC_AUDIT=false
NEED_SYMLINK_AUDIT=false
NEED_REGISTRY_SYNC=false
NEED_INTJM_CHECK=false
NEED_DEAD_CODE=false
NEED_DUP_CHECK=false
NEED_REDUNDANCY=false
NEED_BACKUP=false
NEED_SERVICE_RESTART=false

echo "$CHANGED_FILES" | grep -qE '\.(py|md|json|sh)$' && NEED_INDEX=true
[[ "$MODE" == "all" ]] && NEED_INDEX=true

echo "$CHANGED_FILES" | grep -qE '\.py$' && NEED_SEMANTIC_INDEX=true
[[ "$MODE" == "all" ]] && NEED_SEMANTIC_INDEX=true

echo "$CHANGED_FILES" | grep -q 'docs/' && NEED_DOC_AUDIT=true
[[ "$MODE" == "all" || "$MODE" == "audit" ]] && NEED_DOC_AUDIT=true

[[ "$MODE" == "all" || "$MODE" == "audit" ]] && NEED_SYMLINK_AUDIT=true
echo "$CHANGED_FILES" | grep -qE '(AGENTS|GEMINI|CLAUDE)\.md' && NEED_SYMLINK_AUDIT=true

[[ "$MODE" == "all" || "$MODE" == "audit" || "$MODE" == "post-push" ]] && NEED_REGISTRY_SYNC=true
if [[ "${CHANGED_COUNT:-0}" =~ ^[0-9]+$ ]] && [[ "${CHANGED_COUNT:-0}" -gt 0 ]]; then NEED_REGISTRY_SYNC=true; fi

$NEED_REGISTRY_SYNC && NEED_INTJM_CHECK=true

NEED_DEAD_CODE=true
NEED_DUP_CHECK=true

$NEED_REGISTRY_SYNC && NEED_REDUNDANCY=true

[[ "$MODE" == "all" ]] && NEED_BACKUP=true

echo "$CHANGED_FILES" | grep -qE '\.(py|service)$' && NEED_SERVICE_RESTART=true

log "index=$NEED_INDEX semantic=$NEED_SEMANTIC_INDEX doc_audit=$NEED_DOC_AUDIT symlink=$NEED_SYMLINK_AUDIT registry=$NEED_REGISTRY_SYNC intjm=$NEED_INTJM_CHECK dead_code=$NEED_DEAD_CODE dup=$NEED_DUP_CHECK redundancy=$NEED_REDUNDANCY backup=$NEED_BACKUP svc=$NEED_SERVICE_RESTART"

# =============================================================================
# ██████  ACT  ████████████████████████████████████████████████████████████████
# =============================================================================
sep "ACT"

# ── A0.5: Symlink audit ───────────────────────────────────────────────────────
if $NEED_SYMLINK_AUDIT; then
  log "symlink audit…"
  SYM_OUT="$REPO_ROOT/logs/symlink_audit.txt"
  TMP_SYM=$(mktemp)
  {
    echo "# Symlink Audit — $(TS)"
    echo ""
    echo "## Broken/Dangling symlinks"
    find "$REPO_ROOT" -not -path '*/.git/*' -not -path '*/venv/*' \
      -not -path '*/.venv/*' -not -path '*/.aider*' \
      -not -path '*/.mypy_cache/*' -not -path '*/.pytest_cache/*' \
      -type l 2>/dev/null | while read -r link; do
        if [[ ! -e "$link" ]]; then
          target=$(readlink "$link" 2>/dev/null || echo "unreadable")
          echo "  BROKEN: ${link#$REPO_ROOT/} -> $target"
        fi
      done
    echo ""
    echo "## All symlinks"
    find "$REPO_ROOT" -not -path '*/.git/*' -not -path '*/venv/*' \
      -not -path '*/.venv/*' -not -path '*/.aider*' \
      -not -path '*/.mypy_cache/*' -not -path '*/.pytest_cache/*' \
      -type l 2>/dev/null | while read -r link; do
        target=$(readlink "$link" 2>/dev/null || echo "unreadable")
        status=$([[ -e "$link" ]] && echo "OK" || echo "BROKEN")
        echo "  [$status] ${link#$REPO_ROOT/} -> $target"
      done
  } > "$TMP_SYM"
  BROKEN_COUNT=$(grep -c 'BROKEN:' "$TMP_SYM" 2>/dev/null || true)
  BROKEN_COUNT=${BROKEN_COUNT:-0}
  RESULT=$(write_if_changed "$SYM_OUT" "$TMP_SYM")
  log "symlink audit: $BROKEN_COUNT broken ($RESULT)"
  if [[ "${BROKEN_COUNT:-0}" =~ ^[0-9]+$ ]] && [[ "${BROKEN_COUNT:-0}" -gt 0 ]]; then
    alert "⚠️ $BROKEN_COUNT broken symlinks — see logs/symlink_audit.txt"
  fi
fi

# ── A1: Regen index ───────────────────────────────────────────────────────────
if $NEED_INDEX; then
  log "regenerating nina_index…"
  IDX="$REPO_ROOT/tools/update_index.py"
  [[ ! -f "$IDX" ]] && IDX="$REPO_ROOT/update_index.py"
  if [[ -f "$IDX" ]]; then
    PY "$IDX" >> "$LOG" 2>&1 && log "index updated" || log "index regen non-fatal error (continuing)"
  else
    log "update_index.py not found — skipping"
  fi
fi

# ── A1.5: Semantic AST index ──────────────────────────────────────────────────
if $NEED_SEMANTIC_INDEX; then
  log "semantic AST index…"
  SSOT_TOOL="$REPO_ROOT/tools/ssot_registry.py"
  if [[ -f "$SSOT_TOOL" ]]; then
    PY "$SSOT_TOOL" semantic >> "$LOG" 2>&1 \
      && log "semantic index updated" \
      || log "semantic index non-fatal error (continuing)"
  else
    log "ssot_registry.py not found — skipping semantic index"
  fi
fi

# ── A2: Doc freshness audit ───────────────────────────────────────────────────
if $NEED_DOC_AUDIT; then
  log "doc freshness audit…"
  STALE_THRESHOLD_DAYS=30
  STALE_REPORT="$REPO_ROOT/docs/space/nina_repo_hygiene_dashboard.md"
  TMP_STALE=$(mktemp)
  {
    echo "# Nina Repo Hygiene Dashboard"
    echo "_auto-generated by nina_sync.sh v10.5 OODA loop — $(TS)_"
    echo ""
    echo "## Sync State"
    echo "- State: $SYNC_STATE"
    echo "- SHA before: $LAST_SYNC_SHA"
    echo "- SHA after:  $NEW_SHA"
    echo "- Changed files: $CHANGED_COUNT"
    echo "- FS files discovered: $FS_COUNT"
    echo ""
    echo "## Open PRs"
    echo "$OPEN_PRS open PR(s)"
    echo ""
    echo "## Stale Docs (>$STALE_THRESHOLD_DAYS days unchanged)"
    find "$REPO_ROOT/docs" -name '*.md' -mtime +$STALE_THRESHOLD_DAYS 2>/dev/null \
      | sed "s|$REPO_ROOT/||" | sort \
      | while read -r f; do
          age=$(( ( $(date +%s) - $(stat -c%Y "$REPO_ROOT/$f" 2>/dev/null || echo 0) ) / 86400 ))
          echo "- $f (${age}d)"
        done || echo "_none_"
    echo ""
    echo "## Symlink Status"
    BROKEN=$(grep -c 'BROKEN:' "$REPO_ROOT/logs/symlink_audit.txt" 2>/dev/null || echo 0)
    echo "- Broken symlinks: $BROKEN"
    echo ""
    echo "## Large Files (>500KB)"
    find "$REPO_ROOT" -not -path '*/.git/*' -not -path '*/venv/*' -size +500k 2>/dev/null \
      | sed "s|$REPO_ROOT/||" | sort || echo "_none_"
    echo ""
    echo "## Registry Status"
    if [[ -f "$REGISTRY" ]]; then
      REG_COUNT=$("$REPO_ROOT/venv/bin/python3" -c "import json,sys;d=json.load(open(sys.argv[1]));print(len(d.get('files',[])))\" -- \"$REGISTRY" 2>/dev/null || echo "?")
      echo "- Registered files: $REG_COUNT"
      echo "- FS files: $FS_COUNT"
      ORPHAN_COUNT=$(PY "$REPO_ROOT/tools/ssot_registry.py" orphan_count 2>/dev/null || echo "?")
      echo "- Orphan files (not in registry): $ORPHAN_COUNT"
    else
      echo "- Registry not found — run ssot_registry.py init"
    fi
  } > "$TMP_STALE"
  RESULT=$(write_if_changed "$STALE_REPORT" "$TMP_STALE")
  log "hygiene dashboard $RESULT"
fi

# ── A2.5: Registry orphan check ──────────────────────────────────────────────
if $NEED_REGISTRY_SYNC; then
  log "registry orphan check…"
  SSOT_TOOL="$REPO_ROOT/tools/ssot_registry.py"
  if [[ -f "$SSOT_TOOL" ]]; then
    ORPHAN_OUT=$(PY "$SSOT_TOOL" sync "$FS_SNAPSHOT" 2>&1) || true
    ORPHAN_COUNT=$(printf "%s\n" "$ORPHAN_OUT" | grep -c 'ORPHAN:' 2>/dev/null || true)
    ORPHAN_COUNT=${ORPHAN_COUNT:-0}
    log "registry sync: $ORPHAN_COUNT orphan files found"
    if [[ "${ORPHAN_COUNT:-0}" =~ ^[0-9]+$ ]] && [[ "${ORPHAN_COUNT:-0}" -gt 0 ]]; then
      alert "⚠️ $ORPHAN_COUNT files not in SSOT registry (undiscoverable orphans)"
      echo "$ORPHAN_OUT" > "$REPO_ROOT/logs/registry_orphans.txt"
    fi
  else
    log "ssot_registry.py not found — skipping registry check"
  fi
  rm -f "$FS_SNAPSHOT"
fi

# ── A3: Dead-code scan (vulture + whitelist, exclude archives/backups) ────────
if $NEED_DEAD_CODE; then
  log "dead-code scan (vulture)…"
  DEAD_OUT="$REPO_ROOT/logs/dead_code_report.txt"
  if PY -m vulture --version > /dev/null 2>&1; then
    TMP_DEAD=$(mktemp)
    PY -m vulture "$REPO_ROOT" "$REPO_ROOT/vulture_whitelist.py" \
      --exclude '.git,venv,__pycache__,node_modules,logs,upgrades/backups,archive,backups' \
      --min-confidence 80 > "$TMP_DEAD" 2>&1 || true
    DEAD_COUNT=$(wc -l < "$TMP_DEAD" | tr -d ' ')
    RESULT=$(write_if_changed "$DEAD_OUT" "$TMP_DEAD")
    log "dead-code items: $DEAD_COUNT ($RESULT)"
    [[ "$DEAD_COUNT" -gt 50 ]] && alert "⚠️ $DEAD_COUNT dead-code items — review logs/dead_code_report.txt"
  else
    log "vulture not found in venv — run: venv/bin/pip install vulture"
  fi
fi

# ── A3.5: INTJ/INTM drift check ──────────────────────────────────────────────
if $NEED_INTJM_CHECK; then
  log "INTJ/INTM drift check…"
  SSOT_TOOL="$REPO_ROOT/tools/ssot_registry.py"
  if [[ -f "$SSOT_TOOL" ]]; then
    DRIFT_OUT=$(PY "$SSOT_TOOL" drift 2>&1) || true
    DRIFT_COUNT=$(printf "%s\n" "$DRIFT_OUT" | grep -c 'DRIFT:' 2>/dev/null || true)
    DRIFT_COUNT=${DRIFT_COUNT:-0}
    log "INTJ/INTM drift: $DRIFT_COUNT mirrors out of sync"
    if [[ "${DRIFT_COUNT:-0}" =~ ^[0-9]+$ ]] && [[ "${DRIFT_COUNT:-0}" -gt 0 ]]; then
      alert "⚠️ $DRIFT_COUNT INTM mirrors drifted from INTJ source — check logs/intjm_drift.txt"
      echo "$DRIFT_OUT" > "$REPO_ROOT/logs/intjm_drift.txt"
    fi
  else
    log "ssot_registry.py not found — skipping INTJ/INTM check"
  fi
fi

# ── A4: Duplicate scan ────────────────────────────────────────────────────────
if $NEED_DUP_CHECK; then
  log "duplicate file scan (hash + semantic)…"
  DUP_OUT="$REPO_ROOT/logs/duplicate_files.txt"
  TMP_DUP=$(mktemp)
  {
    echo "# Duplicate File Report — $(TS)"
    echo ""
    echo "## Exact duplicates (md5)"
    find "$REPO_ROOT" \
      -not -path '*/.git/*' -not -path '*/venv/*' -not -path '*/.venv/*' \
      -not -path '*/.aider*' -not -path '*/.mypy_cache/*' -not -path '*/.pytest_cache/*' \
      -not -path '*/__pycache__/*' -not -path '*/logs/*' -not -path '*/.cache/*' \
      -not -name '*.pyc' -not -name 'nina_index.json' -not -name 'nina_index.md' -not -name '*.log' \
      -type f -exec md5sum {} \; 2>/dev/null \
      | sort | awk 'BEGIN{h=""} h==$1{print $2} {h=$1}' \
      | sed "s|$REPO_ROOT/||" || true
    echo ""
    echo "## Semantic duplicates (.py files with identical AST structure)"
    SSOT_TOOL="$REPO_ROOT/tools/ssot_registry.py"
    if [[ -f "$SSOT_TOOL" ]]; then
      PY "$SSOT_TOOL" semantic_dup 2>/dev/null || echo "(skipped — ssot_registry.py error)"
    else
      echo "(ssot_registry.py not found)"
    fi
  } > "$TMP_DUP"
  RESULT=$(write_if_changed "$DUP_OUT" "$TMP_DUP")
  log "duplicate scan: done ($RESULT)"
  EXACT_DUPS=$(grep -v '^#\|^$\|^##' "$DUP_OUT" 2>/dev/null | wc -l | tr -d ' ' || echo 0)
  [[ "$EXACT_DUPS" -gt 5 ]] && alert "⚠️ $EXACT_DUPS exact duplicate files — review logs/duplicate_files.txt"
fi

# ── A5: Redundancy update ─────────────────────────────────────────────────────
if $NEED_REDUNDANCY; then
  log "redundancy check…"
  SSOT_TOOL="$REPO_ROOT/tools/ssot_registry.py"
  if [[ -f "$SSOT_TOOL" ]]; then
    PY "$SSOT_TOOL" redundancy >> "$LOG" 2>&1 \
      && log "redundancy check done" \
      || log "redundancy check non-fatal error"
  else
    log "ssot_registry.py not found — skipping redundancy"
  fi
fi

# ── A5.5: Backup (inline, stamp-gated 6h) ────────────────────────────────────
if $NEED_BACKUP; then
  log "backup check (stamp-guard 6h)…"
  BACKUP_DIR="$REPO_ROOT/backups"
  mkdir -p "$BACKUP_DIR"
  STAMP_FILE="$BACKUP_DIR/.last_backup_ts"
  NOW_TS=$(date +%s)
  LAST_TS=$(cat "$STAMP_FILE" 2>/dev/null || echo 0)
  AGE_SECS=$(( NOW_TS - LAST_TS ))
  if [[ "$AGE_SECS" -lt 21600 ]]; then
    log "backup skipped (last run ${AGE_SECS}s ago — within 6h window)"
  else
    echo "$NOW_TS" > "$STAMP_FILE"
    CLAUDE_FEED_OUT="$BACKUP_DIR/claude_feed_$(date +%Y%m%d).md"
    TMP_CF=$(mktemp)
    {
      echo "# NINA Claude Feed — $(TS)"
      echo ""
      for f in docs/space/nina_error_register.md \
                docs/space/jules_backlog.md \
                docs/space/nina_runbook.md \
                ARCHITECTURE.md; do
        [[ -f "$REPO_ROOT/$f" ]] && {
          echo "## $f"
          cat "$REPO_ROOT/$f"
          echo ""
        }
      done
    } > "$TMP_CF"
    CF_RESULT=$(write_if_changed "$CLAUDE_FEED_OUT" "$TMP_CF")
    MANIFEST_OUT="$BACKUP_DIR/repo_manifest_$(date +%Y%m%d).txt"
    TMP_MF=$(mktemp)
    {
      echo "# NINA Repo Manifest — $(TS)"
      find "$REPO_ROOT" \
        -not -path '*/.git/*' -not -path '*/venv/*' \
        -not -path '*/.venv/*' -not -path '*/__pycache__/*' \
        -not -path '*/logs/*' -not -path '*/backups/*' \
        -not -name '*.pyc' -not -name '*.log' \
        -type f | sort | xargs -I{} du -sh {} 2>/dev/null \
        | sed "s|$REPO_ROOT/||"
    } > "$TMP_MF"
    MF_RESULT=$(write_if_changed "$MANIFEST_OUT" "$TMP_MF")
    log "✅ backup complete (feed=$CF_RESULT manifest=$MF_RESULT)"
  fi
fi

# ── A6: Stage + commit all artefacts ─────────────────────────────────────────
if [[ "$MODE" != "pull-only" && "$MODE" != "audit" && "$MODE" != "post-push" ]]; then
  log "staging artefacts…"
  git add -A
  if ! git diff --cached --quiet; then
    git commit --no-verify -m "chore(auto): OODA sync $(TS) [skip ci]" >> "$LOG" 2>&1
    log "artefacts committed"
  else
    log "nothing to commit"
  fi
fi

# ── A7: PR resolver → reconcile → Push ───────────────────────────────────────
# Architecture (v10.5):
#   resolver  = GitHub-side surgeon (PRs, branches, merges, closes)
#   nina_sync = git transport owner (fetch, rebase, push)
#
# After resolver exits (whether it merged, updated-branch, or skipped):
#   1. re-fetch origin/main — resolver may have changed the remote HEAD
#   2. rebase local commits on top of whatever resolver did
#   3. push — local artefacts (A6 commit) are now safely on top
# This ensures local never stays permanently ahead of a changed origin.
if [[ "$MODE" != "pull-only" && "$MODE" != "audit" && "$MODE" != "post-push" ]]; then
  if [[ "$OPEN_PRS" -gt 0 ]]; then
    log "open PRs detected ($OPEN_PRS) — running PR resolver…"
    PR_RESOLVER="$REPO_ROOT/scripts/nina_pr_resolver.py"
    if [[ -f "$PR_RESOLVER" ]]; then
      PY "$PR_RESOLVER" >> "$LOG" 2>&1 \
        && log "PR resolver complete" \
        || { alert "⚠️ PR resolver error — manual check needed"; log "PR resolver failed"; }

      # ── Post-resolver reconcile (THE FIX v10.5) ──────────────────────────
      # Re-sync local with whatever resolver did on GitHub origin
      log "post-resolver reconcile: fetching origin/main…"
      git fetch origin main --quiet 2>/dev/null || true
      LOCAL_POST=$(git rev-parse HEAD 2>/dev/null)
      REMOTE_POST=$(git rev-parse origin/main 2>/dev/null)
      if [[ "$LOCAL_POST" != "$REMOTE_POST" ]]; then
        git rebase origin/main >> "$LOG" 2>&1 \
          || { git rebase --abort 2>/dev/null || true; log "post-resolver rebase failed — will retry next cycle"; }
        log "rebased local commits onto origin/main post-resolver"
      else
        log "post-resolver: local already at origin/main — no rebase needed"
      fi

      # Push local artefacts (A6 commit + any post-rebase commits)
      PUSH_OK=false
      for attempt in 1 2; do
        if git push --no-verify origin main >> "$LOG" 2>&1; then
          PUSH_OK=true; break
        else
          log "post-resolver push attempt $attempt failed — refetching"
          git fetch origin main --quiet 2>/dev/null || true
          git rebase origin/main >> "$LOG" 2>&1 || git rebase --abort 2>/dev/null || true
          sleep 2
        fi
      done
      $PUSH_OK \
        && log "✅ pushed after PR resolution" \
        || { alert "⚠️ post-resolver push failed — manual check needed"; log "post-resolver push failed"; }
    else
      log "nina_pr_resolver.py not found — falling back to skip"
      alert "ℹ️ nina_sync skipped push — $OPEN_PRS open PR(s) pending review"
    fi
  else
    PUSH_OK=false
    for attempt in 1 2; do
      if git push --no-verify origin main >> "$LOG" 2>&1; then
        PUSH_OK=true; break
      else
        log "push attempt $attempt failed — pulling and retrying"
        git fetch origin main --quiet 2>/dev/null || true
        git rebase origin/main >> "$LOG" 2>&1 || git rebase --abort 2>/dev/null || true
        sleep 2
      fi
    done
    $PUSH_OK && log "pushed to origin/main" || { alert "❌ push failed — manual fix needed"; log "push failed"; }
  fi
fi

# ── A8: Service health ────────────────────────────────────────────────────────
if $NEED_SERVICE_RESTART; then
  log "restarting nina.service…"
  systemctl --user restart nina.service >> "$LOG" 2>&1 \
    && log "nina.service restarted" \
    || { alert "⚠️ nina.service restart failed"; log "service restart failed"; }
else
  systemctl --user is-active nina.service > /dev/null 2>&1 \
    && log "nina.service: active" \
    || { log "nina.service: inactive — restarting"; systemctl --user restart nina.service >> "$LOG" 2>&1 || true; }
fi

# =============================================================================
# DONE — snake eats itself, ready for next trigger 🐍
# =============================================================================
log "✅ OODA loop complete | mode=$MODE | state=$SYNC_STATE | open_prs=$OPEN_PRS | sha=$NEW_SHA"
alert "✅ nina_sync v10.5 done (mode=$MODE, state=$SYNC_STATE)"
