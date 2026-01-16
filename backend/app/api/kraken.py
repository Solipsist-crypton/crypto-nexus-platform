from fastapi import APIRouter
from app.exchanges.kraken_client import KrakenClient

router = APIRouter(prefix="/api/kraken", tags=["kraken"])
client = KrakenClient()

@router.get("/price/{pair}")
async def get_kraken_price(pair: str = "XXBTZUSD"):
    """Отримати ціну з Kraken"""
    price_data = await client.get_price(pair)
    if price_data:
        return {
            "success": True,
            "data": price_data,
            "message": f"Ціна {pair} з Kraken"
        }
    return {
        "success": False,
        "message": "Не вдалося отримати ціну з Kraken"
    }

@router.get("/prices")
async def get_kraken_prices():
    """Отримати ціни для топ-3 монет"""
    prices = await client.get_prices()
    return {
        "success": True,
        "data": prices,
        "message": "Ціни з Kraken"
    }