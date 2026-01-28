// frontend/src/components/futures/LearningSignalDisplay.tsx
import React, { useState, useEffect } from 'react';
import SignalDisplay from './SignalDisplay';

interface LearningSignalDisplayProps {
  signal: any;
  onTrack: () => void;
  loading: boolean;
  analyzing: boolean;
  onTimeframeChange?: (timeframe: string) => void;
  learningReport?: any;
}

const LearningSignalDisplay: React.FC<LearningSignalDisplayProps> = ({ 
  signal, 
  onTrack, 
  loading,
  analyzing,
  onTimeframeChange,
  learningReport
}) => {
  const [showLearning, setShowLearning] = useState(false);
  const [progress, setProgress] = useState(0);

  // Ефект для анімації прогресу
  useEffect(() => {
    if (learningReport?.training_progress) {
      const target = learningReport.training_progress;
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= target) {
            clearInterval(interval);
            return target;
          }
          return prev + 1;
        });
      }, 20);
      
      return () => clearInterval(interval);
    }
  }, [learningReport?.training_progress]);

  // Якщо немає даних про навчання, показуємо стандартний компонент
  if (!learningReport) {
    return (
      <SignalDisplay 
        signal={signal}
        onTrack={onTrack}
        loading={loading}
        analyzing={analyzing}
        onTimeframeChange={onTimeframeChange}
      />
    );
  }

  // Перевірка чи це навчальний сигнал
  const isLearningSignal = signal?.learning_data?.training_mode || false;
  const learningData = signal?.learning_data || {};

  return (
    <div className="space-y-4">
      {/* ===== ПАНЕЛЬ НАВЧАННЯ ===== */}
      <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 p-4 rounded-xl border border-purple-700/50">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="text-2xl">🧠</div>
            <div>
              <h3 className="font-bold">AI НАВЧАЄТЬСЯ</h3>
              <p className="text-xs text-gray-400">
                {learningReport.learning_mode ? 'Режим навчання' : 'Режим торгівлі'}
              </p>
            </div>
          </div>
          
          <button
            onClick={() => setShowLearning(!showLearning)}
            className="px-3 py-1 text-sm bg-purple-800/50 hover:bg-purple-700/50 rounded-lg"
          >
            {showLearning ? '▲' : '▼'}
          </button>
        </div>
        
        {/* Прогрес бар */}
        <div className="mb-2">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">Прогрес навчання</span>
            <span className="font-bold text-blue-400">{progress}%</span>
          </div>
          <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
        
        {/* Основна статистика */}
        <div className="grid grid-cols-3 gap-2 text-sm">
          <div className="text-center">
            <div className="text-gray-400">Сигналів</div>
            <div className="font-bold">{learningReport.total_signals}</div>
          </div>
          <div className="text-center">
            <div className="text-gray-400">Точність</div>
            <div className={`font-bold ${
              learningReport.current_accuracy > 0.6 ? 'text-green-400' : 
              learningReport.current_accuracy > 0.5 ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {(learningReport.current_accuracy * 100).toFixed(1)}%
            </div>
          </div>
          <div className="text-center">
            <div className="text-gray-400">Днів</div>
            <div className="font-bold">{learningReport.days_learning}</div>
          </div>
        </div>
        
        {/* Розгорнута інформація */}
        {showLearning && (
          <div className="mt-4 pt-4 border-t border-purple-700/30 space-y-3">
            {/* Детальна статистика */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-900/50 p-2 rounded-lg">
                <div className="text-xs text-gray-400">Перемог</div>
                <div className="font-bold text-green-400">{learningReport.winning_signals}</div>
              </div>
              <div className="bg-gray-900/50 p-2 rounded-lg">
                <div className="text-xs text-gray-400">Поразок</div>
                <div className="font-bold text-red-400">{learningReport.losing_signals}</div>
              </div>
            </div>
            
            {/* Середні значення */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-900/50 p-2 rounded-lg">
                <div className="text-xs text-gray-400">Середній прибуток</div>
                <div className="font-bold text-green-400">+{learningReport.avg_profit_per_win}%</div>
              </div>
              <div className="bg-gray-900/50 p-2 rounded-lg">
                <div className="text-xs text-gray-400">Середній збиток</div>
                <div className="font-bold text-red-400">-{learningReport.avg_loss_per_loss}%</div>
              </div>
            </div>
            
            {/* Рекомендація */}
            <div className="bg-gray-900/50 p-3 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">💡 Рекомендація системи</div>
              <div className="text-sm text-blue-300">{learningReport.recommendation}</div>
            </div>
          </div>
        )}
      </div>

      {/* ===== НАВЧАЛЬНІ ДАНІ СИГНАЛУ ===== */}
      {isLearningSignal && learningData && (
        <div className="bg-gray-800/30 p-4 rounded-xl border border-gray-700/50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="text-xl">📚</div>
              <h4 className="font-bold">Дані навчання</h4>
            </div>
            <div className="text-xs px-2 py-1 bg-blue-900/50 rounded">
              {learningData.data_quality === 'high' ? 'Висока якість' : 
               learningData.data_quality === 'medium' ? 'Середня якість' : 'Низька якість'}
            </div>
          </div>
          
          {/* Історична ефективність */}
          {learningData.historical_performance && (
            <div className="mb-3">
              <div className="text-sm text-gray-400 mb-2">📊 Історична ефективність</div>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-gray-900/50 p-2 rounded">
                  <div className="text-xs text-gray-400">Схожих паттернів</div>
                  <div className="font-bold">{learningData.historical_performance.similar_patterns_found}</div>
                </div>
                <div className="bg-gray-900/50 p-2 rounded">
                  <div className="text-xs text-gray-400">Шанс успіху</div>
                  <div className={`font-bold ${
                    learningData.historical_performance.win_rate > 0.6 ? 'text-green-400' : 
                    learningData.historical_performance.win_rate > 0.5 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {(learningData.historical_performance.win_rate * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Персоналізовані рекомендації */}
          {learningData.personalized_recommendations && (
            <div>
              <div className="text-sm text-gray-400 mb-2">🎯 Персоналізовані рекомендації</div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Розмір позиції</span>
                  <span className={`px-2 py-1 text-xs rounded ${
                    learningData.personalized_recommendations.position_size_multiplier > 1.1 ? 
                    'bg-green-900/50 text-green-400' : 
                    learningData.personalized_recommendations.position_size_multiplier < 0.9 ?
                    'bg-red-900/50 text-red-400' : 'bg-gray-800 text-gray-300'
                  }`}>
                    {learningData.personalized_recommendations.position_size_multiplier > 1 ? '+' : ''}
                    {((learningData.personalized_recommendations.position_size_multiplier - 1) * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Рівень ризику</span>
                  <span className={`px-2 py-1 text-xs rounded ${
                    learningData.personalized_recommendations.risk_level === 'low' ? 'bg-green-900/50 text-green-400' :
                    learningData.personalized_recommendations.risk_level === 'high' ? 'bg-red-900/50 text-red-400' :
                    'bg-yellow-900/50 text-yellow-400'
                  }`}>
                    {learningData.personalized_recommendations.risk_level === 'low' ? 'Низький' :
                     learningData.personalized_recommendations.risk_level === 'high' ? 'Високий' : 'Середній'}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Час утримання</span>
                  <span className="px-2 py-1 text-xs bg-blue-900/50 text-blue-400 rounded">
                    {learningData.personalized_recommendations.holding_time === 'short_term' ? 'Короткий' :
                     learningData.personalized_recommendations.holding_time === 'long_term' ? 'Довгий' : 'Середній'}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          {/* Якість сигналу */}
          <div className="mt-3 pt-3 border-t border-gray-700/50">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-400">Якість сигналу</div>
                <div className={`text-lg font-bold ${
                  learningData.signal_quality > 0.7 ? 'text-green-400' :
                  learningData.signal_quality > 0.6 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {learningData.signal_quality > 0.7 ? 'Висока' :
                   learningData.signal_quality > 0.6 ? 'Середня' : 'Низька'} 
                  ({learningData.signal_quality * 100}%)
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-400">Подібних знайдено</div>
                <div className="text-lg font-bold">
                  {learningData.similar_patterns_found || 0}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ===== ОСНОВНИЙ СИГНАЛ ===== */}
      <SignalDisplay 
        signal={signal}
        onTrack={onTrack}
        loading={loading}
        analyzing={analyzing}
        onTimeframeChange={onTimeframeChange}
      />

      {/* ===== ПІДВАЛ З НАВЧАННЯМ ===== */}
      <div className="text-center text-xs text-gray-500 pt-3 border-t border-gray-800/50">
        <div className="flex flex-wrap justify-center gap-3 mb-1">
          <span>🧠 AI Learning v2.0</span>
          <span>•</span>
          <span>📊 {learningReport.total_signals} сигналів</span>
          <span>•</span>
          <span>🎯 {learningReport.current_accuracy ? (learningReport.current_accuracy * 100).toFixed(1) : '0'}% точність</span>
        </div>
        {signal?.learning_data?.training_mode && (
          <div className="mt-1 text-blue-400">
            ⚡ Режим навчання активний
          </div>
        )}
      </div>
    </div>
  );
};

export default LearningSignalDisplay;