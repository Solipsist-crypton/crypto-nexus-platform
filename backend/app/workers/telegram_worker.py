import time
import logging
from datetime import datetime
import json
import redis
import sys
import os

# Додаємо шлях для імпортів
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.telegram_notifier import telegram_notifier
# Імпортуємо функцію для отримання арбітражних можливостей
try:
    from app.services.arbitrage_calculator import find_arbitrage_opportunities
    ARBITRAGE_AVAILABLE = True
except ImportError:
    ARBITRAGE_AVAILABLE = False
    # Якщо функції немає, створимо заглушку
    def find_arbitrage_opportunities():
        # Заглушка для тесту
        return [
            {
                'coin': 'BTC',
                'net_profit_percent': 2.5,
                'buy_exchange': 'Binance',
                'sell_exchange': 'KuCoin',
                'buy_price': 45000,
                'sell_price': 46500,
                'volume': 1000000
            },
            {
                'coin': 'ETH',
                'net_profit_percent': 1.8,
                'buy_exchange': 'Coinbase',
                'sell_exchange': 'Kraken',
                'buy_price': 2400,
                'sell_price': 2450,
                'volume': 500000
            }
        ]

logger = logging.getLogger(__name__)

class TelegramArbitrageWorker:
    """
    Окремий воркер для моніторингу арбітражу та відправки сповіщень в Telegram
    """
    
    def __init__(self, check_interval=30, profit_threshold=0.5):
        """
        Args:
            check_interval: секунди між перевірками (default: 30)
            profit_threshold: мінімальний прибуток для сповіщення % (default: 0.5)
        """
        self.check_interval = check_interval
        self.profit_threshold = profit_threshold
        self.running = False
        self.alert_history = {}  # Історія сповіщень
        
        # Підключення до Redis для уникнення дублікатів
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            logger.info("✅ Redis connected for alert deduplication")
            self.redis_available = True
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}. Using in-memory cache.")
            self.redis_available = False
        
        # Перевірка Telegram
        if not telegram_notifier.enabled:
            logger.error("❌ Telegram notifier is disabled!")
        else:
            logger.info("✅ Telegram notifier is ready")
    
    def _get_alert_key(self, opportunity):
        """
        Генерує унікальний ключ для арбітражу
        Використовується для уникнення дублікатів
        """
        coin = opportunity.get('coin', 'unknown').upper()
        profit = round(opportunity.get('net_profit_percent', 0), 1)  # Округлюємо до 0.1%
        hour_window = datetime.now().strftime("%Y-%m-%d-%H")  # Группуємо по годинах
        
        return f"arb:{coin}:{profit}:{hour_window}"
    
    def _should_send_alert(self, opportunity):
        """
        Визначає, чи потрібно відправляти сповіщення
        """
        profit = opportunity.get('net_profit_percent', 0)
        
        # 1. Перевірка порогу прибутку
        if profit < self.profit_threshold:
            return False
        
        # 2. Перевірка на дублікати (через Redis або пам'ять)
        alert_key = self._get_alert_key(opportunity)
        
        if self.redis_available:
            # Використовуємо Redis з TTL 1 година
            if self.redis_client.exists(alert_key):
                return False
            self.redis_client.setex(alert_key, 3600, "1")
        else:
            # Використовуємо пам'ять
            if alert_key in self.alert_history:
                return False
            self.alert_history[alert_key] = datetime.now()
            
            # Очищаємо старі записи (старше 2 годин)
            old_keys = [k for k, v in self.alert_history.items() 
                       if (datetime.now() - v).seconds > 7200]
            for k in old_keys:
                del self.alert_history[k]
        
        return True
    
    def check_arbitrage(self):
        """
        Перевіряє наявність арбітражних можливостей
        Повертає список можливостей, що відповідають порогу
        """
        try:
            if not ARBITRAGE_AVAILABLE:
                logger.warning("⚠️ Using mock arbitrage data")
            
            opportunities = find_arbitrage_opportunities()
            
            if not opportunities:
                return []
            
            # Фільтруємо за порогом прибутку
            filtered = []
            for opp in opportunities:
                if opp.get('net_profit_percent', 0) >= self.profit_threshold:
                    filtered.append(opp)
            
            return filtered
            
        except Exception as e:
            logger.error(f"❌ Error checking arbitrage: {e}")
            return []
    
    def send_alerts(self, opportunities):
        """
        Відправляє сповіщення для списку можливостей
        """
        sent_count = 0
        
        for opp in opportunities:
            if self._should_send_alert(opp):
                success = telegram_notifier.send_arbitrage_alert(
                    opp, 
                    threshold_percent=self.profit_threshold
                )
                
                if success:
                    sent_count += 1
                    coin = opp.get('coin', 'Unknown')
                    profit = opp.get('net_profit_percent', 0)
                    logger.info(f"📨 Alert sent: {coin} ({profit:.2f}%)")
        
        return sent_count
    
    def run_iteration(self):
        """
        Виконує одну ітерацію перевірки та відправки
        """
        logger.info(f"🔍 Checking arbitrage (threshold: {self.profit_threshold}%)...")
        
        # Отримуємо можливості
        opportunities = self.check_arbitrage()
        
        if not opportunities:
            logger.info("📭 No arbitrage opportunities found")
            return 0
        
        logger.info(f"📊 Found {len(opportunities)} opportunities")
        
        # Відправляємо сповіщення
        sent = self.send_alerts(opportunities)
        
        if sent > 0:
            logger.info(f"✅ Sent {sent} alerts to Telegram")
        else:
            logger.info("📭 No new alerts to send (duplicates)")
        
        return sent
    
    def run_continuous(self):
        """
        Запускає безперервний моніторинг
        """
        self.running = True
        logger.info(f"🚀 Starting Telegram Arbitrage Worker")
        logger.info(f"   Check interval: {self.check_interval}s")
        logger.info(f"   Profit threshold: {self.profit_threshold}%")
        logger.info("   Press Ctrl+C to stop")
        
        iteration = 0
        
        try:
            while self.running:
                iteration += 1
                start_time = time.time()
                
                logger.info(f"\n{'='*50}")
                logger.info(f"Iteration #{iteration}")
                
                # Виконуємо перевірку
                alerts_sent = self.run_iteration()
                
                # Обчислюємо час очікування
                elapsed = time.time() - start_time
                sleep_time = max(1, self.check_interval - elapsed)
                
                if sleep_time > 0:
                    logger.info(f"⏰ Next check in {sleep_time:.1f}s")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logger.info("\n🛑 Worker stopped by user")
        except Exception as e:
            logger.error(f"💥 Worker crashed: {e}", exc_info=True)
        finally:
            self.running = False
    
    def run_once(self):
        """Запускає одну перевірку"""
        return self.run_iteration()