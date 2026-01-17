# backend/app/exchanges/bybit_client.py
import aiohttp
import asyncio
from typing import Dict, Optional
from datetime import datetime

class BybitClient:
    """Клієнт для Bybit API (спот торгівля)"""
    
    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=10)
        
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з Bybit"""
        try:
            # Bybit використовує формат BTCUSDT
            session = await self._get_session()
            
            # Для спот-торгівлі
            url = f"{self.base_url}/v5/market/tickers"
            params = {"category": "spot", "symbol": symbol}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("retCode") == 0 and len(data.get("result", {}).get("list", [])) > 0:
                        ticker = data["result"]["list"][0]
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
            print(f"Bybit API error for {symbol}: {e}")
        
        return None
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()