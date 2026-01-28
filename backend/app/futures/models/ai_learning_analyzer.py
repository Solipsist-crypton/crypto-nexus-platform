# backend/modules/ai_learning_analyzer.py
import numpy as np
import pandas as pd
import talib
import json
import hashlib
import pickle
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Імпортуємо оригінальний аналізатор
from .ai_analyzer import AIAnalyzer

class AILearningAnalyzer(AIAnalyzer):
    """
    Розширений AI аналізатор з механізмом навчання.
    Успадковує всю логіку з AIAnalyzer і додає навчання.
    """
    
    def __init__(self, db_connection=None, config_file: str = None):
        # Викликаємо конструктор батьківського класу
        super().__init__()
        
        # Налаштування навчання
        self.learning_mode = True  # True = збираємо дані, False = реальні сигнали
        self.min_training_signals = 100  # Мінімум сигналів для початку навчання
        self.training_progress = 0  # Прогрес навчання 0-100
        
        # База знань (в пам'яті, можна зберігати в файл)
        self.knowledge_base = {
            'winning_patterns': [],
            'losing_patterns': [],
            'indicator_performance': defaultdict(lambda: {'wins': 0, 'losses': 0, 'total': 0}),
            'market_context_performance': defaultdict(lambda: {'wins': 0, 'losses': 0}),
            'time_based_performance': defaultdict(lambda: {'wins': 0, 'losses': 0}),
            'last_analysis_time': None
        }
        
        # Динамічні ваги (будуть коригуватись)
        self.dynamic_weights = {
            'trend': 0.30,
            'momentum': 0.25,
            'risk': 0.20,
            'volume': 0.15,
            'structure': 0.10,
        }
        
        # Підключення до БД
        self.db = db_connection
        
        # Статистика навчання
        self.learning_stats = {
            'total_signals': 0,
            'winning_signals': 0,
            'losing_signals': 0,
            'neutral_signals': 0,
            'current_accuracy': 0.0,
            'avg_profit_per_win': 0.0,
            'avg_loss_per_loss': 0.0,
            'total_profit': 0.0,
            'best_pattern': None,
            'worst_pattern': None,
            'learning_start_date': datetime.now(),
            'last_optimization': None
        }
        
        # Завантажуємо попередні навчання якщо є
        if config_file:
            self._load_knowledge_base(config_file)
    
    def generate_trading_signal_with_learning(self, symbol: str, df: pd.DataFrame, timeframe: str = '1h') -> Dict:
        """
        Генерація сигналу з врахуванням набутих знань.
        Повертає збагачений сигнал з навчальними даними.
        """
        self.logger.info(f"🎓 Генерую сигнал з навчанням для {symbol} ({timeframe})")
        
        # 1. Генеруємо базовий сигнал (з батьківського класу)
        base_signal = super().generate_trading_signal(symbol, df, timeframe)
        
        if 'error' in base_signal:
            return base_signal
        
        # 2. Аналізуємо контекст ринку для навчання
        market_context = self._analyze_learning_context(df, base_signal)
        
        # 3. Отримуємо історичну ефективність для схожих умов
        historical_performance = self._get_historical_performance(base_signal, market_context)
        
        # 4. Корегуємо впевненість на основі історії
        adjusted_confidence = self._adjust_confidence_with_history(
            base_signal['confidence'],
            historical_performance
        )
        
        # 5. Генеруємо персоналізовані рекомендації
        personalized_recommendations = self._generate_personalized_recommendations(
            base_signal,
            market_context,
            historical_performance
        )
        
        # 6. Оцінюємо якість сигналу
        signal_quality = self._assess_signal_quality(base_signal, historical_performance)
        
        # 7. Збагачуємо сигнал навчальними даними
        enhanced_signal = {
            **base_signal,
            'confidence': round(adjusted_confidence, 3),
            'learning_data': {
                'historical_performance': historical_performance,
                'market_context': market_context,
                'personalized_recommendations': personalized_recommendations,
                'learning_progress': self.training_progress,
                'signal_quality': signal_quality,
                'training_mode': self.learning_mode,
                'similar_patterns_found': historical_performance.get('similar_patterns_found', 0)
            }
        }
        
        # 8. Зберігаємо сигнал для подальшого навчання
        if self.learning_mode or signal_quality >= 0.6:
            signal_id = self._save_signal_for_learning(enhanced_signal)
            enhanced_signal['learning_signal_id'] = signal_id
        
        # 9. Оновлюємо статистику
        self._update_learning_stats(enhanced_signal)
        
        return enhanced_signal
    
    def _analyze_learning_context(self, df: pd.DataFrame, signal: Dict) -> Dict:
        """
        Аналіз контексту ринку для навчання.
        Включає час, волатильність, тренд та інші фактори.
        """
        close = df['close'].values
        
        # Часова інформація
        now = datetime.now()
        
        # Волатильність
        if len(close) > 20:
            returns = np.diff(np.log(close[-20:])) if len(close) > 1 else np.array([0])
            volatility = np.std(returns) * np.sqrt(252) * 100 if len(returns) > 0 else 0
        else:
            volatility = 0
        
        # Тренд
        if len(close) > 50:
            sma_20 = talib.SMA(close, timeperiod=20)[-1] if len(close) >= 20 else close[-1]
            sma_50 = talib.SMA(close, timeperiod=50)[-1] if len(close) >= 50 else close[-1]
            trend = "bullish" if sma_20 > sma_50 else "bearish" if sma_20 < sma_50 else "sideways"
        else:
            trend = "unknown"
        
        # Рівень ціни
        if len(close) > 100:
            high_band = np.percentile(close[-100:], 70)
            low_band = np.percentile(close[-100:], 30)
            current_price = close[-1]
            
            if current_price > high_band:
                price_level = "high"
            elif current_price < low_band:
                price_level = "low"
            else:
                price_level = "middle"
        else:
            price_level = "unknown"
        
        return {
            'timestamp': now.isoformat(),
            'hour_of_day': now.hour,
            'day_of_week': now.weekday(),
            'market_session': self._get_market_session(now),
            'volatility_pct': round(volatility, 2),
            'trend': trend,
            'price_level': price_level,
            'candle_pattern': signal.get('market_structure', {}).get('candle_pattern', 'none'),
            'structure': signal.get('price_action', {}).get('structure', 'ranging')
        }
    
    def _get_historical_performance(self, signal: Dict, market_context: Dict) -> Dict:
        """
        Отримання історичної ефективності для схожих умов.
        """
        # На початку повертаємо базові значення
        if self.learning_stats['total_signals'] < self.min_training_signals:
            return {
                'similar_patterns_found': 0,
                'win_rate': 0.5,
                'avg_profit': 0.0,
                'avg_hold_time': 0.0,
                'reliability_score': 0.5,
                'recommendation': 'insufficient_data',
                'data_quality': 'low'
            }
        
        # Шукаємо схожі паттерни в базі знань
        similar_patterns = self._find_similar_patterns(signal, market_context)
        
        if not similar_patterns:
            return {
                'similar_patterns_found': 0,
                'win_rate': 0.5,
                'avg_profit': 0.0,
                'avg_hold_time': 0.0,
                'reliability_score': 0.5,
                'recommendation': 'no_similar_patterns',
                'data_quality': 'medium'
            }
        
        # Аналізуємо результати схожих паттернів
        wins = [p for p in similar_patterns if p.get('result') == 'win']
        losses = [p for p in similar_patterns if p.get('result') == 'loss']
        
        total = len(similar_patterns)
        win_rate = len(wins) / total if total > 0 else 0
        
        avg_profit = np.mean([p.get('profit_pct', 0) for p in wins]) if wins else 0
        avg_loss = np.mean([abs(p.get('profit_pct', 0)) for p in losses]) if losses else 0
        avg_hold_time = np.mean([p.get('hold_time_hours', 0) for p in similar_patterns]) if similar_patterns else 0
        
        # Розраховуємо рейтинг надійності
        reliability_score = self._calculate_reliability_score(win_rate, avg_profit, avg_loss)
        
        # Визначаємо рекомендацію
        recommendation = self._determine_recommendation(reliability_score, total)
        
        return {
            'similar_patterns_found': total,
            'win_rate': round(win_rate, 3),
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'avg_hold_time': round(avg_hold_time, 1),
            'reliability_score': round(reliability_score, 3),
            'recommendation': recommendation,
            'data_quality': 'high' if total >= 10 else 'medium'
        }
    
    def _adjust_confidence_with_history(self, base_confidence: float, historical_performance: Dict) -> float:
        """
        Корекція впевненості на основі історичної ефективності.
        """
        if historical_performance['similar_patterns_found'] == 0:
            # Немає даних для корекції
            return base_confidence
        
        reliability = historical_performance['reliability_score']
        data_quality = historical_performance.get('data_quality', 'low')
        
        # Коефіцієнт довіри до даних
        data_trust_factor = {
            'low': 0.3,
            'medium': 0.7,
            'high': 0.9
        }.get(data_quality, 0.5)
        
        # Корекція впевненості
        if reliability > 0.7:
            # Підвищуємо впевненість для надійних паттернів
            adjusted = base_confidence * (1 + (reliability - 0.7) * 0.5 * data_trust_factor)
        elif reliability < 0.4:
            # Знижуємо впевненість для ненадійних паттернів
            adjusted = base_confidence * (0.5 + reliability * data_trust_factor)
        else:
            # Незначна корекція
            adjusted = base_confidence * (0.9 + reliability * 0.1 * data_trust_factor)
        
        return min(1.0, max(0.0, adjusted))
    
    def _generate_personalized_recommendations(self, signal: Dict, market_context: Dict, 
                                              historical_performance: Dict) -> Dict:
        """
        Генерація персоналізованих рекомендацій на основі історії.
        """
        recommendations = {
            'entry_strategy': 'standard_limit',
            'position_size_multiplier': 1.0,
            'take_profit_adjustment': 0.0,
            'stop_loss_adjustment': 0.0,
            'holding_time': 'medium',
            'risk_level': 'medium',
            'scaling_recommendation': 'standard',
            'time_sensitivity': 'normal'
        }
        
        # Аналізуємо історичну ефективність
        if historical_performance['similar_patterns_found'] > 0:
            win_rate = historical_performance['win_rate']
            avg_hold_time = historical_performance['avg_hold_time']
            reliability = historical_performance['reliability_score']
            
            # Корекція розміру позиції
            if win_rate > 0.7 and reliability > 0.6:
                recommendations['position_size_multiplier'] = 1.2
                recommendations['risk_level'] = 'low'
            elif win_rate < 0.4 or reliability < 0.4:
                recommendations['position_size_multiplier'] = 0.7
                recommendations['risk_level'] = 'high'
            
            # Корекція часу утримання
            if avg_hold_time < 4:
                recommendations['holding_time'] = 'short_term'
                recommendations['time_sensitivity'] = 'high'
            elif avg_hold_time > 24:
                recommendations['holding_time'] = 'long_term'
                recommendations['time_sensitivity'] = 'low'
        
        # Корекція на основі контексту ринку
        if market_context['volatility_pct'] > 50:
            recommendations['stop_loss_adjustment'] = 0.2  # Збільшуємо стоп на 20%
            recommendations['risk_level'] = 'high'
        elif market_context['volatility_pct'] < 20:
            recommendations['take_profit_adjustment'] = -0.1  # Зменшуємо тейк на 10%
            recommendations['entry_strategy'] = 'aggressive_limit'
        
        # Корекція на основі часу доби
        hour = market_context['hour_of_day']
        if hour >= 22 or hour < 4:  # Ніч
            recommendations['time_sensitivity'] = 'very_low'
            recommendations['entry_strategy'] = 'patient_limit'
        
        return recommendations
    
    def _assess_signal_quality(self, signal: Dict, historical_performance: Dict) -> float:
        """
        Оцінка якості сигналу (0.0 - 1.0).
        """
        quality_score = signal['confidence']
        
        # Корекція на основі історичної ефективності
        if historical_performance['similar_patterns_found'] > 5:
            reliability = historical_performance['reliability_score']
            data_quality = historical_performance.get('data_quality', 'low')
            
            data_weight = {
                'low': 0.2,
                'medium': 0.5,
                'high': 0.8
            }.get(data_quality, 0.3)
            
            # Змішуємо поточну впевненість з історичною надійністю
            quality_score = (quality_score * (1 - data_weight)) + (reliability * data_weight)
        
        # Корекція на основі конфліктів
        conflict_score = signal.get('conflict_score', 0.5)
        quality_score *= (1 - conflict_score * 0.3)
        
        # Корекція на основі R/R
        risk_reward = signal.get('risk_reward', 1.0)
        if risk_reward >= 3:
            quality_score *= 1.15
        elif risk_reward >= 2.5:
            quality_score *= 1.1
        elif risk_reward >= 2:
            quality_score *= 1.05
        
        return round(min(1.0, max(0.1, quality_score)), 3)
    
    def _save_signal_for_learning(self, signal: Dict) -> str:
        """
        Збереження сигналу для подальшого навчання.
        """
        try:
            # Створюємо унікальний ID
            signal_id = hashlib.md5(
                f"{signal['symbol']}_{signal['timestamp']}_{signal['direction']}".encode()
            ).hexdigest()[:12]
            
            # Готуємо запис для навчання
            learning_record = {
                'signal_id': signal_id,
                'symbol': signal['symbol'],
                'direction': signal['direction'],
                'timestamp': signal['timestamp'],
                'timeframe': signal.get('timeframe', '1h'),
                
                # Показання індикаторів
                'indicators_summary': signal.get('indicators_summary', {}),
                'factors': signal.get('factors', {}),
                
                # Контекст
                'market_context': signal['learning_data']['market_context'],
                'confidence': signal['confidence'],
                'signal_quality': signal['learning_data']['signal_quality'],
                
                # Для заповнення після угоди
                'result': None,
                'profit_pct': None,
                'hold_time_hours': None,
                'max_drawdown': None,
                'exit_timestamp': None,
                'exit_reason': None,
                'learning_notes': None,
                'status': 'pending'
            }
            
            # Додаємо в базу знань
            self.knowledge_base.setdefault('pending_signals', {})[signal_id] = learning_record
            
            self.logger.info(f"💾 Сигнал {signal_id} збережено для навчання")
            return signal_id
            
        except Exception as e:
            self.logger.error(f"Помилка збереження сигналу для навчання: {str(e)}")
            return f"error_{hash(str(e))[:8]}"
    
    def update_signal_result(self, signal_id: str, result_data: Dict):
        """
        Оновлення результату сигналу після закриття угоди.
        """
        try:
            # Знаходимо сигнал в очікуючих
            pending_signals = self.knowledge_base.get('pending_signals', {})
            if signal_id not in pending_signals:
                self.logger.warning(f"Сигнал {signal_id} не знайдено в очікуючих")
                return
            
            signal_record = pending_signals[signal_id]
            
            # Оновлюємо результат
            signal_record.update({
                'result': result_data.get('result'),  # 'win', 'loss', 'break_even'
                'profit_pct': result_data.get('profit_pct', 0.0),
                'hold_time_hours': result_data.get('hold_time_hours', 0),
                'max_drawdown': result_data.get('max_drawdown', 0.0),
                'exit_timestamp': result_data.get('exit_timestamp', datetime.now().isoformat()),
                'exit_reason': result_data.get('exit_reason', 'unknown'),
                'learning_notes': self._generate_learning_notes(result_data, signal_record),
                'status': 'completed'
            })
            
            # Переміщуємо в відповідну категорію
            del pending_signals[signal_id]
            
            if signal_record['result'] == 'win':
                self.knowledge_base['winning_patterns'].append(signal_record)
            else:
                self.knowledge_base['losing_patterns'].append(signal_record)
            
            # Оновлюємо статистику індикаторів
            self._update_indicator_performance(signal_record)
            
            # Оновлюємо загальну статистику
            self._update_learning_stats_from_result(signal_record)
            
            # Кожні 50 сигналів проводимо оптимізацію
            if self.learning_stats['total_signals'] % 50 == 0:
                self._optimize_weights()
                self._save_knowledge_base('knowledge_base_backup.pkl')
            
            self.logger.info(f"📊 Результат сигналу {signal_id}: {signal_record['result']} "
                           f"({signal_record['profit_pct']:.2f}%)")
            
        except Exception as e:
            self.logger.error(f"Помилка оновлення результату: {str(e)}")
    
    def _find_similar_patterns(self, signal: Dict, market_context: Dict) -> List[Dict]:
        """
        Пошук схожих паттернів в базі знань.
        """
        similar_patterns = []
        
        # Перевіряємо виграшні паттерни
        for pattern in self.knowledge_base['winning_patterns']:
            if self._patterns_are_similar(signal, pattern, market_context):
                similar_patterns.append(pattern)
        
        # Перевіряємо програшні паттерни
        for pattern in self.knowledge_base['losing_patterns']:
            if self._patterns_are_similar(signal, pattern, market_context):
                similar_patterns.append(pattern)
        
        return similar_patterns
    
    def _patterns_are_similar(self, signal1: Dict, signal2: Dict, context: Dict) -> bool:
        """
        Порівняння двох паттернів на схожість.
        """
        # Порівнюємо основні параметри
        if signal1['direction'] != signal2['direction']:
            return False
        
        # Порівнюємо RSI (з допуском ±5)
        rsi1 = signal1.get('indicators_summary', {}).get('rsi', 50)
        rsi2 = signal2.get('indicators_summary', {}).get('rsi', 50)
        if abs(rsi1 - rsi2) > 10:
            return False
        
        # Порівнюємо MACD сигнал
        macd1 = signal1.get('indicators_summary', {}).get('macd_hist', 0)
        macd2 = signal2.get('indicators_summary', {}).get('macd_hist', 0)
        if (macd1 > 0 and macd2 < 0) or (macd1 < 0 and macd2 > 0):
            return False
        
        # Порівнюємо контекст (час доби, день тижня)
        context1 = context
        context2 = signal2.get('market_context', {})
        
        if context1.get('hour_of_day', 0) // 6 != context2.get('hour_of_day', 0) // 6:
            return False  # Різні періоди доби
        
        if context1.get('day_of_week', 0) != context2.get('day_of_week', 0):
            return False  # Різні дні тижня
        
        return True
    
    def _calculate_reliability_score(self, win_rate: float, avg_profit: float, avg_loss: float) -> float:
        """
        Розрахунок рейтингу надійності паттерну.
        """
        if avg_loss == 0:
            return win_rate
        
        # Формула: win_rate * (1 + profit/loss ratio) * (1 - consistency penalty)
        profit_loss_ratio = avg_profit / avg_loss if avg_loss > 0 else 1.0
        
        # Штраф за неконсистентність
        consistency = min(1.0, (avg_profit + avg_loss) / max(avg_profit, avg_loss))
        consistency_penalty = 0.1 * (1 - consistency)
        
        reliability = win_rate * (1 + profit_loss_ratio * 0.5) * (1 - consistency_penalty)
        
        return min(1.0, max(0.0, reliability))
    
    def _determine_recommendation(self, reliability_score: float, sample_size: int) -> str:
        """
        Визначення рекомендації на основі надійності.
        """
        if sample_size < 5:
            return 'insufficient_data'
        
        if reliability_score >= 0.75:
            return 'high_confidence'
        elif reliability_score >= 0.60:
            return 'medium_confidence'
        elif reliability_score >= 0.45:
            return 'low_confidence'
        else:
            return 'avoid'
    
    def _update_indicator_performance(self, signal_record: Dict):
        """
        Оновлення статистики індикаторів.
        """
        factors = signal_record.get('factors', {})
        result = signal_record.get('result')
        
        if not result:
            return
        
        for indicator, value in factors.items():
            if isinstance(value, (int, float)):
                # Оновлюємо статистику для цього індикатора
                perf = self.knowledge_base['indicator_performance'][indicator]
                perf['total'] += 1
                
                if result == 'win':
                    perf['wins'] += 1
                else:
                    perf['losses'] += 1
    
    def _update_learning_stats(self, signal: Dict):
        """
        Оновлення статистики навчання.
        """
        self.learning_stats['total_signals'] += 1
        
        if signal['direction'] == 'neutral':
            self.learning_stats['neutral_signals'] += 1
        
        # Оновлюємо прогрес навчання
        total_needed = self.min_training_signals * 2  # Повний цикл навчання
        progress = min(100, (self.learning_stats['total_signals'] / total_needed) * 100)
        self.training_progress = round(progress, 1)
    
    def _update_learning_stats_from_result(self, signal_record: Dict):
        """
        Оновлення статистики з результату угоди.
        """
        result = signal_record.get('result')
        profit_pct = signal_record.get('profit_pct', 0.0)
        
        if result == 'win':
            self.learning_stats['winning_signals'] += 1
            self.learning_stats['total_profit'] += profit_pct
            
            # Оновлюємо середній прибуток
            wins = self.learning_stats['winning_signals']
            current_avg = self.learning_stats['avg_profit_per_win']
            self.learning_stats['avg_profit_per_win'] = (
                (current_avg * (wins - 1) + profit_pct) / wins
            )
            
        elif result == 'loss':
            self.learning_stats['losing_signals'] += 1
            
            # Оновлюємо середній збиток
            losses = self.learning_stats['losing_signals']
            current_avg = self.learning_stats['avg_loss_per_loss']
            self.learning_stats['avg_loss_per_loss'] = (
                (current_avg * (losses - 1) + abs(profit_pct)) / losses
            )
        
        # Оновлюємо точність
        total_completed = self.learning_stats['winning_signals'] + self.learning_stats['losing_signals']
        if total_completed > 0:
            self.learning_stats['current_accuracy'] = (
                self.learning_stats['winning_signals'] / total_completed
            )
    
    def _optimize_weights(self):
        """
        Оптимізація ваг індикаторів на основі статистики.
        """
        self.logger.info("🔧 Запуск оптимізації ваг індикаторів...")
        
        # Аналізуємо ефективність індикаторів
        indicator_performance = self.knowledge_base['indicator_performance']
        
        # Створюємо нові ваги на основі статистики
        new_weights = {}
        total_efficiency = 0
        
        for indicator, perf in indicator_performance.items():
            if perf['total'] >= 10:  # Тільки для індикаторів з достатньою статистикою
                win_rate = perf['wins'] / perf['total'] if perf['total'] > 0 else 0.5
                
                # Ефективність індикатора
                efficiency = abs(win_rate - 0.5) * 2  # 0.0-1.0, де 1.0 = ідеальний
                
                new_weights[indicator] = efficiency
                total_efficiency += efficiency
        
        # Нормалізуємо ваги
        if total_efficiency > 0:
            for indicator in new_weights:
                new_weights[indicator] /= total_efficiency
            
            # Застосовуємо нові ваги (поступово)
            for category in self.dynamic_weights:
                if category in new_weights:
                    # Плавна корекція (10% за раз)
                    old_weight = self.dynamic_weights[category]
                    target_weight = new_weights[category]
                    self.dynamic_weights[category] = old_weight * 0.9 + target_weight * 0.1
        
        self.learning_stats['last_optimization'] = datetime.now()
        self.logger.info(f"✅ Ваги оновлено: {self.dynamic_weights}")
    
    def _generate_learning_notes(self, result_data: Dict, signal_record: Dict) -> str:
        """
        Генерація нотаток для навчання.
        """
        result = result_data.get('result', 'unknown')
        profit_pct = result_data.get('profit_pct', 0.0)
        hold_time = result_data.get('hold_time_hours', 0)
        
        notes = []
        
        if result == 'win':
            if profit_pct > signal_record.get('expected_pnl_percent', 2.0) * 1.5:
                notes.append("Значно перевищив очікування")
            elif profit_pct < signal_record.get('expected_pnl_percent', 2.0) * 0.5:
                notes.append("Менше очікуваного, можливо ранній вихід")
            
            if hold_time < 4:
                notes.append("Швидкий прибуток")
            elif hold_time > 12:
                notes.append("Довге утримання")
        
        elif result == 'loss':
            if abs(profit_pct) > signal_record.get('position_size', {}).get('size_percent', 2.0):
                notes.append("Великий збиток - переглянути стопи")
            else:
                notes.append("Контрольований збиток")
        
        # Аналіз контексту
        context = signal_record.get('market_context', {})
        if context.get('volatility_pct', 0) > 50:
            notes.append("Висока волатильність")
        
        return "; ".join(notes) if notes else "Стандартний результат"
    
    def _get_market_session(self, dt: datetime) -> str:
        """
        Визначення торгової сесії за часом.
        """
        hour = dt.hour
        
        if 0 <= hour < 8:
            return "asia"
        elif 8 <= hour < 16:
            return "europe"
        elif 16 <= hour < 24:
            return "us"
        else:
            return "asia"
    
    def _save_knowledge_base(self, filename: str):
        """
        Збереження бази знань у файл.
        """
        try:
            with open(filename, 'wb') as f:
                pickle.dump({
                    'knowledge_base': self.knowledge_base,
                    'learning_stats': self.learning_stats,
                    'dynamic_weights': self.dynamic_weights,
                    'training_progress': self.training_progress,
                    'save_timestamp': datetime.now().isoformat()
                }, f)
            self.logger.info(f"💾 База знань збережена в {filename}")
        except Exception as e:
            self.logger.error(f"Помилка збереження бази знань: {str(e)}")
    
    def _load_knowledge_base(self, filename: str):
        """
        Завантаження бази знань з файлу.
        """
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                
            self.knowledge_base = data.get('knowledge_base', self.knowledge_base)
            self.learning_stats = data.get('learning_stats', self.learning_stats)
            self.dynamic_weights = data.get('dynamic_weights', self.dynamic_weights)
            self.training_progress = data.get('training_progress', 0)
            
            self.logger.info(f"📂 База знань завантажена з {filename}")
            self.logger.info(f"📊 Статистика: {self.learning_stats['total_signals']} сигналів, "
                           f"точність: {self.learning_stats['current_accuracy']:.1%}")
            
        except FileNotFoundError:
            self.logger.info("📂 Файл бази знань не знайдено, починаємо з нуля")
        except Exception as e:
            self.logger.error(f"Помилка завантаження бази знань: {str(e)}")
    
    def get_learning_report(self) -> Dict:
        """
        Отримання звіту про навчання.
        """
        total_completed = self.learning_stats['winning_signals'] + self.learning_stats['losing_signals']
        
        return {
            'learning_mode': self.learning_mode,
            'training_progress': self.training_progress,
            'total_signals': self.learning_stats['total_signals'],
            'completed_signals': total_completed,
            'winning_signals': self.learning_stats['winning_signals'],
            'losing_signals': self.learning_stats['losing_signals'],
            'neutral_signals': self.learning_stats['neutral_signals'],
            'current_accuracy': round(self.learning_stats['current_accuracy'], 3),
            'avg_profit_per_win': round(self.learning_stats['avg_profit_per_win'], 2),
            'avg_loss_per_loss': round(self.learning_stats['avg_loss_per_loss'], 2),
            'total_profit': round(self.learning_stats['total_profit'], 2),
            'dynamic_weights': self.dynamic_weights,
            'knowledge_base_size': {
                'winning_patterns': len(self.knowledge_base['winning_patterns']),
                'losing_patterns': len(self.knowledge_base['losing_patterns']),
                'indicator_performance': len(self.knowledge_base['indicator_performance']),
                'pending_signals': len(self.knowledge_base.get('pending_signals', {}))
            },
            'learning_start_date': self.learning_stats['learning_start_date'].isoformat(),
            'days_learning': (datetime.now() - self.learning_stats['learning_start_date']).days,
            'last_optimization': self.learning_stats['last_optimization'].isoformat() 
                if self.learning_stats['last_optimization'] else None,
            'recommendation': self._get_training_recommendation()
        }
    
    def _get_training_recommendation(self) -> str:
        """
        Отримання рекомендації щодо навчання.
        """
        if self.training_progress < 30:
            return "Продовжуйте збір даних (фаза накопичення)"
        elif self.training_progress < 70:
            return "Достатньо даних, починайте аналіз паттернів"
        elif self.training_progress < 90:
            return "Оптимізація ваг, підготовка до реальної торгівлі"
        else:
            return "Готово до реальної торгівлі"
    
    def enable_real_trading(self, min_accuracy: float = 0.6, min_signals: int = 100):
        """
        Увімкнути режим реальної торгівлі.
        """
        if self.learning_stats['total_signals'] < min_signals:
            return {
                'success': False,
                'message': f"Недостатньо сигналів. Потрібно {min_signals}, маємо {self.learning_stats['total_signals']}",
                'required': min_signals,
                'current': self.learning_stats['total_signals']
            }
        
        total_completed = self.learning_stats['winning_signals'] + self.learning_stats['losing_signals']
        if total_completed == 0:
            return {
                'success': False,
                'message': "Немає завершених угод для аналізу",
                'completed_signals': total_completed
            }
        
        accuracy = self.learning_stats['current_accuracy']
        if accuracy < min_accuracy:
            return {
                'success': False,
                'message': f"Точність ({accuracy:.1%}) нижча за мінімальну ({min_accuracy:.1%})",
                'accuracy': accuracy,
                'required_accuracy': min_accuracy
            }
        
        # Увімкнути реальну торгівлю
        self.learning_mode = False
        
        return {
            'success': True,
            'message': "🚀 Увімкнено режим реальної торгівлі!",
            'stats': {
                'total_signals': self.learning_stats['total_signals'],
                'accuracy': accuracy,
                'avg_profit': self.learning_stats['avg_profit_per_win'],
                'avg_loss': self.learning_stats['avg_loss_per_loss']
            }
        }


# ===== ТЕСТУВАННЯ =====
def test_learning_analyzer():
    """Тестування нового аналізатора"""
    print("🧪 ТЕСТУВАННЯ AI АНАЛІЗАТОРА З НАВЧАННЯМ")
    print("=" * 60)
    
    # Створюємо аналізатор
    analyzer = AILearningAnalyzer()
    
    # Отримуємо початковий статус
    report = analyzer.get_learning_report()
    
    print(f"\n🏁 ПОЧАТКОВИЙ СТАТУС:")
    print(f"   • Режим: {'НАВЧАННЯ' if report['learning_mode'] else 'ТОРГІВЛЯ'}")
    print(f"   • Прогрес: {report['training_progress']}%")
    print(f"   • Сигналів: {report['total_signals']}")
    print(f"   • Точність: {report['current_accuracy']:.1%}")
    
    # Створюємо тестові дані
    print(f"\n📊 СТВОРЕННЯ ТЕСТОВИХ ДАНИХ...")
    
    # Генеруємо прості детерміновані дані
    num_points = 200
    dates = pd.date_range(start='2024-01-01', periods=num_points, freq='H')
    
    # Детермінована цінова крива
    t = np.arange(num_points)
    close = 100 + 0.1 * t + 5 * np.sin(2 * np.pi * t / 50)
    high = close + 1 + 0.5 * np.sin(2 * np.pi * t / 25)
    low = close - 1 - 0.5 * np.cos(2 * np.pi * t / 25)
    open_price = np.roll(close, 1)
    open_price[0] = 99.5
    
    df = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': np.full(num_points, 1000)
    }, index=dates)
    
    print(f"   • Період: {df.index[0]} - {df.index[-1]}")
    print(f"   • Свічок: {len(df)}")
    print(f"   • Close: {df['close'].iloc[-1]:.2f}")
    
    # Тест генерації сигналу
    print(f"\n📈 ТЕСТ ГЕНЕРАЦІЇ СИГНАЛУ...")
    
    signal = analyzer.generate_trading_signal_with_learning('BTC/USDT', df, '1h')
    
    print(f"   • Символ: {signal['symbol']}")
    print(f"   • Напрямок: {signal['direction'].upper()}")
    print(f"   • Впевненість: {signal['confidence']:.1%}")
    print(f"   • Якість: {signal['learning_data']['signal_quality']:.1%}")
    
    if 'learning_signal_id' in signal:
        print(f"   • ID для навчання: {signal['learning_signal_id']}")
        
        # Імітуємо результат
        print(f"\n🎮 ІМІТАЦІЯ РЕЗУЛЬТАТУ УГОДИ...")
        
        # Простий детермінований результат
        if signal['direction'] == 'long':
            result = 'win' if np.random.random() > 0.3 else 'loss'
        else:
            result = 'win' if np.random.random() > 0.4 else 'loss'
        
        profit = 2.5 if result == 'win' else -1.8
        
        result_data = {
            'result': result,
            'profit_pct': profit,
            'hold_time_hours': 6,
            'max_drawdown': abs(profit) * 0.3,
            'exit_timestamp': datetime.now().isoformat(),
            'exit_reason': 'target_hit' if result == 'win' else 'stop_loss'
        }
        
        analyzer.update_signal_result(signal['learning_signal_id'], result_data)
        print(f"   • Результат: {result.upper()} ({profit:+.2f}%)")
    
    # Оновлений звіт
    print(f"\n📊 ОНОВЛЕНИЙ ЗВІТ:")
    updated_report = analyzer.get_learning_report()
    
    print(f"   • Сигналів: {updated_report['total_signals']}")
    print(f"   • Перемог: {updated_report['winning_signals']}")
    print(f"   • Поразок: {updated_report['losing_signals']}")
    print(f"   • Точність: {updated_report['current_accuracy']:.1%}")
    print(f"   • Прогрес: {updated_report['training_progress']}%")
    print(f"   • Рекомендація: {updated_report['recommendation']}")
    
    return analyzer

if __name__ == "__main__":
    # Запускаємо тест
    analyzer = test_learning_analyzer()