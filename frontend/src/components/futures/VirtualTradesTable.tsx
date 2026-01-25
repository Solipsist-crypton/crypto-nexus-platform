// frontend/src/components/futures/VirtualTradesTable.tsx
import React from 'react';

interface Trade {
  id: number;
  symbol: string;
  direction: 'long' | 'short';
  entry_price: number;
  current_price: number;
  pnl_percentage: number;
  status: 'active' | 'tp_hit' | 'sl_hit' | 'closed';
  take_profit?: number;
  stop_loss?: number;
}

interface VirtualTradesTableProps {
  trades: Trade[];
}

const VirtualTradesTable: React.FC<VirtualTradesTableProps> = ({ trades }) => {
  // Якщо угод немає
  if (trades.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-5xl mb-4">📭</div>
        <h3 className="text-xl font-medium mb-2">Немає віртуальних угод</h3>
        <p className="text-gray-400">
          Почніть відстежувати AI сигнали, щоб створити свою першу угоду
        </p>
      </div>
    );
  }

  // Функція для відображення статусу
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'active':
        return { text: '🟢 Активна', color: 'text-green-400' };
      case 'tp_hit':
        return { text: '🎯 TP досягнуто', color: 'text-green-400' };
      case 'sl_hit':
        return { text: '🛑 SL досягнуто', color: 'text-red-400' };
      case 'closed':
        return { text: '⚫ Закрита', color: 'text-gray-400' };
      default:
        return { text: status, color: 'text-gray-400' };
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="text-left py-3 px-4 font-medium text-gray-400">Символ</th>
            <th className="text-left py-3 px-4 font-medium text-gray-400">Напрямок</th>
            <th className="text-left py-3 px-4 font-medium text-gray-400">Вхід</th>
            <th className="text-left py-3 px-4 font-medium text-gray-400">Поточна</th>
            <th className="text-left py-3 px-4 font-medium text-gray-400">TP</th>
            <th className="text-left py-3 px-4 font-medium text-gray-400">SL</th>
            <th className="text-left py-3 px-4 font-medium text-gray-400">PnL%</th>
            <th className="text-left py-3 px-4 font-medium text-gray-400">Статус</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => {
            const pnl = trade.pnl_percentage || 0;
            const pnlColor = pnl >= 0 ? 'text-green-400' : 'text-red-400';
            const directionColor = trade.direction === 'long' ? 'text-green-400' : 'text-red-400';
            const directionText = trade.direction === 'long' ? 'LONG' : 'SHORT';
            const statusInfo = getStatusInfo(trade.status);

            return (
              <tr 
                key={trade.id} 
                className="border-b border-gray-800 hover:bg-gray-750 transition-colors"
              >
                <td className="py-3 px-4 font-medium">{trade.symbol}</td>
                <td className="py-3 px-4">
                  <span className={`font-bold ${directionColor}`}>
                    {trade.direction === 'long' ? '📈' : '📉'} {directionText}
                  </span>
                </td>
                <td className="py-3 px-4">${trade.entry_price.toFixed(2)}</td>
                <td className="py-3 px-4">${trade.current_price.toFixed(2)}</td>
                <td className="py-3 px-4 text-green-300">
                  ${trade.take_profit?.toFixed(2) || '-'}
                </td>
                <td className="py-3 px-4 text-red-300">
                  ${trade.stop_loss?.toFixed(2) || '-'}
                </td>
                <td className={`py-3 px-4 font-bold ${pnlColor}`}>
                  {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}%
                </td>
                <td className={`py-3 px-4 ${statusInfo.color}`}>
                  {statusInfo.text}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      
      {/* Статистика по таблиці */}
      <div className="mt-6 pt-4 border-t border-gray-700 text-sm text-gray-400">
        <div className="flex justify-between items-center">
          <div>
            Показано <span className="text-white font-medium">{trades.length}</span> угод
          </div>
          <div className="flex gap-4">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
              Активні: {trades.filter(t => t.status === 'active').length}
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-gray-500 mr-2"></div>
              Завершені: {trades.filter(t => t.status !== 'active').length}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VirtualTradesTable;