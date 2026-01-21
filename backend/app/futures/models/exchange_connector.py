# backend/app/futures/models/exchange_connector.py
import ccxt
import pandas as pd
from typing import Dict, List, Optional
import talib
import numpy as np

class ExchangeConnector:
    def __init__(self, exchange_id: str = 'binance'):
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True
            }
        })
        
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        """Отримання історичних даних"""
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    
    def fetch_ticker(self, symbol: str):
        """Отримання поточних даних"""
        return self.exchange.fetch_ticker(symbol)
    
    def fetch_funding_rate(self, symbol: str):
        """Отримання фандинг рейту для ф'ючерсів"""
        if hasattr(self.exchange, 'fetchFundingRate'):
            return self.exchange.fetchFundingRate(symbol)
        return None