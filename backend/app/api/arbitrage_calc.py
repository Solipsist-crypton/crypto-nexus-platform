from fastapi import APIRouter
from app.services.arbitrage_calculator import ArbitrageCalculator

router = APIRouter(prefix="/api/arbitrage", tags=["arbitrage-calc"])
calculator = ArbitrageCalculator()

@router.get("/compare/{coin}")
async def compare_coin_prices(coin: str = "BTC"):
    """
    Порівняти ціни на Binance та Kraken для конкретної монети
    """
    result = await calculator.compare_prices(coin.upper())
    return {
        "success": "error" not in result,
        "data": result,
        "message": f"Порівняння цін {coin}" if "error" not in result else result["error"]
    }

@router.get("/scan")
async def scan_all_opportunities():
    """
    Сканувати всі доступні арбітражні можливості
    """
    opportunities = await calculator.scan_all_coins()
    return {
        "success": True,
        "data": opportunities,
        "count": len(opportunities),
        "message": f"Знайдено {len(opportunities)} арбітражних можливостей"
    }

@router.get("/best")
async def get_best_opportunity():
    """
    Отримати найкращу арбітражну можливість
    """
    best = await calculator.find_best_opportunity()
    return {
        "success": best is not None,
        "data": best,
        "message": "Найкраща арбітражна можливість" if best else "Можливостей не знайдено"
    }