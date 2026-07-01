#!/usr/bin/env python3
"""
nina_search relay — semantic code/doc search via ollama embeddings + cosine sim.
Fallback: ripgrep-style grep when ollama unavailable.
Usage: python3 mcp/search_relay.py "<query>"
"""
import sys
import os
import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).parent.parent

def grep_fallback(query: str) -> list[dict]:
    """Fast grep-based fallback."""
    results = []
    try:
        out = subprocess.run(
            ["grep", "-rn", "--include=*.py", "--include=*.md",
             "-i", query,
             "--exclude-dir=.git", "--exclude-dir=venv",
             "--exclude-dir=logs", "--exclude-dir=.cache",
             str(REPO_ROOT)],
            capture_output=True, text=True, timeout=10
        )
        for line in out.stdout.splitlines()[:50]:
            parts = line.split(":", 2)
            if len(parts) >= 3:
                fpath, lineno, content = parts[0], parts[1], parts[2]
                results.append({
                    "file": fpath.replace(str(REPO_ROOT) + "/", ""),
                    "line": int(lineno),
                    "content": content.strip(),
                    "score": 1.0
                })
    except Exception as e:
        results.append({"error": str(e)})
    return results

def ollama_search(query: str) -> list[dict]:
    """Embed query + all .py/.md files, return top-10 cosine matches."""
    try:
        import numpy as np
    except ImportError:
        return grep_fallback(query)

    def embed(text: str) -> list[float]:
        r = subprocess.run(
            ["ollama", "embeddings", "--model", "nomic-embed-text", "--input", text[:2000]],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            return []
        return json.loads(r.stdout).get("embedding", [])

    q_vec = embed(query)
    if not q_vec:
        return grep_fallback(query)

    q_arr = np.array(q_vec)
    results = []

    for ext in ("*.py", "*.md"):
        for fp in REPO_ROOT.rglob(ext):
            if any(p in fp.parts for p in (".git", "venv", "logs", ".cache", "__pycache__")):
                continue
            try:
                text = fp.read_text(errors="ignore")[:3000]
                vec = embed(text)
                if not vec:
                    continue
                v_arr = np.array(vec)
                score = float(np.dot(q_arr, v_arr) / (np.linalg.norm(q_arr) * np.linalg.norm(v_arr) + 1e-9))
                results.append({
                    "file": str(fp.relative_to(REPO_ROOT)),
                    "score": round(score, 4),
                    "snippet": text[:300]
                })
            except Exception:
                continue

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        print(json.dumps({"error": "no query provided"}))
        sys.exit(1)

    try:
        subprocess.run(["ollama", "--version"], capture_output=True, timeout=3)
        hits = ollama_search(query)
    except Exception:
        hits = grep_fallback(query)

    print(json.dumps({"query": query, "hits": hits}, indent=2))
