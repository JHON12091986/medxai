import pytest
from tools.retry import retry, ToolResult
from tools.finance import run_expenditure_report
from tools.market import run_market_monitor

# --- RETRY TESTS ---
def test_retry_succeeds_first_attempt():
    calls = []
    @retry(max_attempts=3, backoff_seconds=0.01)
    def my_func():
        calls.append(1)
        return "success"

    result = my_func()
    assert result == "success"
    assert len(calls) == 1

def test_retry_succeeds_on_second():
    calls = []
    @retry(max_attempts=3, backoff_seconds=0.01)
    def my_func():
        calls.append(1)
        if len(calls) == 1:
            raise ValueError("first time fail")
        return "success"

    result = my_func()
    assert result == "success"
    assert len(calls) == 2

def test_retry_exhausted_raises():
    calls = []
    @retry(max_attempts=2, backoff_seconds=0.01)
    def my_func():
        calls.append(1)
        raise ValueError("always fail")

    with pytest.raises(ValueError, match="always fail"):
        my_func()

    assert len(calls) == 2

# --- TOOL RESULT TESTS ---
def test_tool_result_success():
    res = ToolResult.success(42)
    assert res.ok is True
    assert res.data == 42
    assert res.error is None

def test_tool_result_failure():
    res = ToolResult.failure("err")
    assert res.ok is False
    assert res.data is None
    assert res.error == "err"

# --- FINANCE/MARKET TESTS ---
def test_finance_returns_tool_result():
    # Calling the finance function (it parses strings, no HTTP needed)
    res = run_expenditure_report("2023-10-15, 50.00, Groceries")
    assert isinstance(res, ToolResult)
    assert res.ok is True

@pytest.mark.asyncio
async def test_market_returns_tool_result(monkeypatch):
    # market uses a dummy mock anyway, but we mock the internal dummy
    import tools.market
    monkeypatch.setattr(tools.market, "_fetch_dummy_price", lambda t: 100.0)

    res = await run_market_monitor()
    assert isinstance(res, ToolResult)
    assert res.ok is True
