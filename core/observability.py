"""
NINA Observability — Rich live TUI telemetry panel.
Reads from telemetry.jsonl and renders a live dashboard showing:
  - Task tree progress (OODA phases, status icons)
  - Per-provider quota and model routing
  - Hardware metrics (CPU / RAM / GPU via psutil)
  - Token budget tracking
  - Contradiction and rejection alerts

Usage (run in a separate terminal alongside agy):
    python3 -m core.observability

Part of NINA Swarm v1.
"""
from __future__ import annotations
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger("nina.observability")

class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"

@dataclass
class NinaMetrics:
    uptime_seconds: float = 0.0
    tasks_total: int = 0
    tasks_ok: int = 0
    tasks_fail: int = 0
    router_calls: int = 0
    last_sync_ts: str = ""
    last_health_check_ts: str = ""
    active_providers: list[str] = None
    error_rate: float = 0.0
    memory_mb: float = 0.0

    def __post_init__(self):
        if self.active_providers is None:
            self.active_providers = []

class ObservabilityHub:
    def __init__(self):
        self.metrics = NinaMetrics()
        self.start_time = time.time()

    def record_task(self, ok: bool):
        self.metrics.tasks_total += 1
        if ok:
            self.metrics.tasks_ok += 1
        else:
            self.metrics.tasks_fail += 1
        self.metrics.error_rate = self.metrics.tasks_fail / self.metrics.tasks_total if self.metrics.tasks_total > 0 else 0.0

    def record_router_call(self):
        self.metrics.router_calls += 1

    def set_sync_ts(self):
        from datetime import datetime, timezone
        self.metrics.last_sync_ts = datetime.now(timezone.utc).isoformat()

    def set_health_ts(self):
        from datetime import datetime, timezone
        self.metrics.last_health_check_ts = datetime.now(timezone.utc).isoformat()

    def set_active_providers(self, names: list[str]):
        self.metrics.active_providers = names

    def get_status(self) -> HealthStatus:
        if self.metrics.error_rate > 0.5:
            return HealthStatus.CRITICAL
        elif self.metrics.error_rate > 0.2:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def to_dict(self) -> dict:
        self.metrics.uptime_seconds = time.time() - self.start_time
        data = asdict(self.metrics)
        data["status"] = self.get_status().value
        return data

    def emit_log(self):
        logger.info(json.dumps(self.to_dict()))

_hub = None

def get_hub() -> ObservabilityHub:
    global _hub
    if _hub is None:
        _hub = ObservabilityHub()
    return _hub

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
    from rich.layout import Layout
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ── Paths ────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).parent.parent
TELEM_PATH = _ROOT / "telemetry.jsonl"
STATUS_ICONS = {
    "pending":  "[dim]○[/dim]",
    "active":   "[bold cyan]↻[/bold cyan]",
    "done":     "[bold green]✓[/bold green]",
    "failed":   "[bold red]✗[/bold red]",
    "rejected": "[bold yellow]⚠[/bold yellow]",
}
PHASE_COLORS = {
    "observe": "cyan",
    "orient":  "yellow",
    "decide":  "magenta",
    "act":     "green",
}


# ── State accumulator ───────────────────────────────────────────────────────────

class TelemetryState:
    def __init__(self):
        self.root_goal: str = "(waiting for task...)"
        self.nodes: Dict[str, Dict] = {}   # task_id → latest telemetry snapshot
        self.total_tokens: int = 0
        self.token_budget: int = 40_000
        self.provider_usage: Dict[str, int] = defaultdict(int)
        self.swarm_active: bool = False
        self.contradictions: List[Any] = []
        self.alerts: List[str] = []
        self._file_pos: int = 0

    def refresh(self):
        """Read any new lines from telemetry.jsonl."""
        if not TELEM_PATH.exists():
            return
        try:
            with open(TELEM_PATH, "r") as f:
                f.seek(self._file_pos)
                for raw in f:
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        ev = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    self._process(ev)
                self._file_pos = f.tell()
        except Exception:
            pass

    def _process(self, ev: Dict):
        event = ev.get("event", "")

        if event == "plan_ready":
            self.root_goal = ev.get("root_goal", self.root_goal)
            self.swarm_active = True

        elif event == "swarm_start":
            self.root_goal = ev.get("root_goal", self.root_goal)
            self.swarm_active = True
            self.nodes.clear()

        elif event in ("node_start", "node_done", "node_rejected",
                       "node_error", "node_deadlock"):
            nid = ev.get("id")
            if nid:
                self.nodes[nid] = ev
                # Track provider usage
                provider = ev.get("provider")
                if provider and event == "node_done":
                    self.provider_usage[provider] += 1
                    self.total_tokens += ev.get("tokens", 0)

        elif event == "contradictions_detected":
            self.contradictions = ev.get("pairs", [])
            if self.contradictions:
                self.alerts.append(
                    f"[yellow]⚠ {len(self.contradictions)} contradiction(s) detected[/yellow]"
                )

        elif event == "swarm_done":
            self.swarm_active = False
            done = ev.get("done", 0)
            failed = ev.get("failed", 0)
            self.alerts.append(
                f"[green]✓ Swarm complete: {done} done, {failed} failed[/green]"
            )


# ── Hardware snapshot ───────────────────────────────────────────────────────────

def _hw_snapshot() -> Dict[str, str]:
    if not PSUTIL_AVAILABLE:
        return {"cpu": "n/a", "ram": "n/a", "gpu": "n/a"}
    cpu = f"{psutil.cpu_percent(interval=None):.0f}%"
    ram = psutil.virtual_memory()
    ram_str = f"{ram.used / 1e9:.1f}/{ram.total / 1e9:.1f} GB"
    # GPU via nvidia-smi if available
    gpu_str = "n/a"
    try:
        import subprocess
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            timeout=1, stderr=subprocess.DEVNULL
        ).decode().strip().split("\n")[0]
        util, used, total = [x.strip() for x in out.split(",")]
        gpu_str = f"{util}% | {int(used)//1024}/{int(total)//1024} GB VRAM"
    except Exception:
        pass
    return {"cpu": cpu, "ram": ram_str, "gpu": gpu_str}


# ── Rich panel builder ───────────────────────────────────────────────────────────

def _build_panel(state: TelemetryState) -> Panel:
    lines: List[str] = []

    # ─ Header
    status_label = "[bold cyan]↻ ACTIVE[/bold cyan]" if state.swarm_active \
                   else "[dim]idle[/dim]"
    lines.append(f"[bold]ROOT TASK:[/bold] {state.root_goal[:80]}  {status_label}")
    lines.append("")

    # ─ Task nodes table
    if state.nodes:
        done  = sum(1 for n in state.nodes.values() if n.get("status") == "done")
        total = len(state.nodes)
        pct   = int(done / total * 100) if total else 0
        bar   = "▄" * (pct // 5) + "░" * (20 - pct // 5)
        lines.append(f"[bold]PROGRESS:[/bold] [{bar}] {pct}%  {done}/{total} tasks")
        lines.append("")

        for nid, n in list(state.nodes.items()):
            status  = n.get("status", "pending")
            icon    = STATUS_ICONS.get(status, "○")
            label   = n.get("label", nid)[:45]
            phase   = n.get("phase", "observe")
            phase_c = PHASE_COLORS.get(phase, "white")
            prov    = n.get("provider") or ""
            elapsed = n.get("elapsed", 0)
            score   = n.get("score", 1.0)
            score_s = f"[dim]score:{score:.2f}[/dim]" if status == "rejected" else ""
            lines.append(
                f"  {icon} [{phase_c}]{phase.upper()[:3]}[/{phase_c}] "
                f"{label:<45} "
                f"[dim]{prov:<12}[/dim] "
                f"[dim]{elapsed:.0f}s[/dim] {score_s}"
            )
    else:
        lines.append("  [dim](no tasks yet — waiting for swarm...)[/dim]")

    lines.append("")

    # ─ Hardware
    hw = _hw_snapshot()
    lines.append(
        f"[bold]HARDWARE[/bold] │ CPU {hw['cpu']} │ RAM {hw['ram']} │ GPU {hw['gpu']}"
    )

    # ─ Tokens
    token_pct = int(state.total_tokens / state.token_budget * 100) if state.token_budget else 0
    lines.append(
        f"[bold]TOKENS  [/bold] │ Used: {state.total_tokens:,} │ "
        f"Budget: {state.token_budget:,} │ [{token_pct}%]"
    )

    # ─ Provider usage
    if state.provider_usage:
        prov_str = "  ".join(
            f"{p}:{c}" for p, c in sorted(
                state.provider_usage.items(), key=lambda x: -x[1]
            )[:6]
        )
        lines.append(f"[bold]PROVIDERS[/bold] │ {prov_str}")

    # ─ Alerts
    if state.alerts:
        lines.append("")
        for a in state.alerts[-3:]:
            lines.append(f"  {a}")

    body = "\n".join(lines)
    return Panel(
        body,
        title="[bold magenta]★ NINA SWARM TELEMETRY ★[/bold magenta]",
        border_style="bright_black",
        box=box.ROUNDED,
    )


# ── Daemon loop ─────────────────────────────────────────────────────────────────

def run_daemon(refresh_rate: float = 1.0):
    """
    Runs the live TUI panel in the terminal.
    Launch in a separate terminal: python3 -m core.observability
    """
    if not RICH_AVAILABLE:
        print("[NINA telemetry] rich not installed. Run: pip install rich", file=sys.stderr)
        sys.exit(1)

    console = Console()
    state   = TelemetryState()

    console.print("[bold magenta]NINA Swarm Telemetry[/bold magenta] — watching telemetry.jsonl")
    console.print(f"[dim]File: {TELEM_PATH}[/dim]")
    console.print("[dim]Press Ctrl+C to exit.[/dim]\n")

    try:
        with Live(_build_panel(state), console=console,
                  refresh_per_second=int(1 / refresh_rate)) as live:
            while True:
                state.refresh()
                live.update(_build_panel(state))
                time.sleep(refresh_rate)
    except KeyboardInterrupt:
        console.print("\n[dim]Telemetry daemon stopped.[/dim]")


# ── Lightweight emit helper (imported by other modules) ──────────────────────────

def emit(event: str, data: Dict[str, Any]):
    """Write a telemetry event. Safe to call from any thread/coroutine."""
    entry = {"event": event, "ts": time.time(), **data}
    try:
        with open(TELEM_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_daemon()
