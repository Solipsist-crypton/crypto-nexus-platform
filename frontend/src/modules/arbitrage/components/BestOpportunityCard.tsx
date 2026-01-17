import React from 'react';

interface BestOpportunityProps {
  opportunity: any;
}

const BestOpportunityCard: React.FC<BestOpportunityProps> = ({ opportunity }) => {
  if (!opportunity) {
    return (
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-yellow-400">⚠️</span>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              На даний момент не знайдено арбітражних можливостей з різницею вище 0.1%
            </p>
          </div>
        </div>
      </div>
    );
  }

  const profitPercent = opportunity.net_profit_percent || opportunity.price_difference_percent;
  const isHighProfit = profitPercent > 0.5;
  const isMediumProfit = profitPercent > 0.2;

  return (
    <div className={`rounded-lg shadow-lg overflow-hidden ${
      isHighProfit ? 'bg-gradient-to-r from-green-50 to-emerald-50' :
      isMediumProfit ? 'bg-gradient-to-r from-blue-50 to-cyan-50' :
      'bg-gradient-to-r from-gray-50 to-slate-50'
    }`}>
      <div className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              🎯 Найкраща можливість
            </h2>
            <p className="text-gray-600 mt-1">
              Знайдено щойно
            </p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
            isHighProfit ? 'bg-green-100 text-green-800' :
            isMediumProfit ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {profitPercent.toFixed(2)}% прибуток
          </span>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Монета */}
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <p className="text-sm text-gray-500">Монета</p>
            <div className="flex items-center mt-2">
              <span className="text-2xl font-bold text-gray-900">{opportunity.coin}</span>
              <span className="ml-2 text-sm text-gray-500">({opportunity.coin})</span>
            </div>
          </div>

          {/* Купівля */}
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <p className="text-sm text-gray-500">Купівля на</p>
            <div className="flex items-center mt-2">
              <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
                <span className="text-red-600">↓</span>
              </div>
              <div className="ml-3">
                <p className="font-semibold text-gray-900">{opportunity.buy_exchange}</p>
                <p className="text-lg font-bold text-red-600">
                  ${opportunity.buy_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 })}
                </p>
              </div>
            </div>
          </div>

          {/* Продаж */}
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <p className="text-sm text-gray-500">Продаж на</p>
            <div className="flex items-center mt-2">
              <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                <span className="text-green-600">↑</span>
              </div>
              <div className="ml-3">
                <p className="font-semibold text-gray-900">{opportunity.sell_exchange}</p>
                <p className="text-lg font-bold text-green-600">
                  ${opportunity.sell_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 })}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Деталі */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">Різниця в ціні</p>
              <p className="text-lg font-semibold text-gray-900">
                ${opportunity.price_difference?.toFixed(8)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Прибуток на 1 {opportunity.coin}</p>
              <p className="text-lg font-semibold text-green-600">
                ${opportunity.price_difference?.toFixed(8)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Відсоток прибутку</p>
              <p className="text-lg font-semibold text-green-600">
                {profitPercent.toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Час оновлення</p>
              <p className="text-sm text-gray-900">
                {new Date(opportunity.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BestOpportunityCard;