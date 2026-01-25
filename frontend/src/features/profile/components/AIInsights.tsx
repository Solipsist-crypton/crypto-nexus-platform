// frontend/src/features/profile/components/AIInsights.tsx
import React from 'react';
import { Brain, TrendingUp, AlertTriangle, Zap, Target, BarChart } from 'lucide-react';

interface AIInsightsProps {
  stats: any;
  trades: any[];
}

const AIInsights: React.FC<AIInsightsProps> = ({ stats, trades }) => {
  const generateInsights = () => {
    const insights = [];
    
    // Аналіз Win Rate
    const winRate = parseFloat(stats.win_rate) || 0;
    if (winRate >= 70) {
      insights.push({
        type: 'success',
        icon: TrendingUp,
        title: 'Відмінна ефективність!',
        description: `Ваш Win Rate ${winRate}% вище середнього. Продовжуйте в тому ж дусі!`,
        action: 'Розгляньте збільшення розміру позицій'
      });
    } else if (winRate >= 50) {
      insights.push({
        type: 'info',
        icon: Target,
        title: 'Стабільні результати',
        description: `Win Rate ${winRate}% показує стабільну роботу системи.`,
        action: 'Оптимізуйте точність входу в позиції'
      });
    } else {
      insights.push({
        type: 'warning',
        icon: AlertTriangle,
        title: 'Потрібна оптимізація',
        description: `Win Rate ${winRate}% нижче оптимального. Перегляньте стратегію.`,
        action: 'Аналізуйте невдалі угоди'
      });
    }
    
    // Аналіз активних угод
    const activeTrades = trades.filter(t => t.status === 'active');
    if (activeTrades.length > 5) {
      insights.push({
        type: 'warning',
        icon: AlertTriangle,
        title: 'Забагато активних угод',
        description: `${activeTrades.length} активних позицій може збільшити ризик.`,
        action: 'Розгляньте закриття частини позицій'
      });
    }
    
    // Аналіз PnL
    const totalPnl = parseFloat(stats.total_pnl) || 0;
    if (totalPnl > 10) {
      insights.push({
        type: 'success',
        icon: Zap,
        title: 'Вражаючий прибуток!',
        description: `Загальний PnL +${totalPnl.toFixed(2)}% демонструє майстерність.`,
        action: 'Розгляньте стратегію масштабування'
      });
    }
    
    // Рекомендація по монетам
    const symbolPerformance = trades.reduce((acc, trade) => {
      if (!acc[trade.symbol]) acc[trade.symbol] = { wins: 0, total: 0 };
      acc[trade.symbol].total++;
      if (trade.pnl_percentage > 0) acc[trade.symbol].wins++;
      return acc;
    }, {});
    
    const bestSymbol = Object.entries(symbolPerformance)
      .map(([symbol, data]: [string, any]) => ({
        symbol,
        winRate: (data.wins / data.total) * 100
      }))
      .sort((a, b) => b.winRate - a.winRate)[0];
    
    if (bestSymbol && bestSymbol.winRate > 60) {
      insights.push({
        type: 'info',
        icon: BarChart,
        title: 'Сильна монета',
        description: `${bestSymbol.symbol} показує ${bestSymbol.winRate.toFixed(1)}% Win Rate.`,
        action: 'Розгляньте більше угод з цією монетою'
      });
    }
    
    // Якщо мало інсайтів, додаємо загальні
    if (insights.length < 2) {
      insights.push({
        type: 'info',
        icon: Brain,
        title: 'Порада від AI',
        description: 'Система AI рекомендує тестувати різні стратегії на віртуальних угодах.',
        action: 'Експериментуйте з різними параметрами ризику'
      });
    }
    
    return insights.slice(0, 3); // Максимум 3 інсайта
  };

  const insights = generateInsights();
  
  const typeConfig = {
    success: { color: 'text-green-400', bg: 'bg-green-900/20', border: 'border-green-800/30' },
    warning: { color: 'text-yellow-400', bg: 'bg-yellow-900/20', border: 'border-yellow-800/30' },
    info: { color: 'text-blue-400', bg: 'bg-blue-900/20', border: 'border-blue-800/30' }
  };

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl">
          <Brain className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-xl font-bold">AI Аналіз & Рекомендації</h3>
          <p className="text-gray-400">Персональні інсайти на основі вашої статистики</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {insights.map((insight, index) => {
          const config = typeConfig[insight.type as keyof typeof typeConfig];
          const Icon = insight.icon;
          
          return (
            <div
              key={index}
              className={`p-5 rounded-xl border ${config.border} ${config.bg} hover:scale-[1.02] transition-transform duration-300`}
            >
              <div className="flex items-start gap-3 mb-3">
                <div className={`p-2 rounded-lg ${config.bg}`}>
                  <Icon className={`w-5 h-5 ${config.color}`} />
                </div>
                <div>
                  <h4 className={`font-bold ${config.color}`}>{insight.title}</h4>
                  <p className="text-sm text-gray-300 mt-1">{insight.description}</p>
                </div>
              </div>
              
              <div className="mt-4 pt-3 border-t border-gray-700">
                <div className="text-xs text-gray-400 mb-1">Рекомендація:</div>
                <div className="text-sm font-medium">{insight.action}</div>
              </div>
            </div>
          );
        })}
      </div>
      
      {insights.length === 0 && (
        <div className="text-center py-8">
          <div className="text-4xl mb-3">🤖</div>
          <h4 className="text-lg font-medium mb-2">AI аналізує ваші дані</h4>
          <p className="text-gray-400">Після кількох угод з'являться персональні рекомендації</p>
        </div>
      )}
    </div>
  );
};

export default AIInsights;