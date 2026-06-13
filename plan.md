1. **Context Injector (AG-N-05)**
   - Update `cmd_code_call_stack` in `tools/ninaflash.py`.
   - Replace `ast.unparse(current_node)` with `ast.get_source_segment(source, current_node)` to preserve formatting and comments. I'll read the `source` text once and pass it.

2. **Dependency Cycle Detector (AG-N-08)**
   - Wait, `AG-N-08` says "Dependency Cycle Detector — Identify circular imports locally."
   - Let's check the bug. I think the bug is the length of cycles (`len(cycle) > 2`). For a direct cycle `A -> A`, length is 2. Let's fix this to `len(cycle) >= 2`.
   - Wait! The instruction says: "The memory implies we don't need any new tasks here, wait, memory says: "To locally identify circular dependency imports within the project, use the command `python3 tools/ninaflash.py code cycles`".
   - Okay, maybe just make sure there are no other bugs. I will change `len(cycle) > 2` to `len(cycle) >= 2` and fix the relative import logic (`get_module_name` vs `__init__.py`). Wait, `get_module_name` logic in `cmd_code_cycles` is what I found. I'll fix the `module_name.split(".")` for relative imports so that `__init__.py` modules are treated properly (append `__init__` if it's an init module internally, or adjust level).

3. **Code Complexity Watchdog (AG-N-09)**
   - Add `cmd_check_complexity(args)` to `tools/ninaflash.py` to calculate cyclomatic complexity using the `ast` module.
   - Nodes to count: `If, For, AsyncFor, While, ExceptHandler, With, AsyncWith, BoolOp`. (I'll just add 1 for each to match the text literally, or `+1` for each BoolOp).
   - Hook it up to the argument parser: `p_chk.add_parser("complexity").add_argument("file")` (Wait, it's `args.sub == "complexity"`).

4. **Symbol Migration Tool (AG-N-10)**
   - Refactor `cmd_code_migrate` in `tools/ninaflash.py` to use `libcst`.
   - `libcst.parse_module(source)`
   - Create a `CSTTransformer` that renames the `old_name` to `new_name`.
   - Write back `module.code`.

5. **Pre-commit Checks**
   - Run linter/tests as requested by `pre_commit_instructions`.
