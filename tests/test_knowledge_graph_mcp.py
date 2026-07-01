"""
Unit tests for NINA's Knowledge Graph and MCP Client.
"""
from __future__ import annotations
import pytest
import os
from pathlib import Path
from core.knowledge_graph import KnowledgeGraph
from core.mcp_client import MCPClient

class PurePythonDiGraph:
    def __init__(self):
        self.nodes_data = {}
        self.edges_list = []

    def add_node(self, node_id, **attrs):
        self.nodes_data[node_id] = attrs

    def add_edge(self, src, tgt, **attrs):
        self.edges_list.append({"source": src, "target": tgt, **attrs})

    def get_nodes(self):
        return self.nodes_data

    def neighbors(self, node_id):
        return [e["target"] for e in self.edges_list if e["source"] == node_id]

    def get_edges(self):
        return self.edges_list

    def remove_node(self, node_id):
        if node_id in self.nodes_data:
            del self.nodes_data[node_id]
        self.edges_list = [e for e in self.edges_list if e["source"] != node_id and e["target"] != node_id]


TEST_KG_FILE = "data/test_knowledge_graph.json"

@pytest.fixture(autouse=True)
def cleanup_test_files():
    # Setup
    p = Path(TEST_KG_FILE)
    if p.exists():
        p.unlink()
    yield
    # Teardown
    if p.exists():
        p.unlink()


def test_pure_python_digraph():
    g = PurePythonDiGraph()
    g.add_node("A", type="file", size=100)
    g.add_node("B", type="module")
    g.add_edge("A", "B", relation="imports")

    assert "A" in g.get_nodes()
    assert g.get_nodes()["A"]["size"] == 100
    assert g.neighbors("A") == ["B"]
    
    edges = g.get_edges()
    assert len(edges) == 1
    assert edges[0]["source"] == "A"
    assert edges[0]["target"] == "B"
    assert edges[0]["relation"] == "imports"

    g.remove_node("B")
    assert "B" not in g.get_nodes()
    assert g.neighbors("A") == []


@pytest.mark.asyncio
async def test_knowledge_graph_operations():
    kg = KnowledgeGraph(file_path=TEST_KG_FILE)
    await kg.add_entity("main.py", "file", {"lines": 149})
    await kg.add_entity("core/router.py", "file")
    await kg.add_relation("main.py", "imports", "core/router.py")

    ent = await kg.get_entity("main.py")
    assert ent["type"] == "file"
    assert ent["lines"] == 149
    assert kg.query_neighbors("main.py") == ["core/router.py"]

    entities = kg.get_all_entities_by_type("file")
    assert "main.py" in entities
    assert "core/router.py" in entities

    # Save and Load
    kg.save()
    assert os.path.exists(TEST_KG_FILE)

    kg2 = KnowledgeGraph(file_path=TEST_KG_FILE)
    ent2 = await kg2.get_entity("main.py")
    assert ent2["lines"] == 149
    assert kg2.query_neighbors("main.py") == ["core/router.py"]


@pytest.mark.asyncio
async def test_mcp_client_local_tools():
    client = MCPClient()

    async def my_tool(x: int) -> int:
        return x + 1

    client.register_local_tool("add_one", my_tool)

    tools = await client.list_tools()
    assert any(t.name == "add_one" for t in tools)

    res = await client.call("add_one", {"x": 5})
    assert res.success
    assert res.content == 6

    # Call nonexistent
    res2 = await client.call("invalid_tool", {})
    assert not res2.success
