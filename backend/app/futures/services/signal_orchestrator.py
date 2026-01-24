# backend/app/futures/services/signal_orchestrator.py
import pandas as pd
from datetime import datetime
from typing import Dict, List
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
            
            # 1. Отримуємо реальні дані (для майбутньої інтеграції)
            df = self.exchange.fetch_ohlcv(symbol, timeframe, limit=200)
            
            # 2. Аналізуємо через AI (користуємось нашою імітаційною моделлю)
            # Примітка: поточний AIAnalyzer НЕ використовує df, але ми передаємо його
            # для майбутньої реалізації з реальним аналізом
            analysis = self.analyzer.analyze_market(symbol, timeframe)
            
            # 3. Додаємо реальні ціни з біржі замість імітованих
            ticker = self.exchange.fetch_ticker(symbol)
            if ticker:
                current_price = ticker['last']
                analysis['entry_price'] = current_price
                # Перераховуємо TP/SL на основі реальної ціни
                if analysis['direction'] == "long":
                    analysis['take_profit'] = current_price * 1.03
                    analysis['stop_loss'] = current_price * 0.98
                else:
                    analysis['take_profit'] = current_price * 0.97
                    analysis['stop_loss'] = current_price * 1.02
            
            # 4. Генеруємо пояснення
            explanation = self.explainer.build_explanation(analysis)
            analysis['explanation'] = explanation
            
            # 5. Додаємо метадані
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['timeframe'] = timeframe
            analysis['symbol'] = symbol
            
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