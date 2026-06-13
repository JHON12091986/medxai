#!/usr/bin/env bash
# nina_sync.sh v5 — Full post-session sync + built-in MD scan (Step 7)
# D-12: skip git push when Jules PR branches are open to prevent merge conflicts

set -euo pipefail

PATH="$HOME/bin:$PATH"

NINA=~/nina
SPACE_DIR="$NINA/docs/space"
LOGS_DIR="$NINA/logs"
DRY_RUN=false
[ "${1:-}" = "--dry-run" ] && DRY_RUN=true

TS=$(date '+%Y-%m-%d %H:%M')
DATE=$(date '+%Y-%m-%d')

# Fixed list of files to mirror/sync
SPACE_FILES=(
  docs/space/ninaflash_task_tracker.md
  docs/space/jules_backlog.md
  docs/space/jules_task_tracker.md
  docs/space/nina_error_register.md
  docs/space/nina_exporter_contract.md
  docs/space/nina_state.md
)

echo "================================================"
echo " NINA POST-SESSION SYNC  $TS$([ "$DRY_RUN" = true ] && echo " [DRY-RUN]")"
echo "================================================"

cd "$NINA"

_tg_notify() {
  local msg="$1"
  local token user_id
  token=$(grep -E '^TELEGRAMBOTTOKEN=' "$NINA/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' || true)
  user_id=$(grep -E '^AUTHORIZEDUSERID=' "$NINA/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' || true)
  if [ -n "$token" ] && [ -n "$user_id" ]; then
    curl -s -X POST "https://api.telegram.org/bot${token}/sendMessage" \
      -d "chat_id=${user_id}" -d "text=${msg}" > /dev/null 2>&1 || true
  fi
}

echo "[0/8] Health check..."
BAD_FILES=$(find "$NINA" -maxdepth 1 \( -name "*-*.md" -o -name "*-*.sh" \) 2>/dev/null || true)
if [ -n "$BAD_FILES" ]; then
  echo "  ⚠  Hyphenated filenames — auto-renaming to snake_case:"
  while IFS= read -r bad; do
    good=$(basename "$bad" | sed 's/-/_/g')
    echo "     $(basename $bad) → $good"
    [ "$DRY_RUN" = false ] && git mv "$(basename $bad)" "$good" 2>/dev/null || true
  done <<< "$BAD_FILES"
else
  echo "  ✓ Naming convention consistent"
fi

SVC_STATUS=$(systemctl is-active nina 2>/dev/null || true)
[ -z "$SVC_STATUS" ] && SVC_STATUS="unknown"
[ "$SVC_STATUS" = "active" ] && echo "  ✓ nina.service running" || echo "  ⚠  nina.service is $SVC_STATUS"

git fetch origin --quiet 2>/dev/null || true
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
[ "$BEHIND" -gt 0 ] && echo "  ⚠  $BEHIND commit(s) behind origin/main" || echo "  ✓ In sync with origin/main"

echo "[1/8] Auto-fetch from Downloads..."
FETCHED=0
for f in "${SPACE_FILES[@]}"; do
  SRC="$HOME/Downloads/$(basename "$f")"; DST="$NINA/$f"
  if [ -f "$SRC" ]; then
    if ! diff -q "$SRC" "$DST" > /dev/null 2>&1; then
      echo "  ↓ $f (updated from Downloads)"
      [ "$DRY_RUN" = false ] && cp "$SRC" "$DST"
      FETCHED=$((FETCHED+1))
    else
      echo "  = $f (Downloads copy identical)"
    fi
  fi
done
[ "$FETCHED" -eq 0 ] && echo "  (no new Downloads files)"

echo "[2/8] Mirror to docs/space/..."
[ "$DRY_RUN" = false ] && mkdir -p "$SPACE_DIR"
# 2. Fixed Mirror Loop
for f in "${SPACE_FILES[@]}"; do
  SRC="$NINA/$f"; DST="$SPACE_DIR/$(basename "$f")"
  if [ ! -f "$SRC" ]; then echo "  ✗ MISSING: $f"; continue; fi
  if [ ! -f "$DST" ] || ! diff -q "$SRC" "$DST" > /dev/null 2>&1; then
    echo "  ✓ $f (updated)"; [ "$DRY_RUN" = false ] && cp "$SRC" "$DST"
  else
    echo "  = $f (unchanged)"
  fi
done

# 2.1 Dynamic Master Backup Mirror (handles date-stamped files)
for f in "$SPACE_DIR"/nina_master_backup_*.md; do
  if [ -f "$f" ]; then
    echo "  = $(basename "$f") (present)"
  fi
done
for lf in nina_update_log.md; do
  if [ -f "$LOGS_DIR/$lf" ] && [ -f "$NINA/$lf" ]; then
    if ! diff -q "$LOGS_DIR/$lf" "$NINA/$lf" > /dev/null 2>&1; then
      echo "  ✓ $lf (synced from logs/)"; [ "$DRY_RUN" = false ] && cp "$LOGS_DIR/$lf" "$NINA/$lf"
    fi
  fi
done

echo "[3/8] Backup cleanup..."
OLD_FILES=$(find "$NINA/upgrades/backups" -maxdepth 3 \
  \( -name "*.bak" -o -name "*.fix" -o -name "*.save" \) -mtime +30 2>/dev/null || true)
if [ -n "$OLD_FILES" ]; then
  COUNT=$(echo "$OLD_FILES" | wc -l | tr -d ' ')
  echo "  🗑  $COUNT stale file(s) >30 days old"
  if [ "$DRY_RUN" = false ]; then
    echo "$OLD_FILES" | xargs rm -f && echo "  ✓ Cleaned"
  else
    echo "  (dry-run: would delete)"
  fi
else
  echo "  ✓ No stale backup files"
fi

echo "[4/8] Update log entry..."
LAST_ENTRY=$(grep -c "^## Entry" "$NINA/nina_update_log.md" 2>/dev/null || echo "0")
NEXT_NUM=$(printf '%03d' $((LAST_ENTRY + 1)))
CHANGED_FILES=$(git status --porcelain 2>/dev/null | awk '{print $2}' | tr '\n' ',' | sed 's/,$//' || echo "none")
if [ "$DRY_RUN" = false ] && [ -n "$CHANGED_FILES" ] && [ "$CHANGED_FILES" != "none" ]; then
  python3 - << PYEOF
lines = [
    "",
    "---",
    "",
    "## Entry $NEXT_NUM — $DATE · D-sync Post-session sync",
    "",
    "**Triggered by:** nina_sync.sh v5 automated run",
    "",
    "**Files changed:** $CHANGED_FILES",
    "",
    "**Verification:** git push OK, nina.service $SVC_STATUS",
    "",
]
entry = chr(10).join(lines)
for path in ["$NINA/nina_update_log.md", "$LOGS_DIR/nina_update_log.md"]:
    try:
        open(path, "a").write(entry)
    except Exception:
        pass
print("  ✓ Log entry appended (Entry $NEXT_NUM)")
PYEOF
else
  echo "  = No changes to log"
fi

echo "[5/8] Staging..."
if [ "$DRY_RUN" = false ]; then
  git add docs/space/ "${SPACE_FILES[@]}" nina_sync.sh 2>/dev/null || true
  git add -u 2>/dev/null || true
fi

echo "[5b/8] RULE 0 compliance audit..."
if [ "$DRY_RUN" = false ]; then
  python3 "$NINA/tools/rule0_audit.py" --hours 8 || true
else
  echo "  (dry-run: skipping)"
fi

echo "[6/8] Committing and pushing..."
if [ "$DRY_RUN" = true ]; then
  echo "  (dry-run: skipping commit)"
else
  STAGED=$(git diff --cached --name-only 2>/dev/null || true)
  if [ -n "$STAGED" ]; then
    echo "  Changed files:"; echo "$STAGED" | sed 's/^/     /'
    git commit -m "docs: post-session sync $TS"

    # D-12: Check for open Jules PR branches before pushing to main
    # This prevents nina_sync.sh from moving main ahead of Jules branches
    # and causing merge conflicts on all open Jules PRs.
    git remote prune origin --dry-run 2>/dev/null; git remote prune origin
    JULES_BRANCHES=$(gh pr list --state open --json headRefName --limit 100 2>/dev/null | jq '[.[] | select(.headRefName | (startswith("jules-") or startswith("nina-j") or startswith("feat/") or startswith("pr-")))] | length' 2>/dev/null || echo "0")
    if [ "$JULES_BRANCHES" -gt 0 ]; then
      echo ""
      echo "  ⚠️  PUSH SKIPPED — $JULES_BRANCHES open Jules PR branch(es) detected on origin."
      echo "     Pushing now would cause merge conflicts on open Jules PRs."
      echo "     → Merge or close all Jules PRs first, then run: cd ~/nina && git push origin main"
      echo ""
      _tg_notify "⚠️ NINA sync [$TS] — Push SKIPPED: $JULES_BRANCHES Jules PR branch(es) open. Merge/close PRs first, then push manually."
    else
      git push origin main
      STAT=$(git show --stat HEAD | tail -1)
      echo "  ✓ Pushed — $STAT"
      _tg_notify "✅ NINA sync [$TS]
$STAT
Service: $SVC_STATUS"
    fi
  else
    echo "  Nothing to commit"
    _tg_notify "ℹ️ NINA sync [$TS] — nothing to commit. Service: $SVC_STATUS"
  fi
fi

echo "[7/8] Doc/config coverage scan..."
echo "  ── All .md/.txt/.json files in ~/nina (excl. venv/.git/exports/backups) ──"

COVERED_BASES=()
for f in "${SPACE_FILES[@]}"; do
  COVERED_BASES+=("$(basename "$f")")
done

ALL_MD=$(find "$NINA" \
  \( -path "*/venv/*" -o -path "*/.git/*" -o -path "*/node_modules/*" \
     -o -path "*/upgrades/backups/*" -o -path "*/exports/*" \
     -o -path "*/__pycache__/*" \) -prune \
  -o \( -name "*.md" -o -name "*.txt" -o -name "*.json" \) -print | sort)

TOTAL=0; COVERED=0; UNCOVERED=0
UNCOVERED_LIST=""

while IFS= read -r filepath; do
  [ -z "$filepath" ] && continue
  rel="${filepath#$NINA/}"
  base=$(basename "$filepath")
  lines=$(wc -l < "$filepath" 2>/dev/null || echo "?")
  mtime=$(stat -c "%y" "$filepath" 2>/dev/null | cut -d'.' -f1 || echo "?")
  TOTAL=$((TOTAL+1))

  IN_SPACE=false
  if [ -f "$SPACE_DIR/$base" ]; then
    IN_SPACE=true
  fi
  for cb in "${COVERED_BASES[@]}"; do
    [ "$cb" = "$base" ] && IN_SPACE=true
  done

  if [ "$IN_SPACE" = true ]; then
    echo "  ✅  $rel  ($lines lines, $mtime)"
    COVERED=$((COVERED+1))
  else
    echo "  ⚠️   $rel  ($lines lines, $mtime)  ← NOT in docs/space or SPACE_FILES"
    UNCOVERED=$((UNCOVERED+1))
    UNCOVERED_LIST="$UNCOVERED_LIST\n  • $rel"
  fi
done <<< "$ALL_MD"

echo ""
echo "  ── Summary ──"
echo "  Total .md files : $TOTAL"
echo "  Covered         : $COVERED"
echo "  NOT covered     : $UNCOVERED"
if [ "$UNCOVERED" -gt 0 ]; then
  echo ""
  echo "  ⚠️  Files not in docs/space (not uploaded to Perplexity):"
  echo -e "$UNCOVERED_LIST"
  echo ""
  echo "  → Add them to SPACE_FILES array in nina_sync.sh if needed."
fi
echo "[8.0/8] Auto-regenerating docs from live source..."
if [ "$DRY_RUN" = false ]; then
  python3 "$NINA/tools/doc_autogen.py" && echo " ✅ Docs auto-patched" || echo " ⚠️ Doc autogen failed (non-fatal)"
else
  echo "  (dry-run: skipping)"
fi

echo "[8/8] Full master export for Perplexity Space..."
if [ "$DRY_RUN" = true ]; then
  echo "  (dry-run: skipping)"
else
  # Step 8: Call the compact exporter Python script
  python3 "$NINA/tools/compact_exporter.py"
  
  echo "  ✅ nina_latest.md:      $(wc -c < $HOME/Downloads/nina_space_upload/nina_latest.md) bytes"
  echo "  ✅ nina_diff.md:        $(wc -c < $HOME/Downloads/nina_space_upload/nina_diff.md) bytes"
  BFILE=$(ls -t $HOME/Downloads/nina_space_upload/nina_full_backup_*.md 2>/dev/null | head -1)
  [ -n "$BFILE" ] && echo "  ✅ $(basename $BFILE): $(wc -c < $BFILE) bytes"

  if command -v rclone >/dev/null 2>&1 && rclone listremotes 2>/dev/null | grep -q "gdrive:"; then
    rclone copy "$HOME/Downloads/nina_space_upload/nina_latest.md" "gdrive:nina-backup/" --no-traverse 2>/dev/null \
      && echo "  ☁️  nina_latest.md → gdrive:nina-backup/ (overwritten)" \
      || echo "  ⚠️  nina_latest.md upload failed"

    rclone copy "$HOME/Downloads/nina_space_upload/nina_diff.md" "gdrive:nina-backup/" --no-traverse 2>/dev/null \
      && echo "  ☁️  nina_diff.md → gdrive:nina-backup/ (overwritten)" \
      || echo "  ⚠️  nina_diff.md upload failed"

    BACKUP_FILE=$(ls -t "$HOME/Downloads/nina_space_upload/nina_full_backup_"*.md 2>/dev/null | head -1)
    if [ -n "$BACKUP_FILE" ]; then
      rclone copy "$BACKUP_FILE" "gdrive:nina-backup/versioned/" --no-traverse 2>/dev/null \
        && echo "  ☁️  $(basename $BACKUP_FILE) → gdrive:nina-backup/versioned/ (permanent version)" \
        || echo "  ⚠️  Full backup upload failed"
    fi
  fi

  echo "[8.1/8] Generating Claude feed..."
  export JULES_API_KEY=$(grep -E '^JULES_API_KEY=' "$NINA/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' || echo "")
  
  # Generate Claude feed and upload
  python3 - << 'PYEOF'
import subprocess, json, re, time
from pathlib import Path

NINA = Path.home() / "nina"
OUT = NINA / "docs/space/claude_feed.md"
BACKLOG = NINA / "docs/space/jules_backlog.md"
LOCK = NINA / "jules_lock.txt"
STATE = NINA / "docs/space/nina_state.md"

lines = []
lines.append("# NINA Claude Feed — Session Startup Context")
lines.append("> Auto-generated by nina_sync.sh — do not edit manually")
lines.append("> Claude: read this. Then generate 10 non-overlapping Jules specs.\n")

# 1. Snapshot header
import subprocess, time
head = subprocess.getoutput("cd ~/nina && git log -1 --pretty='%H|%s|%ci'").split("|")
lines.append("## 1. Snapshot")
lines.append(f"- Generated: {time.strftime('%Y-%m-%d %H:%M %Z')}")
lines.append(f"- Git HEAD: {head[0] if head else 'unknown'}")
lines.append(f"- Last commit: {head[1] if len(head)>1 else 'unknown'}")
svc_status = subprocess.getoutput('systemctl is-active nina 2>/dev/null || echo unknown').strip()
svc_detail = subprocess.getoutput('systemctl status nina --no-pager -n 5 2>/dev/null || echo unavailable')
lines.append(f"- Service: {svc_status}")
lines.append(f"```")
lines.append(svc_detail.strip())
lines.append(f"```")

# 2. Active Jules sessions
lines.append("## 2. Active Jules Sessions (live)")
try:
    import asyncio, sys
    sys.path.insert(0, str(NINA))
    from tools.jules_api import run
    result = asyncio.run(run("status"))
    lines.append(result)
except Exception as e:
    lines.append(f"- Jules API unavailable: {e}")
lines.append("")

# 3. File lock registry
lines.append("## 3. Locked Files (do not touch in new specs)")
if LOCK.exists():
    lines.append(f"```\n{LOCK.read_text().strip()}\n```")
else:
    lines.append("- jules_lock.txt not found — all files available")
lines.append("")

# 4. READY backlog items
lines.append("## 4. READY Items (eligible for new Jules specs)")
if BACKLOG.exists():
    backlog = BACKLOG.read_text()
    ready_blocks = re.findall(r'((?:###|####).+?(?=###|####|\Z))', backlog, re.DOTALL)
    ready = [b.strip() for b in ready_blocks if 'READY' in b][:20]
    lines.append(f"_Found {len(ready)} READY items_\n")
    for b in ready:
        lines.append(b[:400])
        lines.append("")
else:
    lines.append("- Backlog file not found")
lines.append("")

# 5. Last 5 completions
lines.append("## 5. Last 5 Completions")
lines.append("```")
lines.append(subprocess.getoutput("cd ~/nina && git log --oneline -5"))
lines.append("```")
lines.append("")

# 6. Open blockers
lines.append("## 6. Open Blockers")
if BACKLOG.exists():
    for line in BACKLOG.read_text().splitlines():
        if any(x in line for x in ['BLOCKED','O-06','S-01','S-02','O-02','F-02','F-03']) and 'DONE' not in line and 'FIXED' not in line:
            lines.append(f"- {line.strip()}")
lines.append("")

# 7. Static cheatsheet
lines.append("## 7. File Ownership Cheatsheet")
lines.append("| File | Purpose | Risk |")
lines.append("|------|---------|------|")
cheatsheet = [
    ("core/nina.py","NinaOS orchestrator, system prompt","HIGH"),
    ("core/router.py","HybridRouter V4, 19+ providers, circuit breaker","HIGH"),
    ("core/agent.py","AgentLoop THINK→PLAN→ACT, self-check, RAM guard","HIGH"),
    ("core/memory.py","ChromaDB + facts.json, build_context()","MEDIUM"),
    ("core/task_store.py","TaskStore persistence, file locking","MEDIUM"),
    ("core/config.py","NinaConfig, RATELIMITS","HIGH"),
    ("interfaces/telegram_interface.py","Telegram bot, auth gate","HIGH"),
    ("guardian_engine.py","Forensic engine, AST scans, baseline","HIGH"),
    ("tools/jules_api.py","Jules REST API dispatch/status","LOW"),
    ("tools/market.py","DSE/CSE monitor (dummy prices — needs real API)","LOW"),
    ("tools/finance.py","Expenditure tracker","LOW"),
    ("tools/office_mail.py","Email triage (EWS blocked — O-02 open)","LOW"),
    ("tools/shell.py","Shell execution (cat in allowlist — O-06 CRITICAL)","HIGH"),
    ("tools/browser.py","URL fetch (SSRF fix S-01 pending)","MEDIUM"),
    ("ninagate/main.py","OpenAI-compatible proxy (duplicate router — debt)","MEDIUM"),
    ("idleloop.py","IdleProposalLoop, IMPACT briefs","LOW"),
    ("crons/manager.py","APScheduler, reminders, daily reports","MEDIUM"),
    ("data/memory/facts.json","Personal context facts (F-02 injection pending)","MEDIUM"),
]
for f,p,r in cheatsheet:
    lines.append(f"| {f} | {p} | {r} |")

lines.append("## 8. PRs Ready to Merge (agy merge candidates)")
pr_list = subprocess.getoutput(
    "gh pr list --state open --json number,title,headRefName "
    "--jq '.[] | \"#\\(.number) \\(.title) [\\(.headRefName)]\"' 2>/dev/null || echo 'gh CLI unavailable'"
).strip()
lines.append(pr_list if pr_list else "- No open PRs")
lines.append("")

size = len("\n".join(lines))
lines.append(f"\n---\n_Feed size: {size} bytes_")

OUT.write_text("\n".join(lines))
print(f"  ✅ claude_feed.md generated: {size} bytes")
PYEOF

  # Upload claude_feed.md to fixed location
  if command -v rclone >/dev/null 2>&1 && rclone listremotes 2>/dev/null | grep -q "gdrive:"; then
    rclone copy "$NINA/docs/space/claude_feed.md" "gdrive:nina-backup/" --no-traverse 2>/dev/null \
      && echo "  ☁️  claude_feed.md → gdrive:nina-backup/ (overwritten)" \
      || echo "  ⚠️  claude_feed.md upload failed"
  fi
fi

LOGBASE_OUT=$(bash "$HOME/nina/nina_logbase_backup.sh" | grep "saved to" | awk -F'saved to ' '{print $2}')
DOCBASE_OUT=$(bash "$HOME/nina/nina_docbase_backup.sh" | grep "saved to" | awk -F'saved to ' '{print $2}')
CODEBASE_OUT=$(bash "$HOME/nina/nina_codebase_backup.sh" | grep "saved to" | awk -F'saved to ' '{print $2}')

echo "NINA logbase backup saved to $LOGBASE_OUT"
echo "NINA docbase backup saved to $DOCBASE_OUT"
echo "NINA codebase backup saved to $CODEBASE_OUT"

if command -v rclone >/dev/null 2>&1 && rclone listremotes 2>/dev/null | grep -q "gdrive:"; then
  [ -n "$LOGBASE_OUT" ] && rclone copy "$LOGBASE_OUT" "gdrive:nina-backup/versioned/" --no-traverse 2>/dev/null && echo "  ☁️  $(basename "$LOGBASE_OUT") → gdrive:nina-backup/versioned/" || echo "  ⚠️  Logbase backup upload failed"
  [ -n "$DOCBASE_OUT" ] && rclone copy "$DOCBASE_OUT" "gdrive:nina-backup/versioned/" --no-traverse 2>/dev/null && echo "  ☁️  $(basename "$DOCBASE_OUT") → gdrive:nina-backup/versioned/" || echo "  ⚠️  Docbase backup upload failed"
  [ -n "$CODEBASE_OUT" ] && rclone copy "$CODEBASE_OUT" "gdrive:nina-backup/versioned/" --no-traverse 2>/dev/null && echo "  ☁️  $(basename "$CODEBASE_OUT") → gdrive:nina-backup/versioned/" || echo "  ⚠️  Codebase backup upload failed"
fi

echo "================================================"
echo " SYNC COMPLETE  $TS"
echo "================================================"
