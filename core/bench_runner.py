# core/bench_runner.py
# Module 10 — NinaGate Provider Benchmark Engine
#
# Fires a configurable prompt suite at every active provider and measures:
#   - TTFT  : time-to-first-token  (seconds, streaming)
#   - tok/s : token throughput     (tokens per second)
#   - delta : latency vs historical baseline (+/- ms)
#   - verdict: FAST / OK / SLOW / TIMEOUT based on thresholds
#
# Results are persisted to data/bench_history.json for trend tracking.
# Routing weight suggestions are derived from live TTFT vs providers.json min_spacing.
#
# Usage (programmatic):
#   from core.bench_runner import run_bench
#   results = await run_bench(providers_subset=["GROQ", "CEREBRAS"])

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger("nina.bench")

# ── Paths ───────────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).parent.parent
_HISTORY_FILE = _REPO_ROOT / "data" / "bench_history.json"
_PROVIDERS_FILE = _REPO_ROOT / "ninagate" / "providers.json"

# ── Thresholds ──────────────────────────────────────────────────────────────────
_TTFT_FAST_S    = 0.5   # <= 0.5s TTFT  → FAST
_TTFT_OK_S      = 2.0   # <= 2.0s TTFT  → OK
_TTFT_SLOW_S    = 5.0   # <= 5.0s TTFT  → SLOW  (> 5s → TIMEOUT)
_PROXY_BASE_URL = "http://localhost:8080"
_BENCH_TIMEOUT  = 15.0  # per-request timeout seconds

# ── 10-prompt benchmark suite ──────────────────────────────────────────────────────────
# Carefully chosen to be: short (fast to process), deterministic (no web search),
# representative of real NINA workloads (code, reasoning, factual recall).
_BENCH_PROMPTS: list[str] = [
    "Reply with exactly: pong",
    "What is 17 * 23? Reply with just the number.",
    "Complete: The capital of France is",
    "In Python, what does `x = x or []` do? One sentence.",
    "Name 3 sorting algorithms separated by commas. No explanation.",
    "What is the time complexity of binary search? One expression.",
    "Translate to French: Hello, how are you?",
    "What does HTTP stand for? Acronym expansion only.",
    "List 5 Python built-in functions as a comma-separated list.",
    "What is the output of: print(type(42))? Exact output only.",
]


# ── Data structures ───────────────────────────────────────────────────────────────────

@dataclass
class PromptResult:
    prompt_idx: int
    ttft_s: float           # time-to-first-token in seconds (-1 if timeout)
    total_s: float          # total wall time for complete response
    tokens_in: int          # input token count (estimated from prompt chars)
    tokens_out: int         # output token count (from response or stream count)
    tps: float              # tokens per second (tokens_out / total_s)
    error: Optional[str] = None


@dataclass
class ProviderBenchResult:
    provider:      str
    model:         str
    timestamp_utc: str
    prompts_run:   int
    prompts_ok:    int
    ttft_avg_s:    float   # average TTFT across successful prompts
    ttft_p90_s:    float   # 90th percentile TTFT
    tps_avg:       float   # average tokens/sec
    tps_p10:       float   # 10th percentile tok/s (worst-case throughput)
    verdict:       str     # FAST / OK / SLOW / TIMEOUT / ERROR
    delta_vs_baseline_ms: float   # +ms = slower, -ms = faster than historical avg
    min_spacing_current_s: float  # current value from providers.json
    suggested_spacing_s:   float  # suggested value based on live TTFT
    prompt_results: list[PromptResult] = field(default_factory=list)


# ── History I/O ───────────────────────────────────────────────────────────────────

def _load_history() -> dict:
    if _HISTORY_FILE.exists():
        try:
            return json.loads(_HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_history(history: dict) -> None:
    _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _get_baseline_ttft(history: dict, provider: str) -> Optional[float]:
    """Return the rolling average TTFT (seconds) from the last 5 runs."""
    runs: list[dict] = history.get(provider, [])
    if not runs:
        return None
    recent = runs[-5:]
    valid = [r["ttft_avg_s"] for r in recent if r.get("ttft_avg_s", -1) >= 0]
    return sum(valid) / len(valid) if valid else None


def _append_history(history: dict, result: ProviderBenchResult) -> None:
    """Keep last 20 runs per provider."""
    key = result.provider
    history.setdefault(key, [])
    history[key].append({
        "timestamp_utc":       result.timestamp_utc,
        "ttft_avg_s":          result.ttft_avg_s,
        "ttft_p90_s":          result.ttft_p90_s,
        "tps_avg":             result.tps_avg,
        "verdict":             result.verdict,
        "delta_vs_baseline_ms": result.delta_vs_baseline_ms,
    })
    history[key] = history[key][-20:]  # rolling window


# ── Provider config loader ──────────────────────────────────────────────────────────────────

def _load_providers_config() -> dict:
    if _PROVIDERS_FILE.exists():
        try:
            return json.loads(_PROVIDERS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _get_active_providers(config: dict, subset: list[str] | None = None) -> list[dict]:
    """
    Return provider records that:
    - have an api_key_env that is either null (keyless) or set in the env
    - are not in disabled_providers list
    - match the optional subset filter
    """
    import os
    disabled: set[str] = set(config.get("disabled_providers", []))
    active: list[dict] = []

    for p in config.get("providers", []):
        name = p.get("name", "").upper()
        if name in disabled:
            continue
        key_env = p.get("api_key_env")
        if key_env is not None and not os.environ.get(key_env):
            continue   # key required but not set
        if subset and name not in [s.upper() for s in subset]:
            continue
        active.append(p)

    return active


# ── Single-provider benchmark ─────────────────────────────────────────────────────────────────

async def _bench_provider(
    provider_cfg: dict,
    prompts: list[str],
    baseline_ttft: Optional[float],
) -> ProviderBenchResult:
    name  = provider_cfg.get("name", "UNKNOWN").upper()
    model = provider_cfg.get("default_model", "default")
    min_spacing_s = float(provider_cfg.get("min_spacing_s", 1.0))
    ts_utc = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    prompt_results: list[PromptResult] = []

    async with httpx.AsyncClient(base_url=_PROXY_BASE_URL, timeout=_BENCH_TIMEOUT) as client:
        for idx, prompt_text in enumerate(prompts):
            pr = await _bench_single_prompt(client, name, model, idx, prompt_text)
            prompt_results.append(pr)
            # Respect min_spacing between requests to avoid rate limit during bench
            if idx < len(prompts) - 1:
                await asyncio.sleep(min_spacing_s)

    ok_results = [r for r in prompt_results if r.error is None and r.ttft_s >= 0]

    if not ok_results:
        return ProviderBenchResult(
            provider=name, model=model, timestamp_utc=ts_utc,
            prompts_run=len(prompts), prompts_ok=0,
            ttft_avg_s=-1, ttft_p90_s=-1, tps_avg=0, tps_p10=0,
            verdict="ERROR", delta_vs_baseline_ms=0,
            min_spacing_current_s=min_spacing_s, suggested_spacing_s=min_spacing_s,
            prompt_results=prompt_results,
        )

    ttfts = sorted(r.ttft_s for r in ok_results)
    tps_list = sorted(r.tps for r in ok_results if r.tps > 0)

    ttft_avg = sum(ttfts) / len(ttfts)
    ttft_p90 = ttfts[int(len(ttfts) * 0.9)] if len(ttfts) >= 2 else ttfts[-1]
    tps_avg  = sum(tps_list) / len(tps_list) if tps_list else 0
    tps_p10  = tps_list[0] if tps_list else 0   # lowest = p10 (already sorted asc)

    # Verdict
    if ttft_avg <= _TTFT_FAST_S:
        verdict = "FAST"
    elif ttft_avg <= _TTFT_OK_S:
        verdict = "OK"
    elif ttft_avg <= _TTFT_SLOW_S:
        verdict = "SLOW"
    else:
        verdict = "TIMEOUT"

    # Delta vs historical baseline
    delta_ms = 0.0
    if baseline_ttft is not None:
        delta_ms = (ttft_avg - baseline_ttft) * 1000.0

    # Suggested spacing: round TTFT * 1.1 to nearest 0.5s, floor at 0.5s, ceil at 60s
    suggested_s = max(0.5, min(60.0, round(ttft_avg * 1.1 * 2) / 2))

    return ProviderBenchResult(
        provider=name, model=model, timestamp_utc=ts_utc,
        prompts_run=len(prompts), prompts_ok=len(ok_results),
        ttft_avg_s=round(ttft_avg, 3), ttft_p90_s=round(ttft_p90, 3),
        tps_avg=round(tps_avg, 1), tps_p10=round(tps_p10, 1),
        verdict=verdict, delta_vs_baseline_ms=round(delta_ms, 1),
        min_spacing_current_s=min_spacing_s, suggested_spacing_s=suggested_s,
        prompt_results=prompt_results,
    )


async def _bench_single_prompt(
    client: httpx.AsyncClient,
    provider: str,
    model: str,
    idx: int,
    prompt: str,
) -> PromptResult:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 64,
        "stream": True,
        "x_nina_provider": provider,  # NinaGate provider targeting header
    }
    tokens_in  = max(1, len(prompt) // 4)   # rough char-to-token estimate
    tokens_out = 0
    ttft_s     = -1.0
    t_start    = time.perf_counter()

    try:
        async with client.stream(
            "POST",
            "/v1/chat/completions",
            json=payload,
            headers={"X-Nina-Provider": provider},
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_lines():
                now = time.perf_counter()
                if not chunk or not chunk.startswith("data:"):
                    continue
                data = chunk[5:].strip()
                if data == "[DONE]":
                    break
                if ttft_s < 0:
                    ttft_s = now - t_start   # first real data chunk = TTFT
                try:
                    obj = json.loads(data)
                    delta = obj.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        tokens_out += max(1, len(content) // 4)
                except (json.JSONDecodeError, IndexError, KeyError):
                    pass

        total_s = time.perf_counter() - t_start
        if ttft_s < 0:
            ttft_s = total_s  # non-streaming fallback
        tps = tokens_out / total_s if total_s > 0 else 0.0

        return PromptResult(
            prompt_idx=idx, ttft_s=round(ttft_s, 3), total_s=round(total_s, 3),
            tokens_in=tokens_in, tokens_out=tokens_out, tps=round(tps, 1),
        )

    except httpx.TimeoutException:
        total_s = time.perf_counter() - t_start
        return PromptResult(
            prompt_idx=idx, ttft_s=-1, total_s=round(total_s, 3),
            tokens_in=tokens_in, tokens_out=0, tps=0,
            error="TIMEOUT",
        )
    except Exception as e:
        total_s = time.perf_counter() - t_start
        return PromptResult(
            prompt_idx=idx, ttft_s=-1, total_s=round(total_s, 3),
            tokens_in=tokens_in, tokens_out=0, tps=0,
            error=str(e)[:120],
        )


# ── Public API ───────────────────────────────────────────────────────────────────

async def run_bench(
    providers_subset: list[str] | None = None,
    num_prompts: int = 10,
) -> list[ProviderBenchResult]:
    """
    Run the full benchmark suite.

    Args:
        providers_subset: optional list of provider names to restrict the run.
                          None = all active providers.
        num_prompts:       number of prompts from BENCH_PROMPTS to use (1-10).

    Returns:
        List of ProviderBenchResult, one per provider tested, sorted TTFT asc.
    """
    cfg      = _load_providers_config()
    active   = _get_active_providers(cfg, providers_subset)
    history  = _load_history()
    prompts  = _BENCH_PROMPTS[:min(num_prompts, len(_BENCH_PROMPTS))]

    if not active:
        logger.warning("bench: no active providers found")
        return []

    results: list[ProviderBenchResult] = []
    for p_cfg in active:
        name     = p_cfg.get("name", "?").upper()
        baseline = _get_baseline_ttft(history, name)
        logger.info("bench: testing %s ...", name)
        result = await _bench_provider(p_cfg, prompts, baseline)
        _append_history(history, result)
        results.append(result)

    _save_history(history)

    # Sort by TTFT ascending (ERROR/TIMEOUT last)
    def _sort_key(r: ProviderBenchResult) -> tuple:
        order = {"FAST": 0, "OK": 1, "SLOW": 2, "TIMEOUT": 3, "ERROR": 4}
        return (order.get(r.verdict, 9), r.ttft_avg_s)

    results.sort(key=_sort_key)
    return results


def build_routing_weight_suggestions(results: list[ProviderBenchResult]) -> dict[str, dict]:
    """
    Build a dict of suggested routing weight overrides based on live TTFT.
    Intended to be pasted into providers.json or applied via HybridRouter.update_weights().
    """
    suggestions: dict[str, dict] = {}
    for r in results:
        if r.verdict in ("TIMEOUT", "ERROR"):
            suggestions[r.provider] = {
                "min_spacing_s": r.min_spacing_current_s,
                "health_bias":   -0.3,
                "note":          f"Demote: {r.verdict} during bench",
            }
        elif r.suggested_spacing_s != r.min_spacing_current_s:
            diff = r.suggested_spacing_s - r.min_spacing_current_s
            suggestions[r.provider] = {
                "min_spacing_s": r.suggested_spacing_s,
                "health_bias":   0.0,
                "note":          f"{'Tighten' if diff < 0 else 'Relax'} spacing: "
                                  f"{r.min_spacing_current_s}s → {r.suggested_spacing_s}s "
                                  f"(TTFT avg={r.ttft_avg_s:.2f}s)",
            }
    return suggestions
