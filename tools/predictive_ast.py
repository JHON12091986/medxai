#!/usr/bin/env python3
"""
NINA Predictive AST Analyzer
Calculates static risk score, impact radius, and cyclomatic complexity
of targeted codebase updates before OODA or Jules deploys them.
"""

import ast
import pathlib
import sys
import json
from typing import Dict, Any

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1
        self.functions = 0
        self.imports = 0
        self.globals = 0

    def visit_FunctionDef(self, node):
        self.functions += 1
        self.complexity += 1  # Base overhead per function
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.functions += 1
        self.complexity += 1
        self.generic_visit(node)

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_And(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Or(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Import(self, node):
        self.imports += len(node.names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.imports += len(node.names)
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Count global variables
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.globals += 1
        self.generic_visit(node)

def analyze_file_risk(filepath: str) -> Dict[str, Any]:
    """Performs static analysis to evaluate the risk of a python script."""
    path = pathlib.Path(filepath)
    if not path.exists() or not path.is_file():
        return {
            "error": f"File {filepath} not found.",
            "risk_score": 0.0,
            "complexity": 0,
            "status": "MISSING"
        }

    try:
        content = path.read_text(errors="ignore")
        tree = ast.parse(content, filename=filepath)
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        lines = len(content.splitlines())
        
        # Calculate dependency impact radius (how many other python files import this file)
        impact_radius = calculate_impact_radius(path)
        
        # Calculate Risk Score (composite metric of complexity, globals, and impact radius)
        # Higher score = higher maintenance/modification risk
        base_risk = (visitor.complexity * 0.4) + (visitor.globals * 1.5) + (impact_radius * 3.0)
        risk_score = round(min(100.0, max(1.0, base_risk)), 2)
        
        risk_category = "LOW"
        if risk_score > 35.0:
            risk_category = "HIGH"
        elif risk_score > 15.0:
            risk_category = "MEDIUM"

        return {
            "file": path.name,
            "lines_of_code": lines,
            "cyclomatic_complexity": visitor.complexity,
            "function_count": visitor.functions,
            "global_assignments": visitor.globals,
            "import_count": visitor.imports,
            "impact_radius": impact_radius,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "status": "OK"
        }
    except Exception as e:
        return {
            "file": path.name,
            "error": str(e),
            "risk_score": 50.0,  # High default on parsing failure
            "risk_category": "HIGH",
            "status": "ERROR"
        }

def calculate_impact_radius(target_path: pathlib.Path) -> int:
    """Finds how many other .py files import the target module."""
    module_name = target_path.stem
    repo_root = target_path.resolve().parent
    # Trace up to repo root if in subfolders
    for _ in range(5):
        if (repo_root / "nina_context_graph.json").exists() or (repo_root / "AGENTS.md").exists():
            break
        repo_root = repo_root.parent

    impact_count = 0
    for py_file in repo_root.glob("**/*.py"):
        if py_file.resolve() == target_path.resolve():
            continue
        try:
            content = py_file.read_text(errors="ignore")
            # Simple keyword check for fast scanning
            if f"import {module_name}" in content or f"from {module_name}" in content:
                impact_count += 1
        except Exception:
            pass
    return impact_count

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 predictive_ast.py <file_path>")
        sys.exit(1)
        
    res = analyze_file_risk(sys.argv[1])
    print(json.dumps(res, indent=2))
