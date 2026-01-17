from fastapi import APIRouter
import aiohttp
import asyncio
from typing import Dict, Optional, List
from datetime import datetime

# Власний клієнт всередині API модуля
class KrakenClient:
    def __init__(self):
        self.base_url = "https://api.kraken.com"
        self.session = None
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з Kraken"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = f"{self.base_url}/0/public/Ticker"
            params = {"pair": symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("error") == []:
                        result = data.get("result", {})
                        if result:
                            # Беремо перший ключ (напр. XXBTZUSD)
                            first_key = list(result.keys())[0]
                            ticker = result[first_key]
                            price = float(ticker.get('c', [0])[0])
                            
                            return {
                                "price": price,
                                "exchange": "Kraken",
                                "symbol": symbol,
                                "timestamp": datetime.utcnow().isoformat()
                            }
        except Exception as e:
            print(f"Kraken error for {symbol}: {e}")
        return None
    
    async def get_prices(self, symbols: List[str]) -> List[Optional[Dict]]:
        """Отримати ціни для списку монет"""
        tasks = [self.get_price(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)

# FastAPI роутер
router = APIRouter(prefix="/api/kraken", tags=["kraken"])
client = KrakenClient()

@router.get("/price/{symbol}")
async def get_kraken_price(symbol: str = "XXBTZUSD"):
    """Отримати ціну з Kraken"""
    price_data = await client.get_price(symbol)
    if price_data:
        return {
            "success": True,
            "data": price_data,
            "message": f"Ціна {symbol} з Kraken"
        }
    return {
        "success": False,
        "message": "Не вдалося отримати ціну"
    }

@router.get("/prices")
async def get_kraken_prices():
    """Отримати ціни для топ-3 монет"""
    symbols = ["XXBTZUSD", "XETHZUSD", "SOLUSD"]
    prices = await client.get_prices(symbols)
    return {
        "success": True,
        "data": prices,
        "message": "Ціни з Kraken"
    }