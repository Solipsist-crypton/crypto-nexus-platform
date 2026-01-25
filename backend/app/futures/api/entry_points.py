# backend/app/futures/api/entry_points.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from ...database import get_db
from ..services.signal_timing import SignalTimingService

router = APIRouter(prefix="/entry-points", tags=["entry-points"])

@router.get("/active")
def get_active_entry_points(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Отримати активні точки входу"""
    signals_data = SignalTimingService.get_active_signals(db)
    
    # Форматуємо для фронтенду
    entry_points = []
    for signal in signals_data["active"]:
        entry_point = {
            "id": signal["id"],
            "symbol": signal["symbol"],
            "direction": signal["direction"],
            "confidence": signal["confidence"],
            "entry_price": signal["entry_price"],
            "take_profit": signal["take_profit"],
            "stop_loss": signal["stop_loss"],
            "signal_strength": signal.get("signal_strength", "medium"),
            "timing": signal["timing"],
            "urgency": signal["timing"]["urgency_level"],
            "action": "available"  # available, entered, expired
        }
        entry_points.append(entry_point)
    
    return {
        "status": "success",
        "count": len(entry_points),
        "entry_points": entry_points[:limit],
        "statistics": signals_data["counts"]
    }

@router.post("/enter/{signal_id}")
def enter_trade(
    signal_id: int,
    user_id: int = 1,  # TODO: Замінити на реальний user_id
    db: Session = Depends(get_db)
):
    """Увійти в угоду по сигналу"""
    result = SignalTimingService.create_timed_trade(db, signal_id, user_id)
    
    if "error" in result:
        raise HTTPException(
            status_code=400 if result["error"] == "Signal expired" else 409,
            detail=result["error"]
        )
    
    return {
        "status": "success",
        "message": "Successfully entered trade",
        **result
    }

@router.get("/my-trades")
def get_my_trades(
    user_id: int = 1,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Отримати мої віртуальні угоди"""
    from ..models import VirtualTrade
    from sqlalchemy import desc
    
    query = db.query(VirtualTrade).filter(VirtualTrade.user_id == user_id)
    
    if status:
        query = query.filter(VirtualTrade.status == status)
    
    trades = query.order_by(desc(VirtualTrade.created_at)).all()
    
    # Додаємо інформацію про сигнал
    enhanced_trades = []
    for trade in trades:
        trade_dict = trade.to_dict()
        
        # Додаємо таймінги з сигналу
        if trade.signal_id:
            from ..models import Signal
            signal = db.query(Signal).filter(Signal.id == trade.signal_id).first()
            if signal:
                timing = SignalTimingService.calculate_timing(signal)
                trade_dict["signal_timing"] = timing
        
        enhanced_trades.append(trade_dict)
    
    return {
        "status": "success",
        "count": len(trades),
        "trades": enhanced_trades
    }