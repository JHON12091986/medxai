"""
memory/trie_index.py
NINA Local Inverted Text Index (No sentence-transformers)

Sub-millisecond keyword search across Nina's files without
any neural embedding model. Replaces heavy vector search
for exact and near-exact lookups.

Two structures:
    TrieNode / Trie   — prefix tree for sub-ms autocomplete/prefix match
    InvertedIndex     — keyword → {file_path: [line_numbers]} map

Usage:
    from memory.trie_index import InvertedIndex

    idx = InvertedIndex.load()
    idx.index_file(Path("core/kernel.py"))
    results = idx.search("circuit_breaker")
    # → {'core/circuit_breaker.py': [1, 14, 28], ...}
    idx.save()
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).parent.parent
STORE = ROOT / "data" / "trie_index.json"

# Token pattern: words, dotted names, underscored identifiers
TOKEN_RE = re.compile(r"[\w][\w\.]*")


# ------------------------------------------------------------------ #
#  Trie                                                                #
# ------------------------------------------------------------------ #

class TrieNode:
    __slots__ = ("children", "is_end", "count")

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end: bool = False
        self.count: int = 0


class Trie:
    """Prefix tree for sub-millisecond autocomplete over known tokens."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word.lower():
            node = node.children.setdefault(ch, TrieNode())
            node.count += 1
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._traverse(word.lower())
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> List[str]:
        node = self._traverse(prefix.lower())
        if node is None:
            return []
        results: List[str] = []
        self._collect(node, list(prefix.lower()), results)
        return results

    def _traverse(self, s: str) -> Optional[TrieNode]:
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def _collect(self, node: TrieNode, path: list, results: list) -> None:
        if node.is_end:
            results.append("".join(path))
        for ch, child in node.children.items():
            self._collect(child, path + [ch], results)


# ------------------------------------------------------------------ #
#  Inverted Index                                                      #
# ------------------------------------------------------------------ #

class InvertedIndex:
    """Maps every token to the files and line numbers where it appears.

    Schema (JSON):
        { "token": { "rel/path/to/file.py": [1, 14, 28] } }
    """

    def __init__(self):
        # token → canonical_path → [line_numbers]
        self._index: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        self.trie = Trie()

    # ------------------------------------------------------------------ #
    #  Indexing                                                            #
    # ------------------------------------------------------------------ #
    def index_file(self, path: Path) -> int:
        """Index a file. Returns number of tokens indexed."""
        try:
            text = path.read_text(errors="replace")
        except (OSError, PermissionError):
            return 0

        try:
            rel = str(path.resolve().relative_to(ROOT))
        except ValueError:
            rel = str(path)

        # Remove this file's old entries first (re-index on change)
        self._remove_file(rel)

        count = 0
        for lineno, line in enumerate(text.splitlines(), start=1):
            for token in TOKEN_RE.findall(line.lower()):
                if len(token) < 2:
                    continue
                self._index[token][rel].append(lineno)
                self.trie.insert(token)
                count += 1
        return count

    def index_directory(self, directory: Path, extensions: tuple = (".py", ".md", ".txt", ".json")) -> int:
        """Recursively index all matching files under directory."""
        total = 0
        for ext in extensions:
            for fpath in directory.rglob(f"*{ext}"):
                total += self.index_file(fpath)
        return total

    def _remove_file(self, rel: str) -> None:
        to_delete = []
        for token, file_map in self._index.items():
            if rel in file_map:
                del file_map[rel]
            if not file_map:
                to_delete.append(token)
        for token in to_delete:
            del self._index[token]

    # ------------------------------------------------------------------ #
    #  Search                                                              #
    # ------------------------------------------------------------------ #
    def search(self, query: str, top_n: int = 20) -> Dict[str, List[int]]:
        """Exact token search. Returns {file: [lines]} sorted by hit count."""
        token = query.lower().strip()
        hits = dict(self._index.get(token, {}))
        return dict(sorted(hits.items(), key=lambda x: len(x[1]), reverse=True)[:top_n])

    def prefix_search(self, prefix: str, top_n: int = 10) -> List[str]:
        """Return all indexed tokens starting with prefix."""
        return self.trie.starts_with(prefix)[:top_n]

    def search_multi(self, *tokens: str) -> Dict[str, List[int]]:
        """AND search: files containing ALL tokens."""
        if not tokens:
            return {}
        sets = [set(self._index.get(t.lower(), {}).keys()) for t in tokens]
        common = sets[0].intersection(*sets[1:])
        result = {}
        for f in common:
            lines = []
            for t in tokens:
                lines.extend(self._index.get(t.lower(), {}).get(f, []))
            result[f] = sorted(set(lines))
        return result

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #
    def save(self) -> None:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        tmp = STORE.with_suffix(".tmp")
        # Convert defaultdicts to plain dicts for JSON
        plain = {token: dict(files) for token, files in self._index.items()}
        tmp.write_text(json.dumps(plain, separators=(",", ":")))
        tmp.replace(STORE)

    @classmethod
    def load(cls) -> "InvertedIndex":
        idx = cls()
        if STORE.exists():
            try:
                data = json.loads(STORE.read_text())
                for token, files in data.items():
                    for fpath, lines in files.items():
                        idx._index[token][fpath] = lines
                        idx.trie.insert(token)
            except Exception:
                pass  # corrupt index — will rebuild on next index_directory call
        return idx

    def __repr__(self) -> str:
        return f"InvertedIndex(tokens={len(self._index)}, files={len(set(f for fm in self._index.values() for f in fm))})"
