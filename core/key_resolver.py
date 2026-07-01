"""
core/key_resolver.py — NINA Permanent API Key Resolver
======================================================
Single source of truth for ALL credential resolution.

Resolution order (first non-empty wins):
  1. os.environ (in-process, highest priority — covers test patches)
  2. .env.local  (machine-local overrides, git-ignored)
  3. .env        (repo baseline)
  4. data/secrets.json  (persisted fallback; written by /setkey Telegram cmd)
  5. Auto-generate (only for API_SECRET_KEY — creates & persists to secrets.json)
  6. HARD_FAIL — raises KeyResolutionError with exact remediation message

Usage:
    from core.key_resolver import resolver
    token = resolver.get("TELEGRAM_BOT_TOKEN")        # raises on missing required
    key   = resolver.get("GROQ_API_KEY", required=False)  # None if missing
    resolver.set("GROQ_API_KEY", "gsk_...")           # persist to secrets.json
    report = resolver.audit()                         # full visibility table

All resolution events are logged to logs/key_resolver.log (JSON lines).
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values

logger = logging.getLogger("nina.key_resolver")

# ── Paths ─────────────────────────────────────────────────────────────────────
_REPO_ROOT    = Path(__file__).parent.parent.resolve()
_DOT_ENV      = _REPO_ROOT / ".env"
_DOT_ENV_LOCAL = _REPO_ROOT / ".env.local"
_SECRETS_JSON = _REPO_ROOT / "data" / "secrets.json"
_RESOLVER_LOG = _REPO_ROOT / "logs" / "key_resolver.log"

# ── Key catalogue ─────────────────────────────────────────────────────────────
# Format: key → {required, auto_generate, description, aliases}
KEY_CATALOGUE: dict[str, dict] = {
    # ── REQUIRED — service won't start without these ────────────────────────
    "TELEGRAM_BOT_TOKEN": {
        "required": True,
        "auto_generate": False,
        "description": "Telegram Bot API token (from @BotFather)",
        "aliases": ["TELEGRAM_TOKEN"],
        "remediation": "Get from @BotFather on Telegram → /newbot → copy token → add to .env",
    },
    "TELEGRAM_CHAT_ID": {
        "required": True,
        "auto_generate": False,
        "description": "Your personal Telegram chat/user ID",
        "aliases": ["TELEGRAMCHATID", "AUTHORIZED_USER_ID", "ALLOWED_USERS"],
        "remediation": "Message @userinfobot on Telegram → copy 'Id' number → add to .env",
    },
    "API_SECRET_KEY": {
        "required": True,
        "auto_generate": True,    # ← auto-generates & persists if missing
        "description": "NINA HTTP API bearer token (ninagate + internal auth)",
        "aliases": ["NINA_API_KEY", "SECRET_KEY"],
        "remediation": "Auto-generated on first boot. Check data/secrets.json or logs/key_resolver.log",
    },
    # ── OPTIONAL LLM PROVIDERS — degraded but functional if absent ──────────
    "GROQ_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Groq LPU inference (Tier-1 fast provider)",
        "aliases": [],
        "remediation": "https://console.groq.com → API Keys → Create Key",
    },
    "GEMINI_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Google Gemini (aggregator + quality tier)",
        "aliases": ["GOOGLE_API_KEY"],
        "remediation": "https://aistudio.google.com/app/apikey",
    },
    "CEREBRAS_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Cerebras inference",
        "aliases": [],
        "remediation": "https://cloud.cerebras.ai → API Keys",
    },
    "MISTRAL_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Mistral AI provider",
        "aliases": [],
        "remediation": "https://console.mistral.ai → API Keys",
    },
    "OPENROUTER_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "OpenRouter multi-provider gateway",
        "aliases": [],
        "remediation": "https://openrouter.ai/keys",
    },
    "OPENAI_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "OpenAI (currently dummy 'nina' value — non-functional)",
        "aliases": [],
        "remediation": "https://platform.openai.com/api-keys",
    },
    "DEEPSEEK_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "DeepSeek provider",
        "aliases": [],
        "remediation": "https://platform.deepseek.com/api_keys",
    },
    "PERPLEXITY_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Perplexity sonar provider",
        "aliases": [],
        "remediation": "https://www.perplexity.ai/settings/api",
    },
    "TOGETHER_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Together AI provider",
        "aliases": [],
        "remediation": "https://api.together.xyz/settings/api-keys",
    },
    "COHERE_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Cohere provider",
        "aliases": [],
        "remediation": "https://dashboard.cohere.com/api-keys",
    },
    "FIREWORKS_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Fireworks AI provider",
        "aliases": [],
        "remediation": "https://fireworks.ai/account/api-keys",
    },
    "XAI_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "xAI Grok provider",
        "aliases": [],
        "remediation": "https://console.x.ai/",
    },
    "SAMBANOVA_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "SambaNova provider",
        "aliases": [],
        "remediation": "https://cloud.sambanova.ai/apis",
    },
    "HYPERBOLIC_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Hyperbolic provider",
        "aliases": [],
        "remediation": "https://app.hyperbolic.xyz/settings",
    },
    "NOVITA_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "Novita AI provider",
        "aliases": [],
        "remediation": "https://novita.ai/settings/key-management",
    },
    "ONEBRAIN_API_KEY": {
        "required": False,
        "auto_generate": False,
        "description": "OneBrain provider key",
        "aliases": [],
        "remediation": "Contact OneBrain for API key",
    },
    "ONEBRAIN_API_BASE": {
        "required": False,
        "auto_generate": False,
        "description": "OneBrain provider base URL",
        "aliases": [],
        "remediation": "Contact OneBrain for API base URL",
    },
    # ── EWS / Email ─────────────────────────────────────────────────────────
    "EWS_USERNAME": {
        "required": False,
        "auto_generate": False,
        "description": "BASIC Bank EWS username (NTLM)",
        "aliases": [],
        "remediation": "Your BASIC Bank Windows domain username",
    },
    "EWS_PASSWORD": {
        "required": False,
        "auto_generate": False,
        "description": "BASIC Bank EWS password",
        "aliases": [],
        "remediation": "Your BASIC Bank Windows domain password",
    },
    "EWS_MY_EMAIL": {
        "required": False,
        "auto_generate": False,
        "description": "Your BASIC Bank email address",
        "aliases": [],
        "remediation": "e.g. malam@basicbanklimited.com",
    },
    "EWS_SHARED_EMAIL": {
        "required": False,
        "auto_generate": False,
        "description": "Shared mailbox address to monitor",
        "aliases": [],
        "remediation": "Shared mailbox address at BASIC Bank",
    },
}

# ── Dummy / invalid value patterns ────────────────────────────────────────────
_INVALID_PATTERNS = (
    "your_", "dummy", "placeholder", "changeme",
    "<your", "example", "xxx", "todo",
)


def _is_valid_value(val: str | None) -> bool:
    """Returns False for None, empty, or well-known placeholder strings."""
    if not val or not str(val).strip():
        return False
    v = val.strip().lower()
    return not any(p in v for p in _INVALID_PATTERNS)


class KeyResolutionError(RuntimeError):
    """Raised when a required key cannot be resolved from any source."""
    pass


class KeyResolver:
    """
    Singleton key resolver.
    Thread-safe. Lazy-loads secrets.json on first access.
    """

    _instance: "KeyResolver | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "KeyResolver":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._cache: dict[str, str] = {}   # resolved values, in-process cache
        self._json_secrets: dict[str, str] = {}
        self._env_values: dict[str, str] = {}
        self._env_local_values: dict[str, str] = {}
        self._loaded = False
        self._initialized = True

    # ── Public API ─────────────────────────────────────────────────────────

    def get(self, key: str, required: bool | None = None, default: str | None = None) -> str | None:
        """
        Resolve a key through the full contingency chain.

        Args:
            key:      Environment variable name.
            required: Override KEY_CATALOGUE required flag. None = use catalogue.
            default:  Return this if key is optional and not found.

        Returns:
            Resolved value string, or None/default if optional.

        Raises:
            KeyResolutionError: If key is required and cannot be resolved.
        """
        self._ensure_loaded()

        # In-process cache hit
        if key in self._cache:
            return self._cache[key]

        meta = KEY_CATALOGUE.get(key, {})
        is_required = required if required is not None else meta.get("required", False)
        aliases = meta.get("aliases", [])

        # Resolution chain — try key + all aliases at each layer
        all_keys = [key] + aliases
        value = None
        source = None

        # Layer 1: os.environ (in-process, highest priority)
        for k in all_keys:
            v = os.environ.get(k)
            if _is_valid_value(v):
                value, source = v, f"os.environ[{k}]"
                break

        # Layer 2: .env.local
        if value is None:
            for k in all_keys:
                v = self._env_local_values.get(k)
                if _is_valid_value(v):
                    value, source = v, f".env.local[{k}]"
                    break

        # Layer 3: .env
        if value is None:
            for k in all_keys:
                v = self._env_values.get(k)
                if _is_valid_value(v):
                    value, source = v, f".env[{k}]"
                    break

        # Layer 4: data/secrets.json
        if value is None:
            for k in all_keys:
                v = self._json_secrets.get(k)
                if _is_valid_value(v):
                    value, source = v, f"secrets.json[{k}]"
                    break

        # Layer 5: Auto-generate (only for API_SECRET_KEY)
        if value is None and meta.get("auto_generate") and key == "API_SECRET_KEY":
            value = secrets.token_urlsafe(32)
            source = "auto_generated"
            self._persist_to_json(key, value)
            logger.warning("key_resolver: AUTO-GENERATED %s → persisted to data/secrets.json", key)

        # Layer 6: Hard fail or default
        if value is None:
            if is_required:
                remediation = meta.get("remediation", f"Add {key} to .env")
                self._log_event(key, "HARD_FAIL", None)
                raise KeyResolutionError(
                    f"\n"
                    f"  NINA cannot start: required key '{key}' is missing.\n"
                    f"  Description : {meta.get('description', 'N/A')}\n"
                    f"  Aliases     : {aliases or 'none'}\n"
                    f"  Fix         : {remediation}\n"
                    f"  Sources tried: os.environ → .env.local → .env → data/secrets.json\n"
                )
            self._log_event(key, "MISSING_OPTIONAL", None)
            return default

        # Promote canonical key to os.environ so all downstream code finds it
        os.environ[key] = value
        self._cache[key] = value
        self._log_event(key, "RESOLVED", source)
        return value

    def set(self, key: str, value: str) -> None:
        """
        Persist a key to data/secrets.json and update in-process cache.
        Called by Telegram /setkey command or admin tools.
        """
        self._ensure_loaded()
        self._persist_to_json(key, value)
        os.environ[key] = value
        self._cache[key] = value
        self._log_event(key, "SET_RUNTIME", "telegram_cmd")
        logger.info("key_resolver: SET %s via runtime API → persisted", key)

    def audit(self) -> str:
        """
        Returns a full visibility table of ALL keys in KEY_CATALOGUE.
        Safe to print — values are masked.
        """
        self._ensure_loaded()
        lines = [
            "",
            "╔══════════════════════════════════════════════════════════════════════╗",
            "║              NINA KEY RESOLVER — FULL AUDIT REPORT                  ║",
            f"║  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}                              ║",
            "╠══════════════╤══════════╤══════════╤════════════════════════════════╣",
            "║ KEY          │ REQUIRED │ STATUS   │ SOURCE                         ║",
            "╠══════════════╪══════════╪══════════╪════════════════════════════════╣",
        ]

        required_missing = []
        optional_missing = []

        for key, meta in KEY_CATALOGUE.items():
            is_req = meta.get("required", False)
            try:
                val = self.get(key, required=False)
            except Exception:
                val = None

            if _is_valid_value(val):
                status = "✅ OK"
                source = self._find_source(key, meta.get("aliases", []))
                masked = self._mask(val)
            else:
                status = "🔴 MISSING" if is_req else "⚪ absent"
                source = "—"
                masked = ""
                if is_req:
                    required_missing.append(key)
                else:
                    optional_missing.append(key)

            req_label = "REQUIRED" if is_req else "optional"
            lines.append(
                f"║ {key:<12} │ {req_label:<8} │ {status:<8} │ {source:<30} ║"
            )

        lines += [
            "╚══════════════╧══════════╧══════════╧════════════════════════════════╝",
            "",
        ]

        if required_missing:
            lines.append(f"  ❌ BLOCKERS ({len(required_missing)}): {', '.join(required_missing)}")
            for key in required_missing:
                rem = KEY_CATALOGUE[key].get("remediation", "")
                lines.append(f"     → {key}: {rem}")
            lines.append("")

        if optional_missing:
            lines.append(f"  ⚠️  Optional missing ({len(optional_missing)}): {', '.join(optional_missing)}")
            lines.append("     Providers for these keys will be skipped during routing.")
            lines.append("")

        if not required_missing:
            lines.append("  ✅ All required keys resolved — NINA can start.")
            lines.append("")

        return "\n".join(lines)

    def reload(self) -> None:
        """Force reload all file sources. Clears in-process cache."""
        self._loaded = False
        self._cache.clear()
        self._json_secrets.clear()
        self._env_values.clear()
        self._env_local_values.clear()
        self._ensure_loaded()
        logger.info("key_resolver: reloaded all sources")

    # ── Internal helpers ───────────────────────────────────────────────────

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        with self._lock:
            if self._loaded:
                return
            self._load_all()
            self._loaded = True

    def _load_all(self) -> None:
        """Load .env, .env.local, and data/secrets.json into memory."""
        # .env
        if _DOT_ENV.exists():
            try:
                self._env_values = {k: v for k, v in dotenv_values(_DOT_ENV).items() if v}
            except Exception as e:
                logger.error("key_resolver: failed to load .env: %s", e)

        # .env.local
        if _DOT_ENV_LOCAL.exists():
            try:
                self._env_local_values = {k: v for k, v in dotenv_values(_DOT_ENV_LOCAL).items() if v}
            except Exception as e:
                logger.error("key_resolver: failed to load .env.local: %s", e)

        # data/secrets.json
        self._json_secrets = self._load_json_secrets()

    def _load_json_secrets(self) -> dict[str, str]:
        if not _SECRETS_JSON.exists():
            return {}
        try:
            raw = json.loads(_SECRETS_JSON.read_text(encoding="utf-8"))
            return {k: v for k, v in raw.items() if isinstance(v, str) and v}
        except Exception as e:
            logger.error("key_resolver: failed to load data/secrets.json: %s", e)
            return {}

    def _persist_to_json(self, key: str, value: str) -> None:
        _SECRETS_JSON.parent.mkdir(parents=True, exist_ok=True)
        existing = self._load_json_secrets()
        existing[key] = value
        try:
            _SECRETS_JSON.write_text(
                json.dumps(existing, indent=2),
                encoding="utf-8",
            )
            self._json_secrets = existing
        except Exception as e:
            logger.error("key_resolver: failed to write data/secrets.json: %s", e)

    def _find_source(self, key: str, aliases: list[str]) -> str:
        """Identify which source layer a key came from (for audit display)."""
        all_keys = [key] + aliases
        for k in all_keys:
            if os.environ.get(k) and _is_valid_value(os.environ.get(k)):
                return f"os.environ[{k}]"
        for k in all_keys:
            if self._env_local_values.get(k):
                return f".env.local[{k}]"
        for k in all_keys:
            if self._env_values.get(k):
                return f".env[{k}]"
        for k in all_keys:
            if self._json_secrets.get(k):
                return f"secrets.json[{k}]"
        return "auto_gen / unknown"

    @staticmethod
    def _mask(val: str) -> str:
        """Show first 4 chars + asterisks. Safe for logs."""
        if not val or len(val) < 5:
            return "****"
        return val[:4] + "*" * min(len(val) - 4, 20)

    def _log_event(self, key: str, event: str, source: str | None) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
            "key": key,
            "event": event,
            "source": source,
        }
        try:
            _RESOLVER_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(_RESOLVER_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass


# ── Module-level singleton ─────────────────────────────────────────────────────
resolver = KeyResolver()


def get_key(key: str, required: bool | None = None, default: str | None = None) -> str | None:
    """Convenience alias for resolver.get()."""
    return resolver.get(key, required=required, default=default)


def set_key(key: str, value: str) -> None:
    """Convenience alias for resolver.set(). Called by /setkey Telegram command."""
    resolver.set(key, value)


def audit_keys() -> str:
    """Return the full audit report string."""
    return resolver.audit()
