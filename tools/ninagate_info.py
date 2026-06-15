import sys
import os
import json
import datetime
import urllib.request
from dotenv import load_dotenv

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_info():
    load_dotenv()

    providers_path = 'ninagate/providers.json'
    providers = []
    if os.path.exists(providers_path):
        with open(providers_path, 'r') as f:
            providers = json.load(f)

    try:
        from core.config import RATELIMITS
    except ImportError as e:
        RATELIMITS = {}

    quota_path = 'data/quota_state.json'
    quota_state = {}
    if os.path.exists(quota_path):
        with open(quota_path, 'r') as f:
            quota_state = json.load(f)

    ninagate_models = []
    try:
        with urllib.request.urlopen('http://localhost:8080/v1/models', timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
            ninagate_models = data.get('data', [])
    except Exception as e:
        pass

    models_by_provider = {}
    for m in ninagate_models:
        owned = m.get('owned_by')
        models_by_provider[owned] = models_by_provider.get(owned, []) + [m.get('id')]

    print("# Ninagate Status Report")
    print()
    print("## Quota Usage & Timer Reset Details")
    
    quotas = quota_state.get('quotas', {})
    last_reset_ts = quota_state.get('last_reset', 0.0)
    quota_exhausted = quota_state.get('quota_exhausted', False)
    
    dt_reset = datetime.datetime.fromtimestamp(last_reset_ts, datetime.timezone.utc)
    dt_reset_bd = dt_reset + datetime.timedelta(hours=6)
    
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    recent_reset = now_utc.replace(hour=7, minute=0, second=0, microsecond=0)
    if now_utc >= recent_reset:
        next_reset = recent_reset + datetime.timedelta(days=1)
    else:
        next_reset = recent_reset
    next_reset_bd = next_reset + datetime.timedelta(hours=6)
    time_to_reset = next_reset - now_utc
    
    print(f"- **Daily Request Cap**: 900 requests per provider (Gemini soft-limit config)")
    print(f"- **Gemini Request Usage**: {quotas.get('gemini', 0)} / 900 requests used")
    print(f"- **Quota Exhausted Status**: `{quota_exhausted}`")
    print(f"- **Last Reset Time**: {dt_reset_bd.strftime('%Y-%m-%d %I:%M:%S %p')} BD local time ({dt_reset.strftime('%H:%M:%S')} UTC)")
    print(f"- **Next Reset Time**: {next_reset_bd.strftime('%Y-%m-%d %I:%M:%S %p')} BD local time (in {str(time_to_reset).split('.')[0]})")
    print()

    print("## Model Providers Status")
    print("| Provider | Status | Key Configured? | Tier | Context Window | RPM Limit | Min Spacing | Active Models Count | Default Model |")
    print("|---|---|---|---|---|---|---|---|---|")
    
    for p in providers:
        name = p['name']
        key_env = p.get('api_key_env')
        key_configured = False
        if key_env:
            key_configured = os.getenv(key_env) is not None
        else:
            key_configured = True if name == 'OLLAMA' else False
        
        status = "Active"
        if key_env and not key_configured:
            status = "Disabled (Missing Key)"
        elif not key_env and name != 'OLLAMA':
            status = "Skipped (No Key config)"
            
        tier = p.get('tier', 2)
        ctx = p.get('context_window', 8192)
        
        rl = RATELIMITS.get(name, {})
        rpm = rl.get('rpm', 'N/A')
        spacing = rl.get('min_spacing_s', 'N/A')
        if spacing != 'N/A':
            spacing = f"{spacing}s"
            
        models_count = len(models_by_provider.get(name, []))
        default_model = p.get('model', 'N/A')
        
        print(f"| **{name}** | {status} | `{key_configured}` | Tier {tier} | {ctx:,} | {rpm} | {spacing} | {models_count} | `{default_model}` |")

if __name__ == '__main__':
    get_info()
