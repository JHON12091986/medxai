import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional

class ScratchpadManager:
    def __init__(self):
        self.file_path = Path("data/memory/scratchpad.json")
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write({})

    def _read(self) -> dict:
        try:
            return json.loads(self.file_path.read_text())
        except Exception:
            return {}

    def _write(self, data: dict):
        tmp = self.file_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2))
        tmp.replace(self.file_path)

    def store(self, key: str, value: Any, ttl_seconds: int = 300):
        data = self._read()
        from datetime import timedelta
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()

        data[key] = {
            "value": value,
            "expires_at": expires_at
        }
        self._write(data)

    def get(self, key: str) -> Optional[Any]:
        data = self._read()
        if key not in data:
            return None

        entry = data[key]
        expires_at = entry.get("expires_at", "")

        if datetime.now(timezone.utc).isoformat() > expires_at:
            # Clean it up immediately
            del data[key]
            self._write(data)
            return None

        return entry.get("value")

    def clear_expired(self):
        data = self._read()
        now = datetime.now(timezone.utc).isoformat()

        keys_to_remove = [k for k, v in data.items() if now > v.get("expires_at", "")]
        if keys_to_remove:
            for k in keys_to_remove:
                del data[k]
            self._write(data)

    def clear_all(self):
        self._write({})
