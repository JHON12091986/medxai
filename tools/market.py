import json
from tools.retry import retry, ToolResult
import logging
from datetime import datetime

logger = logging.getLogger("nina.tools")

WATCHLIST = [
    {"ticker": "GP", "threshold_pct": 1.0, "last_price": 250.0},
    {"ticker": "BATBC", "threshold_pct": 1.0, "last_price": 500.0},
    {"ticker": "SQURPHARMA", "threshold_pct": 1.5, "last_price": 210.0},
]

@retry
def _fetch_dummy_price(ticker: str) -> float:
    """
    Abstracted dummy price source.
    Returns a mocked price to simulate market movements.
    """
    # Simple deterministic mock for now.
    mock_prices = {
        "GP": 253.5,        # +1.4%
        "BATBC": 498.0,     # -0.4%
        "SQURPHARMA": 215.0 # +2.3%
    }
    return mock_prices.get(ticker, 100.0)

async def run_market_monitor(nina_os=None) -> ToolResult:
    """
    Evaluates a watchlist of tickers against dummy prices.
    Generates a human-readable summary and JSON result.
    Logs output to tools.log.
    """
    try:
        logger.info("market_monitor_started")
        results = []
        alerts = []

        for item in WATCHLIST:
            ticker = item["ticker"]
            threshold = item["threshold_pct"]
            last_price = item["last_price"]

            current_price = _fetch_dummy_price(ticker)

            change = current_price - last_price
            change_pct = (change / last_price) * 100

            status = {
                "ticker": ticker,
                "last_price": last_price,
                "current_price": current_price,
                "change_pct": round(change_pct, 2),
                "alert": False
            }

            if abs(change_pct) >= threshold:
                status["alert"] = True
                direction = "UP" if change > 0 else "DOWN"
                alerts.append(f"{ticker}: {current_price} ({direction} {abs(change_pct):.2f}%)")

            results.append(status)

        summary = "Market Monitor Run: "
        if alerts:
            summary += "Alerts triggered for: " + ", ".join(alerts)
        else:
            summary += "No significant movements."

        logger.info(f"market_monitor_summary: {summary}")
        logger.info(f"market_monitor_json: {json.dumps(results)}")

        return ToolResult.success({
            "summary": summary,
            "details": results,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"market_monitor_error: {str(e)}")
        return ToolResult.failure(str(e))
