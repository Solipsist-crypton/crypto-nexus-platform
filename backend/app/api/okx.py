from fastapi import APIRouter, HTTPException
import aiohttp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)
router = APIRouter()


class OKXClient:
    def __init__(self):
        self.base_url = "https://www.okx.com/api/v5"

    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з OKX"""
        try:
            url = f"{self.base_url}/market/ticker?instId={symbol}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('code') != '0':
                            logger.error(f"OKX API error: {data.get('msg')}")
                            return None
                        
                        result = data.get('data', [])
                        if not result:
                            return None
                        
                        ticker = result[0]
                        return {
                            'price': float(ticker.get('last', 0)),
                            'exchange': 'OKX',
                            'symbol': symbol,
                            'bid': float(ticker.get('bidPx', 0)),
                            'ask': float(ticker.get('askPx', 0)),
                            'volume': float(ticker.get('vol24h', 0)),
                            'timestamp': ticker.get('ts', '')
                        }
                    return None
        except Exception as e:
            logger.error(f"Error fetching price from OKX: {e}")
            return None


client = OKXClient()


@router.get("/health")
async def health_check():
    try:
        price = await client.get_price("BTC-USDT")
        return {
            "status": "healthy" if price else "unhealthy",
            "exchange": "OKX"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    price_data = await client.get_price(symbol)
    if not price_data:
        raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
    
    return {
        "success": True,
        "data": price_data,
        "message": f"Ціна {symbol} отримана з OKX"
    }