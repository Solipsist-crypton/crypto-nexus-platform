import aiohttp
from typing import Dict, Optional
from datetime import datetime

from fastapi import APIRouter

class BybitClient:
    """Клієнт для Bybit API"""
    
    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.session = None
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з Bybit"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.base_url}/v5/market/tickers"
            params = {"category": "spot", "symbol": symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("retCode") == 0 and data.get("result"):
                        result = data["result"]
                        if "list" in result and len(result["list"]) > 0:
                            ticker = result["list"][0]
                            return {
                                "price": float(ticker.get("lastPrice", 0)),
                                "exchange": "Bybit",
                                "symbol": symbol,
                                "bid": float(ticker.get("bid1Price", 0)),
                                "ask": float(ticker.get("ask1Price", 0)),
                                "volume": float(ticker.get("volume24h", 0)),
                                "timestamp": datetime.utcnow().isoformat()
                            }
        except Exception as e:
            print(f"Bybit error for {symbol}: {e}")
        return None
    
    async def get_prices(self, symbols: list) -> list:
        """Отримати ціни для списку монет"""
        import asyncio
        tasks = [self.get_price(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)

# --- FastAPI Router для Bybit ---
router = APIRouter(prefix="/api/bybit", tags=["bybit"])
client = BybitClient()

@router.get("/price/{symbol}")
async def get_bybit_price(symbol: str):
    """
    Отримати ціну однієї монети з Bybit.
    Приклад символу: BTCUSDT, ETHUSDT, SOLUSDT
    """
    price_data = await client.get_price(symbol)
    if price_data:
        return {
            "success": True,
            "data": price_data,
            "message": f"Ціна {symbol} з Bybit"
        }
    return {
        "success": False,
        "message": f"Не вдалося отримати ціну {symbol} з Bybit"
    }

@router.get("/prices")
async def get_bybit_prices(symbols: str = "BTCUSDT,ETHUSDT,SOLUSDT"):
    """
    Отримати ціни для списку монет з Bybit.
    Параметр (опційний): symbols - рядок, розділений комами.
    """
    symbol_list = [s.strip() for s in symbols.split(",")]
    prices = await client.get_prices(symbol_list)
    
    return {
        "success": True,
        "data": prices,
        "message": "Ціни з Bybit",
        "requested_symbols": symbol_list
    }