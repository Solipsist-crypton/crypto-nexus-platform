# backend/app/services/price_updater_service.py
import threading
import time
import logging
from ..database import SessionLocal
from ..futures.services.trade_executor import VirtualTradeExecutor

logger = logging.getLogger(__name__)

class PriceUpdaterService:
    """Сервіс для фонового оновлення цін"""
    
    def __init__(self, interval_seconds=60):
        self.interval = interval_seconds
        self.is_running = False
        self.thread = None
        self.executor = VirtualTradeExecutor()
    
    def start(self):
        """Запуск сервісу"""
        if self.is_running:
            logger.warning("Сервіс вже запущено")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"✅ Сервіс оновлення цін запущено (інтервал: {self.interval}с)")
    
    def stop(self):
        """Зупинка сервісу"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Сервіс оновлення цін зупинено")
    
    def _run(self):
        """Основна логіка оновлення"""
        while self.is_running:
            try:
                self._update_all_trades()
            except Exception as e:
                logger.error(f"Помилка оновлення: {e}")
            
            # Зачекати до наступного оновлення
            for _ in range(self.interval):
                if not self.is_running:
                    break
                time.sleep(1)
    
    def _update_all_trades(self):
        """Оновлення всіх угод"""
        db = SessionLocal()
        try:
            results = self.executor.update_all_active_trades(db)
            
            if results["updated"] > 0:
                logger.info(f"Оновлено {results['updated']}/{results['total']} угод")
                if results["tp_hit"] > 0:
                    logger.info(f"🎯 TP досягнуто: {results['tp_hit']} угод")
                if results["sl_hit"] > 0:
                    logger.info(f"🛑 SL досягнуто: {results['sl_hit']} угод")
                    
        finally:
            db.close()

# Глобальний екземпляр
price_updater = PriceUpdaterService(interval_seconds=30)

# Інтеграція з FastAPI
def start_price_updater():
    """Запустити при старті FastAPI"""
    price_updater.start()

def stop_price_updater():
    """Зупинити при виході"""
    price_updater.stop()