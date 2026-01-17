import aiohttp
from typing import Dict, Optional
from datetime import datetime

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