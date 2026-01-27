// frontend/src/components/futures/TradeChart.tsx
import React, { useEffect, useState, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, ReferenceLine,
  Scatter, Legend, Area, ReferenceArea,
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
  const { cx, cy, payload } = props;
  return (
    <g>
      {/* Велика зовнішня точка */}
      <circle cx={cx} cy={cy} r={10} fill="rgba(59, 130, 246, 0.2)" />
      {/* Внутрішня точка */}
      <circle cx={cx} cy={cy} r={6} fill="#3B82F6" stroke="white" strokeWidth={2} />
      {/* Текст "ENTRY" */}
      <text 
        x={cx} 
        y={cy - 15} 
        textAnchor="middle" 
        fill="#3B82F6" 
        fontSize={10}
        fontWeight="bold"
      >
        ENTRY
      </text>
    </g>
  );
};

// Маркер поточної ціни
const CurrentPriceMarker = (props: any) => {
  const { cx, cy } = props;
  return (
    <g>
      <circle cx={cx} cy={cy} r={8} fill="#F59E0B" stroke="white" strokeWidth={2} />
      <text 
        x={cx} 
        y={cy - 15} 
        textAnchor="middle" 
        fill="#F59E0B" 
        fontSize={10}
        fontWeight="bold"
      >
        NOW
      </text>
    </g>
  );
};

const TradeChart: React.FC<TradeChartProps> = ({ trade }) => {
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<'1h' | '4h' | '1d'>('1h');
  
  const isLong = trade.direction === 'long';
  const entryTime = new Date(trade.created_at);

  // Розраховуємо відсотки відстані до TP/SL
  const distanceToTP = trade.take_profit 
    ? Math.abs(((trade.current_price - trade.take_profit) / trade.entry_price) * 100)
    : 0;
    
  const distanceToSL = trade.stop_loss 
    ? Math.abs(((trade.current_price - trade.stop_loss) / trade.entry_price) * 100)
    : 0;

  // Знаходимо найближчу точку до входу в історичних даних
  const entryPoint = useMemo(() => {
    if (!historicalData.length) return null;
    
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

  // Додаємо вертикальну лінію часу входу
  const entryTimeLine = useMemo(() => {
    if (!historicalData.length) return null;
    return entryTime;
  }, [historicalData, entryTime]);

  // Генеруємо зони ризику/прибутку
  const riskRewardZones = useMemo(() => {
    if (!trade.stop_loss || !trade.take_profit) return null;
    
    const zones = [];
    
    if (isLong) {
      // Для LONG:
      // 🔴 Зона стоп-лосу (нижче входу)
      zones.push({
        y1: trade.stop_loss * 0.99,
        y2: trade.entry_price,
        fill: 'rgba(239, 68, 68, 0.1)',
        label: 'Risk Zone'
      });
      
      // 🟢 Зона тейк-профіта (вище входу)
      zones.push({
        y1: trade.entry_price,
        y2: trade.take_profit * 1.01,
        fill: 'rgba(16, 185, 129, 0.1)',
        label: 'Reward Zone'
      });
    } else {
      // Для SHORT:
      // 🔴 Зона стоп-лосу (вище входу)
      zones.push({
        y1: trade.entry_price,
        y2: trade.stop_loss * 1.01,
        fill: 'rgba(239, 68, 68, 0.1)',
        label: 'Risk Zone'
      });
      
      // 🟢 Зона тейк-профіта (нижче входу)
      zones.push({
        y1: trade.take_profit * 0.99,
        y2: trade.entry_price,
        fill: 'rgba(16, 185, 129, 0.1)',
        label: 'Reward Zone'
      });
    }
    
    return zones;
  }, [trade, isLong]);

  // Custom Tooltip з детальною інформацією
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const isEntryPoint = entryPoint && Math.abs(new Date(label).getTime() - new Date(entryPoint.time).getTime()) < 3600000;
      
      return (
        <div className="bg-gray-900 border border-gray-700 p-4 rounded-lg shadow-xl min-w-64">
          {isEntryPoint && (
            <div className="mb-2 p-2 bg-blue-900/30 rounded border border-blue-800">
              <p className="text-blue-300 font-bold flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                ТОЧКА ВХОДУ В УГОДУ
              </p>
              <p className="text-sm text-blue-400 mt-1">
                Час: {entryTime.toLocaleString('uk-UA')}
              </p>
            </div>
          )}
          
          <p className="text-gray-300 font-medium mb-2">
            {new Date(label).toLocaleString('uk-UA')}
          </p>
          
          <div className="space-y-1">
            {payload.map((pld: any, index: number) => (
              <p key={index} className="text-sm" style={{ color: pld.color }}>
                {pld.name}: <span className="font-mono">${pld.value.toFixed(4)}</span>
              </p>
            ))}
          </div>
          
          {/* Додаємо інформацію про дистанцію */}
          {trade.take_profit && trade.stop_loss && (
            <div className="mt-3 pt-3 border-t border-gray-700">
              <p className="text-xs text-gray-400 mb-1">Дистанція до цілей:</p>
              <div className="flex justify-between text-xs">
                <span className="text-red-400">
                  🔴 До SL: {distanceToSL.toFixed(2)}%
                </span>
                <span className="text-green-400">
                  🟢 До TP: {distanceToTP.toFixed(2)}%
                </span>
              </div>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  useEffect(() => {
    // ... код завантаження даних залишається незмінним ...
  }, [trade?.id, timeframe]);

  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
      {/* Заголовок з прогресс-барами */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-xl font-bold">
            📊 {trade.symbol} • {isLong ? '📈 LONG' : '📉 SHORT'}
          </h3>
          <div className="text-sm text-gray-400">
            Вхід: {entryTime.toLocaleDateString('uk-UA')} {entryTime.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
        
        {/* Прогрес-бари дистанції */}
        {trade.take_profit && trade.stop_loss && (
          <div className="space-y-2">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-green-400">Take Profit</span>
                <span className="text-gray-400">{distanceToTP.toFixed(2)}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 rounded-full"
                  style={{ 
                    width: `${Math.min(distanceToTP / 10, 100)}%`,
                    opacity: 0.7 
                  }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>Поточна ціна</span>
                <span className={`font-bold ${trade.pnl_percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {trade.pnl_percentage >= 0 ? '+' : ''}{trade.pnl_percentage.toFixed(2)}%
                </span>
              </div>
              <div className="h-3 bg-gray-700 rounded-full overflow-hidden relative">
                {/* Вся шкала від SL до TP */}
                <div className="absolute inset-0 flex">
                  <div 
                    className={`h-full ${isLong ? 'bg-red-500/20' : 'bg-green-500/20'}`}
                    style={{ width: '50%' }}
                  ></div>
                  <div 
                    className={`h-full ${isLong ? 'bg-green-500/20' : 'bg-red-500/20'}`}
                    style={{ width: '50%' }}
                  ></div>
                </div>
                
                {/* Маркер поточної позиції */}
                <div 
                  className="absolute top-0 h-3 w-1 bg-yellow-400"
                  style={{ 
                    left: isLong 
                      ? `${50 + (trade.current_price - trade.entry_price) / (trade.take_profit - trade.entry_price) * 50}%`
                      : `${50 - (trade.entry_price - trade.current_price) / (trade.entry_price - trade.take_profit) * 50}%`,
                    transform: 'translateX(-50%)'
                  }}
                ></div>
                
                {/* Маркер входу */}
                <div 
                  className="absolute top-0 h-3 w-2 bg-blue-500 rounded"
                  style={{ 
                    left: '50%',
                    transform: 'translateX(-50%)'
                  }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-red-400">Stop Loss</span>
                <span className="text-gray-400">{distanceToSL.toFixed(2)}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-red-500 rounded-full"
                  style={{ 
                    width: `${Math.min(distanceToSL / 10, 100)}%`,
                    opacity: 0.7 
                  }}
                ></div>
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
            <p className="text-gray-400">Завантаження графіка...</p>
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
              >
                {/* Додаємо маркер часу входу на осі X */}
                {entryTimeLine && (
                  <Label
                    value="⏰ ВХІД"
                    position="insideBottom"
                    offset={-10}
                    fill="#3B82F6"
                    fontSize={10}
                  />
                )}
              </XAxis>
              
              <YAxis 
                stroke="#9CA3AF"
                fontSize={11}
                domain={['auto', 'auto']}
                tickFormatter={(value) => `$${value.toFixed(2)}`}
              />
              
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {/* Кольорові зони ризику/прибутку */}
              {riskRewardZones?.map((zone, index) => (
                <ReferenceArea
                  key={index}
                  y1={zone.y1}
                  y2={zone.y2}
                  fill={zone.fill}
                  stroke="none"
                />
              ))}
              
              {/* Вертикальна лінія часу входу */}
              {entryTimeLine && (
                <ReferenceLine
                  x={entryTimeLine.toISOString()}
                  stroke="#3B82F6"
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  label={{
                    value: 'Час входу',
                    position: 'insideTop',
                    fill: '#3B82F6',
                    fontSize: 10
                  }}
                />
              )}
              
              {/* Горизонтальні лінії TP/SL */}
              {trade.take_profit && (
                <ReferenceLine
                  y={trade.take_profit}
                  stroke="#10B981"
                  strokeWidth={2}
                  strokeDasharray="3 3"
                  label={{
                    value: `TAKE PROFIT $${trade.take_profit.toFixed(4)}`,
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
                  strokeDasharray="3 3"
                  label={{
                    value: `STOP LOSS $${trade.stop_loss.toFixed(4)}`,
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
                label={{
                  value: `ENTRY $${trade.entry_price.toFixed(4)}`,
                  position: 'right',
                  fill: '#3B82F6',
                  fontSize: 12,
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
      
      {/* Легенда та інфо */}
      <div className="mt-4 pt-3 border-t border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
              <div>
                <div className="text-sm font-medium">Точка входу</div>
                <div className="text-xs text-gray-400">
                  ${trade.entry_price.toFixed(4)} • {entryTime.toLocaleTimeString('uk-UA')}
                </div>
              </div>
            </div>
            
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>
              <div>
                <div className="text-sm font-medium">Поточна ціна</div>
                <div className="text-xs text-gray-400">
                  ${trade.current_price.toFixed(4)} • {trade.pnl_percentage >= 0 ? '+' : ''}{trade.pnl_percentage.toFixed(2)}%
                </div>
              </div>
            </div>
          </div>
          
          {trade.take_profit && (
            <div className="space-y-2">
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                <div>
                  <div className="text-sm font-medium">Take Profit</div>
                  <div className="text-xs text-gray-400">
                    ${trade.take_profit.toFixed(4)} • {distanceToTP.toFixed(2)}% до цілі
                  </div>
                </div>
              </div>
              
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min((distanceToTP / 10) * 100, 100)}%` }}
                ></div>
              </div>
            </div>
          )}
          
          {trade.stop_loss && (
            <div className="space-y-2">
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
                <div>
                  <div className="text-sm font-medium">Stop Loss</div>
                  <div className="text-xs text-gray-400">
                    ${trade.stop_loss.toFixed(4)} • {distanceToSL.toFixed(2)}% до цілі
                  </div>
                </div>
              </div>
              
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-red-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min((distanceToSL / 10) * 100, 100)}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TradeChart;