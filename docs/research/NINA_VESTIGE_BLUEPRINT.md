# NinaVestige — Architecture Blueprint

> **System name:** NinaVestige  
> **Codename origin:** Inference is the rarely-needed leftover organ — a vestige, not the core.  
> **Canonical symbols:** `vestige.py`, `VestigeGate`, `VestigeEngine`, `VestigeRouter`  
> **Location:** `docs/research/NINA_VESTIGE_BLUEPRINT.md`  
> **Status:** Research / Pre-implementation  
> **Blueprint version:** 3.0 — 2026-06-26  
> **Changes in v3:** Semantic response cache (Tier −1), confidence-gated cascade routing, execution trace diffing, static AST patch scorer, parallel multi-candidate RAG resolution — ALL deterministic, zero LLM, zero network  
> **Changes in v2:** AST semantic hashing, LSH/MinHash fuzzy matching, prompt caching, vector RAG patch catalog  
> **Supersedes:** `OUROBOROS_BLUEPRINT.md` (name + channel architecture)

---

## Core Principle

Vestige is a **gate, not a peer.** Everything in NINA that currently calls an LLM calls Vestige first. Vestige decides locally — from pattern memory — whether it can resolve the request without any network call. Only when pattern memory genuinely cannot help does it escalate outward, and even then it chooses the channel based on task type, not availability.

**The hard rule: Tier 0 is 100% deterministic.** No LLM calls, no network, no subprocess. Pure Python + stdlib + soft deps. If a v3 upgrade requires an LLM call, it does not belong in Tier 0.

The goal: **Tier 0 handles the overwhelming majority of cases.** Tiers 1 and 2 are the vestigial path — rarely used, architecturally present, never the default.

---

## Top-Level Flow — v3

```
NINA Core (telemetry, error_register, task requests)
        │
        ▼
   VestigeGate.handle(request)
        │
   ┌────┴────────────────────────────────────────────────────────────┐
   │ TIER −1: VestigeSemanticCache                        [v3 NEW]  │
   │                                                                 │
   │  np.dot() cosine similarity over session-scoped embeddings      │
   │  HIT (≥0.92)? → return full VestigeResult replay → DONE (~μs)  │
   └────┬────────────────────────────────────────────────────────────┘
        │ cache miss
        ▼
   ┌────┴────────────────────────────────────────────────────────────┐
   │ TIER 0: VestigeEngine                                           │
   │                                                                 │
   │ 1. Exact traceback SHA-256 hash lookup                          │
   │ 2. AST semantic hash of source block               [v2]         │
   │ 3. LSH / MinHash fuzzy traceback match             [v2]         │
   │ 4. Vector RAG nearest-fix retrieval                [v2]         │
   │                                                                 │
   │ All matches → DeltaVerifier (trace diff)           [v3 NEW]     │
   │ Confirmed patch → StaticPatchScorer (AST safety)   [v3 NEW]     │
   └────┬────────────────────────────────────────────────────────────┘
        │ match confidence returned
        ▼
   ┌────┴────────────────────────────────────────────────────────────┐
   │ TIER 0→1 ROUTING: ConfidenceCascade                  [v3 NEW]  │
   │                                                                 │
   │  ≥ 0.95 → Tier 0 direct return                                  │
   │  ≥ 0.75 → Parallel multi-candidate RAG resolution   [v3 NEW]   │
   │  ≥ 0.40 → Router.escalate() (Claude + RAG)                      │
   │  < 0.40 → Router.escalate() (Claude + Perplexity prefetch)      │
   └────┬────────────────────────────────────────────────────────────┘
        │ genuine miss
        ▼
   VestigeRouter.escalate(request, context)
        │  [Prompt Caching on all outbound LLM calls]    [v2]
        │
   ┌────┼──────────────────┬──────────────────┐
   ▼                       ▼                  ▼
Claude API           Perplexity API      Jules task spec
(synchronous         (side-channel,      (async, written
 patch gen,          knowledge gap       to disk, human-
 inner loop)         → feeds Claude)     dispatched)
```

---

## Three Distinct Classes — Why the Separation Matters

The three names are not aliases. Each owns a single responsibility and has no knowledge of the others' internals.

The class **boundaries are unchanged from v1/v2**. What changes in v3 is:
- A new Tier −1 layer (`VestigeSemanticCache`) inserted before the Gate's Engine call
- `VestigeGate.handle()` now uses `ConfidenceCascade` routing instead of binary threshold
- `VestigeEngine.record()` now gates promotion through `DeltaVerifier` + `StaticPatchScorer`
- `VestigeEngine.match()` with confidence ≥ 0.75 but < 0.95 triggers parallel RAG candidates

---

## NEW v3 — Upgrade 1: Semantic Response Cache (Tier −1)

**Problem:** The Ouroboros loop can fire the same logical error repeatedly across a session — each time paying for Tier 0 Engine lookup (LSH, FAISS query) even though the result was computed 30 seconds ago. On long self-patching sessions this compounds.

**Solution:** Insert a session-scoped in-memory cache keyed by cosine similarity of the request's embedding. Uses the same `SentenceTransformer` already loaded by `VestigeVectorStore` — zero additional deps. The threshold is 0.92 (tighter than RAG's 0.70) to avoid false replays.

**Zero LLM. Zero network. Pure `np.dot()`.**

```python
# core/vestige/vestige_semantic_cache.py

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.vestige.vestige_gate import VestigeRequest, VestigeResult

SEMANTIC_CACHE_THRESHOLD = 0.92   # tight — near-identical only


class VestigeSemanticCache:
    """
    Tier -1: session-scoped in-memory cache.
    Returns a full VestigeResult replay if the incoming request is
    semantically identical (cosine ≥ 0.92) to one already resolved
    this session. Zero network, zero pattern store lookup.

    Reuses VestigeVectorStore._embed() — pass the bound method at init.
    Falls back gracefully if embedder is unavailable (ST not installed).
    """

    def __init__(self, embed_fn=None):
        self._embed = embed_fn          # None → cache disabled
        self._cache: list[dict] = []    # [{vec, result, key}]

    def lookup(self, request: "VestigeRequest") -> "VestigeResult | None":
        if self._embed is None or not self._cache:
            return None
        key = f"{request.error_type}::{request.traceback[:300]}"
        vec = self._embed(key)
        for entry in self._cache:
            sim = float(np.dot(vec, entry["vec"]))
            if sim >= SEMANTIC_CACHE_THRESHOLD:
                return entry["result"]
        return None

    def store(self, request: "VestigeRequest", result: "VestigeResult"):
        if self._embed is None:
            return
        key = f"{request.error_type}::{request.traceback[:300]}"
        self._cache.append({
            "vec": self._embed(key),
            "result": result,
            "key": key,
        })

    def invalidate(self):
        """Call at Ouroboros loop restart — session boundary."""
        self._cache.clear()
```

**Integration in VestigeGate:**

```python
# core/vestige/vestige_gate.py — v3 handle()

def handle(self, request: VestigeRequest) -> VestigeResult:
    # Tier -1: semantic session cache (zero cost)
    if cached := self._semantic_cache.lookup(request):
        return cached

    # Tier 0: Engine match → confidence cascade
    match: MatchResult = self.engine.match(request)
    result = self._cascade(request, match)

    # Store in session cache for replay
    self._semantic_cache.store(request, result)
    return result
```

---

## NEW v3 — Upgrade 2: Confidence-Gated Cascade Routing

**Problem:** v2 uses a single binary threshold (`CONFIDENCE_THRESHOLD = 0.85`). A match at 0.84 confidence (LSH near-hit) gets sent straight to Claude — same cost as a genuine 0.0 miss. Soft-match cases are overpaying.

**Solution:** Replace the binary threshold with a four-band cascade. Each band maps to the cheapest resolution path that can handle it.

**Zero LLM. Pure float comparison.**

```python
# core/vestige/vestige_gate.py — v3 _cascade()

def _cascade(self, request: VestigeRequest, match: MatchResult) -> VestigeResult:
    """
    Four-band confidence cascade — cheapest resolution path per band.
    """
    if match.confidence >= 0.95:
        # Band 1: exact/AST hit — return directly
        return VestigeResult(
            tier=0, patch=match.fix, jules_spec_path=None,
            confidence=match.confidence, from_cache=True,
        )

    if match.confidence >= 0.75:
        # Band 2: LSH/vector soft match — try parallel RAG candidates first
        patch = self._parallel_rag_resolve(request, match)
        if patch:
            return VestigeResult(
                tier=0, patch=patch, jules_spec_path=None,
                confidence=match.confidence, from_cache=False,
            )
        # Parallel RAG failed — fall through to Claude

    if match.confidence >= 0.40:
        # Band 3: weak signal — Claude with RAG context
        return self.router.escalate(request, match)

    # Band 4: confidence < 0.40 — genuinely novel
    # Trigger Perplexity knowledge prefetch before Claude
    return self.router.escalate_with_prefetch(request, match)

def _parallel_rag_resolve(
    self, request: VestigeRequest, match: MatchResult
) -> str | None:
    """
    Fetch top-3 RAG candidates, test all deterministically in parallel.
    Returns the first patch that passes DeltaVerifier + StaticPatchScorer.
    No LLM call. Uses concurrent.futures for parallel trace execution.
    """
    if not self._vector_store:
        return None

    candidates = self._vector_store.query(
        f"{request.error_type}: {request.traceback.splitlines()[-1]}",
        k=3,
    )
    if not candidates:
        return None

    import concurrent.futures

    def test_candidate(entry: dict) -> str | None:
        patch = entry["fix_source"]
        if not self.engine.validate_python(patch):
            return None
        if not delta_verify(request.source, patch):
            return None
        if not static_patch_score(request.source, patch):
            return None
        return patch

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(test_candidate, c): c for c in candidates}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                # Cancel remaining — first valid wins
                for f in futures:
                    f.cancel()
                return result
    return None
```

---

## NEW v3 — Upgrade 3: Execution Trace Diffing (DeltaVerifier)

**Problem:** v2's verifier checks that the patch is valid Python and passes AST parse. It does **not** verify that the patch actually *changes the behaviour* that caused the failure. A no-op patch (same logic with a renamed variable) passes `ast.parse()`, gets recorded as a fix, and the same error fires again next cycle — silently poisoning the pattern store.

**Solution:** Run both the original and patched function under Python's stdlib `trace` module against a synthetic minimal input, then diff the execution line sets. If the patch produces zero execution delta, it is a no-op — reject it.

**Zero LLM. Zero network. Pure stdlib.**

```python
# core/vestige/vestige_verifier.py

from __future__ import annotations
import ast
import io
import sys
import trace
import types
from typing import Callable


def delta_verify(original_source: str, patched_source: str,
                 test_input: dict | None = None) -> bool:
    """
    Returns True if patched_source produces a meaningfully different
    execution trace from original_source.

    Uses a minimal synthetic input if test_input is not provided.
    Catches all exceptions from both runs — a patch that raises differently
    than the original still counts as a delta.
    """
    orig_fn = _compile_fn(original_source)
    patch_fn = _compile_fn(patched_source)
    if orig_fn is None or patch_fn is None:
        return False  # unparseable source — reject

    inputs = test_input or _synthetic_input(original_source)
    orig_lines = _capture_trace(orig_fn, inputs)
    patch_lines = _capture_trace(patch_fn, inputs)

    delta = orig_lines.symmetric_difference(patch_lines)
    return len(delta) > 0   # patch must change at least one execution line


def _compile_fn(source: str) -> Callable | None:
    """Compile source string to a callable, return None on error."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    namespace: dict = {}
    try:
        exec(compile(tree, "<vestige>", "exec"), namespace)  # noqa: S102
    except Exception:
        return None
    callables = [v for v in namespace.values() if callable(v)]
    return callables[0] if callables else None


def _capture_trace(fn: Callable, kwargs: dict) -> set[str]:
    """Run fn(**kwargs) under stdlib trace, return set of executed line strings."""
    tracer = trace.Trace(count=False, trace=True)
    buf = io.StringIO()
    old_stdout, sys.stdout = sys.stdout, buf
    try:
        tracer.runfunc(fn, **kwargs)
    except Exception:
        pass  # exceptions are fine — we only care about lines executed before crash
    finally:
        sys.stdout = old_stdout
    return set(buf.getvalue().splitlines())


def _synthetic_input(source: str) -> dict:
    """
    Attempt to infer minimal inputs from the function signature.
    Falls back to empty dict — an empty call still produces a traceable path.
    """
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                kwargs = {}
                for arg in node.args.args:
                    name = arg.arg
                    # Minimal type inference from annotation
                    if arg.annotation:
                        ann = ast.unparse(arg.annotation)
                        if "str" in ann:
                            kwargs[name] = ""
                        elif "int" in ann or "float" in ann:
                            kwargs[name] = 0
                        elif "list" in ann:
                            kwargs[name] = []
                        elif "dict" in ann:
                            kwargs[name] = {}
                        else:
                            kwargs[name] = None
                    else:
                        kwargs[name] = None
                return kwargs
    except Exception:
        pass
    return {}
```

**Why this is critical for NINA's self-patching loop:** Without trace diffing, the Ouroboros loop can enter a state where it "fixes" the same function with cosmetically different code on every cycle, filling the pattern store with no-op variants. Trace diffing is the kill switch for that failure mode.

---

## NEW v3 — Upgrade 4: Static AST Patch Scorer (pre-record gate)

**Problem:** Before v3, any patch that passed `ast.parse()` was eligible for `VestigeEngine.record()`. This means a patch that adds `import subprocess` or triples the function's line count could be promoted to the permanent pattern store.

**Solution:** A purely deterministic AST-walk scorer that checks safety (no new dangerous imports or calls) and minimality (patch shouldn't be a rewrite). No LLM. No heuristic scores. Hard binary: promote or quarantine.

**Zero LLM. Zero network. Pure `ast.walk()`.**

```python
# core/vestige/vestige_verifier.py (continued)

import re

BANNED_CALLS = {"eval", "exec", "subprocess", "os.system", "__import__",
                "open", "compile", "globals", "locals", "vars"}
BANNED_IMPORTS = {"subprocess", "os", "sys", "shutil", "socket",
                  "pickle", "marshal", "importlib"}

MAX_LINE_GROWTH_FACTOR = 2.5   # patch must not be >2.5× original line count


def static_patch_score(original_source: str, patch_source: str) -> bool:
    """
    Deterministic safety + minimality gate before VestigeEngine.record().
    Returns True (safe to promote) or False (quarantine).

    Checks:
    1. No new top-level imports added by the patch
    2. No calls to BANNED_CALLS added by the patch
    3. Patch line count ≤ original × MAX_LINE_GROWTH_FACTOR
    """
    try:
        orig_tree = ast.parse(original_source)
        patch_tree = ast.parse(patch_source)
    except SyntaxError:
        return False  # unparseable — quarantine

    # Rule 1: new imports
    orig_imports = _import_names(orig_tree)
    patch_imports = _import_names(patch_tree)
    new_imports = patch_imports - orig_imports
    dangerous_new = new_imports & BANNED_IMPORTS
    if dangerous_new:
        return False

    # Rule 2: banned call nodes
    patch_calls = _call_names(patch_tree)
    orig_calls = _call_names(orig_tree)
    new_banned_calls = (patch_calls - orig_calls) & BANNED_CALLS
    if new_banned_calls:
        return False

    # Rule 3: size explosion
    orig_lines = len(original_source.splitlines())
    patch_lines = len(patch_source.splitlines())
    if orig_lines > 0 and patch_lines > orig_lines * MAX_LINE_GROWTH_FACTOR:
        return False

    return True


def _import_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0])
    return names


def _call_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names
```

**Quarantine queue:** Patches that fail `static_patch_score()` are written to `data/vestige_quarantine/` as JSON for human review — not silently discarded.

```python
# In VestigeEngine.record() — v3 gated promotion

def record(self, request, fix_source, pattern_id=None, hash_type="traceback"):
    self._validate_python(fix_source)

    # v3: deterministic pre-record gates
    if not delta_verify(request.source, fix_source):
        self._quarantine(request, fix_source, reason="no_execution_delta")
        return

    if not static_patch_score(request.source, fix_source):
        self._quarantine(request, fix_source, reason="static_safety_fail")
        return

    # Passes all gates — promote to pattern store
    sig = (ast_semantic_hash(request.source or "") if hash_type == "ast"
           else self._signature(request.error_type, request.traceback))
    from datetime import datetime, timezone
    entry = PatternEntry(
        pattern_id=pattern_id or (sig or "")[:12],
        error_type=request.error_type,
        signature_hash=sig or "",
        fix_source=fix_source,
        hash_type=hash_type,
        hit_count=0,
        last_seen=datetime.now(timezone.utc).isoformat(),
    )
    if sig:
        self._store[sig] = entry
    self._flush_store()
    if self._lsh_index:
        self._lsh_index.add(entry.pattern_id, request.traceback, fix_source)

def _quarantine(self, request, fix_source, reason: str):
    import json
    from datetime import datetime, timezone
    QUARANTINE_DIR = Path("data/vestige_quarantine")
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = QUARANTINE_DIR / f"quarantine_{ts}_{request.error_type}_{reason}.json"
    path.write_text(json.dumps({
        "reason": reason,
        "error_type": request.error_type,
        "component": request.component,
        "original_source": request.source,
        "rejected_patch": fix_source,
        "traceback": request.traceback[:1000],
    }, indent=2))
```

---

## Full Matching + Promotion Stack — v3

```
New error arrives at VestigeGate
         │
         ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │  TIER −1 — VestigeSemanticCache                      [v3]      │
    │  cosine(session_vec, request_vec) ≥ 0.92?                       │
    │  YES → replay full VestigeResult ──────────────────────► DONE   │
    └────┬────────────────────────────────────────────────────────────┘
         │ miss
         ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │  TIER 0 — VestigeEngine                                         │
    │                                                                 │
    │  Step 1: SHA-256 traceback hash lookup      confidence=1.0      │
    │  Step 2: AST semantic hash               [v2]  confidence=0.97  │
    │  Step 3: LSH / MinHash Jaccard           [v2]  confidence=sim   │
    │  Step 4: Vector RAG top-1               [v2]  confidence=0.70+  │
    │                                                                 │
    └────┬──────────────────────────────────────────────────────────── 
         │ confidence float returned
         ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │  CONFIDENCE CASCADE — VestigeGate._cascade()         [v3]      │
    │                                                                 │
    │  ≥ 0.95 → Tier 0 direct return                                  │
    │                                                                 │
    │  ≥ 0.75 → Parallel multi-candidate RAG    [v3]                  │
    │           top-3 fixes tested concurrently                       │
    │           DeltaVerifier + StaticPatchScorer on each             │
    │           First valid → return (no LLM)                         │
    │           All fail → fall to Claude                             │
    │                                                                 │
    │  ≥ 0.40 → Claude escalation (with RAG few-shot) [v2]           │
    │                                                                 │
    │  < 0.40 → Claude + Perplexity prefetch                          │
    └────┬────────────────────────────────────────────────────────────┘
         │ Claude returns patch
         ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │  PROMOTION GATE (before record())                    [v3]      │
    │                                                                 │
    │  1. ast.parse() — valid Python?                                 │
    │  2. DeltaVerifier — patch changes execution trace?              │
    │  3. StaticPatchScorer — no new dangerous imports/calls?         │
    │                                                                 │
    │  PASS → VestigeEngine.record() + VestigeVectorStore.add()      │
    │  FAIL → data/vestige_quarantine/{ts}_{reason}.json              │
    └─────────────────────────────────────────────────────────────────┘
         │ Tier 1 exhausted
         ▼
    TIER 2 — Jules spec written to disk (unchanged from v1/v2)
```

---

## VestigeGate — v3 Full

```python
# core/vestige/vestige_gate.py

from __future__ import annotations
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.vestige.vestige_engine import VestigeEngine, MatchResult
from core.vestige.vestige_router import VestigeRouter
from core.vestige.vestige_semantic_cache import VestigeSemanticCache

if TYPE_CHECKING:
    from core.vestige.vestige_vector_store import VestigeVectorStore


@dataclass
class VestigeRequest:
    error_type: str
    traceback: str
    source: str
    component: str
    context: dict
    replay_log: list[dict]


@dataclass
class VestigeResult:
    tier: int
    patch: str | None
    jules_spec_path: str | None
    confidence: float
    from_cache: bool


class VestigeGate:
    """
    Single entry point for all NINA LLM requests.
    v3: Tier -1 semantic cache + confidence cascade routing.
    """

    def __init__(self, engine: VestigeEngine, router: VestigeRouter,
                 vector_store: "VestigeVectorStore | None" = None):
        self.engine = engine
        self.router = router
        self._vector_store = vector_store

        # Tier -1 cache — pass embedder if vector store available
        embed_fn = vector_store._embed if (
            vector_store and vector_store._available
        ) else None
        self._semantic_cache = VestigeSemanticCache(embed_fn)

    def handle(self, request: VestigeRequest) -> VestigeResult:
        # Tier -1: session semantic cache
        if cached := self._semantic_cache.lookup(request):
            return cached

        # Tier 0: engine match
        match: MatchResult = self.engine.match(request)
        result = self._cascade(request, match)

        # Cache result for session replay
        self._semantic_cache.store(request, result)
        return result

    def _cascade(self, request: VestigeRequest, match: MatchResult) -> VestigeResult:
        if match.confidence >= 0.95:
            return VestigeResult(tier=0, patch=match.fix, jules_spec_path=None,
                                 confidence=match.confidence, from_cache=True)

        if match.confidence >= 0.75:
            patch = self._parallel_rag_resolve(request, match)
            if patch:
                return VestigeResult(tier=0, patch=patch, jules_spec_path=None,
                                     confidence=match.confidence, from_cache=False)

        if match.confidence >= 0.40:
            return self.router.escalate(request, match)

        return self.router.escalate_with_prefetch(request, match)

    def _parallel_rag_resolve(self, request: VestigeRequest,
                               match: MatchResult) -> str | None:
        if not self._vector_store:
            return None

        candidates = self._vector_store.query(
            f"{request.error_type}: {request.traceback.splitlines()[-1]}", k=3
        )
        if not candidates:
            return None

        from core.vestige.vestige_verifier import delta_verify, static_patch_score
        import concurrent.futures

        def test_candidate(entry: dict) -> str | None:
            patch = entry["fix_source"]
            if not self.engine.validate_python(patch):
                return None
            if not delta_verify(request.source, patch):
                return None
            if not static_patch_score(request.source, patch):
                return None
            return patch

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = {pool.submit(test_candidate, c): c for c in candidates}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    for f in futures:
                        f.cancel()
                    return result
        return None
```

---

## VestigeEngine — v3 (record() gated)

The Engine class is identical to v2 except `record()` now passes through `DeltaVerifier` + `StaticPatchScorer` before promoting to the store. See the **Upgrade 4** section above for the full `record()` + `_quarantine()` implementation.

The `match()` method is unchanged from v2.

---

## VestigeRouter — Full v2/v3

Unchanged from v2 except `escalate()` now has a companion `escalate_with_prefetch()` for Band 4 (confidence < 0.40) that triggers the Perplexity knowledge lookup before Claude:

```python
def escalate_with_prefetch(self, request: "VestigeRequest",
                            match: "MatchResult") -> "VestigeResult":
    """Band 4: genuinely novel error — Perplexity prefetch before Claude."""
    extra_context = self._perplexity_lookup(request)
    return self._escalate_inner(request, match, extra_context)

def escalate(self, request: "VestigeRequest",
             match: "MatchResult") -> "VestigeResult":
    """Bands 2–3: Claude with optional knowledge gap lookup."""
    extra_context = ""
    if self._needs_knowledge_gap(request):
        extra_context = self._perplexity_lookup(request)
    return self._escalate_inner(request, match, extra_context)

def _escalate_inner(self, request, match, extra_context) -> "VestigeResult":
    from core.vestige.vestige_gate import VestigeResult
    if self._is_tier2(request):
        spec_path = self._write_jules_spec(request)
        return VestigeResult(tier=2, patch=None, jules_spec_path=str(spec_path),
                             confidence=0.0, from_cache=False)

    patch = self._claude_patch_loop(request, extra_context)
    if patch and self._engine.validate_python(patch):
        self._engine.record(request, patch)   # v3 gates inside record()
        if self._vector_store:
            self._vector_store.add(
                patch[:12],
                f"{request.error_type}: {request.traceback.splitlines()[-1]}",
                patch,
            )
        tier = 11 if extra_context else 1
        return VestigeResult(tier=tier, patch=patch, jules_spec_path=None,
                             confidence=0.9, from_cache=False)

    spec_path = self._write_jules_spec(request)
    return VestigeResult(tier=2, patch=None, jules_spec_path=str(spec_path),
                         confidence=0.0, from_cache=False)
```

---

## Tier Summary — v3

| Tier | Trigger | Latency | LLM? | Tokens |
|---|---|---|---|---|
| **−1 — Semantic cache** | Session cosine hit ≥ 0.92 [v3] | ~μs | ❌ | 0 |
| **0a — Exact hash** | SHA-256 traceback hit | ~1ms | ❌ | 0 |
| **0b — AST hash** | Structural shape match [v2] | ~5ms | ❌ | 0 |
| **0c — LSH match** | Jaccard ≥ 0.85 [v2] | ~10ms | ❌ | 0 |
| **0d — Parallel RAG** | Confidence 0.75–0.95 [v3] | ~50ms | ❌ | 0 |
| **1 — Claude + RAG** | Confidence 0.40–0.75 [v2+v3] | Seconds | ✅ | ~90% less |
| **1b — Perplexity→Claude** | Confidence < 0.40 [v3] | Seconds | ✅ | ~90% less |
| **2 — Jules spec** | Tier 1 exhausted | Hours (async) | ❌ | 0 |

**Tiers −1 through 0d are 100% deterministic — no LLM, no network, no subprocess.**

---

## File Structure — v3

```
core/
└── vestige/
    ├── __init__.py
    ├── vestige_gate.py              ← + semantic cache, + confidence cascade
    ├── vestige_engine.py            ← + DeltaVerifier/StaticScorer in record()
    ├── vestige_router.py            ← + escalate_with_prefetch()
    ├── vestige_lsh.py               ← [v2] VestigeLSHIndex (datasketch)
    ├── vestige_vector_store.py      ← [v2] VestigeVectorStore (FAISS + ST)
    ├── vestige_semantic_cache.py    ← [v3 NEW] session cosine cache
    └── vestige_verifier.py          ← [v3 NEW] delta_verify + static_patch_score

data/
├── vestige_patterns.json            ← exact hash store
├── vestige_vectors.npz              ← [v2] FAISS index
├── vestige_vector_meta.json         ← [v2] FAISS metadata
├── vestige_quarantine/              ← [v3 NEW] rejected patches for human review
│   └── quarantine_{ts}_{reason}.json
└── jules_specs/
    └── jules_spec_*.md

docs/
└── research/
    ├── OUROBOROS_BLUEPRINT.md
    └── NINA_VESTIGE_BLUEPRINT.md    ← THIS FILE
```

---

## Dependencies — v3

| Package | Required | Notes |
|---|---|---|
| `anthropic ≥ 0.28` | Required | `betas=["prompt-caching-2024-07-31"]` |
| `datasketch ≥ 1.6` | Soft | LSH/MinHash. Pure Python, ~1.5MB. |
| `sentence-transformers ≥ 2.7` | Soft | CPU embeddings. Also powers Tier −1. |
| `faiss-cpu ≥ 1.8` | Soft | Vector search, no GPU needed. |
| `google-generativeai ≥ 0.7` | Optional | Gemini context caching alternative. |

All v3 features use only Python stdlib (`ast`, `trace`, `concurrent.futures`, `hashlib`, `re`). Zero new hard dependencies added in v3.

---

## Configuration — .env.example (v3 additions)

```bash
# v1 (unchanged)
VESTIGE_CONFIDENCE_THRESHOLD=0.85
VESTIGE_TIER1_MAX_RETRIES=4
VESTIGE_MODEL_CLAUDE=claude-sonnet-4-5
VESTIGE_MODEL_PERPLEXITY=sonar-pro
VESTIGE_STORE_PATH=data/vestige_patterns.json
VESTIGE_JULES_SPEC_DIR=data/jules_specs

# v2
VESTIGE_AST_HASHING=true
VESTIGE_LSH_ENABLED=true
VESTIGE_LSH_THRESHOLD=0.85
VESTIGE_PROMPT_CACHING=true
VESTIGE_CACHE_PROVIDER=anthropic
VESTIGE_VECTOR_RAG_ENABLED=true
VESTIGE_VECTOR_STORE_PATH=data/vestige_vectors.npz
VESTIGE_VECTOR_META_PATH=data/vestige_vector_meta.json
VESTIGE_VECTOR_TOP_K=3
VESTIGE_VECTOR_SIMILARITY_THRESHOLD=0.70

# v3 — new flags
VESTIGE_SEMANTIC_CACHE_ENABLED=true
VESTIGE_SEMANTIC_CACHE_THRESHOLD=0.92
VESTIGE_CASCADE_BAND1=0.95
VESTIGE_CASCADE_BAND2=0.75
VESTIGE_CASCADE_BAND3=0.40
VESTIGE_DELTA_VERIFY_ENABLED=true
VESTIGE_STATIC_SCORER_ENABLED=true
VESTIGE_QUARANTINE_DIR=data/vestige_quarantine
VESTIGE_MAX_LINE_GROWTH_FACTOR=2.5
```

---

## Integration Checklist — v3

**v1/v2 items (carry forward):**
- [ ] `VestigeEngine` unit tests — zero network, zero API keys
- [ ] `VestigeRouter` integration tests — mock Claude + Perplexity clients
- [ ] `VestigeGate` wired as single LLM entry point
- [ ] `data/vestige_patterns.json` initialised (empty `{}`)
- [ ] `datasketch` in `requirements.txt`
- [ ] `sentence-transformers` + `faiss-cpu` in `requirements.txt` (optional)
- [ ] Prompt caching verified — check `cache_creation_input_tokens` in Anthropic response

**v3 additions:**
- [ ] `vestige_semantic_cache.py` — unit test: lookup miss on empty cache, hit after store
- [ ] `vestige_verifier.py` — unit test `delta_verify()`: confirm no-op patch returns False
- [ ] `vestige_verifier.py` — unit test `static_patch_score()`: confirm `subprocess` import returns False
- [ ] `VestigeGate._cascade()` — unit test all four confidence bands with mock engine
- [ ] `VestigeGate._parallel_rag_resolve()` — test with 3 mock candidates, first-valid-wins behaviour
- [ ] `VestigeEngine.record()` — test quarantine path: no-op patch writes to `data/vestige_quarantine/`
- [ ] `data/vestige_quarantine/` — directory created on first quarantine event (auto via `mkdir(parents=True)`)
- [ ] Semantic cache invalidation called at Ouroboros loop restart (`VestigeSemanticCache.invalidate()`)
- [ ] Confidence cascade thresholds in `.env.example` with safe defaults

---

## Open Questions — v3

1. **DeltaVerifier synthetic inputs:** The current `_synthetic_input()` uses annotation hints. For untyped functions, it injects `None` for all args — this may cause the trace to terminate instantly on `None` checks. Consider a second pass with `0` / `""` / `[]` if the first pass produces empty traces on both sides.
2. **Parallel RAG thread safety:** `VestigeVectorStore` FAISS index is read-only during query — safe for concurrent reads. Writes (`add()`) must remain single-threaded; add a `threading.Lock` to `VestigeVectorStore.add()`.
3. **Semantic cache memory growth:** Session cache grows unbounded in very long Ouroboros sessions. Add a max-size eviction (LRU, cap at 256 entries) if memory becomes a concern.
4. **Quarantine review workflow:** Currently quarantined patches are JSON files — no tooling to review or promote them. A future `vestige_admin.py` CLI (`quarantine list`, `quarantine promote <id>`) would close this loop.
5. **Cascade band tuning:** The four thresholds (0.95 / 0.75 / 0.40) are initial estimates. After first 500 production escalations, plot the confidence distribution and adjust band boundaries empirically.

---

*Blueprint version: 3.0 — 2026-06-26*  
*Author: M. Baizid Alam / NINA Architect Overwatch + Perplexity session*  
*v3 additions: VestigeSemanticCache (Tier −1), ConfidenceCascade routing, DeltaVerifier (execution trace diff), StaticPatchScorer (AST walk), parallel multi-candidate RAG resolution — all deterministic, zero LLM*  
*v2 additions: AST semantic hashing, LSH/MinHash fuzzy matching, Anthropic/Gemini prompt caching, FAISS+SentenceTransformers vector RAG*
