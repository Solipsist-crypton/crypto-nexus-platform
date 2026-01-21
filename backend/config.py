# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Біржа
    EXCHANGE = os.getenv('EXCHANGE', 'binance')
    EXCHANGE_TYPE = 'future'
    
    # Торгові пари
    SYMBOLS = [
        'BTC/USDT:USDT',
        'ETH/USDT:USDT',
        'SOL/USDT:USDT',
        'XRP/USDT:USDT',
        'ADA/USDT:USDT',
    ]
    
    # Таймфрейми для аналізу
    TIMEFRAMES = ['5m', '15m', '1h', '4h']
    
    # Налаштування ризиків
    MAX_POSITION_SIZE = 0.1  # 10% портфеля
    MAX_DAILY_LOSS = 0.05    # 5% на день
    MIN_CONFIDENCE = 0.65    # Мінімальна впевненість для входу
    
    # API Keys (для реальної торгівлі)
    API_KEY = os.getenv('EXCHANGE_API_KEY')
    API_SECRET = os.getenv('EXCHANGE_API_SECRET')