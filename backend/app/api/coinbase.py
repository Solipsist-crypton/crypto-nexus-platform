from fastapi import APIRouter, HTTPException
import aiohttp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)
router = APIRouter()


class CoinbaseClient:
    def __init__(self):
        self.base_url = "https://api.pro.coinbase.com"

    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Отримати ціну з Coinbase"""
        try:
            url = f"{self.base_url}/products/{symbol}/ticker"
            logger.info(f"Coinbase API call: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    logger.info(f"Coinbase response status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Coinbase data: {data}")
                        # Перевіряємо, чи є ціна у відповіді
                        price_str = data.get('price')
                        if not price_str:
                            logger.error("Coinbase: No price in response")
                            return None
                        try:
                            price = float(price_str)
                            return {
                                'price': price,
                                'exchange': 'Coinbase',
                                'symbol': symbol,
                                'bid': float(data.get('bid', 0)),
                                'ask': float(data.get('ask', 0)),
                                'volume': float(data.get('volume', 0)),
                                'timestamp': data.get('time', '')
                            }
                        except ValueError as e:
                            logger.error(f"Coinbase: Error converting price '{price_str}' to float: {e}")
                            return None
                    else:
                        # Якщо статус не 200, читаємо текст помилки
                        error_text = await response.text()
                        logger.error(f"Coinbase API error {response.status}: {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching price from Coinbase: {e}", exc_info=True)
            return None


client = CoinbaseClient()


@router.get("/health")
async def health_check():
    try:
        price = await client.get_price("BTC-USD")
        return {
            "status": "healthy" if price else "unhealthy",
            "exchange": "Coinbase"
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
        "message": f"Ціна {symbol} отримана з Coinbase"
    }