import requests
import logging
from datetime import datetime  # Додаємо імпорт
import os

# Налаштування логування
logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        
        self.token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')

        
        # Перевірка
        if not self.token or not self.chat_id:
            logger.error("❌ Telegram credentials not configured!")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ Telegram notifier initialized")
    
    def _format_message(self, opportunity, threshold_percent):
        """Формує повідомлення для Telegram"""
        coin = opportunity.get('coin', 'Unknown')
        profit = opportunity.get('net_profit_percent', 0)
        buy_exchange = opportunity.get('buy_exchange', 'N/A')
        sell_exchange = opportunity.get('sell_exchange', 'N/A')
        buy_price = opportunity.get('buy_price', 0)
        sell_price = opportunity.get('sell_price', 0)
        volume = opportunity.get('volume', 0)
        
        # Формуємо повідомлення
        message = f"🚀 *ARBITRAGE ALERT!*\n\n"
        message += f"*Coin:* `{coin}`\n"
        message += f"*Profit:* `{profit:.2f}%` (Threshold: {threshold_percent}%)\n"
        message += f"*Buy at:* {buy_exchange} - ${buy_price:,.2f}\n"
        message += f"*Sell at:* {sell_exchange} - ${sell_price:,.2f}\n"
        
        if sell_price > buy_price:
            spread = sell_price - buy_price
            message += f"*Spread:* ${spread:,.2f}\n"
        
        if volume > 0:
            message += f"*Volume:* ${volume:,.0f}\n"
        
        message += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    def send_message(self, text, parse_mode='Markdown'):
        """Відправляє будь-яке повідомлення"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"📨 Telegram message sent")
            return True
            
        except requests.exceptions.Timeout:
            logger.error("❌ Telegram API timeout")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ No internet connection to Telegram")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
            return False
    
    def send_arbitrage_alert(self, opportunity, threshold_percent=1.0):
        """Відправляє сповіщення про арбітраж"""
        if not self.enabled:
            return False
        
        try:
            # Форматуємо повідомлення
            message = self._format_message(opportunity, threshold_percent)
            
            # Відправляємо
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"❌ Failed to send arbitrage alert: {e}")
            return False
    
    def test_connection(self):
        """Тестує підключення до Telegram"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"✅ Bot connected: {bot_info.get('result', {}).get('username')}")
                return True
            else:
                logger.error(f"❌ Bot connection failed: {response.json()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Bot test failed: {e}")
            return False

# Глобальний екземпляр для імпорту
telegram_notifier = TelegramNotifier()

# Тестуємо при імпорті (опційно)
if __name__ == "__main__":
    print("🤖 Testing Telegram notifier...")
    
    # Тест підключення
    if telegram_notifier.test_connection():
        print("✅ Bot connection OK")
        
        # Тест повідомлення
        test_msg = telegram_notifier.send_message("🔄 Telegram notifier test successful!")
        if test_msg:
            print("✅ Test message sent")
        else:
            print("❌ Test message failed")
    else:
        print("❌ Bot connection failed")