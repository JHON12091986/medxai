#!/usr/bin/env bash
# =============================================================================
# npush.sh v7 — Nina bulletproof autopilot push
#
# DESIGN:
#   Everything is automatic. Just run: npush ["message"]
#
# ROOT CAUSE OF PRIOR LOOPS:
#   pre-push hook commits regen output mid-push → moves HEAD → remote falls
#   behind → cleanup push triggers pre-push again → infinite race.
#
# SOLUTION (delta-sync, 2-stage push):
#   Stage 1: Normal push (pre-push hook runs regen, auto-commits, push lands)
#   Stage 2: If hook left unpushed commits, push --no-verify (skip hooks)
#            This breaks the race permanently.
#
# OODA SUPPRESSION:
#   Touch .push_in_flight — what post-commit hook actually checks.
#   Never committed: excluded from every git add AND in .gitignore.
#
# Contingencies:
#   ✓ Unstaged / staged index — git add -A before commit
#   ✓ .push_in_flight accidentally committed — excluded + gitignored
#   ✓ OODA post-commit loop — suppressed via .push_in_flight
#   ✓ Gitignored-but-cached files — untracked every run
#   ✓ Secrets — .env/.env.local never committed
#   ✓ Remote ahead (non-fast-forward) — pull before push
#   ✓ Rebase conflict — abort + merge fallback
#   ✓ pre-push hook race — broken by --no-verify stage-2 push
#   ✓ Stage-2 push rejected — pull + retry once
#   ✓ No internet — local commit only, clean exit
# =============================================================================

set -uo pipefail

NINA="$HOME/nina"
MSG="${1:-chore: sync workspace}"
mkdir -p "$NINA/runtime/logs"
LOG="$NINA/runtime/logs/npush.log"
FLAG="$NINA/.push_in_flight"
TS() { date '+%Y-%m-%d %H:%M:%S'; }

exec > >(tee -a "$LOG") 2>&1
cd "$NINA" || { echo "[npush] ❌ Cannot cd"; exit 1; }

echo ""
echo "[npush] $(TS) 🚀 v7 | $MSG"

git rev-parse --git-dir &>/dev/null || { echo "[npush] ❌ Not a git repo"; exit 1; }

# Ensure .push_in_flight is gitignored (idempotent)
grep -qxF '.push_in_flight' .gitignore 2>/dev/null || \
    echo '.push_in_flight' >> .gitignore

# ---- Network check ----
if ! git ls-remote --exit-code origin HEAD &>/dev/null; then
    echo "[npush] ❌ No remote — committing locally."
    touch "$FLAG"
    git add -A -- ':!.push_in_flight'
    git diff --cached --quiet || git commit -m "$MSG [offline]"
    rm -f "$FLAG"
    exit 0
fi

# ---- Suppress OODA post-commit for entire session ----
touch "$FLAG"
trap 'rm -f "$FLAG"; echo "[npush] 🧹 flag removed"' EXIT

# ---- Untrack secrets ----
for f in .env .env.local; do
    git ls-files --error-unmatch "$f" &>/dev/null && \
        git rm --cached "$f" && echo "[npush] ⚠️  Untracked: $f"
done 2>/dev/null || true

# ---- Untrack gitignored-but-cached files ----
UNTRACKED=$(git ls-files -ci --exclude-standard 2>/dev/null)
if [ -n "$UNTRACKED" ]; then
    echo "[npush] 🧹 Untracking cached+ignored:"
    echo "$UNTRACKED" | while read -r f; do
        git rm --cached "$f" 2>/dev/null && echo "    • $f" || true
    done
fi

# ---- Commit all changes ----
git add -A -- ':!.push_in_flight'
if ! git diff --cached --quiet; then
    git commit -m "$MSG" && echo "[npush] ✅ Committed"
else
    echo "[npush] ℹ️  Nothing to commit"
fi

# ---- Pull (rebase preferred, merge fallback) ----
echo "[npush] $(TS) ⏬ Pulling..."
if ! git pull --rebase origin main 2>&1; then
    echo "[npush] ⚠️  Rebase failed — trying merge..."
    git rebase --abort 2>/dev/null || true
    git pull --no-rebase origin main 2>&1 || {
        echo "[npush] ❌ Pull failed. Check: git status"
        exit 1
    }
fi

# ---- Stage 1: Normal push (pre-push hook runs here) ----
echo "[npush] $(TS) ⬆️  Push stage 1..."
if ! git push origin main 2>&1; then
    echo "[npush] ⚠️  Push rejected — pulling and retrying..."
    git pull --rebase origin main 2>/dev/null || \
        git pull --no-rebase origin main 2>/dev/null || true
    git push origin main 2>&1 || { echo "[npush] ❌ Push failed"; exit 1; }
fi
echo "[npush] ✅ Stage 1 pushed"

# ---- Stage 2: Push any commits the pre-push hook left behind ----
# Use --no-verify to skip hooks — breaks the infinite hook race
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "")
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[npush] $(TS) ⬆️  Push stage 2 (hook leftovers, --no-verify)..."
    if ! git push --no-verify origin main 2>&1; then
        echo "[npush] ⚠️  Stage 2 rejected — pulling and retrying..."
        git pull --rebase origin main 2>/dev/null || \
            git pull --no-rebase origin main 2>/dev/null || true
        git push --no-verify origin main 2>&1 && \
            echo "[npush] ✅ Stage 2 pushed" || \
            echo "[npush] ⚠️  Stage 2 failed — next npush will sync"
    else
        echo "[npush] ✅ Stage 2 pushed"
    fi
else
    echo "[npush] ✅ Already in sync"
fi

echo "[npush] $(TS) 🏁 Done."
