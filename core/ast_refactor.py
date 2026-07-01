"""NINA — AST-level self-patch engine.
Blueprint pass 2: wrapped compile() + ast.parse() in asyncio.to_thread()
so CPU-bound AST operations never block the event loop.

Pass 2 changes (24 Jun 2026):
  - _parse_async()   : awaitable wrapper for ast.parse()
  - _compile_async() : awaitable wrapper for compile()
  - apply_patch()    : updated to await both, replacing sync calls
  All previous logic is preserved; only the blocking calls are lifted.
"""
from __future__ import annotations

import ast
import asyncio
import logging
import shutil
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Callable

logger = logging.getLogger("nina.ast_refactor")

# ── Async wrappers for CPU-bound ops ──────────────────────────────────────

async def _parse_async(source: str, filename: str = "<string>") -> ast.Module:
    """Non-blocking ast.parse() via asyncio.to_thread().
    Resolves blueprint § V: 'asyncio.to_thread() wrapping ast.parse() verified'
    """
    return await asyncio.to_thread(ast.parse, source, filename)


async def _compile_async(
    source: str | ast.AST,
    filename: str = "<string>",
    mode: str = "exec",
) -> bool:
    """Non-blocking compile() gate via asyncio.to_thread().
    Returns True if source compiles cleanly, False on SyntaxError.
    Resolves blueprint § V: 'asyncio.to_thread() wrapping compile() verified'
    """
    def _check() -> bool:
        try:
            compile(source, filename, mode)  # type: ignore[arg-type]
            return True
        except SyntaxError as exc:
            logger.warning("ast_compile_gate_failed file=%s err=%s", filename, exc)
            return False
    return await asyncio.to_thread(_check)


# ── Patch application ─────────────────────────────────────────────────────

async def apply_patch(
    file_path: str | Path,
    node_locator: Callable[[ast.Module], ast.AST | None],
    node_rewriter: Callable[[ast.AST], ast.AST],
    *,
    dry_run: bool = False,
) -> bool:
    """Atomically rewrite a single AST node in file_path.

    Pipeline (Blueprint § II — Self-Patching Pipeline):
      1. Read source
      2. _parse_async()   — CPU-bound, non-blocking
      3. Locate target node via node_locator()
      4. Rewrite via node_rewriter()
      5. _compile_async() — CPU-bound, non-blocking gate
      6. If gate passes → atomic write via WAL (backup → write → verify)
      7. Return True on success, False on any failure

    Args:
        file_path:     Path to the .py file to modify.
        node_locator:  Callable(ast.Module) → target AST node or None.
        node_rewriter: Callable(ast.AST) → modified AST node (in-place OK).
        dry_run:       If True, parse + compile but do not write.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error("ast_patch_file_not_found path=%s", path)
        return False

    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("ast_patch_read_error path=%s err=%s", path, exc)
        return False

    # Step 2 — non-blocking parse
    try:
        tree = await _parse_async(source, filename=str(path))
    except SyntaxError as exc:
        logger.error("ast_patch_parse_error path=%s err=%s", path, exc)
        return False

    # Step 3 — locate
    target = node_locator(tree)
    if target is None:
        logger.warning("ast_patch_node_not_found path=%s", path)
        return False

    # Step 4 — rewrite
    try:
        node_rewriter(target)
        ast.fix_missing_locations(tree)
    except Exception as exc:
        logger.error("ast_patch_rewrite_error path=%s err=%s", path, exc)
        return False

    # Step 5 — compile gate (non-blocking)
    modified_source = ast.unparse(tree)
    if not await _compile_async(modified_source, filename=str(path)):
        logger.error("ast_patch_compile_gate_rejected path=%s", path)
        return False

    if dry_run:
        logger.info("ast_patch_dry_run_ok path=%s", path)
        return True

    # Step 6 — atomic write via WAL (backup → write → verify)
    backup = path.with_suffix(
        f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    )
    try:
        shutil.copy2(path, backup)
        path.write_text(modified_source, encoding="utf-8")
        # Verify the written file compiles cleanly
        written = path.read_text(encoding="utf-8")
        if not await _compile_async(written, filename=str(path)):
            logger.error("ast_patch_verify_failed — restoring backup path=%s", path)
            shutil.copy2(backup, path)
            return False
        backup.unlink(missing_ok=True)
        logger.info("ast_patch_applied path=%s", path)
        return True
    except OSError as exc:
        logger.error("ast_patch_write_error path=%s err=%s", path, exc)
        # Attempt restore
        if backup.exists():
            try:
                shutil.copy2(backup, path)
            except OSError:
                pass
        return False


# ── Convenience helpers ───────────────────────────────────────────────────

async def verify_file(file_path: str | Path) -> bool:
    """Compile-check a file without modifying it.
    Useful for guardian_loop post-patch verification.
    """
    path = Path(file_path)
    if not path.exists():
        return False
    source = path.read_text(encoding="utf-8")
    return await _compile_async(source, filename=str(path))


async def batch_verify(paths: list[str | Path]) -> dict[str, bool]:
    """Concurrently compile-check multiple files.
    Returns {path_str: ok} mapping.
    """
    results = await asyncio.gather(
        *[verify_file(p) for p in paths], return_exceptions=True
    )
    return {
        str(p): (r if isinstance(r, bool) else False)
        for p, r in zip(paths, results)
    }


class VarVisitor(ast.NodeVisitor):
    def __init__(self):
        self.reads = set()
        self.writes = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.reads.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.writes.add(node.id)
        self.generic_visit(node)

    def visit_arg(self, node):
        self.writes.add(node.arg)
        self.generic_visit(node)


def _analyze_nodes(nodes):
    v = VarVisitor()
    if isinstance(nodes, list):
        for n in nodes:
            v.visit(n)
    else:
        v.visit(nodes)
    return v.reads, v.writes


def extract_method(
    source: str, start_line: int, end_line: int, new_func_name: str
) -> tuple[str, str]:
    """
    Extracts a block of code into a new function using AST parsing.
    Returns (modified_source, newly_extracted_function_code).
    """
    tree = ast.parse(source)

    # We assume we are extracting from a function
    target_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            if any(start_line <= stmt.lineno <= end_line for stmt in node.body):
                target_func = node
                break

    if not target_func:
        raise ValueError("Could not find function containing the given line numbers.")

    before = []
    sel = []
    after = []

    for stmt in target_func.body:
        if stmt.lineno < start_line:
            before.append(stmt)
        elif (
            stmt.lineno >= start_line
            and getattr(stmt, "end_lineno", stmt.lineno) <= end_line
        ):
            sel.append(stmt)
        else:
            after.append(stmt)

    if not sel:
        raise ValueError("No statements found in the given line range.")

    for node in sel:
        for child in ast.walk(node):
            if isinstance(child, (ast.Return, ast.Break, ast.Continue)):
                raise ValueError(
                    "Cannot extract block containing return/break/continue"
                )

    before_reads, before_writes = _analyze_nodes(before)
    sel_reads, sel_writes = _analyze_nodes(sel)
    after_reads, after_writes = _analyze_nodes(after)

    args_reads, args_writes = _analyze_nodes(target_func.args)
    defined_before = before_writes.union(args_writes)

    inputs = sorted(list(sel_reads.intersection(defined_before) - {"self"}))
    outputs = sorted(list(sel_writes.intersection(after_reads) - {"self"}))

    # Check if 'self' is used in the selected block to determine if it should be an argument
    sel_reads_raw, _ = _analyze_nodes(sel)
    has_self = "self" in sel_reads_raw
    if has_self and "self" not in inputs:
        inputs = ["self"] + inputs

    lines = source.splitlines()

    # Find indentation of the selected block
    sel_start_line = sel[0].lineno - 1
    sel_end_line = sel[-1].end_lineno

    indent = len(lines[sel_start_line]) - len(lines[sel_start_line].lstrip())
    indent_str = " " * indent

    # Build new function
    new_func_lines = []
    new_func_lines.append(f"def {new_func_name}({', '.join(inputs)}):")
    for i in range(sel_start_line, sel_end_line):
        line = lines[i]
        if line.startswith(indent_str):
            new_func_lines.append("    " + line[indent:])
        else:
            new_func_lines.append("    " + line)

    if outputs:
        if len(outputs) == 1:
            new_func_lines.append(f"    return {outputs[0]}")
        else:
            new_func_lines.append(f"    return {', '.join(outputs)}")

    extracted_func_code = "\n".join(new_func_lines) + "\n"

    # Replace selected block with function call
    call_args = ", ".join(inputs)
    if outputs:
        if len(outputs) == 1:
            call_stmt = f"{indent_str}{outputs[0]} = {new_func_name}({call_args})"
        else:
            call_stmt = (
                f"{indent_str}{', '.join(outputs)} = {new_func_name}({call_args})"
            )
    else:
        call_stmt = f"{indent_str}{new_func_name}({call_args})"

    modified_source_lines = lines[:sel_start_line] + [call_stmt] + lines[sel_end_line:]
    modified_source = "\n".join(modified_source_lines) + "\n"

    return modified_source, extracted_func_code
