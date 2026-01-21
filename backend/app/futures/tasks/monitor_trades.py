"""
Celery завдання для моніторингу віртуальних угод.
"""

from celery import Celery
import os
import random
from datetime import datetime

# Налаштування Celery ВИЩЕ за все
celery_app = Celery(
    'futures_tasks',
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0")
)

def get_current_price(symbol: str = "BTCUSDT") -> float:
    """Отримати поточну ціну (тимчасово - симуляція)"""
    try:
        base_prices = {
            "BTCUSDT": 42000.0,
            "ETHUSDT": 2250.0,
            "SOLUSDT": 95.0,
            "ADAUSDT": 0.45
        }
        base = base_prices.get(symbol.upper(), 100.0)
        variation = random.uniform(-0.02, 0.02)  # ±2%
        return round(base * (1 + variation), 2)
    except Exception:
        return 0.0

@celery_app.task
def monitor_virtual_trades():
    """Основне завдання для моніторингу активних віртуальних угод"""
    print(f"[{datetime.now()}] Starting virtual trades monitoring...")
    
    # Імпортуємо ВСЕРЕДИНІ функції, щоб уникнути циклічних залежностей
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.app.futures.models import VirtualTrade, Signal
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return {"status": "error", "error": "No DATABASE_URL"}
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        active_trades = db.query(VirtualTrade).filter(
            VirtualTrade.status == "active"
        ).all()
        
        print(f"Found {len(active_trades)} active trades")
        updated_count = 0
        closed_count = 0
        
        for trade in active_trades:
            signal = db.query(Signal).filter(Signal.id == trade.signal_id).first()
            if not signal:
                continue
            
            symbol = signal.symbol
            current_price = get_current_price(symbol)
            
            if current_price > 0:
                old_status = trade.status
                
                # Оновлюємо PnL
                if trade.calculate_pnl(current_price):
                    db.add(trade)
                
                # Якщо статус змінився
                if trade.status != old_status and trade.status in ["tp_hit", "sl_hit"]:
                    from sqlalchemy.sql import func
                    trade.closed_at = func.now()
                    closed_count += 1
                    print(f"  Trade {trade.id} changed: {old_status} -> {trade.status}, PnL: {trade.pnl_percentage:.2f}%")
                
                updated_count += 1
        
        db.commit()
        
        result = {
            "status": "success",
            "updated": updated_count,
            "closed": closed_count,
            "timestamp": datetime.now().isoformat()
        }
        print(f"Result: {result}")
        return result
        
    except Exception as e:
        print(f"Error in monitor_virtual_trades: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@celery_app.task
def update_all_prices():
    """Оновити ціни для всіх активних угод"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.app.futures.models import VirtualTrade, Signal
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return {"status": "error", "error": "No DATABASE_URL"}
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        trades = db.query(VirtualTrade).filter(
            VirtualTrade.status == "active"
        ).all()
        
        for trade in trades:
            signal = db.query(Signal).filter(Signal.id == trade.signal_id).first()
            if signal:
                price = get_current_price(signal.symbol)
                if price > 0:
                    trade.current_price = price
                    db.add(trade)
        
        db.commit()
        return {"updated": len(trades)}
    finally:
        db.close()

# Планувальник завдань
celery_app.conf.beat_schedule = {
    'monitor-virtual-trades-every-5-minutes': {
        'task': 'backend.app.futures.tasks.monitor_trades.monitor_virtual_trades',
        'schedule': 300.0,  # 5 хвилин
    },
}