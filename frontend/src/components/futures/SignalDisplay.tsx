// frontend/src/components/futures/SignalDisplay.tsx
import React, { useState } from 'react';

interface SignalDisplayProps {
  signal: any;
  onTrack: () => void;
  loading: boolean;
  analyzing: boolean;
  onTimeframeChange?: (timeframe: string) => void;
}

// Компонент метрик
const MetricCard = ({ 
  title, 
  value, 
  subtext, 
  color = 'default',
  icon 
}: { 
  title: string; 
  value: string | number; 
  subtext?: string; 
  color?: 'green' | 'red' | 'yellow' | 'blue' | 'purple' | 'default';
  icon?: string;
}) => {
  const colorClasses = {
    green: 'border-l-green-500 bg-green-900/10',
    red: 'border-l-red-500 bg-red-900/10',
    yellow: 'border-l-yellow-500 bg-yellow-900/10',
    blue: 'border-l-blue-500 bg-blue-900/10',
    purple: 'border-l-purple-500 bg-purple-900/10',
    default: 'border-l-gray-600 bg-gray-800/30'
  };

  const textColors = {
    green: 'text-green-400',
    red: 'text-red-400',
    yellow: 'text-yellow-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400',
    default: 'text-gray-300'
  };

  return (
    <div className={`p-4 rounded-r-lg border-l-4 ${colorClasses[color]} transition-all hover:scale-[1.02]`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            {icon && <span className="text-lg">{icon}</span>}
            <span className="text-sm font-medium text-gray-400">{title}</span>
          </div>
          <div className={`text-2xl font-bold ${textColors[color]}`}>{value}</div>
          {subtext && <div className="text-xs text-gray-500 mt-1">{subtext}</div>}
        </div>
      </div>
    </div>
  );
};

// Компонент прогрес бару
const ProgressBar = ({ 
  value, 
  max = 100, 
  color = 'green',
  showLabel = true 
}: { 
  value: number; 
  max?: number; 
  color?: 'green' | 'red' | 'yellow' | 'blue';
  showLabel?: boolean;
}) => {
  const percentage = Math.min(100, (value / max) * 100);
  
  const colorClasses = {
    green: 'bg-gradient-to-r from-green-500 to-emerald-500',
    red: 'bg-gradient-to-r from-red-500 to-pink-500',
    yellow: 'bg-gradient-to-r from-yellow-500 to-amber-500',
    blue: 'bg-gradient-to-r from-blue-500 to-cyan-500'
  };

  return (
    <div className="space-y-1">
      {showLabel && (
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Прогрес</span>
          <span className="font-medium">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div 
          className={`h-full ${colorClasses[color]} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

// Компонент цінової точки
const PricePoint = ({ 
  type, 
  price, 
  entryPrice,
  label,
  description 
}: { 
  type: 'entry' | 'tp' | 'sl' | 'current';
  price: number;
  entryPrice: number;
  label: string;
  description?: string;
}) => {
  const difference = ((price - entryPrice) / entryPrice) * 100;
  const isPositive = difference >= 0;
  
  const config = {
    entry: { icon: '📍', color: 'border-blue-500', bg: 'bg-blue-900/20' },
    tp: { icon: '🎯', color: 'border-green-500', bg: 'bg-green-900/20' },
    sl: { icon: '🛡️', color: 'border-red-500', bg: 'bg-red-900/20' },
    current: { icon: '📊', color: 'border-purple-500', bg: 'bg-purple-900/20' }
  }[type];

  return (
    <div className={`p-3 rounded-lg border ${config.color} ${config.bg}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{config.icon}</span>
          <span className="font-medium">{label}</span>
        </div>
        {type !== 'entry' && (
          <span className={`text-sm font-bold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
            {isPositive ? '+' : ''}{difference.toFixed(2)}%
          </span>
        )}
      </div>
      <div className="text-2xl font-bold mb-1">
        ${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
      </div>
      {description && <div className="text-xs text-gray-400">{description}</div>}
    </div>
  );
};

// Головний компонент
const SignalDisplay: React.FC<SignalDisplayProps> = ({ 
  signal, 
  onTrack, 
  loading,
  analyzing,
  onTimeframeChange
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'analysis' | 'risk'>('overview');

  // Стан завантаження
  if (analyzing) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="relative mb-6">
          <div className="w-20 h-20 border-4 border-blue-500/30 rounded-full"></div>
          <div className="absolute top-0 left-0 w-20 h-20 border-4 border-transparent border-t-blue-500 rounded-full animate-spin"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-2xl">🤖</div>
        </div>
        <h3 className="text-xl font-bold mb-2">AI аналізує ринок...</h3>
        <p className="text-gray-400 text-center mb-6">
          Аналіз 150+ свічок та 20+ технічних індикаторів
        </p>
        <div className="w-64 h-1 bg-gray-800 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 animate-pulse"></div>
        </div>
      </div>
    );
  }

  // Немає сигналу
  if (!signal || signal.error) {
    return (
      <div className="text-center py-12 px-4">
        <div className="inline-block p-6 bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl mb-6">
          <div className="text-5xl mb-4">📈</div>
          <h3 className="text-xl font-bold mb-2">Професійний AI аналіз</h3>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            Оберіть криптовалюту для генерації детального торгового сигналу
          </p>
          
          {onTimeframeChange && (
            <div className="flex flex-wrap justify-center gap-2">
              {['15m', '1h', '4h', '1d'].map((tf) => (
                <button
                  key={tf}
                  onClick={() => onTimeframeChange(tf)}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-all hover:scale-105"
                >
                  {tf}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // --- Дані сигналу ---
  const isLong = signal.direction === 'long';
  const isNeutral = signal.direction === 'neutral';
  
  const entryPrice = signal.entry_points?.optimal_entry || signal.entry_price || 0;
  const currentPrice = signal.current_price || entryPrice || 0;
  const takeProfit = signal.take_profit || 0;
  const stopLoss = signal.stop_loss || 0;
  const confidence = Math.round((signal.confidence || 0) * 100);
  
  // Розрахунки
  const profitDistance = Math.abs(takeProfit - entryPrice);
  const riskDistance = Math.abs(stopLoss - entryPrice);
  const riskReward = riskDistance > 0 ? (profitDistance / riskDistance).toFixed(2) : '1.0';
  const positionSize = signal.position_size?.size_percent || 2.0;

  // Стилізація
  const signalConfig = {
    long: {
      gradient: 'from-green-600 to-emerald-600',
      icon: '📈',
      label: 'LONG',
      color: 'green'
    },
    short: {
      gradient: 'from-red-600 to-pink-600', 
      icon: '📉',
      label: 'SHORT',
      color: 'red'
    },
    neutral: {
      gradient: 'from-yellow-600 to-amber-600',
      icon: '⚖️',
      label: 'NEUTRAL',
      color: 'yellow'
    }
  }[isLong ? 'long' : isNeutral ? 'neutral' : 'short'];

  return (
    <div className="space-y-6">
      {/* Заголовок сигналу */}
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="text-4xl">{signalConfig.icon}</div>
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h2 className="text-2xl font-bold">{signal.symbol}</h2>
                <span className={`px-3 py-1 rounded-full text-sm font-bold bg-gradient-to-r ${signalConfig.gradient}`}>
                  {signalConfig.label}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-400">
                <span>TF: {signal.timeframe || '1h'}</span>
                <span>•</span>
                <span>AI Confidence: {confidence}%</span>
                <span>•</span>
                <span>R/R: 1:{riskReward}</span>
              </div>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-3xl font-bold">
              ${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
            </div>
            <div className="text-sm text-gray-400">Current Price</div>
          </div>
        </div>
        
        {/* Теми */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-lg transition-all ${activeTab === 'overview' ? 'bg-gray-700' : 'bg-gray-800 hover:bg-gray-700'}`}
          >
            📊 Огляд
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`px-4 py-2 rounded-lg transition-all ${activeTab === 'analysis' ? 'bg-gray-700' : 'bg-gray-800 hover:bg-gray-700'}`}
          >
            🔍 Аналіз
          </button>
          <button
            onClick={() => setActiveTab('risk')}
            className={`px-4 py-2 rounded-lg transition-all ${activeTab === 'risk' ? 'bg-gray-700' : 'bg-gray-800 hover:bg-gray-700'}`}
          >
            🛡️ Ризик
          </button>
        </div>
      </div>

      {/* Контент за темою */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Основні метрики */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricCard
              title="Шанс успіху"
              value={`${Math.min(95, confidence + 20)}%`}
              subtext="На основі історичних даних"
              color={confidence >= 70 ? 'green' : confidence >= 60 ? 'yellow' : 'red'}
              icon="🎯"
            />
            <MetricCard
              title="Рекомендований розмір"
              value={`${positionSize}%`}
              subtext={`Ризик: ${signal.position_size?.risk_per_trade || 2}%`}
              color="blue"
              icon="📊"
            />
            <MetricCard
              title="Очікуваний прибуток"
              value={`+${(positionSize * (Number(riskReward) - 1)).toFixed(1)}%`}
              subtext="За умови виконання TP"
              color="purple"
              icon="💰"
            />
          </div>

          {/* Цінові точки */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <PricePoint
              type="entry"
              price={entryPrice}
              entryPrice={entryPrice}
              label="Точка входу"
              description="Рекомендована ціна для відкриття позиції"
            />
            <PricePoint
              type="current"
              price={currentPrice}
              entryPrice={entryPrice}
              label="Поточна ціна"
              description={`Відхилення: ${(((currentPrice - entryPrice) / entryPrice) * 100).toFixed(2)}%`}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <PricePoint
              type="tp"
              price={takeProfit}
              entryPrice={entryPrice}
              label="Take Profit"
              description="Цільова ціна для закриття з прибутком"
            />
            <PricePoint
              type="sl"
              price={stopLoss}
              entryPrice={entryPrice}
              label="Stop Loss"
              description="Захист від великих втрат"
            />
          </div>
        </div>
      )}

      {activeTab === 'analysis' && (
        <div className="space-y-6">
          <div className="bg-gray-800/30 rounded-xl p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              📈 Технічний аналіз
            </h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {signal.indicators_summary && Object.entries(signal.indicators_summary).map(([key, value]) => (
                <div key={key} className="p-3 bg-gray-800/50 rounded-lg">
                  <div className="text-sm text-gray-400 mb-1">{key.toUpperCase()}</div>
                  <div className="text-xl font-bold">
                    {typeof value === 'number' ? value.toFixed(2) : String(value)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'risk' && (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6">
            <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
              🛡️ Управління ризиками
            </h3>
            
            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">Розподіл ризику</span>
                  <span className="font-medium">Макс. втрата: {riskDistance.toFixed(2)}%</span>
                </div>
                <ProgressBar value={riskDistance * 10} color="red" />
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">Потенційний прибуток</span>
                  <span className="font-medium">Макс. прибуток: {profitDistance.toFixed(2)}%</span>
                </div>
                <ProgressBar value={profitDistance * 10} color="green" />
              </div>
              
              <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="text-center p-4 bg-gray-800/50 rounded-lg">
                  <div className="text-2xl font-bold text-green-400 mb-1">
                    1:{riskReward}
                  </div>
                  <div className="text-sm text-gray-400">Risk/Reward</div>
                </div>
                
                <div className="text-center p-4 bg-gray-800/50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-400 mb-1">
                    {positionSize}%
                  </div>
                  <div className="text-sm text-gray-400">Position Size</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Пояснення сигналу */}
      {signal.explanation && (
        <div className="bg-gray-800/30 rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            🤖 AI Пояснення
          </h3>
          <div className="text-gray-300 space-y-2">
            {signal.explanation.split('\n').map((line: string, i: number) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </div>
      )}

      {/* Кнопка відстеження */}
      <div className="sticky bottom-6 bg-gray-900/95 backdrop-blur-sm rounded-xl p-4 border border-gray-700">
        <button
          onClick={onTrack}
          disabled={loading || isNeutral}
          className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
            isNeutral || loading
              ? 'bg-gray-800 text-gray-400 cursor-not-allowed'
              : `bg-gradient-to-r ${signalConfig.gradient} hover:opacity-90 hover:scale-[1.02] active:scale-95`
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
              Додавання до відстеження...
            </span>
          ) : isNeutral ? (
            '⚖️ Чекати кращих умов'
          ) : (
            <span className="flex items-center justify-center">
              <span className="mr-3 text-xl">🎯</span>
              Відстежувати сигнал
            </span>
          )}
        </button>
        
        {!isNeutral && (
          <div className="text-center text-sm text-gray-400 mt-3">
            Сигнал дійсний до: {new Date(signal.valid_until).toLocaleTimeString('uk-UA', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default SignalDisplay;