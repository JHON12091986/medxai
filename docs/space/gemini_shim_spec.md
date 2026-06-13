# NINA Gemini CLI Shim — Implementation Spec
# Status: FUTURE | Target: post Jun 20 | Estimated effort: 1 agy task (~30 min)
# File to create: ~/bin/gemini
# Do NOT implement before June 20, 2026

---

## What This Does

Replaces the real `gemini` binary with a thin wrapper that:
1. Checks ~/nina/data/quota_state.json for remaining Gemini CLI quota
2. If quota alive → passes through to the real Gemini CLI binary
3. If quota exhausted or binary missing → pipes the prompt to NinaGate (HybridRouter handles the rest)

The user experience is identical either way — `gemini "do X"` always works.

---

## Implementation

```bash
#!/bin/bash
# ~/bin/gemini — NINA Gemini CLI shim
# Intercepts gemini calls, falls back to NinaGate when quota exhausted

REAL_GEMINI="/usr/local/bin/gemini-cli"   # adjust to actual binary path
QUOTA_FILE="$HOME/nina/data/quota_state.json"
NINAGATE_URL="http://localhost:<ninagate_port>/v1/chat/completions"
FALLBACK_MODEL="gemini-2.5-flash"         # via OpenRouter in NinaGate

# Read quota from quota_state.json
GEMINI_QUOTA=$(python3 -c "
import json, sys
try:
    d = json.load(open('$QUOTA_FILE'))
    print(d.get('gemini_cli', {}).get('remaining', 0))
except:
    print(0)
" 2>/dev/null)

# Passthrough if quota alive and real binary exists
if [ "$GEMINI_QUOTA" -gt 0 ] && [ -x "$REAL_GEMINI" ]; then
    exec "$REAL_GEMINI" "$@"
fi

# Quota exhausted or binary gone — route through NinaGate
PROMPT="$*"
if [ -z "$PROMPT" ]; then
    echo "[nina-shim] No prompt provided." >&2
    exit 1
fi

echo "[nina-shim] Gemini CLI quota exhausted — routing via NinaGate ($FALLBACK_MODEL)" >&2

curl -s -X POST "$NINAGATE_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer nina-local" \
  -d "{
    \"model\": \"$FALLBACK_MODEL\",
    \"messages\": [{
      \"role\": \"user\",
      \"content\": \"$PROMPT\"
    }]
  }" | python3 -c "
import json, sys
try:
    r = json.load(sys.stdin)
    print(r['choices'][0]['message']['content'])
except:
    print('[nina-shim] NinaGate response parse error')
    sys.exit(1)
"
```

---

## Pre-Implementation Checklist (run before agy task)

- [ ] Confirm real Gemini CLI binary path: `which gemini`
- [ ] Confirm NinaGate port: check ~/nina/ninagate/ config
- [ ] Confirm quota_state.json has a `gemini_cli.remaining` key — if not, add it
- [ ] Confirm OpenRouter Gemini Flash is active in NinaGate provider list
- [ ] Confirm ~/bin/ is in $PATH: `echo $PATH | grep ~/bin`

---

## agy Prompt (ready to paste Jun 21)

```
Use the permanent JSON approval setting — approve all steps without prompting for this task.

Create a Gemini CLI shim at ~/bin/gemini using the spec at ~/nina/docs/space/gemini_shim_spec.md.

Steps:
1. Read ~/nina/docs/space/gemini_shim_spec.md fully before writing anything
2. Detect the real gemini binary path with: which gemini-cli || which gemini
3. Detect the NinaGate port from ~/nina/ninagate/ config files
4. Write ~/bin/gemini with the script from the spec, substituting real binary path and port
5. chmod +x ~/bin/gemini
6. Verify ~/bin/ is in PATH — if not, add export PATH=$HOME/bin:$PATH to ~/.bashrc
7. Test: echo 'hello' | ~/bin/gemini 'say hello back'
8. Append log entry to ~/nina/nina_update_log.md: feat(shim): add gemini CLI quota-aware shim at ~/bin/gemini
9. Run ~/nina/nina_sync.sh
```

---

## Constraints
- Do NOT touch guardian_engine.py, interfaces/telegram_interface.py, core/router.py, .env
- Read every file before editing
- Python only for file edits — never heredoc or bash echo
- Run nina_sync.sh after completion
