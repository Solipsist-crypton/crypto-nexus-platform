import aiohttp
from typing import Dict, Optional
from datetime import datetime

from fastapi import APIRouter

class OKXClient:
    """Клієнт для OKX API"""
    
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.session = None
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з OKX"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.base_url}/api/v5/market/ticker"
            params = {"instId": symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == "0" and data.get("data"):
                        tickers = data["data"]
                        if len(tickers) > 0:
                            ticker = tickers[0]
                            return {
                                "price": float(ticker.get("last", 0)),
                                "exchange": "OKX",
                                "symbol": symbol,
                                "bid": float(ticker.get("bidPx", 0)),
                                "ask": float(ticker.get("askPx", 0)),
                                "volume": float(ticker.get("vol24h", 0)),
                                "timestamp": datetime.utcnow().isoformat()
                            }
        except Exception as e:
            print(f"OKX error for {symbol}: {e}")
        return None
    
    async def get_prices(self, symbols: list) -> list:
        """Отримати ціни для списку монет"""
        import asyncio
        tasks = [self.get_price(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)
# --- FastAPI Router для OKX ---
router = APIRouter(prefix="/api/okx", tags=["okx"])
client = OKXClient()

@router.get("/price/{symbol}")
async def get_okx_price(symbol: str):
    """
    Отримати ціну однієї монети з OKX.
    Приклад символу: BTC-USDT, ETH-USDT, SOL-USDT
    """
    price_data = await client.get_price(symbol)
    if price_data:
        return {
            "success": True,
            "data": price_data,
            "message": f"Ціна {symbol} з OKX"
        }
    return {
        "success": False,
        "message": f"Не вдалося отримати ціну {symbol} з OKX"
    }

@router.get("/prices")
async def get_okx_prices(symbols: str = "BTC-USDT,ETH-USDT,SOL-USDT"):
    """
    Отримати ціни для списку монет з OKX.
    Параметр (опційний): symbols - рядок, розділений комами.
    """
    symbol_list = [s.strip() for s in symbols.split(",")]
    prices = await client.get_prices(symbol_list)
    
    return {
        "success": True,
        "data": prices,
        "message": "Ціни з OKX",
        "requested_symbols": symbol_list
    }