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

# --- Guardian pre-task snapshot ---
GUARDIAN_PRE=""
if [[ -f ~/nina/guardian_engine.py ]]; then
  GUARDIAN_PRE=$(cd ~/nina && python3 guardian_engine.py --snapshot 2>/dev/null || echo "guardian_unavailable")
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

# --- Auto-inject codemap rows for target file ---
CODEMAP_BLOCK=""
if [[ -f ~/nina/nina_codemap.md ]]; then
  # Extract the section for this file from the codemap
  BASENAME=$(basename "$FILE")
  CODEMAP_BLOCK=$(awk "/### $BASENAME/,/^###/{if (/^###/ && !/### $BASENAME/) exit; print}" ~/nina/nina_codemap.md 2>/dev/null | head -30 || true)
  if [[ -z "$CODEMAP_BLOCK" ]]; then
    # fallback: grep for any line mentioning the file
    CODEMAP_BLOCK=$(grep -i "$BASENAME" ~/nina/nina_codemap.md | head -10 || true)
  fi
fi

# --- Optional: inject relevant context via AST function extraction ---
CONTEXT_BLOCK=""
if [[ "$INJECT_CTX" == true && -f "$FILE" ]]; then
  # Try AST-based function extraction first
  KEYWORD=$(echo "$TASK" | grep -oP '(?<=fix |add |update |change |rename |remove |refactor |in |for )[a-zA-Z_]+' | head -1 || true)
  if [[ -n "$KEYWORD" && "$FILE" == *.py ]]; then
    # Use Python AST to extract the exact function body containing the keyword
    CONTEXT_BLOCK=$(python3 - <<PYEOF 2>/dev/null || true
import ast, sys
target = "$KEYWORD"
path = "$FILE"
try:
    src = open(path).read()
    lines = src.splitlines()
    tree = ast.parse(src)
    best = None
    best_score = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fname = node.name.lower()
            # score: exact match > contains keyword > keyword in body
            body_src = '\n'.join(lines[node.lineno-1:node.end_lineno])
            score = 0
            if fname == target.lower(): score = 100
            elif target.lower() in fname: score = 50
            elif target.lower() in body_src.lower(): score = 10
            if score > best_score:
                best_score = score
                best = node
    if best:
        start = best.lineno - 1
        end = min(best.end_lineno, start + 60)
        print(f'# AST-extracted: {best.name}() lines {best.lineno}-{best.end_lineno}')
        print('\n'.join(lines[start:end]))
except Exception as e:
    pass
PYEOF
    )
  fi
  # Fallback to keyword grep window if AST found nothing
  if [[ -z "$CONTEXT_BLOCK" && -n "${KEYWORD:-}" ]]; then
    MATCH=$(grep -n "$KEYWORD" "$FILE" | head -1 | cut -d: -f1 || true)
    if [[ -n "$MATCH" ]]; then
      START=$(( MATCH > 5 ? MATCH - 5 : 1 ))
      CONTEXT_BLOCK=$(awk "NR>=$START && NR<=$((START+35))" "$FILE" | head -40)
    fi
  fi
  # Final fallback: first 40 lines
  if [[ -z "$CONTEXT_BLOCK" ]]; then
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
Post-task verify: run \`python3 -m py_compile $FILE\` + \`pyflakes $FILE\` + \`python3 agy_impact_check.py $FILE\` — confirm zero errors before committing.
Commit format: fix(scope): description ($TASK_ID)

PROMPT

if [[ -n "$CODEMAP_BLOCK" ]]; then
  echo "--- Codemap: $FILE ---"
  echo "$CODEMAP_BLOCK"
  echo "--- End codemap ---"
  echo ""
fi

if [[ -n "$CONTEXT_BLOCK" ]]; then
  echo "--- Relevant context from $FILE ---"
  echo "$CONTEXT_BLOCK"
  echo "--- End context ---"
  echo ""
fi

echo "✅ Pre-flight passed. Copy the prompt above into agy."
echo "   After task completes, run: ./agy_verify.sh $FILE"

# --- Store guardian pre-snapshot for post-verify comparison ---
if [[ -n "$GUARDIAN_PRE" && "$GUARDIAN_PRE" != "guardian_unavailable" ]]; then
  echo "$GUARDIAN_PRE" > /tmp/nina_guardian_pre_"$TASK_ID".snap
  echo "   Guardian snapshot saved → /tmp/nina_guardian_pre_${TASK_ID}.snap"
fi
