#!/usr/bin/env bash
# agy_task.sh — fast agy prompt generator (Codex-inspired: tiered load + scope sandbox + self-diff loop)
# Usage: ./agy_task.sh <file> "<task>" ["<do not touch>"] ["<acceptance>"] [--inject-context] [--multifile]
# Example: ./agy_task.sh tools/ninaflash.py "fix the rate limit logic in _handle_quota" "" "" --inject-context

set -euo pipefail

PYTHON="python3"
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
elif [ -f "ninavenv/bin/python" ]; then
    PYTHON="ninavenv/bin/python"
fi

FILE="${1:-}"
TASK="${2:-}"
NOTOUCH="${3:-<none>}"
ACCEPT="${4:-file compiles clean with zero pyflakes warnings}"
INJECT_CTX=false
MULTIFILE=false

for arg in "$@"; do
  [[ "$arg" == "--inject-context" ]] && INJECT_CTX=true
  [[ "$arg" == "--multifile" ]]     && MULTIFILE=true
done

if [[ -z "$FILE" || -z "$TASK" ]]; then
  echo "Usage: ./scripts/agy_task.sh <file> \"<task>\" [\"<do not touch>\"] [\"<acceptance>\"] [--inject-context] [--multifile]"
  exit 1
fi

# --- Pre-flight checks ---
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
if [[ "$BRANCH" != "main" ]]; then
  echo "\u274c ERROR: Not on main branch (currently: $BRANCH). Aborting."
  exit 1
fi

if grep -qF "$FILE" ~/nina/juleslock.txt 2>/dev/null; then
  echo "\u274c ERROR: $FILE is locked in juleslock.txt. Aborting."
  exit 1
fi

STATUS=$(git status --porcelain 2>/dev/null)
if [[ -n "$STATUS" ]]; then
  echo "\u26a0\ufe0f  WARNING: Working tree is not clean:"
  echo "$STATUS"
  read -rp "Continue anyway? [y/N] " CONFIRM
  [[ "$CONFIRM" =~ ^[Yy]$ ]] || exit 1
fi

# --- Guardian pre-task snapshot ---
GUARDIAN_PRE=""
if [[ -f ~/nina/guardian_engine.py ]]; then
  GUARDIAN_PRE=$(cd ~/nina && "$PYTHON" guardian_engine.py --snapshot 2>/dev/null || echo "guardian_unavailable")
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

# --- Determine prompt tier ---
CORE=$(cat ~/nina/agy_prompt_core.md 2>/dev/null || echo "[agy_prompt_core.md not found]")
RULES=""
if [[ "$MULTIFILE" == false ]]; then
  RULES=$(cat ~/nina/agy_prompt_rules.md 2>/dev/null || echo "[agy_prompt_rules.md not found]")
fi
MULTIFILE_RULES=""
if [[ "$MULTIFILE" == true ]]; then
  MULTIFILE_RULES=$(cat ~/nina/agy_prompt_multifile.md 2>/dev/null || echo "[agy_prompt_multifile.md not found]")
fi

# --- Auto-inject codemap rows for target file ---
CODEMAP_BLOCK=""
if [[ -f ~/nina/nina_codemap.md ]]; then
  BASENAME=$(basename "$FILE")
  CODEMAP_BLOCK=$(awk "/### $BASENAME/,/^###/{if (/^###/ && !/### $BASENAME/) exit; print}" ~/nina/nina_codemap.md 2>/dev/null | head -30 || true)
  if [[ -z "$CODEMAP_BLOCK" ]]; then
    CODEMAP_BLOCK=$(grep -i "$BASENAME" ~/nina/nina_codemap.md | head -10 || true)
  fi
fi

# --- AST-based context injection ---
CONTEXT_BLOCK=""
if [[ "$INJECT_CTX" == true && -f "$FILE" ]]; then
  KEYWORD=$(echo "$TASK" | grep -oP '(?<=fix |add |update |change |rename |remove |refactor |in |for )[a-zA-Z_]+' | head -1 || true)
  if [[ -n "$KEYWORD" && "$FILE" == *.py ]]; then
    CONTEXT_BLOCK=$("$PYTHON" - <<PYEOF 2>/dev/null || true
import ast
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
except Exception:
    pass
PYEOF
    )
  fi
  if [[ -z "$CONTEXT_BLOCK" && -n "${KEYWORD:-}" ]]; then
    MATCH=$(grep -n "$KEYWORD" "$FILE" | head -1 | cut -d: -f1 || true)
    if [[ -n "$MATCH" ]]; then
      START=$(( MATCH > 5 ? MATCH - 5 : 1 ))
      CONTEXT_BLOCK=$(awk "NR>=$START && NR<=$((START+35))" "$FILE" | head -40)
    fi
  fi
  [[ -z "$CONTEXT_BLOCK" ]] && CONTEXT_BLOCK=$(head -40 "$FILE")
fi

# --- Output prompt ---
echo ""
echo "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
echo " TASK ID : $TASK_ID"
echo " FILE    : $FILE"
[[ "$MULTIFILE" == true ]] && echo " MODE    : MULTI-FILE"
echo "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
echo ""

echo "$CORE"
echo ""
[[ -n "$RULES" ]] && echo "$RULES" && echo ""
[[ -n "$MULTIFILE_RULES" ]] && echo "$MULTIFILE_RULES" && echo ""

cat <<PROMPT
---
File: $FILE
SCOPE: $FILE
OUT_OF_SCOPE: $NOTOUCH
Task: $TASK
Acceptance: $ACCEPT
Post-task verify: \`python3 -m py_compile $FILE\` + \`pyflakes $FILE\` + \`python3 agy_impact_check.py $FILE\` — zero errors.
Then run OBSERVE loop (git diff HEAD → confirm acceptance → COMMIT or FIX FIRST).
Commit format: fix(scope): description ($TASK_ID)
PROMPT

if [[ -n "$CODEMAP_BLOCK" ]]; then
  echo ""
  echo "--- Codemap: $FILE ---"
  echo "$CODEMAP_BLOCK"
  echo "--- End codemap ---"
fi

if [[ -n "$CONTEXT_BLOCK" ]]; then
  echo ""
  echo "--- Relevant context from $FILE ---"
  echo "$CONTEXT_BLOCK"
  echo "--- End context ---"
fi

echo ""
echo "\u2705 Pre-flight passed. Copy everything above into agy."
echo "   After task completes, run: ./scripts/agy_verify.sh $FILE $TASK_ID"

if [[ -n "$GUARDIAN_PRE" && "$GUARDIAN_PRE" != "guardian_unavailable" ]]; then
  echo "$GUARDIAN_PRE" > /tmp/nina_guardian_pre_"$TASK_ID".snap
  echo "   Guardian snapshot saved \u2192 /tmp/nina_guardian_pre_${TASK_ID}.snap"
fi
