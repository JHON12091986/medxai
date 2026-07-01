import json
import uuid
import os
import fcntl
from datetime import datetime, timezone

DATA_FILE = "data/knowledge.json"

def remember(key: str, value: str) -> str:
    """
    Stores or overwrites an entry by key.
    Returns: "✅ Remembered: {key}"
    """
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    # whitespace-stripped key
    norm_key = key.strip().lower()
    
    mode = 'r+' if os.path.exists(DATA_FILE) else 'w+'
    with open(DATA_FILE, mode) as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            content = f.read().strip()
            data = json.loads(content) if content else []
        except Exception:
            data = []
            
        # Overwrite if key exists (case-insensitive compare)
        existing = None
        for entry in data:
            if entry.get("key", "").strip().lower() == norm_key:
                existing = entry
                break
                
        now_iso = datetime.now(timezone.utc).isoformat()
        if existing:
            existing["value"] = value
            existing["created_at"] = now_iso
        else:
            entry_id = str(uuid.uuid4())[:8]
            data.append({
                "id": entry_id,
                "key": key.strip(), # preserve original casing for key, but compare lowercased
                "value": value,
                "created_at": now_iso
            })
            
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
        
    return f"✅ Remembered: {key.strip()}"

def recall(query: str) -> str:
    """
    Searches entries where query (lowercased) is a substring of key or value.
    Returns formatted list of matches, or "🔍 Nothing found for: {query}"
    Format per match: "• [{id}] {key}: {value}  ({created_at[:10]})\n"
    """
    if not os.path.exists(DATA_FILE):
        return f"🔍 Nothing found for: {query}"
        
    with open(DATA_FILE, 'r') as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            data = json.load(f)
        except Exception:
            return "🔍 Error loading knowledge base."
            
    norm_query = query.strip().lower()
    matches = []
    for entry in data:
        k = entry.get("key", "").lower()
        v = entry.get("value", "").lower()
        if norm_query in k or norm_query in v:
            matches.append(entry)
            
    if not matches:
        return f"🔍 Nothing found for: {query}"
        
    lines = []
    for m in matches:
        created = m.get("created_at", "2026-06-16")[:10]
        lines.append(f"• [{m.get('id')}] {m.get('key')}: {m.get('value')}  ({created})")
        
    return "\n".join(lines)

def forget(key_or_id: str) -> str:
    """
    Removes entry matching key or id.
    Returns: "🗑️ Forgotten: {key}" or "Not found: {key_or_id}"
    """
    if not os.path.exists(DATA_FILE):
        return f"Not found: {key_or_id}"
        
    norm_target = key_or_id.strip().lower()
    
    with open(DATA_FILE, 'r+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            content = f.read().strip()
            data = json.loads(content) if content else []
        except Exception:
            return f"Not found: {key_or_id}"
            
        found_entry = None
        for entry in data:
            if entry.get("id", "").strip().lower() == norm_target or entry.get("key", "").strip().lower() == norm_target:
                found_entry = entry
                break
                
        if found_entry:
            data.remove(found_entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            return f"🗑️ Forgotten: {found_entry.get('key')}"
            
    return f"Not found: {key_or_id}"
