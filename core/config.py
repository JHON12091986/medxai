"""NINA v12 — NinaConfig + RATELIMITS (Stage 1+2)."""
import os
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

RATELIMITS = {
    "GROQ":       {"rpm":30,  "tpd":None,    "rpd":14400, "min_spacing_s":2},
    "CEREBRAS":   {"rpm":30,  "tpd":100000,  "rpd":None,  "min_spacing_s":2},
    "GEMINI":     {"rpm":15,  "tpd":1500000, "rpd":1500,  "min_spacing_s":4},
    "MISTRAL":    {"rpm":1,   "tpd":None,    "rpd":None,  "min_spacing_s":61},
    "POLLINATIONS":{"rpm":5,  "tpd":None,    "rpd":None,  "min_spacing_s":12},
    "CHUTES":     {"rpm":3,   "tpd":None,    "rpd":None,  "min_spacing_s":20},
    "HFPUBLIC":   {"rpm":10,  "tpd":None,    "rpd":None,  "min_spacing_s":6},
    "DEEPSEEK":   {"rpm":60,  "tpd":500000,  "rpd":None,  "min_spacing_s":1},
    "TOGETHER":   {"rpm":60,  "tpd":None,    "rpd":None,  "min_spacing_s":1},
    "COHERE":     {"rpm":20,  "tpd":None,    "rpd":1000,  "min_spacing_s":3},
    "FIREWORKS":  {"rpm":30,  "tpd":None,    "rpd":None,  "min_spacing_s":2},
    "XAI":        {"rpm":60,  "tpd":None,    "rpd":None,  "min_spacing_s":1},
    "SAMBANOVA":  {"rpm":30,  "tpd":100000,  "rpd":None,  "min_spacing_s":2},
    "HYPERBOLIC": {"rpm":60,  "tpd":None,    "rpd":None,  "min_spacing_s":1},
    "NOVITA":     {"rpm":30,  "tpd":None,    "rpd":None,  "min_spacing_s":2},
    "PERPLEXITY": {"rpm":50,  "tpd":None,    "rpd":None,  "min_spacing_s":2},
    "OPENAI":     {"rpm":500, "tpd":None,    "rpd":None,  "min_spacing_s":0},
    "ONEBRAIN":   {"rpm":20,  "tpd":None,    "rpd":None,  "min_spacing_s":3},
    "OPENROUTER": {"rpm":20,  "tpd":None,    "rpd":None,  "min_spacing_s":3},
}

class NinaConfig(BaseModel):
    telegram_bot_token:   str
    authorized_user_id:   str
    ollama_host:          str = "http://localhost:11434"
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
    api_secret_key:       Optional[str] = None
    api_rate_limit_rpm:   int = 60
    ews_server:           str = "webmail.basicbanklimited.com"
    ews_domain:           str = "basic.bank"
    ews_username:         Optional[str] = None
    ews_password:         Optional[str] = None
    ews_auth_type:        str = "NTLM"
    ews_my_email:         Optional[str] = None
    ews_shared_email:     Optional[str] = None
    ews_max_emails:       int = 10
    ews_keywords:         str = "SWIFT,LC,MT103,MT202,MT700,discrepancy,amendment,BG,overdue,urgent"
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
    model_overrides: dict = {}

def load_config() -> NinaConfig:
    tok = os.getenv("TELEGRAMBOTTOKEN")
    uid = os.getenv("AUTHORIZEDUSERID")
    if not tok:
        raise RuntimeError("TELEGRAM_BOT_TOKEN missing from .env — cannot start NINA.")
    if not uid:
        raise RuntimeError("AUTHORIZED_USER_ID missing from .env — cannot start NINA.")
    cfg = NinaConfig(
        telegram_bot_token = tok,
        authorized_user_id = uid,
        **{k: os.getenv(v) for k,v in {  # type: ignore  # dynamically populated config fields
            "ollama_host":"OLLAMAHOST","cerebras_api_key":"CEREBRAS_API_KEY",
            "groq_api_key":"GROQ_API_KEY","gemini_api_key":"GEMINI_API_KEY",
            "mistral_api_key":"MISTRAL_API_KEY","openrouter_api_key":"OPENROUTER_API_KEY",
            "openai_api_key":"OPEN_AI_API_KEY","deepseek_api_key":"DEEPSEEK_API_KEY",
            "perplexity_api_key":"PERPLEXITY_API_KEY","together_api_key":"TOGETHER_API_KEY",
            "cohere_api_key":"COHERE_API_KEY","fireworks_api_key":"FIREWORKS_API_KEY",
            "xai_api_key":"XAI_API_KEY","sambanova_api_key":"SAMBANOVA_API_KEY",
            "hyperbolic_api_key":"HYPERBOLIC_API_KEY","novita_api_key":"NOVITA_API_KEY",
            "one_brain_api_key":"ONEBRAINAPIKEY","one_brain_api_base":"ONEBRAINAPIBASE",
            "api_secret_key":"APISECRETKEY","ews_password":"EWSPASSWORD","ews_username":"EWS_USERNAME","ews_my_email":"EWS_MY_EMAIL","ews_shared_email":"EWS_SHARED_EMAIL",
            "dead_man_ping_url":"DEADMANPINGURL",
        }.items() if os.getenv(v)}
    )
    if v := os.getenv("IDLE_AUTO_APPROVE"):
        cfg.idle_auto_approve = v.lower() == "true"
    if v := os.getenv("IDLE_THRESHOLD_MIN"):
        cfg.idle_threshold_min = int(v)
    if v := os.getenv("IDLE_REPORT_MIN"):
        cfg.idle_report_min = int(v)
    return cfg
