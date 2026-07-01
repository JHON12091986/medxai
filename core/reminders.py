import json
import uuid
import os
import fcntl
from datetime import datetime, timedelta, timezone

DATA_FILE = "data/reminders.json"

def _load_data() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def _save_data(data: list) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_reminder(text: str, due_at: str, repeat: str = None) -> str:
    """Adds reminder, returns confirmation string with ID."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    # Simple parse/normalize repeat
    if repeat:
        repeat = repeat.lower().strip()
        if repeat not in ("daily", "weekly"):
            repeat = None

    # Check lock/write
    mode = 'r+' if os.path.exists(DATA_FILE) else 'w+'
    with open(DATA_FILE, mode) as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            content = f.read().strip()
            data = json.loads(content) if content else []
        except Exception:
            data = []
            
        rem_id = str(uuid.uuid4())[:8]
        entry = {
            "id": rem_id,
            "text": text,
            "due_at": due_at,
            "repeat": repeat,
            "fired": False
        }
        data.append(entry)
        
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()
        
    return f"✅ Reminder set! ID: {rem_id} | Text: '{text}' at {due_at} (repeat={repeat or 'none'})"

def list_reminders() -> str:
    """Returns formatted string of pending reminders."""
    if not os.path.exists(DATA_FILE):
        return "🔍 No reminders set."
        
    with open(DATA_FILE, 'r') as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            data = json.load(f)
        except Exception:
            return "🔍 Error loading reminders."
            
    pending = [r for r in data if not r.get("fired", False)]
    if not pending:
        return "🔍 No pending reminders."
        
    lines = ["🔔 Pending Reminders:"]
    for r in pending:
        rep_str = f" ({r.get('repeat')})" if r.get('repeat') else ""
        lines.append(f"• [{r.get('id')}] {r.get('due_at')}{rep_str}: {r.get('text')}")
    return "\n".join(lines)

def check_and_fire(send_fn) -> None:
    """
    Checks all reminders with due_at <= now() and fired=False.
    For each due reminder:
      - Calls send_fn(text) to deliver the Telegram message
      - Sets fired=True
      - If repeat=="daily": sets due_at += 1 day, fired=False
      - If repeat=="weekly": sets due_at += 7 days, fired=False
      - Persists changes to DATA_FILE
    """
    if not os.path.exists(DATA_FILE):
        return

    now_utc = datetime.now(timezone.utc)
    
    with open(DATA_FILE, 'r+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            content = f.read().strip()
            data = json.loads(content) if content else []
        except Exception:
            return
            
        updated = []
        changed = False
        
        for r in data:
            if r.get("fired", False):
                updated.append(r)
                continue
                
            try:
                # ISO 8601 UTC parse or naive parse
                due_str = r.get("due_at", "")
                if "T" in due_str:
                    due_dt = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
                else:
                    due_dt = datetime.fromisoformat(due_str)
                    
                if due_dt.tzinfo is None:
                    due_dt = due_dt.replace(tzinfo=timezone.utc)
                    
                if due_dt <= now_utc:
                    changed = True
                    # Fire!
                    # Deliver the message
                    import asyncio
                    msg = f"🔔 *PROACTIVE REMINDER*:\n{r.get('text')}"
                    if asyncio.iscoroutinefunction(send_fn):
                        asyncio.run(send_fn(msg))
                    else:
                        send_fn(msg)
                        
                    r["fired"] = True
                    
                    rep = r.get("repeat")
                    if rep == "daily":
                        next_dt = due_dt + timedelta(days=1)
                        # Instead of resetting fired=True on same item or creating new one, 
                        # let's reset it on the same item but advance due_at as specified:
                        r["due_at"] = next_dt.isoformat()
                        r["fired"] = False
                    elif rep == "weekly":
                        next_dt = due_dt + timedelta(weeks=1)
                        r["due_at"] = next_dt.isoformat()
                        r["fired"] = False
            except Exception:
                # Log or handle parsing exception
                pass
                
            updated.append(r)
            
        if changed:
            f.seek(0)
            json.dump(updated, f, indent=2)
            f.truncate()
