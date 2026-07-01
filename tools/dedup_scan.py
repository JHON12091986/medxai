#!/usr/bin/env python3
"""
Nina incremental duplicate scanner — hash cache layer.
Cache lives at .cache/dedup_cache.json
Usage: python3 tools/dedup_scan.py [--full] [--json]
NINA_FEATURE: incremental-dedup-scanner v1.0
"""
import os, json, hashlib, time, argparse
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_FILE = REPO_ROOT / ".cache" / "dedup_cache.json"
IGNORE_DIRS = {'.git','venv','.venv','.cache','__pycache__','node_modules','.mypy_cache','archive','upgrades'}
IGNORE_EXT  = {'.pyc','.pyo','.so','.egg-info'}

def file_key(p: Path):
    s = p.stat()
    return (str(p.relative_to(REPO_ROOT)), s.st_mtime, s.st_size)

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def load_cache():
    if CACHE_FILE.exists():
        try: return json.loads(CACHE_FILE.read_text())
        except: pass
    return {}

def save_cache(cache):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))

def scan(full=False):
    cache = {} if full else load_cache()
    new_cache = {}
    hash_to_files = defaultdict(list)
    scanned = stale = 0

    for p in REPO_ROOT.rglob('*'):
        if not p.is_file() or p.is_symlink(): continue
        if any(d in p.parts for d in IGNORE_DIRS): continue
        if p.suffix in IGNORE_EXT: continue
        if p.stat().st_size < 32: continue

        rel = str(p.relative_to(REPO_ROOT))
        scanned += 1
        key = file_key(p)
        cache_entry = cache.get(rel)
        # Reuse cache if mtime+size unchanged
        if cache_entry and cache_entry['mtime'] == key[1] and cache_entry['size'] == key[2]:
            h = cache_entry['hash']
        else:
            h = sha256(p)
            stale += 1
        new_cache[rel] = {'hash': h, 'mtime': key[1], 'size': key[2]}
        hash_to_files[h].append(rel)

    save_cache(new_cache)
    dupes = {h: files for h, files in hash_to_files.items() if len(files) > 1}
    return dupes, scanned, stale

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--full', action='store_true', help='Ignore cache, rehash everything')
    ap.add_argument('--json', action='store_true', help='Output JSON')
    args = ap.parse_args()

    t0 = time.time()
    dupes, scanned, stale = scan(full=args.full)
    elapsed = time.time() - t0

    if args.json:
        print(json.dumps({'dupes': dupes, 'scanned': scanned, 'stale': stale, 'elapsed_s': round(elapsed,2)}, indent=2))
    else:
        print(f"Scanned {scanned} files ({stale} rehashed) in {elapsed:.1f}s")
        if dupes:
            print(f"\n⚠️  {len(dupes)} duplicate content groups:")
            for h, files in dupes.items():
                print(f"  [{h[:8]}] {', '.join(files)}")
        else:
            print("✓ No exact duplicates found.")
