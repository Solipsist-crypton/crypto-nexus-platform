from fastapi import APIRouter, HTTPException
import aiohttp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)
router = APIRouter()


class BybitClient:
    def __init__(self):
        self.base_url = "https://api.bybit.com/v5/market"

    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з Bybit"""
        try:
            url = f"{self.base_url}/tickers?category=spot&symbol={symbol}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get('result', {})
                        list_data = result.get('list', [])
                        
                        if not list_data:
                            return None
                        
                        ticker = list_data[0]
                        return {
                            'price': float(ticker.get('lastPrice', 0)),
                            'exchange': 'Bybit',
                            'symbol': symbol,
                            'bid': float(ticker.get('bid1Price', 0)),
                            'ask': float(ticker.get('ask1Price', 0)),
                            'volume': float(ticker.get('volume24h', 0)),
                            'timestamp': ticker.get('time', '')
                        }
                    return None
        except Exception as e:
            logger.error(f"Error fetching price from Bybit: {e}")
            return None


client = BybitClient()


@router.get("/health")
async def health_check():
    try:
        price = await client.get_price("BTCUSDT")
        return {
            "status": "healthy" if price else "unhealthy",
            "exchange": "Bybit"
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
        "message": f"Ціна {symbol} отримана з Bybit"
    }