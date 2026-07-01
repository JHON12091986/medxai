#!/usr/bin/env python3
"""
Nina Provider Benchmarker — pings each provider with a 10-token test prompt,
measures P50/P95 latency, rewrites ninagate/providers.json sorted by speed.
Usage: python3 tools/bench_providers.py [--dry-run] [--rounds N]
NINA_FEATURE: bench-providers v1.0
"""
import json, time, argparse, statistics, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
PROVIDERS_FILE = REPO_ROOT / "ninagate" / "providers.json"
NINAGATE_URL = "http://localhost:8080/v1"
TEST_PROMPT = "Reply with exactly: ok"
TEST_MODEL = "auto"


def ping_ninagate(provider_hint=None, timeout=15):
    payload = json.dumps({
        "model": TEST_MODEL,
        "messages": [{"role": "user", "content": TEST_PROMPT}],
        "max_tokens": 5,
        "_provider_hint": provider_hint,
    }).encode()
    headers = {"Content-Type": "application/json", "Authorization": "Bearer ninagate"}
    req = urllib.request.Request(f"{NINAGATE_URL}/chat/completions", data=payload, headers=headers)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        r.read()
    return round((time.time() - t0) * 1000, 1)


def load_providers():
    if PROVIDERS_FILE.exists():
        try:
            return json.loads(PROVIDERS_FILE.read_text())
        except Exception:
            pass
    return []


def benchmark(providers, rounds=3):
    results = []
    for p in providers:
        name = p.get("name", p.get("id", "unknown"))
        lats = []
        for _ in range(rounds):
            try:
                ms = ping_ninagate(provider_hint=name)
                lats.append(ms)
                time.sleep(0.3)
            except Exception as e:
                print(f"  ⚠️  {name}: {e}")
        if lats:
            p50 = statistics.median(lats)
            p95 = sorted(lats)[int(len(lats) * 0.95)] if len(lats) >= 2 else lats[-1]
            results.append((name, p50, p95, p, lats))
            print(f"  {name:25s}  p50={p50:.0f}ms  p95={p95:.0f}ms  samples={lats}")
        else:
            print(f"  {name:25s}  UNREACHABLE — skipped in ranking")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Benchmark NinaGate providers")
    ap.add_argument("--dry-run", action="store_true", help="Show ranking without rewriting providers.json")
    ap.add_argument("--rounds", type=int, default=3, help="Ping rounds per provider")
    args = ap.parse_args()

    providers = load_providers()
    if not providers:
        print(f"No providers found at {PROVIDERS_FILE}")
        exit(1)

    print(f"Benchmarking {len(providers)} providers ({args.rounds} rounds each)...")
    results = benchmark(providers, rounds=args.rounds)

    if not results:
        print("No results — is NinaGate running at localhost:8080?")
        exit(1)

    # Sort by p50 latency ascending (fastest first)
    results.sort(key=lambda x: x[1])
    ranked_providers = [r[3] for r in results]

    print("\nRanking (fastest → slowest):")
    for i, (name, p50, p95, _, _) in enumerate(results, 1):
        print(f"  {i}. {name:25s}  p50={p50:.0f}ms")

    if args.dry_run:
        print("\n[dry-run] providers.json NOT rewritten.")
    else:
        # Preserve non-benchmarked providers at end
        bench_names = {r[0] for r in results}
        remaining = [p for p in providers if p.get("name", p.get("id")) not in bench_names]
        final = ranked_providers + remaining
        # Add benchmark metadata
        meta = {
            "_last_bench": datetime.utcnow().isoformat() + "Z",
            "_bench_ranking": [r[0] for r in results],
        }
        output = {"meta": meta, "providers": final} if isinstance(providers, list) else final
        PROVIDERS_FILE.write_text(json.dumps(output if isinstance(output, dict) else final, indent=2))
        print(f"\n✓ providers.json rewritten with speed-ranked order.")
