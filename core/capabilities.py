from typing import Optional, List
"""NINA v12 — CapabilityRegistry (Stage 6.8)"""
import asyncio, json, logging, time
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger("nina.capabilities")
CAP_FILE = Path("data/capabilities.json")

DEFAULT_CAPS = {
    "shell":   {"loaded": True, "healthy": True},
    "web":     {"loaded": True, "healthy": True},
    "browser": {"loaded": True, "healthy": True},
    "file":    {"loaded": True, "healthy": True},
    "system":  {"loaded": True, "healthy": True},
    "email":   {"loaded": True, "healthy": True},
    "gpu":     {"loaded": True, "healthy": True},
    "finance": {"loaded": True, "healthy": True},
}

class CapabilityRegistry:
    _lock: asyncio.Lock = None

    def __init__(self):
        if CapabilityRegistry._lock is None:
            CapabilityRegistry._lock = asyncio.Lock()
        self._lock = CapabilityRegistry._lock
        CAP_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not CAP_FILE.exists():
            CAP_FILE.write_text(json.dumps(DEFAULT_CAPS, indent=2))
        self._caps: dict = json.loads(CAP_FILE.read_text())

    def register(self, name: str, path: str, description: str = "", role: str = "tool"):
        """Register a new dynamic capability."""
        self._caps[name] = {
            "path": path,
            "description": description,
            "role": role,
            "loaded": True,
            "healthy": True,
            "registered_at": time.strftime("%Y-%m-%dT%H:%M:%S+0600")
        }
        CAP_FILE.write_text(json.dumps(self._caps, indent=2))
        logger.info(f"capability_registered name={name} path={path}")

    def get_capability(self, name: str) -> Optional[dict]:
        return self._caps.get(name)

    def list_capabilities(self) -> List[dict]:
        return [{"name": k, **v} for k, v in self._caps.items()]

    def is_healthy(self, tool_name: str) -> bool:
        return self._caps.get(tool_name, {}).get("healthy", True)

    async def mark_unhealthy(self, tool_name: str, error: str = ""):
        if tool_name in self._caps:
            async with self._lock:
                self._caps[tool_name].update({"healthy": False, "error": error,
                    "last_checked": time.strftime("%Y-%m-%dT%H:%M:%S+0600")})
                await asyncio.to_thread(
                    CAP_FILE.write_text, json.dumps(self._caps, indent=2))
            logger.warning(f"capability_unhealthy tool={tool_name} error={error}")

    async def mark_healthy(self, tool_name: str):
        if tool_name in self._caps:
            async with self._lock:
                self._caps[tool_name].update({"healthy": True,
                    "last_checked": time.strftime("%Y-%m-%dT%H:%M:%S+0600")})
                self._caps[tool_name].pop("error", None)
                await asyncio.to_thread(
                    CAP_FILE.write_text, json.dumps(self._caps, indent=2))

    def status(self) -> str:
        lines = ["Tool capabilities:"]
        for name, e in self._caps.items():
            icon = "✅" if e.get("healthy") else "❌"
            err  = f" — {e['error']}" if not e.get("healthy") and "error" in e else ""
            lines.append(f"  {icon} {name}{err}")
        return "\n".join(lines)
