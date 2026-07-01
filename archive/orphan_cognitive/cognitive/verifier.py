"""
NINA Modular Cognitive Layer - Hot-swappable Verifier
"""
from __future__ import annotations
import logging
import re as _re
from typing import Any, Dict, Optional
from .base import BaseVerifier

logger = logging.getLogger("nina.cognitive.verifier")

class CognitiveVerifier(BaseVerifier):
    @property
    def name(self) -> str:
        return "cognitive_verifier"

    @property
    def version(self) -> str:
        return "1.0.0"

    def __init__(self, router: Any = None) -> None:
        self.router = router
        self._seen_answers: list = []

    async def verify(self, code_or_content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        # Deduplication: reject answers identical to a previously rejected one
        _fingerprint = code_or_content.strip()[:120]
        if _fingerprint in self._seen_answers:
            logger.warning("Verifier: duplicate answer detected — forcing revision")
            return False
        self._seen_answers.append(_fingerprint)
        if len(self._seen_answers) > 10:
            self._seen_answers.pop(0)  # keep rolling window of 10

        logger.info("Performing content verification checks")
        if not code_or_content or not code_or_content.strip():
            logger.warning("Verifier: empty content rejected")
            return False
        # Python syntax check
        if metadata and metadata.get("type") == "python":
            try:
                compile(code_or_content, "<string>", "exec")
                logger.info("Python compile verification passed")
                return True
            except Exception as e:
                logger.warning(f"Python compile verification failed: {e}")
                return False
        # General content: reject known failure patterns
        FAILURE_PATTERNS = [
            "i cannot", "i am unable", "as an ai", "i don't have access",
            "no answer generated", "failed due to error", "[tool error]",
            "[tool_failed:", "[no dispatcher]", "[tool returned empty]",
        ]
        lower = code_or_content.lower()
        for pat in FAILURE_PATTERNS:
            if _re.search(r'(?<!\w)' + _re.escape(pat) + r'(?!\w)', lower):
                logger.warning(f"Verifier: failure pattern detected: '{pat}'")
                return False
        _stripped = code_or_content.strip()
        if len(_stripped) < 5:
            logger.warning("Verifier: answer too short to be meaningful")
            return False
        
        _min_len = 15 if (metadata and metadata.get("task_type") in ("diagnostic", "lookup")) else 30
        if len(_stripped) < _min_len:
            # Short but potentially valid (shell exit codes, booleans, status words)
            SHORT_VALID = {"ok", "true", "false", "done", "0", "1", "yes", "no", "none"}
            if _stripped.lower() not in SHORT_VALID:
                logger.warning(f"Verifier: answer too short ({len(_stripped)} < {_min_len})")
                return False
            else:
                logger.debug(f"Verifier: short answer accepted: {_stripped!r}")
        return True
