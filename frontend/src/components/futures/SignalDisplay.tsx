// frontend/src/components/futures/SignalDisplay.tsx
import React from 'react';

interface SignalDisplayProps {
  signal: any;
  onTrack: (signalId: number) => void;
  loading: boolean;
  analyzing: boolean;
}

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

  // ВИПРАВЛЕНА ФУНКЦІЯ: Правильний розрахунок відсотків для TP/SL
  const calculatePercentage = (entry: number, target: number, isTakeProfit: boolean): string => {
    const change = ((target - entry) / entry) * 100;
    
    // Для LONG: TP має бути вище (+), SL нижче (-)
    // Для SHORT: TP має бути нижче (-), SL вище (+)
    
    if (isLong) {
      // LONG позиція
      if (isTakeProfit) {
        // TP для LONG: має бути +
        return `${change >= 0 ? '📈' : '📉'} ${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
      } else {
        // SL для LONG: має бути -
        return `${change < 0 ? '📉' : '📈'} ${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
      }
    } else {
      // SHORT позиція
      if (isTakeProfit) {
        // TP для SHORT: має бути -
        return `${change < 0 ? '📉' : '📈'} ${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
      } else {
        // SL для SHORT: має бути +
        return `${change >= 0 ? '📈' : '📉'} ${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
      }
    }
  };

  // ПОКРАЩЕНЕ ПОЯСНЕННЯ AI
  const getAIExplanation = () => {
    if (!signal.explanation) {
      const reasons = [];
      
      if (signal.factors) {
        if (signal.factors.trend_score > 0.7) {
          reasons.push("сильний тренд");
        }
        if (signal.factors.momentum_score > 0.7) {
          reasons.push("сильний моментум");
        }
        if (signal.factors.volume_confirmation > 0.7) {
          reasons.push("підтвердження об'ємом");
        }
        if (signal.factors.rsi_level < 30) {
          reasons.push("перепроданість (RSI < 30)");
        } else if (signal.factors.rsi_level > 70) {
          reasons.push("перекупленість (RSI > 70)");
        }
      }
      
      if (reasons.length > 0) {
        return `AI бачить ${reasons.join(', ')} для ${isLong ? 'росту' : 'падіння'} ціни.`;
      }
      
      return `AI рекомендує ${isLong ? 'купувати (LONG)' : 'продавати (SHORT)'} з впевненістю ${Math.round(signal.confidence * 100)}%.`;
    }
    return signal.explanation;
  };

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
        
        <div className={`px-4 py-2 ${directionBg} rounded-full`}>
          <span className="font-bold">{Math.round(signal.confidence * 100)}%</span>
          <span className="text-gray-300 ml-2">впевненості</span>
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
          <div className={`text-sm mt-1 ${
            isLong ? 'text-green-300' : 'text-red-300'  // Для SHORT TP показуємо червоним
          }`}>
            {calculatePercentage(signal.entry_price, signal.take_profit, true)}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {isLong ? 'Ціль зростання' : 'Ціль падіння'}
          </div>
        </div>
        
        <div className="bg-red-900/20 p-4 rounded-lg border border-red-800/50">
          <div className="text-gray-400 text-sm mb-1">Stop Loss</div>
          <div className="text-2xl font-bold text-red-400">
            ${parseFloat(signal.stop_loss).toFixed(2)}
          </div>
          <div className={`text-sm mt-1 ${
            isLong ? 'text-red-300' : 'text-green-300'  // Для SHORT SL показуємо зеленим
          }`}>
            {calculatePercentage(signal.entry_price, signal.stop_loss, false)}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {isLong ? 'Захист від падіння' : 'Захист від зростання'}
          </div>
        </div>
      </div>

      {/* ПОКРАЩЕНЕ ПОЯСНЕННЯ AI */}
      <div className="bg-gray-700/50 p-4 rounded-lg">
        <h4 className="font-bold mb-2 flex items-center">
          <span className="mr-2">🧠</span> Логіка AI: Чому {isLong ? 'вгору' : 'вниз'}?
        </h4>
        <p className="text-gray-300 mb-3">{getAIExplanation()}</p>
        
        {signal.factors && (
          <div className="mt-3 pt-3 border-t border-gray-600">
            <div className="text-sm text-gray-400 mb-2">Деталі аналізу:</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {signal.factors.trend_score && (
                <div className="flex justify-between">
                  <span>Сила тренду:</span>
                  <span className="text-yellow-300">
                    {Math.round(signal.factors.trend_score * 100)}%
                  </span>
                </div>
              )}
              {signal.factors.momentum_score && (
                <div className="flex justify-between">
                  <span>Моментум:</span>
                  <span className="text-yellow-300">
                    {Math.round(signal.factors.momentum_score * 100)}%
                  </span>
                </div>
              )}
              {signal.factors.volume_confirmation && (
                <div className="flex justify-between">
                  <span>Підтвердження об'ємом:</span>
                  <span className="text-yellow-300">
                    {Math.round(signal.factors.volume_confirmation * 100)}%
                  </span>
                </div>
              )}
              {signal.factors.rsi_level && (
                <div className="flex justify-between">
                  <span>RSI рівень:</span>
                  <span className={
                    signal.factors.rsi_level < 30 ? 'text-green-300' : 
                    signal.factors.rsi_level > 70 ? 'text-red-300' : 'text-yellow-300'
                  }>
                    {Math.round(signal.factors.rsi_level)}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Кнопки дій */}
      <div className="flex flex-col sm:flex-row gap-3 pt-4">
        <button
          onClick={() => onTrack(signal.id)}
          disabled={loading}
          className={`flex-1 py-3 rounded-lg font-bold transition-all ${
            loading 
              ? 'bg-gray-700 cursor-not-allowed' 
              : isLong 
                ? 'bg-green-600 hover:bg-green-700 active:scale-95' 
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
              <span className="mr-2">{isLong ? '📈' : '📉'}</span>
              ВІДСТЕЖУВАТИ {isLong ? 'LONG' : 'SHORT'}
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