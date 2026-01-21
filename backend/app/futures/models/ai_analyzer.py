# backend/modules/ai_analyzer.py
import numpy as np
import pandas as pd
import talib
from typing import Dict, List, Tuple, Any
import logging

class AIAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Розрахунок технічних індикаторів"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        open_price = df['open'].values
        volume = df['volume'].values
        
        # Отримання індикаторів окремо
        ema_20 = talib.EMA(close, timeperiod=20)
        ema_50 = talib.EMA(close, timeperiod=50)
        ema_200 = talib.EMA(close, timeperiod=200)
        sma_20 = talib.SMA(close, timeperiod=20)
        adx = talib.ADX(high, low, close, timeperiod=14)
        rsi = talib.RSI(close, timeperiod=14)
        
        # STOCH повертає два масиви
        stoch_k, stoch_d = talib.STOCH(high, low, close)
        
        # MACD повертає три масиви
        macd, macd_signal, macd_hist = talib.MACD(close)
        
        # BBANDS повертає три масиви
        bb_upper, bb_middle, bb_lower = talib.BBANDS(close)
        
        atr = talib.ATR(high, low, close, timeperiod=14)
        obv = talib.OBV(close, volume)
        
        # Свечні паттерни
        doji = talib.CDLDOJI(open_price, high, low, close)
        hammer = talib.CDLHAMMER(open_price, high, low, close)
        engulfing = talib.CDLENGULFING(open_price, high, low, close)
        
        indicators = {
            # Трендові індикатори
            'ema_20': ema_20,
            'ema_50': ema_50,
            'ema_200': ema_200,
            'sma_20': sma_20,
            'adx': adx,
            
            # Осцилятори
            'rsi': rsi,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d,
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_hist': macd_hist,
            
            # Волатильність
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'atr': atr,
            
            # Обсяги
            'obv': obv,
            
            # Свечні паттерни
            'doji': doji,
            'hammer': hammer,
            'engulfing': engulfing,
        }
        
        return indicators
    
    def find_support_levels(self, df: pd.DataFrame, window: int = 20) -> List[float]:
        """Знаходження рівнів підтримки (локальні мінімуми)"""
        support_levels = []
        close_prices = df['close'].values
        
        for i in range(window, len(close_prices) - window):
            local_min = np.min(close_prices[i-window:i+window+1])
            if close_prices[i] == local_min:
                support_levels.append(close_prices[i])
        
        # Повертаємо унікальні значення, відсортовані
        return sorted(list(set([round(level, 2) for level in support_levels[-5:]])))
    
    def find_resistance_levels(self, df: pd.DataFrame, window: int = 20) -> List[float]:
        """Знаходження рівнів опору (локальні максимуми)"""
        resistance_levels = []
        close_prices = df['close'].values
        
        for i in range(window, len(close_prices) - window):
            local_max = np.max(close_prices[i-window:i+window+1])
            if close_prices[i] == local_max:
                resistance_levels.append(close_prices[i])
        
        # Повертаємо унікальні значення, відсортовані
        return sorted(list(set([round(level, 2) for level in resistance_levels[-5:]])))
    
    def analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """Аналіз структури ринку"""
        close = df['close'].values
        
        if len(close) < 20:
            return {
                'trend': 'neutral',
                'market_structure': 'unknown',
                'support_levels': [],
                'resistance_levels': []
            }
        
        # Визначення ВНР (Higher Highs / Lower Lows)
        hh = np.all(close[-5:] > close[-10:-5]) if len(close) >= 10 else False
        ll = np.all(close[-5:] < close[-10:-5]) if len(close) >= 10 else False
        
        # Перевірка наявності EMA у DataFrame
        if 'ema_50' not in df.columns or 'ema_200' not in df.columns:
            # Розрахуємо EMA, якщо їх немає
            df['ema_50'] = talib.EMA(df['close'].values, timeperiod=50)
            df['ema_200'] = talib.EMA(df['close'].values, timeperiod=200)
        
        # Визначення тренду
        trend_up = (close[-1] > df['ema_50'].iloc[-1] > df['ema_200'].iloc[-1]) 
        trend_down = (close[-1] < df['ema_50'].iloc[-1] < df['ema_200'].iloc[-1])
        
        return {
            'trend': 'bullish' if trend_up else 'bearish' if trend_down else 'range',
            'market_structure': 'uptrend' if hh else 'downtrend' if ll else 'consolidation',
            'support_levels': self.find_support_levels(df),
            'resistance_levels': self.find_resistance_levels(df),
        }
    
    def generate_signal(self, symbol: str, df: pd.DataFrame, indicators: Dict) -> Dict:
        """Генерація торгового сигналу на основі реальних даних"""
        if len(df) < 50:
            return {
                'symbol': symbol,
                'direction': 'neutral',
                'confidence': 0.0,
                'entry_price': 0.0,
                'take_profit': 0.0,
                'stop_loss': 0.0,
                'timestamp': pd.Timestamp.now(),
                'factors': [],
                'indicators': {},
                'error': 'Insufficient data'
            }
        
        # Конфлігентність індикаторів
        confidence_factors = []
        close_prices = df['close'].values
        current_price = close_prices[-1]
        
        # Додаємо EMA до DataFrame якщо ще немає
        if 'ema_20' not in df.columns:
            df['ema_20'] = indicators.get('ema_20', talib.EMA(close_prices, timeperiod=20))
        if 'ema_50' not in df.columns:
            df['ema_50'] = indicators.get('ema_50', talib.EMA(close_prices, timeperiod=50))
        if 'ema_200' not in df.columns:
            df['ema_200'] = indicators.get('ema_200', talib.EMA(close_prices, timeperiod=200))
        
        # 1. Тренд (вага 30%)
        ema_20_current = df['ema_20'].iloc[-1] if not df['ema_20'].isna().iloc[-1] else current_price
        ema_50_current = df['ema_50'].iloc[-1] if not df['ema_50'].isna().iloc[-1] else current_price
        ema_200_current = df['ema_200'].iloc[-1] if not df['ema_200'].isna().iloc[-1] else current_price
        
        if ema_20_current > ema_50_current > ema_200_current:
            trend_score = 1.0
            direction = 'long'
        elif ema_20_current < ema_50_current < ema_200_current:
            trend_score = 1.0
            direction = 'short'
        else:
            trend_score = 0.3
            direction = 'neutral'
        
        confidence_factors.append(('trend', trend_score, 0.3))
        
        # 2. RSI (вага 20%)
        rsi_values = indicators.get('rsi', [])
        rsi_current = rsi_values[-1] if len(rsi_values) > 0 else 50
        
        if direction == 'long' and rsi_current < 40:
            rsi_score = 1.0
        elif direction == 'short' and rsi_current > 60:
            rsi_score = 1.0
        elif 40 <= rsi_current <= 60:
            rsi_score = 0.5
        else:
            rsi_score = 0.2
        
        confidence_factors.append(('rsi', rsi_score, 0.2))
        
        # 3. MACD (вага 25%)
        macd_hist_values = indicators.get('macd_hist', [])
        macd_hist_current = macd_hist_values[-1] if len(macd_hist_values) > 0 else 0
        
        if direction == 'long' and macd_hist_current > 0:
            macd_score = 1.0
        elif direction == 'short' and macd_hist_current < 0:
            macd_score = 1.0
        else:
            macd_score = 0.3
        
        confidence_factors.append(('macd', macd_score, 0.25))
        
        # 4. Обсяги (вага 15%)
        volume_values = df['volume'].values
        current_volume = volume_values[-1]
        
        if len(volume_values) >= 20:
            avg_volume = np.mean(volume_values[-20:])
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        else:
            volume_ratio = 1.0
            
        if volume_ratio > 1.2:
            volume_score = 1.0
        elif volume_ratio > 0.8:
            volume_score = 0.6
        else:
            volume_score = 0.3
        
        confidence_factors.append(('volume', volume_score, 0.15))
        
        # 5. Волатильність (вага 10%)
        atr_values = indicators.get('atr', [])
        atr_current = atr_values[-1] if len(atr_values) > 0 else 0
        
        if current_price > 0:
            atr_percent = (atr_current / current_price) * 100
        else:
            atr_percent = 0
            
        if 1 < atr_percent < 5:  # Оптимальна волатильність для трейдингу
            volatility_score = 1.0
        else:
            volatility_score = 0.4
        
        confidence_factors.append(('volatility', volatility_score, 0.1))
        
        # Розрахунок загальної впевненості
        total_confidence = sum(score * weight for _, score, weight in confidence_factors)
        
        # Розрахунок TP/SL на основі ATR
        if atr_current > 0:
            if direction == 'long':
                take_profit = current_price + (atr_current * 3)  # TP: 3 ATR
                stop_loss = current_price - (atr_current * 1.5)  # SL: 1.5 ATR
            elif direction == 'short':
                take_profit = current_price - (atr_current * 3)
                stop_loss = current_price + (atr_current * 1.5)
            else:
                take_profit = current_price
                stop_loss = current_price
        else:
            # Якщо ATR не розраховано, використовуємо процентні значення
            if direction == 'long':
                take_profit = current_price * 1.03  # 3%
                stop_loss = current_price * 0.985  # 1.5%
            elif direction == 'short':
                take_profit = current_price * 0.97  # 3%
                stop_loss = current_price * 1.015  # 1.5%
            else:
                take_profit = current_price
                stop_loss = current_price
        
        # Перевірка на нейтральний сигнал
        if direction == 'neutral' or total_confidence < 0.5:
            direction = 'neutral'
            take_profit = current_price
            stop_loss = current_price
        
        return {
            'symbol': symbol,
            'direction': direction,
            'confidence': round(min(total_confidence, 1.0), 2),  # Обмежуємо до 1.0
            'entry_price': round(float(current_price), 4),
            'take_profit': round(float(take_profit), 4),
            'stop_loss': round(float(stop_loss), 4),
            'timestamp': pd.Timestamp.now(),
            'factors': confidence_factors,
            'indicators': {
                'rsi': round(float(rsi_current), 2),
                'macd_hist': round(float(macd_hist_current), 4),
                'atr_percent': round(float(atr_percent), 2),
                'volume_ratio': round(float(volume_ratio), 2),
                'ema_20': round(float(ema_20_current), 4),
                'ema_50': round(float(ema_50_current), 4),
                'ema_200': round(float(ema_200_current), 4)
            }
        }