import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CoinGeckoClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.coingecko.com/api/v3"):
        self.base_url = base_url
        self.api_key = api_key
        self.session = None
        self.rate_limit = 30  # запитів на хвилину
        self.last_request_time = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Базовий метод для запитів з rate limiting"""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.rate_limit
        
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                self.last_request_time = time.time()
                
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Rate limit exceeded, waiting 60 seconds")
                    await asyncio.sleep(60)
                    return await self._make_request(endpoint, params)
                else:
                    logger.error(f"API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    async def get_top_coins(self, limit: int = 100) -> List[Dict]:
        """Отримати топ криптовалют за market cap"""
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false"
        }
        
        data = await self._make_request("coins/markets", params)
        return data if data else []
    
    async def get_coin_tickers(self, coin_id: str) -> Optional[Dict]:
        """Отримати ціни монети на всіх біржах"""
        params = {
            "include_exchange_logo": "false",
            "depth": "false"
        }
        
        data = await self._make_request(f"coins/{coin_id}/tickers", params)
        return data
    
    async def get_coin_history(self, coin_id: str, days: int = 7) -> Optional[Dict]:
        """Отримати історію цін монети"""
        params = {
            "vs_currency": "usd",
            "days": days
        }
        
        data = await self._make_request(f"coins/{coin_id}/market_chart", params)
        return data
    
    async def get_exchanges(self) -> List[Dict]:
        """Отримати список всіх бірж"""
        data = await self._make_request("exchanges")
        return data if data else []