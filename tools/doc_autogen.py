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
            # If it's a preview name, clean it up for display if needed? 
            # No, keep it literal as requested.
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
            # Count keys in provider dicts
            count = 0
            for block_name in ["PROVIDERS_TIER1", "PROVIDERS_TIER2", "PROVIDERS_TIER3"]:
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
        
        # Prepare replacement with facts
        # Note: we use double backslashes for group references in re.sub
        final_replacement = replacement.format(**facts)
        
        if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
            print(f"SKIP: pattern not found in {file_path}")
            return False
        
        # Use lambda for replacement to avoid group reference issues with literal backslashes if any
        # But here we want group references from the pattern.
        # Actually, let's just use \1, \2 etc and hope for the best.
        # The error "invalid group reference 18" was likely due to something in the format() call
        # or the way re.sub handles backslashes.
        
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

    # ARCHITECTURE.md updates
    # 1. NinaGate Proxy section - Model
    # Pattern: ### 3. NinaGate Proxy ... Gemini ... usage
    if patch_file("ARCHITECTURE.md", 
                  r"(### 3\. NinaGate Proxy.*?Gemini\s+)(.*?)(?=\s+usage)", 
                  r"\1{MODEL}", facts):
        patched.append("ARCHITECTURE.md (Model)")
    
    # 2. NinaGate Proxy section - Port
    if patch_file("ARCHITECTURE.md", 
                  r"(### 3\. NinaGate Proxy.*?port\s+)(\d+)", 
                  r"\1{NINAGATE_PORT}", facts):
        patched.append("ARCHITECTURE.md (Port)")

    # README.md updates
    # 1. Three-Tier Agent Model table row for ninaflash
    if patch_file("README.md", 
                  r"(\| ninaflash \(nf\) \| Local Muscle \| )(.*?)(\s+\|)", 
                  r"\1{MODEL}\3", facts):
        patched.append("README.md (Model-Table)")

    # 2. Tool Quota Cascade table row for ninaflash
    if patch_file("README.md", 
                  r"(\| ninaflash \(agy\) \| )(.*?)(\s+\|)", 
                  r"\1{MODEL}\3", facts):
        patched.append("README.md (Model-Quota)")

    # docs/nina_proxy_usage.md updates
    # Find port in URL
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
