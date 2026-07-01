"""NINA SSOT — core/constants.py

SINGLE SOURCE OF TRUTH for every connector name used across the codebase.
This means: env var names, config attribute names, log channel names,
cron job IDs, tool dict keys, Telegram command strings, file paths,
service names, dict keys — anything that links two files together.

RULE: If you add a new connector (env var, function key, job ID, command,
log channel, file path constant), define it HERE first.
No file may hardcode a connector string that is already defined here.

Usage:
    from core.constants import ENV_TELEGRAM_BOT_TOKEN, LOG_AGENT
"""

# =============================================================================
# ENV VAR NAMES  (keys read from .env / vault / os.environ)
# =============================================================================
# Telegram
ENV_TELEGRAM_BOT_TOKEN   = "TELEGRAM_BOT_TOKEN"
ENV_TELEGRAM_CHAT_ID     = "TELEGRAM_CHAT_ID"       # ONE canonical name — no aliases
ENV_API_SECRET_KEY       = "API_SECRET_KEY"
ENV_AUTHORIZED_USER_ID   = "AUTHORIZED_USER_ID"     # alias → vault resolves to TELEGRAM_CHAT_ID
ENV_ALLOWED_USERS        = "ALLOWED_USERS"           # alias → vault resolves to TELEGRAM_CHAT_ID

# ---------------------------------------------------------------------------
# DEAD ALIASES — DO NOT RE-ADD
# These were removed because they all map to the same concept as
# TELEGRAM_CHAT_ID. vault._resolve_aliases() normalises any stale .env
# entries at boot. Remove these keys from .env permanently.
# ---------------------------------------------------------------------------
# ENV_TELEGRAMCHATID      = "TELEGRAMCHATID"        ← DEAD: use ENV_TELEGRAM_CHAT_ID
# ---------------------------------------------------------------------------

# Alias list consumed by core/vault._resolve_aliases() and tools/env_audit.py
CHAT_ID_ALIASES: list[str] = [
    "TELEGRAMCHATID",
    "ALLOWED_USERS",
    "AUTHORIZED_USER_ID",
]

# LLM providers
ENV_OPENAI_API_KEY       = "OPENAI_API_KEY"
ENV_ANTHROPIC_API_KEY    = "ANTHROPIC_API_KEY"
ENV_GEMINI_API_KEY       = "GEMINI_API_KEY"
ENV_GROQ_API_KEY         = "GROQ_API_KEY"
ENV_CEREBRAS_API_KEY     = "CEREBRAS_API_KEY"
ENV_MISTRAL_API_KEY      = "MISTRAL_API_KEY"
ENV_DEEPSEEK_API_KEY     = "DEEPSEEK_API_KEY"
ENV_PERPLEXITY_API_KEY   = "PERPLEXITY_API_KEY"
ENV_TOGETHER_API_KEY     = "TOGETHER_API_KEY"
ENV_COHERE_API_KEY       = "COHERE_API_KEY"
ENV_FIREWORKS_API_KEY    = "FIREWORKS_API_KEY"
ENV_XAI_API_KEY          = "XAI_API_KEY"
ENV_SAMBANOVA_API_KEY    = "SAMBANOVA_API_KEY"
ENV_HYPERBOLIC_API_KEY   = "HYPERBOLIC_API_KEY"
ENV_NOVITA_API_KEY       = "NOVITA_API_KEY"
ENV_OPENROUTER_API_KEY   = "OPENROUTER_API_KEY"
ENV_ONEBRAIN_API_KEY     = "ONEBRAIN_API_KEY"
ENV_ONEBRAIN_API_BASE    = "ONEBRAIN_API_BASE"

# Infrastructure
ENV_OLLAMA_HOST          = "OLLAMA_HOST"            # fixed: was "OLLAMAHOST" (bug)
ENV_DEAD_MAN_PING_URL    = "DEAD_MAN_PING_URL"
ENV_JULES_API_KEY        = "JULES_API_KEY"
ENV_NINAGATE_URL         = "NINAGATE_URL"
ENV_NINAGATE_PORT        = "NINAGATE_PORT"
ENV_NINAGATE_QUOTA_DAILY = "NINAGATE_QUOTA_DAILY"

# EWS / Email
ENV_EWS_SERVER           = "EWS_SERVER"
ENV_EWS_DOMAIN           = "EWS_DOMAIN"
ENV_EWS_AUTH_TYPE        = "EWS_AUTH_TYPE"
ENV_EWS_PASSWORD         = "EWS_PASSWORD"
ENV_EWS_USERNAME         = "EWS_USERNAME"
ENV_EWS_MY_EMAIL         = "EWS_MY_EMAIL"
ENV_EWS_SHARED_EMAIL     = "EWS_SHARED_EMAIL"
ENV_EWS_MAX_EMAILS       = "EWS_MAX_EMAILS"
ENV_EWS_KEYWORDS         = "EWS_KEYWORDS"

# Runtime tuning
ENV_IDLE_AUTO_APPROVE    = "IDLE_AUTO_APPROVE"
ENV_IDLE_THRESHOLD_MIN   = "IDLE_THRESHOLD_MIN"
ENV_IDLE_REPORT_MIN      = "IDLE_REPORT_MIN"
ENV_RAM_GUARD_GB         = "RAM_GUARD_GB"
ENV_MODEL_OVERRIDES      = "MODEL_OVERRIDES"
ENV_HYPERDRIVE_ENABLED   = "HYPERDRIVE_ENABLED"
ENV_WORKSPACE_DIR        = "WORKSPACE_DIR"
ENV_LOG_LEVEL            = "LOG_LEVEL"
ENV_SESSION_MAX_TURNS    = "SESSION_MAX_TURNS"
ENV_AGENT_TIMEOUT_S      = "AGENT_TIMEOUT_S"
ENV_API_RATE_LIMIT_RPM   = "API_RATE_LIMIT_RPM"

# Dead man / thermal
ENV_DEAD_MAN_MAX_INTERVAL_MIN = "DEAD_MAN_MAX_INTERVAL_MIN"
ENV_THERMAL_WARN_CPU     = "THERMAL_WARN_CPU"
ENV_THERMAL_WARN_GPU     = "THERMAL_WARN_GPU"
ENV_THERMAL_GUARD_CPU    = "THERMAL_GUARD_CPU"
ENV_THERMAL_GUARD_GPU    = "THERMAL_GUARD_GPU"
ENV_THERMAL_CRITICAL_CPU = "THERMAL_CRITICAL_CPU"
ENV_THERMAL_CRITICAL_GPU = "THERMAL_CRITICAL_GPU"

# =============================================================================
# CONFIG ATTRIBUTE NAMES  (NinaConfig Pydantic field names)
# =============================================================================
CFG_TELEGRAM_BOT_TOKEN   = "telegram_bot_token"
CFG_TELEGRAM_CHAT_ID     = "telegram_chat_id"       # ONE canonical attr — no aliases
CFG_API_SECRET_KEY       = "api_secret_key"
CFG_ONE_BRAIN_API_KEY    = "one_brain_api_key"
CFG_ONE_BRAIN_API_BASE   = "one_brain_api_base"
# CFG_AUTHORIZED_USER_ID  = "authorized_user_id"   ← DEAD: use CFG_TELEGRAM_CHAT_ID

# =============================================================================
# LOG CHANNEL NAMES  (logger = logging.getLogger(LOG_*))
# =============================================================================
LOG_ROOT                 = "nina"
LOG_CONFIG               = "nina.config"
LOG_AGENT                = "nina.agent"
LOG_TELEGRAM             = "nina.telegram"
LOG_SECURITY             = "nina.security"
LOG_MEMORY               = "nina.memory"
LOG_SCHEDULER            = "nina.scheduler"
LOG_ROUTER               = "nina.router"
LOG_VAULT                = "nina.vault"
LOG_MCP                  = "nina.mcp"
LOG_NINAGATE             = "nina.ninagate"
LOG_CRON                 = "nina.cron"
LOG_GUARD                = "nina.guard"
LOG_COORDINATOR          = "nina.coordinator"

# =============================================================================
# CRON JOB IDs  (CronJob.id values — must match exactly in crons/)
# =============================================================================
CRON_MORNING_REPORT      = "morning_report"
CRON_BACKUP_JOBS         = "backup_jobs"
CRON_NEXUS_EVOLUTION     = "nexus_evolution"
CRON_MANAGER             = "manager"
CRON_HEALTH_CHECK        = "health_check"
CRON_MEMORY_CONSOLIDATE  = "memory_consolidate"

# =============================================================================
# TOOL DICT KEYS  (keys in agent.tools / tool dispatch dicts)
# =============================================================================
TOOL_SHELL               = "shell"
TOOL_WEB                 = "web"
TOOL_BROWSER             = "browser"
TOOL_MEMORY              = "memory"
TOOL_FILE                = "file"
TOOL_CODE                = "code"
TOOL_EMAIL               = "email"
TOOL_CALENDAR            = "calendar"
TOOL_SEARCH              = "search"
TOOL_SYSTEM              = "system"
TOOL_OPENCODE            = "opencode"
TOOL_IMAGE               = "image"

# =============================================================================
# TELEGRAM COMMANDS  (handler registration keys)
# =============================================================================
CMD_START                = "/start"
CMD_STATUS               = "/status"
CMD_HELP                 = "/help"
CMD_REMIND               = "/remind"
CMD_MEMORY               = "/memory"
CMD_TASK                 = "/task"
CMD_CANCEL               = "/cancel"
CMD_MODEL                = "/model"
CMD_CRON                 = "/cron"
CMD_RESET                = "/reset"

# =============================================================================
# SERVICE / SYSTEMD NAMES
# =============================================================================
SERVICE_NINA             = "nina.service"
SERVICE_NINAGATE         = "ninagate.service"

# =============================================================================
# KEY FILE PATHS  (relative to repo root — use Path(REPO_ROOT) / PATH_*)
# =============================================================================
PATH_ENV                 = ".env"
PATH_ENV_LOCAL           = ".env.local"
PATH_ENV_TEMPLATE        = ".env.local.template"
PATH_NINA_INDEX          = "docs/space/nina_index.json"
PATH_FILE_REGISTRY       = "docs/space/nina_file_registry.json"
PATH_CONTRACT            = "docs/space/nina_contract.md"
PATH_JULES_BACKLOG       = "docs/space/jules_backlog.md"
PATH_ERROR_REGISTER      = "docs/space/nina_error_register.md"
PATH_JULES_REGISTRY      = "data/jules_registry.json"
PATH_CRON_RESULTS        = "data/cron_results.json"
PATH_CAPABILITIES        = "data/capabilities.yaml"

# =============================================================================
# SESSION / MEMORY DICT KEYS
# =============================================================================
SESSION_USER_ID          = "user_id"
SESSION_CHAT_ID          = "chat_id"
SESSION_HISTORY          = "history"
SESSION_CONTEXT          = "context"
SESSION_TURN_COUNT       = "turn_count"

# =============================================================================
# PROVIDER TIER KEYS  (used in router fallback chains)
# =============================================================================
PROVIDER_GROQ            = "GROQ"
PROVIDER_CEREBRAS        = "CEREBRAS"
PROVIDER_GEMINI          = "GEMINI"
PROVIDER_MISTRAL         = "MISTRAL"
PROVIDER_OPENAI          = "OPENAI"
PROVIDER_DEEPSEEK        = "DEEPSEEK"
PROVIDER_TOGETHER        = "TOGETHER"
PROVIDER_COHERE          = "COHERE"
PROVIDER_FIREWORKS       = "FIREWORKS"
PROVIDER_XAI             = "XAI"
PROVIDER_SAMBANOVA       = "SAMBANOVA"
PROVIDER_HYPERBOLIC      = "HYPERBOLIC"
PROVIDER_NOVITA          = "NOVITA"
PROVIDER_PERPLEXITY      = "PERPLEXITY"
PROVIDER_OPENROUTER      = "OPENROUTER"
PROVIDER_ONEBRAIN        = "ONEBRAIN"
PROVIDER_POLLINATIONS    = "POLLINATIONS"
PROVIDER_CHUTES          = "CHUTES"
PROVIDER_HFPUBLIC        = "HFPUBLIC"

# Jules (AI coding agent)
ENV_JULES_API_KEY        = "JULES_API_KEY"
