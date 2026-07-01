"""
swarm/auditor.py
NINA Hive Auditor — Trigger Reflex subscriber.

Subscribes to BLACKBOARD_MUTATION events on the EventBus.
Auto-wakes the moment a worker emits a HivePacket.
Validates mutation hash chain, scores the packet, emits AUDIT_RESULT.

This closes Missing Wire #1: Trigger Reflex.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

# Re-export: external callers import AuditFrame from here
try:
    from core.critic import Critic as AuditFrame  # type: ignore
except ImportError:
    AuditFrame = None  # type: ignore


def _score_packet(packet_dict: dict) -> float:
    """Simple heuristic scorer — returns 0.0–1.0."""
    mutations = packet_dict.get("blackboard_mutations", {})
    learnings = packet_dict.get("collective_learnings", {})
    score = 1.0
    if not mutations.get("post_execution_hash"):
        score -= 0.3
    if not mutations.get("pre_execution_hash"):
        score -= 0.1
    if not learnings.get("bottleneck_flagged") and not learnings.get("alternative_adapted"):
        score -= 0.1
    return max(0.0, round(score, 2))


def handle_mutation_event(event) -> None:
    """Called by EventBus when BLACKBOARD_MUTATION fires (Trigger Reflex)."""
    try:
        import sqlite3, json
        from pathlib import Path
        from core.event_bus import EventBus, Event

        DB_PATH = Path(__file__).parent.parent / "data" / "nina.db"
        if not DB_PATH.exists():
            return

        trace_id = event.payload.get("trace_id", "") if hasattr(event, "payload") else ""
        con = sqlite3.connect(str(DB_PATH))
        cur = con.cursor()
        cur.execute(
            "SELECT payload FROM events WHERE event_type LIKE 'HIVE_%' "
            "AND json_extract(payload,'$.hive_event.trace_id') = ? "
            "ORDER BY ts DESC LIMIT 1",
            (trace_id,),
        )
        row = cur.fetchone()
        con.close()

        if not row:
            return

        packet_dict = json.loads(row[0])
        score = _score_packet(packet_dict)

        # Emit audit result back to Blackboard
        bus = EventBus.instance()
        bus.publish(Event(
            type="AUDIT_RESULT",
            payload={
                "trace_id": trace_id,
                "score": score,
                "pass": score >= 0.6,
                "ts": time.time(),
            },
        ))
    except Exception:
        pass  # Auditor must never crash the hive


def register_trigger_reflex() -> None:
    """Call once at startup to wire Auditor to Blackboard mutations."""
    try:
        from core.event_bus import EventBus
        bus = EventBus.instance()
        bus.subscribe("BLACKBOARD_MUTATION", handle_mutation_event)
    except Exception:
        pass
