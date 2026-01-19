import requests
import time
import os
import logging
import sys

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

class TelegramArbitrageBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not self.token or not self.chat_id:
            logger.error("❌ Telegram credentials not set in environment variables!")
            logger.error("   Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
            sys.exit(1)
        self.api_url = os.getenv('BACKEND_URL', 'http://backend:5000')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
        self.profit_threshold = float(os.getenv('PROFIT_THRESHOLD', '0.5'))
        
        # Тестуємо з'єднання при старті
        self.test_connections()
        
        logger.info(f"🤖 Telegram Arbitrage Bot Started")
        logger.info(f"   Token: {'***' + self.token[-8:]}")
        logger.info(f"   Chat ID: {self.chat_id}")
        logger.info(f"   Backend: {self.api_url}")
        logger.info(f"   Interval: {self.check_interval}s")
        logger.info(f"   Threshold: {self.profit_threshold}%")
    
    def test_connections(self):
        """Тестує з'єднання з бекендом і Telegram"""
        logger.info("🔍 Testing connections...")
        
        # Тест бекенду
        try:
            response = requests.get(f"{self.api_url}/api/arbitrage/scan", timeout=5)
            logger.info(f"✅ Backend: {response.status_code}")
            
            data = response.json()
            logger.info(f"   API structure: {list(data.keys())}")
            
            if 'data' in data:
                logger.info(f"   Data keys: {list(data['data'].keys())}")
                
        except Exception as e:
            logger.error(f"❌ Backend connection failed: {e}")
        
        # Тест Telegram
        try:
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            response = requests.get(url, timeout=5)
            logger.info(f"✅ Telegram: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Telegram connection failed: {e}")
    
    def send_telegram(self, message):
        """Відправляє повідомлення в Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                logger.error(f"❌ Telegram error: {response.json()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram: {e}")
            return False
    
    def check_arbitrage(self):
        """Перевіряє арбітраж через API бекенда"""
        try:
            url = f"{self.api_url}/api/arbitrage/scan"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 🔽 ВИПРАВЛЕННЯ: правильний шлях до даних
                opportunities = data.get('data', {}).get('opportunities', [])
                # 🔼 ВИПРАВЛЕНО 🔼
                
                # Фільтруємо за порогом прибутку
                filtered = []
                for opp in opportunities:
                    profit = opp.get('net_profit_percent', 0)
                    if profit >= self.profit_threshold:
                        filtered.append(opp)
                
                return filtered
            else:
                logger.error(f"❌ API error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"💥 Error checking arbitrage: {e}")
            return []
    
    def format_alert(self, opportunity):
        """Форматує повідомлення про арбітраж"""
        coin = opportunity.get('coin', 'Unknown')
        profit = opportunity.get('net_profit_percent', 0)
        buy_ex = opportunity.get('buy_exchange', 'N/A')
        sell_ex = opportunity.get('sell_exchange', 'N/A')
        buy_price = opportunity.get('buy_price', 0)
        sell_price = opportunity.get('sell_price', 0)
        volume = opportunity.get('volume', 0)
        
        message = f"🚀 *ARBITRAGE ALERT!*\n\n"
        message += f"*Coin:* `{coin}`\n"
        message += f"*Profit:* `{profit:.2f}%`\n"
        message += f"*Buy:* {buy_ex} - ${buy_price:,.2f}\n"
        message += f"*Sell:* {sell_ex} - ${sell_price:,.2f}\n"
        
        if sell_price > buy_price:
            spread = sell_price - buy_price
            spread_percent = (spread / buy_price) * 100
            message += f"*Spread:* ${spread:,.2f} ({spread_percent:.2f}%)\n"
        
        if volume > 0:
            message += f"*Volume:* ${volume:,.0f}\n"
        
        message += f"\n⏰ {time.strftime('%H:%M:%S')}"
        
        return message
    
    def run_once(self):
        """Виконує одну перевірку"""
        logger.info("🔍 Checking for arbitrage opportunities...")
        
        opportunities = self.check_arbitrage()
        
        if not opportunities:
            logger.info("📭 No opportunities found")
            return 0
        
        logger.info(f"📊 Found {len(opportunities)} opportunities")
        
        sent_count = 0
        for opp in opportunities:
            message = self.format_alert(opp)
            if self.send_telegram(message):
                sent_count += 1
                logger.info(f"📨 Alert sent for {opp.get('coin')} ({opp.get('net_profit_percent', 0):.2f}%)")
        
        logger.info(f"✅ Sent {sent_count} alerts")
        return sent_count
    
    def run_continuous(self):
        """Запускає безперервний моніторинг"""
        iteration = 0
        
        logger.info(f"\n{'='*60}")
        logger.info("🚀 Starting continuous monitoring")
        logger.info(f"   Press Ctrl+C to stop")
        logger.info(f"{'='*60}\n")
        
        try:
            while True:
                iteration += 1
                
                logger.info(f"\n📊 Iteration #{iteration}")
                logger.info(f"{'-'*40}")
                
                start_time = time.time()
                alerts_sent = self.run_once()
                
                # Чекаємо до наступної перевірки
                elapsed = time.time() - start_time
                sleep_time = max(1, self.check_interval - elapsed)
                
                if sleep_time > 0:
                    logger.info(f"⏰ Next check in {sleep_time:.1f}s")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"💥 Bot crashed: {e}")

if __name__ == "__main__":
    bot = TelegramArbitrageBot()
    bot.run_continuous()