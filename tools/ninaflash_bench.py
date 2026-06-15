# tools/ninaflash_bench.py
# Module 10 — nf bench subcommand implementation
#
# Entry point: cmd_bench_run(args)
# Called from ninaflash.py dispatch as: nf bench [--provider X] [--prompts N] [--export] [--quiet]

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

_REPO_ROOT = Path(__file__).parent.parent

# ANSI colours (gracefully disabled on non-TTY)
_USE_COLOR = sys.stdout.isatty()

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text

_GREEN  = lambda t: _c("32", t)   # noqa: E731
_YELLOW = lambda t: _c("33", t)   # noqa: E731
_RED    = lambda t: _c("31", t)   # noqa: E731
_CYAN   = lambda t: _c("36", t)   # noqa: E731
_BOLD   = lambda t: _c("1",  t)   # noqa: E731
_DIM    = lambda t: _c("2",  t)   # noqa: E731


def _verdict_color(verdict: str) -> str:
    mapping = {
        "FAST":    _GREEN(verdict),
        "OK":      _YELLOW(verdict),
        "SLOW":    _RED(verdict),
        "TIMEOUT": _RED(verdict),
        "ERROR":   _RED(verdict),
    }
    return mapping.get(verdict, verdict)


def _delta_str(delta_ms: float) -> str:
    if abs(delta_ms) < 10:
        return _DIM("  ±0ms")
    sign  = "+" if delta_ms > 0 else ""
    color = _RED if delta_ms > 200 else (_YELLOW if delta_ms > 50 else _GREEN)
    return color(f"{sign}{delta_ms:.0f}ms")


def _spacing_advice(current: float, suggested: float) -> str:
    if abs(current - suggested) < 0.1:
        return _DIM("ok")
    if suggested < current:
        return _GREEN(f"{suggested}s ↓ tighten")
    return _YELLOW(f"{suggested}s ↑ relax")


def _print_table(results: list) -> None:
    """Print rich ASCII benchmark results table to stdout."""
    cols = [
        ("Provider",    18),
        ("Model",       24),
        ("TTFT avg",     9),
        ("TTFT p90",     9),
        ("tok/s avg",   10),
        ("tok/s p10",   10),
        ("vs baseline", 12),
        ("OK/Run",       7),
        ("Spacing",     17),
        ("Verdict",      9),
    ]
    sep  = "─" * (sum(w for _, w in cols) + len(cols) * 3 + 1)
    head = " │ ".join(f"{_BOLD(h):<{w}}" for h, w in cols)

    print()
    print(_BOLD(" NINA Provider Benchmark — nf bench"))
    print(_DIM(f" {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"))
    print(sep)
    print(f" {head} ")
    print(sep)

    for r in results:
        from core.bench_runner import ProviderBenchResult
        assert isinstance(r, ProviderBenchResult)

        ttft_avg = f"{r.ttft_avg_s:.3f}s" if r.ttft_avg_s >= 0 else _DIM("N/A")
        ttft_p90 = f"{r.ttft_p90_s:.3f}s" if r.ttft_p90_s >= 0 else _DIM("N/A")
        tps_avg  = f"{r.tps_avg:.1f}"   if r.tps_avg > 0  else _DIM("N/A")
        tps_p10  = f"{r.tps_p10:.1f}"   if r.tps_p10 > 0  else _DIM("N/A")
        ok_run   = f"{r.prompts_ok}/{r.prompts_run}"
        baseline = _delta_str(r.delta_vs_baseline_ms)
        spacing  = _spacing_advice(r.min_spacing_current_s, r.suggested_spacing_s)
        verdict  = _verdict_color(r.verdict)
        model    = r.model[:23]

        row = [
            (r.provider[:17], 18),
            (model,            24),
            (ttft_avg,          9),
            (ttft_p90,          9),
            (tps_avg,          10),
            (tps_p10,          10),
            (baseline,         12),
            (ok_run,            7),
            (spacing,          17),
            (verdict,           9),
        ]
        line = " │ ".join(f"{v:<{w}}" for v, w in row)
        print(f" {line} ")

    print(sep)
    print()


def _print_weight_suggestions(suggestions: dict) -> None:
    if not suggestions:
        print(_GREEN("  ✔ All provider spacings look healthy — no changes needed."))
        return
    print(_BOLD("  Routing weight suggestions:"))
    for pid, rec in suggestions.items():
        note = rec.get("note", "")
        new_s = rec.get("min_spacing_s", "?")
        print(f"    {_CYAN(pid)}: {note}  → set min_spacing_s={new_s} in providers.json")
    print()


def cmd_bench_run(args: "argparse.Namespace") -> None:
    """
    Main entry point for `nf bench`.
    Runs the benchmark suite and prints results to stdout.
    """
    provider_filter: list[str] | None = None
    if getattr(args, "provider", None):
        provider_filter = [p.strip().upper() for p in args.provider.split(",")]

    num_prompts: int = getattr(args, "prompts", 10)
    quiet:       bool = getattr(args, "quiet", False)
    do_export:   bool = getattr(args, "export", False)

    if not quiet:
        print(_DIM(f"  Starting benchmark: {num_prompts} prompts × "
                   f"{len(provider_filter) if provider_filter else 'all active'} providers ..."))
        print(_DIM("  (respecting min_spacing between requests — may take a few minutes)"))
        print()

    try:
        from core.bench_runner import run_bench, build_routing_weight_suggestions
    except ImportError as e:
        print(f"\u274c bench_runner import failed: {e}")
        sys.exit(1)

    results = asyncio.run(
        run_bench(
            providers_subset=provider_filter,
            num_prompts=num_prompts,
        )
    )

    if not results:
        print("  No active providers found. Is ninagate running on localhost:8080?")
        sys.exit(0)

    if quiet:
        # Machine-readable JSON output
        from dataclasses import asdict
        print(json.dumps([asdict(r) for r in results], indent=2))
        return

    _print_table(results)

    suggestions = build_routing_weight_suggestions(results)
    _print_weight_suggestions(suggestions)

    if do_export:
        ts   = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        out  = _REPO_ROOT / "logs" / f"bench_{ts}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        from dataclasses import asdict
        out.write_text(
            json.dumps([asdict(r) for r in results], indent=2),
            encoding="utf-8",
        )
        print(f"  ✔ Exported to {out}")
