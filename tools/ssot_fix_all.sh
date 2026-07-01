#!/usr/bin/env bash
# tools/ssot_fix_all.sh — NINA SSOT 1-Click Hardcode Fixer
# Idempotent. Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "[ssot_fix_all] Root: $(pwd)"
echo "[ssot_fix_all] Patching real hardcoded getenv calls..."

patch_file() {
    local file="$1"; shift
    [ -f "$file" ] && { echo "  [FIX] $file"; sed -i "$@" "$file"; } || echo "  [SKIP] $file"
}

COMMON=(
    -e 's/\.get("TELEGRAM_BOT_TOKEN")/\.get(ENV_TELEGRAM_BOT_TOKEN)/g'
    -e 's/\.getenv("TELEGRAM_BOT_TOKEN")/\.getenv(ENV_TELEGRAM_BOT_TOKEN)/g'
    -e 's/\.get("TELEGRAM_CHAT_ID")/\.get(ENV_TELEGRAM_CHAT_ID)/g'
    -e 's/\.getenv("TELEGRAM_CHAT_ID")/\.getenv(ENV_TELEGRAM_CHAT_ID)/g'
    -e 's/\.get("AUTHORIZED_USER_ID")/\.get(ENV_TELEGRAM_CHAT_ID)/g'
    -e 's/\.getenv("AUTHORIZED_USER_ID")/\.getenv(ENV_TELEGRAM_CHAT_ID)/g'
    -e 's/\.get("ALLOWED_USERS")/\.get(ENV_TELEGRAM_CHAT_ID)/g'
    -e 's/\.getenv("ALLOWED_USERS")/\.getenv(ENV_TELEGRAM_CHAT_ID)/g'
    -e 's/\.get("API_SECRET_KEY")/\.get(ENV_API_SECRET_KEY)/g'
    -e 's/\.getenv("API_SECRET_KEY")/\.getenv(ENV_API_SECRET_KEY)/g'
    -e 's/\.get("OLLAMA_HOST")/\.get(ENV_OLLAMA_HOST)/g'
    -e 's/\.getenv("OLLAMA_HOST")/\.getenv(ENV_OLLAMA_HOST)/g'
    -e 's/\.get("OPENAI_API_KEY")/\.get(ENV_OPENAI_API_KEY)/g'
    -e 's/\.get("CEREBRAS_API_KEY")/\.get(ENV_CEREBRAS_API_KEY)/g'
    -e 's/\.get("GROQ_API_KEY")/\.get(ENV_GROQ_API_KEY)/g'
    -e 's/\.get("GEMINI_API_KEY")/\.get(ENV_GEMINI_API_KEY)/g'
    -e 's/\.get("MISTRAL_API_KEY")/\.get(ENV_MISTRAL_API_KEY)/g'
    -e 's/\.get("OPENROUTER_API_KEY")/\.get(ENV_OPENROUTER_API_KEY)/g'
    -e 's/\.get("DEEPSEEK_API_KEY")/\.get(ENV_DEEPSEEK_API_KEY)/g'
    -e 's/\.get("PERPLEXITY_API_KEY")/\.get(ENV_PERPLEXITY_API_KEY)/g'
    -e 's/\.get("TOGETHER_API_KEY")/\.get(ENV_TOGETHER_API_KEY)/g'
    -e 's/\.get("COHERE_API_KEY")/\.get(ENV_COHERE_API_KEY)/g'
    -e 's/\.get("FIREWORKS_API_KEY")/\.get(ENV_FIREWORKS_API_KEY)/g'
    -e 's/\.get("XAI_API_KEY")/\.get(ENV_XAI_API_KEY)/g'
    -e 's/\.get("SAMBANOVA_API_KEY")/\.get(ENV_SAMBANOVA_API_KEY)/g'
    -e 's/\.get("HYPERBOLIC_API_KEY")/\.get(ENV_HYPERBOLIC_API_KEY)/g'
    -e 's/\.get("NOVITA_API_KEY")/\.get(ENV_NOVITA_API_KEY)/g'
    -e 's/\.get("EWS_USERNAME")/\.get(ENV_EWS_USERNAME)/g'
    -e 's/\.get("EWS_MY_EMAIL")/\.get(ENV_EWS_MY_EMAIL)/g'
    -e 's/\.get("EWS_SHARED_EMAIL")/\.get(ENV_EWS_SHARED_EMAIL)/g'
)

patch_file tools/semantic_dedup.py          "${COMMON[@]}"
patch_file tools/audit_repo_hygiene.py      "${COMMON[@]}"
patch_file tools/telegram_notify.py         "${COMMON[@]}"
patch_file tools/pipeline_autopilot.py      "${COMMON[@]}" \
    -e 's/\.get("JULES_API_KEY")/\.get(ENV_JULES_API_KEY)/g' \
    -e 's/\.getenv("JULES_API_KEY")/\.getenv(ENV_JULES_API_KEY)/g'
patch_file tools/jules.py                   "${COMMON[@]}"
patch_file core/task_manager/dispatcher.py  "${COMMON[@]}"
patch_file tools/ninagate_client.py         "${COMMON[@]}"
patch_file tools/ninagate/main.py           "${COMMON[@]}"

echo ""
echo "--- Adding imports ---"
IMPORT='from core.constants import (ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID, ENV_API_SECRET_KEY, ENV_OPENAI_API_KEY, ENV_CEREBRAS_API_KEY, ENV_GROQ_API_KEY, ENV_GEMINI_API_KEY, ENV_MISTRAL_API_KEY, ENV_OPENROUTER_API_KEY, ENV_DEEPSEEK_API_KEY, ENV_PERPLEXITY_API_KEY, ENV_TOGETHER_API_KEY, ENV_COHERE_API_KEY, ENV_FIREWORKS_API_KEY, ENV_XAI_API_KEY, ENV_SAMBANOVA_API_KEY, ENV_HYPERBOLIC_API_KEY, ENV_NOVITA_API_KEY, ENV_OLLAMA_HOST, ENV_EWS_USERNAME, ENV_EWS_MY_EMAIL, ENV_EWS_SHARED_EMAIL, ENV_JULES_API_KEY)'

add_import() {
    local f="$1"
    [ ! -f "$f" ] && return
    if grep -qF 'from core.constants import' "$f"; then
        echo "  [OK] $f"
    else
        python3 - "$f" "$IMPORT" <<'PY'
import sys, re
f, imp = sys.argv[1], sys.argv[2]
lines = open(f).readlines()
last = next((i for i in range(len(lines)-1,-1,-1) if re.match(r'^(import |from )', lines[i])), 0)
lines.insert(last+1, imp+'\n')
open(f,'w').writelines(lines)
print(f'  [ADD] {f}')
PY
    fi
}

for f in tools/semantic_dedup.py tools/audit_repo_hygiene.py tools/telegram_notify.py \
         tools/pipeline_autopilot.py tools/jules.py core/task_manager/dispatcher.py \
         tools/ninagate_client.py tools/ninagate/main.py; do
    add_import "$f"
done

# Add ENV_JULES_API_KEY to constants if missing
if ! grep -q 'ENV_JULES_API_KEY' core/constants.py; then
    printf '\n# Jules\nENV_JULES_API_KEY = "JULES_API_KEY"\n' >> core/constants.py
    echo "  [ADD] ENV_JULES_API_KEY to core/constants.py"
fi

echo ""
echo "--- Verifying ---"
PY=$( [ -f .venv/bin/python ] && echo .venv/bin/python || echo python3 )
"$PY" tools/nina_ssot.py --report
echo ""
echo "[ssot_fix_all] Done. Remaining violations should be ORPHAN env vars only."
