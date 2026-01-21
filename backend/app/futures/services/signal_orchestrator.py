# backend/modules/signal_orchestrator.py
import asyncio
from typing import List, Dict
import pandas as pd

class SignalOrchestrator:
    def __init__(self, exchange_connector, ai_analyzer):
        self.exchange = exchange_connector
        self.analyzer = ai_analyzer
        self.timeframes = ['5m', '15m', '1h', '4h', '1d']
        
    async def analyze_multiple_timeframes(self, symbol: str) -> Dict:
        """Аналіз на різних таймфреймах"""
        signals = {}
        
        for tf in self.timeframes:
            df = self.exchange.fetch_ohlcv(symbol, tf, 200)
            indicators = self.analyzer.calculate_indicators(df)
            signal = self.analyzer.generate_signal(symbol, df, indicators)
            signals[tf] = signal
            
            # Додаткова логіка конфірмації між таймфреймами
            if tf in ['1h', '4h'] and signal['confidence'] > 0.7:
                # Додаткова перевірка на старшому таймфреймі
                higher_tf = '4h' if tf == '1h' else '1d'
                higher_df = self.exchange.fetch_ohlcv(symbol, higher_tf, 100)
                higher_indicators = self.analyzer.calculate_indicators(higher_df)
                
                # Конфірмація тренду
                if (signal['direction'] == 'long' and 
                    higher_df['close'].iloc[-1] > higher_df['ema_50'].iloc[-1]):
                    signal['confidence'] *= 1.1  # Підвищення впевненості
        
        return signals