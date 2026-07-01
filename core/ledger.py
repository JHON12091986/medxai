"""
core/ledger.py — NINA Single Source of Truth Ledger
GAP-01 · GAP-04 · GAP-07 · 24 Jun 2026

Replaces chromadb. Zero external deps (sqlite3 is stdlib).
Four tables:
  events  — immutable append-only audit log with temporal window support
  state   — current SSOT key/value store
  locks   — idempotency guard (prevents duplicate executions)
  wal_log — asyncio.to_thread()-safe WAL commit log (GAP-07)

Temporal API (GAP-01):
    db.log_temporal(action, path, valid_from, valid_to)  # bounded event
    db.fetch_at(ts)                                       # point-in-time snapshot
    db.expire_at(event_id, ts)                            # soft-delete
    db.vacuum(days=30)                                    # prune old rows

WAL commit API (GAP-07):
    db.wal_commit(task_id, result)   # kernel STATE 04 commit
    db.wal_recent(limit)             # recent WAL entries

asyncio usage — wrap blocking calls with asyncio.to_thread():
    result = await asyncio.to_thread(ledger.log, "event", "/path")
    await asyncio.to_thread(ledger.wal_commit, task_id, result)

Base API (unchanged):
    db.log(action, path, meta)   # append event
    db.set(key, value)           # upsert state
    db.get(key)                  # read state
    db.acquire(task_id)          # idempotency lock
    db.release(task_id)          # release lock
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

try:
    import mmh3
    _HAS_MMH3 = True
except ImportError:
    _HAS_MMH3 = False


DB_PATH = Path.home() / "nina" / "data" / "nina.db"
LOCK_TTL = 300          # seconds — auto-expire stale locks
DEFAULT_RETENTION = 30  # days — vacuum window


class Ledger:
    """Thread-safe sqlite3-backed SSOT ledger for NINA.

    All public methods are synchronous and safe to call from
    asyncio.to_thread(). Never call directly from the event loop thread
    without to_thread() — sqlite3 I/O will block the loop.
    """

    def __init__(self, path: Path = DB_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")   # safe concurrent writes
        self._conn.execute("PRAGMA synchronous=NORMAL") # fast but safe
        self._bootstrap()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _bootstrap(self) -> None:
        c = self._conn
        c.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                ts         REAL    NOT NULL,
                action     TEXT    NOT NULL,
                path       TEXT,
                hash       TEXT,
                meta       TEXT,
                valid_from REAL,
                valid_to   REAL
            );
            CREATE INDEX IF NOT EXISTS idx_events_action     ON events(action);
            CREATE INDEX IF NOT EXISTS idx_events_path       ON events(path);
            CREATE INDEX IF NOT EXISTS idx_events_valid_from ON events(valid_from);
            CREATE INDEX IF NOT EXISTS idx_events_valid_to   ON events(valid_to);

            CREATE TABLE IF NOT EXISTS state (
                key        TEXT PRIMARY KEY,
                value      TEXT,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS locks (
                task_id    TEXT PRIMARY KEY,
                acquired   REAL NOT NULL,
                expires    REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS wal_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                ts         REAL    NOT NULL,
                task_id    TEXT    NOT NULL,
                result     TEXT,
                committed  INTEGER NOT NULL DEFAULT 1
            );
            CREATE INDEX IF NOT EXISTS idx_wal_task ON wal_log(task_id);
        """)
        # Safe migration: add columns if upgrading from pre-GAP-01 schema
        for col, typedef in [
            ("valid_from", "REAL"),
            ("valid_to",   "REAL"),
        ]:
            try:
                c.execute(f"ALTER TABLE events ADD COLUMN {col} {typedef}")
            except sqlite3.OperationalError:
                pass  # column already exists — safe to ignore
        c.commit()

    # ------------------------------------------------------------------
    # Events — append-only audit log
    # ------------------------------------------------------------------

    def log(self, action: str, path: str = "", meta: str = "") -> int:
        """Append an immutable event. Returns new row id."""
        file_hash = self._hash_path(path) if path else ""
        cur = self._conn.execute(
            "INSERT INTO events (ts, action, path, hash, meta) VALUES (?,?,?,?,?)",
            (time.time(), action, path, file_hash, meta),
        )
        self._conn.commit()
        return cur.lastrowid

    def log_temporal(
        self,
        action: str,
        path: str = "",
        meta: str = "",
        valid_from: Optional[float] = None,
        valid_to: Optional[float] = None,
    ) -> int:
        """Append event with explicit temporal validity window (GAP-01).

        Args:
            valid_from: unix timestamp when this event becomes active.
                        Defaults to now.
            valid_to:   unix timestamp when this event expires.
                        None = no expiry (permanent).
        """
        now = time.time()
        file_hash = self._hash_path(path) if path else ""
        cur = self._conn.execute(
            "INSERT INTO events (ts, action, path, hash, meta, valid_from, valid_to) "
            "VALUES (?,?,?,?,?,?,?)",
            (now, action, path, file_hash, meta,
             valid_from if valid_from is not None else now,
             valid_to),
        )
        self._conn.commit()
        return cur.lastrowid

    def fetch_at(self, ts: float, action: str = "") -> list[dict]:
        """Point-in-time snapshot: events valid AT timestamp ts (GAP-01).

        Returns events where:
            valid_from <= ts AND (valid_to IS NULL OR valid_to > ts)

        Rows logged without temporal context (valid_from IS NULL) are
        always considered valid for backwards-compatibility.
        """
        base = """
            SELECT id, ts, action, path, hash, meta, valid_from, valid_to
            FROM events
            WHERE (valid_from IS NULL OR valid_from <= ?)
              AND (valid_to   IS NULL OR valid_to   >  ?)
        """
        params: list = [ts, ts]
        if action:
            base += " AND action = ?"
            params.append(action)
        base += " ORDER BY ts DESC"
        rows = self._conn.execute(base, params).fetchall()
        keys = ["id", "ts", "action", "path", "hash", "meta", "valid_from", "valid_to"]
        return [dict(zip(keys, r)) for r in rows]

    def expire_at(self, event_id: int, ts: Optional[float] = None) -> None:
        """Soft-delete an event by setting valid_to = ts (default: now)."""
        self._conn.execute(
            "UPDATE events SET valid_to = ? WHERE id = ?",
            (ts if ts is not None else time.time(), event_id),
        )
        self._conn.commit()

    def recent(self, action: str = "", limit: int = 50) -> list[dict]:
        """Return recent events, optionally filtered by action."""
        if action:
            rows = self._conn.execute(
                "SELECT id,ts,action,path,hash,meta,valid_from,valid_to "
                "FROM events WHERE action=? ORDER BY id DESC LIMIT ?",
                (action, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id,ts,action,path,hash,meta,valid_from,valid_to "
                "FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        keys = ["id", "ts", "action", "path", "hash", "meta", "valid_from", "valid_to"]
        return [dict(zip(keys, r)) for r in rows]

    def vacuum(self, days: int = DEFAULT_RETENTION) -> int:
        """Prune events older than `days`. Returns count of deleted rows (GAP-04).

        Only deletes rows where both ts AND valid_to are past the cutoff,
        or valid_to is NULL (permanent row past retention window).
        Call from idleloop.py via asyncio.to_thread(ledger.vacuum).
        """
        cutoff = time.time() - (days * 86400)
        cur = self._conn.execute(
            "DELETE FROM events WHERE ts < ? AND (valid_to IS NULL OR valid_to < ?)",
            (cutoff, cutoff),
        )
        self._conn.execute("VACUUM")
        self._conn.commit()
        return cur.rowcount

    # ------------------------------------------------------------------
    # WAL commit log — kernel STATE 04 (GAP-07)
    # ------------------------------------------------------------------

    def wal_commit(self, task_id: str, result: Any = None) -> int:
        """Record a STATE 04 WAL commit. Safe to call from asyncio.to_thread().

        kernel.py STATE 04 pattern:
            await asyncio.to_thread(ledger.wal_commit, packet.task_id, result)
        """
        result_str = json.dumps(result, default=str) if result is not None else None
        cur = self._conn.execute(
            "INSERT INTO wal_log (ts, task_id, result) VALUES (?,?,?)",
            (time.time(), task_id, result_str),
        )
        self._conn.commit()
        return cur.lastrowid

    def wal_recent(self, limit: int = 20) -> list[dict]:
        """Return recent WAL commits."""
        rows = self._conn.execute(
            "SELECT id, ts, task_id, result, committed FROM wal_log "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        keys = ["id", "ts", "task_id", "result", "committed"]
        return [dict(zip(keys, r)) for r in rows]

    # ------------------------------------------------------------------
    # State — SSOT key/value
    # ------------------------------------------------------------------

    def set(self, key: str, value: Any) -> None:
        self._conn.execute(
            "INSERT INTO state (key,value,updated_at) VALUES (?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, "
            "updated_at=excluded.updated_at",
            (key, str(value), time.time()),
        )
        self._conn.commit()

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        row = self._conn.execute(
            "SELECT value FROM state WHERE key=?", (key,)
        ).fetchone()
        return row[0] if row else default

    def delete(self, key: str) -> None:
        self._conn.execute("DELETE FROM state WHERE key=?", (key,))
        self._conn.commit()

    # ------------------------------------------------------------------
    # Locks — idempotency guard
    # ------------------------------------------------------------------

    def acquire(self, task_id: str, ttl: int = LOCK_TTL) -> bool:
        """Acquire an idempotency lock. Returns False if already held."""
        now = time.time()
        self._conn.execute("DELETE FROM locks WHERE expires < ?", (now,))
        try:
            self._conn.execute(
                "INSERT INTO locks (task_id, acquired, expires) VALUES (?,?,?)",
                (task_id, now, now + ttl),
            )
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def release(self, task_id: str) -> None:
        self._conn.execute("DELETE FROM locks WHERE task_id=?", (task_id,))
        self._conn.commit()

    def is_locked(self, task_id: str) -> bool:
        now = time.time()
        row = self._conn.execute(
            "SELECT 1 FROM locks WHERE task_id=? AND expires > ?", (task_id, now)
        ).fetchone()
        return row is not None

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    @staticmethod
    def _hash_path(path: str) -> str:
        if _HAS_MMH3:
            return hex(mmh3.hash128(path, signed=False))
        return hashlib.sha256(path.encode()).hexdigest()[:16]

    @staticmethod
    def hash_content(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    # ------------------------------------------------------------------
    # Housekeeping
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._conn.close()

    def __repr__(self) -> str:
        return f"Ledger(path={self._path})"


_ledger: Optional[Ledger] = None


def get_ledger() -> Ledger:
    """Return the process-wide Ledger singleton."""
    global _ledger
    if _ledger is None:
        _ledger = Ledger()
    return _ledger
