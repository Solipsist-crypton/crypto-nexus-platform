from fastapi import APIRouter
from datetime import datetime

from sqlalchemy import func
from app.futures.services.explanation_builder import explanation_builder
from typing import List, Optional
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.futures.models import Signal, VirtualTrade
import random


router = APIRouter(tags=["futures"])  # БЕЗ prefix тут

@router.get("/health")
def health_check():
    """Проста перевірка роботи модуля ф'ючерсів"""
    return {
        "module": "futures_signals",
        "status": "active",
        "version": "0.0.1",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/test")
def test_endpoint():
    """Тестовий ендпоінт"""
    return {
        "message": "Futures module is working",
        "test_data": {
            "signal": "BTCUSDT LONG",
            "confidence": 0.75,
            "timestamp": datetime.now().isoformat()
        }
    }
@router.post("/signals/generate")
def generate_signal():
    """Згенерувати тестовий AI-сигнал з поясненням"""
    # Симулюємо AI-фактори
    factors = {
        "trend_strength": round(random.uniform(0.5, 0.9), 2),
        "volume_confirmation": round(random.uniform(0.4, 0.8), 2),
        "support_resistance": round(random.uniform(0.6, 0.95), 2),
        "volatility": round(random.uniform(0.3, 0.7), 2),
        "momentum": round(random.uniform(0.5, 0.85), 2),
        "market_sentiment": round(random.uniform(0.4, 0.8), 2)
    }
    
    confidence = round(random.uniform(0.6, 0.95), 2)
    direction = random.choice(["long", "short"])
    
    # Генеруємо пояснення
    explanation = explanation_builder.build_explanation(
        symbol="BTCUSDT",
        direction=direction,
        confidence=confidence,
        factors=factors
    )
    
    return {
        "status": "success",
        "signal": {
            "symbol": "BTCUSDT",
            "direction": direction,
            "confidence": confidence,
            "explanation": explanation,
            "factors": factors,
            "entry_price": round(42000 + random.uniform(-1000, 1000), 2),
            "take_profit": round(44000 + random.uniform(-2000, 2000), 2),
            "stop_loss": round(41000 + random.uniform(-2000, 2000), 2),
            "timestamp": datetime.now().isoformat()
        },
        "module": "futures_v1"
    }

@router.get("/explain")
def explain_signal(
    symbol: str = "BTCUSDT",
    direction: str = "long",
    confidence: float = 0.75
):
    """Отримати текстове пояснення для сигналу"""
    explanation = explanation_builder.build_explanation(
        symbol=symbol,
        direction=direction,
        confidence=confidence
    )
    
    return {
        "symbol": symbol,
        "direction": direction,
        "confidence": confidence,
        "explanation": explanation,
        "timestamp": datetime.now().isoformat()
    }
@router.post("/virtual-trades", response_model=dict)
def create_virtual_trade(
    signal_id: int,
    entry_price: float,
    take_profit: float,
    stop_loss: float,
    db: Session = Depends(get_db)
):
    """
    Створити віртуальну угоду для тестування сигналу
    
    Args:
        signal_id: ID сигналу з БД
        entry_price: Ціна входу
        take_profit: Ціна take profit
        stop_loss: Ціна stop loss
    """
    # Перевіряємо чи існує сигнал
    signal = db.query(Signal).filter(Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    # Створюємо віртуальну угоду
    virtual_trade = VirtualTrade(
        signal_id=signal_id,
        entry_price=entry_price,
        take_profit=take_profit,
        stop_loss=stop_loss,
        current_price=entry_price,  # Початкова ціна = ціна входу
        status="active"
    )
    
    db.add(virtual_trade)
    db.commit()
    db.refresh(virtual_trade)
    
    return {
        "status": "success",
        "message": "Virtual trade created",
        "trade": virtual_trade.to_dict()
    }

@router.get("/virtual-trades", response_model=dict)
def get_virtual_trades(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Отримати список віртуальних угод"""
    query = db.query(VirtualTrade)
    
    if status:
        query = query.filter(VirtualTrade.status == status)
    
    trades = query.order_by(VirtualTrade.created_at.desc()).limit(limit).all()
    
    return {
        "status": "success",
        "count": len(trades),
        "trades": [trade.to_dict() for trade in trades]
    }

@router.get("/virtual-trades/{trade_id}", response_model=dict)
def get_virtual_trade(
    trade_id: int,
    db: Session = Depends(get_db)
):
    """Отримати деталі віртуальної угоди"""
    trade = db.query(VirtualTrade).filter(VirtualTrade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Virtual trade not found")
    
    return {
        "status": "success",
        "trade": trade.to_dict()
    }

@router.post("/virtual-trades/{trade_id}/update-price", response_model=dict)
def update_trade_price(
    trade_id: int,
    current_price: float,
    db: Session = Depends(get_db)
):
    """Оновити поточну ціну для віртуальної угоди"""
    trade = db.query(VirtualTrade).filter(VirtualTrade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Virtual trade not found")
    
    if trade.status != "active":
        raise HTTPException(status_code=400, detail=f"Trade is {trade.status}, cannot update")
    
    # Оновлюємо ціну та розраховуємо PnL
    old_status = trade.status
    trade.calculate_pnl(current_price)
    
    # Якщо статус змінився (досягнуто TP/SL), встановлюємо closed_at
    if trade.status != old_status and trade.status in ["tp_hit", "sl_hit"]:
        trade.closed_at = func.now()
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"Price updated to {current_price}",
        "trade": trade.to_dict(),
        "pnl_update": {
            "old_status": old_status,
            "new_status": trade.status,
            "pnl_percentage": round(trade.pnl_percentage, 2),
            "pnl_amount": round(trade.pnl_amount, 2)
        }
    }

@router.delete("/virtual-trades/{trade_id}", response_model=dict)
def delete_virtual_trade(
    trade_id: int,
    db: Session = Depends(get_db)
):
    """Видалити віртуальну угоду"""
    trade = db.query(VirtualTrade).filter(VirtualTrade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Virtual trade not found")
    
    db.delete(trade)
    db.commit()
    
    return {
        "status": "success",
        "message": "Virtual trade deleted"
    }