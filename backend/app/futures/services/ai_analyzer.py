# backend/app/futures/services/ai_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, List, Optional
import logging
from app.futures.models.exchange_connector import ExchangeConnector

class AIAnalyzer:
    """ПРОФЕСІЙНИЙ AI аналіз з повним набором індикаторів для максимальної точності"""
    
    def __init__(self):
        self.exchange = ExchangeConnector()
        self.logger = logging.getLogger(__name__)
        
    def analyze_market(self, symbol: str, timeframe: str = "1h") -> Dict:
        """
        ПРОФЕСІЙНИЙ аналіз з 8+ індикаторами для максимального прибутку
        
        Повертає: {
            "direction": "long"/"short"/"neutral",
            "confidence": 0.0-1.0,
            "factors": {...},
            "entry_price": float,
            "take_profit": float,
            "stop_loss": float,
            "risk_reward": float,
            "expected_pnl": float
        }
        """
        try:
            # 1. Отримуємо більше даних для точного аналізу
            df = self.exchange.fetch_ohlcv(symbol, timeframe, limit=500)
            if len(df) < 100:
                return self._get_fallback_signal(symbol)
            
            # 2. Розраховуємо ПОВНИЙ НАБІР індикаторів
            indicators = self._calculate_all_indicators(df)
            
            # 3. ГЛИБОКИЙ аналіз з конфірмацією
            signal_analysis = self._deep_signal_analysis(df, indicators)
            
            # 4. РОЗРАХУНОК РИЗИК-ПРИБУТОК
            risk_reward = self._calculate_risk_reward(signal_analysis, indicators['current_price'])
            
            # 5. ФОРМУВАННЯ СИГНАЛУ
            final_signal = {
                "direction": signal_analysis['direction'],
                "confidence": round(min(signal_analysis['confidence'], 0.95), 2),
                "factors": signal_analysis['factors'],
                "entry_price": round(indicators['current_price'], 4),
                "take_profit": round(signal_analysis['take_profit'], 4),
                "stop_loss": round(signal_analysis['stop_loss'], 4),
                "risk_reward": round(risk_reward['ratio'], 2),
                "expected_pnl_percent": round(risk_reward['expected_pnl'], 2),
                "position_size": self._calculate_position_size(indicators, signal_analysis),
                "symbol": symbol,
                "timeframe": timeframe,
                "indicators_summary": self._get_indicators_summary(indicators),
                "signal_strength": signal_analysis['strength'],
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"🎯 ПРОФІ сигнал для {symbol}: {final_signal['direction']} "
                           f"({final_signal['confidence']*100}%), RR: {final_signal['risk_reward']}")
            
            return final_signal
            
        except Exception as e:
            self.logger.error(f"❌ Помилка аналізу {symbol}: {e}")
            return self._get_fallback_signal(symbol)
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> Dict:
        """РОЗРАХУНОК ВСІХ 8+ КРИТИЧНИХ ІНДИКАТОРІВ"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        indicators = {
            # БАЗОВІ (вже є)
            'sma_20': self._calculate_sma(close, 20),
            'sma_50': self._calculate_sma(close, 50),
            'sma_200': self._calculate_sma(close, 200),
            'ema_12': self._calculate_ema(close, 12),
            'ema_26': self._calculate_ema(close, 26),
            'rsi': self._calculate_rsi(close, 14),
            'macd': self._calculate_macd(close)[0],
            'macd_signal': self._calculate_macd(close)[1],
            'macd_histogram': self._calculate_macd(close)[2],
            'bb_upper': self._calculate_bollinger_bands(close, 20, 2)[0],
            'bb_middle': self._calculate_bollinger_bands(close, 20, 2)[1],
            'bb_lower': self._calculate_bollinger_bands(close, 20, 2)[2],
            'atr': self._calculate_atr(high, low, close, 14),
            'current_price': close[-1],
            'volume_array': volume,
            
            # НОВІ ПРОФІ ІНДИКАТОРИ ⭐⭐⭐
            'vwap': self._calculate_vwap(df),  # Volume Weighted Average Price
            'stoch_rsi_k': self._calculate_stoch_rsi(close)[0],  # Stochastic RSI K
            'stoch_rsi_d': self._calculate_stoch_rsi(close)[1],  # Stochastic RSI D
            'ichimoku': self._calculate_ichimoku(df),  # Ichimoku Cloud
            'obv': self._calculate_obv(close, volume),  # On-Balance Volume
            'adl': self._calculate_adl(df),  # Accumulation/Distribution Line
            'cci': self._calculate_cci(df, 20),  # Commodity Channel Index
            'williams_r': self._calculate_williams_r(df, 14),  # Williams %R
            
            # ДОДАТКОВІ
            'volume_sma': self._calculate_sma(volume, 20),
            'price_change_24h': ((close[-1] - close[-24]) / close[-24]) * 100 if len(close) >= 24 else 0,
        }
        
        indicators['volume_ratio'] = volume[-1] / indicators['volume_sma'][-1] if indicators['volume_sma'][-1] > 0 else 1
        
        return indicators
    
    # ===== НОВІ ПРОФІ МЕТОДИ =====
    
    def _calculate_vwap(self, df: pd.DataFrame) -> np.ndarray:
        """Volume Weighted Average Price (ВАЖЛИВО для інституційного аналізу)"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        return vwap.values
    
    def _calculate_stoch_rsi(self, prices: np.ndarray, rsi_period: int = 14, stoch_period: int = 14) -> Tuple[np.ndarray, np.ndarray]:
        """Stochastic RSI - суперчутливий індикатор перекупленості/перепроданості"""
        rsi = self._calculate_rsi(prices, rsi_period)
        rsi_series = pd.Series(rsi)
        
        # Stochastic з RSI
        stoch_k = 100 * (rsi_series - rsi_series.rolling(stoch_period).min()) / \
                  (rsi_series.rolling(stoch_period).max() - rsi_series.rolling(stoch_period).min())
        stoch_d = stoch_k.rolling(3).mean()
        
        return stoch_k.values, stoch_d.values
    
    def _calculate_ichimoku(self, df: pd.DataFrame) -> Dict:
        """Ichimoku Cloud - комплексний аналіз тренду, підтримки та опору"""
        high, low, close = df['high'].values, df['low'].values, df['close'].values
        
        # Tenkan-sen (Conversion Line)
        period9_high = pd.Series(high).rolling(9).max()
        period9_low = pd.Series(low).rolling(9).min()
        tenkan_sen = (period9_high + period9_low) / 2
        
        # Kijun-sen (Base Line)
        period26_high = pd.Series(high).rolling(26).max()
        period26_low = pd.Series(low).rolling(26).min()
        kijun_sen = (period26_high + period26_low) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        
        # Senkou Span B (Leading Span B)
        period52_high = pd.Series(high).rolling(52).max()
        period52_low = pd.Series(low).rolling(52).min()
        senkou_span_b = ((period52_high + period52_low) / 2).shift(26)
        
        # Chikou Span (Lagging Span)
        chikou_span = pd.Series(close).shift(-26)
        
        return {
            'tenkan_sen': tenkan_sen.values,
            'kijun_sen': kijun_sen.values,
            'senkou_span_a': senkou_span_a.values,
            'senkou_span_b': senkou_span_b.values,
            'chikou_span': chikou_span.values,
            'cloud_top': np.maximum(senkou_span_a.values, senkou_span_b.values),
            'cloud_bottom': np.minimum(senkou_span_a.values, senkou_span_b.values),
            'cloud_color': 'green' if senkou_span_a.iloc[-1] > senkou_span_b.iloc[-1] else 'red',
            'price_above_cloud': close[-1] > max(senkou_span_a.iloc[-1], senkou_span_b.iloc[-1]),
            'price_below_cloud': close[-1] < min(senkou_span_a.iloc[-1], senkou_span_b.iloc[-1]),
        }
    
    def _calculate_obv(self, prices: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """On-Balance Volume - дивергенція ціни та об'єму"""
        obv = np.zeros_like(prices)
        obv[0] = volume[0]
        
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                obv[i] = obv[i-1] + volume[i]
            elif prices[i] < prices[i-1]:
                obv[i] = obv[i-1] - volume[i]
            else:
                obv[i] = obv[i-1]
        
        return obv
    
    def _calculate_adl(self, df: pd.DataFrame) -> np.ndarray:
        """Accumulation/Distribution Line - грошовий потік"""
        high, low, close, volume = df['high'].values, df['low'].values, df['close'].values, df['volume'].values
        
        clv = ((close - low) - (high - close)) / (high - low + 0.000001)  # + epsilon для поділу на 0
        clv = np.nan_to_num(clv)
        adl = np.cumsum(clv * volume)
        
        return adl
    
    def _calculate_cci(self, df: pd.DataFrame, period: int = 20) -> np.ndarray:
        """Commodity Channel Index - виявлення початку трендів"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma = typical_price.rolling(period).mean()
        mad = typical_price.rolling(period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        cci = (typical_price - sma) / (0.015 * mad)
        return cci.values
    
    def _calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Williams %R - індикатор перекупленості/перепроданості"""
        high, low, close = df['high'].values, df['low'].values, df['close'].values
        
        highest_high = pd.Series(high).rolling(period).max()
        lowest_low = pd.Series(low).rolling(period).min()
        williams_r = -100 * (highest_high - close) / (highest_high - lowest_low + 0.000001)
        
        return williams_r.values
    
    # ===== ГЛИБОКИЙ АНАЛІЗ СИГНАЛУ =====
    
    def _deep_signal_analysis(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """ГЛИБОКИЙ аналіз з множинною конфірмацією"""
        current_price = indicators['current_price']
        
        # 1. Аналіз КОЖНОГО індикатора окремо
        signal_scores = {
            'trend': self._analyze_trend_indicators(indicators),
            'momentum': self._analyze_momentum_indicators(indicators),
            'volume': self._analyze_volume_indicators(indicators),
            'volatility': self._analyze_volatility_indicators(indicators),
            'market_structure': self._analyze_market_structure(indicators),
        }
        
        # 2. МНОЖИННА КОНФІРМАЦІЯ (необхідно 3+ з 5 категорій)
        confirmed_categories = [cat for cat, score in signal_scores.items() if score['direction'] != 'neutral']
        confirmation_ratio = len(confirmed_categories) / 5
        
        # 3. ВИЗНАЧЕННЯ НАПРЯМКУ
        long_votes = sum(1 for cat in signal_scores.values() if cat['direction'] == 'long')
        short_votes = sum(1 for cat in signal_scores.values() if cat['direction'] == 'short')
        
        if confirmation_ratio >= 0.6:
            if long_votes > short_votes:
                direction = 'long'
            elif short_votes > long_votes:
                direction = 'short'
            else:
                direction = 'neutral'
    
    # ДЕТЕРМІНОВАНА впевненість (без random!)
            if confirmation_ratio >= 0.85:
                confidence_base = 0.85  # Дуже сильні сигнали
            elif confirmation_ratio >= 0.75:
                confidence_base = 0.75  # Сильні сигнали
            elif confirmation_ratio >= 0.65:
                confidence_base = 0.65  # Середні сигнали
            else:  # 0.6-0.65
                confidence_base = 0.55  # Слабкі але дійсні сигнали
    
    # Додаткова корекція на перевагу голосів
            vote_diff = abs(long_votes - short_votes)
            if vote_diff >= 3:  # Ясна перевага (4-1, 5-0)
                confidence_base += 0.05
            elif vote_diff == 2:  # Помірна перевага (3-1)
                confidence_base += 0.02
    
        else:
            direction = 'neutral'
            confidence_base = 0.25  # Низька впевненість для слабких сигналів

# ОБМЕЖЕННЯ
        if direction == 'neutral':
            confidence_base = min(0.45, confidence_base)  # Neutral не більше 45%
        else:
            confidence_base = min(0.90, confidence_base)  # Максимум 90%
        
        # 4. СИЛА СИГНАЛУ
        strength = 'strong' if confirmation_ratio >= 0.8 else \
                   'medium' if confirmation_ratio >= 0.6 else 'weak'
        
        # 5. РОЗРАХУНОК TP/SL на основі ATR та індикаторів
        atr = indicators['atr'][-1] if len(indicators['atr']) > 0 else current_price * 0.02
        
        if direction == 'long':
            # Агресивніший TP для сильних сигналів
            tp_multiplier = 4 if strength == 'strong' else 3 if strength == 'medium' else 2
            sl_multiplier = 1.5 if strength == 'strong' else 1.2 if strength == 'medium' else 1
            
            take_profit = current_price + (atr * tp_multiplier)
            stop_loss = current_price - (atr * sl_multiplier)
            
        elif direction == 'short':
            tp_multiplier = 4 if strength == 'strong' else 3 if strength == 'medium' else 2
            sl_multiplier = 1.5 if strength == 'strong' else 1.2 if strength == 'medium' else 1
            
            take_profit = current_price - (atr * tp_multiplier)
            stop_loss = current_price + (atr * sl_multiplier)
        else:
            take_profit = current_price
            stop_loss = current_price
            confidence_base = confidence_base * 0.6  # Додатково знижуємо для neutral
        
        # 6. ФАКТОРИ ДЛЯ ПОЯСНЕННЯ
        factors = {
            "trend_score": round(signal_scores['trend']['score'], 2),
            "momentum_score": round(signal_scores['momentum']['score'], 2),
            "volume_confirmation": round(signal_scores['volume']['score'], 2),
            "volatility_score": round(signal_scores['volatility']['score'], 2),
            "structure_score": round(signal_scores['market_structure']['score'], 2),
            "confirmation_ratio": round(confirmation_ratio, 2),
            "rsi_level": round(indicators['rsi'][-1] if len(indicators['rsi']) > 0 else 50, 1),
            "stoch_rsi_level": round(indicators['stoch_rsi_k'][-1] if len(indicators['stoch_rsi_k']) > 0 else 50, 1),
            "vwap_position": "above" if current_price > indicators['vwap'][-1] else "below",
            "ichimoku_signal": indicators['ichimoku'].get('cloud_color', 'neutral'),
            "obv_trend": "bullish" if indicators['obv'][-1] > indicators['obv'][-5] else "bearish",
        }
        
        return {
            'direction': direction,
            'confidence': min(confidence_base, 0.95),
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'strength': strength,
            'factors': factors,
            'confirmed_categories': confirmed_categories,
            'signal_scores': signal_scores,
        }
    
    # ===== АНАЛІТИЧНІ МЕТОДИ КАТЕГОРІЙ =====
    
    def _analyze_trend_indicators(self, indicators: Dict) -> Dict:
        """Аналіз трендових індикаторів (SMA, EMA, Ichimoku)"""
        score = 0.5
        direction = 'neutral'
        current_price = indicators['current_price']
        
        # SMA аналіз
        sma_20 = indicators['sma_20'][-1] if len(indicators['sma_20']) > 0 else current_price
        sma_50 = indicators['sma_50'][-1] if len(indicators['sma_50']) > 0 else current_price
        sma_200 = indicators['sma_200'][-1] if len(indicators['sma_200']) > 0 else current_price
        
        if current_price > sma_20 > sma_50 > sma_200:
            score = 1.0
            direction = 'long'
        elif current_price < sma_20 < sma_50 < sma_200:
            score = 1.0
            direction = 'short'
        elif current_price > sma_50:
            score = 0.7
            direction = 'long'
        elif current_price < sma_50:
            score = 0.7
            direction = 'short'
        
        # Ichimoku аналіз
        ichimoku = indicators.get('ichimoku', {})
        if ichimoku.get('price_above_cloud', False):
            score = max(score, 0.8)
            direction = 'long' if direction == 'neutral' else direction
        elif ichimoku.get('price_below_cloud', False):
            score = max(score, 0.8)
            direction = 'short' if direction == 'neutral' else direction
        
        return {'direction': direction, 'score': score}
    
    def _analyze_momentum_indicators(self, indicators: Dict) -> Dict:
        """Аналіз індикаторів моментуму (RSI, MACD, Stochastic, Williams)"""
        score = 0.5
        direction = 'neutral'
        
        # RSI
        rsi = indicators['rsi'][-1] if len(indicators['rsi']) > 0 else 50
        if rsi < 35:
            score = 0.9
            direction = 'long'
        elif rsi > 65:
            score = 0.9
            direction = 'short'
        elif rsi < 45:
            score = 0.7
            direction = 'long'
        elif rsi > 55:
            score = 0.7
            direction = 'short'
        
        # Stochastic RSI
        stoch_k = indicators['stoch_rsi_k'][-1] if len(indicators['stoch_rsi_k']) > 0 else 50
        if stoch_k < 20:
            score = max(score, 0.85)
            direction = 'long' if direction == 'neutral' else direction
        elif stoch_k > 80:
            score = max(score, 0.85)
            direction = 'short' if direction == 'neutral' else direction
        
        # MACD
        macd_hist = indicators['macd_histogram'][-1] if len(indicators['macd_histogram']) > 0 else 0
        if macd_hist > 0:
            score = max(score, 0.6)
            direction = 'long' if direction == 'neutral' else direction
        elif macd_hist < 0:
            score = max(score, 0.6)
            direction = 'short' if direction == 'neutral' else direction
        
        # Williams %R
        williams = indicators['williams_r'][-1] if len(indicators['williams_r']) > 0 else -50
        if williams < -80:
            score = max(score, 0.8)
            direction = 'long' if direction == 'neutral' else direction
        elif williams > -20:
            score = max(score, 0.8)
            direction = 'short' if direction == 'neutral' else direction
        
        return {'direction': direction, 'score': score}
    
    def _analyze_volume_indicators(self, indicators: Dict) -> Dict:
        """Аналіз об'ємних індикаторів (OBV, ADL, Volume Ratio)"""
        score = 0.5
        direction = 'neutral'
        
        # Volume Ratio
        volume_ratio = indicators.get('volume_ratio', 1)
        if volume_ratio > 1.5:
            score = 0.8
        elif volume_ratio > 1.2:
            score = 0.7
        elif volume_ratio < 0.8:
            score = 0.3
        
        # OBV тренд
        obv = indicators.get('obv', [0])
        if len(obv) >= 5:
            if obv[-1] > obv[-5]:  # Зростання OBV
                score = max(score, 0.7)
                direction = 'long' if direction == 'neutral' else direction
            elif obv[-1] < obv[-5]:  # Падіння OBV
                score = max(score, 0.7)
                direction = 'short' if direction == 'neutral' else direction
        
        # VWAP позиція
        vwap = indicators.get('vwap', [0])
        current_price = indicators['current_price']
        if len(vwap) > 0:
            if current_price > vwap[-1]:
                score = max(score, 0.6)
                direction = 'long' if direction == 'neutral' else direction
            else:
                score = max(score, 0.6)
                direction = 'short' if direction == 'neutral' else direction
        
        return {'direction': direction, 'score': score}
    
    def _analyze_volatility_indicators(self, indicators: Dict) -> Dict:
        """Аналіз волатильності (ATR, Bollinger Bands)"""
        score = 0.5
        direction = 'neutral'
        current_price = indicators['current_price']
        
        # Bollinger Bands позиція
        bb_upper = indicators['bb_upper'][-1] if len(indicators['bb_upper']) > 0 else current_price
        bb_lower = indicators['bb_lower'][-1] if len(indicators['bb_lower']) > 0 else current_price
        bb_middle = indicators['bb_middle'][-1] if len(indicators['bb_middle']) > 0 else current_price
        
        if current_price <= bb_lower:
            score = 0.9
            direction = 'long'  # Перепроданість
        elif current_price >= bb_upper:
            score = 0.9
            direction = 'short'  # Перекупленість
        elif current_price > bb_middle:
            score = 0.6
            direction = 'long'
        elif current_price < bb_middle:
            score = 0.6
            direction = 'short'
        
        # ATR (оптимальна волатильність для торгівлі)
        atr = indicators['atr'][-1] if len(indicators['atr']) > 0 else 0
        atr_percent = (atr / current_price) * 100 if current_price > 0 else 0
        
        if 0.5 < atr_percent < 3:  # Оптимальна волатильність
            score = max(score, 0.8)
        elif atr_percent > 5:  # Занадто висока волатильність
            score = score * 0.7  # Знижуємо впевненість
        
        return {'direction': direction, 'score': score}
    
    def _analyze_market_structure(self, indicators: Dict) -> Dict:
        """Аналіз структури ринку (CCI, ціна відносно VWAP)"""
        score = 0.5
        direction = 'neutral'
        
        # CCI (Commodity Channel Index)
        cci = indicators['cci'][-1] if len(indicators['cci']) > 0 else 0
        if cci > 100:
            score = 0.8
            direction = 'long'
        elif cci < -100:
            score = 0.8
            direction = 'short'
        elif cci > 0:
            score = 0.6
            direction = 'long'
        elif cci < 0:
            score = 0.6
            direction = 'short'
        
        return {'direction': direction, 'score': score}
    
    # ===== РОЗРАХУНОК РИЗИК-ПРИБУТОК =====

    def _calculate_risk_reward(self, signal_analysis: Dict, entry_price: float) -> Dict:
        """Розрахунок співвідношення ризик/прибуток та очікуваного PnL"""
        if signal_analysis['direction'] == 'neutral':
            return {'ratio': 1.0, 'expected_pnl': 0, 'profit_pips': 0, 'risk_pips': 0}
        
        tp = signal_analysis['take_profit']
        sl = signal_analysis['stop_loss']
        confidence = signal_analysis['confidence']
        
        if entry_price == 0 or tp == entry_price or sl == entry_price:
            return {'ratio': 1.0, 'expected_pnl': 0, 'profit_pips': 0, 'risk_pips': 0}
        
        if signal_analysis['direction'] == 'long':
            profit = tp - entry_price  # позитивне, якщо TP > entry
            risk = entry_price - sl    # позитивне, якщо SL < entry
            if profit <= 0 or risk <= 0:
                return {'ratio': 1.0, 'expected_pnl': 0, 'profit_pips': 0, 'risk_pips': 0}
        else:
            profit = entry_price - tp  # позитивне, якщо TP < entry
            risk = sl - entry_price    # позитивне, якщо SL > entry
            if profit <= 0 or risk <= 0:
                return {'ratio': 1.0, 'expected_pnl': 0, 'profit_pips': 0, 'risk_pips': 0}
        # Розрахунок Risk/Reward
        rr_ratio = profit / risk
        # Очікуваний PnL з урахуванням впевненості
        # win_rate приймаємо 55% для AI сигналів
        win_rate = 0.55
        expected_pnl_per_trade = (profit * win_rate * confidence) - (risk * (1 - win_rate) * (1 - confidence))
        expected_pnl_percent = (expected_pnl_per_trade / entry_price) * 100

        return {
            'ratio': rr_ratio,
            'expected_pnl': expected_pnl_percent,
            'profit_pips': profit,
            'risk_pips': risk,
            'win_rate': win_rate
      }
    
    def _calculate_position_size(self, indicators: Dict, signal_analysis: Dict) -> Dict:
        """Розрахунок розміру позиції на основі ризику"""
        atr = indicators['atr'][-1] if len(indicators['atr']) > 0 else 0
        current_price = indicators['current_price']
        confidence = signal_analysis['confidence']
        
        if signal_analysis['direction'] == 'neutral' or atr == 0:
            return {'size_percent': 0, 'risk_per_trade': 0}
        
        # Базований на Kelly Criterion
        win_rate = 0.55  # Припущення
        risk_per_trade = 0.02  # 2% на угоду
        
        # Корекція на впевненість
        adjusted_risk = risk_per_trade * confidence
        
        # Корекція на волатильність (ATR)
        atr_percent = (atr / current_price) * 100
        if atr_percent > 3:  # Висока волатильність
            adjusted_risk = adjusted_risk * 0.7
        elif atr_percent < 1:  # Низька волатильність
            adjusted_risk = adjusted_risk * 1.2
        
        # Максимальний розмір позиції
        max_position_size = min(adjusted_risk * 100, 10)  # Макс 10% портфеля
        
        return {
            'size_percent': round(max_position_size, 2),
            'risk_per_trade': round(adjusted_risk * 100, 2),
            'atr_adjustment': round(atr_percent, 2),
            'confidence_multiplier': round(confidence, 2)
        }
    
    def _get_indicators_summary(self, indicators: Dict) -> Dict:
        """Короткий звіт по всім індикаторам"""
        return {
            'rsi': round(indicators['rsi'][-1] if len(indicators['rsi']) > 0 else 50, 1),
            'stoch_rsi': round(indicators['stoch_rsi_k'][-1] if len(indicators['stoch_rsi_k']) > 0 else 50, 1),
            'macd_hist': round(indicators['macd_histogram'][-1] if len(indicators['macd_histogram']) > 0 else 0, 4),
            'sma_20_50': f"{round(indicators['sma_20'][-1], 2)}/{round(indicators['sma_50'][-1], 2)}",
            'atr_percent': round((indicators['atr'][-1] / indicators['current_price']) * 100, 2),
            'volume_ratio': round(indicators.get('volume_ratio', 1), 2),
            'vwap_position': "above" if indicators['current_price'] > indicators['vwap'][-1] else "below",
            'bollinger_position': self._get_bb_position(indicators),
            'ichimoku_cloud': indicators.get('ichimoku', {}).get('cloud_color', 'neutral'),
            'williams_r': round(indicators['williams_r'][-1] if len(indicators['williams_r']) > 0 else -50, 1),
            'cci': round(indicators['cci'][-1] if len(indicators['cci']) > 0 else 0, 1),
        }
    
    def _get_bb_position(self, indicators: Dict) -> str:
        """Позиція ціни відносно Bollinger Bands"""
        current_price = indicators['current_price']
        bb_upper = indicators['bb_upper'][-1] if len(indicators['bb_upper']) > 0 else current_price
        bb_lower = indicators['bb_lower'][-1] if len(indicators['bb_lower']) > 0 else current_price
        
        if current_price >= bb_upper:
            return 'upper_band'
        elif current_price <= bb_lower:
            return 'lower_band'
        elif current_price > (bb_upper + bb_lower) / 2:
            return 'upper_half'
        else:
            return 'lower_half'
    
    # ===== БАЗОВІ МЕТОДИ ІНДИКАТОРІВ (залишаються) =====
    
    def _calculate_sma(self, prices: np.ndarray, period: int) -> np.ndarray:
        return pd.Series(prices).rolling(window=period).mean().values
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        return pd.Series(prices).ewm(span=period, adjust=False).mean().values
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.values
    
    def _calculate_macd(self, prices: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)
        macd = ema12 - ema26
        signal = self._calculate_ema(macd, 9)
        histogram = macd - signal
        return macd, signal, histogram
    
    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: float = 2):
        sma = self._calculate_sma(prices, period)
        std = pd.Series(prices).rolling(window=period).std().values
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    def _calculate_atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        high_low = high[1:] - low[1:]
        high_close = np.abs(high[1:] - close[:-1])
        low_close = np.abs(low[1:] - close[:-1])
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = pd.Series(tr).rolling(window=period).mean().values
        return atr
    
    def _get_fallback_signal(self, symbol: str) -> Dict:
        return {
            "direction": "neutral",
            "confidence": 0.1,
            "factors": {"error": "insufficient_data"},
            "entry_price": 0,
            "take_profit": 0,
            "stop_loss": 0,
            "risk_reward": 1.0,
            "expected_pnl_percent": 0,
            "position_size": {"size_percent": 0, "risk_per_trade": 0},
            "symbol": symbol,
            "signal_strength": "weak"
        }


# Глобальний екземпляр
ai_analyzer = AIAnalyzer()