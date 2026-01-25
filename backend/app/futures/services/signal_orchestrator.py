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
        """Повний пайплайн генерації сигналу - ВИПРАВЛЕНА ВЕРСІЯ"""
        try:
            self.logger.info(f"🔍 Генерація сигналу для {symbol} ({timeframe})")
            
            # ========== ВАЖЛИВЕ: БЕЗПЕЧНА РОБОТА З ДАНИМИ ==========
            # 1. Отримуємо дані, але готові до того, що їх може не бути
            current_price = None
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                # ВИПРАВЛЕННЯ: перетворюємо ціну в float одразу та перевіряємо
                if ticker and 'last' in ticker:
                    # Це виправляє баг "str > float"!
                    current_price = float(ticker['last'])
                    self.logger.info(f"💰 Отримано реальну ціну: {current_price}")
            except (ValueError, TypeError) as e:
                self.logger.warning(f"⚠️ Не вдалося отримати чи конвертувати ціну: {e}")
                # Якщо не вийшло, current_price залишиться None

            # 2. Аналізуємо через AI (основна логіка)
            analysis = self.analyzer.analyze_market(symbol, timeframe)
            
            # Перевіряємо, чи не повернув AI помилку
            if analysis.get('error'):
                self.logger.error(f"❌ AI Analyzer помилка: {analysis.get('error')}")
                return {'error': analysis.get('error'), 'symbol': symbol}
            
            # ========== ВИПРАВЛЕННЯ ЛОГІКИ ЦІН ==========
            # 3. Якщо ми отримали реальну ціну - коригуємо лише entry_price
            #    і ПРОПОРЦІЙНО перераховуємо TP/SL з аналізу
            if current_price is not None:
                original_entry = float(analysis['entry_price'])  # Конвертуємо для безпеки
                new_entry = current_price
                
                # Обчислюємо % відхилення TP/SL від старої ціни входу
                tp_percent_diff = (float(analysis['take_profit']) - original_entry) / original_entry
                sl_percent_diff = (float(analysis['stop_loss']) - original_entry) / original_entry
                
                # Застосовуємо той самий % до нової ціни входу
                analysis['entry_price'] = new_entry
                analysis['take_profit'] = new_entry * (1 + tp_percent_diff)
                analysis['stop_loss'] = new_entry * (1 + sl_percent_diff)
                
                self.logger.info(f"📊 Ціни скориговано. TP: {analysis['take_profit']:.2f}, SL: {analysis['stop_loss']:.2f}")
            else:
                # Якщо реальної ціни немає, просто конвертуємо все в float
                # Це запобігає багу "str > float" в майбутньому
                analysis['entry_price'] = float(analysis['entry_price'])
                analysis['take_profit'] = float(analysis['take_profit'])
                analysis['stop_loss'] = float(analysis['stop_loss'])
            
            # ВИПРАВЛЕННЯ: гарантуємо, що confidence - це число
            analysis['confidence'] = float(analysis['confidence'])
            
            # 4. Генеруємо пояснення
            explanation = self.explainer.build_explanation(analysis)
            analysis['explanation'] = explanation
            
            # 5. ВИПРАВЛЕННЯ: гарантуємо наявність ключа 'factors'
            if 'factors' not in analysis:
                analysis['factors'] = {
                    "technical": 0.4,
                    "sentiment": 0.3,
                    "volume": 0.3
                }
            
            # 6. Додаємо метадані
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['timeframe'] = timeframe
            analysis['symbol'] = symbol
            
            self.logger.info(f"✅ Сигнал згенеровано: {analysis['direction']} ({analysis['confidence']:.1%})")
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Критична помилка генерації сигналу: {e}", exc_info=True)
            return {'error': str(e), 'symbol': symbol}
    
    def generate_multiple_signals(self, symbols: List[str]) -> List[Dict]:
        """Генерація сигналів для кількох пар"""
        signals = []
        for symbol in symbols:
            signal = self.generate_signal(symbol)
            if 'error' not in signal:
                signals.append(signal)
        return signals