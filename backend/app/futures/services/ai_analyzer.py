# backend/app/futures/services/ai_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import logging
from app.futures.models.exchange_connector import ExchangeConnector

class AIAnalyzer:
    """Справжній AI аналіз ринкових даних з технічними індикаторами"""
    
    def __init__(self):
        self.exchange = ExchangeConnector()
        self.logger = logging.getLogger(__name__)
        
    def analyze_market(self, symbol: str, timeframe: str = "1h") -> Dict:
        """
        Реальний аналіз ринкових даних з технічними індикаторами
        
        Повертає: {
            "direction": "long"/"short"/"neutral",
            "confidence": 0.0-1.0,
            "factors": {...},
            "entry_price": float,
            "take_profit": float,
            "stop_loss": float
        }
        """
        try:
            # 1. Отримуємо реальні дані з біржі
            df = self.exchange.fetch_ohlcv(symbol, timeframe, limit=200)
            if len(df) < 50:
                return self._get_fallback_signal(symbol)
            
            # 2. Розраховуємо технічні індикатори
            indicators = self._calculate_technical_indicators(df)
            
            # 3. Аналізуємо тренд та структуру ринку
            trend_analysis = self._analyze_trend(df, indicators)
            
            # 4. Приймаємо торгове рішення
            signal = self._make_trading_decision(df, indicators, trend_analysis)
            
            # 5. Додаємо symbol та timeframe
            signal['symbol'] = symbol
            signal['timeframe'] = timeframe
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Помилка аналізу {symbol}: {e}")
            return self._get_fallback_signal(symbol)
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Розрахунок реальних технічних індикаторів"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        # Прості ковзні середні
        sma_20 = self._calculate_sma(close, 20)
        sma_50 = self._calculate_sma(close, 50)
        sma_200 = self._calculate_sma(close, 200)
        
        # Експоненційні ковзні середні
        ema_12 = self._calculate_ema(close, 12)
        ema_26 = self._calculate_ema(close, 26)
        
        # RSI (Relative Strength Index)
        rsi = self._calculate_rsi(close, 14)
        
        # MACD
        macd, macd_signal, macd_histogram = self._calculate_macd(close)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close, 20, 2)
        
        # ATR (Average True Range) для волатильності
        atr = self._calculate_atr(high, low, close, 14)
        
        # Об'ємний аналіз
        volume_sma = self._calculate_sma(volume, 20)
        volume_ratio = volume[-1] / volume_sma[-1] if volume_sma[-1] > 0 else 1
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'sma_200': sma_200,
            'ema_12': ema_12,
            'ema_26': ema_26,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_histogram': macd_histogram,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'atr': atr,
            'volume_ratio': volume_ratio,
            'current_price': close[-1]
        }
    
    def _analyze_trend(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """Аналіз тренду та структури ринку"""
        close = df['close'].values
        current_price = close[-1]
        
        # Аналіз ковзних середніх
        sma_trend = self._analyze_moving_averages_trend(indicators)
        
        # Аналіз RSI
        rsi_signal = self._analyze_rsi(indicators['rsi'][-1])
        
        # Аналіз MACD
        macd_signal = self._analyze_macd(
            indicators['macd_histogram'][-1],
            indicators['macd'][-1],
            indicators['macd_signal'][-1]
        )
        
        # Аналіз ціни відносно Bollinger Bands
        bb_signal = self._analyze_bollinger_bands(
            current_price,
            indicators['bb_upper'][-1],
            indicators['bb_middle'][-1],
            indicators['bb_lower'][-1]
        )
        
        # Аналіз об'ємів
        volume_signal = self._analyze_volume(indicators['volume_ratio'])
        
        return {
            'sma_trend': sma_trend,
            'rsi_signal': rsi_signal,
            'macd_signal': macd_signal,
            'bb_signal': bb_signal,
            'volume_signal': volume_signal,
            'trend_score': self._calculate_trend_score(sma_trend, rsi_signal, macd_signal)
        }
    
    def _make_trading_decision(self, df: pd.DataFrame, indicators: Dict, trend_analysis: Dict) -> Dict:
        """Прийняття торгового рішення на основі аналізу"""
        current_price = indicators['current_price']
        atr = indicators['atr'][-1] if len(indicators['atr']) > 0 else current_price * 0.02
        
        # Розраховуємо загальну впевненість
        confidence_factors = []
        
        # 1. Тренд ковзних середніх (30% ваги)
        sma_score = 1.0 if trend_analysis['sma_trend']['direction'] != 'neutral' else 0.3
        confidence_factors.append(('sma_trend', sma_score, 0.3))
        
        # 2. RSI (20% ваги)
        rsi_score = 1.0 if trend_analysis['rsi_signal']['strength'] == 'strong' else 0.5
        confidence_factors.append(('rsi', rsi_score, 0.2))
        
        # 3. MACD (25% ваги)
        macd_score = 1.0 if trend_analysis['macd_signal']['direction'] != 'neutral' else 0.4
        confidence_factors.append(('macd', macd_score, 0.25))
        
        # 4. Об'єми (15% ваги)
        volume_score = 1.0 if trend_analysis['volume_signal'] == 'strong' else 0.3
        confidence_factors.append(('volume', volume_score, 0.15))
        
        # 5. Волатильність (10% ваги)
        volatility_score = 1.0 if 0.01 < (atr / current_price) < 0.05 else 0.4
        confidence_factors.append(('volatility', volatility_score, 0.1))
        
        # Загальна впевненість
        total_confidence = sum(score * weight for _, score, weight in confidence_factors)
        
        # Визначаємо напрямок на основі аналізу
        if trend_analysis['trend_score'] > 0.6:
            direction = 'long'
        elif trend_analysis['trend_score'] < 0.4:
            direction = 'short'
        else:
            direction = 'neutral'
        
        # Розраховуємо TP/SL на основі ATR
        if direction == 'long':
            take_profit = current_price + (atr * 3)
            stop_loss = current_price - (atr * 1.5)
        elif direction == 'short':
            take_profit = current_price - (atr * 3)
            stop_loss = current_price + (atr * 1.5)
        else:
            take_profit = current_price
            stop_loss = current_price
            total_confidence = max(0.3, total_confidence * 0.7)
        
        # Фактори для пояснення
        factors = {
            "trend_strength": round(trend_analysis['trend_score'], 2),
            "momentum": round(trend_analysis['macd_signal'].get('strength_value', 0.5), 2),
            "volume_confirmation": round(volume_score, 2),
            "volatility_score": round(volatility_score, 2),
            "rsi_level": round(indicators['rsi'][-1] if len(indicators['rsi']) > 0 else 50, 1),
            "bollinger_position": trend_analysis['bb_signal']['position']
        }
        
        return {
            "direction": direction,
            "confidence": round(min(total_confidence, 0.95), 2),
            "factors": factors,
            "entry_price": round(current_price, 4),
            "take_profit": round(take_profit, 4),
            "stop_loss": round(stop_loss, 4),
            "indicators_summary": {
                "rsi": round(indicators['rsi'][-1] if len(indicators['rsi']) > 0 else 50, 1),
                "macd_hist": round(indicators['macd_histogram'][-1] if len(indicators['macd_histogram']) > 0 else 0, 4),
                "sma_20": round(indicators['sma_20'][-1] if len(indicators['sma_20']) > 0 else 0, 2),
                "sma_50": round(indicators['sma_50'][-1] if len(indicators['sma_50']) > 0 else 0, 2),
                "atr_percent": round((atr / current_price) * 100, 2),
                "volume_ratio": round(indicators['volume_ratio'], 2)
            }
        }
    
    # ===== ДОПОМІЖНІ МЕТОДИ ДЛЯ ІНДИКАТОРІВ =====
    
    def _calculate_sma(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Проста ковзна середня"""
        return pd.Series(prices).rolling(window=period).mean().values
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Експоненційна ковзна середня"""
        return pd.Series(prices).ewm(span=period, adjust=False).mean().values
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Relative Strength Index"""
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.values
    
    def _calculate_macd(self, prices: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """MACD (Moving Average Convergence Divergence)"""
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)
        macd = ema12 - ema26
        signal = self._calculate_ema(macd, 9)
        histogram = macd - signal
        return macd, signal, histogram
    
    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: float = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Смуги Боллінджера"""
        sma = self._calculate_sma(prices, period)
        std = pd.Series(prices).rolling(window=period).std().values
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    def _calculate_atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Average True Range"""
        high_low = high[1:] - low[1:]
        high_close = np.abs(high[1:] - close[:-1])
        low_close = np.abs(low[1:] - close[:-1])
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = pd.Series(tr).rolling(window=period).mean().values
        return atr
    
    # ===== АНАЛІТИЧНІ МЕТОДИ =====
    
    def _analyze_moving_averages_trend(self, indicators: Dict) -> Dict:
        """Аналіз тренду на основі ковзних середніх"""
        sma_20 = indicators['sma_20'][-1] if len(indicators['sma_20']) > 0 else 0
        sma_50 = indicators['sma_50'][-1] if len(indicators['sma_50']) > 0 else 0
        sma_200 = indicators['sma_200'][-1] if len(indicators['sma_200']) > 0 else 0
        current_price = indicators['current_price']
        
        # Перевірка "золотого хреста" та "хреста смерті"
        if sma_20 > sma_50 > sma_200 and current_price > sma_20:
            return {'direction': 'long', 'strength': 'strong', 'description': 'Golden cross, strong uptrend'}
        elif sma_20 < sma_50 < sma_200 and current_price < sma_20:
            return {'direction': 'short', 'strength': 'strong', 'description': 'Death cross, strong downtrend'}
        elif current_price > sma_50:
            return {'direction': 'long', 'strength': 'medium', 'description': 'Above 50 SMA'}
        elif current_price < sma_50:
            return {'direction': 'short', 'strength': 'medium', 'description': 'Below 50 SMA'}
        else:
            return {'direction': 'neutral', 'strength': 'weak', 'description': 'Consolidation'}
    
    def _analyze_rsi(self, rsi_value: float) -> Dict:
        """Аналіз RSI"""
        if rsi_value > 70:
            return {'direction': 'short', 'strength': 'strong', 'level': 'overbought'}
        elif rsi_value < 30:
            return {'direction': 'long', 'strength': 'strong', 'level': 'oversold'}
        elif rsi_value > 60:
            return {'direction': 'short', 'strength': 'medium', 'level': 'neutral'}
        elif rsi_value < 40:
            return {'direction': 'long', 'strength': 'medium', 'level': 'neutral'}
        else:
            return {'direction': 'neutral', 'strength': 'weak', 'level': 'neutral'}
    
    def _analyze_macd(self, histogram: float, macd: float, signal: float) -> Dict:
        """Аналіз MACD"""
        if histogram > 0 and macd > signal:
            strength_value = abs(histogram) / (abs(macd) + 0.0001)
            strength = 'strong' if strength_value > 0.5 else 'medium'
            return {'direction': 'long', 'strength': strength, 'strength_value': strength_value}
        elif histogram < 0 and macd < signal:
            strength_value = abs(histogram) / (abs(macd) + 0.0001)
            strength = 'strong' if strength_value > 0.5 else 'medium'
            return {'direction': 'short', 'strength': strength, 'strength_value': strength_value}
        else:
            return {'direction': 'neutral', 'strength': 'weak', 'strength_value': 0.1}
    
    def _analyze_bollinger_bands(self, price: float, bb_upper: float, bb_middle: float, bb_lower: float) -> Dict:
        """Аналіз позиції ціни відносно смуг Боллінджера"""
        if price <= bb_lower:
            return {'position': 'oversold', 'action': 'buy', 'distance': (bb_middle - price) / bb_middle}
        elif price >= bb_upper:
            return {'position': 'overbought', 'action': 'sell', 'distance': (price - bb_middle) / bb_middle}
        elif price > bb_middle:
            return {'position': 'upper_half', 'action': 'hold_bullish', 'distance': (price - bb_middle) / bb_middle}
        else:
            return {'position': 'lower_half', 'action': 'hold_bearish', 'distance': (bb_middle - price) / bb_middle}
    
    def _analyze_volume(self, volume_ratio: float) -> str:
        """Аналіз об'ємів"""
        if volume_ratio > 1.5:
            return 'very_strong'
        elif volume_ratio > 1.2:
            return 'strong'
        elif volume_ratio > 0.8:
            return 'normal'
        else:
            return 'weak'
    
    def _calculate_trend_score(self, sma_trend: Dict, rsi_signal: Dict, macd_signal: Dict) -> float:
        """Розрахунок загального балу тренду"""
        score = 0.5  # нейтральна точка
        
        # Ковзні середні (40% ваги)
        if sma_trend['direction'] == 'long':
            score += 0.2 if sma_trend['strength'] == 'strong' else 0.1
        elif sma_trend['direction'] == 'short':
            score -= 0.2 if sma_trend['strength'] == 'strong' else 0.1
        
        # RSI (30% ваги)
        if rsi_signal['direction'] == 'long':
            score += 0.15 if rsi_signal['strength'] == 'strong' else 0.075
        elif rsi_signal['direction'] == 'short':
            score -= 0.15 if rsi_signal['strength'] == 'strong' else 0.075
        
        # MACD (30% ваги)
        if macd_signal['direction'] == 'long':
            score += 0.15 * macd_signal.get('strength_value', 0.5)
        elif macd_signal['direction'] == 'short':
            score -= 0.15 * macd_signal.get('strength_value', 0.5)
        
        return max(0, min(1, score))
    
    def _get_fallback_signal(self, symbol: str) -> Dict:
        """Резервний сигнал на випадок помилки"""
        return {
            "direction": "neutral",
            "confidence": 0.1,
            "factors": {
                "error": "insufficient_data",
                "trend_strength": 0.1,
                "momentum": 0.1,
                "volume_confirmation": 0.1
            },
            "entry_price": 0,
            "take_profit": 0,
            "stop_loss": 0,
            "symbol": symbol
        }


# Глобальний екземпляр
ai_analyzer = AIAnalyzer()