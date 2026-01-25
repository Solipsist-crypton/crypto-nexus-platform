// frontend/src/features/profile/components/PerformanceChart.tsx
import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface PerformanceChartProps {
  trades: any[];
  timeframe: '7d' | '30d' | '90d' | 'all';
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ trades, timeframe }) => {
  // Фільтруємо угоди за вибраним періодом
  const filteredTrades = useMemo(() => {
    if (timeframe === 'all') return trades;
    
    const daysMap = {
      '7d': 7,
      '30d': 30,
      '90d': 90
    };
    
    const days = daysMap[timeframe];
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    return trades.filter(trade => {
      if (!trade.created_at) return true;
      const tradeDate = new Date(trade.created_at);
      return tradeDate >= cutoffDate;
    });
  }, [trades, timeframe]);

  // Розширений аналіз за символами
  const analyzeBySymbol = () => {
    const symbolMap: Record<string, { 
      wins: number; 
      losses: number; 
      total: number; 
      totalPnl: number;
      bestTrade: number;
      worstTrade: number;
    }> = {};
    
    filteredTrades.forEach(trade => {
      const symbol = trade.symbol ? trade.symbol.split(':')[0] : 'Unknown';
      
      if (!symbolMap[symbol]) {
        symbolMap[symbol] = { 
          wins: 0, 
          losses: 0, 
          total: 0, 
          totalPnl: 0,
          bestTrade: -Infinity,
          worstTrade: Infinity
        };
      }
      
      const pnl = trade.pnl_percentage || 0;
      
      symbolMap[symbol].total++;
      symbolMap[symbol].totalPnl += pnl;
      
      // Оновлюємо кращу/гіршу угоду
      if (pnl > symbolMap[symbol].bestTrade) {
        symbolMap[symbol].bestTrade = pnl;
      }
      if (pnl < symbolMap[symbol].worstTrade) {
        symbolMap[symbol].worstTrade = pnl;
      }
      
      if (pnl > 0) {
        symbolMap[symbol].wins++;
      } else if (pnl < 0) {
        symbolMap[symbol].losses++;
      }
    });
    
    // Конвертуємо в масив та додаємо статистику
    return Object.entries(symbolMap).map(([symbol, data]) => {
      const winRate = data.total > 0 ? (data.wins / data.total) * 100 : 0;
      const avgPnl = data.total > 0 ? (data.totalPnl / data.total) : 0;
      
      return {
        symbol,
        winRate,
        avgPnl,
        totalTrades: data.total,
        bestTrade: data.bestTrade === -Infinity ? 0 : data.bestTrade,
        worstTrade: data.worstTrade === Infinity ? 0 : data.worstTrade,
        profitFactor: data.losses > 0 ? (data.wins / data.losses) : data.wins > 0 ? 10 : 0 // Множник прибутку
      };
    }).sort((a, b) => b.winRate - a.winRate);
  };

  const performanceData = analyzeBySymbol();
  const topCoins = performanceData.slice(0, 8); // Топ 8 монет

  // Статистика по категоріях
  const stats = {
    totalCoins: performanceData.length,
    highWinRate: performanceData.filter(c => c.winRate >= 70).length,
    mediumWinRate: performanceData.filter(c => c.winRate >= 50 && c.winRate < 70).length,
    lowWinRate: performanceData.filter(c => c.winRate < 50).length,
    bestCoin: performanceData[0] || null,
    totalTrades: performanceData.reduce((sum, coin) => sum + coin.totalTrades, 0),
    filteredTradesCount: filteredTrades.length,
    timeframeLabel: timeframe === '7d' ? '7 днів' : timeframe === '30d' ? '30 днів' : timeframe === '90d' ? '90 днів' : 'весь час'
  };

  return (
    <div className="bg-gray-900 rounded-xl p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-xl font-bold flex items-center">
              <span className="mr-2">🎯</span> Ефективність по монетах
            </h3>
            <p className="text-gray-400">Win Rate та середній PnL за символами</p>
          </div>
          <div className="px-3 py-1 bg-gray-800 rounded-lg text-sm">
            <span className="text-gray-400">Період: </span>
            <span className="font-semibold">{stats.timeframeLabel}</span>
            <span className="text-gray-500 ml-2">({stats.filteredTradesCount} угод)</span>
          </div>
        </div>
      </div>
      
      {/* Графік Win Rate */}
      <div className="h-64 mb-8">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={topCoins}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="symbol" 
              stroke="#9CA3AF"
              fontSize={11}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis 
              stroke="#9CA3AF"
              fontSize={12}
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              contentStyle={{ 
                backgroundColor: '#1F2937',
                borderRadius: '8px',
                fontSize: '14px'
              }}
              formatter={(value: any, name: string) => {
                if (name === 'winRate') return [`${Number(value).toFixed(1)}%`, 'Win Rate'];
                if (name === 'avgPnl') {
                  const val = Number(value);
                  return [`${val >= 0 ? '+' : ''}${val.toFixed(2)}%`, 'Середній PnL'];
                }
                return [value, name];
              }}
              labelFormatter={(label) => `Монета: ${label}`}
            />
            <Bar 
              dataKey="winRate" 
              name="Win Rate"
              radius={[4, 4, 0, 0]}
              barSize={30}
            >
              {topCoins.map((entry, index) => {
                let fillColor;
                if (entry.winRate >= 80) fillColor = '#10B981'; // Високий
                else if (entry.winRate >= 60) fillColor = '#F59E0B'; // Середній
                else if (entry.winRate >= 40) fillColor = '#F97316'; // Низький
                else fillColor = '#EF4444'; // Дуже низький
                
                return <Cell key={`cell-${index}`} fill={fillColor} />;
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Детальна статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Найкраща монета */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-2">🏆 Найкраща монета ({stats.timeframeLabel})</div>
          {stats.bestCoin ? (
            <>
              <div className="text-lg font-bold mb-1">{stats.bestCoin.symbol}</div>
              <div className="text-green-400 text-sm font-semibold mb-1">
                {stats.bestCoin.winRate.toFixed(1)}% Win Rate
              </div>
              <div className="text-gray-400 text-xs">
                {stats.bestCoin.totalTrades} угод • Середній PnL: {stats.bestCoin.avgPnl >= 0 ? '+' : ''}{stats.bestCoin.avgPnl.toFixed(2)}%
              </div>
            </>
          ) : (
            <div className="text-gray-500">Немає даних</div>
          )}
        </div>
        
        {/* Загальна статистика */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-2">📊 Статистика монет</div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="text-2xl font-bold">{stats.totalCoins}</div>
              <div className="text-gray-400 text-xs">Всього монет</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{stats.totalTrades}</div>
              <div className="text-gray-400 text-xs">Всього угод</div>
            </div>
          </div>
          <div className="text-gray-400 text-xs mt-2">в аналізі за {stats.timeframeLabel}</div>
        </div>
        
        {/* Розподіл Win Rate */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-2">📈 Розподіл Win Rate</div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
                <span className="text-sm">≥70%</span>
              </div>
              <span className="font-bold text-green-400">{stats.highWinRate}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded mr-2"></div>
                <span className="text-sm">50-69%</span>
              </div>
              <span className="font-bold text-yellow-400">{stats.mediumWinRate}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-500 rounded mr-2"></div>
                <span className="text-sm">{'<'}50%</span>
              </div>
              <span className="font-bold text-red-400">{stats.lowWinRate}</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Додаткова інформація */}
      {performanceData.length > 0 && (
        <div className="mt-6 text-sm text-gray-400 text-center">
          {performanceData.length > 8 ? (
            <span>Показано топ 8 з {performanceData.length} монет за {stats.timeframeLabel}. Натисніть для деталей</span>
          ) : (
            <span>Проаналізовано {performanceData.length} монет за {stats.timeframeLabel}</span>
          )}
        </div>
      )}
    </div>
  );
};

export default PerformanceChart;