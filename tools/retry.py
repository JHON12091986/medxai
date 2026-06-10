import time
import logging
from typing import Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("nina.tools.retry")

@dataclass
class ToolResult:
    ok: bool
    data: Any
    error: Optional[str]

    @classmethod
    def success(cls, data: Any) -> "ToolResult":
        return cls(ok=True, data=data, error=None)

    @classmethod
    def failure(cls, error: str) -> "ToolResult":
        return cls(ok=False, data=None, error=error)

def retry(func=None, max_attempts=3, backoff_seconds=2, exceptions=(Exception,)):
    if func is None:
        def decorator(f):
            return retry(f, max_attempts=max_attempts, backoff_seconds=backoff_seconds, exceptions=exceptions)
        return decorator

    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(1, max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt == max_attempts:
                    break
                current_backoff = backoff_seconds * (2 ** (attempt - 1))
                logger.warning(f"Retry attempt {attempt}/{max_attempts} for {func.__name__} failed: {str(e)}. Retrying in {current_backoff}s...")
                time.sleep(current_backoff)
        if last_exception:
            logger.warning(f"All {max_attempts} attempts failed for {func.__name__}. Last error: {str(last_exception)}")
            raise last_exception

    return wrapper
