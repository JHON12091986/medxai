import ast
import tempfile
import os
from tools.ast_cache import get_ast, count_tokens, ASTCache

def test_ast_cache_get_ast():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def foo():\n    return 1")
        filepath = f.name

    try:
        cache = ASTCache()

        # First call: parses and caches
        tree1 = cache.get_ast(filepath)
        assert isinstance(tree1, ast.AST)

        # Second call: returns cached AST
        tree2 = cache.get_ast(filepath)
        assert tree1 is tree2

        # Modify file
        with open(filepath, 'w') as f:
            f.write("def foo():\n    return 2")

        # Third call: hash mismatch, parses again
        tree3 = cache.get_ast(filepath)
        assert tree3 is not tree1

    finally:
        os.remove(filepath)

def test_ast_cache_count_tokens():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("a = 1")
        filepath = f.name

    try:
        cache = ASTCache()

        count1 = cache.count_tokens(filepath)
        assert count1 > 0

        # Modify file to have more tokens
        with open(filepath, 'w') as f:
            f.write("a = 1\nb = 2")

        count2 = cache.count_tokens(filepath)
        assert count2 > count1

    finally:
        os.remove(filepath)

def test_global_functions():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("print('hello')")
        filepath = f.name

    try:
        tree = get_ast(filepath)
        assert isinstance(tree, ast.AST)

        count = count_tokens(filepath)
        assert count > 0

    finally:
        os.remove(filepath)
