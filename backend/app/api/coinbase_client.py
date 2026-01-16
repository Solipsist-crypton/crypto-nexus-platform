# app/exchanges/coinbase_client.py
import aiohttp
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime

class CoinbaseClient:
    """Клієнт для Coinbase Pro API"""
    
    def __init__(self):
        self.base_url = "https://api.pro.coinbase.com"
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=10)
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Отримати або створити сесію"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """
        Отримати поточну ціну з Coinbase Pro
        
        Args:
            symbol: формат "BTC-USD", "ETH-USD" тощо
        
        Returns:
            Dict з ціною та метаданими або None
        """
        try:
            # Конвертуємо символ для Coinbase API
            # BTC-USD -> BTC-USD (залишаємо як є)
            product_id = symbol
            
            session = await self._get_session()
            url = f"{self.base_url}/products/{product_id}/ticker"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Coinbase повертає ціну як рядок
                    price = float(data.get('price', 0))
                    volume = float(data.get('volume', 0))
                    
                    return {
                        "price": price,
                        "exchange": "Coinbase",
                        "symbol": symbol,
                        "volume": volume,
                        "bid": float(data.get('bid', 0)),
                        "ask": float(data.get('ask', 0)),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    print(f"Coinbase API error {response.status}: {await response.text()}")
                    
        except asyncio.TimeoutError:
            print(f"Coinbase timeout for {symbol}")
        except Exception as e:
            print(f"Coinbase error for {symbol}: {e}")
        
        return None
    
    async def get_order_book(self, symbol: str, level: int = 1) -> Optional[Dict]:
        """Отримати стакан замовлень"""
        try:
            product_id = symbol
            session = await self._get_session()
            url = f"{self.base_url}/products/{product_id}/book?level={level}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Coinbase order book error: {e}")
        return None
    
    async def close(self):
        """Закрити сесію"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Деструктор для закриття сесії"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.close())