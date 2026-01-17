from fastapi import APIRouter, HTTPException
import aiohttp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)
router = APIRouter()


class KrakenClient:
    def __init__(self):
        self.base_url = "https://api.kraken.com/0/public"

    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з Kraken"""
        try:
            url = f"{self.base_url}/Ticker?pair={symbol}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('error'):
                            logger.error(f"Kraken API error: {data['error']}")
                            return None
                        
                        # Kraken повертає дані з ключем result, де ключ - це символ
                        result = data.get('result', {})
                        if not result:
                            return None
                        
                        # Беремо перший символ з результату
                        first_key = list(result.keys())[0]
                        ticker_data = result[first_key]
                        
                        # Беремо ціну закриття (c[0])
                        price = float(ticker_data.get('c', [0])[0])
                        
                        return {
                            'price': price,
                            'exchange': 'Kraken',
                            'symbol': symbol,
                            'bid': float(ticker_data.get('b', [0])[0]),
                            'ask': float(ticker_data.get('a', [0])[0]),
                            'volume': float(ticker_data.get('v', [0])[0]),
                            'timestamp': data.get('timestamp', '')
                        }
                    return None
        except Exception as e:
            logger.error(f"Error fetching price from Kraken: {e}")
            return None


client = KrakenClient()


@router.get("/health")
async def health_check():
    try:
        price = await client.get_price("XXBTZUSD")
        return {
            "status": "healthy" if price else "unhealthy",
            "exchange": "Kraken"
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
        "message": f"Ціна {symbol} отримана з Kraken"
    }