# backend/app/futures/models/exchange_connector.py
import ccxt
import pandas as pd
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# 1️⃣ ВИКЛИК load_dotenv() ДЛЯ ЗАВАНТАЖЕННЯ КЛЮЧІВ З .env
load_dotenv()

class ExchangeConnector:
    def __init__(self, exchange_id: str = 'binance'):
        # 2️⃣ Зчитуємо ключі
        api_key = os.getenv('EXCHANGE_API_KEY')
        api_secret = os.getenv('EXCHANGE_API_SECRET')
        
        # 3️⃣ Перевірка на наявність ключів (важливо!)
        if not api_key or not api_secret:
            raise ValueError("❌ API ключі не знайдено. Перевірте .env файл")
        
        # 4️⃣ Створюємо підключення
        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True
            }
        })
        
        print(f"✅ Підключено до {exchange_id}. Ключ: {'Так' if api_key else 'Ні'}")
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Отримання історичних даних"""
        try:
            # 5️⃣ Виправлення: ccxt може вимагати правильний формат символу
            if not symbol.endswith(':USDT'):
                symbol = f"{symbol}:USDT"
                
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"❌ Помилка отримання даних {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        """Отримання поточних даних"""
        try:
            if not symbol.endswith(':USDT'):
                symbol = f"{symbol}:USDT"
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            print(f"❌ Помилка ticker {symbol}: {e}")
            return None
    
    def fetch_funding_rate(self, symbol: str) -> Optional[Dict]:
        """Отримання фандинг рейту для ф'ючерсів"""
        try:
            if not symbol.endswith(':USDT'):
                symbol = f"{symbol}:USDT"
                
            if hasattr(self.exchange, 'fetchFundingRate'):
                return self.exchange.fetchFundingRate(symbol)
            return None
        except Exception as e:
            print(f"⚠️  Фандинг рейт не отримано {symbol}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Простий тест підключення"""
        try:
            # 6️⃣ Тестуємо отримання балансу
            balance = self.exchange.fetch_balance()
            print(f"✅ Баланс отримано! USDT: {balance.get('USDT', {}).get('free', 0)}")
            return True
        except Exception as e:
            print(f"❌ Помилка тесту: {e}")
            return False