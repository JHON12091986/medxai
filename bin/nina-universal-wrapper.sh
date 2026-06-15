#!/usr/bin/env bash
# ~/nina/bin/nina-universal-wrapper.sh
# A universal proxy wrapper for AI CLI tools.
# It intercepts calls to CLIs (like agy, gemini, etc.) and routes them
# through the NinaGate proxy to ensure local fallback when quotas are exhausted.

TOOL_NAME=$(basename "$0")
NINAGATE_URL="http://localhost:8080/genai"
NINAGATE_OPENAI_URL="http://localhost:8080/v1"

# --- Inject Environment Variables ---
# Gemini SDK configuration
export GOOGLE_GEMINI_BASE_URL="$NINAGATE_URL"
export GEMINI_BASE_URL="$NINAGATE_URL"

# OpenAI SDK configuration
export OPENAI_BASE_URL="$NINAGATE_OPENAI_URL"

# Ensure API keys are populated to prevent SDK errors
if [ -z "$GEMINI_API_KEY" ]; then
    export GEMINI_API_KEY="nina-local-bypass"
fi
if [ -z "$OPENAI_API_KEY" ]; then
    export OPENAI_API_KEY="nina-local-bypass"
fi

# --- Resolve Real Binary ---
REAL_BIN=""
# Iterate over all executables in PATH matching TOOL_NAME
while IFS= read -r p; do
    if [ -n "$p" ] && [ "$p" != "$0" ] && [ "$(realpath -q "$p")" != "$(realpath -q "$0")" ]; then
        REAL_BIN="$p"
        break
    fi
done < <(which -a "$TOOL_NAME" 2>/dev/null)

if [ -z "$REAL_BIN" ]; then
    echo "[nina-wrapper] Error: Could not find original binary for '$TOOL_NAME' in PATH." >&2
    
    # If it's gemini, we have a fallback script for missing binary
    if [ "$TOOL_NAME" = "gemini" ]; then
        echo "[nina-wrapper] Routing directly via NinaGate Python fallback" >&2
        python3 -c "
import urllib.request, json, sys, os
prompt = ' '.join(sys.argv[1:])
if not prompt: sys.exit(1)
url = 'http://localhost:8080/v1/chat/completions'
payload = {'model': 'gemini-2.5-flash', 'messages': [{'role': 'user', 'content': prompt}]}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {os.getenv(\"GEMINI_API_KEY\")}'})
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode('utf-8'))
        if 'choices' in res and res['choices']: print(res['choices'][0]['message']['content'])
except Exception as e:
    print(f'[nina-wrapper] NinaGate request failed: {e}', file=sys.stderr)
    sys.exit(1)
" "$@"
        exit $?
    fi
    
    exit 1
fi

# echo "[nina-wrapper] Routing $TOOL_NAME -> $REAL_BIN via NinaGate" >&2

# --- Execute Real Binary ---
exec "$REAL_BIN" "$@"
