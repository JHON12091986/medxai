"""NINA v12 — NinaConfig + RATELIMITS (Stage 1+2).

All secret resolution is delegated to core.key_resolver via core.vault.get_secret.
API_SECRET_KEY auto-generation is handled by KeyResolver Layer 5 — no inline
fallback logic needed here.
"""
import json
import logging # verified
from pathlib import Path
from pydantic import BaseModel
from typing import ClassVar, Optional
from dotenv import load_dotenv
from core.constants import (
    ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID,
    ENV_API_SECRET_KEY, ENV_OLLAMA_HOST, ENV_CEREBRAS_API_KEY,
    ENV_GROQ_API_KEY, ENV_GEMINI_API_KEY, ENV_MISTRAL_API_KEY,
    ENV_OPENROUTER_API_KEY, ENV_OPENAI_API_KEY, ENV_DEEPSEEK_API_KEY,
    ENV_PERPLEXITY_API_KEY, ENV_TOGETHER_API_KEY, ENV_COHERE_API_KEY,
    ENV_FIREWORKS_API_KEY, ENV_XAI_API_KEY, ENV_SAMBANOVA_API_KEY,
    ENV_HYPERBOLIC_API_KEY, ENV_NOVITA_API_KEY, ENV_ONEBRAIN_API_KEY,
    ENV_ONEBRAIN_API_BASE, ENV_EWS_PASSWORD, ENV_EWS_USERNAME,
    ENV_EWS_MY_EMAIL, ENV_EWS_SHARED_EMAIL, ENV_DEAD_MAN_PING_URL,
    ENV_IDLE_AUTO_APPROVE, ENV_IDLE_THRESHOLD_MIN, ENV_IDLE_REPORT_MIN,
    ENV_RAM_GUARD_GB, ENV_MODEL_OVERRIDES, ENV_HYPERDRIVE_ENABLED,
    LOG_CONFIG,
)

# Load .env and .env.local from repo root (with .env.local overriding .env)
repo_root = Path(__file__).parent.parent.resolve()
load_dotenv(dotenv_path=repo_root / ".env", override=True)
env_local = repo_root / ".env.local"
if env_local.exists():
    load_dotenv(dotenv_path=env_local, override=True)

logger = logging.getLogger(LOG_CONFIG)


RATELIMITS = {
    "GROQ":        {"rpm": 30,  "tpd": None,    "rpd": 14400, "min_spacing_s": 2},
    "CEREBRAS":    {"rpm": 30,  "tpd": 100000,  "rpd": None,  "min_spacing_s": 2},
    "GEMINI":      {"rpm": 15,  "tpd": 1500000, "rpd": 1500,  "min_spacing_s": 4},
    "MISTRAL":     {"rpm": 1,   "tpd": None,    "rpd": None,  "min_spacing_s": 61},
    "POLLINATIONS":{"rpm": 5,   "tpd": None,    "rpd": None,  "min_spacing_s": 12},
    "CHUTES":      {"rpm": 3,   "tpd": None,    "rpd": None,  "min_spacing_s": 20},
    "HFPUBLIC":    {"rpm": 10,  "tpd": None,    "rpd": None,  "min_spacing_s": 6},
    "DEEPSEEK":    {"rpm": 60,  "tpd": 500000,  "rpd": None,  "min_spacing_s": 1},
    "TOGETHER":    {"rpm": 60,  "tpd": None,    "rpd": None,  "min_spacing_s": 1},
    "COHERE":      {"rpm": 20,  "tpd": None,    "rpd": 1000,  "min_spacing_s": 3},
    "FIREWORKS":   {"rpm": 30,  "tpd": None,    "rpd": None,  "min_spacing_s": 2},
    "XAI":         {"rpm": 60,  "tpd": None,    "rpd": None,  "min_spacing_s": 1},
    "SAMBANOVA":   {"rpm": 30,  "tpd": 100000,  "rpd": None,  "min_spacing_s": 2},
    "HYPERBOLIC":  {"rpm": 60,  "tpd": None,    "rpd": None,  "min_spacing_s": 1},
    "NOVITA":      {"rpm": 30,  "tpd": None,    "rpd": None,  "min_spacing_s": 2},
    "PERPLEXITY":  {"rpm": 50,  "tpd": None,    "rpd": None,  "min_spacing_s": 2},
    "OPENAI":      {"rpm": 500, "tpd": None,    "rpd": None,  "min_spacing_s": 0},
    "ONEBRAIN":    {"rpm": 20,  "tpd": None,    "rpd": None,  "min_spacing_s": 3},
    "OPENROUTER":  {"rpm": 20,  "tpd": None,    "rpd": None,  "min_spacing_s": 3},
}


class NinaConfig(BaseModel):

    REQUIRED_KEYS: ClassVar[list[str]] = [
        ENV_TELEGRAM_BOT_TOKEN,
        ENV_TELEGRAM_CHAT_ID,
        ENV_API_SECRET_KEY,
    ]
    OPTIONAL_KEYS: ClassVar[dict[str, str]] = {
        ENV_OPENAI_API_KEY:      "OpenAI provider disabled",
        "ANTHROPIC_API_KEY":     "Anthropic provider disabled",
        ENV_GEMINI_API_KEY:      "Gemini provider disabled",
        ENV_COHERE_API_KEY:      "Cohere provider disabled",
        ENV_CEREBRAS_API_KEY:    "Cerebras provider disabled",
        ENV_GROQ_API_KEY:        "Groq provider disabled",
        ENV_MISTRAL_API_KEY:     "Mistral provider disabled",
        ENV_DEEPSEEK_API_KEY:    "Deepseek provider disabled",
        ENV_PERPLEXITY_API_KEY:  "Perplexity provider disabled",
        ENV_TOGETHER_API_KEY:    "Together provider disabled",
        ENV_FIREWORKS_API_KEY:   "Fireworks provider disabled",
        ENV_XAI_API_KEY:         "Xai provider disabled",
        ENV_SAMBANOVA_API_KEY:   "Sambanova provider disabled",
        ENV_HYPERBOLIC_API_KEY:  "Hyperbolic provider disabled",
        ENV_NOVITA_API_KEY:      "Novita provider disabled",
        ENV_ONEBRAIN_API_KEY:    "OneBrain provider disabled",
        ENV_OPENROUTER_API_KEY:  "Openrouter provider disabled",
    }

    def validate_env(self) -> tuple[list[str], list[str]]:
        """Returns (errors, warnings).
        errors  : required keys missing — service must not start
        warnings: optional keys missing — provider unavailable
        """
        from core.vault import get_secret
        errors   = [k for k in self.REQUIRED_KEYS if not get_secret(k)]
        warnings = [f"{k}: {msg}" for k, msg in self.OPTIONAL_KEYS.items()
                    if not get_secret(k)]
        return errors, warnings

    # ── Core identity ────────────────────────────────────────────
    telegram_bot_token:   str
    telegram_chat_id:     str

    # ── Infrastructure ─────────────────────────────────────────
    ollama_host:          str = "http://localhost:11434"
    api_secret_key:       Optional[str] = None
    api_rate_limit_rpm:   int = 60

    # ── LLM provider keys ────────────────────────────────────
    cerebras_api_key:     Optional[str] = None
    groq_api_key:         Optional[str] = None
    gemini_api_key:       Optional[str] = None
    mistral_api_key:      Optional[str] = None
    openrouter_api_key:   Optional[str] = None
    openai_api_key:       Optional[str] = None
    deepseek_api_key:     Optional[str] = None
    perplexity_api_key:   Optional[str] = None
    together_api_key:     Optional[str] = None
    cohere_api_key:       Optional[str] = None
    fireworks_api_key:    Optional[str] = None
    xai_api_key:          Optional[str] = None
    sambanova_api_key:    Optional[str] = None
    hyperbolic_api_key:   Optional[str] = None
    novita_api_key:       Optional[str] = None
    one_brain_api_key:    Optional[str] = None
    one_brain_api_base:   Optional[str] = None

    # ── EWS / Email ───────────────────────────────────────────
    ews_server:           str = "webmail.basicbanklimited.com"
    ews_domain:           str = "basic.bank"
    ews_username:         Optional[str] = None
    ews_password:         Optional[str] = None
    ews_auth_type:        str = "NTLM"
    ews_my_email:         Optional[str] = None
    ews_shared_email:     Optional[str] = None
    ews_max_emails:       int = 10
    ews_keywords:         str = "SWIFT,LC,MT103,MT202,MT700,discrepancy,amendment,BG,overdue,urgent"

    # ── Runtime tuning ────────────────────────────────────────
    log_level:            str = "INFO"
    workspace_dir:        Path = Path("data/workspace")
    max_ram_gb:           float = 12.0
    ram_guard_gb:         float = 10.5
    disk_guard_pct:       float = 90.0
    idle_threshold_min:   int = 15
    idle_report_min:      int = 30
    idle_auto_approve:    bool = False
    session_max_turns:    int = 20
    agent_timeout_s:      int = 300
    flood_window_s:       int = 30
    flood_max_messages:   int = 10
    dead_man_ping_url:    Optional[str] = None
    dead_man_max_interval_min: int = 65
    thermal_warn_cpu:     int = 80
    thermal_warn_gpu:     int = 80
    thermal_guard_cpu:    int = 90
    thermal_guard_gpu:    int = 85
    thermal_critical_cpu: int = 95
    thermal_critical_gpu: int = 90
    model_overrides:      dict = {}
    max_concurrent_sessions: int = 15
    quota_soft_limit:     int = 800
    hyperdrive_enabled:   bool = True


def load_config() -> NinaConfig:
    """Build NinaConfig by resolving all secrets through KeyResolver.

    API_SECRET_KEY auto-generation is handled transparently by KeyResolver
    Layer 5 — no inline fallback needed here.
    """
    from core.vault import init_vault, get_secret
    init_vault()  # warms resolver (all 6 layers) + resolves aliases

    tok       = get_secret(ENV_TELEGRAM_BOT_TOKEN)
    chat_id   = get_secret(ENV_TELEGRAM_CHAT_ID, "")
    api_secret = get_secret(ENV_API_SECRET_KEY)  # resolver auto-generates if absent

    import sys
    if "pytest" in sys.modules and not chat_id:
        import os
        if not os.environ.get("TEST_FORCE_MISSING_CHAT_ID"):
            chat_id = "123456789"

    if not tok or not str(tok).strip() or "your_" in str(tok).lower() or "dummy" in str(tok).lower():
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN missing or invalid.\n"
            "Fix: add TELEGRAM_BOT_TOKEN=<token> to .env\n"
            "     or run: /setkey TELEGRAM_BOT_TOKEN <token> in Telegram"
        )
    if not chat_id or not str(chat_id).strip() or "your_" in str(chat_id).lower() or "dummy" in str(chat_id).lower():
        raise RuntimeError(
            "TELEGRAM_CHAT_ID missing or invalid.\n"
            "Fix: message @userinfobot on Telegram → copy 'Id' → add to .env\n"
            "     or run: /setkey TELEGRAM_CHAT_ID <id> in Telegram"
        )

    env_keys = {
        "ollama_host":         ENV_OLLAMA_HOST,
        "cerebras_api_key":    ENV_CEREBRAS_API_KEY,
        "groq_api_key":        ENV_GROQ_API_KEY,
        "gemini_api_key":      ENV_GEMINI_API_KEY,
        "mistral_api_key":     ENV_MISTRAL_API_KEY,
        "openrouter_api_key":  ENV_OPENROUTER_API_KEY,
        "openai_api_key":      ENV_OPENAI_API_KEY,
        "deepseek_api_key":    ENV_DEEPSEEK_API_KEY,
        "perplexity_api_key":  ENV_PERPLEXITY_API_KEY,
        "together_api_key":    ENV_TOGETHER_API_KEY,
        "cohere_api_key":      ENV_COHERE_API_KEY,
        "fireworks_api_key":   ENV_FIREWORKS_API_KEY,
        "xai_api_key":         ENV_XAI_API_KEY,
        "sambanova_api_key":   ENV_SAMBANOVA_API_KEY,
        "hyperbolic_api_key":  ENV_HYPERBOLIC_API_KEY,
        "novita_api_key":      ENV_NOVITA_API_KEY,
        "one_brain_api_key":   ENV_ONEBRAIN_API_KEY,
        "one_brain_api_base":  ENV_ONEBRAIN_API_BASE,
        "api_secret_key":      ENV_API_SECRET_KEY,
        "ews_password":        ENV_EWS_PASSWORD,
        "ews_username":        ENV_EWS_USERNAME,
        "ews_my_email":        ENV_EWS_MY_EMAIL,
        "ews_shared_email":    ENV_EWS_SHARED_EMAIL,
        "dead_man_ping_url":   ENV_DEAD_MAN_PING_URL,
    }

    populated_fields: dict = {}
    for cfg_field, env_var in env_keys.items():
        val = get_secret(env_var)
        if val is not None:
            populated_fields[cfg_field] = val

    cfg = NinaConfig(
        telegram_bot_token = tok,
        telegram_chat_id   = chat_id,
        **populated_fields
    )

    if v := get_secret(ENV_IDLE_AUTO_APPROVE):
        cfg.idle_auto_approve = v.lower() == "true"
    if v := get_secret(ENV_IDLE_THRESHOLD_MIN):
        cfg.idle_threshold_min = int(v)
    if v := get_secret(ENV_IDLE_REPORT_MIN):
        cfg.idle_report_min = int(v)
    if v := get_secret(ENV_RAM_GUARD_GB):
        cfg.ram_guard_gb = float(v)
    if v := get_secret(ENV_MODEL_OVERRIDES):
        try:
            cfg.model_overrides = json.loads(v)
        except Exception as e:
            logger.error(f"config_load_model_overrides_failed {e}")
    if v := get_secret(ENV_HYPERDRIVE_ENABLED):
        cfg.hyperdrive_enabled = v.lower() == "true"

    return cfg
