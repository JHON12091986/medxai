# NINA Key Resolver — Architecture & Runbook

> **File**: `core/key_resolver.py`  
> **Singleton**: `from core.key_resolver import resolver`  
> **Log**: `logs/key_resolver.log` (JSON lines)

---

## Resolution Chain (priority order)

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1 │ os.environ      (in-process, highest priority) │
│  Layer 2 │ .env.local      (machine-local, git-ignored)   │
│  Layer 3 │ .env            (repo baseline)                 │
│  Layer 4 │ data/secrets.json  (runtime-persisted)         │
│  Layer 5 │ AUTO-GENERATE   (API_SECRET_KEY only)          │
│  Layer 6 │ HARD FAIL       (required) / None (optional)   │
└─────────────────────────────────────────────────────────┘
```

For each layer, **all known aliases** are tried before moving to the next layer.

---

## Key Status Table

| Key | Required | Auto-gen | Description |
|-----|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ YES | ❌ | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | ✅ YES | ❌ | Your Telegram user/chat ID |
| `API_SECRET_KEY` | ✅ YES | ✅ AUTO | NINA HTTP bearer token |
| `GROQ_API_KEY` | optional | ❌ | Groq LPU (Tier-1) |
| `GEMINI_API_KEY` | optional | ❌ | Google Gemini aggregator |
| `CEREBRAS_API_KEY` | optional | ❌ | Cerebras |
| `MISTRAL_API_KEY` | optional | ❌ | Mistral |
| `OPENROUTER_API_KEY` | optional | ❌ | OpenRouter |
| `OPENAI_API_KEY` | optional | ❌ | OpenAI |
| `DEEPSEEK_API_KEY` | optional | ❌ | DeepSeek |
| `PERPLEXITY_API_KEY` | optional | ❌ | Perplexity |
| `TOGETHER_API_KEY` | optional | ❌ | Together AI |
| `COHERE_API_KEY` | optional | ❌ | Cohere |
| `FIREWORKS_API_KEY` | optional | ❌ | Fireworks |
| `XAI_API_KEY` | optional | ❌ | xAI Grok |
| `SAMBANOVA_API_KEY` | optional | ❌ | SambaNova |
| `HYPERBOLIC_API_KEY` | optional | ❌ | Hyperbolic |
| `NOVITA_API_KEY` | optional | ❌ | Novita |
| `ONEBRAIN_API_KEY` | optional | ❌ | OneBrain |
| `EWS_USERNAME` | optional | ❌ | BASIC Bank EWS |
| `EWS_PASSWORD` | optional | ❌ | BASIC Bank EWS |
| `EWS_MY_EMAIL` | optional | ❌ | Your BASIC Bank email |
| `EWS_SHARED_EMAIL` | optional | ❌ | Shared mailbox |

---

## Known Aliases (auto-resolved)

| Canonical Key | Accepted Aliases |
|---|---|
| `TELEGRAM_CHAT_ID` | `TELEGRAMCHATID`, `AUTHORIZED_USER_ID`, `ALLOWED_USERS` |
| `TELEGRAM_BOT_TOKEN` | `TELEGRAM_TOKEN` |
| `API_SECRET_KEY` | `NINA_API_KEY`, `SECRET_KEY` |
| `GEMINI_API_KEY` | `GOOGLE_API_KEY` |

Aliases are resolved in every layer. The canonical key is always written back to `os.environ` on first resolution.

---

## data/secrets.json — Runtime Persistence

`data/secrets.json` is the **persistence layer for keys set at runtime**.

- Created automatically on first write.
- **Git-ignored** (add `data/secrets.json` to `.gitignore` if not already there).
- Written by:
  - `resolver.set(key, value)` — programmatic
  - `/setkey KEY value` — Telegram command (wires to `set_key()`)
  - Auto-generation of `API_SECRET_KEY` on first boot

### Format
```json
{
  "API_SECRET_KEY": "auto-generated-token-here",
  "GROQ_API_KEY": "gsk_..."
}
```

---

## API Usage

### Resolve a key
```python
from core.key_resolver import resolver

# Required key — raises KeyResolutionError with exact remediation if missing
token = resolver.get("TELEGRAM_BOT_TOKEN")

# Optional key — returns None if missing
groq = resolver.get("GROQ_API_KEY", required=False)

# Optional with default
host = resolver.get("OLLAMA_HOST", required=False, default="http://localhost:11434")
```

### Set a key at runtime
```python
from core.key_resolver import set_key
set_key("GROQ_API_KEY", "gsk_newkey")  # persisted to data/secrets.json immediately
```

### Full audit report
```python
from core.key_resolver import audit_keys
print(audit_keys())
```

### Reload (after editing .env on disk)
```python
resolver.reload()
```

---

## Startup Integration

`core/config.py → load_config()` now calls `resolver.get()` instead of `get_secret()` for all keys.

`core/vault.py → init_vault()` calls `resolver.reload()` to sync after `.env` is re-read.

---

## Telegram /setkey Command

Wire this in `interfaces/telegram_interface.py`:

```python
# In the command handler:
if text.startswith("/setkey "):
    parts = text.split(" ", 2)
    if len(parts) == 3:
        _, key, value = parts
        from core.key_resolver import set_key
        set_key(key.upper(), value.strip())
        await bot.send_message(chat_id, f"✅ Key `{key.upper()}` saved.")
```

---

## Error Format

When a required key is missing, `KeyResolutionError` is raised with full context:

```
NINA cannot start: required key 'TELEGRAM_BOT_TOKEN' is missing.
  Description : Telegram Bot API token (from @BotFather)
  Aliases     : ['TELEGRAM_TOKEN']
  Fix         : Get from @BotFather on Telegram → /newbot → copy token → add to .env
  Sources tried: os.environ → .env.local → .env → data/secrets.json
```

---

## Logs

`logs/key_resolver.log` — one JSON line per resolution event:

```json
{"ts": "2026-06-25T06:40:00.000000+0000", "key": "TELEGRAM_BOT_TOKEN", "event": "RESOLVED", "source": ".env[TELEGRAM_BOT_TOKEN]"}
{"ts": "2026-06-25T06:40:00.001000+0000", "key": "API_SECRET_KEY",      "event": "auto_generated", "source": "auto_generated"}
{"ts": "2026-06-25T06:40:00.002000+0000", "key": "GROQ_API_KEY",        "event": "MISSING_OPTIONAL", "source": null}
```

Events: `RESOLVED` | `MISSING_OPTIONAL` | `HARD_FAIL` | `SET_RUNTIME` | `auto_generated`

---

## Contingency Runbook

### NINA won't start — TELEGRAM_BOT_TOKEN missing
1. Go to Telegram → message `@BotFather` → `/mybots` → select your bot → `API Token`
2. `echo 'TELEGRAM_BOT_TOKEN=123456:ABCdef...' >> ~/nina/.env`
3. `systemctl --user restart nina`

### NINA won't start — TELEGRAM_CHAT_ID missing
1. Message `@userinfobot` on Telegram → copy the `Id` number
2. `echo 'TELEGRAM_CHAT_ID=123456789' >> ~/nina/.env`
3. `systemctl --user restart nina`

### API_SECRET_KEY missing (ninagate auth broken)
- **This auto-generates on boot** — check `data/secrets.json` for the generated value
- Or set manually: `echo 'API_SECRET_KEY=mysecret' >> ~/nina/.env`
- opencode config: update `OPENAI_API_KEY` in opencode settings to match

### Key was set but still not found
1. Run audit: `cd ~/nina && python -c "from core.key_resolver import audit_keys; print(audit_keys())"`
2. Check `logs/key_resolver.log` for `HARD_FAIL` events
3. Try `resolver.reload()` if you edited `.env` while NINA was running

### Add a new provider key at runtime (no restart needed)
```
/setkey NEWPROVIDER_API_KEY sk-abc123
```
Then NINA will pick it up immediately via `data/secrets.json`.
