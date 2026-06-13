"""NINA v12 -- ConfigHotReload (Stage 6.6)
Watches .env every 60s. Reloads reloadable fields without restart.
Non-reloadable fields require restart -- changes are logged but ignored.
"""
from typing import Any
import asyncio, logging, json
from pathlib import Path
from dotenv import dotenv_values
from pydantic.fields import PydanticUndefined

logger = logging.getLogger("nina.config")

RELOADABLE = {
    "EWS_MAX_EMAILS":       ("ews_max_emails",        int),
    "EWS_KEYWORDS":         ("ews_keywords",           str),
    "IDLE_THRESHOLD_MIN":   ("idle_threshold_min",     int),
    "IDLE_REPORT_MIN":      ("idle_report_min",        int),
    "IDLE_AUTO_APPROVE":    ("idle_auto_approve",      lambda v: v.lower() == "true"),
    "FLOOD_WINDOW_S":       ("flood_window_s",         int),   # FIX: was FLOOD_WINDOWS
    "FLOOD_MAX_MESSAGES":   ("flood_max_messages",     int),
    "SESSION_MAX_TURNS":    ("session_max_turns",      int),
    "AGENT_TIMEOUT_S":      ("agent_timeout_s",        int),   # FIX: was AGENT_TIMEOUTS
    "API_RATE_LIMIT_RPM":   ("api_rate_limit_rpm",     int),
    "DEAD_MAN_PING_URL":    ("dead_man_ping_url",      str),
    "LOG_LEVEL":            ("log_level",              str),
    "THERMAL_WARN_CPU":     ("thermal_warn_cpu",       int),
    "THERMAL_WARN_GPU":     ("thermal_warn_gpu",       int),
    "THERMAL_GUARD_CPU":    ("thermal_guard_cpu",      int),
    "THERMAL_GUARD_GPU":    ("thermal_guard_gpu",      int),
    "THERMAL_CRITICAL_CPU": ("thermal_critical_cpu",   int),
    "THERMAL_CRITICAL_GPU": ("thermal_critical_gpu",   int),
    "MODEL_OVERRIDES":      ("model_overrides",        json.loads),
}


class ConfigHotReload:
    def __init__(self, config: Any, telegram: Any=None) -> None:
        self.config    = config
        self.telegram  = telegram
        self._env_path = Path(".env")
        self._last_mtime: float = self._mtime()
        self._task = None

    def _mtime(self) -> float:
        try:
            return self._env_path.stat().st_mtime
        except Exception as e:
            logger.warning(f"config_hotreload_mtime_failed {e}")
            return 0.0

    async def initialize(self) -> None:
        self._task = asyncio.create_task(self._watch())
        logger.info("ConfigHotReload watching .env every 60s")

    async def _watch(self) -> None:
        while True:
            try:
                await asyncio.sleep(60)
                mtime = self._mtime()
                if mtime <= self._last_mtime:
                    continue
                self._last_mtime = mtime
                await self._reload()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"config_hotreload_error {e}")

    async def _reload(self) -> None:
        try:
            env     = dotenv_values(".env")
            changed = []
            for env_key, (attr, cast) in RELOADABLE.items():
                val = env.get(env_key)
                if val is None or val.strip() == "":
                    field = self.config.model_fields.get(attr)
                    if field is not None:
                        default = field.default
                        if default is not PydanticUndefined and getattr(self.config, attr) != default:
                            setattr(self.config, attr, default)
                            changed.append(f"{attr}: reverted to default({default})")
                    continue
                try:
                    new_val = cast(val)
                except Exception:
                    continue
                old_val = getattr(self.config, attr, None)
                if new_val != old_val:
                    setattr(self.config, attr, new_val)
                    changed.append(f"{attr}: {old_val} -> {new_val}")

            if changed:
                msg = "Config reloaded:\n" + "\n".join(changed)
                logger.info(f"config_hotreload changed={changed}", extra={"log": "nina.log"})
                if self.telegram:
                    await self.telegram.send_message(msg)
            else:
                logger.info("config_hotreload no reloadable changes")
        except Exception as e:
            logger.error(f"config_hotreload_failed {e}")
            if self.telegram:
                await self.telegram.send_message(
                    f"Config reload failed: {e} -- keeping old config.")
