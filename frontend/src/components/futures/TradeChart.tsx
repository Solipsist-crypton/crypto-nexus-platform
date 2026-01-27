// frontend/src/components/futures/TradeChart.tsx
import React, { useEffect, useState, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, ReferenceLine,
  Scatter, Legend, ReferenceArea,
  Label
} from 'recharts';
import { fetchTradeHistory } from '../../services/futuresApi';

interface TradeChartProps {
  trade: {
    id: number;
    symbol: string;
    entry_price: number;
    take_profit?: number;
    stop_loss?: number;
    current_price: number;
    direction: 'long' | 'short';
    pnl_percentage: number;
    created_at: string;
    status?: 'active' | 'closed';
  };
}

// Кастомний маркер для точки входу
const EntryPointMarker = (props: any) => {
  const { cx, cy } = props;
  return (
    <g>
      <circle cx={cx} cy={cy} r={8} fill="#3B82F6" stroke="white" strokeWidth={2} />
      <text 
        x={cx} 
        y={cy - 12} 
        textAnchor="middle" 
        fill="#3B82F6" 
        fontSize={9}
        fontWeight="bold"
      >
        ВХІД
      </text>
    </g>
  );
};

// Маркер поточної ціни
const CurrentPriceMarker = (props: any) => {
  const { cx, cy } = props;
  return (
    <g>
      <circle cx={cx} cy={cy} r={6} fill="#F59E0B" stroke="white" strokeWidth={2} />
      <text 
        x={cx} 
        y={cy - 12} 
        textAnchor="middle" 
        fill="#F59E0B" 
        fontSize={9}
        fontWeight="bold"
      >
        ЗАРАЗ
      </text>
    </g>
  );
};

const TradeChart: React.FC<TradeChartProps> = ({ trade }) => {
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<'1h' | '4h' | '1d'>('1h');
  const [dataSource, setDataSource] = useState<'live' | 'simulation'>('live');
  
  const isLong = trade.direction === 'long';
  const entryTime = new Date(trade.created_at);

  // Розраховуємо відсотки відстані до TP/SL
  const tpPercentage = trade.take_profit 
    ? ((trade.take_profit - trade.entry_price) / trade.entry_price) * 100
    : 0;
    
  const slPercentage = trade.stop_loss 
    ? ((trade.stop_loss - trade.entry_price) / trade.entry_price) * 100
    : 0;

  const distanceToTP = trade.take_profit 
    ? Math.abs(((trade.current_price - trade.take_profit) / trade.entry_price) * 100)
    : 0;
    
  const distanceToSL = trade.stop_loss 
    ? Math.abs(((trade.current_price - trade.stop_loss) / trade.entry_price) * 100)
    : 0;

  // Знаходимо точку входу на графіку
  const entryPoint = useMemo(() => {
    if (!historicalData.length) return null;
    
    // Шукаємо точку найближчу до часу входу
    let closestPoint = historicalData[0];
    let minDiff = Math.abs(new Date(closestPoint.time).getTime() - entryTime.getTime());
    
    historicalData.forEach(point => {
      const diff = Math.abs(new Date(point.time).getTime() - entryTime.getTime());
      if (diff < minDiff) {
        minDiff = diff;
        closestPoint = point;
      }
    });
    
    return {
      time: closestPoint.time,
      price: trade.entry_price,
      x: closestPoint.time,
      y: trade.entry_price
    };
  }, [historicalData, trade.entry_price, entryTime]);

  // Знаходимо точку поточної ціни
  const currentPricePoint = useMemo(() => {
    if (!historicalData.length) return null;
    
    const latestPoint = historicalData[historicalData.length - 1];
    return {
      time: latestPoint.time,
      price: trade.current_price,
      x: latestPoint.time,
      y: trade.current_price
    };
  }, [historicalData, trade.current_price]);

  // Додаємо більш наочні зони для TP/SL
  const enhancedZones = useMemo(() => {
    if (!trade.stop_loss || !trade.take_profit) return null;
    
    return {
      tpZone: {
        y1: isLong ? trade.entry_price : trade.take_profit,
        y2: isLong ? trade.take_profit : trade.entry_price,
        fill: 'rgba(16, 185, 129, 0.15)',
        border: '#10B981'
      },
      slZone: {
        y1: isLong ? trade.stop_loss : trade.entry_price,
        y2: isLong ? trade.entry_price : trade.stop_loss,
        fill: 'rgba(239, 68, 68, 0.15)',
        border: '#EF4444'
      }
    };
  }, [trade, isLong]);

  // Custom Tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const isEntryPoint = entryPoint && Math.abs(new Date(label).getTime() - new Date(entryPoint.time).getTime()) < 3600000;
      
      return (
        <div className="bg-gray-900 border border-gray-700 p-3 rounded-lg shadow-lg">
          <p className="text-gray-300 text-sm mb-1">
            {new Date(label).toLocaleString('uk-UA', {
              day: 'numeric',
              month: 'short',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </p>
          
          {isEntryPoint && (
            <div className="mb-2 p-2 bg-blue-900/30 rounded">
              <p className="text-blue-300 text-xs font-bold">📍 ТОЧКА ВХОДУ</p>
              <p className="text-blue-400 text-xs">${trade.entry_price.toFixed(2)}</p>
            </div>
          )}
          
          <div className="space-y-1">
            <p className="text-white text-sm">
              Ціна: <span className="font-mono">${payload[0]?.value.toFixed(2)}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  // Завантаження даних
  useEffect(() => {
    if (trade?.id) {
      fetchTradeHistoryData();
    }
  }, [trade?.id, timeframe]);

  const fetchTradeHistoryData = async () => {
    try {
      setLoading(true);
      
      const response = await fetchTradeHistory(trade.id, timeframe, 24);
      
      if (response?.history && response.history.length > 0) {
        const formattedData = response.history.map((item: any) => ({
          time: item.time,
          price: item.close,
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
          volume: item.volume
        }));
        
        setHistoricalData(formattedData);
        setDataSource('live');
      } else {
        setHistoricalData(generateSimulationData());
        setDataSource('simulation');
      }
    } catch (err: any) {
      console.error('Помилка завантаження:', err);
      setHistoricalData(generateSimulationData());
      setDataSource('simulation');
    } finally {
      setLoading(false);
    }
  };

  const generateSimulationData = () => {
    const data = [];
    const basePrice = trade.entry_price;
    const symbol = trade.symbol.split('/')[0];
    
    const volatility = {
      'BTC': 0.015, 'ETH': 0.020, 'SOL': 0.030,
      'XRP': 0.025, 'ADA': 0.028, 'BNB': 0.018,
      'AVAX': 0.035, 'DOGE': 0.045, 'LINK': 0.025
    }[symbol] || 0.025;
    
    const trend = 0.01 * (isLong ? 1 : -1);
    
    for (let i = 0; i < 24; i++) {
      const randomWalk = (Math.random() - 0.5) * 2 * volatility;
      const priceChange = trend + randomWalk;
      const price = basePrice * (1 + priceChange);
      
      const openPrice = price * (1 - volatility/4);
      const highPrice = price * (1 + volatility/3);
      const lowPrice = price * (1 - volatility/3);
      const closePrice = price;
      
      data.push({
        time: new Date(Date.now() - (24 - i) * 3600000).toISOString(),
        price: closePrice,
        open: openPrice,
        high: highPrice,
        low: lowPrice,
        close: closePrice,
        volume: Math.random() * 1000 + 500
      });
    }
    
    return data;
  };

  const refreshData = () => {
    fetchTradeHistoryData();
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
      {/* Заголовок */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-3">
          <div>
            <h3 className="text-xl font-bold">
              📊 {trade.symbol} • {isLong ? '📈 LONG' : '📉 SHORT'}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <div className={`px-2 py-1 rounded text-xs ${dataSource === 'live' ? 'bg-green-900/30 text-green-400' : 'bg-blue-900/30 text-blue-400'}`}>
                {dataSource === 'live' ? '🔄 LIVE' : '📈 SIMULATION'}
              </div>
              <div className="text-xs text-gray-500">
                Час входу: {entryTime.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
          
          <div className="flex gap-2">
            {(['1h', '4h', '1d'] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 rounded text-sm ${
                  timeframe === tf 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
                disabled={loading}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* Візуалізація дистанції до цілей */}
        {trade.take_profit && trade.stop_loss && (
          <div className="mb-4 p-3 bg-gray-900/50 rounded-lg border border-gray-700">
            <div className="grid grid-cols-3 gap-4 mb-3">
              <div className="text-center">
                <div className="text-xs text-gray-400 mb-1">Stop Loss</div>
                <div className="text-red-400 font-bold">${trade.stop_loss.toFixed(2)}</div>
                <div className="text-xs text-gray-500">{slPercentage.toFixed(2)}%</div>
              </div>
              
              <div className="text-center">
                <div className="text-xs text-gray-400 mb-1">Entry Price</div>
                <div className="text-blue-400 font-bold">${trade.entry_price.toFixed(2)}</div>
                <div className="text-xs text-gray-500">0%</div>
              </div>
              
              <div className="text-center">
                <div className="text-xs text-gray-400 mb-1">Take Profit</div>
                <div className="text-green-400 font-bold">${trade.take_profit.toFixed(2)}</div>
                <div className="text-xs text-gray-500">+{tpPercentage.toFixed(2)}%</div>
              </div>
            </div>
            
            {/* Прогрес бар */}
            <div className="relative h-6 bg-gray-800 rounded-full overflow-hidden">
              <div className="absolute inset-0 flex">
                <div className="h-full bg-red-500/20" style={{ width: '50%' }}></div>
                <div className="h-full bg-green-500/20" style={{ width: '50%' }}></div>
              </div>
              
              {/* Маркер поточної ціни */}
              <div 
                className="absolute top-1/2 h-8 w-8 bg-yellow-500 rounded-full border-2 border-white transform -translate-y-1/2 -translate-x-1/2 z-20 flex items-center justify-center"
                style={{ 
                  left: isLong 
                    ? `${50 + (trade.current_price - trade.entry_price) / (trade.take_profit - trade.entry_price) * 50}%`
                    : `${50 - (trade.entry_price - trade.current_price) / (trade.entry_price - trade.take_profit) * 50}%`,
                }}
                title={`Поточна ціна: $${trade.current_price.toFixed(2)}`}
              >
                <span className="text-xs font-bold text-black">●</span>
              </div>
              
              {/* Маркер входу */}
              <div 
                className="absolute top-1/2 left-1/2 h-6 w-6 bg-blue-500 rounded-full border-2 border-white transform -translate-y-1/2 -translate-x-1/2 z-10"
                title={`Вхід: $${trade.entry_price.toFixed(2)}`}
              ></div>
            </div>
            
            <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
              <div className="text-red-400">
                <span className="font-medium">🔴 До SL:</span> {distanceToSL.toFixed(2)}%
              </div>
              <div className="text-green-400 text-right">
                <span className="font-medium">🟢 До TP:</span> {distanceToTP.toFixed(2)}%
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Графік */}
      {loading ? (
        <div className="h-80 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-2 border-blue-500 border-t-transparent mx-auto mb-4"></div>
            <p className="text-gray-400">
              {dataSource === 'live' 
                ? 'Завантаження даних...' 
                : 'Генерація моделювання...'}
            </p>
          </div>
        </div>
      ) : (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={historicalData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              
              <XAxis 
                dataKey="time" 
                stroke="#9CA3AF"
                fontSize={11}
                tickFormatter={(time) => {
                  const date = new Date(time);
                  if (timeframe === '1h') {
                    return date.toLocaleTimeString('uk-UA', { hour: '2-digit' });
                  } else {
                    return date.toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' });
                  }
                }}
              />
              
              <YAxis 
                stroke="#9CA3AF"
                fontSize={11}
                domain={['auto', 'auto']}
                tickFormatter={(value) => `$${value.toFixed(0)}`}
              />
              
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {/* Кольорові зони TP/SL */}
              {enhancedZones && (
                <>
                  <ReferenceArea
                    y1={enhancedZones.tpZone.y1}
                    y2={enhancedZones.tpZone.y2}
                    fill={enhancedZones.tpZone.fill}
                    stroke={enhancedZones.tpZone.border}
                    strokeWidth={1}
                    strokeDasharray="3 3"
                  />
                  
                  <ReferenceArea
                    y1={enhancedZones.slZone.y1}
                    y2={enhancedZones.slZone.y2}
                    fill={enhancedZones.slZone.fill}
                    stroke={enhancedZones.slZone.border}
                    strokeWidth={1}
                    strokeDasharray="3 3"
                  />
                </>
              )}
              
              {/* Вертикальна лінія часу входу */}
              {entryPoint && (
                <ReferenceLine
                  x={entryPoint.time}
                  stroke="#3B82F6"
                  strokeWidth={2}
                  label={{
                    value: '⏰ ВХІД',
                    position: 'top',
                    fill: '#3B82F6',
                    fontSize: 12,
                    fontWeight: 'bold',
                  }}
                />
              )}
              
              {/* Горизонтальні лінії TP/SL */}
              {trade.take_profit && (
                <ReferenceLine
                  y={trade.take_profit}
                  stroke="#10B981"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  label={{
                    value: `🟢 TP: $${trade.take_profit.toFixed(2)}`,
                    position: 'right',
                    fill: '#10B981',
                    fontSize: 11,
                    fontWeight: 'bold'
                  }}
                />
              )}
              
              {trade.stop_loss && (
                <ReferenceLine
                  y={trade.stop_loss}
                  stroke="#EF4444"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  label={{
                    value: `🔴 SL: $${trade.stop_loss.toFixed(2)}`,
                    position: 'right',
                    fill: '#EF4444',
                    fontSize: 11,
                    fontWeight: 'bold'
                  }}
                />
              )}
              
              {/* Лінія ціни входу */}
              <ReferenceLine
                y={trade.entry_price}
                stroke="#3B82F6"
                strokeWidth={2}
                strokeDasharray="5 5"
                label={{
                  value: `ВХІД: $${trade.entry_price.toFixed(2)}`,
                  position: 'right',
                  fill: '#3B82F6',
                  fontSize: 11,
                  fontWeight: 'bold'
                }}
              />
              
              {/* Основна лінія графіка */}
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#FFFFFF" 
                strokeWidth={2}
                dot={false}
                name="Ціна"
                activeDot={{ r: 4, fill: '#F59E0B' }}
              />
              
              {/* Точка входу */}
              {entryPoint && (
                <Scatter
                  data={[entryPoint]}
                  shape={<EntryPointMarker />}
                  name="Точка входу"
                />
              )}
              
              {/* Точка поточної ціни */}
              {currentPricePoint && (
                <Scatter
                  data={[currentPricePoint]}
                  shape={<CurrentPriceMarker />}
                  name="Поточна ціна"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
      
      {/* Футер */}
      <div className="mt-4 pt-3 border-t border-gray-700">
        <div className="flex justify-between items-center">
          <div className="text-xs text-gray-500">
            {dataSource === 'live' ? '🔄 Live Binance' : '📈 Market simulation'} • 
            PnL: <span className={trade.pnl_percentage >= 0 ? 'text-green-400' : 'text-red-400'}>
              {trade.pnl_percentage >= 0 ? '+' : ''}{trade.pnl_percentage.toFixed(2)}%
            </span>
          </div>
          <button
            onClick={refreshData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 rounded text-sm bg-gray-700 hover:bg-gray-600 text-gray-300"
          >
            {loading ? '⟳' : '🔄'} Оновити
          </button>
        </div>
      </div>
    </div>
  );
};

export default TradeChart;