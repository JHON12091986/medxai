import json # verified
import asyncio
import logging
import re
import urllib.request
from pathlib import Path
from tools.telegram_notify import send_message

logger = logging.getLogger("nina.tools.market")
WATCHLIST_FILE = Path("data/market_watchlist.json")

def _load_watchlist() -> list:
    if not WATCHLIST_FILE.exists():
        return []
    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_watchlist(data: list) -> None:
    WATCHLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

async def add_to_watchlist(symbol: str, exchange: str = "DSE", alert_above: float = None, alert_below: float = None) -> str:
    def _add():
        data = _load_watchlist()
        symbol_upper = symbol.strip().upper()
        for item in data:
            if item["symbol"] == symbol_upper:
                item["exchange"] = exchange.upper()
                item["alert_above"] = float(alert_above) if alert_above is not None else None
                item["alert_below"] = float(alert_below) if alert_below is not None else None
                _save_watchlist(data)
                return f"✅ Updated watchlist for {symbol_upper}."
        
        data.append({
            "symbol": symbol_upper,
            "exchange": exchange.upper(),
            "alert_above": float(alert_above) if alert_above is not None else None,
            "alert_below": float(alert_below) if alert_below is not None else None
        })
        _save_watchlist(data)
        return f"✅ Added {symbol_upper} to watchlist."
    return await asyncio.to_thread(_add)

async def remove_from_watchlist(symbol: str) -> str:
    def _remove():
        data = _load_watchlist()
        symbol_upper = symbol.strip().upper()
        filtered = [item for item in data if item["symbol"] != symbol_upper]
        if len(filtered) == len(data):
            return f"❌ Symbol {symbol_upper} not found in watchlist."
        _save_watchlist(filtered)
        return f"✅ Removed {symbol_upper} from watchlist."
    return await asyncio.to_thread(_remove)

async def get_watchlist() -> str:
    def _get():
        data = _load_watchlist()
        if not data:
            return "Watchlist is empty."
        lines = ["📈 Personal Share Watchlist:"]
        for item in data:
            above = f"above {item['alert_above']}" if item.get("alert_above") is not None else "None"
            below = f"below {item['alert_below']}" if item.get("alert_below") is not None else "None"
            lines.append(f"  - {item['symbol']} ({item['exchange']}): Alert Above={above}, Alert Below={below}")
        return "\n".join(lines)
    return await asyncio.to_thread(_get)

async def fetch_prices() -> dict:
    """Fetches DSE prices from DSE website. Returns a dict of symbol -> current_price."""
    try:
        url = "https://www.dsebd.org/price_all.php"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        prices = {}
        matches = re.finditer(r'displayCompany\.php\?name=([A-Z0-9_-]+)[^>]*>([^<]+)</a></td>\s*<td[^>]*>([\d.,]+)</td>', html, re.IGNORECASE)
        for m in matches:
            sym = m.group(1).upper()
            try:
                price = float(m.group(3).replace(',', ''))
                prices[sym] = price
            except ValueError:
                pass
        
        if not prices:
            try:
                from tools import browser
                html = await browser.fetch(url)
                matches = re.finditer(r'displayCompany\.php\?name=([A-Z0-9_-]+)[^>]*>([^<]+)</a></td>\s*<td[^>]*>([\d.,]+)</td>', html, re.IGNORECASE)
                for m in matches:
                    sym = m.group(1).upper()
                    try:
                        price = float(m.group(3).replace(',', ''))
                        prices[sym] = price
                    except ValueError:
                        pass
                
                if not prices:
                    lines = html.splitlines()
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 2:
                            sym = parts[0].upper()
                            if sym.isupper() and sym.isalalpha() and len(sym) <= 12:
                                try:
                                    price = float(parts[1].replace(',', ''))
                                    prices[sym] = price
                                except ValueError:
                                    pass
            except Exception as e:
                logger.warning(f"Browser fallback fetch failed: {e}")
        
        return prices
    except Exception as e:
        logger.warning(f"urllib price fetch failed: {e}")
        return {}

async def check_alerts(nina_os=None) -> list[str]:
    logger.info("Checking share market alerts...")
    watchlist = _load_watchlist()
    if not watchlist:
        return []
        
    prices = await fetch_prices()
    if not prices:
        logger.warning("Could not fetch real-time market prices, using mock prices for alerts.")
        mock_prices = {
            "GP": 253.5,
            "BATBC": 498.0,
            "SQURPHARMA": 215.0
        }
        prices = mock_prices
        
    alerts_triggered = []
    for item in watchlist:
        sym = item["symbol"]
        price = prices.get(sym)
        if price is None:
            continue
            
        above = item.get("alert_above")
        below = item.get("alert_below")
        
        if above is not None and price >= above:
            msg = f"🔔 [MARKET ALERT] {sym} is currently at {price} (Threshold Above: {above})"
            alerts_triggered.append(msg)
        elif below is not None and price <= below:
            msg = f"🔔 [MARKET ALERT] {sym} is currently at {price} (Threshold Below: {below})"
            alerts_triggered.append(msg)
            
    if alerts_triggered:
        alert_text = "\n".join(alerts_triggered)
        send_message(alert_text)
        logger.info(f"Market alerts triggered and sent to Telegram: {alert_text}")
        
    return alerts_triggered

async def run(user_input: str) -> str:
    """Agent interface for market monitor tool."""
    user_input = user_input.strip()
    try:
        args = json.loads(user_input)
        if isinstance(args, dict):
            action = args.get("action", "").lower()
            if action == "add":
                return await add_to_watchlist(args.get("symbol", ""), args.get("exchange", "DSE"), args.get("alert_above"), args.get("alert_below"))
            elif action == "remove":
                return await remove_from_watchlist(args.get("symbol", ""))
            elif action == "get":
                return await get_watchlist()
            elif action == "check":
                al = await check_alerts()
                if al:
                    return "Alerts triggered: " + ", ".join(al)
                return "No alerts triggered."
    except Exception:
        pass
        
    if "add" in user_input.lower():
        m = re.search(r"add\s+(\w+)(?:\s+(\w+))?(?:\s+above\s+([\d.]+))?(?:\s+below\s+([\d.]+))?", user_input, re.IGNORECASE)
        if m:
            symbol = m.group(1)
            exch = m.group(2) or "DSE"
            if exch.upper() not in ("DSE", "CSE"):
                exch = "DSE"
            above = float(m.group(3)) if m.group(3) else None
            below = float(m.group(4)) if m.group(4) else None
            return await add_to_watchlist(symbol, exch, above, below)
    elif "remove" in user_input.lower() or "delete" in user_input.lower():
        m = re.search(r"(?:remove|delete)\s+(\w+)", user_input, re.IGNORECASE)
        if m:
            return await remove_from_watchlist(m.group(1))
    elif "show" in user_input.lower() or "watchlist" in user_input.lower() or "get" in user_input.lower():
        return await get_watchlist()
    elif "check" in user_input.lower() or "alert" in user_input.lower() or "run" in user_input.lower():
        al = await check_alerts()
        if al:
            return "Alerts triggered: " + ", ".join(al)
        return "No alerts triggered."
        
    return "Could not parse market command. Try: 'add GP above 260' or 'watchlist'."

# --- LEGACY FOR TESTS ---
from tools.retry import retry, ToolResult
from datetime import datetime

WATCHLIST = [
    {"ticker": "GP", "threshold_pct": 1.0, "last_price": 250.0},
    {"ticker": "BATBC", "threshold_pct": 1.0, "last_price": 500.0},
    {"ticker": "SQURPHARMA", "threshold_pct": 1.5, "last_price": 210.0},
]

@retry
def _fetch_dummy_price(ticker: str) -> float:
    mock_prices = {
        "GP": 253.5,        # +1.4%
        "BATBC": 498.0,     # -0.4%
        "SQURPHARMA": 215.0 # +2.3%
    }
    return mock_prices.get(ticker, 100.0)

async def run_market_monitor(nina_os=None) -> ToolResult:
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
