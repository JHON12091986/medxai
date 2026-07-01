# Slot 13 — PERF-003: AST Token Count Parser with Caching
**Tier:** PERF | **Priority:** P2 | **Interval:** Every 12h (offset :00)
**Backlog ref:** `docs/space/jules_backlog.md` → Section 5 → PERF-003
**Dependency:** PERF-002 (Slot 12) preferred first (but not blocking)

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Does ast_cache.py exist?
test -f tools/ast_cache.py && grep -n 'ASTCache\|count_tokens' tools/ast_cache.py

# SCAN 2: Prior commit?
git log --oneline --all | grep -i 'ast.*cache\|ast_cache\|token.*count.*cache' | head -5

# SCAN 3: Is there an existing AST cache in core/ast_refactor.py?
grep -n 'cache\|_cache\|lru_cache' core/ast_refactor.py 2>/dev/null | head -5
```

**SKIP IF:** `tools/ast_cache.py` exists AND contains a hash-based caching mechanism for AST parsing

---

## Task Execution

**Goal:** Create `tools/ast_cache.py` with SHA-256 file hash-based AST cache.
- `get_ast(filepath: str) -> ast.AST` — parses file, caches by SHA-256 hash, returns cached on re-call
- `count_tokens(filepath: str) -> int` — returns node count, uses same cache
- Cache invalidated when file hash changes
- Thread-safe

**Target files:** `tools/ast_cache.py`, `tests/test_ast_cache.py`

**Validation:**
```bash
python3 -m py_compile tools/ast_cache.py tests/test_ast_cache.py
./venv/bin/pytest tests/test_ast_cache.py -v
./guardian
```

**PR title:** `feat(perf): add AST parsing cache utility`
