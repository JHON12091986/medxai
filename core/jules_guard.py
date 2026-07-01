import os
import re
import json
from datetime import datetime, timedelta
from tools.telegram_notify import send_message

BLOCKED_KEYWORDS = [".env", "secret", "token", "API_KEY", "credential", "password"]
STATE_FILE = "/home/aibony/nina/docs/space/nina_state.json"
AUDIT_LOG_FILE = "/home/aibony/nina/docs/space/nina_audit_log.jsonl"

def append_audit(entry: dict):
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.utcnow().isoformat()
    try:
        with open(AUDIT_LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

def requires_human_action(task_description: str) -> bool:
    # 1. Keyword Check
    blocked = any(kw in task_description.lower() for kw in BLOCKED_KEYWORDS)
    
    # 2. Regex Scan
    patterns = [
        r'[A-Fa-f0-9]{32,}',
        r'Bearer\s+\S+',
        r'bot:\d+:',
        r'sk-[A-Za-z0-9]+',
        r'AIza[A-Za-z0-9_-]+'
    ]
    
    secret_found = False
    redacted = task_description
    for pattern in patterns:
        matches = re.findall(pattern, redacted)
        if matches:
            secret_found = True
            for m in matches:
                redacted = redacted.replace(m, "[REDACTED]")
            # Alert
            send_message(f"⚠️ Security Alert: Confidential pattern match found and redacted in task: {pattern}")
            
    if blocked or secret_found:
        append_audit({"action": "block", "reason": "Confidential pattern or blocked keyword found in task description"})
        return True
    return False

def redact_secrets(task_description: str) -> str:
    patterns = [
        r'[A-Fa-f0-9]{32,}',
        r'Bearer\s+\S+',
        r'bot:\d+:',
        r'sk-[A-Za-z0-9]+',
        r'AIza[A-Za-z0-9_-]+'
    ]
    redacted = task_description
    for pattern in patterns:
        matches = re.findall(pattern, redacted)
        for m in matches:
            redacted = redacted.replace(m, "[REDACTED]")
    return redacted

def check_before_jules_submit(error_id: str, open_prs: list) -> bool:
    skip = any(error_id.lower() in (pr.get("title","") + pr.get("body","")).lower() for pr in open_prs)
    if skip:
        append_audit({"action": "skip", "error_id": error_id, "reason": "Already exists in open PRs"})
    return skip

def detect_loop(error_id: str) -> bool:
    # 1. Load state
    state_data = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                state_data = json.load(f)
        except Exception:
            pass
            
    # Check cooldown
    cooldowns = state_data.setdefault("cooldowns", {})
    now = datetime.utcnow()
    if error_id in cooldowns:
        try:
            expiry = datetime.fromisoformat(cooldowns[error_id])
            if now < expiry:
                append_audit({"action": "block", "error_id": error_id, "reason": "Blocked by active cooldown"})
                return True # loop blocked by cooldown
        except Exception:
            pass
            
    # Check attempts
    tracker = state_data.setdefault("jules_attempts_tracker", {})
    entry = tracker.setdefault(error_id, {"jules_attempts": 0, "last_attempt": None})
    
    # Check open PR matching error_id
    open_prs = state_data.get("open_prs", [])
    has_open_pr = any(error_id.lower() in str(pr).lower() for pr in open_prs)
    
    j_attempts = entry.get("jules_attempts", 0)
    last_attempt_str = entry.get("last_attempt")
    
    within_24h = False
    if last_attempt_str:
        try:
            last_attempt = datetime.fromisoformat(last_attempt_str)
            if now - last_attempt <= timedelta(hours=24):
                within_24h = True
        except Exception:
            pass
            
    if has_open_pr and j_attempts >= 2 and within_24h:
        # Send Telegram alert + set cooldown 48h
        send_message(f"🚨 Loop Detected for error: {error_id}. Active PR exists with {j_attempts} attempts within 24h. Activating 48h cooldown.")
        cooldown_expiry = now + timedelta(hours=48)
        cooldowns[error_id] = cooldown_expiry.isoformat()
        
        # Save state
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state_data, f, indent=2)
        except Exception:
            pass
        append_audit({"action": "block", "error_id": error_id, "reason": "Loop detected, activating cooldown"})
        return True
        
    # Otherwise, update tracker (record attempt)
    entry["jules_attempts"] = j_attempts + 1
    entry["last_attempt"] = now.isoformat()
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state_data, f, indent=2)
    except Exception:
        pass
        
    return False

def daily_dispatch_counter(increment: bool = True) -> bool:
    state_data = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                state_data = json.load(f)
        except Exception:
            pass
            
    # Auto reset at UTC midnight if date changed
    now = datetime.utcnow()
    last_date_str = state_data.get("last_dispatch_date")
    current_date_str = now.date().isoformat()
    
    if last_date_str != current_date_str:
        state_data["jules_dispatched_today"] = 0
        state_data["last_dispatch_date"] = current_date_str
        
    dispatched = state_data.get("jules_dispatched_today", 0)
    if dispatched >= 5:
        send_message("⚠️ Jules daily dispatch limit of 5/day reached. Blocking further dispatches.")
        append_audit({"action": "block", "reason": "Daily dispatch limit reached"})
        return True # Blocked
        
    if increment:
        state_data["jules_dispatched_today"] = dispatched + 1
        state_data["last_dispatch_date"] = current_date_str
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state_data, f, indent=2)
        except Exception:
            pass
        append_audit({"action": "dispatch", "count": dispatched + 1})
            
    return False

def validate_task_spec(task: str) -> dict:
    failures = []
    
    # 1. Single file path present
    paths = set()
    exts = ('.py', '.json', '.md', '.yml', '.yaml', '.sh', '.txt', '.js', '.ts', '.css', '.html', '.jsonl', '.template')
    for word in task.split():
        clean_word = word.strip(".,;:()[]'\"`*!?")
        if "/" in clean_word or "." in clean_word:
            if clean_word.endswith(exts) or ('/' in clean_word and not clean_word.startswith('http')):
                paths.add(clean_word)
    if len(paths) > 1:
        non_test_paths = {p for p in paths if not ('test_' in p or 'tests/' in p or '_test' in p)}
        if non_test_paths:
            paths = non_test_paths
    if len(paths) != 1:
        failures.append(f"Expected exactly one file path, found {len(paths)}: {list(paths)}")
        
    # 2. Line number or function name present
    has_line = bool(re.search(r'\b(?:line|lines|L)\s*#?\s*\d+\b', task, re.IGNORECASE)) or bool(re.search(r'\bL\d+\b', task))
    has_func = (
        bool(re.search(r'\b[a-zA-Z_][a-zA-Z0-9_]*\(\)', task)) or 
        bool(re.search(r'\b(?:function|method|def)\s+`?[a-zA-Z_][a-zA-Z0-9_]*`?\b', task, re.IGNORECASE)) or
        any(('_' in w and '.' not in w and not w.startswith('__') and not w.endswith('__') and re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', w)) for w in [word.strip(".,;:()[]'\"`*!?") for word in task.split()])
    )
    if not (has_line or has_func):
        failures.append("Neither line number nor function name is present in task spec")
        
    # 3. No secret keywords
    found_keywords = [kw for kw in BLOCKED_KEYWORDS if kw.lower() in task.lower()]
    if found_keywords:
        failures.append(f"Secret keywords found: {found_keywords}")
        
    # 4. Verify command present
    has_verify = any(kw in task.lower() for kw in ["verify", "pytest", "run", "command", "test"])
    if not has_verify:
        failures.append("Verify command or instruction is not present in task spec")
        
    # 5. Word count < 200
    word_count = len(task.split())
    if word_count >= 200:
        failures.append(f"Word count is {word_count}, must be less than 200")
        
    valid = len(failures) == 0
    if not valid:
        append_audit({"action": "block", "reason": f"Task specification validation failed: {failures}"})
        raise ValueError(f"Task specification validation failed: {failures}")
        
    return {
        "valid": valid,
        "failures": failures
    }
