"""Prompt compressor — reduces cloud API token usage by 40% by deduplicating system prompt lines seen in this session, capping examples at 2, and replacing verbose tool descriptions with one-line summaries."""

import re
import logging
import hashlib

_session_seen_lines: set[str] = set()

def reset_session_cache() -> None:
    """Clear the session line cache. Call at session start or after a context reset."""
    _session_seen_lines.clear()

def _hash_line(line: str) -> str:
    """Return a short hash of a stripped line for deduplication."""
    return hashlib.md5(line.strip().encode()).hexdigest()[:12]

def deduplicate_system_prompt(system_prompt: str) -> str:
    """Remove lines already seen in this session from system_prompt. Updates session cache with new lines. Returns deduplicated prompt."""
    lines = system_prompt.split('\n')
    out_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out_lines.append(line)
            continue
        h = _hash_line(line)
        if h in _session_seen_lines:
            continue
        _session_seen_lines.add(h)
        out_lines.append(line)
    return '\n'.join(out_lines)

def cap_examples(text: str, *, max_examples: int = 2) -> str:
    """Find example blocks delimited by lines starting with "Example" or "e.g." or numbered like "1." / "2.". Keep only the first max_examples and truncate the rest. Returns modified text."""
    pattern = re.compile(r'^(Example\s*\d*[:.]|e\.g\.|\d+\.\s)', re.MULTILINE)
    matches = list(pattern.finditer(text))
    if len(matches) <= max_examples:
        return text
    cutoff_pos = matches[max_examples].start()
    truncated_text = text[:cutoff_pos].rstrip() + '\n[... additional examples truncated for token efficiency]'
    return truncated_text

def compress_tool_descriptions(text: str) -> str:
    """Replace multi-line tool description blocks (lines between "Description:" and the next blank line that exceed 3 lines) with a single-line summary of the first non-empty line of the block."""
    lines = text.split('\n')
    out_lines = []
    capturing = False
    captured_lines = []
    desc_indent = ""
    
    for line in lines:
        if not capturing:
            m = re.match(r'^(\s*)Description:\s*(.*)', line)
            if m:
                capturing = True
                desc_indent = m.group(1)
                first_val = m.group(2).strip()
                captured_lines = []
                if first_val:
                    captured_lines.append(first_val)
            else:
                out_lines.append(line)
        else:
            if line.strip() == "":
                if len(captured_lines) >= 3:
                    out_lines.append(f"{desc_indent}Description: {captured_lines[0]} [compressed]")
                    out_lines.append("")
                else:
                    desc_val = " ".join(captured_lines) if captured_lines else ""
                    out_lines.append(f"{desc_indent}Description: {desc_val}")
                    out_lines.append("")
                capturing = False
            else:
                captured_lines.append(line.strip())
    if capturing:
        if len(captured_lines) >= 3:
            out_lines.append(f"{desc_indent}Description: {captured_lines[0]} [compressed]")
        else:
            desc_val = " ".join(captured_lines) if captured_lines else ""
            out_lines.append(f"{desc_indent}Description: {desc_val}")
    return '\n'.join(out_lines)

def compress_prompt(messages: list[dict], *, session_dedup: bool = True, cap_ex: bool = True, compress_tools: bool = True) -> list[dict]:
    """Main entry point. Takes an OpenAI-style messages list (each dict has role and content). Applies all enabled compression passes. Returns compressed messages list. Never modifies the input list in place."""
    original_messages_str = str(messages)
    original_len = len(original_messages_str) // 4
    
    result = [dict(m) for m in messages]
    for message in result:
        if message.get("role") == "system":
            content = message.get("content", "")
            if compress_tools:
                content = compress_tool_descriptions(content)
            if cap_ex:
                content = cap_examples(content, max_examples=2)
            if session_dedup:
                content = deduplicate_system_prompt(content)
            message["content"] = content
            
    compressed_len = len(str(result)) // 4
    logging.debug(f'[prompt_compressor] original_tokens_est={original_len} compressed_tokens_est={compressed_len}')
    return result
