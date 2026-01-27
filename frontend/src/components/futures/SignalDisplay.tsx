// frontend/src/components/futures/SignalDisplay.tsx
import React from 'react';

interface SignalDisplayProps {
  signal: any;
  onTrack: () => void;  // ЗМІНА: без параметрів
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

  // Функція для розрахунку відсотків
  const calculatePercentage = (entry: number, target: number, isProfit: boolean): string => {
    const change = ((target - entry) / entry) * 100;
    const sign = change >= 0 ? '+' : '';
    const emoji = isProfit ? '📈' : '📉';
    return `${emoji} ${sign}${change.toFixed(2)}%`;
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

      {/* Пояснення AI */}
      {signal.explanation && (
        <div className="bg-gray-700/50 p-4 rounded-lg">
          <h4 className="font-bold mb-2 flex items-center">
            <span className="mr-2">🧠</span> Логіка AI
          </h4>
          <p className="text-gray-300">{signal.explanation}</p>
        </div>
      )}

      {/* Фактори аналізу (додано нове) */}
      {signal.factors && Object.keys(signal.factors).length > 0 && (
        <div className="bg-gray-800/50 p-4 rounded-lg">
          <h4 className="font-bold mb-3 flex items-center">
            <span className="mr-2">⚖️</span> Фактори аналізу
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(signal.factors).map(([key, value]) => {
              const percentage = Math.round(Number(value) * 100);
              let color = 'bg-red-500';
              if (percentage > 70) color = 'bg-green-500';
              else if (percentage > 40) color = 'bg-yellow-500';
              
              return (
                <div key={key} className="bg-gray-900/50 rounded p-2">
                  <div className="flex justify-between items-center mb-1">
                    <div className="text-xs text-gray-400 capitalize">
                      {key.replace(/_/g, ' ')}
                    </div>
                    <span className="text-xs font-bold">{percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${color}`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Кнопки дій */}
      <div className="flex flex-col sm:flex-row gap-3 pt-4">
        <button
          onClick={onTrack}  // ЗМІНА: без параметрів
          disabled={loading}
          className={`flex-1 py-3 rounded-lg font-bold transition-all ${
            loading 
              ? 'bg-gray-700 cursor-not-allowed' 
              : 'bg-green-600 hover:bg-green-700 active:scale-95'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <span className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
              Створення...
            </span>
          ) : (
            <span className="flex items-center justify-center">
              <span className="mr-2">🎯</span> ВІДСТЕЖУВАТИ ЦЕЙ СИГНАЛ
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
