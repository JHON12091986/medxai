import ast
import hashlib
import threading
from typing import Dict, Tuple

class ASTCache:
    def __init__(self):
        self._cache: Dict[str, Tuple[str, ast.AST, int]] = {}
        self._lock = threading.Lock()

    def _get_file_hash(self, filepath: str) -> str:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def get_ast(self, filepath: str) -> ast.AST:
        current_hash = self._get_file_hash(filepath)

        with self._lock:
            if filepath in self._cache:
                cached_hash, cached_ast, _ = self._cache[filepath]
                if cached_hash == current_hash:
                    return cached_ast

            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            parsed_ast = ast.parse(source)
            node_count = sum(1 for _ in ast.walk(parsed_ast))

            self._cache[filepath] = (current_hash, parsed_ast, node_count)
            return parsed_ast

    def count_tokens(self, filepath: str) -> int:
        current_hash = self._get_file_hash(filepath)

        with self._lock:
            if filepath in self._cache:
                cached_hash, _, cached_count = self._cache[filepath]
                if cached_hash == current_hash:
                    return cached_count

            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            parsed_ast = ast.parse(source)
            node_count = sum(1 for _ in ast.walk(parsed_ast))

            self._cache[filepath] = (current_hash, parsed_ast, node_count)
            return node_count

_global_cache = ASTCache()

def get_ast(filepath: str) -> ast.AST:
    return _global_cache.get_ast(filepath)

def count_tokens(filepath: str) -> int:
    return _global_cache.count_tokens(filepath)
