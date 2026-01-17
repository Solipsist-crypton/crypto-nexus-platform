from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..models.arbitrage import ArbitrageOpportunity as ArbitrageModel

# Схеми Pydantic (без імпорту з schemas для уникнення циклічності)
class ArbitrageOpportunityBase(BaseModel):
    base_currency: str
    target_currency: str
    exchange_from: str
    exchange_to: str
    price_from: float
    price_to: float
    price_difference: float
    volume_24h: Optional[float] = None
    trust_score: Optional[float] = None
    potential_profit: Optional[float] = None
    is_opportunity: bool = True

class ArbitrageOpportunityCreate(ArbitrageOpportunityBase):
    pass

class ArbitrageOpportunityResponse(ArbitrageOpportunityBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

router = APIRouter(prefix="/api/arbitrage", tags=["arbitrage"])

@router.get("/opportunities", response_model=List[ArbitrageOpportunityResponse])
def get_opportunities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    min_profit: Optional[float] = Query(1.0, description="Мінімальний прибуток у %"),
    base_currency: Optional[str] = None
):
    """
    Отримати список арбітражних можливостей
    """
    query = db.query(ArbitrageModel).filter(
        ArbitrageModel.price_difference >= min_profit,
        ArbitrageModel.is_opportunity == True
    )
    
    if base_currency:
        query = query.filter(ArbitrageModel.base_currency == base_currency)
    
    return query.offset(skip).limit(limit).all()

@router.post("/opportunities", response_model=ArbitrageOpportunityResponse)
def create_opportunity(
    opportunity: ArbitrageOpportunityCreate,
    db: Session = Depends(get_db)
):
    """
    Додати нову арбітражну можливість
    """
    db_opportunity = ArbitrageModel(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

@router.get("/opportunities/{id}", response_model=ArbitrageOpportunityResponse)
def get_opportunity(id: int, db: Session = Depends(get_db)):
    """
    Отримати конкретну арбітражну можливість за ID
    """
    opportunity = db.query(ArbitrageModel).filter(ArbitrageModel.id == id).first()
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@router.get("/calculate/{coin}/{buy_exchange}/{sell_exchange}/{amount}")
async def calculate_specific_arbitrage(
    coin: str,
    buy_exchange: str,
    sell_exchange: str,
    amount: float = 1.0
):
    """
    Детальний розрахунок арбітражу для конкретної пари бірж
    """
    try:
        from app.services.arbitrage_calculator import ArbitrageCalculator
        
        calculator = ArbitrageCalculator()
        
        # Перевірка вхідних даних
        if coin.upper() not in calculator.supported_coins:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Монета {coin} не підтримується. Доступні: {calculator.supported_coins}"
                }
            )
        
        if buy_exchange not in calculator.supported_exchanges:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Біржа {buy_exchange} не підтримується. Доступні: {calculator.supported_exchanges}"
                }
            )
        
        if sell_exchange not in calculator.supported_exchanges:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Біржа {sell_exchange} не підтримується. Доступні: {calculator.supported_exchanges}"
                }
            )
        
        # Отримати ціни
        print(f"[DEBUG] Отримання цін для {coin}...")
        prices = await calculator._fetch_all_prices(coin.upper())
        print(f"[DEBUG] Отримані ціни: {prices}")
        
        if not prices.get(buy_exchange) or not prices.get(sell_exchange):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Не вдалося отримати ціни. Buy price: {prices.get(buy_exchange)}, Sell price: {prices.get(sell_exchange)}"
                }
            )
        
        # Розрахувати арбітраж
        print(f"[DEBUG] Розрахунок арбітражу {buy_exchange} -> {sell_exchange}...")
        result = await calculator.calculate_arbitrage(
            coin=coin.upper(),
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            buy_price=prices[buy_exchange],
            sell_price=prices[sell_exchange],
            amount=amount
        )
        
        return {
            "success": True,
            "data": result,
            "debug": {
                "prices_used": {
                    buy_exchange: prices[buy_exchange],
                    sell_exchange: prices[sell_exchange]
                },
                "symbols_used": {
                    buy_exchange: calculator.symbol_map[coin.upper()][buy_exchange],
                    sell_exchange: calculator.symbol_map[coin.upper()][sell_exchange]
                }
            }
        }
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Помилка в calculate: {e}")
        print(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()[:500]  # Обмежуємо для безпеки
            }
        )