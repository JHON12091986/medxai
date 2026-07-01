# NINA Contract Registry

> **SSOT for every connector name in the codebase.**
> A connector = any string that links two files together:
> env var names, config attributes, log channels, cron IDs, tool keys,
> Telegram commands, file paths, service names, session dict keys.
>
> **Rule:** Before adding any new connector, add it to `core/constants.py`
> AND add a row here. Never hardcode a connector string in any file.

---

## 1. Environment Variables

| Constant | `.env` Key | Config Attr | Defined In | Consumed By | Notes |
|---|---|---|---|---|---|
| `ENV_TELEGRAM_BOT_TOKEN` | `TELEGRAM_BOT_TOKEN` | `telegram_bot_token` | `core/constants.py` | `core/config.py`, `core/vault.py` | Required. No alias. |
| `ENV_TELEGRAM_CHAT_ID` | `TELEGRAM_CHAT_ID` | `telegram_chat_id` | `core/constants.py` | `core/config.py`, `interfaces/telegram_interface.py` | Required. **Old alias `TELEGRAMCHATID` removed.** |
| `ENV_AUTHORIZED_USER_ID` | `AUTHORIZED_USER_ID` | `authorized_user_id` | `core/constants.py` | `core/config.py`, `interfaces/middleware.py` | Required. Auth gate. |
| `ENV_API_SECRET_KEY` | `API_SECRET_KEY` | `api_secret_key` | `core/constants.py` | `core/config.py`, `tools/ninagate/main.py` | Auto-generated if missing. |
| `ENV_GROQ_API_KEY` | `GROQ_API_KEY` | `groq_api_key` | `core/constants.py` | `core/config.py`, `core/router.py` | Optional. |
| `ENV_GEMINI_API_KEY` | `GEMINI_API_KEY` | `gemini_api_key` | `core/constants.py` | `core/config.py`, `core/router.py` | Optional. |
| `ENV_CEREBRAS_API_KEY` | `CEREBRAS_API_KEY` | `cerebras_api_key` | `core/constants.py` | `core/config.py`, `core/router.py` | Optional. |
| `ENV_OPENAI_API_KEY` | `OPENAI_API_KEY` | `openai_api_key` | `core/constants.py` | `core/config.py`, `core/router.py` | Optional. |
| `ENV_MISTRAL_API_KEY` | `MISTRAL_API_KEY` | `mistral_api_key` | `core/constants.py` | `core/config.py`, `core/router.py` | Optional. |
| `ENV_DEEPSEEK_API_KEY` | `DEEPSEEK_API_KEY` | `deepseek_api_key` | `core/constants.py` | `core/config.py`, `core/router.py` | Optional. |
| `ENV_OPENROUTER_API_KEY` | `OPENROUTER_API_KEY` | `openrouter_api_key` | `core/constants.py` | `core/config.py`, `core/router.py` | Optional. |
| `ENV_ONEBRAIN_API_KEY` | `ONEBRAINAPIKEY` | `one_brain_api_key` | `core/constants.py` | `core/config.py` | Note: no underscore in env key. |
| `ENV_ONEBRAIN_API_BASE` | `ONEBRAINAPIBASE` | `one_brain_api_base` | `core/constants.py` | `core/config.py` | Note: no underscore in env key. |
| `ENV_OLLAMA_HOST` | `OLLAMAHOST` | `ollama_host` | `core/constants.py` | `core/config.py` | Note: no underscore in env key. |
| `ENV_DEAD_MAN_PING_URL` | `DEADMANPINGURL` | `dead_man_ping_url` | `core/constants.py` | `core/config.py` | Note: no underscore in env key. |
| `ENV_EWS_PASSWORD` | `EWSPASSWORD` | `ews_password` | `core/constants.py` | `core/config.py` | Note: no underscore in env key. |
| `ENV_EWS_USERNAME` | `EWS_USERNAME` | `ews_username` | `core/constants.py` | `core/config.py` | |
| `ENV_EWS_MY_EMAIL` | `EWS_MY_EMAIL` | `ews_my_email` | `core/constants.py` | `core/config.py` | |
| `ENV_EWS_SHARED_EMAIL` | `EWS_SHARED_EMAIL` | `ews_shared_email` | `core/constants.py` | `core/config.py` | |

---

## 2. Logger Channel Names

| Constant | String Value | Who Uses It |
|---|---|---|
| `LOG_ROOT` | `nina` | Root logger |
| `LOG_CONFIG` | `nina.config` | `core/config.py` |
| `LOG_AGENT` | `nina.agent` | `core/agent.py` |
| `LOG_TELEGRAM` | `nina.telegram` | `interfaces/telegram_interface.py` |
| `LOG_SECURITY` | `nina.security` | `interfaces/middleware.py` |
| `LOG_MEMORY` | `nina.memory` | `core/memory*.py` |
| `LOG_SCHEDULER` | `nina.scheduler` | `crons/runner.py` |
| `LOG_ROUTER` | `nina.router` | `core/router.py` |
| `LOG_VAULT` | `nina.vault` | `core/vault.py` |
| `LOG_MCP` | `nina.mcp` | `core/mcp_client.py` |
| `LOG_NINAGATE` | `nina.ninagate` | `tools/ninagate/main.py` |
| `LOG_CRON` | `nina.cron` | `crons/` |
| `LOG_GUARD` | `nina.guard` | guardian engine |
| `LOG_COORDINATOR` | `nina.coordinator` | `core/coordinator_agent.py` |

---

## 3. Cron Job IDs

| Constant | `CronJob.id` Value | File | Schedule |
|---|---|---|---|
| `CRON_MORNING_REPORT` | `morning_report` | `crons/` | Daily |
| `CRON_BACKUP_JOBS` | `backup_jobs` | `crons/backup_jobs.py` | Daily |
| `CRON_NEXUS_EVOLUTION` | `nexus_evolution` | `crons/nexus_evolution.py` | Periodic |
| `CRON_MANAGER` | `manager` | `crons/manager.py` | Periodic |
| `CRON_HEALTH_CHECK` | `health_check` | `crons/` | Periodic |
| `CRON_MEMORY_CONSOLIDATE` | `memory_consolidate` | `crons/` | Nightly |

---

## 4. Tool Dict Keys

| Constant | Key String | Registered In | Used By |
|---|---|---|---|
| `TOOL_SHELL` | `shell` | `core/agent.py` | tool dispatch |
| `TOOL_WEB` | `web` | `core/agent.py` | tool dispatch |
| `TOOL_BROWSER` | `browser` | `core/agent.py` | tool dispatch |
| `TOOL_MEMORY` | `memory` | `core/agent.py` | tool dispatch |
| `TOOL_FILE` | `file` | `core/agent.py` | tool dispatch |
| `TOOL_CODE` | `code` | `core/agent.py` | tool dispatch |
| `TOOL_EMAIL` | `email` | `core/agent.py` | tool dispatch |
| `TOOL_SYSTEM` | `system` | `core/agent.py` | tool dispatch |
| `TOOL_OPENCODE` | `opencode` | `core/agent.py` | tool dispatch |

---

## 5. Telegram Commands

| Constant | Command | Handler |
|---|---|---|
| `CMD_START` | `/start` | `interfaces/telegram_interface.py` |
| `CMD_STATUS` | `/status` | `interfaces/telegram_interface.py` |
| `CMD_HELP` | `/help` | `interfaces/telegram_interface.py` |
| `CMD_REMIND` | `/remind` | `interfaces/telegram_interface.py` |
| `CMD_MEMORY` | `/memory` | `interfaces/telegram_interface.py` |
| `CMD_TASK` | `/task` | `interfaces/telegram_interface.py` |
| `CMD_CANCEL` | `/cancel` | `interfaces/telegram_interface.py` |
| `CMD_MODEL` | `/model` | `interfaces/telegram_interface.py` |
| `CMD_CRON` | `/cron` | `interfaces/telegram_interface.py` |
| `CMD_RESET` | `/reset` | `interfaces/telegram_interface.py` |

---

## 6. Key File Paths

| Constant | Path | Purpose |
|---|---|---|
| `PATH_ENV` | `.env` | Main secrets file |
| `PATH_ENV_LOCAL` | `.env.local` | Local overrides |
| `PATH_NINA_INDEX` | `docs/space/nina_index.json` | File index SSOT |
| `PATH_FILE_REGISTRY` | `docs/space/nina_file_registry.json` | File registry |
| `PATH_CONTRACT` | `docs/space/nina_contract.md` | **This file** |
| `PATH_JULES_BACKLOG` | `docs/space/jules_backlog.md` | Jules task queue |
| `PATH_ERROR_REGISTER` | `docs/space/nina_error_register.md` | Error log |
| `PATH_JULES_REGISTRY` | `data/jules_registry.json` | Jules activity |
| `PATH_CRON_RESULTS` | `data/cron_results.json` | Cron run results |
| `PATH_CAPABILITIES` | `data/capabilities.yaml` | Capability store |

---

## 7. Known Mismatches Fixed in This Commit

| What was wrong | Where | Fixed |
|---|---|---|
| `TELEGRAMCHATID` alias in `load_config()` | `core/config.py` | Removed — use `TELEGRAM_CHAT_ID` only |
| Hardcoded string `"TELEGRAMCHATID"` | `core/config.py` | Replaced with `ENV_TELEGRAM_CHAT_ID` |
| All 20+ hardcoded env var strings | `core/config.py` | Replaced with constants imports |
| Logger string `"nina.config"` hardcoded | `core/config.py` | Replaced with `LOG_CONFIG` |

---

## 8. Pending — Files That Still Hardcode Connectors

These files need to be updated to import from `core/constants.py`:

| File | Hardcoded Connector | Should Use |
|---|---|---|
| `interfaces/telegram_interface.py` | `"nina.telegram"` logger string | `LOG_TELEGRAM` |
| `interfaces/telegram_interface.py` | `send_message()` uses `authorized_user_id` as chat_id | `config.telegram_chat_id` |
| `core/agent.py` | tool key strings `"shell"`, `"web"` etc | `TOOL_SHELL`, `TOOL_WEB` |
| `crons/backup_jobs.py` | `id='backup_jobs'` | `CRON_BACKUP_JOBS` |
| `crons/nexus_evolution.py` | `id='nexus_evolution'` | `CRON_NEXUS_EVOLUTION` |
| `interfaces/middleware.py` | command string literals | `CMD_*` constants |
| `tools/ninagate/main.py` | provider key strings | `PROVIDER_*` constants |
| `.env.local.template` | still lists `TELEGRAMCHATID=` as alias | Remove alias row |

> Jules: pick items from Section 8 as P2 tasks.
> Perplexity: validate this table is current before any new connector is added.

---

*Last updated: 2026-06-22 by Architect Overwatch (Perplexity/NINA)*
