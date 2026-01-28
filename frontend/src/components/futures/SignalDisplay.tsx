// frontend/src/components/futures/SignalDisplay.tsx
import React, { useMemo } from 'react';

interface SignalDisplayProps {
  signal: any;
  onTrack: () => void;
  loading: boolean;
  analyzing: boolean;
}

// Функція для перекладу ключів факторів
const translateFactorKey = (key: string): string => {
  const translations: Record<string, string> = {
    'trend_score': 'Тренд',
    'momentum_score': 'Моментум',
    'volume_confirmation': 'Обсяги',
    'volatility_score': 'Волатильність',
    'structure_score': 'Структура',
    'confirmation_ratio': 'Підтвердження',
    'rsi_level': 'RSI',
    'stoch_rsi_level': 'Stoch RSI',
    'vwap_position': 'VWAP позиція',
    'ichimoku_signal': 'Ішимоку',
    'obv_trend': 'OBV тренд',
    'williams_r': 'Williams %R',
    'cci_level': 'CCI'
  };
  
  return translations[key] || key.replace(/_/g, ' ');
};

// Функція для інтерпретації значень
const interpretFactorValue = (key: string, value: any): { text: string; color: string; icon: string; score: number } => {
  const numValue = Number(value);
  
  switch (key) {
    case 'trend_score':
    case 'momentum_score':
    case 'volume_confirmation':
    case 'volatility_score':
    case 'structure_score':
    case 'confirmation_ratio':
      if (numValue >= 0.8) return { text: 'Сильний', color: 'text-green-400', icon: '🟢', score: 85 };
      if (numValue >= 0.6) return { text: 'Помірний', color: 'text-yellow-400', icon: '🟡', score: 65 };
      return { text: 'Слабкий', color: 'text-red-400', icon: '🔴', score: 30 };
    
    case 'rsi_level':
      if (numValue > 70) return { text: 'Перекупленість', color: 'text-red-400', icon: '🔴', score: 40 };
      if (numValue < 30) return { text: 'Перепроданість', color: 'text-green-400', icon: '🟢', score: 70 };
      return { text: 'Нейтральний', color: 'text-yellow-400', icon: '🟡', score: 60 };
    
    case 'stoch_rsi_level':
      if (numValue > 80) return { text: 'Перекупленість', color: 'text-red-400', icon: '🔴', score: 40 };
      if (numValue < 20) return { text: 'Перепроданість', color: 'text-green-400', icon: '🟢', score: 70 };
      return { text: 'Нейтральний', color: 'text-yellow-400', icon: '🟡', score: 60 };
    
    case 'cci_level':
      if (numValue > 100) return { text: 'Сильний вверх', color: 'text-green-400', icon: '🟢', score: 80 };
      if (numValue < -100) return { text: 'Сильний вниз', color: 'text-red-400', icon: '🔴', score: 20 };
      return { text: 'Нейтральний', color: 'text-yellow-400', icon: '🟡', score: 50 };
    
    case 'williams_r':
      if (numValue > -20) return { text: 'Перекупленість', color: 'text-red-400', icon: '🔴', score: 40 };
      if (numValue < -80) return { text: 'Перепроданість', color: 'text-green-400', icon: '🟢', score: 70 };
      return { text: 'Нейтральний', color: 'text-yellow-400', icon: '🟡', score: 60 };
    
    case 'vwap_position':
      if (value === 'above') return { text: 'Вище VWAP', color: 'text-green-400', icon: '📈', score: 60 };
      if (value === 'below') return { text: 'Нижче VWAP', color: 'text-red-400', icon: '📉', score: 50 };
      return { text: String(value), color: 'text-gray-400', icon: '📊', score: 50 };
    
    case 'ichimoku_signal':
      if (value === 'green' || value === 'зелений' || value === 'буличний') 
        return { text: 'Буличний', color: 'text-green-400', icon: '🟢', score: 70 };
      if (value === 'red' || value === 'червоний' || value === 'ведмежий') 
        return { text: 'Ведмежий', color: 'text-red-400', icon: '🔴', score: 30 };
      return { text: String(value), color: 'text-gray-400', icon: '⚫', score: 50 };
    
    case 'obv_trend':
      if (value === 'bullish' || value === 'буличний') 
        return { text: 'Буличний', color: 'text-green-400', icon: '📈', score: 70 };
      if (value === 'bearish' || value === 'ведмежий') 
        return { text: 'Ведмежий', color: 'text-red-400', icon: '📉', score: 30 };
      return { text: String(value), color: 'text-gray-400', icon: '📊', score: 50 };
    
    default:
      return { text: String(value), color: 'text-gray-400', icon: '📊', score: 50 };
  }
};

// Функція для перекладу сили сигналу
const translateSignalStrength = (strength: string): { text: string; color: string; emoji: string } => {
  const lowerStrength = strength?.toLowerCase() || '';
  
  if (lowerStrength.includes('strong') || lowerStrength.includes('сильн') || lowerStrength === 'strong') {
    return { text: 'Сильний', color: 'text-green-400', emoji: '🟢' };
  }
  if (lowerStrength.includes('medium') || lowerStrength.includes('помірн') || lowerStrength === 'medium') {
    return { text: 'Помірний', color: 'text-yellow-400', emoji: '🟡' };
  }
  if (lowerStrength.includes('weak') || lowerStrength.includes('слабк') || lowerStrength === 'weak') {
    return { text: 'Слабкий', color: 'text-red-400', emoji: '🔴' };
  }
  
  return { text: 'Помірний', color: 'text-yellow-400', emoji: '🟡' };
};

// ПОКРАЩЕНА Функція для розрахунку реальної ймовірності успіху
const calculateSuccessProbability = (signal: any): number => {
  if (!signal?.factors) return 50;
  
  const factors = signal.factors;
  let positiveFactors = 0;
  let totalFactors = 0;
  let weightedScore = 0;
  let totalWeight = 0;
  
  // Більш реальні ваги (сума = 100)
  const weights: Record<string, number> = {
    // Основні фактори (більш важливі)
    'trend_score': 20,
    'momentum_score': 15,
    'structure_score': 15,
    
    // Осцилятори (середня важливість)
    'rsi_level': 10,
    'stoch_rsi_level': 8,
    'cci_level': 7,
    
    // Підтвердження
    'volume_confirmation': 8,
    'confirmation_ratio': 6,
    
    // Волатильність та інші
    'volatility_score': 5,
    'williams_r': 3,
    'vwap_position': 2,
    'ichimoku_signal': 3,
    'obv_trend': 4,
  };
  
  // Підраховуємо позитивні фактори
  Object.entries(factors).forEach(([key, value]) => {
    totalFactors++;
    
    const interpretation = interpretFactorValue(key, value);
    const weight = weights[key] || 2;
    
    // Додаємо до загального скора
    weightedScore += interpretation.score * (weight / 100);
    totalWeight += weight;
    
    // Вважаємо позитивним, якщо інтерпретація зелена або жовта
    if (interpretation.color === 'text-green-400' || interpretation.color === 'text-yellow-400') {
      positiveFactors++;
    }
  });
  
  // Базовий розрахунок на основі ваг
  const weightedProbability = totalWeight > 0 ? weightedScore / totalWeight * 100 : 50;
  
  // Враховуємо співвідношення позитивних факторів
  const positiveRatio = positiveFactors / totalFactors;
  const positiveBonus = (positiveRatio - 0.5) * 20; // ±10%
  
  // Враховуємо впевненість AI
  const confidence = signal.confidence || 0.5;
  const confidenceBonus = (confidence - 0.5) * 30; // ±15%
  
  // Враховуємо ризик/прибуток
  const riskReward = signal.risk_reward ? Number(signal.risk_reward) : 3.01;
  let rrBonus = 0;
  if (riskReward >= 3) rrBonus = 15;
  else if (riskReward >= 2) rrBonus = 10;
  else if (riskReward >= 1.5) rrBonus = 5;
  
  // Обчислюємо загальну ймовірність
  let probability = weightedProbability + positiveBonus + confidenceBonus + rrBonus;
  
  // Коригування за типом сигналу (лонг/шорт)
  if (signal.direction === 'long') {
    // Для лонгів додаємо невеликий бонус
    probability += 5;
  }
  
  // Обмежуємо розумними межами
  probability = Math.max(25, Math.min(85, probability));
  
  // Округлюємо
  return Math.round(probability);
};

// ПОКРАЩЕНА Функція для оцінки ризику
const calculateRiskScore = (signal: any): { score: number; description: string } => {
  if (!signal) return { score: 50, description: 'Середній' };
  
  let riskScore = 50; // Початкове значення
  const factors = signal.factors || {};
  
  // Аналізуємо ризикові фактори
  let riskFactors = 0;
  let totalRiskFactors = 0;
  
  // 1. Осцилятори в екстремальних зонах
  if (factors.rsi_level) {
    totalRiskFactors++;
    const rsi = Number(factors.rsi_level);
    if (rsi > 80 || rsi < 20) {
      riskFactors++;
      riskScore += 20;
    } else if (rsi > 70 || rsi < 30) {
      riskScore += 10;
    }
  }
  
  if (factors.stoch_rsi_level) {
    totalRiskFactors++;
    const stoch = Number(factors.stoch_rsi_level);
    if (stoch > 90 || stoch < 10) {
      riskFactors++;
      riskScore += 15;
    } else if (stoch > 80 || stoch < 20) {
      riskScore += 8;
    }
  }
  
  if (factors.williams_r) {
    totalRiskFactors++;
    const will = Number(factors.williams_r);
    if (will > -10 || will < -90) {
      riskFactors++;
      riskScore += 10;
    }
  }
  
  // 2. Волатильність
  if (factors.volatility_score) {
    totalRiskFactors++;
    const vol = Number(factors.volatility_score);
    if (vol > 0.9) {
      riskFactors++;
      riskScore += 25; // Дуже висока волатильність
    } else if (vol > 0.8) {
      riskScore += 15;
    } else if (vol < 0.2) {
      riskScore += 10; // Дуже низька волатильність (можлива пробій)
    }
  }
  
  // 3. Підтвердження
  if (factors.confirmation_ratio) {
    totalRiskFactors++;
    const conf = Number(factors.confirmation_ratio);
    if (conf < 0.3) {
      riskFactors++;
      riskScore += 20; // Дуже мало підтверджень
    } else if (conf < 0.5) {
      riskScore += 10;
    }
  }
  
  // 4. Відсоток ризикових факторів
  const riskFactorRatio = totalRiskFactors > 0 ? riskFactors / totalRiskFactors : 0;
  
  if (riskFactorRatio > 0.5) {
    riskScore += 30;
  } else if (riskFactorRatio > 0.3) {
    riskScore += 15;
  }
  
  // 5. Коригування за співвідношенням ризик/прибуток
  const riskReward = signal.risk_reward ? Number(signal.risk_reward) : 3.01;
  if (riskReward < 1.0) {
    riskScore += 40; // Дуже погане R/R
  } else if (riskReward < 1.5) {
    riskScore += 25;
  } else if (riskReward >= 2.5) {
    riskScore -= 20; // Хороше R/R знижує ризик
  } else if (riskReward >= 2.0) {
    riskScore -= 10;
  }
  
  // Обмежуємо та нормалізуємо
  riskScore = Math.min(100, Math.max(0, riskScore));
  
  // Визначаємо опис
  let description = 'Низький';
  if (riskScore >= 70) description = 'Дуже високий';
  else if (riskScore >= 60) description = 'Високий';
  else if (riskScore >= 40) description = 'Середній';
  else if (riskScore >= 20) description = 'Низький';
  else description = 'Мінімальний';
  
  return { score: Math.round(riskScore), description };
};

const SignalDisplay: React.FC<SignalDisplayProps> = ({ 
  signal, 
  onTrack, 
  loading,
  analyzing 
}) => {
  // Показуємо завантаження під час аналізу
  if (analyzing) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-6"></div>
        <h3 className="text-xl font-medium mb-2">AI аналізує ринок...</h3>
        <p className="text-gray-400 max-w-md mx-auto">
          Система обробляє ринкові дані та генерує сигнал
        </p>
      </div>
    );
  }

  // Якщо немає сигнала - показуємо привітання
  if (!signal || signal.error) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🤖</div>
        <h3 className="text-xl font-medium mb-2">Оберіть монету для аналізу</h3>
        <p className="text-gray-400 max-w-md mx-auto">
          AI проаналізує ринкові дані та згенерує торговий сигнал з рекомендаціями
        </p>
        {signal?.error && (
          <div className="mt-4 p-3 bg-red-900/30 border border-red-800 rounded-lg max-w-md mx-auto">
            <p className="text-red-300">{signal.message}</p>
          </div>
        )}
      </div>
    );
  }

  const isLong = signal.direction === 'long';
  const directionColor = isLong ? 'text-green-400' : 'text-red-400';
  const directionBg = isLong ? 'bg-green-900/30' : 'bg-red-900/30';
  const directionEmoji = isLong ? '📈 LONG' : '📉 SHORT';
  
  // Розрахунок реальної статистики
  const successProbability = useMemo(() => calculateSuccessProbability(signal), [signal]);
  const riskData = useMemo(() => calculateRiskScore(signal), [signal]);
  const winChance = successProbability;
  const lossChance = 100 - successProbability;
  
  // Визначаємо силу сигналу на основі ймовірності
  const getStrengthFromProbability = (probability: number) => {
    if (probability >= 70) return { text: 'Високий', color: 'text-green-400', emoji: '🟢' };
    if (probability >= 60) return { text: 'Помірний', color: 'text-yellow-400', emoji: '🟡' };
    if (probability >= 50) return { text: 'Слабкий', color: 'text-orange-400', emoji: '🟠' };
    return { text: 'Низький', color: 'text-red-400', emoji: '🔴' };
  };
  
  const signalStrength = translateSignalStrength(signal.signal_strength);
  const probabilityStrength = getStrengthFromProbability(successProbability);
  const confidencePercent = Math.round(signal.confidence * 100);

  // Функція для розрахунку відсотків
  const calculatePercentage = (entry: number, target: number, isProfit: boolean): string => {
    const change = ((target - entry) / entry) * 100;
    const sign = change >= 0 ? '+' : '';
    const emoji = isProfit ? '📈' : '📉';
    return `${emoji} ${sign}${change.toFixed(2)}%`;
  };

  // Оцінка якості сигналу
  const getSignalQuality = () => {
    const rrRatio = signal.risk_reward ? Number(signal.risk_reward) : 3.01;
    
    if (winChance >= 65 && riskData.score <= 30 && rrRatio >= 2.5) {
      return { text: 'Високоякісний', color: 'text-green-400', icon: '🏆', desc: 'Чудове співвідношення ризик/прибуток' };
    }
    if (winChance >= 60 && riskData.score <= 40 && rrRatio >= 2.0) {
      return { text: 'Добрий', color: 'text-blue-400', icon: '👍', desc: 'Гарні умови для торгівлі' };
    }
    if (winChance >= 55 || (winChance >= 50 && rrRatio >= 3.0)) {
      return { text: 'Середній', color: 'text-yellow-400', icon: '🤔', desc: 'Можна розглянути з обережністю' };
    }
    return { text: 'Ризикований', color: 'text-red-400', icon: '⚠️', desc: 'Високий ризик або низькі шанси' };
  };

  const signalQuality = getSignalQuality();

  // Аналіз факторів для пояснення
  const analyzeFactors = () => {
    const factors = signal.factors || {};
    const positive = Object.entries(factors).filter(([key, value]) => {
      const interpretation = interpretFactorValue(key, value);
      return interpretation.color === 'text-green-400';
    }).length;
    
    const neutral = Object.entries(factors).filter(([key, value]) => {
      const interpretation = interpretFactorValue(key, value);
      return interpretation.color === 'text-yellow-400';
    }).length;
    
    const negative = Object.entries(factors).filter(([key, value]) => {
      const interpretation = interpretFactorValue(key, value);
      return interpretation.color === 'text-red-400';
    }).length;
    
    return { positive, neutral, negative };
  };

  const factorAnalysis = analyzeFactors();

  return (
    <div className="space-y-6">
      {/* Заголовок сигналу */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className={`text-2xl font-bold ${directionColor}`}>
            {directionEmoji} {signal.symbol}
          </h3>
          <p className="text-gray-400">AI сигнал на основі ринкового аналізу</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className={`px-4 py-2 ${probabilityStrength.color.replace('text-', 'bg-')}/20 rounded-full border ${probabilityStrength.color.replace('text-', 'border-')}/30`}>
            <span className="font-bold">{probabilityStrength.emoji} {winChance}%</span>
            <span className="text-gray-300 ml-2">шанс на успіх</span>
          </div>
        </div>
      </div>

      {/* Ціни: Entry, TP, SL */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-700 p-4 rounded-lg">
          <div className="text-gray-400 text-sm mb-1">Вхідна ціна</div>
          <div className="text-2xl font-bold">${parseFloat(signal.entry_price).toFixed(2)}</div>
        </div>
        
        <div className="bg-green-900/20 p-4 rounded-lg border border-green-800/50">
          <div className="text-gray-400 text-sm mb-1">Take Profit</div>
          <div className="text-2xl font-bold text-green-400">
            ${parseFloat(signal.take_profit).toFixed(2)}
          </div>
          <div className="text-sm text-green-300 mt-1">
            {calculatePercentage(signal.entry_price, signal.take_profit, isLong)}
          </div>
        </div>
        
        <div className="bg-red-900/20 p-4 rounded-lg border border-red-800/50">
          <div className="text-gray-400 text-sm mb-1">Stop Loss</div>
          <div className="text-2xl font-bold text-red-400">
            ${parseFloat(signal.stop_loss).toFixed(2)}
          </div>
          <div className="text-sm text-red-300 mt-1">
            {calculatePercentage(signal.entry_price, signal.stop_loss, !isLong)}
          </div>
        </div>
      </div>

      {/* Статистика успіху */}
      <div className="bg-gray-800/50 p-4 rounded-lg">
        <h4 className="font-bold mb-3 flex items-center">
          <span className="mr-2">📈</span> Статистика успіху
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="text-center p-3 bg-gray-900/30 rounded">
            <div className="text-gray-400 text-sm mb-1">Шанс на успіх</div>
            <div className={`text-2xl font-bold ${probabilityStrength.color}`}>
              {winChance}%
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {winChance >= 60 ? 'Високий' : winChance >= 50 ? 'Помірний' : 'Низький'} шанс
            </div>
          </div>
          
          <div className="text-center p-3 bg-gray-900/30 rounded">
            <div className="text-gray-400 text-sm mb-1">Ризик збитків</div>
            <div className={`text-2xl font-bold ${lossChance > 50 ? 'text-red-400' : 'text-yellow-400'}`}>
              {lossChance}%
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {lossChance > 60 ? 'Високий' : lossChance > 40 ? 'Помірний' : 'Низький'} ризик
            </div>
          </div>
          
          <div className="text-center p-3 bg-gray-900/30 rounded">
            <div className="text-gray-400 text-sm mb-1">Оцінка ризику</div>
            <div className={`text-2xl font-bold ${riskData.score > 60 ? 'text-red-400' : riskData.score > 40 ? 'text-yellow-400' : 'text-green-400'}`}>
              {riskData.score}/100
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {riskData.description} ризик
            </div>
          </div>
          
          <div className="text-center p-3 bg-gray-900/30 rounded">
            <div className="text-gray-400 text-sm mb-1">Якість сигналу</div>
            <div className={`text-xl font-bold ${signalQuality.color}`}>
              {signalQuality.icon} {signalQuality.text}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {factorAnalysis.positive} 🟢 / {factorAnalysis.neutral} 🟡 / {factorAnalysis.negative} 🔴
            </div>
          </div>
        </div>
        
        {/* Прогрес бар для візуалізації шансів */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-400 mb-1">
            <span>🔴 Шанс на збиток: {lossChance}%</span>
            <span>🟢 Шанс на прибуток: {winChance}%</span>
          </div>
          <div className="w-full h-6 bg-gray-700 rounded-full overflow-hidden flex">
            <div 
              className="h-full bg-red-500 transition-all duration-500"
              style={{ width: `${lossChance}%` }}
              title={`${lossChance}% шанс досягнення Stop Loss`}
            ></div>
            <div 
              className="h-full bg-green-500 transition-all duration-500"
              style={{ width: `${winChance}%` }}
              title={`${winChance}% шанс досягнення Take Profit`}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Досягнення SL ({lossChance}%)</span>
            <span>Досягнення TP ({winChance}%)</span>
          </div>
        </div>
        
        {/* Пояснення результатів */}
        <div className="mt-4 p-3 bg-gray-900/30 rounded">
          <div className="text-sm text-gray-300">
            <span className="font-medium">Аналіз сигналу:</span> 
            <span className="ml-2">
              {factorAnalysis.positive} позитивних, {factorAnalysis.neutral} нейтральних, {factorAnalysis.negative} негативних факторів.
              {winChance >= 60 ? ' Сигнал має високі шанси на успіх.' : 
               winChance >= 50 ? ' Сигнал має помірні шанси.' : 
               ' Сигнал має низькі шанси, рекомендується обережність.'}
            </span>
          </div>
        </div>
      </div>

      {/* Пояснення AI */}
      {signal.explanation && (
        <div className="bg-gray-700/50 p-4 rounded-lg">
          <h4 className="font-bold mb-2 flex items-center">
            <span className="mr-2">🧠</span> Логіка AI
          </h4>
          <p className="text-gray-300">{signal.explanation}</p>
        </div>
      )}

      {/* Рекомендація */}
      <div className={`p-4 rounded-lg ${winChance >= 60 ? 'bg-green-900/20 border border-green-800/50' : 
                                             winChance >= 50 ? 'bg-yellow-900/20 border border-yellow-800/50' : 
                                             'bg-red-900/20 border border-red-800/50'}`}>
        <div className="flex items-start">
          <span className="text-2xl mr-3 mt-1">
            {winChance >= 65 ? '✅' : 
             winChance >= 55 ? '🤔' : 
             winChance >= 45 ? '⚠️' : '❌'}
          </span>
          <div>
            <h4 className="font-bold text-lg mb-1">
              {winChance >= 65 ? 'Рекомендовано до торгівлі' : 
               winChance >= 55 ? 'Можна розглянути' : 
               winChance >= 45 ? 'Обережно' : 'Не рекомендується'}
            </h4>
            <p className="text-gray-300">
              {winChance >= 65 ? 
                `З ${winChance}% ймовірністю успіху та співвідношенням ризик/прибуток 1:${signal.risk_reward || '3.01'}, цей сигнал має високі шанси на прибуток.` :
               winChance >= 55 ?
                `З ${winChance}% ймовірністю успіху. Можна розглянути угоду з меншим розміром позиції.` :
               winChance >= 45 ?
                `З ${winChance}% ймовірністю успіху. Рекомендується почекати кращих умов або використовувати дуже малий розмір позиції.` :
                `Лише ${winChance}% ймовірність успіху. Рекомендується утриматись від торгівлі за цим сигналом.`
              }
            </p>
            {signal.risk_reward && Number(signal.risk_reward) >= 2.5 && (
              <p className="text-green-300 text-sm mt-2">
                🎯 Чудове співвідношення ризик/прибуток (1:{signal.risk_reward}) компенсує нижчі шанси успіху.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Кнопки дій */}
      <div className="flex flex-col sm:flex-row gap-3 pt-4">
        <button
          onClick={onTrack}
          disabled={loading}
          className={`flex-1 py-3 rounded-lg font-bold transition-all ${
            loading 
              ? 'bg-gray-700 cursor-not-allowed' 
              : winChance >= 60 
                ? 'bg-green-600 hover:bg-green-700 active:scale-95'
                : winChance >= 50
                ? 'bg-yellow-600 hover:bg-yellow-700 active:scale-95'
                : 'bg-red-600 hover:bg-red-700 active:scale-95'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <span className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
              Створення...
            </span>
          ) : (
            <span className="flex items-center justify-center">
              <span className="mr-2">🎯</span> 
              {winChance >= 60 ? 'ВІДСТЕЖУВАТИ СИГНАЛ' :
               winChance >= 50 ? 'ВІДСТЕЖУВАТИ (обережно)' : 
               'ВІДСТЕЖУВАТИ (ризиковано)'}
            </span>
          )}
        </button>
        
        <button
          onClick={() => window.location.reload()}
          className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-colors"
        >
          <span className="flex items-center justify-center">
            <span className="mr-2">🔄</span> Новий аналіз
          </span>
        </button>
      </div>
    </div>
  );
};

export default SignalDisplay;