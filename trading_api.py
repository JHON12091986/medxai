import json
from fastapi import FastAPI, HTTPException
from typing import Optional
from datetime import datetime
import uvicorn

# ================= CONFIGURACIÓN =================
app = FastAPI(
    title="Bybit Trading Signals API - Tiburón Supremo",
    version="1.0.0"
)

# ================= CARGAR DATOS =================
with open("data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

# ================= ENDPOINTS =================

@app.get("/")
async def root():
    return {
        "service": "Bybit Trading Signals API - Tiburón Supremo",
        "endpoints": {
            "/status": "Estado del sistema",
            "/signals": "Todas las señales",
            "/signals/{symbol}": "Señal de un símbolo",
            "/history": "Historial de trades",
            "/equity-history": "Historial de equity",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health():
    return {"status": "alive", "timestamp": datetime.now().isoformat()}

@app.get("/status")
async def status():
    return {
        "status": DATA.get("status"),
        "equity": DATA.get("equity"),
        "total_pnl": DATA.get("total_pnl"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/signals")
async def signals():
    return DATA.get("signals", {})

@app.get("/signals/{symbol}")
async def signal(symbol: str):
    sig = DATA.get("signals", {}).get(symbol)
    if not sig:
        raise HTTPException(404, f"Symbol '{symbol}' not found")
    return {symbol: sig}

@app.get("/history")
async def history(limit: Optional[int] = 20):
    hist = DATA.get("trade_history", [])
    return hist[-limit:] if limit else hist

@app.get("/equity-history")
async def equity_history(limit: Optional[int] = None):
    hist = DATA.get("equity_hist", [])
    return hist[-limit:] if limit else hist

# ================= EJECUCIÓN =================
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)