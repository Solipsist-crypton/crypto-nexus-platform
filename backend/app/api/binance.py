from fastapi import APIRouter
import aiohttp
from typing import Dict, Optional, List
from datetime import datetime
import asyncio

# Власний клієнт всередині API модуля
class BinanceClient:
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.session = None
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з Binance"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {"symbol": symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "price": float(data["price"]),
                        "exchange": "Binance",
                        "symbol": symbol,
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            print(f"Binance error: {e}")
        return None
    
    async def get_prices(self, symbols: List[str]) -> List[Optional[Dict]]:
        """Отримати ціни для списку монет"""
        tasks = [self.get_price(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)

# FastAPI роутер
router = APIRouter(prefix="/api/binance", tags=["binance"])
client = BinanceClient()

@router.get("/price/{symbol}")
async def get_binance_price(symbol: str = "BTCUSDT"):
    """Отримати ціну з Binance"""
    price_data = await client.get_price(symbol)
    if price_data:
        return {
            "success": True,
            "data": price_data,
            "message": f"Ціна {symbol} з Binance"
        }
    return {
        "success": False,
        "message": "Не вдалося отримати ціну"
    }

@router.get("/prices")
async def get_binance_prices():
    """Отримати ціни для топ-3 монет"""
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    prices = await client.get_prices(symbols)
    return {
        "success": True,
        "data": prices,
        "message": "Ціни з Binance"
    }