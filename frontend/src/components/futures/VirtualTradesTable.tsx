// frontend/src/components/futures/VirtualTradesTable.tsx
import React, { useState } from 'react';

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
  created_at?: string; // Додаємо дату створення
}

interface VirtualTradesTableProps {
  trades: Trade[];
}

const VirtualTradesTable: React.FC<VirtualTradesTableProps> = ({ trades }) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'closed'>('all');

  // Функція для форматування часу
  const formatTime = (dateString?: string) => {
    if (!dateString) return '-';
    
    try {
      const date = new Date(dateString);
      
      // Якщо сьогодні - показуємо тільки час
      const today = new Date();
      if (date.toDateString() === today.toDateString()) {
        return date.toLocaleTimeString('uk-UA', { 
          hour: '2-digit', 
          minute: '2-digit' 
        });
      }
      
      // Якщо вчора - показуємо "вчора" + час
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      if (date.toDateString() === yesterday.toDateString()) {
        return `вчора ${date.toLocaleTimeString('uk-UA', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })}`;
      }
      
      // Інакше - дата + час
      return date.toLocaleDateString('uk-UA', { 
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).replace(',', '');
    } catch {
      return '-';
    }
  };

  // Функція для форматування повної дати (для тултіпа)
  const formatFullDate = (dateString?: string) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleString('uk-UA', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return '';
    }
  };

  // Фільтрація угод
  const filteredTrades = trades.filter(trade => {
    if (filter === 'active') return trade.status === 'active';
    if (filter === 'closed') return trade.status !== 'active';
    return true;
  });

  // Сортування за часом (найновіші зверху)
  const sortedTrades = [...filteredTrades].sort((a, b) => {
    const timeA = a.created_at ? new Date(a.created_at).getTime() : 0;
    const timeB = b.created_at ? new Date(b.created_at).getTime() : 0;
    return timeB - timeA; // Сортування за спаданням (новіші перші)
  });

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

  // Inline стилі для скролбара
  const scrollbarStyles = {
    maxHeight: '400px',
    scrollbarWidth: 'thin' as const,
    scrollbarColor: '#4B5563 #1F2937',
  };

  return (
    <div>
      {/* Заголовок та фільтри */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <h3 className="text-lg font-bold flex items-center">
          <span className="mr-2">📋</span> Мої Віртуальні Угоди
        </h3>
        
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Всі ({trades.length})
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === 'active' 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Активні ({trades.filter(t => t.status === 'active').length})
          </button>
          <button
            onClick={() => setFilter('closed')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === 'closed' 
                ? 'bg-gray-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Завершені ({trades.filter(t => t.status !== 'active').length})
          </button>
        </div>
      </div>

      {/* Таблиця з фіксованою висотою та скролом */}
      <div 
        className="overflow-y-auto rounded-lg border border-gray-700"
        style={scrollbarStyles}
      >
        {/* Додаємо стилі через глобальний тег style */}
        <style>{`
          .custom-scrollbar::-webkit-scrollbar {
            width: 6px;
          }
          .custom-scrollbar::-webkit-scrollbar-track {
            background: #1F2937;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #4B5563;
            border-radius: 3px;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: #6B7280;
          }
        `}</style>
        
        {/* Додаємо клас для WebKit браузерів */}
        <div className="custom-scrollbar">
          {sortedTrades.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">📄</div>
              <p className="text-gray-400">Немає угод за обраним фільтром</p>
            </div>
          ) : (
            <table className="w-full min-w-max">
              <thead className="sticky top-0 bg-gray-800 z-10">
                <tr className="border-b border-gray-700">
                  <th className="text-left py-3 px-4 font-medium text-gray-400 text-sm">Символ</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-400 text-sm">Напрямок</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-400 text-sm">Вхід</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-400 text-sm">Поточна</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-400 text-sm">TP</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-400 text-sm">SL</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-400 text-sm">PnL%</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-400 text-sm">Статус</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-400 text-sm">Час входу</th>
                </tr>
              </thead>
              <tbody>
                {sortedTrades.map((trade) => {
                  const pnl = trade.pnl_percentage || 0;
                  const pnlColor = pnl >= 0 ? 'text-green-400' : 'text-red-400';
                  const directionColor = trade.direction === 'long' ? 'text-green-400' : 'text-red-400';
                  const directionText = trade.direction === 'long' ? 'LONG' : 'SHORT';
                  const statusInfo = getStatusInfo(trade.status);
                  const formattedTime = formatTime(trade.created_at);
                  const fullDate = formatFullDate(trade.created_at);

                  return (
                    <tr 
                      key={trade.id} 
                      className="border-b border-gray-800 hover:bg-gray-750 transition-colors"
                    >
                      <td className="py-3 px-4 font-medium whitespace-nowrap">{trade.symbol}</td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className={`font-bold ${directionColor}`}>
                          {trade.direction === 'long' ? '📈' : '📉'} {directionText}
                        </span>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">${trade.entry_price.toFixed(4)}</td>
                      <td className="py-3 px-4 whitespace-nowrap">${trade.current_price.toFixed(4)}</td>
                      <td className="py-3 px-4 text-green-300 whitespace-nowrap">
                        ${trade.take_profit?.toFixed(4) || '-'}
                      </td>
                      <td className="py-3 px-4 text-red-300 whitespace-nowrap">
                        ${trade.stop_loss?.toFixed(4) || '-'}
                      </td>
                      <td className={`py-3 px-4 font-bold whitespace-nowrap ${pnlColor}`}>
                        {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}%
                      </td>
                      <td className={`py-3 px-4 whitespace-nowrap ${statusInfo.color}`}>
                        {statusInfo.text}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        {fullDate ? (
                          <span 
                            className="text-gray-400 text-sm cursor-help"
                            title={fullDate}
                          >
                            {formattedTime}
                          </span>
                        ) : (
                          <span className="text-gray-500 text-sm">-</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
      
      {/* Статистика під таблицею */}
      <div className="mt-4 pt-3 border-t border-gray-700">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div className="text-sm text-gray-400">
            Показано <span className="text-white font-medium">{sortedTrades.length}</span> з {trades.length} угод
            {filter !== 'all' && (
              <span className="ml-2 text-blue-400">
                (Фільтр: {filter === 'active' ? 'Активні' : 'Завершені'})
              </span>
            )}
          </div>
          
          <div className="flex flex-wrap gap-3">
            <div className="flex items-center text-sm">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
              Активні: <span className="font-medium ml-1 text-white">{trades.filter(t => t.status === 'active').length}</span>
            </div>
            <div className="flex items-center text-sm">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
              TP: <span className="font-medium ml-1 text-white">{trades.filter(t => t.status === 'tp_hit').length}</span>
            </div>
            <div className="flex items-center text-sm">
              <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
              SL: <span className="font-medium ml-1 text-white">{trades.filter(t => t.status === 'sl_hit').length}</span>
            </div>
            <div className="flex items-center text-sm">
              <div className="w-3 h-3 rounded-full bg-gray-500 mr-2"></div>
              Інші: <span className="font-medium ml-1 text-white">{trades.filter(t => t.status === 'closed').length}</span>
            </div>
          </div>
        </div>
        
        {/* Додаткова інформація про часовий формат */}
        <div className="mt-2 text-xs text-gray-500">
          <span className="inline-flex items-center">
            <span className="mr-1">ℹ️</span>
            Час показується у форматі: "сьогодні/вчора HH:MM" або "DD.MM HH:MM"
          </span>
        </div>
      </div>
    </div>
  );
};

export default VirtualTradesTable;