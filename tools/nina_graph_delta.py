"""
Nina Context Graph — delta/append-only layer.
NINA_FEATURE: context-graph-delta v1.0
Wraps nina_context_graph.py to make rebuilds incremental.
Usage: python3 tools/nina_graph_delta.py [--apply]
"""
import json, time, hashlib
from pathlib import Path

REPO_ROOT  = Path.home() / "nina"
GRAPH_FILE = REPO_ROOT / "data" / "dependency_graph.json"
DELTA_FILE = REPO_ROOT / "data" / "dependency_graph_delta.jsonl"

def node_hash(node: dict) -> str:
    stable = json.dumps({k: node.get(k) for k in sorted(node) if k not in ("last_seen","removed_at")}, sort_keys=True)
    return hashlib.md5(stable.encode()).hexdigest()[:12]

def load_graph() -> dict:
    if GRAPH_FILE.exists():
        try: return json.loads(GRAPH_FILE.read_text())
        except: pass
    return {"nodes": {}, "edges": []}

def apply_delta(graph: dict, delta_entries: list) -> dict:
    """Apply a list of delta ops to a graph snapshot."""
    nodes = graph.get("nodes", {})
    for op in delta_entries:
        if op["op"] == "upsert":
            nodes[op["id"]] = op["data"]
        elif op["op"] == "remove":
            if op["id"] in nodes:
                nodes[op["id"]]["removed_at"] = op["ts"]
    graph["nodes"] = nodes
    return graph

def compute_deltas(old_nodes: dict, new_nodes: dict, ts: str) -> list:
    ops = []
    all_ids = set(old_nodes) | set(new_nodes)
    for nid in all_ids:
        if nid not in old_nodes:
            ops.append({"op": "upsert", "id": nid, "ts": ts, "data": new_nodes[nid]})
        elif nid not in new_nodes:
            ops.append({"op": "remove", "id": nid, "ts": ts})
        elif node_hash(old_nodes[nid]) != node_hash(new_nodes[nid]):
            ops.append({"op": "upsert", "id": nid, "ts": ts, "data": new_nodes[nid]})
    return ops

def write_delta(ops: list):
    with open(DELTA_FILE, "a") as f:
        for op in ops:
            f.write(json.dumps(op) + "\n")

def temporal_query(since_ts: str) -> list:
    """Return all node ops after since_ts (ISO string)."""
    if not DELTA_FILE.exists(): return []
    results = []
    with open(DELTA_FILE) as f:
        for line in f:
            try:
                op = json.loads(line)
                if op.get("ts", "") >= since_ts:
                    results.append(op)
            except: pass
    return results

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Apply pending deltas to graph")
    ap.add_argument("--since", help="Show ops since ISO timestamp (e.g. 2026-06-20T00:00:00)")
    args = ap.parse_args()

    graph = load_graph()
    if args.apply:
        if DELTA_FILE.exists():
            delta_entries = [json.loads(l) for l in DELTA_FILE.read_text().splitlines() if l.strip()]
            graph = apply_delta(graph, delta_entries)
            GRAPH_FILE.write_text(json.dumps(graph, indent=2))
            # Archive and reset delta log
            archive = DELTA_FILE.with_suffix(f".{int(time.time())}.jsonl")
            DELTA_FILE.rename(archive)
            print(f"✓ Applied {len(delta_entries)} delta ops. Archived to {archive.name}")
        else:
            print("No pending deltas.")
    elif args.since:
        ops = temporal_query(args.since)
        print(f"{len(ops)} ops since {args.since}:")
        for op in ops[-20:]:
            print(f"  {op['ts']} {op['op']:6s} {op['id']}")
    else:
        print(f"Graph: {len(graph.get('nodes', {}))} nodes | Delta log: {DELTA_FILE.name}")
        print(f"Run with --apply to merge deltas, --since TIMESTAMP for history")
