import aiohttp
from typing import Dict, Optional
from datetime import datetime

from fastapi import APIRouter

class CoinbaseClient:
    """Клієнт для Coinbase API"""
    
    def __init__(self):
        self.base_url = "https://api.exchange.coinbase.com"
        self.session = None
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з Coinbase"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.base_url}/products/{symbol}/ticker"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "price": float(data.get("price", 0)),
                        "exchange": "Coinbase",
                        "symbol": symbol,
                        "bid": float(data.get("bid", 0)),
                        "ask": float(data.get("ask", 0)),
                        "volume": float(data.get("volume", 0)),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            print(f"Coinbase error for {symbol}: {e}")
        return None
    
    async def get_prices(self, symbols: list) -> list:
        """Отримати ціни для списку монет"""
        import asyncio
        tasks = [self.get_price(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)

# --- FastAPI Router для Coinbase ---
router = APIRouter(prefix="/api/coinbase", tags=["coinbase"])
client = CoinbaseClient()

@router.get("/price/{symbol}")
async def get_coinbase_price(symbol: str):
    """
    Отримати ціну однієї монети з Coinbase.
    Приклад символу: BTC-USD, ETH-USD, SOL-USD
    """
    price_data = await client.get_price(symbol)
    if price_data:
        return {
            "success": True,
            "data": price_data,
            "message": f"Ціна {symbol} з Coinbase"
        }
    return {
        "success": False,
        "message": f"Не вдалося отримати ціну {symbol} з Coinbase"
    }

@router.get("/prices")
async def get_coinbase_prices(symbols: str = "BTC-USD,ETH-USD,SOL-USD"):
    """
    Отримати ціни для списку монет з Coinbase.
    Параметр (опційний): symbols - рядок, розділений комами.
    """
    symbol_list = [s.strip() for s in symbols.split(",")]
    prices = await client.get_prices(symbol_list)
    
    return {
        "success": True,
        "data": prices,
        "message": "Ціни з Coinbase",
        "requested_symbols": symbol_list
    }    