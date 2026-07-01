"""
core/manifest_watcher.py
NINA Ouroboros Trigger — File System Watchdog

The 'snake biting its tail.' A watchdog-based file system
observer that fires BLACKBOARD_MUTATION on any file hash
change, triggering the full self-healing cascade:

  file change
    → hash drift detected
    → BLACKBOARD_MUTATION event
    → Auditor wakes (Trigger Reflex)
    → audit → index update → SSOT sync
    → loop

Usage:
    from core.manifest_watcher import ManifestWatcher

    watcher = ManifestWatcher(watch_path=ROOT)
    watcher.start()   # non-blocking background thread
    # ... later ...
    watcher.stop()
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Set

ROOT = Path(__file__).parent.parent
log = logging.getLogger("nina.manifest_watcher")

# Extensions to watch
WATCH_EXTS: Set[str] = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt"}
# Directories to ignore
IGNORE_DIRS: Set[str] = {".git", "__pycache__", ".venv", "venv", ".mypy_cache", "node_modules"}


def _file_hash(path: Path) -> str:
    """SHA-256 of file contents, truncated to 16 chars."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    except (OSError, PermissionError):
        return ""


class ManifestWatcher:
    """Polls the watch_path every `interval` seconds for file hash changes.
    On drift, fires a BLACKBOARD_MUTATION event via EventBus.

    Uses polling (not inotify) for maximum portability across
    Linux/macOS/WSL without requiring the `watchdog` package.
    """

    def __init__(
        self,
        watch_path: Path = ROOT,
        interval: float = 5.0,
    ):
        self.watch_path = watch_path
        self.interval = interval
        self._hashes: Dict[str, str] = {}   # canonical_path → hash
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    #  Lifecycle                                                           #
    # ------------------------------------------------------------------ #
    def start(self) -> None:
        """Start the background watcher thread (non-blocking)."""
        self._stop_event.clear()
        self._hashes = self._snapshot()  # baseline
        self._thread = threading.Thread(
            target=self._watch_loop,
            name="nina-manifest-watcher",
            daemon=True,
        )
        self._thread.start()
        log.info(f"ManifestWatcher started — watching {self.watch_path} ({len(self._hashes)} files)")

    def stop(self) -> None:
        """Signal the watcher to stop gracefully."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10)
        log.info("ManifestWatcher stopped.")

    # ------------------------------------------------------------------ #
    #  Internal loop                                                       #
    # ------------------------------------------------------------------ #
    def _watch_loop(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(self.interval)
            try:
                self._check_drift()
            except Exception as exc:
                log.warning(f"ManifestWatcher error: {exc}")

    def _check_drift(self) -> None:
        current = self._snapshot()
        with self._lock:
            old = self._hashes
            # Changed or new files
            for path, new_hash in current.items():
                old_hash = old.get(path, "")
                if old_hash != new_hash:
                    self._fire_mutation(path, old_hash, new_hash)
            # Deleted files
            for path in set(old) - set(current):
                self._fire_mutation(path, old[path], "DELETED")
            self._hashes = current

    def _snapshot(self) -> Dict[str, str]:
        """Walk watch_path and return {canonical_path_str: hash}."""
        result: Dict[str, str] = {}
        for fpath in self.watch_path.rglob("*"):
            if fpath.is_file() and fpath.suffix in WATCH_EXTS:
                # Skip ignored dirs
                if any(part in IGNORE_DIRS for part in fpath.parts):
                    continue
                result[str(fpath.resolve())] = _file_hash(fpath)
        return result

    def _fire_mutation(self, path: str, pre_hash: str, post_hash: str) -> None:
        """Fire BLACKBOARD_MUTATION event via EventBus + HivePacket."""
        log.debug(f"Hash drift: {Path(path).name} {pre_hash!r} → {post_hash!r}")
        try:
            from core.hive_packet import HivePacket
            packet = HivePacket.create(
                sender_node="manifest_watcher",
                target_scope=path,
                pre_hash=pre_hash,
                post_payload=post_hash,
                bottleneck="",
                adaptation="",
            )
            packet.emit()  # validate → ledger → fires BLACKBOARD_MUTATION → wakes Auditor
        except Exception as exc:
            log.warning(f"ManifestWatcher emit failed: {exc}")
            # Fallback: fire event directly without HivePacket
            try:
                from core.event_bus import EventBus, Event
                EventBus.instance().publish(Event(
                    type="BLACKBOARD_MUTATION",
                    payload={"scope": path, "pre_hash": pre_hash, "post_hash": post_hash},
                ))
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    #  SIGTERM / SIGINT integration                                        #
    # ------------------------------------------------------------------ #
    def register_signals(self) -> None:
        """Register OS signal handlers to stop watcher gracefully."""
        import signal

        def _handler(signum, frame):
            log.info(f"ManifestWatcher caught signal {signum} — stopping.")
            self.stop()

        signal.signal(signal.SIGTERM, _handler)
        signal.signal(signal.SIGINT, _handler)


# ------------------------------------------------------------------ #
#  Module-level singleton                                              #
# ------------------------------------------------------------------ #
_watcher: Optional[ManifestWatcher] = None


def get_watcher(watch_path: Path = ROOT, interval: float = 5.0) -> ManifestWatcher:
    global _watcher
    if _watcher is None:
        _watcher = ManifestWatcher(watch_path=watch_path, interval=interval)
    return _watcher


def start_ouroboros(watch_path: Path = ROOT, interval: float = 5.0) -> ManifestWatcher:
    """One-line call to start the Ouroboros loop from kernel.py or main.py."""
    w = get_watcher(watch_path, interval)
    w.register_signals()
    w.start()
    return w
