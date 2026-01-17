import React, { useState } from 'react';

interface Opportunity {
  coin: string;
  prices: Record<string, number>;
  best_opportunity: any;
}

interface PriceComparisonTableProps {
  opportunities: Opportunity[];
}

const PriceComparisonTable: React.FC<PriceComparisonTableProps> = ({ opportunities }) => {
  const [selectedCoin, setSelectedCoin] = useState<string>('BTC');
  
  const exchanges = ['Binance', 'Kraken', 'Bybit', 'OKX'];
  const coins = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX'];

  const getPriceForCoin = (coin: string, exchange: string): number | null => {
    const opportunity = opportunities.find(op => op.coin === coin);
    return opportunity?.prices?.[exchange] || null;
  };

  const formatPrice = (price: number | null): string => {
    if (price === null) return '-';
    if (price >= 1000) return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
    if (price >= 1) return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
    return `$${price.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 8 })}`;
  };

  return (
    <div>
      {/* Фільтр монет */}
      <div className="flex space-x-2 mb-4">
        {coins.map(coin => (
          <button
            key={coin}
            onClick={() => setSelectedCoin(coin)}
            className={`px-4 py-2 rounded-lg font-medium ${
              selectedCoin === coin 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {coin}
          </button>
        ))}
      </div>

      {/* Таблиця цін */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Біржа
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ціна
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Різниця від Binance
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {exchanges.map((exchange, index) => {
              const price = getPriceForCoin(selectedCoin, exchange);
              const binancePrice = getPriceForCoin(selectedCoin, 'Binance');
              const difference = price && binancePrice ? ((price - binancePrice) / binancePrice * 100) : null;
              
              return (
                <tr key={exchange} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        index === 0 ? 'bg-yellow-400' :
                        index === 1 ? 'bg-purple-400' :
                        index === 2 ? 'bg-blue-400' :
                        'bg-green-400'
                      }`}></div>
                      <span className="font-medium text-gray-900">{exchange}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-lg font-semibold text-gray-900">
                      {formatPrice(price)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      price !== null 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {price !== null ? '🟢 Активна' : '🔴 Неактивна'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {difference !== null ? (
                      <span className={`font-medium ${
                        difference > 0 ? 'text-green-600' : 
                        difference < 0 ? 'text-red-600' : 
                        'text-gray-600'
                      }`}>
                        {difference > 0 ? '+' : ''}{difference.toFixed(2)}%
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Міні-статистика */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-sm text-blue-600">Активних бірж</p>
          <p className="text-2xl font-bold text-blue-700">
            {exchanges.filter(exchange => 
              getPriceForCoin(selectedCoin, exchange) !== null
            ).length}
          </p>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-sm text-green-600">Найвища ціна</p>
          <p className="text-xl font-bold text-green-700">
            {formatPrice(
              Math.max(...exchanges
                .map(exchange => getPriceForCoin(selectedCoin, exchange) || 0)
                .filter(price => price > 0)
              )
            )}
          </p>
        </div>
        <div className="bg-red-50 rounded-lg p-4">
          <p className="text-sm text-red-600">Найнижча ціна</p>
          <p className="text-xl font-bold text-red-700">
            {formatPrice(
              Math.min(...exchanges
                .map(exchange => getPriceForCoin(selectedCoin, exchange) || Infinity)
                .filter(price => price < Infinity)
              )
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PriceComparisonTable;