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
            facts["MODEL"] = data.get("model", "unknown")
    except Exception as e:
        print(f"Error extracting MODEL: {e}")
        facts["MODEL"] = "unknown"

    # 2. NINAGATE_PORT from ninagate/main.py
    facts["NINAGATE_PORT"] = "8080" # Default
    try:
        with open("ninagate/main.py", "r") as f:
            content = f.read()
            match = re.search(r"uvicorn\.run\(app, host=\".*?\", port=(\d+)\)", content)
            if match:
                facts["NINAGATE_PORT"] = match.group(1)
    except Exception as e:
        print(f"Error extracting NINAGATE_PORT: {e}")

    # 3. PROVIDER_COUNT from core/router.py
    facts["PROVIDER_COUNT"] = 0
    try:
        with open("core/router.py", "r") as f:
            content = f.read()
            # Count keys in PROVIDERS_TIER1, 2, 3 and LOCAL_PROVIDERS
            # Pattern: "KEY": {
            tier1 = len(re.findall(r"PROVIDERS_TIER1 = \{", content))
            tier2 = len(re.findall(r"PROVIDERS_TIER2 = \{", content))
            tier3 = len(re.findall(r"PROVIDERS_TIER3 = \{", content))
            local = len(re.findall(r"LOCAL_PROVIDERS = \{", content))
            
            # Simple count of dictionary items
            p_matches = re.findall(r"\"[A-Z0-9]+\": \{", content)
            # Filter to only those inside the provider dicts
            # Actually, let's just count occurrences of base_url or model inside those blocks
            # But the requirement is simple. Let's just count keys in those blocks.
            count = 0
            for block_name in ["PROVIDERS_TIER1", "PROVIDERS_TIER2", "PROVIDERS_TIER3", "LOCAL_PROVIDERS"]:
                block_match = re.search(fr"{block_name} = \{{(.*?)\}}", content, re.DOTALL)
                if block_match:
                    items = re.findall(r"\"[A-Z0-9]+\": \{", block_match.group(1))
                    count += len(items)
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
        
        # Injected values
        final_replacement = replacement.format(**facts)
        
        if not re.search(pattern, content, re.MULTILINE):
            print(f"SKIP: pattern not found in {file_path}")
            return False
        
        new_content = re.sub(pattern, final_replacement, content, flags=re.MULTILINE)
        
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

    # ARCHITECTURE.md updates
    # Replace model name in NinaGate section
    if patch_file("ARCHITECTURE.md", 
                  r"(### 3\. NinaGate Proxy.*?Gemini\s+)([\w\-\.]+)(\s+Flash)", 
                  r"\1{MODEL}\3", facts):
        patched.append("ARCHITECTURE.md (Model)")
    
    # Replace port number
    if patch_file("ARCHITECTURE.md", 
                  r"(### 3\. NinaGate Proxy.*?port\s+)(\d+)", 
                  r"\1{NINAGATE_PORT}", facts):
        patched.append("ARCHITECTURE.md (Port)")

    # README.md updates
    # Replace model name in ninaflash row
    if patch_file("README.md", 
                  r"(\| ninaflash \(nf\) \| Local Muscle \| )([\w\-\.]+)(\s+\|)", 
                  r"\1{MODEL}\3", facts):
        patched.append("README.md (Model)")

    # docs/nina_proxy_usage.md updates
    # The requirement said "Find the 'Current model:' line or equivalent"
    # Let's try to find a model string or port string.
    if patch_file("docs/nina_proxy_usage.md", 
                  r"(Current model:\s+)([\w\-\.]+)", 
                  r"\1{MODEL}", facts):
        patched.append("docs/nina_proxy_usage.md (Model)")
    elif patch_file("docs/nina_proxy_usage.md", 
                    r"(model string is\s+`)([\w\-\.]+)(`)", 
                    r"\1{MODEL}\3", facts):
        patched.append("docs/nina_proxy_usage.md (Model-code)")

    # Update port if found
    if patch_file("docs/nina_proxy_usage.md", 
                  r"(http://localhost:)(\d+)", 
                  r"\1{NINAGATE_PORT}", facts):
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
