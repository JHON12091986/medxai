#!/usr/bin/env bash
# =============================================================================
# ngit.sh  v1.0  —  Nina pure git transport
#
# SINGLE RESPONSIBILITY: get your local commits to remote. That's it.
#
# USAGE:
#   ngit "fix: telegram handler"
#   ngit                          ← defaults to "chore: sync workspace"
#
# WHAT IT DOES:
#   1. Untrack secrets + gitignored-but-cached files
#   2. Stage all → commit
#   3. Pull (rebase preferred, merge fallback)
#   4. Push  --no-verify  (stage 1)
#   5. If pre-push hook left unpushed commits → push --no-verify  (stage 2)
#
# WHAT IT DOES NOT DO:
#   ✗  No OODA audits
#   ✗  No index regen
#   ✗  No dead-code / dedup / registry scans
#   ✗  No Telegram alerts
#   ✗  No hook firing (both pushes use --no-verify)
#
# OODA HAPPENS AUTOMATICALLY:
#   After ngit lands on remote, the post-push hook fires nina_sync.sh
#   in the background — you don't need to do anything.
#
# WHEN TO USE:
#   You edited a file, fixed a bug, added a feature → ngit "your message"
#   That's the only time you need ngit.
#
# WHEN TO USE sync INSTEAD:
#   - After pulling external changes (Jules / agy / Gemini)
#   - Want a manual health check
#   - After a service crash
#   See: scripts/nina_sync.sh
#
# ARCHITECTURE:
#   ngit  →  git push --no-verify  →  post-push hook  →  sync (OODA)
#   (transport)                        (auto)             (brain)
# =============================================================================

set -uo pipefail

NINA="${NINA_ROOT:-$HOME/nina}"
MSG="${1:-chore: sync workspace}"
mkdir -p "$NINA/runtime/logs"
LOG="$NINA/runtime/logs/ngit.log"
TS() { date '+%Y-%m-%d %H:%M:%S'; }

exec > >(tee -a "$LOG") 2>&1
cd "$NINA" || { echo "[ngit] ❌ Cannot cd to $NINA"; exit 1; }

echo ""
echo "[ngit] $(TS) 🚀 v1.0 | $MSG"

git rev-parse --git-dir &>/dev/null || { echo "[ngit] ❌ Not a git repo"; exit 1; }

# ── Ensure .push_in_flight is gitignored (idempotent) ──
grep -qxF '.push_in_flight' .gitignore 2>/dev/null || echo '.push_in_flight' >> .gitignore
rm -f .push_in_flight

# ── Network check ──────────────────────────────────────────────────────────
if ! git ls-remote --exit-code origin HEAD &>/dev/null; then
    echo "[ngit] ⚠️  No remote — committing locally only."
    git add -A -- ':!.push_in_flight'
    git diff --cached --quiet || git commit -m "$MSG [offline]"
    exit 0
fi

# ── Untrack secrets ────────────────────────────────────────────────────────
for f in .env .env.local; do
    git ls-files --error-unmatch "$f" &>/dev/null && \
        git rm --cached "$f" && echo "[ngit] ⚠️  Untracked secret: $f"
done 2>/dev/null || true

# ── Untrack gitignored-but-cached files ────────────────────────────────────
UNTRACKED=$(git ls-files -ci --exclude-standard 2>/dev/null)
if [ -n "$UNTRACKED" ]; then
    echo "[ngit] 🧹 Untracking cached+ignored:"
    echo "$UNTRACKED" | while read -r f; do
        git rm --cached "$f" 2>/dev/null && echo "    • $f" || true
    done
fi

# ── Stage + commit ─────────────────────────────────────────────────────────
git add -A -- ':!.push_in_flight'
if ! git diff --cached --quiet; then
    git commit -m "$MSG" && echo "[ngit] ✅ Committed"
else
    echo "[ngit] ℹ️  Nothing to commit"
fi

# ── Pull (rebase preferred, merge fallback) ────────────────────────────────
echo "[ngit] $(TS) ⏬ Pulling..."
if ! git pull --rebase origin main 2>&1; then
    echo "[ngit] ⚠️  Rebase failed — trying merge..."
    git rebase --abort 2>/dev/null || true
    git pull --no-rebase origin main 2>&1 || {
        echo "[ngit] ❌ Pull failed. Check: git status"
        exit 1
    }
fi

# ── Stage 1 push: --no-verify (no hooks fire) ──────────────────────────────
echo "[ngit] $(TS) ⬆️  Push stage 1 (--no-verify)..."
if ! git push --no-verify origin main 2>&1; then
    echo "[ngit] ⚠️  Push rejected — pulling and retrying..."
    git pull --rebase origin main 2>/dev/null || \
        git pull --no-rebase origin main 2>/dev/null || true
    git push --no-verify origin main 2>&1 || {
        echo "[ngit] ❌ Push failed"
        exit 1
    }
fi
echo "[ngit] ✅ Stage 1 pushed"

# ── Stage 2: push any governance-hook leftovers ────────────────────────────
# Safety net in case a hook still runs somehow and commits extra files.
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "")
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[ngit] $(TS) ⬆️  Push stage 2 (hook leftovers, --no-verify)..."
    if ! git push --no-verify origin main 2>&1; then
        git pull --rebase origin main 2>/dev/null || \
            git pull --no-rebase origin main 2>/dev/null || true
        git push --no-verify origin main 2>&1 && \
            echo "[ngit] ✅ Stage 2 pushed" || \
            echo "[ngit] ⚠️  Stage 2 failed — next ngit will sync"
    else
        echo "[ngit] ✅ Stage 2 pushed"
    fi
else
    echo "[ngit] ✅ Already in sync"
fi

echo "[ngit] $(TS) 🏁 Done. OODA running in background via post-push hook."
