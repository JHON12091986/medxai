# Slot 12 — PERF-002: Speed-Optimized Regex Matching Registry
**Tier:** PERF | **Priority:** P2 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → PERF-002

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does regex_cache.py exist?
test -f tools/regex_cache.py && grep -n 'RegexRegistry\|get_compiled' tools/regex_cache.py

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'regex.*cache\|regex_cache\|RegexRegistry' | head -5

# SCAN 3: Is there already a compiled regex cache elsewhere in codebase?
grep -rn 'RegexRegistry\|_compiled_patterns\|re\.compile.*cache' core/ tools/ 2>/dev/null | grep -v '__pycache__' | head -5
```

**SKIP IF:** `tools/regex_cache.py` exists AND contains `RegexRegistry`

---

## Task Execution

**Goal:** Create `tools/regex_cache.py` with a thread-safe `RegexRegistry` class.
- Pre-compiles and caches patterns: sensitive data (`API_KEY`, `TOKEN`, `SECRET`), log structure, task classification
- `get_compiled(pattern_name: str) -> re.Pattern` — returns cached compiled pattern
- Thread-safe using `threading.Lock`
- `register_pattern(name, pattern_str)` for external extension

**Target files:** `tools/regex_cache.py`, `tests/test_regex_cache.py`

**Validation:**
```bash
python3 -m py_compile tools/regex_cache.py tests/test_regex_cache.py
./venv/bin/pytest tests/test_regex_cache.py -v
./guardian
```

**PR title:** `feat(perf): optimize regex parsing with precompiled cache`
