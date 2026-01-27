// frontend/src/components/futures/TradeDetailsModal.tsx
import React from 'react';
import TradeChart from './TradeChart';

interface TradeDetailsModalProps {
  trade: any;
  isOpen: boolean;
  onClose: () => void;
}

const TradeDetailsModal: React.FC<TradeDetailsModalProps> = ({ 
  trade, 
  isOpen, 
  onClose 
}) => {
  if (!isOpen) return null;
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400';
      case 'tp_hit': return 'text-blue-400';
      case 'sl_hit': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };
  
  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '🟢 Активна';
      case 'tp_hit': return '🎯 TP досягнуто';
      case 'sl_hit': return '🛑 SL досягнуто';
      case 'closed': return '⚫ Закрита';
      default: return status;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Заголовок */}
        <div className="flex justify-between items-center p-6 border-b border-gray-700">
          <div>
            <h2 className="text-2xl font-bold">
              📊 Детальний аналіз угоди: {trade.symbol}
            </h2>
            <p className="text-gray-400">
              Статус: <span className={getStatusColor(trade.status)}>
                {getStatusText(trade.status)}
              </span>
              <span className="mx-2">•</span>
              Відкрита: {new Date(trade.created_at).toLocaleDateString('uk-UA')}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl p-2"
          >
            ✕
          </button>
        </div>
        
        {/* Контент */}
        <div className="p-6">
          {/* Графік */}
          <TradeChart trade={trade} />
          
          {/* Детальна статистика */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-gray-400 text-sm mb-1">Напрямок</div>
              <div className={`text-xl font-bold ${
                trade.direction === 'long' ? 'text-green-400' : 'text-red-400'
              }`}>
                {trade.direction === 'long' ? '📈 LONG' : '📉 SHORT'}
              </div>
            </div>
            
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-gray-400 text-sm mb-1">Поточний PnL</div>
              <div className={`text-xl font-bold ${
                trade.pnl_percentage >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {trade.pnl_percentage >= 0 ? '+' : ''}{trade.pnl_percentage.toFixed(2)}%
                <div className="text-sm text-gray-400">
                  ${((trade.pnl_percentage / 100) * 100).toFixed(2)} при $100
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-gray-400 text-sm mb-1">Ризик/Прибуток</div>
              <div className="text-xl font-bold">
                {trade.take_profit && trade.stop_loss 
                  ? `1:${Math.abs(
                      (trade.take_profit - trade.entry_price) / 
                      (trade.stop_loss - trade.entry_price)
                    ).toFixed(2)}`
                  : 'N/A'}
              </div>
            </div>
            
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-gray-400 text-sm mb-1">Час у позиції</div>
              <div className="text-xl font-bold">
                {(() => {
                  const start = new Date(trade.created_at);
                  const now = new Date();
                  const diffMs = now.getTime() - start.getTime();
                  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
                  const diffDays = Math.floor(diffHours / 24);
                  
                  if (diffDays > 0) {
                    return `${diffDays}д ${diffHours % 24}г`;
                  } else {
                    return `${diffHours} годин`;
                  }
                })()}
              </div>
            </div>
          </div>
          
          {/* Додаткова інформація */}
          <div className="mt-6 bg-gray-800/50 p-4 rounded-lg">
            <h4 className="font-medium mb-3">📋 Деталі угоди:</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div>
                <div className="text-gray-400">ID угоди:</div>
                <div className="font-mono">{trade.id}</div>
              </div>
              <div>
                <div className="text-gray-400">Вхідна ціна:</div>
                <div>${trade.entry_price.toFixed(4)}</div>
              </div>
              <div>
                <div className="text-gray-400">Поточна ціна:</div>
                <div>${trade.current_price.toFixed(4)}</div>
              </div>
              <div>
                <div className="text-gray-400">Відстань до TP:</div>
                <div className={trade.pnl_percentage >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {trade.take_profit 
                    ? `${Math.abs(((trade.current_price - trade.take_profit) / trade.entry_price) * 100).toFixed(2)}%`
                    : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeDetailsModal;