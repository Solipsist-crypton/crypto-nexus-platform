# backend/modules/ai_analyzer.py
import numpy as np
import pandas as pd
import talib
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AIAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Налаштування для професійної торгівлі
        self.MIN_CANDLES = 150  # Мінімум свічок для аналізу
        self.BASE_RISK = 0.02   # Базовий ризик 2% на угоду
        self.MIN_RR = 2.0       # Мінімальне R/R співвідношення
        self.MAX_POSITION = 5.0 # Максимальний розмір позиції 5%
        
    def setup_logging(self):
        """Налаштування логування"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def calculate_indicators(self, df: pd.DataFrame, timeframe: str = '1h') -> Dict[str, Any]:
        """Розрахунок професійних технічних індикаторів"""
        close = df['close'].values.astype(float)
        high = df['high'].values.astype(float)
        low = df['low'].values.astype(float)
        open_price = df['open'].values.astype(float)
        volume = df['volume'].values.astype(float)
        
        # ====== ТРЕНДОВІ ІНДИКАТОРИ ======
        ema_8 = talib.EMA(close, timeperiod=8)
        ema_20 = talib.EMA(close, timeperiod=20)
        ema_50 = talib.EMA(close, timeperiod=50)
        ema_100 = talib.EMA(close, timeperiod=100)
        ema_200 = talib.EMA(close, timeperiod=200)
        
        sma_20 = talib.SMA(close, timeperiod=20)
        sma_50 = talib.SMA(close, timeperiod=50)
        
        # ADX для сили тренду
        adx = talib.ADX(high, low, close, timeperiod=14)
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=14)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=14)
        
        # ====== МОМЕНТУМ ======
        rsi = talib.RSI(close, timeperiod=14)
        stoch_k, stoch_d = talib.STOCH(high, low, close)
        stoch_rsi_k, stoch_rsi_d = talib.STOCHRSI(close, timeperiod=14)
        
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(close)
        
        # ====== ВОЛАТИЛЬНІСТЬ ======
        atr = talib.ATR(high, low, close, timeperiod=14)
        bollinger_upper, bollinger_middle, bollinger_lower = talib.BBANDS(
            close, timeperiod=20, nbdevup=2, nbdevdn=2
        )
        
        # Додаткова волатильність
        natr = talib.NATR(high, low, close, timeperiod=14)
        
        # ====== ОБСЯГИ ======
        obv = talib.OBV(close, volume)
        vwap = self.calculate_vwap(df)
        volume_sma = pd.Series(volume).rolling(20).mean().values
        
        # Об'ємні індикатори
        mfi = talib.MFI(high, low, close, volume, timeperiod=14)
        ad = talib.AD(high, low, close, volume)
        
        # ====== ОСЦИЛЯТОРИ ======
        williams_r = talib.WILLR(high, low, close, timeperiod=14)
        cci = talib.CCI(high, low, close, timeperiod=20)
        ultosc = talib.ULTOSC(high, low, close)
        
        # ====== ІШИМОКУ ======
        tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span = self.calculate_ichimoku(df)
        
        # ====== СВЕЧНІ ПАТТЕРНИ ======
        doji = talib.CDLDOJI(open_price, high, low, close)
        hammer = talib.CDLHAMMER(open_price, high, low, close)
        engulfing = talib.CDLENGULFING(open_price, high, low, close)
        morning_star = talib.CDLMORNINGSTAR(open_price, high, low, close)
        evening_star = talib.CDLEVENINGSTAR(open_price, high, low, close)
        harami = talib.CDLHARAMI(open_price, high, low, close)
        
        indicators = {
            # Трендові
            'ema_8': ema_8, 'ema_20': ema_20, 'ema_50': ema_50, 
            'ema_100': ema_100, 'ema_200': ema_200,
            'sma_20': sma_20, 'sma_50': sma_50,
            'adx': adx, 'plus_di': plus_di, 'minus_di': minus_di,
            
            # Моментум
            'rsi': rsi, 'stoch_k': stoch_k, 'stoch_d': stoch_d,
            'stoch_rsi_k': stoch_rsi_k, 'stoch_rsi_d': stoch_rsi_d,
            'macd': macd, 'macd_signal': macd_signal, 'macd_hist': macd_hist,
            
            # Волатильність
            'atr': atr, 'natr': natr,
            'bb_upper': bollinger_upper, 'bb_middle': bollinger_middle, 'bb_lower': bollinger_lower,
            
            # Обсяги
            'obv': obv, 'vwap': vwap, 'volume_sma': volume_sma,
            'mfi': mfi, 'ad': ad,
            
            # Осцилятори
            'williams_r': williams_r, 'cci': cci, 'ultosc': ultosc,
            
            # Ішимоку
            'tenkan_sen': tenkan_sen, 'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a, 'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span,
            
            # Свечні паттерни
            'doji': doji, 'hammer': hammer, 'engulfing': engulfing,
            'morning_star': morning_star, 'evening_star': evening_star, 'harami': harami,
            
            # Базові ціни
            'close': close, 'high': high, 'low': low, 'open': open_price, 'volume': volume,
        }
        
        return indicators
    
    def calculate_vwap(self, df: pd.DataFrame) -> np.ndarray:
        """Розрахунок VWAP"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        return vwap.values
    
    def calculate_ichimoku(self, df: pd.DataFrame) -> Tuple:
        """Розрахунок Ішимоку Кінко Хйо"""
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        # Tenkan-sen (Conversion Line)
        period9_high = pd.Series(high).rolling(window=9).max()
        period9_low = pd.Series(low).rolling(window=9).min()
        tenkan_sen = ((period9_high + period9_low) / 2).values
        
        # Kijun-sen (Base Line)
        period26_high = pd.Series(high).rolling(window=26).max()
        period26_low = pd.Series(low).rolling(window=26).min()
        kijun_sen = ((period26_high + period26_low) / 2).values
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2)
        
        # Senkou Span B (Leading Span B)
        period52_high = pd.Series(high).rolling(window=52).max()
        period52_low = pd.Series(low).rolling(window=52).min()
        senkou_span_b = ((period52_high + period52_low) / 2).values
        
        # Chikou Span (Lagging Span)
        chikou_span = np.roll(close, -26)
        
        return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span
    
    def analyze_price_action(self, df: pd.DataFrame) -> Dict:
        """Детальний аналіз цінової дії"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        open_price = df['open'].values
        volume = df['volume'].values
        
        if len(close) < 50:
            return {}
        
        # Структура максимумів та мінімумів
        highs, lows = [], []
        for i in range(10, len(close) - 10):
            if high[i] == max(high[i-10:i+11]):
                highs.append((i, high[i]))
            if low[i] == min(low[i-10:i+11]):
                lows.append((i, low[i]))
        
        # Тренд за структурою
        higher_highs = sum(1 for i in range(1, min(5, len(highs))) if highs[i][1] > highs[i-1][1])
        lower_lows = sum(1 for i in range(1, min(5, len(lows))) if lows[i][1] < lows[i-1][1])
        
        # Волатильність
        returns = np.diff(close) / close[:-1]
        volatility_annual = np.std(returns) * np.sqrt(365) * 100 if len(returns) > 0 else 0
        
        # Обсяги
        volume_sma = pd.Series(volume).rolling(20).mean()
        volume_spike = False
        if len(volume_sma) > 0 and not pd.isna(volume_sma.iloc[-1]) and volume_sma.iloc[-1] > 0:
            volume_spike = volume[-1] > volume_sma.iloc[-1] * 1.8
        
        # Аналіз останніх свічок
        recent_candles = min(5, len(close))
        bullish_candles = 0
        for i in range(-recent_candles, 0):
            if i + len(close) >= 0:  # Перевірка меж
                if close[i] > open_price[i]:
                    bullish_candles += 1
        bearish_candles = recent_candles - bullish_candles
        
        return {
            'higher_highs': higher_highs,
            'lower_lows': lower_lows,
            'volatility_annual': round(volatility_annual, 2),
            'volume_spike': volume_spike,
            'volume_ratio': round(volume[-1] / volume_sma.iloc[-1], 2) if len(volume_sma) > 0 and volume_sma.iloc[-1] > 0 else 1.0,
            'bullish_candles': bullish_candles,
            'bearish_candles': bearish_candles,
            'structure': 'uptrend' if higher_highs >= 3 else 'downtrend' if lower_lows >= 3 else 'ranging',
        }
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Розрахунок рівнів підтримки та опору з кластеризацією"""
        close = df['close'].values
        
        # Знаходимо локальні екстремуми
        supports, resistances = [], []
        
        for i in range(window, len(close) - window):
            local_min = np.min(close[i-window:i+window+1])
            local_max = np.max(close[i-window:i+window+1])
            
            if close[i] == local_min:
                supports.append(close[i])
            if close[i] == local_max:
                resistances.append(close[i])
        
        # Кластеризація
        def cluster_levels(levels, threshold_percent=0.015):
            if not levels:
                return []
            
            levels = sorted(levels)
            clusters = []
            current_cluster = [levels[0]]
            
            for price in levels[1:]:
                cluster_mean = np.mean(current_cluster)
                if cluster_mean == 0:
                    current_cluster.append(price)
                    continue
                    
                if abs(price - cluster_mean) / cluster_mean < threshold_percent:
                    current_cluster.append(price)
                else:
                    clusters.append(np.mean(current_cluster))
                    current_cluster = [price]
            
            if current_cluster:
                clusters.append(np.mean(current_cluster))
            
            return clusters
        
        support_clusters = cluster_levels(supports)
        resistance_clusters = cluster_levels(resistances)
        
        # Знаходимо найближчі рівні
        current_price = close[-1] if len(close) > 0 else 0
        
        nearest_support = min(support_clusters, key=lambda x: abs(x - current_price)) if support_clusters else None
        nearest_resistance = min(resistance_clusters, key=lambda x: abs(x - current_price)) if resistance_clusters else None
        
        # Розраховуємо відстань до рівнів
        support_distance = ((current_price - nearest_support) / current_price * 100) if nearest_support else None
        resistance_distance = ((nearest_resistance - current_price) / current_price * 100) if nearest_resistance else None
        
        return {
            'supports': [round(s, 4) for s in support_clusters[-5:]],
            'resistances': [round(r, 4) for r in resistance_clusters[-5:]],
            'nearest_support': round(nearest_support, 4) if nearest_support else None,
            'nearest_resistance': round(nearest_resistance, 4) if nearest_resistance else None,
            'support_distance_pct': round(support_distance, 2) if support_distance else None,
            'resistance_distance_pct': round(resistance_distance, 2) if resistance_distance else None,
        }
    
    def analyze_market_structure(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """Аналіз структури ринку"""
        close = df['close'].values
        if len(close) < 50:
            return {}
        
        # Тренд за EMA
        ema_20 = indicators.get('ema_20', [])
        ema_50 = indicators.get('ema_50', [])
        ema_200 = indicators.get('ema_200', [])
        
        if len(ema_20) == 0 or len(ema_50) == 0 or len(ema_200) == 0:
            return {}
        
        ema_20_current = ema_20[-1] if not pd.isna(ema_20[-1]) else close[-1]
        ema_50_current = ema_50[-1] if not pd.isna(ema_50[-1]) else close[-1]
        ema_200_current = ema_200[-1] if not pd.isna(ema_200[-1]) else close[-1]
        
        # Визначення тренду
        ema_trend = "bullish" if ema_20_current > ema_50_current > ema_200_current else \
                   "bearish" if ema_20_current < ema_50_current < ema_200_current else "neutral"
        
        # ADX сила тренду
        adx = indicators.get('adx', [])
        adx_current = adx[-1] if len(adx) > 0 and not pd.isna(adx[-1]) else 0
        trend_strength = "strong" if adx_current > 25 else "weak" if adx_current > 20 else "none"
        
        # Ішимоку сигнал
        tenkan_sen = indicators.get('tenkan_sen', [])
        kijun_sen = indicators.get('kijun_sen', [])
        
        ichimoku_signal = "neutral"
        if len(tenkan_sen) > 0 and len(kijun_sen) > 0:
            tenkan = tenkan_sen[-1] if not pd.isna(tenkan_sen[-1]) else 0
            kijun = kijun_sen[-1] if not pd.isna(kijun_sen[-1]) else 0
            ichimoku_signal = "bullish" if tenkan > kijun else "bearish"
        
        # Свічні паттерни
        morning_star = indicators.get('morning_star', [])
        evening_star = indicators.get('evening_star', [])
        engulfing = indicators.get('engulfing', [])
        
        candle_pattern = "none"
        if len(morning_star) > 0 and morning_star[-1] > 0:
            candle_pattern = "morning_star"
        elif len(evening_star) > 0 and evening_star[-1] > 0:
            candle_pattern = "evening_star"
        elif len(engulfing) > 0 and engulfing[-1] > 0:
            candle_pattern = "bullish_engulfing" if engulfing[-1] > 0 else "bearish_engulfing"
        
        return {
            'ema_trend': ema_trend,
            'ema_alignment': {
                'ema_20_50': "golden" if ema_20_current > ema_50_current else "death",
                'ema_50_200': "golden" if ema_50_current > ema_200_current else "death",
                'all_bullish': ema_20_current > ema_50_current > ema_200_current,
                'all_bearish': ema_20_current < ema_50_current < ema_200_current,
            },
            'trend_strength': trend_strength,
            'adx_value': round(adx_current, 2),
            'ichimoku_signal': ichimoku_signal,
            'candle_pattern': candle_pattern,
            'price_vs_ema': {
                'vs_ema20': round((close[-1] - ema_20_current) / close[-1] * 100, 2) if close[-1] > 0 else 0,
                'vs_ema50': round((close[-1] - ema_50_current) / close[-1] * 100, 2) if close[-1] > 0 else 0,
            }
        }
    
    def generate_trading_signal(self, symbol: str, df: pd.DataFrame, timeframe: str = '1h') -> Dict:
        """Генерація професійного торгового сигналу"""
        self.logger.info(f"Генерую торговий сигнал для {symbol} на {timeframe}")
        
        if len(df) < self.MIN_CANDLES:
            return self._error_response(symbol, f"Недостатньо даних (потрібно мінімум {self.MIN_CANDLES} свічок)")
        
        try:
            # Розрахунок індикаторів
            indicators = self.calculate_indicators(df, timeframe)
            
            # Поточні ціни
            close = indicators['close']
            high = indicators['high']
            low = indicators['low']
            current_price = close[-1] if len(close) > 0 else 0
            
            if current_price == 0:
                return self._error_response(symbol, "Невірна ціна")
            
            # 1. ОСНОВНИЙ ТРЕНД (30%)
            trend_analysis = self._analyze_trend(df, indicators, current_price)
            
            # 2. МОМЕНТУМ (25%)
            momentum_analysis = self._analyze_momentum(indicators, current_price, trend_analysis['direction'])
            
            # 3. РИЗИК ТА ВОЛАТИЛЬНІСТЬ (20%)
            risk_analysis = self._analyze_risk(df, indicators, current_price)
            
            # 4. ОБСЯГИ (15%)
            volume_analysis = self._analyze_volume(df, indicators)
            
            # 5. СТРУКТУРА (10%)
            structure_analysis = self._analyze_structure(df, indicators)
            
            # Збираємо всі фактори
            all_factors = {
                **trend_analysis['factors'],
                **momentum_analysis['factors'],
                **risk_analysis['factors'],
                **volume_analysis['factors'],
                **structure_analysis['factors'],
            }
            
            # Розрахунок загальної впевненості
            total_confidence = self._calculate_total_confidence(
                trend_analysis, momentum_analysis, risk_analysis, volume_analysis, structure_analysis
            )
            
            # Визначення напрямку
            direction = trend_analysis['direction']
            
            # Перевірка на нейтральний сигнал
            if direction == 'neutral' or total_confidence < 0.45:
                return self._neutral_signal(symbol, current_price, total_confidence, timeframe)
            
            # Аналіз конфліктів
            conflict_score = self._calculate_conflict_score(all_factors)
            
            # Якщо забагато конфліктів - нейтральний
            if conflict_score > 0.4:
                return self._neutral_signal(
                    symbol, current_price, total_confidence * 0.7, timeframe,
                    reason="Багато конфліктів між індикаторами"
                )
            
            # Розрахунок точок входу
            entry_points = self._calculate_entry_points(
                direction, current_price, indicators, df
            )
            
            # Розрахунок TP/SL
            tp_sl_points = self._calculate_tp_sl_points(
                direction, entry_points['optimal_entry'],
                risk_analysis['atr'], indicators, df
            )
            
            # Перевірка мінімального R/R
            risk_reward = self._calculate_risk_reward(
                entry_points['optimal_entry'],
                tp_sl_points['take_profit'],
                tp_sl_points['stop_loss']
            )
            
            if risk_reward < self.MIN_RR:
                return self._neutral_signal(
                    symbol, current_price, total_confidence * 0.8, timeframe,
                    reason=f"R/R {risk_reward:.1f} менше мінімального {self.MIN_RR}"
                )
            
            # Розрахунок розміру позиції
            position_size = self._calculate_position_size(
                entry_points['optimal_entry'],
                tp_sl_points['stop_loss'],
                risk_analysis['volatility'],
                total_confidence
            )
            
            # Очікуваний прибуток
            expected_pnl = self._calculate_expected_pnl(total_confidence, risk_reward, position_size['size_percent'])
            
            # Сила сигналу
            signal_strength = self._determine_signal_strength(total_confidence, conflict_score)
            
            # Додаткові аналізи
            price_action = self.analyze_price_action(df)
            support_resistance = self.calculate_support_resistance(df)
            market_structure = self.analyze_market_structure(df, indicators)
            
            # Пояснення
            explanation = self._generate_explanation(
                symbol, direction, total_confidence, risk_reward,
                trend_analysis, momentum_analysis, conflict_score,
                len([v for v in all_factors.values() if isinstance(v, (int, float)) and v > 0.7])
            )
            
            # Збір всіх даних
            signal = {
                'symbol': symbol,
                'direction': direction,
                'confidence': round(total_confidence, 3),
                'signal_strength': signal_strength,
                'entry_points': entry_points,
                'take_profit': round(tp_sl_points['take_profit'], 4),
                'stop_loss': round(tp_sl_points['stop_loss'], 4),
                'risk_reward': round(risk_reward, 2),
                'expected_pnl_percent': round(expected_pnl, 2),
                'position_size': position_size,
                'timestamp': datetime.now().isoformat(),
                'factors': all_factors,
                'indicators_summary': self._create_indicators_summary(indicators, current_price),
                'price_action': price_action,
                'support_resistance': support_resistance,
                'market_structure': market_structure,
                'explanation': explanation,
                'timeframe': timeframe,
                'conflict_score': round(conflict_score, 2),
                'valid_until': (datetime.now() + timedelta(hours=4)).isoformat(),
            }
            
            # Додаткова валідація
            if not self._validate_signal(signal):
                return self._neutral_signal(
                    symbol, current_price, total_confidence * 0.6, timeframe,
                    reason="Сигнал не пройшов фінальну валідацію"
                )
            
            self.logger.info(f"✅ Сигнал для {symbol}: {direction.upper()}, Confidence: {total_confidence:.1%}, R/R: {risk_reward:.1f}")
            return signal
            
        except Exception as e:
            self.logger.error(f"Помилка генерації сигналу для {symbol}: {str(e)}")
            return self._error_response(symbol, f"Помилка аналізу: {str(e)}")
    
    def _analyze_trend(self, df: pd.DataFrame, indicators: Dict, current_price: float) -> Dict:
        """Детальний аналіз тренду"""
        ema_20 = indicators.get('ema_20', [])
        ema_50 = indicators.get('ema_50', [])
        ema_200 = indicators.get('ema_200', [])
        adx = indicators.get('adx', [])
        
        if len(ema_20) < 2 or len(ema_50) < 2 or len(ema_200) < 2:
            return {'direction': 'neutral', 'score': 0.3, 'factors': {'trend_score': 0.3}}
        
        ema_20_current = ema_20[-1] if not pd.isna(ema_20[-1]) else current_price
        ema_50_current = ema_50[-1] if not pd.isna(ema_50[-1]) else current_price
        ema_200_current = ema_200[-1] if not pd.isna(ema_200[-1]) else current_price
        adx_current = adx[-1] if len(adx) > 0 and not pd.isna(adx[-1]) else 0
        
        # Визначення напрямку
        if ema_20_current > ema_50_current > ema_200_current and adx_current > 20:
            direction = 'long'
            # Сила тренду
            if ema_200_current == 0:
                trend_strength = 0
            else:
                trend_strength = min(1.0, (ema_20_current - ema_200_current) / ema_200_current * 3)
            score = 0.6 + trend_strength * 0.4
            
        elif ema_20_current < ema_50_current < ema_200_current and adx_current > 20:
            direction = 'short'
            if ema_20_current == 0:
                trend_strength = 0
            else:
                trend_strength = min(1.0, (ema_200_current - ema_20_current) / ema_20_current * 3)
            score = 0.6 + trend_strength * 0.4
            
        else:
            # Аналіз консолідації
            recent_close = df['close'].values[-20:]
            if len(recent_close) > 0:
                price_range = np.max(recent_close) - np.min(recent_close)
                range_percent = price_range / current_price if current_price > 0 else 0
            else:
                range_percent = 0
            
            if range_percent < 0.01:  # Дуже вузький діапазон
                direction = 'neutral'
                score = 0.2
            else:
                # Слабкий тренд
                if ema_20_current > ema_50_current:
                    direction = 'long'
                    score = 0.4
                else:
                    direction = 'short'
                    score = 0.4
        
        return {
            'direction': direction,
            'score': round(score, 3),
            'factors': {
                'trend_score': round(score, 3),
                'ema_alignment': f"{ema_20_current:.2f}/{ema_50_current:.2f}/{ema_200_current:.2f}",
                'adx_strength': round(adx_current, 1),
            }
        }
    
    def _analyze_momentum(self, indicators: Dict, current_price: float, direction: str) -> Dict:
        """Аналіз моментуму"""
        factors = {}
        scores = []
        
        # RSI
        rsi = indicators.get('rsi', [])
        if len(rsi) > 0:
            rsi_current = rsi[-1] if not pd.isna(rsi[-1]) else 50
            factors['rsi_level'] = round(rsi_current, 1)
            
            if direction == 'long':
                if rsi_current < 35:
                    rsi_score = 0.9
                elif rsi_current < 45:
                    rsi_score = 0.8
                elif rsi_current < 55:
                    rsi_score = 0.6
                elif rsi_current < 65:
                    rsi_score = 0.4
                else:
                    rsi_score = 0.2
            else:  # short
                if rsi_current > 65:
                    rsi_score = 0.9
                elif rsi_current > 55:
                    rsi_score = 0.8
                elif rsi_current > 45:
                    rsi_score = 0.6
                elif rsi_current > 35:
                    rsi_score = 0.4
                else:
                    rsi_score = 0.2
            
            scores.append(('rsi', rsi_score, 0.3))
        
        # MACD
        macd_hist = indicators.get('macd_hist', [])
        if len(macd_hist) > 5:
            macd_current = macd_hist[-1] if not pd.isna(macd_hist[-1]) else 0
            macd_trend = np.mean([x for x in macd_hist[-5:] if not pd.isna(x)])
            factors['macd_hist'] = round(macd_current, 4)
            
            if direction == 'long' and macd_current > 0 and macd_trend > 0:
                macd_score = 0.8 + min(0.2, abs(macd_current) / max(current_price, 1) * 1000)
            elif direction == 'short' and macd_current < 0 and macd_trend < 0:
                macd_score = 0.8 + min(0.2, abs(macd_current) / max(current_price, 1) * 1000)
            else:
                macd_score = 0.3
            
            scores.append(('macd', macd_score, 0.25))
        
        # Stochastic
        stoch_k = indicators.get('stoch_k', [])
        if len(stoch_k) > 0:
            stoch_current = stoch_k[-1] if not pd.isna(stoch_k[-1]) else 50
            factors['stoch_rsi_level'] = round(stoch_current, 1)
            
            if direction == 'long':
                if stoch_current < 25:
                    stoch_score = 0.9
                elif stoch_current < 35:
                    stoch_score = 0.8
                elif stoch_current < 70:
                    stoch_score = 0.6
                else:
                    stoch_score = 0.3
            else:  # short
                if stoch_current > 75:
                    stoch_score = 0.9
                elif stoch_current > 65:
                    stoch_score = 0.8
                elif stoch_current > 30:
                    stoch_score = 0.6
                else:
                    stoch_score = 0.3
            
            scores.append(('stoch', stoch_score, 0.2))
        
        # CCI
        cci = indicators.get('cci', [])
        if len(cci) > 0:
            cci_current = cci[-1] if not pd.isna(cci[-1]) else 0
            factors['cci_level'] = round(cci_current, 1)
            
            if direction == 'long' and cci_current < -100:
                cci_score = 0.9
            elif direction == 'short' and cci_current > 100:
                cci_score = 0.9
            elif -100 < cci_current < 100:
                cci_score = 0.5
            else:
                cci_score = 0.3
            
            scores.append(('cci', cci_score, 0.15))
        
        # Williams %R
        williams_r = indicators.get('williams_r', [])
        if len(williams_r) > 0:
            williams_current = williams_r[-1] if not pd.isna(williams_r[-1]) else -50
            factors['williams_r'] = round(williams_current, 1)
            
            if direction == 'long' and williams_current < -80:
                williams_score = 0.9
            elif direction == 'short' and williams_current > -20:
                williams_score = 0.9
            elif -80 <= williams_current <= -20:
                williams_score = 0.5
            else:
                williams_score = 0.3
            
            scores.append(('williams', williams_score, 0.1))
        
        # Розрахунок загального скора
        if scores:
            momentum_score = sum(score * weight for _, score, weight in scores)
        else:
            momentum_score = 0.3
        
        return {
            'score': round(momentum_score, 3),
            'factors': factors
        }
    
    def _analyze_risk(self, df: pd.DataFrame, indicators: Dict, current_price: float) -> Dict:
        """Аналіз ризику та волатильності"""
        factors = {}
        
        # ATR
        atr = indicators.get('atr', [])
        if len(atr) > 0:
            atr_current = atr[-1] if not pd.isna(atr[-1]) else 0
            atr_percent = (atr_current / current_price * 100) if current_price > 0 else 0
            factors['atr_percent'] = round(atr_percent, 2)
            
            # Оптимальна волатильність
            if 0.5 < atr_percent < 2.5:
                volatility_score = 0.9
            elif 2.5 <= atr_percent < 4:
                volatility_score = 0.7
            elif atr_percent < 0.5:
                volatility_score = 0.5
            else:
                volatility_score = 0.3
            
            factors['volatility_score'] = round(volatility_score, 3)
        else:
            atr_current = 0
            volatility_score = 0.5
        
        # Bollinger Bands
        bb_upper = indicators.get('bb_upper', [])
        bb_lower = indicators.get('bb_lower', [])
        
        if len(bb_upper) > 0 and len(bb_lower) > 0:
            bb_upper_current = bb_upper[-1] if not pd.isna(bb_upper[-1]) else current_price * 1.02
            bb_lower_current = bb_lower[-1] if not pd.isna(bb_lower[-1]) else current_price * 0.98
            
            # Позиція відносно BB
            bb_width = bb_upper_current - bb_lower_current
            if bb_width > 0:
                bb_position = (current_price - bb_lower_current) / bb_width
            else:
                bb_position = 0.5
                
            factors['bollinger_position'] = round(bb_position, 3)
            
            # Оцінка позиції
            if bb_position < 0.15:
                bb_score = 0.9 if current_price > bb_lower_current else 0.6
            elif bb_position > 0.85:
                bb_score = 0.9 if current_price < bb_upper_current else 0.6
            elif 0.35 < bb_position < 0.65:
                bb_score = 0.7
            else:
                bb_score = 0.5
        else:
            bb_score = 0.5
        
        # Загальна оцінка ризику
        risk_score = (volatility_score * 0.6 + bb_score * 0.4)
        
        return {
            'score': round(risk_score, 3),
            'atr': atr_current,
            'volatility': volatility_score,
            'factors': factors
        }
    
    def _analyze_volume(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """Аналіз обсягів"""
        factors = {}
        volume = df['volume'].values
        
        if len(volume) < 20:
            return {'score': 0.5, 'factors': {'volume_ratio': 1.0}}
        
        current_volume = volume[-1]
        avg_volume_20 = np.mean(volume[-20:])
        
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0
        factors['volume_ratio'] = round(volume_ratio, 2)
        
        # OBV тренд
        obv = indicators.get('obv', [])
        if len(obv) > 10:
            obv_current = obv[-1] if not pd.isna(obv[-1]) else 0
            obv_10 = obv[-10] if len(obv) > 10 and not pd.isna(obv[-10]) else 0
            obv_trend = "bullish" if obv_current > obv_10 else "bearish"
            factors['obv_trend'] = obv_trend
        
        # MFI
        mfi = indicators.get('mfi', [])
        if len(mfi) > 0:
            mfi_current = mfi[-1] if not pd.isna(mfi[-1]) else 50
            factors['mfi_level'] = round(mfi_current, 1)
        
        # VWAP позиція
        vwap = indicators.get('vwap', [])
        if len(vwap) > 0:
            vwap_current = vwap[-1] if not pd.isna(vwap[-1]) else 0
            vwap_position = "above" if current_volume > vwap_current else "below"
            factors['vwap_position'] = vwap_position
        
        # Оцінка обсягів
        if volume_ratio > 1.8:
            volume_score = 0.9
        elif volume_ratio > 1.4:
            volume_score = 0.8
        elif volume_ratio > 1.0:
            volume_score = 0.7
        elif volume_ratio > 0.7:
            volume_score = 0.6
        else:
            volume_score = 0.4
        
        return {
            'score': round(volume_score, 3),
            'factors': factors
        }
    
    def _analyze_structure(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """Аналіз структури ринку"""
        factors = {}
        scores = []
        
        # Ішимоку
        tenkan_sen = indicators.get('tenkan_sen', [])
        kijun_sen = indicators.get('kijun_sen', [])
        
        if len(tenkan_sen) > 0 and len(kijun_sen) > 0:
            tenkan = tenkan_sen[-1] if not pd.isna(tenkan_sen[-1]) else 0
            kijun = kijun_sen[-1] if not pd.isna(kijun_sen[-1]) else 0
            
            if tenkan > kijun:
                ichimoku_score = 0.8
                factors['ichimoku_signal'] = 'bullish'
            else:
                ichimoku_score = 0.2
                factors['ichimoku_signal'] = 'bearish'
            
            scores.append(('ichimoku', ichimoku_score, 0.4))
        
        # Свічні паттерни
        morning_star = indicators.get('morning_star', [])
        evening_star = indicators.get('evening_star', [])
        engulfing = indicators.get('engulfing', [])
        
        pattern_score = 0.5
        if len(morning_star) > 0 and morning_star[-1] > 0:
            pattern_score = 0.9
            factors['candle_pattern'] = 'morning_star'
        elif len(evening_star) > 0 and evening_star[-1] > 0:
            pattern_score = 0.1
            factors['candle_pattern'] = 'evening_star'
        elif len(engulfing) > 0:
            if engulfing[-1] > 0:
                pattern_score = 0.8
                factors['candle_pattern'] = 'bullish_engulfing'
            else:
                pattern_score = 0.2
                factors['candle_pattern'] = 'bearish_engulfing'
        
        scores.append(('pattern', pattern_score, 0.3))
        
        # Структурна оцінка
        structure_score = sum(score * weight for _, score, weight in scores) if scores else 0.5
        
        return {
            'score': round(structure_score, 3),
            'factors': factors
        }
    
    def _calculate_conflict_score(self, factors: Dict) -> float:
        """Розрахунок рівня конфліктів між індикаторами"""
        conflicts = 0
        total_checks = 0
        
        # RSI vs Тренд
        if 'rsi_level' in factors and 'trend_score' in factors:
            rsi = factors['rsi_level']
            trend = factors['trend_score']
            
            if rsi > 65 and trend > 0.7:  # Перекупленість + буличний тренд
                conflicts += 1
            elif rsi < 35 and trend < 0.3:  # Перепроданість + ведмежий тренд
                conflicts += 1
            total_checks += 1
        
        # MACD vs Напрямок
        if 'macd_hist' in factors:
            macd = factors['macd_hist']
            if 'trend_score' in factors:
                trend = factors['trend_score']
                if macd > 0 and trend < 0.3:  # MACD позитивний + ведмежий тренд
                    conflicts += 1
                elif macd < 0 and trend > 0.7:  # MACD негативний + буличний тренд
                    conflicts += 1
                total_checks += 1
        
        # Обсяги vs Напрямок
        if 'volume_ratio' in factors and 'obv_trend' in factors:
            volume_ratio = factors['volume_ratio']
            obv_trend = factors['obv_trend']
            
            if volume_ratio < 0.7 and obv_trend == 'bullish':  # Низькі обсяги + буличний OBV
                conflicts += 1
            total_checks += 1
        
        # Ішимоку vs Напрямок
        if 'ichimoku_signal' in factors and 'trend_score' in factors:
            ichimoku = factors['ichimoku_signal']
            trend = factors['trend_score']
            
            if ichimoku == 'bearish' and trend > 0.7:
                conflicts += 1
            elif ichimoku == 'bullish' and trend < 0.3:
                conflicts += 1
            total_checks += 1
        
        return conflicts / max(total_checks, 1)
    
    def _calculate_entry_points(self, direction: str, current_price: float, 
                               indicators: Dict, df: pd.DataFrame) -> Dict:
        """Розрахунок точок входу"""
        # Пошук найкращих точок входу на основі підтримки/опору
        support_resistance = self.calculate_support_resistance(df)
        
        if direction == 'long':
            # Для лонга: входимо на підтримці
            if support_resistance['nearest_support']:
                optimal_entry = support_resistance['nearest_support']
            else:
                optimal_entry = current_price * 0.995
            
            # Діапазон входу
            entry_range = [
                round(optimal_entry * 0.99, 4),   # Нижня межа
                round(optimal_entry * 1.01, 4)    # Верхня межа
            ]
            
            # Стратегія входу
            strategy = "limit_on_support"
            confidence_zones = {
                'high_confidence': round(optimal_entry * 0.995, 4),
                'medium_confidence': round(optimal_entry, 4),
                'low_confidence': round(optimal_entry * 1.005, 4),
            }
            
        else:  # short
            # Для шорта: входимо на опорі
            if support_resistance['nearest_resistance']:
                optimal_entry = support_resistance['nearest_resistance']
            else:
                optimal_entry = current_price * 1.005
            
            # Діапазон входу
            entry_range = [
                round(optimal_entry * 0.99, 4),   # Нижня межа
                round(optimal_entry * 1.01, 4)    # Верхня межа
            ]
            
            # Стратегія входу
            strategy = "limit_on_resistance"
            confidence_zones = {
                'high_confidence': round(optimal_entry * 1.005, 4),
                'medium_confidence': round(optimal_entry, 4),
                'low_confidence': round(optimal_entry * 0.995, 4),
            }
        
        # Рекомендації по входу
        recommendations = {
            'immediate_action': 'place_limit_order' if abs(current_price - optimal_entry) / current_price < 0.02 else 'wait_for_price',
            'order_type': 'limit',
            'time_window_hours': 4,
            'scaling_in': {
                'first_entry': 0.6,   # 60% на оптимальній точці
                'second_entry': 0.3,  # 30% на pullback
                'third_entry': 0.1    # 10% на пробої
            }
        }
        
        return {
            'optimal_entry': round(optimal_entry, 4),
            'entry_range': entry_range,
            'strategy': strategy,
            'confidence_zones': confidence_zones,
            'recommendations': recommendations,
            'distance_to_entry_pct': round(abs(current_price - optimal_entry) / current_price * 100, 2)
        }
    
    def _calculate_tp_sl_points(self, direction: str, entry: float, atr: float, 
                               indicators: Dict, df: pd.DataFrame) -> Dict:
        """Розрахунок Take Profit та Stop Loss з врахуванням структури"""
        support_resistance = self.calculate_support_resistance(df)
        
        if direction == 'long':
            # TP: найближчий опір або ATR-based
            if support_resistance['nearest_resistance']:
                take_profit = min(
                    support_resistance['nearest_resistance'] * 0.995,
                    entry + (atr * 3.0)
                )
            else:
                take_profit = entry + (atr * 3.0)
            
            # SL: найближча підтримка або ATR-based
            if support_resistance['nearest_support']:
                stop_loss = max(
                    support_resistance['nearest_support'] * 1.005,
                    entry - (atr * 1.0)
                )
            else:
                stop_loss = entry - (atr * 1.0)
        else:  # short
            # TP: найближча підтримка або ATR-based
            if support_resistance['nearest_support']:
                take_profit = max(
                    support_resistance['nearest_support'] * 1.005,
                    entry - (atr * 3.0)
                )
            else:
                take_profit = entry - (atr * 3.0)
            
            # SL: найближчий опір або ATR-based
            if support_resistance['nearest_resistance']:
                stop_loss = min(
                    support_resistance['nearest_resistance'] * 0.995,
                    entry + (atr * 1.0)
                )
            else:
                stop_loss = entry + (atr * 1.0)
        
        # Гарантуємо мінімальну відстань
        min_distance = entry * 0.002  # Мінімум 0.2%
        if abs(take_profit - entry) < min_distance:
            take_profit = entry + min_distance if direction == 'long' else entry - min_distance
        
        if abs(stop_loss - entry) < min_distance:
            stop_loss = entry - min_distance if direction == 'long' else entry + min_distance
        
        return {
            'take_profit': round(take_profit, 4),
            'stop_loss': round(stop_loss, 4),
            'tp_distance_pct': round(abs(take_profit - entry) / entry * 100, 2),
            'sl_distance_pct': round(abs(stop_loss - entry) / entry * 100, 2),
        }
    
    def _calculate_total_confidence(self, trend: Dict, momentum: Dict, risk: Dict, 
                                   volume: Dict, structure: Dict) -> float:
        """Розрахунок загальної впевненості"""
        weights = {
            'trend': 0.30,
            'momentum': 0.25,
            'risk': 0.20,
            'volume': 0.15,
            'structure': 0.10,
        }
        
        total = (
            trend['score'] * weights['trend'] +
            momentum['score'] * weights['momentum'] +
            risk['score'] * weights['risk'] +
            volume['score'] * weights['volume'] +
            structure['score'] * weights['structure']
        )
        
        # Корекція за консистентність
        scores = [trend['score'], momentum['score'], risk['score'], volume['score'], structure['score']]
        avg_score = np.mean(scores)
        std_score = np.std(scores)
        
        if std_score < 0.1:
            total *= 1.1  # Бонус за узгодженість
        elif std_score > 0.25:
            total *= 0.9  # Покарання за розбіжності
        
        return round(min(1.0, max(0.0, total)), 3)
    
    def _calculate_risk_reward(self, entry: float, take_profit: float, stop_loss: float) -> float:
        """Розрахунок співвідношення ризик/прибуток"""
        if entry == 0:
            return 1.0
        
        profit = abs(take_profit - entry)
        risk = abs(stop_loss - entry)
        
        if risk == 0:
            return 1.0
        
        return round(profit / risk, 2)
    
    def _calculate_expected_pnl(self, confidence: float, risk_reward: float, 
                               position_size_percent: float) -> float:
        """Розрахунок очікуваного прибутку"""
        win_probability = confidence
        loss_probability = 1 - win_probability
        
        # Очікуване значення (математичне очікування)
        expected_value = (win_probability * risk_reward) - (loss_probability * 1)
        
        # Очікуваний прибуток у відсотках від капіталу
        expected_pnl = expected_value * (position_size_percent / 100)
        
        return round(max(0, expected_pnl * 100), 2)  # У відсотках
    
    def _calculate_position_size(self, entry: float, stop_loss: float, 
                                volatility_score: float, confidence: float) -> Dict:
        """Розрахунок розміру позиції"""
        if entry == 0 or entry == stop_loss:
            return {
                'size_percent': 0,
                'risk_per_trade': self.BASE_RISK * 100,
                'volatility_adjustment': 1.0,
                'confidence_adjustment': 1.0
            }
        
        # Відстань до стопу
        stop_distance_pct = abs(entry - stop_loss) / entry * 100
        
        if stop_distance_pct == 0:
            return {
                'size_percent': 0,
                'risk_per_trade': self.BASE_RISK * 100,
                'volatility_adjustment': 1.0,
                'confidence_adjustment': 1.0
            }
        
        # Базова формула
        position_size = (self.BASE_RISK * 100) / stop_distance_pct
        
        # Корекція за волатильність
        volatility_adjustment = 1.0
        if volatility_score < 0.4:  # Дуже низька волатильність
            volatility_adjustment = 1.3
        elif volatility_score > 0.8:  # Дуже висока волатильність
            volatility_adjustment = 0.7
        elif volatility_score > 0.6:  # Висока волатильність
            volatility_adjustment = 0.8
        
        # Корекція за впевненість
        confidence_adjustment = 1.0
        if confidence >= 0.8:
            confidence_adjustment = 1.2
        elif confidence >= 0.7:
            confidence_adjustment = 1.1
        elif confidence <= 0.5:
            confidence_adjustment = 0.7
        elif confidence <= 0.6:
            confidence_adjustment = 0.8
        
        # Фінальний розрахунок
        position_size = position_size * volatility_adjustment * confidence_adjustment
        position_size = min(position_size, self.MAX_POSITION)
        
        return {
            'size_percent': round(position_size, 2),
            'risk_per_trade': round(self.BASE_RISK * 100, 2),
            'volatility_adjustment': round(volatility_adjustment, 2),
            'confidence_adjustment': round(confidence_adjustment, 2),
            'max_position_percent': self.MAX_POSITION,
            'stop_distance_pct': round(stop_distance_pct, 2)
        }
    
    def _determine_signal_strength(self, confidence: float, conflict_score: float) -> str:
        """Визначення сили сигналу"""
        # Корекція за конфлікти
        adjusted_confidence = confidence * (1 - conflict_score * 0.5)
        
        if adjusted_confidence >= 0.75:
            return "strong"
        elif adjusted_confidence >= 0.65:
            return "medium"
        elif adjusted_confidence >= 0.55:
            return "weak"
        else:
            return "very_weak"
    
    def _create_indicators_summary(self, indicators: Dict, current_price: float) -> Dict:
        """Створення підсумку індикаторів"""
        summary = {}
        
        # RSI
        rsi = indicators.get('rsi', [])
        if len(rsi) > 0:
            rsi_current = rsi[-1]
            if not pd.isna(rsi_current):
                summary['rsi'] = round(rsi_current, 1)
        
        # MACD
        macd_hist = indicators.get('macd_hist', [])
        if len(macd_hist) > 0:
            macd_current = macd_hist[-1]
            if not pd.isna(macd_current):
                summary['macd_hist'] = round(macd_current, 5)
        
        # Stochastic
        stoch_k = indicators.get('stoch_k', [])
        if len(stoch_k) > 0:
            stoch_current = stoch_k[-1]
            if not pd.isna(stoch_current):
                summary['stoch_rsi'] = round(stoch_current, 1)
        
        # ATR
        atr = indicators.get('atr', [])
        if len(atr) > 0 and current_price > 0:
            atr_current = atr[-1]
            if not pd.isna(atr_current):
                summary['atr_percent'] = round((atr_current / current_price * 100), 2)
        
        # ADX
        adx = indicators.get('adx', [])
        if len(adx) > 0:
            adx_current = adx[-1]
            if not pd.isna(adx_current):
                summary['adx'] = round(adx_current, 1)
        
        # Обсяги
        volume_ratio = None
        volume = indicators.get('volume', [])
        volume_sma = indicators.get('volume_sma', [])
        if len(volume) > 0 and len(volume_sma) > 0 and volume_sma[-1] > 0:
            volume_ratio = volume[-1] / volume_sma[-1]
            summary['volume_ratio'] = round(volume_ratio, 2)
        
        # Волатильність
        natr = indicators.get('natr', [])
        if len(natr) > 0:
            natr_current = natr[-1]
            if not pd.isna(natr_current):
                summary['natr'] = round(natr_current, 2)
        
        return summary
    
    def _generate_explanation(self, symbol: str, direction: str, confidence: float, 
                             risk_reward: float, trend: Dict, momentum: Dict, 
                             conflict_score: float, positive_factors: int) -> str:
        """Генерація пояснення сигналу"""
        direction_text = "ЛОНГ" if direction == 'long' else "ШОРТ"
        confidence_pct = int(confidence * 100)
        
        # Визначення сили
        if confidence >= 0.75:
            strength = "🟢 **ВИСОКОЯКІСНИЙ**"
            recommendation = "🎯 Рекомендовано для торгівлі"
        elif confidence >= 0.65:
            strength = "🟡 **ЯКІСНИЙ**"
            recommendation = "👍 Можна торгувати"
        elif confidence >= 0.55:
            strength = "🟠 **СЕРЕДНІЙ**"
            recommendation = "🤔 Обережність, малий розмір"
        else:
            strength = "🔴 **РИЗИКОВАНИЙ**"
            recommendation = "⚠️ Тільки для досвідчених"
        
        # Основа для пояснення
        explanation = f"{strength} {direction_text} СИГНАЛ для {symbol}\n"
        explanation += f"• Впевненість AI: {confidence_pct}%\n"
        explanation += f"• Ризик/Прибуток: 1:{risk_reward:.1f}\n"
        explanation += f"• Позитивних факторів: {positive_factors}\n"
        explanation += f"• Конфліктів: {int(conflict_score * 100)}%\n"
        explanation += f"• {recommendation}"
        
        # Додаткові деталі
        if risk_reward >= 3:
            explanation += f"\n• 📈 Відмінне R/R співвідношення"
        if conflict_score < 0.2:
            explanation += f"\n• ✅ Індикатори узгоджені"
        elif conflict_score > 0.3:
            explanation += f"\n• ⚠️ Є конфлікти між індикаторами"
        
        return explanation
    
    def _validate_signal(self, signal: Dict) -> bool:
        """Фінальна валідація сигналу"""
        # Мінімальні вимоги
        if signal['confidence'] < 0.5:
            return False
        
        if signal['risk_reward'] < self.MIN_RR:
            return False
        
        if signal['conflict_score'] > 0.4:
            return False
        
        # Перевірка на розумність TP/SL
        tp_distance = abs(signal['take_profit'] - signal['entry_points']['optimal_entry'])
        sl_distance = abs(signal['stop_loss'] - signal['entry_points']['optimal_entry'])
        
        if tp_distance == 0 or sl_distance == 0:
            return False
        
        # Перевірка мінімальної відстані
        min_distance = signal['entry_points']['optimal_entry'] * 0.001
        if tp_distance < min_distance or sl_distance < min_distance:
            return False
        
        return True
    
    def _neutral_signal(self, symbol: str, current_price: float, 
                       confidence: float, timeframe: str, reason: str = None) -> Dict:
        """Повернення нейтрального сигналу"""
        explanation = f"🔶 НЕЙТРАЛЬНИЙ СИГНАЛ для {symbol}"
        if reason:
            explanation += f"\n• Причина: {reason}"
        explanation += f"\n• Впевненість: {int(confidence * 100)}%"
        explanation += f"\n• Рекомендація: Чекати кращих умов"
        
        return {
            'symbol': symbol,
            'direction': 'neutral',
            'confidence': round(confidence, 3),
            'signal_strength': 'very_weak',
            'entry_points': {
                'optimal_entry': round(current_price, 4),
                'entry_range': [round(current_price * 0.99, 4), round(current_price * 1.01, 4)],
                'strategy': 'wait',
                'distance_to_entry_pct': 0
            },
            'take_profit': round(current_price, 4),
            'stop_loss': round(current_price, 4),
            'risk_reward': 1.0,
            'expected_pnl_percent': 0.0,
            'position_size': {
                'size_percent': 0,
                'risk_per_trade': round(self.BASE_RISK * 100, 2),
                'volatility_adjustment': 1.0,
                'confidence_adjustment': 1.0
            },
            'timestamp': datetime.now().isoformat(),
            'factors': {},
            'indicators_summary': {},
            'explanation': explanation,
            'timeframe': timeframe,
            'conflict_score': 0.5,
            'valid_until': (datetime.now() + timedelta(hours=2)).isoformat(),
        }
    
    def _error_response(self, symbol: str, error_msg: str) -> Dict:
        """Повернення сигналу з помилкою"""
        return {
            'symbol': symbol,
            'direction': 'neutral',
            'confidence': 0.0,
            'signal_strength': 'error',
            'entry_points': {'optimal_entry': 0},
            'take_profit': 0.0,
            'stop_loss': 0.0,
            'risk_reward': 1.0,
            'expected_pnl_percent': 0.0,
            'position_size': {'size_percent': 0},
            'timestamp': datetime.now().isoformat(),
            'factors': {},
            'indicators_summary': {},
            'error': error_msg,
            'explanation': f"❌ ПОМИЛКА АНАЛІЗУ: {error_msg}",
            'timeframe': '1h',
        }