import pytest

# Mocks to avoid hitting Ollama connection for tests
class MockCollection:
    def __init__(self):
        self.docs = []
        self.metas = []
        self.ids = []

    def add(self, documents, ids, metadatas):
        self.docs.extend(documents)
        self.ids.extend(ids)
        self.metas.extend(metadatas)

    def count(self):
        return len(self.ids)

    def query(self, query_texts, n_results, where=None, include=None):
        res_docs = []
        res_metas = []
        for i, m in zip(self.docs, self.metas):
            if where and all(m.get(k) == v for k, v in where.items()):
                # We do a basic keyword search instead of actual embeddings for mock
                if any(w.lower() in i.lower() for w in query_texts[0].split()):
                    res_docs.append(i)
                    res_metas.append(m)
        res_ids = []
        for d, i, m in zip(self.docs, self.ids, self.metas):
            if where and all(m.get(k) == v for k, v in where.items()):
                if any(w.lower() in d.lower() for w in query_texts[0].split()):
                    res_docs.append(d)
                    res_metas.append(m)
                    res_ids.append(i)
        return {"documents": [res_docs[:n_results]], "metadatas": [res_metas[:n_results]], "ids": [res_ids[:n_results]]}

    def get(self, where=None, include=None):
        res_docs = []
        res_metas = []
        res_ids = []
        for d, i, m in zip(self.docs, self.ids, self.metas):
            if where and all(m.get(k) == v for k, v in where.items()):
                res_docs.append(d)
                res_metas.append(m)
                res_ids.append(i)
        return {"documents": res_docs, "metadatas": res_metas, "ids": res_ids}

from core.memory import MemorySystem

@pytest.fixture
def memory_system(tmp_path):
    db_file = tmp_path / "test_kb.db"
    mem = MemorySystem(db_path=str(db_file))
    mem.col = MockCollection()
    yield mem

@pytest.mark.asyncio
async def test_kb_primitives(memory_system):
    # Add entries
    id1 = await memory_system.kb_add_entry(tags=["work", "project"], text="NINA needs F-08 kb primitives.", source="test")
    id2 = await memory_system.kb_add_entry(tags=["personal"], text="Buy groceries tomorrow.", source="test")

    assert id1.startswith("kb_")
    assert id2.startswith("kb_")

    # Search without query (should get both, sorted by time)
    results = await memory_system.kb_search()
    assert len(results) == 2

    # Search by tag
    results_work = await memory_system.kb_search(tag="work")
    assert len(results_work) == 1
    assert results_work[0]["id"] == id1

    # Search by query
    results_query = await memory_system.kb_search(query="groceries")
    assert len(results_query) == 1
    assert results_query[0]["id"] == id2

    # Search by tag and query
    results_both = await memory_system.kb_search(tag="work", query="NINA")
    assert len(results_both) == 1
    assert results_both[0]["id"] == id1
