#!/usr/bin/env python3
"""
NinaGate unified client — health check, model list, chat completion.
Usage:
  python3 tools/ninagate_client.py --health
  python3 tools/ninagate_client.py --models
  python3 tools/ninagate_client.py --chat "What is 2+2?" [--model auto]
NINA_FEATURE: ninagate-client v1.0
"""
import os, json, urllib.request, argparse, sys
from core.constants import ENV_OLLAMA_HOST, ENV_NINAGATE_URL

NINAGATE = os.getenv(ENV_NINAGATE_URL, "http://localhost:8080/v1")
OLLAMA   = os.getenv(ENV_OLLAMA_HOST,  "http://localhost:11434")

def _get(url, timeout=5):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read()), r.status
    except Exception as e:
        return {"error": str(e)}, 0

def _post(url, payload, timeout=30):
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data,
           headers={"Content-Type":"application/json","Authorization":"Bearer ninagate"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()), r.status
    except Exception as e:
        return {"error": str(e)}, 0

def health():
    ok = True
    # NinaGate
    ng, st = _get(f"{NINAGATE.rstrip('/v1')}/health")
    ng_ok = st == 200 and "error" not in ng
    print(f"NinaGate  [{NINAGATE}]: {'✓ OK' if ng_ok else '✗ DOWN'} {ng if not ng_ok else ''}")
    ok = ok and ng_ok
    # Ollama
    ol, st2 = _get(f"{OLLAMA}/api/tags")
    ol_ok = st2 == 200 and "models" in ol
    models = [m["name"] for m in ol.get("models",[])] if ol_ok else []
    print(f"Ollama    [{OLLAMA}]: {'✓ OK' if ol_ok else '✗ DOWN'}")
    if models:
        print(f"  Models: {', '.join(models[:8])}")
    ok = ok and ol_ok
    return 0 if ok else 1

def list_models():
    _post(f"{NINAGATE}/models", {})
    # Fallback: use Ollama tags
    ol, _ = _get(f"{OLLAMA}/api/tags")
    models = [m["name"] for m in ol.get("models",[])]
    print("Ollama models:", ", ".join(models) if models else "(none)")

def chat(prompt, model="auto"):
    payload = {
        "model": model,
        "messages":[{"role":"user","content":prompt}],
        "max_tokens":512,
        "stream":False
    }
    # Try NinaGate first
    r, st = _post(f"{NINAGATE}/chat/completions", payload)
    if st == 200 and "choices" in r:
        print(r["choices"][0]["message"]["content"])
        return 0
    # Fallback to Ollama direct
    print(f"[NinaGate unreachable ({st}), falling back to Ollama]", file=sys.stderr)
    payload2 = {"model": model if model != "auto" else "llama3.2",
                "prompt": prompt, "stream": False}
    r2, _ = _post(f"{OLLAMA}/api/generate", payload2)
    print(r2.get("response", r2))
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="NinaGate client CLI")
    ap.add_argument("--health",  action="store_true")
    ap.add_argument("--models",  action="store_true")
    ap.add_argument("--chat",    type=str, metavar="PROMPT")
    ap.add_argument("--model",   default="auto")
    args = ap.parse_args()

    if args.health:  sys.exit(health())
    elif args.models: list_models()
    elif args.chat:  sys.exit(chat(args.chat, args.model))
    else: ap.print_help()
