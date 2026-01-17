import aiohttp
from typing import Dict, Optional
from datetime import datetime

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