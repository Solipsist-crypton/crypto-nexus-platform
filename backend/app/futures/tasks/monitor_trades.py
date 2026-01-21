"""
Celery завдання для моніторингу віртуальних угод.
Запускати кожні 5 хвилин для оновлення цін.
"""

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import requests
from datetime import datetime

# Налаштування Celery
celery_app = Celery(
    'futures_tasks',
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# Налаштування БД
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_current_price(symbol: str = "BTCUSDT") -> float:
    """
    Отримати поточну ціну з біржі (тимчасово - з CoinGecko)
    
    Args:
        symbol: Торгова пара (BTCUSDT -> btc)
        
    Returns:
        Поточна ціна
    """
    try:
        # Тимчасово: фіксована ціна або випадкова зміна
        import random
        base_price = 42000.0  # Базова ціна BTC
        price_variation = random.uniform(-0.02, 0.02)  # ±2%
        return base_price * (1 + price_variation)
        
        # Пізніше можна додати реальний API:
        # if symbol.upper().endswith("USDT"):
        #     coin_id = symbol[:-4].lower()
        #     response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd")
        #     return response.json()[coin_id]["usd"]
    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return 0.0

@celery_app.task
def monitor_virtual_trades():
    """
    Основне завдання для моніторингу активних віртуальних угод
    """
    print(f"[{datetime.now()}] Starting virtual trades monitoring...")
    
    db = SessionLocal()
    try:
        # Отримуємо всі активні угоди
        from backend.app.futures.models import VirtualTrade, Signal
        
        active_trades = db.query(VirtualTrade).filter(
            VirtualTrade.status == "active"
        ).all()
        
        print(f"Found {len(active_trades)} active trades")
        
        updated_count = 0
        closed_count = 0
        
        for trade in active_trades:
            # Отримуємо символ з пов'язаного сигналу
            signal = db.query(Signal).filter(Signal.id == trade.signal_id).first()
            if not signal:
                continue
            
            symbol = signal.symbol
            current_price = get_current_price(symbol)
            
            if current_price > 0:
                # Зберігаємо старий статус
                old_status = trade.status
                
                # Оновлюємо PnL
                trade.calculate_pnl(current_price)
                
                # Якщо статус змінився
                if trade.status != old_status:
                    trade.closed_at = datetime.now()
                    closed_count += 1
                    print(f"  Trade {trade.id} changed status: {old_status} -> {trade.status}")
                    print(f"    PnL: {trade.pnl_percentage:.2f}%")
                
                updated_count += 1
        
        db.commit()
        
        print(f"Updated {updated_count} trades, closed {closed_count} trades")
        return {
            "status": "success",
            "updated": updated_count,
            "closed": closed_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error in monitor_virtual_trades: {e}")
        db.rollback()
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    finally:
        db.close()

@celery_app.task
def update_all_prices():
    """
    Оновити ціни для всіх активних угод (швидке завдання)
    """
    db = SessionLocal()
    try:
        from backend.app.futures.models import VirtualTrade, Signal
        
        trades = db.query(VirtualTrade).filter(
            VirtualTrade.status == "active"
        ).all()
        
        for trade in trades:
            signal = db.query(Signal).filter(Signal.id == trade.signal_id).first()
            if signal:
                price = get_current_price(signal.symbol)
                if price > 0:
                    trade.current_price = price
        
        db.commit()
        return {"updated": len(trades)}
        
    finally:
        db.close()

# Планувальник завдань (запускати кожні 5 хвилин)
celery_app.conf.beat_schedule = {
    'monitor-virtual-trades-every-5-minutes': {
        'task': 'backend.app.futures.tasks.monitor_trades.monitor_virtual_trades',
        'schedule': 300.0,  # 5 хвилин
    },
}