from fastapi import APIRouter
from app.exchanges.binance_client import BinanceClient

router = APIRouter(prefix="/api/binance", tags=["binance"])
client = BinanceClient()

@router.get("/price/{symbol}")
async def get_binance_price(symbol: str = "BTCUSDT"):
    """Отримати ціну з Binance (тестовий ендпоінт)"""
    price_data = await client.get_price(symbol)
    if price_data:
        return {
            "success": True,
            "data": price_data,
            "message": f"Ціна {symbol} з Binance"
        }
    return {
        "success": False,
        "message": "Не вдалося отримати ціну"
    }

@router.get("/prices")
async def get_binance_prices():
    """Отримати ціни для топ-3 монет"""
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    prices = await client.get_prices(symbols)
    return {
        "success": True,
        "data": prices,
        "message": "Ціни з Binance"
    }