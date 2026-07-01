"""core/event_watcher.py — Proactive background event system for NINA vNext.

Watches for events across multiple sources and delivers typed NinaEvent
objects to registered async handlers:

  Source          | Trigger
  ────────────────|─────────────────────────────────────────────────
  repo_poll       | New commits in a watched GitHub repo (polling)
  provider_health | LLM provider health check (ping + latency)
  cron            | APScheduler-style cron expressions
  webhook         | Inbound HTTP webhook payloads (via queue)
  user_interrupt  | Manual event injection from Telegram / CLI
  idle            | System idle detection (no activity for N seconds)

Design rules:
  - All watchers are independent asyncio tasks.
  - Failures in one watcher do not affect others.
  - Handlers are async callables registered per event type.
  - EventWatcher has a clean start() / stop() lifecycle.
  - No external dependencies beyond aiohttp (already in NINA).
  - Respects NINA_EVENT_POLL_INTERVAL_S env var.

Usage:
    from core.event_watcher import EventWatcher, EventType

    watcher = EventWatcher(router=router)
    watcher.add_cron("memory_consolidation", "0 */2 * * *",
                     handler=consolidate_fn)
    watcher.watch_repo("aibony/nina", handler=on_new_commit)
    watcher.watch_provider_health(["openai", "anthropic"],
                                  handler=on_health_change)
    await watcher.start()
    # ... later ...
    await watcher.stop()
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Awaitable

log = logging.getLogger("nina.events")

POLL_INTERVAL = int(os.getenv("NINA_EVENT_POLL_INTERVAL_S", "60"))
IDLE_TIMEOUT  = int(os.getenv("NINA_IDLE_TIMEOUT_S", "300"))  # 5 min


class EventType(str, Enum):
    REPO_COMMIT      = "repo_commit"
    PROVIDER_HEALTH  = "provider_health"
    CRON             = "cron"
    WEBHOOK          = "webhook"
    USER_INTERRUPT   = "user_interrupt"
    IDLE             = "idle"
    CUSTOM           = "custom"


@dataclass
class NinaEvent:
    event_type:  EventType
    source:      str
    payload:     dict       = field(default_factory=dict)
    timestamp:   str        = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    priority:    int        = 5   # 1 (highest) – 10 (lowest)

    def summary(self) -> str:
        return (
            f"[{self.event_type.value.upper()}] source={self.source} "
            f"priority={self.priority} ts={self.timestamp[:19]}"
        )


EventHandler = Callable[[NinaEvent], Awaitable[None]]


@dataclass
class _CronEntry:
    name:     str
    cron_str: str
    handler:  EventHandler
    last_run: float = 0.0


class EventWatcher:
    """Background event watcher with multi-source support."""

    def __init__(self, router: Any = None, github_token: str = ""):
        self._router       = router
        self._gh_token     = github_token or os.getenv("GITHUB_TOKEN", "")
        self._handlers:    dict[EventType, list[EventHandler]] = {}
        self._crons:       list[_CronEntry] = []
        self._repo_watches: list[dict] = []          # {repo, last_sha, handler}
        self._provider_watches: list[dict] = []      # {name, url, handler, last_ok}
        self._webhook_queue: asyncio.Queue[NinaEvent] = asyncio.Queue()
        self._tasks:       list[asyncio.Task] = []
        self._running      = False
        self._last_activity = time.time()

    # ── registration API ───────────────────────────────────────────────

    def on(self, event_type: EventType, handler: EventHandler) -> None:
        """Register a handler for all events of a given type."""
        self._handlers.setdefault(event_type, []).append(handler)

    def add_cron(
        self,
        name: str,
        cron_str: str,
        handler: EventHandler,
    ) -> None:
        """Add a cron-triggered job.

        cron_str supports: 'every_N_seconds', 'every_N_minutes',
        'every_N_hours', or a simple 'HH:MM' daily trigger.
        Full crontab syntax requires APScheduler (optional).
        """
        self._crons.append(_CronEntry(name=name, cron_str=cron_str,
                                      handler=handler))
        log.info("events: cron registered '%s' (%s)", name, cron_str)

    def watch_repo(
        self,
        repo: str,
        handler: EventHandler,
        branch: str = "main",
    ) -> None:
        """Poll a GitHub repo for new commits."""
        self._repo_watches.append({
            "repo":     repo,
            "branch":   branch,
            "handler":  handler,
            "last_sha": "",
        })
        log.info("events: watching repo '%s' branch '%s'", repo, branch)

    def watch_provider_health(
        self,
        providers: list[str],
        handler: EventHandler,
        check_url_map: dict[str, str] | None = None,
    ) -> None:
        """Periodically ping LLM providers and fire on health changes."""
        default_urls = {
            "openai":    "https://api.openai.com",
            "anthropic": "https://api.anthropic.com",
            "groq":      "https://api.groq.com",
            "ollama":    "http://localhost:11434",
        }
        urls = {**(check_url_map or {}), **default_urls}
        for name in providers:
            self._provider_watches.append({
                "name":    name,
                "url":     urls.get(name, ""),
                "handler": handler,
                "last_ok": True,
            })
        log.info("events: watching %d providers", len(providers))

    def inject(
        self,
        event_type: EventType,
        source: str,
        payload: dict | None = None,
        priority: int = 3,
    ) -> None:
        """Manually inject an event (user interrupt, webhook, etc.)."""
        event = NinaEvent(
            event_type=event_type,
            source=source,
            payload=payload or {},
            priority=priority,
        )
        self._webhook_queue.put_nowait(event)
        self._last_activity = time.time()

    def ping(self) -> None:
        """Signal user activity to reset idle timer."""
        self._last_activity = time.time()

    # ── lifecycle ──────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start all background watcher tasks."""
        if self._running:
            return
        self._running = True
        self._tasks = [
            asyncio.create_task(self._cron_loop(),    name="nina.events.cron"),
            asyncio.create_task(self._repo_loop(),    name="nina.events.repo"),
            asyncio.create_task(self._health_loop(),  name="nina.events.health"),
            asyncio.create_task(self._queue_loop(),   name="nina.events.queue"),
            asyncio.create_task(self._idle_loop(),    name="nina.events.idle"),
        ]
        log.info("events: watcher started (%d tasks)", len(self._tasks))

    async def stop(self) -> None:
        """Cancel all background tasks and clean up."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        log.info("events: watcher stopped")

    # ── background loops ───────────────────────────────────────────────

    async def _cron_loop(self) -> None:
        while self._running:
            now = time.time()
            for entry in self._crons:
                if _cron_due(entry.cron_str, entry.last_run, now):
                    entry.last_run = now
                    event = NinaEvent(
                        event_type=EventType.CRON,
                        source=entry.name,
                        payload={"cron": entry.cron_str},
                        priority=6,
                    )
                    await self._dispatch(event, [entry.handler])
            await asyncio.sleep(10)  # check resolution: 10s

    async def _repo_loop(self) -> None:
        while self._running:
            for watch in self._repo_watches:
                try:
                    sha = await self._get_latest_sha(
                        watch["repo"], watch["branch"]
                    )
                    if sha and sha != watch["last_sha"]:
                        if watch["last_sha"]:  # skip first poll
                            event = NinaEvent(
                                event_type=EventType.REPO_COMMIT,
                                source=watch["repo"],
                                payload={
                                    "repo":   watch["repo"],
                                    "branch": watch["branch"],
                                    "sha":    sha,
                                    "prev":   watch["last_sha"],
                                },
                                priority=4,
                            )
                            await self._dispatch(event, [watch["handler"]])
                        watch["last_sha"] = sha
                except Exception as exc:
                    log.debug("events: repo poll '%s' failed: %s",
                              watch["repo"], exc)
            await asyncio.sleep(POLL_INTERVAL)

    async def _health_loop(self) -> None:
        while self._running:
            for watch in self._provider_watches:
                try:
                    ok, latency = await self._ping_provider(watch["url"])
                    changed = ok != watch["last_ok"]
                    watch["last_ok"] = ok
                    if changed:
                        event = NinaEvent(
                            event_type=EventType.PROVIDER_HEALTH,
                            source=watch["name"],
                            payload={
                                "provider":   watch["name"],
                                "healthy":    ok,
                                "latency_ms": latency,
                            },
                            priority=2 if not ok else 7,
                        )
                        await self._dispatch(event, [watch["handler"]])
                except Exception as exc:
                    log.debug("events: health check '%s' failed: %s",
                              watch["name"], exc)
            await asyncio.sleep(POLL_INTERVAL)

    async def _queue_loop(self) -> None:
        """Drain the webhook/inject queue."""
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._webhook_queue.get(), timeout=5.0
                )
                handlers = self._handlers.get(event.event_type, [])
                await self._dispatch(event, handlers)
                self._webhook_queue.task_done()
            except asyncio.TimeoutError:
                pass
            except Exception as exc:
                log.debug("events: queue loop error: %s", exc)

    async def _idle_loop(self) -> None:
        """Fire IDLE event when no activity for IDLE_TIMEOUT seconds."""
        idle_fired = False
        while self._running:
            elapsed = time.time() - self._last_activity
            if elapsed >= IDLE_TIMEOUT and not idle_fired:
                event = NinaEvent(
                    event_type=EventType.IDLE,
                    source="system",
                    payload={"idle_seconds": int(elapsed)},
                    priority=8,
                )
                handlers = self._handlers.get(EventType.IDLE, [])
                await self._dispatch(event, handlers)
                idle_fired = True
            elif elapsed < IDLE_TIMEOUT:
                idle_fired = False
            await asyncio.sleep(30)

    # ── internal helpers ───────────────────────────────────────────────

    async def _dispatch(
        self,
        event: NinaEvent,
        extra_handlers: list[EventHandler],
    ) -> None:
        log.info("events: %s", event.summary())
        all_handlers = (
            self._handlers.get(event.event_type, []) + extra_handlers
        )
        for handler in all_handlers:
            try:
                await handler(event)
            except Exception as exc:
                log.error("events: handler error for %s: %s",
                          event.event_type.value, exc)

    async def _get_latest_sha(
        self, repo: str, branch: str
    ) -> str:
        """Poll GitHub API for the latest commit SHA."""
        try:
            import aiohttp
            url     = f"https://api.github.com/repos/{repo}/commits/{branch}"
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self._gh_token:
                headers["Authorization"] = f"token {self._gh_token}"
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("sha", "")
        except Exception as exc:
            log.debug("events: _get_latest_sha failed: %s", exc)
        return ""

    async def _ping_provider(
        self, url: str
    ) -> tuple[bool, float]:
        """Ping a provider URL and return (reachable, latency_ms)."""
        if not url:
            return True, 0.0
        try:
            import aiohttp
            t0 = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    url,
                    timeout=aiohttp.ClientTimeout(total=5),
                    allow_redirects=True,
                ) as resp:
                    latency = (time.time() - t0) * 1000
                    return resp.status < 500, latency
        except Exception:
            return False, 0.0


# ── cron helpers ─────────────────────────────────────────────────────────

def _cron_due(cron_str: str, last_run: float, now: float) -> bool:
    """Simple cron evaluator for NINA's built-in patterns.

    Supported patterns:
        every_N_seconds   — e.g. every_30_seconds
        every_N_minutes   — e.g. every_5_minutes
        every_N_hours     — e.g. every_2_hours
        HH:MM             — daily at given time (UTC)
    Falls back to APScheduler CronTrigger if installed.
    """
    c = cron_str.strip().lower()

    if c.startswith("every_"):
        parts = c.split("_")
        if len(parts) == 3:
            try:
                n    = int(parts[1])
                unit = parts[2]
                secs = {"seconds": 1, "minutes": 60, "hours": 3600}.get(unit, 0)
                if secs and (now - last_run) >= n * secs:
                    return True
            except ValueError:
                pass
        return False

    # HH:MM daily trigger
    if ":" in c and len(c) == 5:
        try:
            hh, mm    = int(c[:2]), int(c[3:])
            now_dt    = datetime.fromtimestamp(now, tz=timezone.utc)
            target_s  = hh * 3600 + mm * 60
            current_s = now_dt.hour * 3600 + now_dt.minute * 60
            # Due if within the 10s check window and not run today
            today_run = datetime.fromtimestamp(last_run, tz=timezone.utc).date()
            if (abs(current_s - target_s) < 10
                    and now_dt.date() > today_run):
                return True
        except ValueError:
            pass
        return False

    # APScheduler fallback
    try:
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.util import datetime_to_utc_timestamp
        import pytz
        trigger  = CronTrigger.from_crontab(cron_str, timezone=pytz.utc)
        prev_dt  = datetime.fromtimestamp(last_run, tz=timezone.utc)
        next_run = trigger.get_next_fire_time(prev_dt, prev_dt)
        return next_run is not None and now >= datetime_to_utc_timestamp(next_run)
    except Exception:
        pass

    return False
