"""Reflexion memory — when NINA receives negative feedback (thumbs-down or correction), logs the failed reasoning trace to memory/reflexion_log.jsonl for use as few-shot negative examples in future similar queries."""

import json
import logging
import os
import time
import pathlib

REFLEXION_LOG_PATH = pathlib.Path(os.path.dirname(__file__)).parent.parent / 'memory' / 'reflexion_log.jsonl'

def ensure_log_dir() -> None:
    """Create memory/ directory if it does not exist."""
    REFLEXION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_negative_trace(query: str, bad_response: str, user_correction: str = '', model_used: str = 'unknown') -> None:
    """Append a failed reasoning trace to reflexion_log.jsonl. Called when user signals negative feedback."""
    ensure_log_dir()
    entry = {
        "timestamp": time.time(),
        "query": query,
        "bad_response": bad_response[:500],
        "user_correction": user_correction[:300],
        "model_used": model_used
    }
    with open(REFLEXION_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
    logging.warning(f"[reflexion] negative trace logged for query: {query[:60]}...")

def get_negative_examples(query: str, *, max_examples: int = 3) -> list[dict]:
    """Load up to max_examples recent negative traces from reflexion_log.jsonl. Returns list of dicts with keys query, bad_response, user_correction. Returns empty list if log does not exist."""
    if not REFLEXION_LOG_PATH.exists():
        return []
    
    try:
        with open(REFLEXION_LOG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Read last 200 lines
        lines_to_parse = lines[-200:]
        entries = []
        for line in lines_to_parse:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                entries.append(json.loads(line_str))
            except Exception:
                pass
        
        # Most recent first
        entries.reverse()
        return entries[:max_examples]
    except Exception as e:
        logging.warning(f"Error reading reflexion log: {e}")
        return []

def build_reflexion_context(query: str) -> str:
    """Return a formatted string of negative examples to prepend to a system prompt. Empty string if no examples exist."""
    examples = get_negative_examples(query)
    if not examples:
        return ''
    
    lines = ['[NINA REFLEXION — Past mistakes to avoid:]']
    for ex in examples:
        lines.append(f'- Query like: {ex.get("query", "")[:80]}')
        lines.append(f'  Bad answer was: {ex.get("bad_response", "")[:120]}')
        if ex.get("user_correction"):
            lines.append(f'  Correct approach: {ex.get("user_correction", "")[:120]}')
    return '\n'.join(lines) + '\n'
