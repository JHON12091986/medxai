import json
import pytest
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.memory import MemorySystem, MemoryHealth
from core.memory_manager import ScratchpadManager

@pytest.fixture
def mock_paths(tmp_path):
    facts_file = tmp_path / "facts.json"
    chroma_dir = tmp_path / "chromadb"
    scratchpad_file = tmp_path / "scratchpad.json"

    with patch("core.memory.FACTS_FILE", facts_file), \
         patch("core.memory.CHROMA_DIR", chroma_dir), \
         patch("core.memory_manager.Path") as MockPath:

        # We need Path("data/memory/scratchpad.json") to return our tmp_path
        def side_effect(arg):
            if str(arg) == "data/memory/scratchpad.json":
                return scratchpad_file
            return Path(arg)
        MockPath.side_effect = side_effect
        yield {"facts": facts_file, "chroma": chroma_dir, "scratchpad": scratchpad_file}

@pytest.fixture
def mock_chromadb():
    with patch("core.memory.chromadb.PersistentClient") as mock_client:
        with patch("core.memory.embedding_functions.OllamaEmbeddingFunction"):
            mock_client_instance = MagicMock()
            mock_col_instance = MagicMock()
            mock_client_instance.get_or_create_collection.return_value = mock_col_instance
            mock_client.return_value = mock_client_instance
            yield mock_client_instance, mock_col_instance

# Existing tests
def test_facts_loads(mock_paths):
    facts_file = mock_paths["facts"]
    facts_file.write_text('{"test": "data"}')

    with open(facts_file, 'r') as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert data["test"] == "data"

def test_memory_health_returns_dict(mock_paths):
    health = MemoryHealth.check()
    assert isinstance(health, dict)
    assert "chromadb_ok" in health
    assert "facts_ok" in health
    assert "collection_count" in health

def test_scratchpad_store_get(mock_paths):
    manager = ScratchpadManager()
    manager.store('x', 1)
    val = manager.get('x')
    assert val == 1

def test_scratchpad_ttl_expired(mock_paths):
    manager = ScratchpadManager()
    manager.store('temp', 'value', ttl_seconds=0)
    time.sleep(1) # wait for expiry
    val = manager.get('temp')
    assert val is None

def test_scratchpad_clear_expired(mock_paths):
    manager = ScratchpadManager()
    manager.store('expired', 'value', ttl_seconds=0)
    manager.store('not_expired', 'value', ttl_seconds=10)
    time.sleep(1)
    manager.clear_expired()

    with open(manager.file_path, 'r') as f:
        data = json.load(f)

    assert 'expired' not in data
    assert 'not_expired' in data

def test_scratchpad_atomic_write(mock_paths):
    manager = ScratchpadManager()
    manager.store('a', 1)
    manager.store('b', 2)

    with open(manager.file_path, 'r') as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert data['a']['value'] == 1
    assert data['b']['value'] == 2

# New Tests (F-02 behavior + general requirements)

@pytest.mark.asyncio
async def test_1_facts_loading(mock_paths, mock_chromadb):
    # MemorySystem loads facts.json correctly; handles missing file
    mem = MemorySystem()
    facts_file = mock_paths["facts"]
    # Test missing file handling
    if facts_file.exists():
        facts_file.unlink()
    await mem.initialize()
    assert mem.facts == {}

    # Test loading
    facts_file.parent.mkdir(parents=True, exist_ok=True)
    facts_file.write_text(json.dumps({"name": {"value": "Alice", "ts": 123.0}, "simple": "value"}))
    mem2 = MemorySystem()
    await mem2.initialize()
    assert mem2.facts["name"]["value"] == "Alice"
    assert mem2.facts["simple"]["value"] == "value"

@pytest.mark.asyncio
async def test_2_personal_context_injection(mock_paths, mock_chromadb):
    # build_context() output always starts with "--- PERSONAL CONTEXT ---" block
    mem = MemorySystem()
    await mem.initialize()
    context = await mem.build_context("hello")
    assert context.startswith("--- PERSONAL CONTEXT ---")

@pytest.mark.asyncio
async def test_3_personal_context_fields(mock_paths, mock_chromadb):
    # block contains name, role, organization, location
    mem = MemorySystem()
    await mem.initialize()
    context = await mem.build_context("hello")
    assert "name:" in context.lower()
    assert "role:" in context.lower()
    assert "organization:" in context.lower()
    assert "location:" in context.lower()

@pytest.mark.asyncio
async def test_4_personal_context_fallback(mock_paths, mock_chromadb):
    # if facts.json empty, block still present with "unknown" values
    mem = MemorySystem()
    # Ensure facts are empty
    facts_file = mock_paths["facts"]
    if facts_file.exists():
        facts_file.unlink()
    await mem.initialize()
    context = await mem.build_context("hello")
    # Should have "unknown" values
    assert "unknown" in context.lower()
    assert "name:" in context.lower()

@pytest.mark.asyncio
async def test_5_chromadb_results_appended(mock_paths, mock_chromadb):
    # semantic results appear AFTER personal context block
    _, mock_col = mock_chromadb
    mock_col.count.return_value = 1
    mock_col.query.return_value = {
        "documents": [["Semantic Result 1"]],
        "metadatas": [[{"ts": 100}]]
    }
    mem = MemorySystem()
    await mem.initialize()
    context = await mem.build_context("hello")

    assert "--- PERSONAL CONTEXT ---" in context
    assert "Semantic Result 1" in context

    # Check order
    pc_index = context.find("--- PERSONAL CONTEXT ---")
    sr_index = context.find("Semantic Result 1")
    assert pc_index < sr_index

def test_6_get_facts_returns_dict():
    # get_facts() returns dict, not None
    mem = MemorySystem()
    facts = mem.get_facts()
    assert isinstance(facts, dict)
    assert facts is not None

@pytest.mark.asyncio
async def test_7_build_context_nonempty(mock_paths, mock_chromadb):
    # build_context("test query") always returns non-empty str
    mem = MemorySystem()
    await mem.initialize()
    context = await mem.build_context("test query")
    assert isinstance(context, str)
    assert len(context.strip()) > 0

@pytest.mark.asyncio
async def test_8_add_memory(mock_paths, mock_chromadb):
    # MemorySystem.save_turn() stores to ChromaDB without exception
    _, mock_col = mock_chromadb
    mem = MemorySystem()
    await mem.initialize()

    await mem.save_turn("user", "test content")

    assert mock_col.add.called

@pytest.mark.asyncio
async def test_9_initialize_graceful(mock_paths):
    # if Ollama unavailable, initialize() logs warning but does not raise (mock chromadb client)
    with patch("core.memory.chromadb.PersistentClient") as mock_client:
        with patch("core.memory.embedding_functions.OllamaEmbeddingFunction"):
            # Simulate Ollama unavailable or ChromaDB error
            mock_client.side_effect = Exception("Ollama Down")
            mem = MemorySystem()
            # Should not raise
            await mem.initialize()
            assert mem.client is None
            assert mem.col is None

@pytest.mark.asyncio
async def test_10_context_length_bounded(mock_paths, mock_chromadb):
    # build_context() output under 4000 chars for typical query (prevents context window overflow)
    _, mock_col = mock_chromadb
    mock_col.count.return_value = 10

    # Return large amount of text
    long_doc = "word " * 1000  # 5000 chars
    mock_col.query.return_value = {
        "documents": [[long_doc] * 5],
        "metadatas": [[{"ts": i} for i in range(5)]]
    }

    mem = MemorySystem()
    await mem.initialize()
    context = await mem.build_context("hello")
    assert len(context) < 4000
