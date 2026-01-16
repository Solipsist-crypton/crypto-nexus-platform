import React, { useState, useEffect } from 'react';

interface ArbitrageOpportunity {
  id: number;
  base_currency: string;
  target_currency: string;
  exchange_from: string;
  exchange_to: string;
  price_from: number;
  price_to: number;
  price_difference: number;
  volume_24h: number;
  trust_score: number;
  potential_profit: number;
  is_opportunity: boolean;
  created_at: string;
}

const ArbitragePage = () => {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const fetchOpportunities = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/arbitrage/opportunities');
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      setOpportunities(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      console.error('Помилка завантаження даних:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatVolume = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    }
    return `$${formatCurrency(value)}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl">Завантаження арбітражних можливостей...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <strong>Помилка:</strong> {error}
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">🔄 Арбітражний моніторинг</h1>
      <p className="text-gray-600 mb-6">Моніторинг цінових різниць між біржами в реальному часі</p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold text-gray-700">Активних можливостей</h3>
          <p className="text-2xl font-bold text-blue-600">{opportunities.length}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold text-gray-700">Середній прибуток</h3>
          <p className="text-2xl font-bold text-green-600">
            {opportunities.length > 0 
              ? `${(opportunities.reduce((sum, o) => sum + o.potential_profit, 0) / opportunities.length).toFixed(2)}%`
              : '0%'}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold text-gray-700">Найвища різниця</h3>
          <p className="text-2xl font-bold text-purple-600">
            {opportunities.length > 0 
              ? `${Math.max(...opportunities.map(o => o.price_difference)).toFixed(2)}%`
              : '0%'}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Пара</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Біржа (купити)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Біржа (продати)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ціна купівлі</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ціна продажу</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Різниця</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Обсяг (24h)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trust Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Прибуток</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {opportunities.map((opp) => (
                <tr key={opp.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-bold">{opp.base_currency}</span>
                    <span className="text-gray-500">/{opp.target_currency}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                      {opp.exchange_from}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-800">
                      {opp.exchange_to}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    ${formatCurrency(opp.price_from)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    ${formatCurrency(opp.price_to)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`font-bold ${opp.price_difference > 1 ? 'text-green-600' : 'text-yellow-600'}`}>
                      {opp.price_difference.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {formatVolume(opp.volume_24h)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded ${
                      opp.trust_score > 0.8 ? 'bg-green-100 text-green-800' :
                      opp.trust_score > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {(opp.trust_score * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`font-bold ${
                      opp.potential_profit > 1.5 ? 'text-green-600' :
                      opp.potential_profit > 0.5 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {opp.potential_profit.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {opp.is_opportunity ? (
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-800">
                        Активна
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-gray-100 text-gray-800">
                        Неактивна
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        <p>Оновлено: {new Date().toLocaleTimeString()}</p>
        <p>Всього записів: {opportunities.length}</p>
      </div>
    </div>
  );
};

export default ArbitragePage;