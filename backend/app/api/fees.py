from fastapi import APIRouter
from app.data.exchange_fees import REAL_EXCHANGE_FEES

router = APIRouter(prefix="/api/fees", tags=["fees"])

@router.get("/{exchange}/{coin}")
async def get_exchange_fees(exchange: str, coin: str):
    """Отримати комісії та метрики біржі"""
    fees = REAL_EXCHANGE_FEES.get(exchange, {}).get(coin, {})
    return {
        "success": bool(fees),
        "exchange": exchange,
        "coin": coin,
        "data": fees,
        "message": f"Комісії {exchange} для {coin}" if fees else "Дані не знайдено"
    }

@router.get("/compare/{coin}")
async def compare_fees(coin: str):
    """Порівняти комісії на різних біржах"""
    comparisons = []
    
    for exchange in ["Binance", "Kraken"]:
        if coin in REAL_EXCHANGE_FEES.get(exchange, {}):
            fees = REAL_EXCHANGE_FEES[exchange][coin]
            comparisons.append({
                "exchange": exchange,
                "maker_fee": fees["maker_fee"] * 100,
                "taker_fee": fees["taker_fee"] * 100,
                "withdrawal_fee": fees["withdrawal_fee"],
                "daily_volume": fees["daily_volume"],
                "spread": fees["spread"]
            })
    
    return {
        "success": True,
        "coin": coin,
        "data": comparisons,
        "message": f"Порівняння комісій для {coin}"
    }