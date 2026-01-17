from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
import logging
from app.services.arbitrage_calculator import ArbitrageCalculator
from app.models.response import ArbitrageResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/compare/{coin}", response_model=ArbitrageResponse)
async def compare_coin_prices(
    coin: str,
    threshold: float = Query(0.1, description="Мінімальна різниця в процентах")
):
    """
    Порівняти ціни на монету на різних біржах
    """
    try:
        logger.info(f"🔍 Порівняння цін для {coin} з порогом {threshold}%")
        
        calculator = ArbitrageCalculator(threshold=threshold)
        result = await calculator.calculate_arbitrage_for_coin(coin)
        
        if not result:
            return ArbitrageResponse(
                success=True,
                data={"coin": coin, "prices": {}, "best_opportunity": None, "all_opportunities": []},
                count=0,
                message=f"Не знайдено арбітражних можливостей для {coin} з різницею вище {threshold}%"
            )
        
        return ArbitrageResponse(
            success=True,
            data=result,
            count=1,
            message=f"Знайдено арбітражні можливості для {coin}"
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка при порівнянні цін для {coin}: {e}")
        return ArbitrageResponse(
            success=False,
            data={},
            count=0,
            message=f"Помилка сервера: {str(e)}"
        )


@router.get("/calculate/{coin}/{buy_exchange}/{sell_exchange}/{amount}", response_model=ArbitrageResponse)
async def calculate_specific_arbitrage(
    coin: str,
    buy_exchange: str,
    sell_exchange: str,
    amount: float = 1.0
):
    """
    Розрахувати конкретну арбітражну операцію
    """
    try:
        logger.info(f"🧮 Розрахунок арбітражу: {coin} {buy_exchange} → {sell_exchange} ({amount})")
        
        calculator = ArbitrageCalculator()
        result = await calculator.calculate_specific_arbitrage(coin, buy_exchange, sell_exchange, amount)
        
        return ArbitrageResponse(
            success=result.get('success', False),
            data=result,
            count=1 if result.get('success') else 0,
            message=result.get('message', 'Розрахунок завершено')
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка при розрахунку арбітражу: {e}")
        return ArbitrageResponse(
            success=False,
            data={},
            count=0,
            message=f"Помилка сервера: {str(e)}"
        )


@router.get("/scan", response_model=ArbitrageResponse)
async def scan_all_coins(
    threshold: float = Query(0.1, description="Мінімальна різниця в процентах"),
    max_coins: int = Query(10, description="Максимальна кількість монет для сканування")
):
    """
    Сканувати всі монети для пошуку арбітражних можливостей
    """
    try:
        logger.info(f"🔄 Сканування всіх монет з порогом {threshold}%")
        
        calculator = ArbitrageCalculator(threshold=threshold)
        opportunities = await calculator.calculate_arbitrage_all_coins()
        
        valid_opportunities = [opp for opp in opportunities if opp and opp.get("best_opportunity")]
        
        return ArbitrageResponse(
            success=True,
            data={
                "opportunities": valid_opportunities,
                "total_scanned": len(opportunities),
                "found_opportunities": len(valid_opportunities),
                "threshold": threshold
            },
            count=len(valid_opportunities),
            message=f"Знайдено {len(valid_opportunities)} арбітражних можливостей з {len(opportunities)} сканованих монет"
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка при скануванні: {e}")
        return ArbitrageResponse(
            success=False,
            data={},
            count=0,
            message=f"Помилка сканування: {str(e)}"
        )


@router.get("/best", response_model=ArbitrageResponse)
async def get_best_opportunity(
    threshold: float = Query(0.1, description="Мінімальна різниця в процентах")
):
    """
    Отримати найкращу арбітражну можливість серед усіх монет
    """
    try:
        logger.info(f"🚀 Запит найкращої можливості з порогом {threshold}%")

        calculator = ArbitrageCalculator(threshold=threshold)
        best_opportunity = await calculator.find_best_opportunity()

        if not best_opportunity:
            return ArbitrageResponse(
                success=True,
                data={},
                count=0,
                message=f"Не знайдено арбітражних можливостей з різницею вище {threshold}%."
            )

        return ArbitrageResponse(
            success=True,
            data=best_opportunity,
            count=1,
            message="Найкраща арбітражна можливість знайдена."
        )

    except Exception as e:
        logger.error(f"❌ Помилка в ендпоїнті /best: {e}")
        return ArbitrageResponse(
            success=False,
            data={},
            count=0,
            message=f"Внутрішня помилка сервера: {str(e)}"
        )