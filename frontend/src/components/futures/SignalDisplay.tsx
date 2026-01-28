// frontend/src/components/futures/SignalDisplay.tsx
import React, { useState } from 'react';

interface SignalDisplayProps {
  signal: any;
  onTrack: () => void;
  loading: boolean;
  analyzing: boolean;
  onTimeframeChange?: (timeframe: string) => void;
}

// Форматування ціни
const formatPrice = (price: number): string => {
  if (!price && price !== 0) return '-';
  if (price >= 1000) return price.toLocaleString('en-US', { maximumFractionDigits: 0 });
  if (price >= 1) return price.toLocaleString('en-US', { maximumFractionDigits: 2 });
  return price.toLocaleString('en-US', { maximumFractionDigits: 4 });
};

// Розрахунок відсотків
const calculatePercentage = (entry: number, target: number): string => {
  if (!entry || entry === 0 || !target) return '0%';
  const change = ((target - entry) / entry) * 100;
  const sign = change >= 0 ? '+' : '';
  return `${sign}${Math.abs(change).toFixed(2)}%`;
};

// Розрахунок реального R/R
const calculateRealRR = (entry: number, tp: number, sl: number): number => {
  if (!entry || entry === 0 || !tp || !sl) return 1.0;
  const profit = Math.abs(tp - entry);
  const risk = Math.abs(sl - entry);
  if (risk === 0) return 1.0;
  return Number((profit / risk).toFixed(2));
};

// Розрахунок ймовірності
const calculateSuccessProbability = (signal: any, realRR: number): number => {
  if (!signal) return 50;
  
  const confidence = signal.confidence || 0;
  const conflict = signal.conflict_score || 0;
  
  let probability = confidence * 100;
  probability *= (1 - conflict * 0.3);
  
  if (realRR >= 3) probability *= 1.15;
  else if (realRR >= 2.5) probability *= 1.1;
  else if (realRR >= 2) probability *= 1.05;
  
  return Math.max(40, Math.min(90, Math.round(probability)));
};

// Переклад ключів факторів
const translateFactorKey = (key: string): string => {
  const translations: Record<string, string> = {
    // Тренд
    'trend_score': 'Тренд',
    'ema_alignment': 'EMA',
    'adx_strength': 'ADX',
    
    // Моментум
    'rsi_level': 'RSI',
    'macd_hist': 'MACD',
    'stoch_rsi_level': 'Stoch RSI',
    'cci_level': 'CCI',
    'williams_r': 'Williams %R',
    'momentum_score': 'Моментум',
    
    // Ризик
    'atr_percent': 'ATR',
    'bollinger_position': 'Bollinger',
    'volatility_score': 'Волатильність',
    
    // Обсяги
    'volume_ratio': 'Обсяги',
    'obv_trend': 'OBV',
    'vwap_position': 'VWAP',
    'volume_confirmation': 'Обсяги',
    
    // Структура
    'ichimoku_signal': 'Ішимоку',
    'candle_pattern': 'Свечний паттерн',
    'structure_score': 'Структура',
    
    // Додатково
    'confirmation_ratio': 'Підтвердження',
    'mfi_level': 'MFI'
  };
  
  return translations[key] || key.replace(/_/g, ' ');
};

// Правильна інтерпретація значень
const interpretValue = (key: string, value: any) => {
  const num = Number(value);
  
  if (typeof value === 'string') {
    if (value.includes('bullish') || value === 'green') {
      return { color: 'text-green-400', icon: '🟢' };
    }
    if (value.includes('bearish') || value === 'red') {
      return { color: 'text-red-400', icon: '🔴' };
    }
    return { color: 'text-gray-400', icon: '📊' };
  }
  
  // Для чисел
  if (key.includes('_score') || key.includes('_ratio')) {
    if (num >= 0.8) return { color: 'text-green-400', icon: '🟢' };
    if (num >= 0.6) return { color: 'text-yellow-400', icon: '🟡' };
    return { color: 'text-red-400', icon: '🔴' };
  }
  
  if (key.includes('rsi_level') || key.includes('rsi')) {
    if (num > 70) return { color: 'text-red-400', icon: '🔴' };
    if (num < 30) return { color: 'text-green-400', icon: '🟢' };
    return { color: 'text-yellow-400', icon: '🟡' };
  }
  
  if (key.includes('stoch')) {
    if (num > 80) return { color: 'text-red-400', icon: '🔴' };
    if (num < 20) return { color: 'text-green-400', icon: '🟢' };
    return { color: 'text-yellow-400', icon: '🟡' };
  }
  
  if (key.includes('macd_hist')) {
    if (num > 0) return { color: 'text-green-400', icon: '📈' };
    if (num < 0) return { color: 'text-red-400', icon: '📉' };
    return { color: 'text-gray-400', icon: '📊' };
  }
  
  if (key.includes('cci')) {
    if (num > 100) return { color: 'text-green-400', icon: '🟢' };
    if (num < -100) return { color: 'text-red-400', icon: '🔴' };
    return { color: 'text-yellow-400', icon: '🟡' };
  }
  
  if (key.includes('williams')) {
    if (num > -20) return { color: 'text-red-400', icon: '🔴' };
    if (num < -80) return { color: 'text-green-400', icon: '🟢' };
    return { color: 'text-yellow-400', icon: '🟡' };
  }
  
  if (key.includes('atr_percent')) {
    if (num > 3) return { color: 'text-red-400', icon: '⚡' };
    if (num > 1) return { color: 'text-yellow-400', icon: '📊' };
    return { color: 'text-green-400', icon: '📉' };
  }
  
  return { color: 'text-gray-300', icon: '📊' };
};

// Функція для розрахунку реального очікуваного прибутку
const calculateExpectedProfit = (signal: any, realRR: number): number => {
  const confidence = signal.confidence || 0.5;
  const positionSize = signal.position_size?.size_percent || 2.0;
  
  // Формула: (ймовірність * прибуток - ймовірність збитку * 1) * розмір позиції
  const winProb = confidence;
  const lossProb = 1 - winProb;
  
  const expectedValue = (winProb * realRR) - (lossProb * 1);
  const expectedProfit = expectedValue * (positionSize / 100) * 100;
  
  return Math.max(0, Number(expectedProfit.toFixed(2)));
};

const SignalDisplay: React.FC<SignalDisplayProps> = ({ 
  signal, 
  onTrack, 
  loading,
  analyzing,
  onTimeframeChange
}) => {
  const [showFactors, setShowFactors] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  // Завантаження
  if (analyzing) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <h3 className="text-lg font-medium mb-1">🤖 AI аналіз...</h3>
        <p className="text-sm text-gray-400">150+ свічок • 20+ індикаторів</p>
      </div>
    );
  }

  // Немає сигналу
  if (!signal || signal.error) {
    return (
      <div className="text-center py-10">
        <div className="text-5xl mb-3">🎯</div>
        <h3 className="text-lg font-medium mb-2">Професійний AI аналіз</h3>
        <p className="text-sm text-gray-400 mb-4">Оберіть актив для генерації сигналу</p>
        
        {onTimeframeChange && (
          <div className="flex justify-center gap-2">
            {['15m', '1h', '4h', '1d'].map((tf) => (
              <button
                key={tf}
                onClick={() => onTimeframeChange(tf)}
                className="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                {tf}
              </button>
            ))}
          </div>
        )}
        
        {signal?.error && (
          <div className="mt-4 p-3 bg-red-900/20 rounded-lg max-w-md mx-auto">
            <p className="text-red-300 text-sm">{signal.error}</p>
          </div>
        )}
      </div>
    );
  }

  // --- РОЗРАХУНКИ ---
  const isLong = signal.direction === 'long';
  const isNeutral = signal.direction === 'neutral';
  
  const entryPrice = signal.entry_points?.optimal_entry || signal.entry_price || 0;
  const currentPrice = signal.current_price || entryPrice || 0;
  const takeProfit = signal.take_profit || 0;
  const stopLoss = signal.stop_loss || 0;
  
  // Реальні розрахунки
  const realRR = calculateRealRR(entryPrice, takeProfit, stopLoss);
  const confidence = Math.round((signal.confidence || 0) * 100);
  const successProb = calculateSuccessProbability(signal, realRR);
  const lossProb = 100 - successProb;
  const expectedProfit = calculateExpectedProfit(signal, realRR);
  
  const positionSize = signal.position_size?.size_percent || 2.0;
  const riskPerTrade = signal.position_size?.risk_per_trade || 2.0;

  // --- СТИЛІ ---
  const signalColor = isLong ? 'green' : isNeutral ? 'yellow' : 'red';
  const colorClasses = {
    green: {
      bg: 'bg-green-900/20',
      border: 'border-green-700/50',
      text: 'text-green-400',
      gradient: 'from-green-600 to-emerald-600'
    },
    yellow: {
      bg: 'bg-yellow-900/20', 
      border: 'border-yellow-700/50',
      text: 'text-yellow-400',
      gradient: 'from-yellow-600 to-amber-600'
    },
    red: {
      bg: 'bg-red-900/20',
      border: 'border-red-700/50',
      text: 'text-red-400',
      gradient: 'from-red-600 to-red-700'
    }
  };
  
  const colors = colorClasses[signalColor];

  return (
    <div className="space-y-4">
      {/* ===== ЗАГОЛОВОК СИГНАЛУ ===== */}
      <div className={`p-4 rounded-xl ${colors.bg} border ${colors.border}`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className={`text-2xl ${colors.text}`}>
              {isLong ? '📈' : isNeutral ? '⚖️' : '📉'}
            </div>
            <div>
              <h3 className={`text-xl font-bold ${colors.text}`}>
                {isLong ? 'LONG' : isNeutral ? 'NEUTRAL' : 'SHORT'} {signal.symbol}
              </h3>
              <p className="text-sm text-gray-400">
                TF: {signal.timeframe} • AI: {confidence}% • R/R: 1:{realRR}
              </p>
            </div>
          </div>
          
          {/* Поточна ціна */}
          <div className="text-right">
            <div className="text-lg font-bold">${formatPrice(currentPrice)}</div>
            <div className="text-sm text-gray-400">Поточна ціна</div>
          </div>
        </div>
        
        {/* Пояснення */}
        {signal.explanation && (
          <div className="mt-3 pt-3 border-t border-gray-700/50">
            <p className="text-sm text-gray-300">{signal.explanation.split('\n')[0]}</p>
          </div>
        )}
      </div>

      {/* ===== ОСНОВНІ МЕТРИКИ ===== */}
      <div className="grid grid-cols-2 gap-3">
        {/* Шанс успіху */}
        <div className="bg-gray-800/50 p-3 rounded-xl">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-gray-400">Шанс успіху</span>
            <span className={`text-sm font-bold ${successProb >= 70 ? 'text-green-400' : successProb >= 60 ? 'text-yellow-400' : 'text-red-400'}`}>
              {successProb}%
            </span>
          </div>
          <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div 
              className={`h-full ${successProb >= 70 ? 'bg-green-500' : successProb >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
              style={{ width: `${successProb}%` }}
            ></div>
          </div>
        </div>
        
        {/* Очікуваний прибуток */}
        <div className="bg-gray-800/50 p-3 rounded-xl">
          <div className="text-sm text-gray-400 mb-1">Очікуваний прибуток</div>
          <div className={`text-xl font-bold ${expectedProfit > 1 ? 'text-green-400' : expectedProfit > 0 ? 'text-yellow-400' : 'text-red-400'}`}>
            {expectedProfit > 0 ? '+' : ''}{expectedProfit}%
          </div>
        </div>
      </div>

      {/* ===== ЦІНИ ТА ТОЧКИ ===== */}
      {!isNeutral ? (
        <>
          {/* Точка входу */}
          <div className="bg-gray-800/30 p-3 rounded-xl">
            <div className="text-sm text-gray-400 mb-2">🎯 Точка входу</div>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs text-gray-400">Рекомендована</div>
                <div className="text-lg font-bold">${formatPrice(entryPrice)}</div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-400">Відхилення</div>
                <div className={`text-sm ${currentPrice > entryPrice ? 'text-green-400' : 'text-red-400'}`}>
                  {calculatePercentage(entryPrice, currentPrice)}
                </div>
              </div>
            </div>
          </div>
          
          {/* TP/SL */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-green-900/20 p-3 rounded-xl border border-green-700/50">
              <div className="text-sm text-gray-400 mb-1">Take Profit</div>
              <div className="text-lg font-bold text-green-400">${formatPrice(takeProfit)}</div>
              <div className="text-sm text-green-400">{calculatePercentage(entryPrice, takeProfit)}</div>
            </div>
            
            <div className="bg-red-900/20 p-3 rounded-xl border border-red-700/50">
              <div className="text-sm text-gray-400 mb-1">Stop Loss</div>
              <div className="text-lg font-bold text-red-400">${formatPrice(stopLoss)}</div>
              <div className="text-sm text-red-400">{calculatePercentage(entryPrice, stopLoss)}</div>
            </div>
          </div>
          
          {/* Прогрес бар для TP/SL */}
          <div className="relative h-8 bg-gray-800 rounded-xl overflow-hidden">
            {/* SL зона */}
            <div 
              className="absolute left-0 h-full bg-red-900/30"
              style={{ width: `${Math.min(30, (Math.abs(stopLoss - entryPrice) / Math.abs(takeProfit - entryPrice)) * 50)}%` }}
            ></div>
            
            {/* Поточна ціна маркер */}
            <div 
              className="absolute top-0 bottom-0 w-0.5 bg-white"
              style={{ left: `${((currentPrice - stopLoss) / (takeProfit - stopLoss)) * 100}%` }}
            >
              <div className="absolute -top-2 -left-1.5 w-3 h-3 bg-white rounded-full"></div>
            </div>
            
            {/* TP зона */}
            <div 
              className="absolute right-0 h-full bg-green-900/30"
              style={{ width: `${Math.min(30, 100 - ((currentPrice - stopLoss) / (takeProfit - stopLoss)) * 100)}%` }}
            ></div>
            
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-sm font-bold">
                Поточна: ${formatPrice(currentPrice)}
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-yellow-900/20 p-4 rounded-xl border border-yellow-700/50 text-center">
          <div className="text-2xl mb-2">⚖️</div>
          <h4 className="font-bold text-yellow-400 mb-1">НЕЙТРАЛЬНИЙ СИГНАЛ</h4>
          <p className="text-sm text-gray-300">AI не виявив чітких торгових можливостей</p>
        </div>
      )}

      {/* ===== РИЗИК-МЕНЕДЖМЕНТ ===== */}
      <div className="bg-gray-800/30 p-3 rounded-xl">
        <div className="text-sm text-gray-400 mb-2">🛡️ Ризик-менеджмент</div>
        
        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <div className="text-xs text-gray-400">Розмір позиції</div>
            <div className={`text-lg font-bold ${positionSize > 0 ? 'text-blue-400' : 'text-gray-400'}`}>
              {positionSize}%
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-400">Ризик на угоду</div>
            <div className="text-lg font-bold text-yellow-400">
              {riskPerTrade}%
            </div>
          </div>
        </div>
        
        {positionSize > 0 && (
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
              style={{ width: `${Math.min(positionSize * 20, 100)}%` }}
            ></div>
          </div>
        )}
      </div>

      {/* ===== ФАКТОРИ АНАЛІЗУ ===== */}
      <div className="space-y-3">
        <button
          onClick={() => setShowFactors(!showFactors)}
          className="w-full py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm flex items-center justify-center gap-2"
        >
          <span>{showFactors ? '▲' : '▼'}</span>
          <span>{showFactors ? 'Сховати фактори' : '📊 Показати фактори аналізу'}</span>
        </button>
        
        {showFactors && signal.factors && (
          <div className="bg-gray-800/30 p-3 rounded-xl">
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(signal.factors)
                .filter(([key]) => !key.includes('ema_alignment')) // Прибираємо довгі значення
                .map(([key, value]) => {
                  const interpretation = interpretValue(key, value);
                  return (
                    <div key={key} className="text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">{translateFactorKey(key)}</span>
                        <span className={`font-medium ${interpretation.color} flex items-center gap-1`}>
                          {interpretation.icon} {typeof value === 'number' ? 
                            (key.includes('level') || key.includes('rsi') || key.includes('cci') || key.includes('williams') ? 
                              value.toFixed(1) : 
                              value.toFixed(2)) : 
                            String(value)}
                        </span>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
        
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm"
        >
          {showDetails ? 'Сховати деталі' : '📈 Показати деталі'}
        </button>
      </div>

      {/* ===== ДЕТАЛІ ===== */}
      {showDetails && (
        <div className="space-y-3">
          {/* Підтримка/Опір */}
          {signal.support_resistance && (
            <div className="bg-gray-800/30 p-3 rounded-xl">
              <div className="text-sm text-gray-400 mb-2">📉 Підтримка та опір</div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-xs text-gray-400">Найближча підтримка</div>
                  <div className="text-sm font-bold text-green-400">
                    ${signal.support_resistance.nearest_support ? formatPrice(signal.support_resistance.nearest_support) : '-'}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-400">Найближчий опір</div>
                  <div className="text-sm font-bold text-red-400">
                    ${signal.support_resistance.nearest_resistance ? formatPrice(signal.support_resistance.nearest_resistance) : '-'}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Цінова дія */}
          {signal.price_action && (
            <div className="bg-gray-800/30 p-3 rounded-xl">
              <div className="text-sm text-gray-400 mb-2">🕯️ Цінова дія</div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {signal.price_action.higher_highs !== undefined && (
                  <div>
                    <div className="text-gray-400">Higher Highs</div>
                    <div className={`font-bold ${signal.price_action.higher_highs >= 2 ? 'text-green-400' : 'text-gray-400'}`}>
                      {signal.price_action.higher_highs}
                    </div>
                  </div>
                )}
                {signal.price_action.lower_lows !== undefined && (
                  <div>
                    <div className="text-gray-400">Lower Lows</div>
                    <div className={`font-bold ${signal.price_action.lower_lows >= 2 ? 'text-red-400' : 'text-gray-400'}`}>
                      {signal.price_action.lower_lows}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ===== КНОПКА ВІДСТЕЖЕННЯ ===== */}
      <div className="pt-2">
        <button
          onClick={onTrack}
          disabled={loading || isNeutral || successProb < 60 || realRR < 1.5}
          className={`w-full py-3 rounded-xl font-bold text-lg transition-all ${
            isNeutral || successProb < 60 || realRR < 1.5
              ? 'bg-gray-800 text-gray-400 cursor-not-allowed'
              : `bg-gradient-to-r ${colors.gradient} hover:opacity-90 hover:scale-[1.02]`
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
              Завантаження...
            </span>
          ) : isNeutral ? (
            '⚖️ Очікувати кращих умов'
          ) : successProb < 60 ? (
            '🔴 Маленький шанс успіху'
          ) : realRR < 1.5 ? (
            '🔴 Погане R/R співвідношення'
          ) : (
            <span className="flex items-center justify-center">
              <span className="mr-2">🎯</span>
              Відстежувати сигнал
            </span>
          )}
        </button>
      </div>

      {/* ===== ПІДВАЛ ===== */}
      <div className="text-center text-xs text-gray-500 pt-3 border-t border-gray-800/50">
        <div className="flex flex-wrap justify-center gap-3 mb-1">
          <span>🤖 AI Trading v2.0</span>
          <span>•</span>
          <span>📊 150+ свічок</span>
          <span>•</span>
          <span>⚡ 20+ індикаторів</span>
        </div>
        {signal.valid_until && (
          <div className="mt-1">
            ⏰ Дійсний до: {new Date(signal.valid_until).toLocaleTimeString('uk-UA', { 
              hour: '2-digit', 
              minute: '2-digit',
              timeZone: 'Europe/Kiev'
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default SignalDisplay;