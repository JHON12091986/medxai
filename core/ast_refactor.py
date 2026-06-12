import ast


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
        # We assume the code is indented inside the original function
        # the new function will be at module level, or we return the code as is.
        # Actually it's easier to just return the code with 4 spaces indent.
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
