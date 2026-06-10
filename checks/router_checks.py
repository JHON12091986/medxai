from checks.runner import record, NINA_DIR
import re
def check_router_regressions():
    router_path = NINA_DIR / "core" / "router.py"
    if not router_path.exists():
        record("INFO", "router.regression.missing", "core/router.py not found — skipping regression scan")
        return

    source = router_path.read_text(errors="replace")

    # R-72: self._http (must be self.http)
    if re.search(r"self\._http\b", source):
        record(
            "BLOCKER", "router.attr.self_http",
            "Regression: self._http found in core/router.py (should be self.http)",
            detail="Pattern: self._http — causes AttributeError at runtime on every provider call.",
            fix="Run: sed -i 's/self\\._http/self.http/g' ~/nina/core/router.py",
        )
    else:
        record("PASS", "router.attr.self_http", "Router attribute self.http — OK")

    # R-69: ordered_providers (must be _ordered_providers)
    if re.search(r"(?<!_)ordered_providers\b", source):
        record(
            "BLOCKER", "router.attr.orderedproviders",
            "Regression: ordered_providers (non-underscore) found in core/router.py",
            detail="Pattern: ordered_providers — should be _ordered_providers.",
            fix="Run: sed -i 's/\\bordered_providers\\b/_ordered_providers/g' ~/nina/core/router.py",
        )
    else:
        record("PASS", "router.attr.orderedproviders", "Router attribute _ordered_providers — OK")

    # R-70: forcelocal (must be force_local)
    if re.search(r"\bforcelocal\b", source):
        record(
            "BLOCKER", "router.attr.forcelocal",
            "Regression: forcelocal (camelCase) found in core/router.py",
            detail="Pattern: forcelocal — should be force_local.",
            fix="Run: sed -i 's/\\bforcelocal\\b/force_local/g' ~/nina/core/router.py ~/nina/core/agent.py",
        )
    else:
        record("PASS", "router.attr.forcelocal", "Router attribute force_local — OK")

    # R-58: dict mutation during iteration in purge_expired
    if re.search(r"for\s+k.*in\s+self\.s\.items\(\).*self\.s\.pop", source, re.DOTALL):
        record(
            "WARN", "router.cache.dict_mutation",
            "Potential dict mutation during iteration in ResponseCache.purge_expired",
            detail="Iterating self.s.items() while calling self.s.pop() causes RuntimeError.",
            fix="Collect dead keys into a list first, then pop in a separate loop (R-58 fix).",
        )
    else:
        record("PASS", "router.cache.dict_mutation", "ResponseCache purge_expired — OK")
