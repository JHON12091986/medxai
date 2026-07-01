#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  setup_opencode_provider.sh — 1-click OpenCode provider config for Nina
#  Usage: bash ~/nina/opencode/setup_opencode_provider.sh
#
#  Schema source: https://opencode.ai/config.json (verified v1.17.9)
#  Correct key path: provider.<name>.options.apiKey
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

NINA_ROOT="$HOME/nina"
OPENCODE_BIN="$HOME/.opencode/bin/opencode"
CONFIG_DIR="$HOME/.config/opencode"
CONFIG_FILE="$CONFIG_DIR/config.json"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║        Nina × OpenCode — Provider Setup              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── Load Nina .env ────────────────────────────────────────────────────────────
ENV_FILE=""
if   [ -f "$NINA_ROOT/.env.local" ]; then ENV_FILE="$NINA_ROOT/.env.local"
elif [ -f "$NINA_ROOT/.env" ];       then ENV_FILE="$NINA_ROOT/.env"
fi

if [ -z "$ENV_FILE" ]; then
  echo "❌  No .env or .env.local found in $NINA_ROOT"
  exit 1
fi

echo "📂  Loading keys from: $ENV_FILE"
set -a; source "$ENV_FILE"; set +a

# ── Pick best available provider ──────────────────────────────────────────────
PROVIDER=""
API_KEY=""
MODEL=""

pick() {
  local name="$1" key="$2" model="$3"
  if [ -n "${key:-}" ] && [ "$key" != '""' ] && [[ "$key" != *"your_"* ]]; then
    PROVIDER="$name"; API_KEY="$key"; MODEL="$model"
  fi
}

# Priority: Gemini → Anthropic → OpenAI → OpenRouter → Groq
pick "gemini"    "${GEMINI_API_KEY:-}"    "gemini-2.0-flash"
[ -z "$PROVIDER" ] && pick "anthropic"  "${ANTHROPIC_API_KEY:-}"  "claude-sonnet-4-5"
[ -z "$PROVIDER" ] && pick "openai"     "${OPENAI_API_KEY:-}"     "gpt-4o-mini"
[ -z "$PROVIDER" ] && pick "openrouter" "${OPENROUTER_API_KEY:-}" "google/gemini-flash-1.5"
[ -z "$PROVIDER" ] && pick "groq"       "${GROQ_API_KEY:-}"       "llama-3.1-8b-instant"

if [ -z "$PROVIDER" ]; then
  echo "❌  No usable API key found in $ENV_FILE"
  echo "    Set at least one of: GEMINI_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY"
  exit 1
fi

MASKED="${API_KEY:0:6}***${API_KEY: -4}"
echo "✅  Provider : $PROVIDER"
echo "🤖  Model    : $PROVIDER/$MODEL"
echo "🔑  Key      : $MASKED"
echo ""

# ── Write ~/.config/opencode/config.json ───────────────────────────────────
# Schema: https://opencode.ai/config.json
# provider.<name>.options.apiKey  (NOT providers.apiKey)
echo "⚙️   Writing $CONFIG_FILE ..."
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_FILE" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "$PROVIDER/$MODEL",
  "provider": {
    "$PROVIDER": {
      "options": {
        "apiKey": "$API_KEY"
      }
    }
  }
}
EOF

echo "✅  Config written:"
cat "$CONFIG_FILE"
echo ""

# ── Smoke test ────────────────────────────────────────────────────────────────
echo "🧪  Smoke test: opencode run \"echo symbiosis-ok\""
cd "$NINA_ROOT"
if timeout 60 "$OPENCODE_BIN" run "echo symbiosis-ok"; then
  echo ""
  echo "✅  OpenCode is LIVE!"
else
  echo ""
  echo "⚠️   Smoke test failed. Config is at: $CONFIG_FILE"
  exit 1
fi

# ── Full Nina loop test ────────────────────────────────────────────────────
echo ""
echo "🔄  Full Nina loop test (skip_ndev_upload + skip_super_sync)..."
cd "$NINA_ROOT"
if source venv/bin/activate 2>/dev/null; then
  python -m tools.opencode "echo hello from nina symbiosis" 2>&1 | tail -20
else
  echo "⚠️  venv not found — run manually: python -m tools.opencode \"echo hello\""
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  🎉  Setup complete!                                 ║"
echo "║                                                      ║"
echo "║  Now send from your Telegram bot:                   ║"
echo "║    /opencode echo hello from nina                   ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
