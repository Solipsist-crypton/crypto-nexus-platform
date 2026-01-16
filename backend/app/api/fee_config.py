from fastapi import APIRouter
from app.config.fees_config import set_fee_mode, update_fee, get_trading_fee, FEE_MODE

router = APIRouter(prefix="/api/fees", tags=["fees-config"])

@router.get("/mode")
async def get_current_fee_mode():
    """Отримати поточний режим комісій"""
    return {
        "success": True,
        "mode": FEE_MODE,
        "message": f"Поточний режим комісій: {FEE_MODE}"
    }

@router.post("/mode/{mode}")
async def change_fee_mode(mode: str):
    """Змінити режим комісій"""
    set_fee_mode(mode)
    return {
        "success": True,
        "new_mode": FEE_MODE,
        "message": f"Режим комісій змінено на: {FEE_MODE}"
    }

@router.post("/update/{exchange}")
async def update_exchange_fee(exchange: str, maker: float = None, taker: float = None):
    """Оновити комісії для біржі"""
    update_fee(exchange, maker, taker)
    return {
        "success": True,
        "exchange": exchange,
        "maker": maker,
        "taker": taker,
        "message": f"Комісії для {exchange} оновлено"
    }