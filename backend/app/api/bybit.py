import aiohttp
from typing import Dict, Optional
from datetime import datetime

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