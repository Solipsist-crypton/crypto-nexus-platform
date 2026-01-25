# backend/app/futures/api/virtual_trades.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ..models import VirtualTrade, Signal
from ..services.trade_executor import VirtualTradeExecutor

router = APIRouter(prefix="/virtual-trades", tags=["virtual-trades"])
executor = VirtualTradeExecutor()

@router.post("/{signal_id}")
def create_from_signal(
    signal_id: int,
    user_id: int = 1,  # TODO: Замінити на реальний user_id з авторизації
    db: Session = Depends(get_db)
):
    """Створити віртуальну угоду на основі сигналу"""
    trade = executor.create_virtual_trade(db, signal_id, user_id)
    
    if not trade:
        raise HTTPException(status_code=400, detail="Не вдалося створити угоду")
    
    return {
        "status": "success",
        "message": "Віртуальна угода створена",
        "trade": trade.to_dict()
    }

@router.get("/")
def get_user_trades(
    user_id: int = 1,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Отримати віртуальні угоди користувача"""
    query = db.query(VirtualTrade).filter(VirtualTrade.user_id == user_id)
    
    if status:
        query = query.filter(VirtualTrade.status == status)
    
    trades = query.order_by(VirtualTrade.created_at.desc()).all()
    
    return {
        "status": "success",
        "count": len(trades),
        "trades": [trade.to_dict() for trade in trades]
    }

@router.post("/{trade_id}/update")
def update_trade_price(
    trade_id: int,
    db: Session = Depends(get_db)
):
    """Оновити ціну для віртуальної угоди"""
    result = executor.update_trade_prices(db, trade_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Угоду не знайдено або вона не активна")
    
    return {
        "status": "success",
        "message": "Ціну оновлено",
        **result
    }

@router.post("/update-all")
def update_all_trades(db: Session = Depends(get_db)):
    """Оновити всі активні угоди"""
    results = executor.update_all_active_trades(db)
    
    return {
        "status": "success",
        "message": "Всі угоди оновлено",
        "results": results
    }

@router.get("/statistics")
def get_trading_statistics(
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Отримати статистику торгівлі"""
    trades = db.query(VirtualTrade).filter(VirtualTrade.user_id == user_id).all()
    
    if not trades:
        return {
            "total_trades": 0,
            "active_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "average_pnl": 0
        }
    
    total_trades = len(trades)
    active_trades = len([t for t in trades if t.status == "active"])
    closed_trades = [t for t in trades if t.status in ["tp_hit", "sl_hit"]]
    
    if closed_trades:
        winning_trades = [t for t in closed_trades if t.status == "tp_hit"]
        win_rate = (len(winning_trades) / len(closed_trades)) * 100
        total_pnl = sum(t.pnl_percentage for t in closed_trades)
        average_pnl = total_pnl / len(closed_trades)
    else:
        win_rate = 0
        total_pnl = 0
        average_pnl = 0
    
    return {
        "total_trades": total_trades,
        "active_trades": active_trades,
        "closed_trades": len(closed_trades),
        "winning_trades": len([t for t in closed_trades if t.status == "tp_hit"]),
        "losing_trades": len([t for t in closed_trades if t.status == "sl_hit"]),
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "average_pnl": round(average_pnl, 2),
        "best_trade": round(max([t.pnl_percentage for t in closed_trades], default=0), 2),
        "worst_trade": round(min([t.pnl_percentage for t in closed_trades], default=0), 2)
    }