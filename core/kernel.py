"""NINA kernel.py — 4-State Non-Blocking Orchestrator Loop
Blueprint: nina_blueprint_23.06.2026.md § II
Pass 3 · 24 Jun 2026 — Ouroboros 5 wired

This is the single coroutine that owns the asyncio event loop lifecycle:
  STATE 01 — Queue Ingestion  (event_bus + BloomFilter dedup gate)
  STATE 02 — Context Assembly (layered_memory + ContextCompressor)
  STATE 03 — Yield to LLM / Shell / Tool (agent_loop)
  STATE 04 — Asymmetric Audit + Deterministic GC (guardian_loop + gc)

Boot sequence (called from nina.py):
  1. ManifestWatcher.start()     ← Ouroboros file-hash loop
  2. InvertedIndex.load()        ← trie keyword index (no sentence-transformers)
  3. InvertedIndex.index_directory(ROOT)  ← warm index
  4. BloomFilter.load()          ← probabilistic dedup gate
  5. Kernel(...)                 ← this class

Does NOT replace core/nina.py — nina.py starts services.
kernel.py is the inner task loop that nina.py's agent pipeline calls.
"""
from __future__ import annotations

import asyncio
import gc
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("nina.kernel")

ROOT = Path(__file__).parent.parent


# ------------------------------------------------------------------ #
#  Ouroboros boot — called once from nina.py startup                  #
# ------------------------------------------------------------------ #

def boot_ouroboros() -> None:
    """Wire the Ouroboros 5 modules into the kernel boot sequence.

    Call this ONCE before creating the Kernel instance:
        from core.kernel import boot_ouroboros
        boot_ouroboros()
        kernel = Kernel(...)
    """
    # 1. Path normalization firewall (no-op import, initialises ROOT)

    # GAP-06
    try:
        from core.gap_scanner.scanner import GapScanner as _GapScanner
        from crons.manager import _active_scheduler

        _gap_scanner = _GapScanner(
            telemetry_path="telemetry.jsonl",
            register_path="docs/space/nina_error_register.md",
            backlog_path="docs/space/jules_backlog.md",
        )
        if _active_scheduler is not None:
            from apscheduler.triggers.interval import IntervalTrigger
            _active_scheduler.add(
                _gap_scanner.run_cycle,
                trigger=IntervalTrigger(minutes=5),
                id="gap_scanner",
                replace_existing=True,
                max_instances=1,
                misfire_grace_time=60,
            )
    except Exception as e:
        import logging
        logging.getLogger("nina.kernel").warning(f"Failed to wire gap_scanner: {e}")

    from core.canonicalizer import canonical_key
    _ = canonical_key

    # 2. Bloom filter — load persisted state from data/bloom_filter.json
    from core.bloom_filter import get_bloom
    bf = get_bloom()
    logger.info("kernel.boot bloom_filter loaded count=%d fill=%.2f%%",
                bf._count, bf.fill_ratio * 100)

    # 3. Inverted text index — load + warm from disk
    from memory.trie_index import InvertedIndex
    idx = InvertedIndex.load()
    n = idx.index_directory(ROOT)
    logger.info("kernel.boot trie_index warmed tokens=%d", n)

    # 4. Manifest watcher — starts 5-second Ouroboros polling loop
    from core.manifest_watcher import start_ouroboros
    start_ouroboros(watch_path=ROOT, interval=5.0)
    logger.info("kernel.boot manifest_watcher started (Ouroboros active)")

    # 5. Context compressor — lazy singleton, no explicit init needed
    logger.info("kernel.boot context_compressor ready")

    logger.info("kernel.boot OUROBOROS_5_WIRED — all subsystems online")


# ------------------------------------------------------------------ #
#  TaskPacket                                                          #
# ------------------------------------------------------------------ #

@dataclass
class TaskPacket:
    """Immutable task unit passed through the 4-state pipeline."""
    task_id: str
    payload: dict
    enqueued_at: float = field(default_factory=time.monotonic)
    context: dict = field(default_factory=dict)


# ------------------------------------------------------------------ #
#  Kernel                                                              #
# ------------------------------------------------------------------ #

class Kernel:
    """4-State Non-Blocking Orchestrator.

    Boot:
        boot_ouroboros()   # wire Ouroboros 5 subsystems
        kernel = Kernel(event_bus, agent_loop_fn, memory, guardian)
        asyncio.create_task(kernel.run())
    """

    def __init__(
        self,
        event_bus: Any,
        agent_loop_fn,
        memory: Any,
        guardian: Any,
        *,
        turn_timeout_s: float = 120.0,
    ) -> None:
        self.bus = event_bus
        self._agent_loop_fn = agent_loop_fn
        self.memory = memory
        self.guardian = guardian
        self.turn_timeout = turn_timeout_s
        self._running = False
        self._cycles: int = 0
        self._task: asyncio.Task | None = None

        # Lazy-loaded singletons (initialised by boot_ouroboros)
        self._bloom = None
        self._compressor = None

    def _get_bloom(self):
        if self._bloom is None:
            try:
                from core.bloom_filter import get_bloom
                self._bloom = get_bloom()
            except Exception:
                self._bloom = False  # disable on import error
        return self._bloom or None

    def _get_compressor(self):
        if self._compressor is None:
            try:
                from memory.context_compressor import compress_packet
                self._compressor = compress_packet
            except Exception:
                self._compressor = False
        return self._compressor or None

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    async def start(self) -> None:
        """Create the kernel coroutine task."""
        if self._running:
            logger.warning("kernel already running")
            return
        self._running = True
        self._task = asyncio.create_task(self._loop(), name="nina.kernel")
        logger.info("kernel started")

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("kernel stopped cycles=%d", self._cycles)

    @property
    def cycles(self) -> int:
        return self._cycles

    # ------------------------------------------------------------------ #
    #  4-State Loop                                                        #
    # ------------------------------------------------------------------ #

    async def _loop(self) -> None:
        while self._running:
            # ── STATE 01: Queue Ingestion + Bloom dedup gate ──────────
            packet = await self._state01_ingest()
            if packet is None:
                continue

            # ── STATE 02: Context Assembly + token compression ────────
            packet = await self._state02_context(packet)

            # ── STATE 03: Yield to LLM / Shell / Tool ─────────────────
            result = await self._state03_execute(packet)

            # ── STATE 04: Audit + Deterministic GC ────────────────────
            asyncio.create_task(
                self._state04_audit_gc(packet, result),
                name=f"nina.kernel.audit.{packet.task_id}",
            )

            self._cycles += 1

    # ── State implementations ──────────────────────────────────────────

    async def _state01_ingest(self) -> TaskPacket | None:
        """Non-blocking queue get; Bloom filter dedup gate; yields CPU on empty."""
        try:
            raw = self.bus.queue.get_nowait()
        except Exception:
            await asyncio.sleep(0.05)  # yield CPU
            return None

        # Bloom dedup gate — skip events already processed this session
        bloom = self._get_bloom()
        if bloom is not None:
            try:
                from core.canonicalizer import canonical_event_key
                event_type = raw.get("type", "TASK") if isinstance(raw, dict) else "TASK"
                scope = raw.get("task_id", str(id(raw))) if isinstance(raw, dict) else str(id(raw))
                ekey = canonical_event_key(event_type, scope)
                if bloom.might_contain(ekey):
                    logger.debug("kernel.state01 bloom_skip ekey=%s", ekey)
                    return None
                bloom.add(ekey)
                bloom.save()
            except Exception as exc:
                logger.debug("kernel.state01 bloom_gate_error %s", exc)

        if isinstance(raw, TaskPacket):
            return raw
        # Wrap plain dict payloads for backwards compat
        return TaskPacket(
            task_id=raw.get("task_id", f"k{self._cycles}") if isinstance(raw, dict) else f"k{self._cycles}",
            payload=raw if isinstance(raw, dict) else {"raw": raw},
        )

    async def _state02_context(self, packet: TaskPacket) -> TaskPacket:
        """Attach memory context to packet; compress via ContextCompressor."""
        try:
            if hasattr(self.memory, "fetch_context_async"):
                ctx = await self.memory.fetch_context_async(
                    packet.payload.get("query", "")
                )
            elif hasattr(self.memory, "build_context"):
                ctx = await asyncio.to_thread(
                    self.memory.build_context,
                    packet.payload.get("query", ""),
                )
            else:
                ctx = {}

            if isinstance(ctx, dict):
                # Compress string values before attaching to context window
                compress = self._get_compressor()
                if compress is not None:
                    try:
                        import json
                        compressed_str = compress(ctx)
                        ctx = json.loads(compressed_str) if isinstance(compressed_str, str) else ctx
                    except Exception:
                        pass  # compression failure is non-fatal
                packet.context.update(ctx)
            else:
                packet.context["raw"] = ctx
        except Exception as exc:
            logger.debug("kernel.state02 context_fetch_failed %s", exc)
        return packet

    async def _state03_execute(self, packet: TaskPacket) -> Any:
        """Await LLM / tool turn with hard timeout."""
        try:
            return await asyncio.wait_for(
                self._agent_loop_fn(packet),
                timeout=self.turn_timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "kernel.state03 timeout task_id=%s timeout=%ss",
                packet.task_id, self.turn_timeout,
            )
            return None
        except Exception as exc:
            logger.error("kernel.state03 execute_error task_id=%s %s", packet.task_id, exc)
            return None

    async def _state04_audit_gc(self, packet: TaskPacket, result: Any) -> None:
        """AST audit + WAL commit + deterministic gen-0 GC.
        Runs as a separate asyncio task — never blocks the main loop.
        """
        try:
            if self.guardian and hasattr(self.guardian, "audit"):
                await asyncio.to_thread(self.guardian.audit, packet, result)
        except Exception as exc:
            logger.debug("kernel.state04 audit_error %s", exc)
        try:
            if self.memory and hasattr(self.memory, "wal_commit"):
                await asyncio.to_thread(self.memory.wal_commit, packet.task_id, result)
        except Exception as exc:
            logger.debug("kernel.state04 wal_commit_error %s", exc)
        # Deterministic gen-0 GC — <1ms, no stop-the-world pause
        del packet, result
        gc.collect(0)
