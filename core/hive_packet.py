"""
core/hive_packet.py
NINA Hive Mind — Enforced Event Packet Schema

Every agent interaction MUST produce a HivePacket.
This is the single contract binding the Blackboard, Workers, and Auditor.

Usage:
    from core.hive_packet import HivePacket, BlackboardMutation, CollectiveLearning

    packet = HivePacket.create(
        sender_node="worker_intm_file_04",
        target_scope="nina/core/kernel.py",
        pre_hash="a1b2c3d4",
        post_payload="PATCH_NODE_LINE_42",
        bottleneck="Subprocess >250ms",
        adaptation="Switched to async stream readers",
    )
    packet.validate()   # raises HivePacketError if malformed
    packet.to_ledger()  # writes to data/nina.db events table
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
import ast
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "nina.db"


class HivePacketError(ValueError):
    """Raised when a HivePacket fails validation."""


@dataclass
class BlackboardMutation:
    """Describes a single atomic change written to the Blackboard."""
    pre_execution_hash: str          # SHA-256 of file/state before change
    post_execution_payload: str      # The patch / new content
    validation_rules: str = "ast.parse(payload)"  # How auditor validates
    post_execution_hash: str = field(default="")   # Computed on validate()

    def compute_post_hash(self) -> str:
        return hashlib.sha256(self.post_execution_payload.encode()).hexdigest()[:16]


@dataclass
class CollectiveLearning:
    """What the hive learned from this execution — persisted to memory."""
    bottleneck_flagged: str = ""     # e.g. "Subprocess took >250ms"
    alternative_adapted: str = ""    # e.g. "Switched to async stream readers"
    confidence: float = 1.0          # 0.0–1.0


@dataclass
class HivePacket:
    """The universal contract for all NINA agent interactions."""
    # Identity
    trace_id: str
    sender_node: str
    target_scope: str
    ts: float = field(default_factory=time.time)

    # Payload
    mutation: BlackboardMutation = field(default_factory=lambda: BlackboardMutation("", ""))
    learning: CollectiveLearning = field(default_factory=CollectiveLearning)

    # Lifecycle
    status: str = "PENDING"   # PENDING | VALIDATED | REJECTED | COMMITTED
    audit_score: float = 0.0
    error: str = ""

    # ------------------------------------------------------------------ #
    #  Factory                                                             #
    # ------------------------------------------------------------------ #
    @classmethod
    def create(
        cls,
        sender_node: str,
        target_scope: str,
        pre_hash: str = "",
        post_payload: str = "",
        bottleneck: str = "",
        adaptation: str = "",
        confidence: float = 1.0,
    ) -> "HivePacket":
        mutation = BlackboardMutation(
            pre_execution_hash=pre_hash,
            post_execution_payload=post_payload,
        )
        learning = CollectiveLearning(
            bottleneck_flagged=bottleneck,
            alternative_adapted=adaptation,
            confidence=confidence,
        )
        return cls(
            trace_id=f"trace_nina_{uuid.uuid4().hex[:8]}",
            sender_node=sender_node,
            target_scope=target_scope,
            mutation=mutation,
            learning=learning,
        )

    # ------------------------------------------------------------------ #
    #  Validation                                                          #
    # ------------------------------------------------------------------ #
    def validate(self) -> "HivePacket":
        """Validate mutation payload. Raises HivePacketError on failure."""
        if not self.sender_node:
            raise HivePacketError("sender_node is required")
        if not self.target_scope:
            raise HivePacketError("target_scope is required")

        payload = self.mutation.post_execution_payload
        if payload and payload.strip():
            # If payload looks like Python code, AST-parse it
            if any(kw in payload for kw in ["def ", "class ", "import ", "return ", "async "]):
                try:
                    ast.parse(payload)
                except SyntaxError as exc:
                    self.status = "REJECTED"
                    self.error = str(exc)
                    raise HivePacketError(f"AST validation failed: {exc}") from exc

        self.mutation.post_execution_hash = self.mutation.compute_post_hash()
        self.status = "VALIDATED"
        return self

    # ------------------------------------------------------------------ #
    #  Serialisation                                                       #
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        return {
            "hive_event": {
                "trace_id": self.trace_id,
                "sender_node": self.sender_node,
                "target_scope": self.target_scope,
                "ts": self.ts,
                "status": self.status,
            },
            "blackboard_mutations": {
                "pre_execution_hash": self.mutation.pre_execution_hash,
                "post_execution_payload": self.mutation.post_execution_payload,
                "post_execution_hash": self.mutation.post_execution_hash,
                "validation_rules": self.mutation.validation_rules,
            },
            "collective_learnings": {
                "bottleneck_flagged": self.learning.bottleneck_flagged,
                "alternative_adapted": self.learning.alternative_adapted,
                "confidence": self.learning.confidence,
            },
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    # ------------------------------------------------------------------ #
    #  Blackboard write                                                    #
    # ------------------------------------------------------------------ #
    def to_ledger(self) -> None:
        """Write this packet to the data/nina.db events table."""
        try:
            import sqlite3
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            con = sqlite3.connect(str(DB_PATH))
            cur = con.cursor()
            # Ensure table exists (idempotent)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts     REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    payload    TEXT
                )
            """)
            cur.execute(
                "INSERT INTO events (ts, event_type, payload) VALUES (?, ?, ?)",
                (self.ts, f"HIVE_{self.status}", self.to_json()),
            )
            con.commit()
            con.close()
            self.status = "COMMITTED"
        except Exception as exc:  # never crash a worker on ledger failure
            self.error = str(exc)

    # ------------------------------------------------------------------ #
    #  Trigger Reflex helper                                               #
    # ------------------------------------------------------------------ #
    def emit(self) -> "HivePacket":
        """Validate → write to Blackboard → fire BLACKBOARD_MUTATION event.

        This is the one-line call workers use:
            packet.emit()  # triggers Auditor automatically
        """
        self.validate()
        self.to_ledger()
        # Fire stigmergy event so Auditor auto-wakes (Trigger Reflex)
        try:
            from core.event_bus import EventBus, Event
            bus = EventBus.instance()
            bus.publish(Event(
                type="BLACKBOARD_MUTATION",
                payload={"trace_id": self.trace_id, "scope": self.target_scope},
            ))
        except Exception:
            pass  # EventBus unavailable during cold boot — safe to skip
        return self
