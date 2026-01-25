// frontend/src/features/profile/components/PerformanceChart.tsx
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface PerformanceChartProps {
  trades: any[];
  timeframe: '7d' | '30d' | '90d' | 'all';
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ trades }) => {
  // Аналіз угод за символами
  const analyzeBySymbol = () => {
    const symbolMap: Record<string, { wins: number; losses: number; total: number; pnl: number }> = {};
    
    trades.forEach(trade => {
      if (!symbolMap[trade.symbol]) {
        symbolMap[trade.symbol] = { wins: 0, losses: 0, total: 0, pnl: 0 };
      }
      
      symbolMap[trade.symbol].total++;
      symbolMap[trade.symbol].pnl += trade.pnl_percentage || 0;
      
      if (trade.pnl_percentage > 0) {
        symbolMap[trade.symbol].wins++;
      } else if (trade.pnl_percentage < 0) {
        symbolMap[trade.symbol].losses++;
      }
    });
    
    return Object.entries(symbolMap).map(([symbol, data]) => ({
      symbol: symbol.split(':')[0],
      winRate: data.total > 0 ? (data.wins / data.total) * 100 : 0,
      totalTrades: data.total,
      avgPnl: data.total > 0 ? (data.pnl / data.total) : 0
    })).sort((a, b) => b.winRate - a.winRate).slice(0, 6); // Топ 6
  };

  const performanceData = analyzeBySymbol();

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-xl font-bold flex items-center">
          <span className="mr-2">🎯</span> Ефективність по монетах
        </h3>
        <p className="text-gray-400">Win Rate та середній PnL за символами</p>
      </div>
      
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="symbol" 
              stroke="#9CA3AF"
              fontSize={12}
            />
            <YAxis 
              stroke="#9CA3AF"
              fontSize={12}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              contentStyle={{ 
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              formatter={(value: any, name: string) => {
                if (name === 'winRate') return [`${value.toFixed(1)}%`, 'Win Rate'];
                if (name === 'avgPnl') return [`${parseFloat(value) >= 0 ? '+' : ''}${parseFloat(value).toFixed(2)}%`, 'Середній PnL'];
                return [value, name];
              }}
            />
            <Bar 
              dataKey="winRate" 
              name="Win Rate"
              radius={[4, 4, 0, 0]}
            >
              {performanceData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`}
                  fill={entry.winRate >= 70 ? '#10B981' : entry.winRate >= 50 ? '#F59E0B' : '#EF4444'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Легенда та статистика */}
      <div className="grid grid-cols-2 gap-4 mt-6">
        <div className="p-3 bg-gray-900/50 rounded-lg">
          <div className="text-sm text-gray-400 mb-1">Найкраща монета</div>
          {performanceData.length > 0 ? (
            <>
              <div className="text-lg font-bold">{performanceData[0].symbol}</div>
              <div className="text-green-400 text-sm">{performanceData[0].winRate.toFixed(1)}% Win Rate</div>
            </>
          ) : (
            <div className="text-gray-500">Немає даних</div>
          )}
        </div>
        
        <div className="p-3 bg-gray-900/50 rounded-lg">
          <div className="text-sm text-gray-400 mb-1">Всього монет</div>
          <div className="text-lg font-bold">{performanceData.length}</div>
          <div className="text-gray-400 text-sm">в аналізі</div>
        </div>
      </div>
      
      {/* Легенда кольорів */}
      <div className="flex items-center justify-center gap-4 mt-4 text-xs">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded mr-1"></div>
          <span className="text-gray-400">≥70% Win Rate</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-yellow-500 rounded mr-1"></div>
          <span className="text-gray-400">50-69% Win Rate</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-500 rounded mr-1"></div>
          <span className="text-gray-400">{'<'}50% Win Rate</span>
        </div>
      </div>
    </div>
  );
};

export default PerformanceChart;