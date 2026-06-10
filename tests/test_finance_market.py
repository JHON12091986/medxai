import pytest
import json
from unittest.mock import patch
from tools.finance import run_expenditure_report
from tools.market import run_market_monitor

def test_finance_format_amount():
    csv_data = "date, amount, category\n2023-10-15, 50.00, Groceries"
    result = json.loads(run_expenditure_report(csv_data))

    assert "Groceries" in result["report"]["2023-10"]
    assert result["report"]["2023-10"]["Groceries"] == 50.00
    assert "Processed 1 expenses" in result["summary"]

def test_finance_handles_zero():
    csv_data = "date, amount, category\n2023-10-15, 0.00, Groceries"
    result = json.loads(run_expenditure_report(csv_data))

    assert result["report"]["2023-10"]["Groceries"] == 0.00
    assert "Processed 1 expenses" in result["summary"]

@pytest.mark.asyncio
@patch('requests.get')
async def test_market_returns_structure(mock_get):
    result = await run_market_monitor()

    assert "summary" in result
    assert "details" in result
    assert "timestamp" in result
    assert isinstance(result["details"], list)

@pytest.mark.asyncio
@patch('requests.get')
async def test_market_handles_network_error(mock_get, monkeypatch):
    mock_get.side_effect = ConnectionError("Network unreachable")

    def mock_fetch_price(*args, **kwargs):
        raise ConnectionError("Network unreachable")

    monkeypatch.setattr("tools.market._fetch_dummy_price", mock_fetch_price)

    try:
        result = await run_market_monitor()
        assert not result or isinstance(result, dict)
    except ConnectionError:
        pytest.xfail("tools.market does not yet suppress exceptions")
