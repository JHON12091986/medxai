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
