import argparse
import os
import pathlib
import sys
import libcst as cst

class ReturnVisitor(cst.CSTVisitor):
    def __init__(self):
        self.has_value_return = False
        self.has_yield = False

    def visit_FunctionDef(self, node: cst.FunctionDef):
        return False

    def visit_ClassDef(self, node: cst.ClassDef):
        return False

    def visit_Return(self, node: cst.Return):
        if node.value is not None:
            self.has_value_return = True

    def visit_Yield(self, node: cst.Yield):
        self.has_yield = True

class TypeHintEnforcer(cst.CSTTransformer):
    def __init__(self):
        self.added_any = False

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        new_params = []
        for param in updated_node.params.params:
            if param.name.value in ("self", "cls"):
                new_params.append(param)
                continue
            if param.annotation is None:
                new_param = param.with_changes(
                    annotation=cst.Annotation(annotation=cst.Name("Any"))
                )
                new_params.append(new_param)
                self.added_any = True
            else:
                new_params.append(param)

        # Handle star_arg
        new_star_arg = updated_node.params.star_arg
        if isinstance(new_star_arg, cst.Param) and new_star_arg.annotation is None:
            new_star_arg = new_star_arg.with_changes(annotation=cst.Annotation(annotation=cst.Name("Any")))
            self.added_any = True

        # Handle star_kwarg
        new_star_kwarg = updated_node.params.star_kwarg
        if isinstance(new_star_kwarg, cst.Param) and new_star_kwarg.annotation is None:
            new_star_kwarg = new_star_kwarg.with_changes(annotation=cst.Annotation(annotation=cst.Name("Any")))
            self.added_any = True

        new_kwonly = []
        for param in updated_node.params.kwonly_params:
            if param.annotation is None:
                new_param = param.with_changes(
                    annotation=cst.Annotation(annotation=cst.Name("Any"))
                )
                new_kwonly.append(new_param)
                self.added_any = True
            else:
                new_kwonly.append(param)

        new_posonly = []
        for param in updated_node.params.posonly_params:
            if param.annotation is None:
                new_param = param.with_changes(
                    annotation=cst.Annotation(annotation=cst.Name("Any"))
                )
                new_posonly.append(new_param)
                self.added_any = True
            else:
                new_posonly.append(param)

        new_returns = updated_node.returns
        if new_returns is None:
            v = ReturnVisitor()
            updated_node.body.visit(v)
            if v.has_value_return or v.has_yield:
                new_returns = cst.Annotation(annotation=cst.Name("Any"))
                self.added_any = True
            else:
                new_returns = cst.Annotation(annotation=cst.Name("None"))

        return updated_node.with_changes(
            params=updated_node.params.with_changes(
                params=new_params,
                star_arg=new_star_arg,
                star_kwarg=new_star_kwarg,
                kwonly_params=new_kwonly,
                posonly_params=new_posonly
            ),
            returns=new_returns
        )

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        if self.added_any:
            # Check if typing is already imported
            has_any = False
            for stmt in updated_node.body:
                if isinstance(stmt, cst.SimpleStatementLine):
                    for obj in stmt.body:
                        if isinstance(obj, cst.ImportFrom) and obj.module is not None and obj.module.value == "typing":
                            if isinstance(obj.names, cst.ImportStar):
                                has_any = True
                            else:
                                for name in obj.names:
                                    if name.name.value == "Any":
                                        has_any = True

            if not has_any:
                import_stmt = cst.SimpleStatementLine(body=[
                    cst.ImportFrom(
                        module=cst.Name("typing"),
                        names=[cst.ImportAlias(name=cst.Name("Any"))]
                    )
                ])
                # Find the best place to insert
                insert_idx = 0
                for i, stmt in enumerate(updated_node.body):
                    if isinstance(stmt, cst.SimpleStatementLine):
                        # skip docstring
                        if isinstance(stmt.body[0], cst.Expr) and isinstance(stmt.body[0].value, (cst.SimpleString, cst.ConcatenatedString)):
                            insert_idx = i + 1
                            continue
                        # skip future import
                        if isinstance(stmt.body[0], cst.ImportFrom) and stmt.body[0].module is not None and stmt.body[0].module.value == "__future__":
                            insert_idx = i + 1
                            continue
                        break

                new_body = list(updated_node.body)
                new_body.insert(insert_idx, import_stmt)
                return updated_node.with_changes(body=tuple(new_body))
        return updated_node

def process_file(filepath: str, fix: bool = False):
    with open(filepath, 'r', encoding='utf-8') as f:
        source_code = f.read()

    try:
        module = cst.parse_module(source_code)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return False

    transformer = TypeHintEnforcer()
    modified_module = module.visit(transformer)

    if modified_module.code != source_code:
        if fix:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_module.code)
            print(f"Fixed: {filepath}")
            return True
        else:
            print(f"Needs fixing: {filepath} (Run with --fix to apply changes)")
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Enforce type hints in Python files.")
    parser.add_argument("path", help="Path to file or directory")
    parser.add_argument("--fix", action="store_true", help="Apply fixes")
    args = parser.parse_args()

    target_path = pathlib.Path(args.path)
    all_passed = True

    if target_path.is_file() and target_path.suffix == '.py':
        all_passed = process_file(str(target_path), args.fix)
    elif target_path.is_dir():
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith('.py'):
                    if not process_file(os.path.join(root, file), args.fix):
                        all_passed = False
    else:
        print(f"Invalid path or no Python files found: {args.path}")
        sys.exit(1)

    if not all_passed and not args.fix:
        sys.exit(1)

if __name__ == "__main__":
    main()
