# NINA OUROBOROS — Pure-Python Self-Stitch Blueprint
<!-- version: v4.0 — 2026-06-29 -->

> **Formerly titled:** OUROBOROS_BLUEPRINT (Ouroboros Pure-Python Self-Stitch)
> **Relation to SOVEREIGN:** This document describes a Python-native re-implementation of the SOVEREIGN loop's patch-and-retry logic — **not a replacement** for the SOVEREIGN daemon. SOVEREIGN (`OUROBOROS.md`) remains the live running loop.
> **Relation to HYDRA:** The `NinaOuroborosLoop` class described here is the candidate implementation for HYDRA's in-process self-healing layer, used when a task fails inside a Python function rather than at the CLI agent level.
>
> **Status: RESEARCH — 2026-06-29 (v4.0)**

---

## What This Is

The SOVEREIGN loop patches NINA's codebase by invoking `opencode` as an external subprocess. This blueprint describes an alternative self-stitch mechanism that operates **inside Python** — no CLI agent required — using `exec()` hot-swap, AST validation, and ninagate as the LLM client.

This is NOT meant to replace SOVEREIGN. It is meant to handle **function-level failures** that occur during a running NINA session — the kind that don't require a full codebase edit, just a runtime repair of a single broken function.

---

## Core Loop Architecture

```
NINA Self-Stitch Loop (Python-native)
─────────────────────────────────────────────────────
   ┌──────────────────────────────────────────────┐
   │           NINA SELF-STITCH LOOP              │
   │                                               │
   │  [OBSERVE]  →  [DIAGNOSE]  →  [PATCH]         │
   │      ↑                            │           │
   │      └─────── [VERIFY] ←──────────┘           │
   │                  │                            │
   │             PASS or RETRY (max N)             │
   └──────────────────────────────────────────────┘
```

## Component: NinaOuroborosLoop

```python
# core/ouroboros/loop.py
import subprocess, sys, traceback, ast, inspect
from pathlib import Path
from typing import Callable

class NinaOuroborosLoop:
    def __init__(self, model_client, max_retries=5):
        self.llm = model_client
        self.max_retries = max_retries
        self.replay_log = []

    def run(self, task_fn: Callable, context: dict):
        for attempt in range(self.max_retries):
            # Cycle guard — must be first check every entry
            if self.patch_graph.has_cycle():
                self.patch_graph.reset()
                self.semantic_cache.clear()
                raise OuroborosSpiral("Patch graph cycle detected — graph + cache reset")
            try:
                result = task_fn(**context)
                if self._verify(result, context):
                    return result
            except Exception as e:
                evidence = self._collect_evidence(e, task_fn)
                patch = self._diagnose_and_patch(evidence)
                task_fn = self._apply_patch(task_fn, patch)
                self.replay_log.append({
                    "attempt": attempt,
                    "error": str(e),
                    "patch": patch
                })
        raise RuntimeError("Max retries exceeded — escalate to human-in-loop")
```

## Component: Observer

```python
def _collect_evidence(self, exc: Exception, fn: Callable) -> dict:
    return {
        "traceback": traceback.format_exc(),
        "source": inspect.getsource(fn),
        "locals": self._safe_locals(),
        "nina_component": fn.__module__,
        "replay_log": self.replay_log[-3:]
    }
```

## Component: Patcher (Hot-Swap)

```python
import types

def _apply_patch(self, original_fn: Callable, patch_code: str) -> Callable:
    try:
        ast.parse(patch_code)
    except SyntaxError as e:
        raise ValueError(f"LLM returned invalid Python: {e}")
    namespace = {}
    exec(patch_code, original_fn.__globals__, namespace)
    patched = next(v for v in namespace.values() if callable(v))
    return patched
```

## Component: Kill Switch (Anti-Loop)

```python
from sklearn.metrics.pairwise import cosine_similarity

def _detect_semantic_loop(self) -> bool:
    if len(self.replay_log) < 3:
        return False
    patches = [r["patch"] for r in self.replay_log[-3:]]
    embeddings = [self.llm.embed(p) for p in patches]
    sim = cosine_similarity(embeddings[-1:], embeddings[:-1])[0]
    return any(s > 0.92 for s in sim)
```

## Decorator Interface

```python
def self_stitch(model_client, max_retries=3):
    def decorator(fn):
        loop = NinaOuroborosLoop(model_client, max_retries)
        def wrapper(*args, **kwargs):
            return loop.run(fn, {"args\": args, "kwargs": kwargs})
        return wrapper
    return decorator

# Usage:
@self_stitch(nina.llm, max_retries=5)
def process_file_batch(files):
    ...
```

---

## v4.0 — VESTIGE Layer (Deterministic, Zero-LLM, Zero-Network)

> Four new modules added in v4. All are deterministic — no LLM calls, no network I/O.

### VestigeRequest — Updated Fields

```python
@dataclass
class VestigeRequest:
    # ... existing fields ...
    passing_inputs: list[dict]    # inputs that pass tests
    failing_inputs: list[dict]    # inputs that trigger the failure
    suspect_lines: list[int]      # line numbers flagged by SBFL
    sbfl_scores: dict[int, float] # Ochiai score per line
```

### Module 1 — `vestige_sbfl.py` (Fault Localization)

Narrows the fault location before RAG lookup using the **Ochiai formula** over `coverage.py` line stats.

```python
# core/ouroboros/vestige_sbfl.py
import math
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class SBFLResult:
    line: int
    ochiai: float   # range [0.0, 1.0] — higher = more suspicious

def ochiai(ef: int, ep: int, nf: int) -> float:
    """
    ef = tests that execute line AND fail
    ep = tests that execute line AND pass
    nf = total failing tests
    """
    denom = math.sqrt(nf * (ef + ep))
    return ef / denom if denom > 0 else 0.0

def run_sbfl(coverage_data: dict, passing: list, failing: list) -> List[SBFLResult]:
    """
    coverage_data: {line_no: {"pass": int, "fail": int}}
    Returns lines sorted by Ochiai score descending.
    """
    total_fail = len(failing)
    results = []
    for line, counts in coverage_data.items():
        score = ochiai(counts["fail"], counts["pass"], total_fail)
        results.append(SBFLResult(line=line, ochiai=score))
    return sorted(results, key=lambda r: r.ochiai, reverse=True)
```

**Wiring:** `sbfl_scores` and `suspect_lines` are populated on `VestigeRequest` before RAG lookup. RAG is restricted to the top-N suspect lines only.

---

### Module 2 — `vestige_naturalness.py` (Style Ranking)

Ranks patch candidates by codebase style fit using a **trigram language model** trained on `core/`.

```python
# core/ouroboros/vestige_naturalness.py
from collections import defaultdict, Counter
import tokenize, io, math

class TrigramLM:
    def __init__(self):
        self.counts: dict[tuple, int] = defaultdict(int)
        self.totals: dict[tuple, int] = defaultdict(int)

    def train(self, source: str):
        tokens = self._tokenize(source)
        for i in range(len(tokens) - 2):
            trigram = (tokens[i], tokens[i+1], tokens[i+2])
            prefix  = (tokens[i], tokens[i+1])
            self.counts[trigram] += 1
            self.totals[prefix]  += 1

    def score(self, source: str) -> float:
        """Returns average log-probability (higher = more natural)."""
        tokens = self._tokenize(source)
        log_prob, n = 0.0, 0
        for i in range(len(tokens) - 2):
            trigram = (tokens[i], tokens[i+1], tokens[i+2])
            prefix  = (tokens[i], tokens[i+1])
            # Add-1 (Laplace) smoothing
            p = (self.counts[trigram] + 1) / (self.totals[prefix] + len(self.counts))
            log_prob += math.log(p)
            n += 1
        return log_prob / n if n > 0 else float("-inf")

    @staticmethod
    def _tokenize(source: str) -> list[str]:
        tokens = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(source).readline):
                if tok.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.ENCODING):
                    tokens.append(tok.string)
        except tokenize.TokenError:
            pass
        return tokens
```

**Wiring:** `_parallel_rag_resolve()` retrieves top-5 candidates (up from 3), sorts by `TrigramLM.score()` descending, then passes the ranked list to the promotion gate.

> `.env` change: `VESTIGE_VECTOR_TOP_K=5` (was `3`)

---

### Module 3 — `vestige_mutation.py` (Patch Verification)

Verifies a patch actually fixes the failure by generating **AST mutants** and confirming the test suite kills at least one.

```python
# core/ouroboros/vestige_mutation.py
import ast, copy, subprocess
from dataclasses import dataclass

@dataclass
class MutationResult:
    killed: int    # mutants killed by test suite
    survived: int  # mutants that passed (bad)
    total: int

class MutantGenerator(ast.NodeTransformer):
    """Generates mutants via three operators."""

    def negate_condition(self, node: ast.If) -> list[ast.AST]:
        m = copy.deepcopy(node)
        m.test = ast.UnaryOp(op=ast.Not(), operand=m.test)
        return [m]

    def swap_compare(self, node: ast.Compare) -> list[ast.AST]:
        swaps = {ast.Lt: ast.Gt, ast.Gt: ast.Lt, ast.LtE: ast.GtE,
                 ast.GtE: ast.LtE, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
        mutants = []
        for i, op in enumerate(node.ops):
            if type(op) in swaps:
                m = copy.deepcopy(node)
                m.ops[i] = swaps[type(op)]()
                mutants.append(m)
        return mutants

    def swap_arith(self, node: ast.BinOp) -> list[ast.AST]:
        swaps = {ast.Add: ast.Sub, ast.Sub: ast.Add,
                 ast.Mult: ast.Div, ast.Div: ast.Mult}
        if type(node.op) in swaps:
            m = copy.deepcopy(node)
            m.op = swaps[type(node.op)]()
            return [m]
        return []

def mutation_verify(patch_source: str, test_cmd: list[str]) -> MutationResult:
    """
    Returns MutationResult. Promotion gate requires killed >= 1.
    """
    tree = ast.parse(patch_source)
    gen  = MutantGenerator()
    mutants = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            mutants.extend(gen.negate_condition(node))
        elif isinstance(node, ast.Compare):
            mutants.extend(gen.swap_compare(node))
        elif isinstance(node, ast.BinOp):
            mutants.extend(gen.swap_arith(node))

    killed = survived = 0
    for mutant in mutants:
        src = ast.unparse(ast.fix_missing_locations(mutant))
        result = subprocess.run(test_cmd, input=src, capture_output=True, timeout=10)
        if result.returncode != 0:
            killed += 1
        else:
            survived += 1

    return MutationResult(killed=killed, survived=survived, total=len(mutants))
```

**Wiring:** 4th gate in the promotion pipeline — `mutation_verify()` must return `killed >= 1` for a patch to be accepted.

---

### Module 4 — `vestige_patch_graph.py` (Lineage DAG)

Tracks patch lineage as a **directed acyclic graph** (DAG). DFS cycle detection raises `OuroborosSpiral`.

```python
# core/ouroboros/vestige_patch_graph.py
from collections import defaultdict

class OuroborosSpiral(Exception):
    """Raised when a patch cycle is detected in the DAG."""

class PatchGraph:
    def __init__(self):
        self.edges: dict[str, list[str]] = defaultdict(list)  # parent → [children]
        self._visited: set[str] = set()
        self._rec_stack: set[str] = set()

    def add_patch(self, parent_id: str, child_id: str):
        self.edges[parent_id].append(child_id)

    def has_cycle(self) -> bool:
        self._visited.clear()
        self._rec_stack.clear()
        return any(
            self._dfs(node)
            for node in self.edges
            if node not in self._visited
        )

    def _dfs(self, node: str) -> bool:
        self._visited.add(node)
        self._rec_stack.add(node)
        for neighbor in self.edges.get(node, []):
            if neighbor not in self._visited:
                if self._dfs(neighbor):
                    return True
            elif neighbor in self._rec_stack:
                return True
        self._rec_stack.discard(node)
        return False

    def reset(self):
        self.edges.clear()
        self._visited.clear()
        self._rec_stack.clear()
```

**Wiring:**
- `VestigeGate.handle()` calls `patch_graph.has_cycle()` at **every entry point** — before any RAG, LLM, or patch step.
- On cycle detection: raise `OuroborosSpiral`, reset `patch_graph`, clear `semantic_cache`.

---

## Promotion Gate (Updated — 4 Gates)

```
Gate 1: schema_check(result)         — Pydantic structural validation
Gate 2: contract_assertions(result)  — deterministic invariant checks
Gate 3: llm_judge(result, expected)  — semantic correctness via LLM
Gate 4: mutation_verify(patch, cmd)  — must kill >= 1 mutant          ← NEW in v4
```

All four gates must pass. Failure at any gate triggers the retry loop.

---

## NINA Component Mapping

| Component | Role | Model |
|---|---|---|
| ninagate | Routes observe→diagnose→patch | SmolLM3-3B (routing) |
| ninaflash | File-level patch + hot-reload | Qwen3.6-27B (code gen) |
| ninasync | Loop state + replay log | DeepSeek V4-Flash (long-ctx) |

---

## .env Changes (v4.0)

```env
# Bumped to feed naturalness ranker enough candidates
VESTIGE_VECTOR_TOP_K=5   # was 3
```

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| v1.0 | 2026-06-25 | Initial blueprint — core loop, observer, patcher, kill switch |
| v1.1 | 2026-06-25 | Added SOVEREIGN/HYDRA context |
| v4.0 | 2026-06-29 | VESTIGE layer: SBFL, naturalness trigram LM, mutation testing, patch DAG |

---

*Location: `docs/research/OUROBOROS_BLUEPRINT.md`*
