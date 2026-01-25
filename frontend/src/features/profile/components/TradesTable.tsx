// frontend/src/features/profile/components/TradesTable.tsx
import React, { useState } from 'react';
import { Filter, Search, ChevronDown, ChevronUp } from 'lucide-react';

interface TradesTableProps {
  trades: any[];
}

const TradesTable: React.FC<TradesTableProps> = ({ trades }) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'closed'>('all');
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'pnl' | 'date' | 'symbol'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const filteredTrades = trades
    .filter(trade => {
      if (filter === 'active') return trade.status === 'active';
      if (filter === 'closed') return trade.status !== 'active';
      return true;
    })
    .filter(trade => 
      trade.symbol.toLowerCase().includes(search.toLowerCase()) ||
      trade.direction.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'pnl') {
        return sortOrder === 'desc' ? b.pnl_percentage - a.pnl_percentage : a.pnl_percentage - b.pnl_percentage;
      }
      if (sortBy === 'symbol') {
        return sortOrder === 'desc' ? b.symbol.localeCompare(a.symbol) : a.symbol.localeCompare(b.symbol);
      }
      // За замовчуванням сортуємо по даті
      return sortOrder === 'desc' ? 1 : -1;
    });

  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'active':
        return { text: '🟢 Активна', color: 'text-green-400', bg: 'bg-green-900/20' };
      case 'tp_hit':
        return { text: '🎯 TP досягнуто', color: 'text-green-400', bg: 'bg-green-900/20' };
      case 'sl_hit':
        return { text: '🛑 SL досягнуто', color: 'text-red-400', bg: 'bg-red-900/20' };
      case 'closed':
        return { text: '⚫ Закрита', color: 'text-gray-400', bg: 'bg-gray-900/20' };
      default:
        return { text: status, color: 'text-gray-400', bg: 'bg-gray-900/20' };
    }
  };

  const toggleSort = (column: 'pnl' | 'date' | 'symbol') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const SortIcon = ({ column }: { column: 'pnl' | 'date' | 'symbol' }) => {
    if (sortBy !== column) return <ChevronDown className="w-4 h-4 opacity-50" />;
    return sortOrder === 'desc' ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />;
  };

  return (
    <div>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div>
          <h3 className="text-xl font-bold flex items-center">
            <span className="mr-2">📋</span> Історія угод
          </h3>
          <p className="text-gray-400">Всі ваші віртуальні операції</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          {/* Пошук */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Пошук по символу..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg w-full md:w-64 focus:outline-none focus:border-blue-500"
            />
          </div>
          
          {/* Фільтри */}
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === 'all' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              Всі
            </button>
            <button
              onClick={() => setFilter('active')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === 'active' 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              Активні
            </button>
            <button
              onClick={() => setFilter('closed')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === 'closed' 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              Завершені
            </button>
          </div>
        </div>
      </div>

      {/* Таблиця */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-3 px-4 font-medium text-gray-400">
                <button 
                  onClick={() => toggleSort('symbol')}
                  className="flex items-center hover:text-white transition-colors"
                >
                  Символ
                  <SortIcon column="symbol" />
                </button>
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-400">Напрямок</th>
              <th className="text-left py-3 px-4 font-medium text-gray-400">Вхід</th>
              <th className="text-left py-3 px-4 font-medium text-gray-400">Поточна</th>
              <th className="text-left py-3 px-4 font-medium text-gray-400">
                <button 
                  onClick={() => toggleSort('pnl')}
                  className="flex items-center hover:text-white transition-colors"
                >
                  PnL%
                  <SortIcon column="pnl" />
                </button>
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-400">Статус</th>
              <th className="text-left py-3 px-4 font-medium text-gray-400">Час</th>
            </tr>
          </thead>
          <tbody>
            {filteredTrades.length > 0 ? (
              filteredTrades.map((trade, index) => {
                const pnl = trade.pnl_percentage || 0;
                const pnlColor = pnl >= 0 ? 'text-green-400' : 'text-red-400';
                const directionColor = trade.direction === 'long' ? 'text-green-400' : 'text-red-400';
                const directionText = trade.direction === 'long' ? 'LONG' : 'SHORT';
                const statusInfo = getStatusInfo(trade.status);

                return (
                  <tr 
                    key={trade.id || index}
                    className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors group"
                  >
                    <td className="py-4 px-4 font-medium">
                      <div className="font-bold">{trade.symbol}</div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`font-bold ${directionColor}`}>
                        {trade.direction === 'long' ? '📈' : '📉'} {directionText}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="font-medium">${trade.entry_price?.toFixed(2) || '0.00'}</div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="font-medium">${trade.current_price?.toFixed(2) || trade.entry_price?.toFixed(2) || '0.00'}</div>
                    </td>
                    <td className={`py-4 px-4 font-bold ${pnlColor}`}>
                      <div className="flex items-center">
                        {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}%
                        {Math.abs(pnl) > 5 && (
                          <span className="ml-2 text-xs px-2 py-1 rounded-full bg-opacity-20 bg-current">
                            {pnl > 0 ? '🔥' : '💧'}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusInfo.bg} ${statusInfo.color}`}>
                        {statusInfo.text}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-gray-400 text-sm">
                      {trade.created_at ? new Date(trade.created_at).toLocaleDateString('uk-UA') : 'Недавно'}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={7} className="py-12 text-center">
                  <div className="text-gray-500">
                    <div className="text-4xl mb-3">📭</div>
                    <div className="text-lg font-medium mb-2">Угод не знайдено</div>
                    <p className="text-gray-400">Спробуйте змінити фільтри або створіть першу угоду</p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Статистика таблиці */}
      {filteredTrades.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-sm text-gray-400">
              Показано <span className="text-white font-medium">{filteredTrades.length}</span> з <span className="text-white font-medium">{trades.length}</span> угод
            </div>
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center text-sm">
                <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                Активні: {trades.filter(t => t.status === 'active').length}
              </div>
              <div className="flex items-center text-sm">
                <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                Успішні: {trades.filter(t => t.pnl_percentage > 0).length}
              </div>
              <div className="flex items-center text-sm">
                <div className="w-3 h-3 rounded-full bg-gray-500 mr-2"></div>
                Завершені: {trades.filter(t => t.status !== 'active').length}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TradesTable;