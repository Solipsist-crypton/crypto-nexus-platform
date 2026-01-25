// frontend/src/components/futures/StatsCards.tsx
import React from 'react';

interface StatsCardsProps {
  stats: {
    active_trades?: number;
    closed_trades?: number;
    win_rate?: number | string;
    total_pnl?: number | string;
    total_trades?: number;
    winning_trades?: number;
    losing_trades?: number;
  };
}

const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const cards = [
    {
      title: 'Активних угод',
      value: stats.active_trades || 0,
      icon: '🟢',
      color: 'text-green-400',
      bgColor: 'bg-gray-800',
      description: 'Відкриті позиції',
    },
    {
      title: 'Завершених',
      value: stats.closed_trades || 0,
      icon: '📊',
      color: 'text-blue-400',
      bgColor: 'bg-gray-800',
      description: 'Вся історія',
    },
    {
      title: 'Win Rate',
      value: typeof stats.win_rate === 'number' 
        ? `${stats.win_rate.toFixed(1)}%` 
        : `${stats.win_rate || '0'}%`,
      icon: '🎯',
      color: 'text-yellow-400',
      bgColor: 'bg-gray-800',
      description: 'Ефективність системи',
    },
    {
      title: 'Загальний PnL',
      value: typeof stats.total_pnl === 'number'
        ? `${stats.total_pnl >= 0 ? '+' : ''}${stats.total_pnl.toFixed(2)}%`
        : `${stats.total_pnl || '0'}%`,
      icon: '💰',
      color: stats.total_pnl && parseFloat(String(stats.total_pnl)) >= 0 
        ? 'text-green-400' 
        : 'text-red-400',
      bgColor: 'bg-gray-800',
      description: 'Сумарний прибуток/збиток',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`${card.bgColor} rounded-xl p-5 transition-transform hover:scale-[1.02]`}
        >
          <div className="flex justify-between items-start mb-3">
            <div>
              <div className="text-gray-400 text-sm">{card.title}</div>
              <div className={`text-3xl font-bold mt-1 ${card.color}`}>
                {card.value}
              </div>
            </div>
            <div className="text-3xl">{card.icon}</div>
          </div>
          <div className="text-gray-500 text-sm">{card.description}</div>
          
          {/* Прогрес-бар для Win Rate */}
          {card.title === 'Win Rate' && stats.winning_trades !== undefined && stats.losing_trades !== undefined && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Виграші: {stats.winning_trades}</span>
                <span>Програші: {stats.losing_trades}</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-yellow-500 rounded-full"
                  style={{ 
                    width: `${typeof stats.win_rate === 'number' ? stats.win_rate : parseFloat(String(stats.win_rate || 0))}%` 
                  }}
                ></div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default StatsCards;