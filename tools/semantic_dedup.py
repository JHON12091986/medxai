#!/usr/bin/env python3
"""
Nina semantic duplicate detector — Ollama + MX150 CUDA layer.
Runs AFTER hash dedup: finds near-duplicates (renamed, reformatted, salvageable dead code).
Usage: python3 tools/semantic_dedup.py [--threshold 0.92] [--ext .py .sh .md]
NINA_FEATURE: semantic-dedup-gpu v1.0
Requires: ollama running, nomic-embed-text pulled
"""
import os, json, argparse, itertools
from pathlib import Path
<<<<<<< Updated upstream
from core.constants import ENV_OLLAMA_HOST
=======
from core.constants import (ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID, ENV_API_SECRET_KEY, ENV_OPENAI_API_KEY, ENV_CEREBRAS_API_KEY, ENV_GROQ_API_KEY, ENV_GEMINI_API_KEY, ENV_MISTRAL_API_KEY, ENV_OPENROUTER_API_KEY, ENV_DEEPSEEK_API_KEY, ENV_PERPLEXITY_API_KEY, ENV_TOGETHER_API_KEY, ENV_COHERE_API_KEY, ENV_FIREWORKS_API_KEY, ENV_XAI_API_KEY, ENV_SAMBANOVA_API_KEY, ENV_HYPERBOLIC_API_KEY, ENV_NOVITA_API_KEY, ENV_OLLAMA_HOST, ENV_EWS_USERNAME, ENV_EWS_MY_EMAIL, ENV_EWS_SHARED_EMAIL)
>>>>>>> Stashed changes

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_FILE = REPO_ROOT / ".cache" / "semantic_embed_cache.json"
IGNORE_DIRS = {'.git','venv','.cache','__pycache__','node_modules','archive'}
OLLAMA_URL = os.getenv(ENV_OLLAMA_HOST, "http://localhost:11434")

def get_embedding(text: str, model="nomic-embed-text") -> list[float]:
    import urllib.request, json as _json
    payload = _json.dumps({"model": model, "prompt": text}).encode()
    req = urllib.request.Request(f"{OLLAMA_URL}/api/embeddings",
                                  data=payload, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return _json.loads(r.read())["embedding"]

def cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = sum(x*x for x in a)**0.5
    nb = sum(x*x for x in b)**0.5
    return dot/(na*nb) if na and nb else 0.0

def collect_files(exts):
    for p in REPO_ROOT.rglob('*'):
        if not p.is_file(): continue
        if any(d in p.parts for d in IGNORE_DIRS): continue
        if p.suffix not in exts: continue
        if p.stat().st_size > 50_000: continue  # skip huge files
        yield p

def load_embed_cache():
    if CACHE_FILE.exists():
        try: return json.loads(CACHE_FILE.read_text())
        except: pass
    return {}

def save_embed_cache(c):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(c))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--threshold', type=float, default=0.92, help='Similarity threshold (0-1)')
    ap.add_argument('--ext', nargs='+', default=['.py','.sh','.md'], help='File extensions to scan')
    ap.add_argument('--model', default='nomic-embed-text')
    args = ap.parse_args()

    cache = load_embed_cache()
    files = list(collect_files(set(args.ext)))
    print(f"Embedding {len(files)} files via {args.model} (cached entries reused)...")

    embeds = {}
    for i, p in enumerate(files):
        rel = str(p.relative_to(REPO_ROOT))
        stat = p.stat()
        ck = f"{rel}:{stat.st_mtime}:{stat.st_size}"
        if ck in cache:
            embeds[rel] = cache[ck]
        else:
            try:
                text = p.read_text(errors='replace')[:4096]  # truncate to ~1k tokens
                embeds[rel] = get_embedding(text, args.model)
                cache[ck] = embeds[rel]
                if i % 20 == 0: save_embed_cache(cache)
                print(f"  [{i+1}/{len(files)}] embedded {rel}")
            except Exception as e:
                print(f"  ⚠️  skip {rel}: {e}")
    save_embed_cache(cache)

    # Compare all pairs
    keys = list(embeds.keys())
    pairs = [(a, b, cosine(embeds[a], embeds[b]))
             for a, b in itertools.combinations(keys, 2)
             if cosine(embeds[a], embeds[b]) >= args.threshold]
    pairs.sort(key=lambda x: -x[2])

    if pairs:
        print(f"\n⚠️  {len(pairs)} near-duplicate pairs (threshold={args.threshold}):")
        for a, b, score in pairs:
            print(f"  {score:.3f}  {a}  ↔  {b}")
    else:
        print(f"\n✓ No near-duplicates above threshold {args.threshold}")
