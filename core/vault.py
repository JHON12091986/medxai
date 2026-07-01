"""NINA credential vault — thin compatibility shim over core.key_resolver.

All secret resolution is now delegated to KeyResolver (6-layer waterfall).
This module keeps its existing public surface intact so every other file
that does  ``from core.vault import get_secret, init_vault``  keeps working
without a single import change.

Resolution order (handled entirely by KeyResolver):
  1. os.environ          (highest — in-process patches, test fixtures)
  2. .env.local          (machine-local overrides, git-ignored)
  3. .env                (repo baseline)
  4. data/secrets.json   (runtime-persisted via /setkey command)
  5. AUTO-GENERATE       (API_SECRET_KEY only — creates & saves)
  6. KeyResolutionError  (hard fail with fix instructions)
"""
import logging
import os
import sys
import threading
from pathlib import Path
from typing import Optional, Dict
from core.constants import (
    ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID,
    ENV_API_SECRET_KEY, ENV_OPENAI_API_KEY, ENV_CEREBRAS_API_KEY,
    ENV_GROQ_API_KEY, ENV_GEMINI_API_KEY, ENV_MISTRAL_API_KEY,
    ENV_OPENROUTER_API_KEY, ENV_DEEPSEEK_API_KEY, ENV_PERPLEXITY_API_KEY,
    ENV_TOGETHER_API_KEY, ENV_COHERE_API_KEY, ENV_FIREWORKS_API_KEY,
    ENV_XAI_API_KEY, ENV_SAMBANOVA_API_KEY, ENV_HYPERBOLIC_API_KEY,
    ENV_NOVITA_API_KEY, ENV_OLLAMA_HOST,
    ENV_EWS_USERNAME, ENV_EWS_MY_EMAIL, ENV_EWS_SHARED_EMAIL,
)

logger = logging.getLogger("nina.vault")


# ---------------------------------------------------------------------------
# CredentialVault — singleton kept for callers that import the class directly
# ---------------------------------------------------------------------------

class CredentialVault:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._secrets: Dict[str, str] = {}
        self._lock = threading.Lock()
        self._initialized = True

    def initialize(self, secrets_dict: Optional[Dict[str, str]] = None):
        """Seed vault memory — called by init_vault() after resolver loads env."""
        with self._lock:
            self._secrets.clear()
            if secrets_dict:
                self._secrets.update(secrets_dict)

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve via resolver (6-layer waterfall), fall back to default."""
        try:
            from core.key_resolver import resolver
            val = resolver.get(key, required=False)
            if val is not None:
                return val
        except Exception:
            pass
        with self._lock:
            if key in self._secrets:
                return self._secrets[key]
        return os.environ.get(key, default)

    @classmethod
    def get_instance(cls) -> "CredentialVault":
        return cls()


# ---------------------------------------------------------------------------
# Module-level _SECRETS dict — kept for legacy callers that do
#   from core.vault import _SECRETS
# ---------------------------------------------------------------------------

_SECRETS: Dict[str, str] = {}


def _resolve_aliases() -> None:
    """Normalise deprecated alias env keys → TELEGRAM_CHAT_ID.

    Alias promotion is now also handled inside KeyResolver; this function
    remains here so vault.init_vault() can trigger it early for code that
    reads os.environ directly before the resolver is warm.
    """
    try:
        from core.constants import CHAT_ID_ALIASES, ENV_TELEGRAM_CHAT_ID
    except ImportError:
        CHAT_ID_ALIASES = ["TELEGRAMCHATID", "ALLOWED_USERS", "AUTHORIZED_USER_ID"]
        ENV_TELEGRAM_CHAT_ID = "TELEGRAM_CHAT_ID"

    canonical_val = os.environ.get(ENV_TELEGRAM_CHAT_ID) or _SECRETS.get(ENV_TELEGRAM_CHAT_ID)

    for alias in CHAT_ID_ALIASES:
        alias_val = os.environ.get(alias) or _SECRETS.get(alias)
        if not alias_val:
            continue
        logger.warning(
            "vault.alias_detected key='%s' canonical='%s' — "
            "rename '%s' to '%s' in .env and remove the alias",
            alias, ENV_TELEGRAM_CHAT_ID, alias, ENV_TELEGRAM_CHAT_ID,
        )
        if not canonical_val:
            os.environ[ENV_TELEGRAM_CHAT_ID] = alias_val
            _SECRETS[ENV_TELEGRAM_CHAT_ID] = alias_val
            canonical_val = alias_val
            logger.warning(
                "vault.alias_promoted '%s' → '%s' (value preserved). "
                "Remove '%s' from .env.",
                alias, ENV_TELEGRAM_CHAT_ID, alias,
            )


def init_vault():
    """Initialise resolver + vault singleton.  Safe to call multiple times."""
    if "pytest" in sys.modules:
        return

    # Let the resolver reload all layers (env files + secrets.json)
    try:
        from core.key_resolver import resolver
        resolver.reload()
    except Exception as exc:
        logger.warning("key_resolver.reload failed — falling back to dotenv: %s", exc)
        from dotenv import load_dotenv
        repo_root = Path(__file__).parent.parent.resolve()
        load_dotenv(repo_root / ".env", override=True)
        env_local = repo_root / ".env.local"
        if env_local.exists():
            load_dotenv(env_local, override=True)

    _SECRETS.clear()
    _SECRETS.update(os.environ)

    _resolve_aliases()
    _SECRETS.update(os.environ)

    CredentialVault.get_instance().initialize(_SECRETS)


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Resolve a secret through the 6-layer KeyResolver waterfall.

    Falls back to direct os.environ lookup so pytest env-patching still works.
    """
    # pytest fast path — env patching must win
    if "pytest" in sys.modules:
        val = os.environ.get(key)
        if val is not None:
            return val
        return _SECRETS.get(key, default)

    # Primary path — delegate to resolver
    try:
        from core.key_resolver import resolver
        val = resolver.get(key, required=False)
        if val is not None:
            return val
    except Exception:
        pass

    # Legacy fallback — in-memory _SECRETS dict
    if key in _SECRETS:
        return _SECRETS[key]

    return default
