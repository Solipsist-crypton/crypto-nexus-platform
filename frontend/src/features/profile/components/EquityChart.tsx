// frontend/src/features/profile/components/EquityChart.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface EquityChartProps {
  trades: any[];
  timeframe: '7d' | '30d' | '90d' | 'all';
}

const EquityChart: React.FC<EquityChartProps> = ({ trades, timeframe }) => {
  // Генерація тестових даних для графіка (тимчасово)
  const generateEquityData = () => {
    const data = [];
    let equity = 10000;
    
    for (let i = 0; i < 30; i++) {
      const change = (Math.random() - 0.45) * 4; // Від -2% до +2%
      equity = equity * (1 + change / 100);
      
      data.push({
        day: `День ${i + 1}`,
        equity: Math.round(equity),
        pnl: change
      });
    }
    
    return data;
  };

  const chartData = generateEquityData();
  const currentEquity = chartData[chartData.length - 1]?.equity || 10000;
  const startingEquity = chartData[0]?.equity || 10000;
  const totalChange = ((currentEquity - startingEquity) / startingEquity) * 100;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold flex items-center">
            <span className="mr-2">📈</span> Крива капіталу
          </h3>
          <p className="text-gray-400">Динаміка віртуального балансу</p>
        </div>
        <div className={`text-2xl font-bold ${totalChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {totalChange >= 0 ? '+' : ''}{totalChange.toFixed(2)}%
        </div>
      </div>
      
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="day" 
              stroke="#9CA3AF"
              fontSize={12}
            />
            <YAxis 
              stroke="#9CA3AF"
              fontSize={12}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip
              contentStyle={{ 
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              formatter={(value: any) => [`$${value}`, 'Капітал']}
              labelFormatter={(label) => `Період: ${label}`}
            />
            <Area
              type="monotone"
              dataKey="equity"
              stroke="#10B981"
              strokeWidth={3}
              fill="url(#equityGradient)"
              activeDot={{ r: 6, fill: '#10B981' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="text-center p-3 bg-gray-900/50 rounded-lg">
          <div className="text-sm text-gray-400">Початковий</div>
          <div className="text-lg font-bold">${startingEquity.toLocaleString()}</div>
        </div>
        <div className="text-center p-3 bg-gray-900/50 rounded-lg">
          <div className="text-sm text-gray-400">Поточний</div>
          <div className="text-lg font-bold">${currentEquity.toLocaleString()}</div>
        </div>
        <div className="text-center p-3 bg-gray-900/50 rounded-lg">
          <div className="text-sm text-gray-400">Прибуток</div>
          <div className={`text-lg font-bold ${totalChange >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ${(currentEquity - startingEquity).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EquityChart;