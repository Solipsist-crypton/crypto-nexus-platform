# backend/app/futures/services/signal_orchestrator.py
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import logging
from app.futures.models.exchange_connector import ExchangeConnector
from .ai_analyzer import AIAnalyzer
from .explanation_builder import ExplanationBuilder

class SignalOrchestrator:
    def __init__(self):
        self.exchange = ExchangeConnector()
        self.analyzer = AIAnalyzer()
        self.explainer = ExplanationBuilder()
        self.logger = logging.getLogger(__name__)
        
    def generate_signal(self, symbol: str, timeframe: str = '1h') -> Dict:
        """Повний пайплайн генерації сигналу"""
        try:
            self.logger.info(f"🔍 Генерація сигналу для {symbol} ({timeframe})")
            
            # 1. Отримуємо дані
            df = self.exchange.fetch_ohlcv(symbol, timeframe, limit=200)
            if len(df) < 50:
                return {'error': 'Недостатньо даних', 'symbol': symbol}
            
            # 2. Аналізуємо (ВИПРАВЛЕНО: використовуємо правильну назву методу)
            indicators = self.analyzer._calculate_indicators(df)  # або .calculate_indicators(df)
            analysis = self.analyzer.generate_signal(symbol, df, indicators)
            
            # 3. Генеруємо пояснення
            explanation = self.explainer.build_explanation(analysis)
            analysis['explanation'] = explanation
            
            # 4. Додаємо метадані
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['timeframe'] = timeframe
            
            self.logger.info(f"✅ Сигнал згенеровано: {analysis['direction']} з впевненістю {analysis['confidence']}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Помилка генерації сигналу: {e}")
            return {'error': str(e), 'symbol': symbol}
    
    def generate_multiple_signals(self, symbols: List[str]) -> List[Dict]:
        """Генерація сигналів для кількох пар"""
        signals = []
        for symbol in symbols:
            signal = self.generate_signal(symbol)
            if 'error' not in signal:
                signals.append(signal)
        return signals