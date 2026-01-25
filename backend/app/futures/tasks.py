# backend/app/futures/tasks.py
from datetime import datetime
import logging
from ..celery_app import celery_app
from ..database import SessionLocal
from .services.trade_executor import VirtualTradeExecutor

logger = logging.getLogger(__name__)

@celery_app.task
def update_virtual_trades_prices():
    """Завдання для автоматичного оновлення цін угод"""
    logger.info("🔄 Оновлення цін віртуальних угод...")
    
    db = SessionLocal()
    try:
        executor = VirtualTradeExecutor()
        results = executor.update_all_active_trades(db)
        
        # Логування
        if results["updated"] > 0:
            message = f"📊 Оновлено {results['updated']}/{results['total']} угод"
            if results["tp_hit"] > 0:
                message += f", 🎯 TP: {results['tp_hit']}"
            if results["sl_hit"] > 0:
                message += f", 🛑 SL: {results['sl_hit']}"
            logger.info(message)
        
        return results
    except Exception as e:
        logger.error(f"❌ Помилка: {str(e)[:100]}")
        return {"error": str(e)[:100], "updated": 0}
    finally:
        db.close()

@celery_app.task
def create_virtual_trade_from_signal(signal_id: int, user_id: int = 1):
    """Створення віртуальної угоди з сигналу (асинхронно)"""
    logger.info(f"📝 Створення вірт. угоди для сигналу {signal_id}")
    
    db = SessionLocal()
    try:
        from .services.trade_executor import VirtualTradeExecutor
        
        executor = VirtualTradeExecutor()
        trade = executor.create_virtual_trade(db, signal_id, user_id)
        
        if trade:
            logger.info(f"✅ Створено угоду #{trade.id} для сигналу #{signal_id}")
            return {"trade_id": trade.id, "status": "created"}
        else:
            logger.warning(f"⚠️ Не вдалося створити угоду для сигналу #{signal_id}")
            return {"trade_id": None, "status": "failed"}
            
    except Exception as e:
        logger.error(f"❌ Помилка створення: {str(e)[:100]}")
        return {"error": str(e)[:100]}
    finally:
        db.close()