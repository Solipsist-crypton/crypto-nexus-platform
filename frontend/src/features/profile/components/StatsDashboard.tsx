// frontend/src/features/profile/components/StatsDashboard.tsx
import React from 'react';
import { TrendingUp, TrendingDown, Target, DollarSign, Clock, BarChart3 } from 'lucide-react';

interface StatsDashboardProps {
  stats: any;
  timeframe: '7d' | '30d' | '90d' | 'all';
}

const StatsDashboard: React.FC<StatsDashboardProps> = ({ stats, timeframe }) => {
  const statsCards = [
    {
      title: 'Віртуальний баланс',
      value: `$${(stats.virtual_balance || 25000).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      change: stats.total_pnl ? `${parseFloat(stats.total_pnl) >= 0 ? '+' : ''}${parseFloat(stats.total_pnl).toFixed(2)}%` : '+0.00%',
      isPositive: stats.total_pnl ? parseFloat(stats.total_pnl) >= 0 : true,
      icon: DollarSign,
      color: 'from-green-500 to-emerald-600',
      description: 'Поточний стан рахунку'
    },
    {
      title: 'Загальний PnL',
      value: stats.total_pnl ? `${parseFloat(stats.total_pnl) >= 0 ? '+' : ''}${parseFloat(stats.total_pnl).toFixed(2)}%` : '+0.00%',
      change: stats.total_trades ? `${stats.total_trades} угод` : '0 угод',
      isPositive: stats.total_pnl ? parseFloat(stats.total_pnl) >= 0 : true,
      icon: TrendingUp,
      color: 'from-blue-500 to-cyan-600',
      description: `За ${timeframe === '7d' ? '7 днів' : timeframe === '30d' ? '30 днів' : timeframe === '90d' ? '90 днів' : 'весь час'}`
    },
    {
      title: 'Win Rate',
      value: typeof stats.win_rate === 'string' ? stats.win_rate : `${stats.win_rate || 0}%`,
      change: stats.winning_trades ? `${stats.winning_trades} виграшів` : '0 виграшів',
      isPositive: (stats.win_rate && parseFloat(stats.win_rate) >= 50) || true,
      icon: Target,
      color: 'from-purple-500 to-pink-600',
      description: 'Ефективність системи'
    },
    {
      title: 'Активних угод',
      value: stats.active_trades || 0,
      change: stats.closed_trades ? `${stats.closed_trades} завершених` : '0 завершених',
      isPositive: true,
      icon: Clock,
      color: 'from-orange-500 to-amber-600',
      description: 'Поточні позиції'
    },
    {
      title: 'Середній PnL',
      value: stats.avg_pnl ? `${parseFloat(stats.avg_pnl) >= 0 ? '+' : ''}${parseFloat(stats.avg_pnl).toFixed(2)}%` : '+0.00%',
      change: stats.best_trade ? `Найкраща: +${parseFloat(stats.best_trade).toFixed(2)}%` : 'Найкраща: +0.00%',
      isPositive: stats.avg_pnl ? parseFloat(stats.avg_pnl) >= 0 : true,
      icon: BarChart3,
      color: 'from-indigo-500 to-violet-600',
      description: 'На угоду'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {statsCards.map((card, index) => {
        const Icon = card.icon;
        
        return (
          <div
            key={index}
            className="bg-gray-800/60 backdrop-blur-lg rounded-2xl p-5 border border-gray-700/50 hover:border-gray-600/50 transition-all duration-300 hover:scale-[1.02] group"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="text-sm text-gray-400 font-medium mb-1">{card.title}</div>
                <div className="text-2xl font-bold">{card.value}</div>
              </div>
              <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color}`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className={`text-sm font-medium ${card.isPositive ? 'text-green-400' : 'text-red-400'}`}>
                {card.isPositive ? (
                  <span className="flex items-center">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    {card.change}
                  </span>
                ) : (
                  <span className="flex items-center">
                    <TrendingDown className="w-4 h-4 mr-1" />
                    {card.change}
                  </span>
                )}
              </div>
              <div className="text-xs text-gray-500">{card.description}</div>
            </div>
            
            {/* Прогрес-бар для Win Rate */}
            {card.title === 'Win Rate' && (
              <div className="mt-4">
                <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${card.isPositive ? 'bg-gradient-to-r from-green-500 to-emerald-500' : 'bg-gradient-to-r from-red-500 to-orange-500'}`}
                    style={{ 
                      width: `${Math.min(100, parseFloat(card.value) || 0)}%` 
                    }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default StatsDashboard;