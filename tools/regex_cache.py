import re
import threading
from typing import Dict, Optional

class RegexRegistry:
    def __init__(self):
        self._cache: Dict[str, re.Pattern] = {}
        self._lock = threading.Lock()

        # Pre-compile default patterns
        self.register_pattern("sensitive_data", r"(API_KEY|TOKEN|SECRET)[=:]\s*[\w\d]+")
        self.register_pattern("log_structure", r"^\[(?P<timestamp>.*?)\] \[(?P<level>INFO|WARN|ERROR)\] (?P<message>.*)")
        self.register_pattern("task_classification", r"\[SLOT-\d+\]|feat\(.*?\):|fix\(.*?\):")

    def register_pattern(self, name: str, pattern_str: str) -> None:
        with self._lock:
            if name not in self._cache:
                self._cache[name] = re.compile(pattern_str, re.IGNORECASE)

    def get_compiled(self, pattern_name: str) -> Optional[re.Pattern]:
        with self._lock:
            return self._cache.get(pattern_name)

# Module-level instance for convenience
registry = RegexRegistry()

def get_compiled(pattern_name: str) -> Optional[re.Pattern]:
    """Module-level helper to get a compiled pattern from the default registry."""
    return registry.get_compiled(pattern_name)
