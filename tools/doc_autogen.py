import os
import re
import json
from datetime import datetime

def extract_facts():
    facts = {}
    
    # 1. MODEL from .gemini/settings.json
    try:
        with open(".gemini/settings.json", "r") as f:
            data = json.load(f)
            model_val = data.get("model", "unknown")
            if isinstance(model_val, dict):
                facts["MODEL"] = model_val.get("name", "unknown")
            else:
                facts["MODEL"] = str(model_val)
    except Exception as e:
        print(f"Error extracting MODEL: {e}")
        facts["MODEL"] = "unknown"

    # 2. NINAGATE_PORT from ninagate/main.py
    facts["NINAGATE_PORT"] = "8080" # Default
    try:
        with open("ninagate/main.py", "r") as f:
            content = f.read()
            match = re.search(r"port=(\d+)", content)
            if match:
                facts["NINAGATE_PORT"] = match.group(1)
    except Exception as e:
        print(f"Error extracting NINAGATE_PORT: {e}")

    # 3. PROVIDER_COUNT from core/router.py
    facts["PROVIDER_COUNT"] = 0
    try:
        with open("core/router.py", "r") as f:
            content = f.read()
            # Count "base_url": in the whole file as a proxy for provider count
            count = len(re.findall(r"\"base_url\":", content))
            facts["PROVIDER_COUNT"] = count
    except Exception as e:
        print(f"Error extracting PROVIDER_COUNT: {e}")

    # 4. DATE
    facts["DATE"] = datetime.now().strftime("%Y-%m-%d")
    
    return facts

def patch_file(file_path, pattern, replacement, facts):
    if not os.path.exists(file_path):
        print(f"SKIP: {file_path} not found")
        return False
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        final_replacement = replacement.format(**facts)
        
        if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
            print(f"SKIP: pattern not found in {file_path}")
            return False
        
        new_content = re.sub(pattern, final_replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        with open(file_path, "w") as f:
            f.write(new_content)
        
        print(f"PATCHED: {file_path}")
        return True
    except Exception as e:
        print(f"Error patching {file_path}: {e}")
        return False

def main():
    facts = extract_facts()
    patched = []

    # WORKFLOW.md updates
    if patch_file("WORKFLOW.md", 
                  r"(\| ninaflash \(agy\) \| )(.*?)(\s+\|)", 
                  r"\g<1>{MODEL}\g<3>", facts):
        patched.append("WORKFLOW.md (Model-Quota)")

    # docs/jules_agent_memory.md updates
    if patch_file("docs/jules_agent_memory.md", 
                  r"(\| agy \| )(.*?)(\s+\|)", 
                  r"\g<1>{MODEL}\g<3>", facts):
        patched.append("docs/jules_agent_memory.md (Model-Quota)")

    # docs/nina_proxy_usage.md updates
    if patch_file("docs/nina_proxy_usage.md", 
                  r"(http://localhost:)(\d+)", 
                  r"\g<1>{NINAGATE_PORT}", facts):
        patched.append("docs/nina_proxy_usage.md (Port)")

    # nina_update_log.md update
    try:
        with open("nina_update_log.md", "a") as f:
            f.write(f"\n## Auto-doc patch — {facts['DATE']}\n")
            f.write(f"- Model: {facts['MODEL']}, NinaGate: {facts['NINAGATE_PORT']}, Providers: {facts['PROVIDER_COUNT']}\n")
        patched.append("nina_update_log.md (Append)")
    except Exception as e:
        print(f"Error appending to log: {e}")

    print("\nSummary of Patches:")
    for p in patched:
        print(f" - {p}")
    print(f"Values used: MODEL={facts['MODEL']}, PORT={facts['NINAGATE_PORT']}, COUNT={facts['PROVIDER_COUNT']}")

if __name__ == "__main__":
    main()


# ── Signature drift detector (NINA enhancement patch) ────────────────────────
# NINA_FEATURE: doc-autogen-drift-detection v1.0

import ast as _ast, json as _json, hashlib as _hl
from pathlib import Path as _Path

_SIG_CACHE = _Path.home() / "nina" / ".cache" / "doc_sig_cache.json"

def _sig_hash(func_node) -> str:
    """Hash a function signature (name + args + return annotation)."""
    args = [a.arg for a in func_node.args.args]
    ret  = _ast.unparse(func_node.returns) if func_node.returns else ""
    raw  = f"{func_node.name}({','.join(args)})->{ret}"
    return _hl.md5(raw.encode()).hexdigest()[:10]

def check_doc_drift(py_files: list) -> list:
    """
    Return list of (file, func_name, status) where status is 'STALE', 'NEW', or 'OK'.
    STALE = signature changed since last doc gen run.
    NEW   = function has docstring but no cached signature.
    """
    cache = {}
    if _SIG_CACHE.exists():
        try: cache = _json.loads(_SIG_CACHE.read_text())
        except: pass

    new_cache = {}
    drift = []

    for path in py_files:
        path = _Path(path)
        if not path.exists(): continue
        try:
            tree = _ast.parse(path.read_text(errors="replace"))
        except:
            continue
        rel = str(path.relative_to(_Path.home()/"nina"))
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.FunctionDef): continue
            if not (_ast.get_docstring(node)): continue  # only tracked if has docstring
            h = _sig_hash(node)
            key = f"{rel}::{node.name}"
            new_cache[key] = h
            prev = cache.get(key)
            if prev is None:
                drift.append((rel, node.name, "NEW"))
            elif prev != h:
                drift.append((rel, node.name, "STALE"))

    _SIG_CACHE.parent.mkdir(exist_ok=True)
    _SIG_CACHE.write_text(_json.dumps(new_cache, indent=2))
    return drift

def print_drift_report(py_files: list):
    drift = check_doc_drift(py_files)
    stale = [d for d in drift if d[2] == "STALE"]
    new   = [d for d in drift if d[2] == "NEW"]
    if stale:
        print(f"\n⚠️  {len(stale)} STALE docstrings (signature changed):")
        for f, fn, _ in stale[:10]:
            print(f"  {f}::{fn}")
    if new:
        print(f"\nℹ️  {len(new)} NEW functions with docstrings (not yet baselined).")
    if not stale and not new:
        print("✓ All docstrings are in sync with signatures.")
    return stale
