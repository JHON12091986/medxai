#!/usr/bin/env bash
# agy_task.sh — fast agy prompt generator
# Usage: ./agy_task.sh <file> "<task description>" ["<do not touch>"] ["<acceptance>"] [--inject-context]
# Example: ./agy_task.sh tools/ninaflash.py "fix the rate limit logic in _handle_quota" "" "" --inject-context

set -euo pipefail

FILE="${1:-}"
TASK="${2:-}"
NOTOUCH="${3:-<none>}"
ACCEPT="${4:-file compiles clean with zero pyflakes warnings}"
INJECT_CTX=false

# Parse flags
for arg in "$@"; do
  [[ "$arg" == "--inject-context" ]] && INJECT_CTX=true
done

if [[ -z "$FILE" || -z "$TASK" ]]; then
  echo "Usage: ./agy_task.sh <file> \"<task>\" [\"<do not touch>\"] [\"<acceptance>\"] [--inject-context]"
  exit 1
fi

# --- Pre-flight checks ---
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [[ "$BRANCH" != "main" ]]; then
  echo "❌ ERROR: Not on main branch (currently: $BRANCH). Aborting."
  exit 1
fi

if grep -qF "$FILE" ~/nina/juleslock.txt 2>/dev/null; then
  echo "❌ ERROR: $FILE is locked in juleslock.txt. Aborting."
  exit 1
fi

STATUS=$(git status --porcelain 2>/dev/null)
if [[ -n "$STATUS" ]]; then
  echo "⚠️  WARNING: Working tree is not clean:"
  echo "$STATUS"
  read -rp "Continue anyway? [y/N] " CONFIRM
  [[ "$CONFIRM" =~ ^[Yy]$ ]] || exit 1
fi

# --- Generate Task ID ---
DATE=$(date +%Y%m%d)
LOGFILE=~/nina/docs/space/agy_task_counter.txt
mkdir -p ~/nina/docs/space
if [[ -f "$LOGFILE" ]]; then
  LAST=$(grep "^${DATE}-" "$LOGFILE" 2>/dev/null | tail -1 | grep -oP '\d{3}$' || echo "000")
  NNN=$(printf "%03d" $(( 10#$LAST + 1 )))
else
  NNN="001"
fi
TASK_ID="nina-${DATE}-${NNN}"
echo "${DATE}-${NNN}" >> "$LOGFILE"

# --- Optional: inject relevant context from file ---
CONTEXT_BLOCK=""
if [[ "$INJECT_CTX" == true && -f "$FILE" ]]; then
  # Extract keyword from task (first meaningful word after common verbs)
  KEYWORD=$(echo "$TASK" | grep -oP '(?<=fix |add |update |change |rename |remove |refactor )[a-zA-Z_]+' | head -1 || true)
  if [[ -n "$KEYWORD" ]]; then
    MATCH=$(grep -n "$KEYWORD" "$FILE" | head -1 | cut -d: -f1 || true)
    if [[ -n "$MATCH" ]]; then
      START=$(( MATCH > 5 ? MATCH - 5 : 1 ))
      CONTEXT_BLOCK=$(awk "NR>=$START && NR<=$((START+35))" "$FILE" | head -40)
    fi
  fi
  if [[ -z "$CONTEXT_BLOCK" ]]; then
    # Fall back: first 40 lines
    CONTEXT_BLOCK=$(head -40 "$FILE")
  fi
fi

# --- Output prompt ---
cat <<PROMPT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TASK ID : $TASK_ID
 FILE    : $FILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Permanent approval mode active — all steps pre-approved, no confirmation needed.

File: $FILE
Do NOT touch: $NOTOUCH
Task: $TASK
Acceptance: $ACCEPT
Post-task verify: run \`python3 -m py_compile $FILE\` + \`pyflakes $FILE\` — confirm zero errors before committing.
Commit format: fix(scope): description ($TASK_ID)

PROMPT

if [[ -n "$CONTEXT_BLOCK" ]]; then
  echo "--- Relevant context from $FILE ---"
  echo "$CONTEXT_BLOCK"
  echo "--- End context ---"
  echo ""
fi

echo "✅ Pre-flight passed. Copy the prompt above into agy."
echo "   After task completes, run: ./agy_verify.sh $FILE"
