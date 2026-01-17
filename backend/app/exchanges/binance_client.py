from fastapi import APIRouter
import aiohttp
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class BinanceClient:
    async def get_price(self, symbol: str):
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return {
                        'price': float(data['price']),
                        'exchange': 'Binance',
                        'symbol': symbol
                    }
        except Exception as e:
            logger.error(f"Binance API error: {e}")
            return None

client = BinanceClient()

@router.get("/price/{symbol}")
async def get_price(symbol: str):
    price_data = await client.get_price(symbol)
    if price_data:
        return {"success": True, "data": price_data, "message": f"Ціна {symbol} отримана"}
    else:
        return {"success": False, "data": None, "message": "Не вдалося отримати ціну"}