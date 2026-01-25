# backend/app/futures/tasks.py
from celery import Celery
from app.database import SessionLocal
from .services.trade_executor import VirtualTradeExecutor

celery_app = Celery('futures_tasks', broker='redis://redis:6379/0')

@celery_app.task
def update_virtual_trades_prices():
    """Завдання для автоматичного оновлення цін угод"""
    db = SessionLocal()
    try:
        executor = VirtualTradeExecutor()
        results = executor.update_all_active_trades(db)
        
        # Логування результатів
        if results["tp_hit"] > 0 or results["sl_hit"] > 0:
            print(f"⚡ Оновлено {results['updated']} угод. TP: {results['tp_hit']}, SL: {results['sl_hit']}")
        
        return results
    finally:
        db.close()

# Розклад завдань
celery_app.conf.beat_schedule = {
    'update-trades-every-5-minutes': {
        'task': 'app.futures.tasks.update_virtual_trades_prices',
        'schedule': 300.0,  # кожні 5 хвилин
    },
}