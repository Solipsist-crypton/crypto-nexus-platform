# backend/app/exchanges/okx_client.py
import aiohttp
import asyncio
from typing import Dict, Optional
from datetime import datetime

class OKXClient:
    """Клієнт для OKX API"""
    
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=10)
        
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з OKX"""
        try:
            # OKX використовує формат BTC-USDT
            session = await self._get_session()
            
            # Ендпоінт для ticker
            url = f"{self.base_url}/api/v5/market/ticker"
            params = {"instId": symbol}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("code") == "0" and len(data.get("data", [])) > 0:
                        ticker = data["data"][0]
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
            print(f"OKX API error for {symbol}: {e}")
        
        return None
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()