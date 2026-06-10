import pytest

@pytest.fixture
def nina_tmp_dir(tmp_path):
    d = tmp_path / "nina_test"
    d.mkdir()
    yield d

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setenv("TELEGRAM_TOKEN", "test")
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test")
    yield
