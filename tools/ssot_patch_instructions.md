# SSOT Production Fix Instructions

Generated: 2026-06-22 by nina_ssot fix commit.

## Why this file exists

`tools/guardian_engine.py` (33KB), `tools/pipeline_autopilot.py`, `tools/jules.py`,
and `core/task_manager/dispatcher.py` contain hardcoded env key strings that
need to be replaced with constants from `core.constants`.

These files are too large to safely rewrite via the GitHub MCP API without
reading and rewriting the entire file (risking data loss). The sed commands
below are safe and reversible.

## Run these on your machine (~/nina)

```bash
# guardian_engine.py
sed -i \
  -e 's/os\.getenv("TELEGRAM_BOT_TOKEN")/os.getenv(ENV_TELEGRAM_BOT_TOKEN)/g' \
  -e 's/os\.getenv("TELEGRAM_CHAT_ID")/os.getenv(ENV_TELEGRAM_CHAT_ID)/g' \
  -e 's/os\.getenv("API_SECRET_KEY")/os.getenv(ENV_API_SECRET_KEY)/g' \
  -e 's/os\.getenv("AUTHORIZED_USER_ID")/os.getenv(ENV_TELEGRAM_CHAT_ID)/g' \
  tools/guardian_engine.py

# pipeline_autopilot.py
sed -i \
  -e 's/os\.getenv("TELEGRAM_BOT_TOKEN")/os.getenv(ENV_TELEGRAM_BOT_TOKEN)/g' \
  -e 's/os\.getenv("TELEGRAM_CHAT_ID")/os.getenv(ENV_TELEGRAM_CHAT_ID)/g' \
  -e 's/os\.getenv("AUTHORIZED_USER_ID")/os.getenv(ENV_TELEGRAM_CHAT_ID)/g' \
  -e 's/os\.getenv("JULES_API_KEY")/os.getenv(ENV_JULES_API_KEY)/g' \
  tools/pipeline_autopilot.py

# jules.py
sed -i \
  -e 's/os\.getenv("TELEGRAM_BOT_TOKEN")/os.getenv(ENV_TELEGRAM_BOT_TOKEN)/g' \
  -e 's/os\.getenv("TELEGRAM_CHAT_ID")/os.getenv(ENV_TELEGRAM_CHAT_ID)/g' \
  -e 's/os\.getenv("AUTHORIZED_USER_ID")/os.getenv(ENV_TELEGRAM_CHAT_ID)/g' \
  tools/jules.py

# core/task_manager/dispatcher.py
sed -i \
  -e 's/os\.getenv("TELEGRAM_BOT_TOKEN")/os.getenv(ENV_TELEGRAM_BOT_TOKEN)/g' \
  -e 's/os\.getenv("TELEGRAM_CHAT_ID")/os.getenv(ENV_TELEGRAM_CHAT_ID)/g' \
  -e 's/os\.getenv("AUTHORIZED_USER_ID")/os.getenv(ENV_TELEGRAM_CHAT_ID)/g' \
  core/task_manager/dispatcher.py
```

## Add imports to each patched file

At the top of each file (after existing imports), add:

```python
from core.constants import (
    ENV_TELEGRAM_BOT_TOKEN,
    ENV_TELEGRAM_CHAT_ID,
    ENV_API_SECRET_KEY,
)
```

## Verify

```bash
python tools/nina_ssot.py --report
# Expected: violations: 5 (orphans only), hardcoded: 0
```

## Orphan env vars (also fix in .env)

These 5 keys are defined in `.env` but never consumed — either add consumers
or remove from `.env`:

- `EWS_SERVER`
- `EWS_DOMAIN`
- `EWS_AUTH_TYPE`
- `WORKSPACE_DIR`
- `DEAD_MAN_MAX_INTERVAL_MIN`
