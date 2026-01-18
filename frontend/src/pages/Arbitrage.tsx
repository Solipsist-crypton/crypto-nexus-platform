
import React, { useState, useEffect, useMemo } from 'react';
import { RefreshCw, TrendingUp, DollarSign, BarChart3, Zap, Filter, ArrowUpDown, ChevronUp, ChevronDown } from 'lucide-react';
import { arbitrageApi, ArbitrageOpportunity } from '../api/arbitrage';
import Loader from '../modules/arbitrage/components/common/Loader';

// Типи для сортування
type SortField = 'coin' | 'buyExchange' | 'sellExchange' | 'buyPrice' | 'sellPrice' | 'profit' | 'profitPercentage';
type SortDirection = 'asc' | 'desc';

const Arbitrage: React.FC = () => {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Стани для фільтрів та сортування
  const [selectedCoin, setSelectedCoin] = useState<string>('ALL');
  const [minProfitFilter, setMinProfitFilter] = useState<number>(0);
  const [sortField, setSortField] = useState<SortField>('profitPercentage');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await arbitrageApi.getOpportunities();
      setOpportunities(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Fetch failed:', error);
      setOpportunities([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 60000);
    return () => clearInterval(intervalId);
  }, []);

  // Функція для обробки сортування
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Якщо вже сортуємо по цьому полю, змінюємо напрямок
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // Якщо нове поле, сортуємо за ним за зменшенням (за замовчуванням)
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Фільтрація та сортування даних
  const filteredAndSortedOpportunities = useMemo(() => {
    let filtered = opportunities;

    // Фільтрація по монеті
    if (selectedCoin !== 'ALL') {
      filtered = filtered.filter(opp => opp.coin.includes(selectedCoin));
    }

    // Фільтрація по мінімальному прибутку
    if (minProfitFilter > 0) {
      filtered = filtered.filter(opp => opp.profitPercentage >= minProfitFilter);
    }

    // Сортування
    filtered.sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];

      // Для строкових значень
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      // Для числових значень
      if (sortDirection === 'asc') {
        return (aValue as number) - (bValue as number);
      } else {
        return (bValue as number) - (aValue as number);
      }
    });

    return filtered;
  }, [opportunities, selectedCoin, minProfitFilter, sortField, sortDirection]);

  // Розрахунок статистики на основі відфільтрованих даних
  const totalProfit = filteredAndSortedOpportunities.reduce((sum, opp) => sum + opp.profit, 0);
  const avgProfit = filteredAndSortedOpportunities.length > 0 
    ? totalProfit / filteredAndSortedOpportunities.length 
    : 0;
  const avgProfitPercentage = filteredAndSortedOpportunities.length > 0
    ? filteredAndSortedOpportunities.reduce((sum, opp) => sum + opp.profitPercentage, 0) / filteredAndSortedOpportunities.length
    : 0;
  const bestOpportunity = filteredAndSortedOpportunities.length > 0 
    ? filteredAndSortedOpportunities.reduce((best, opp) => opp.profitPercentage > best.profitPercentage ? opp : best)
    : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-4 md:p-6">
      {/* Заголовок та керування */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
              📊 Arbitrage Monitor
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Real-time cryptocurrency arbitrage opportunities across exchanges
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={fetchData}
              disabled={loading}
              className="px-4 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Updating...' : 'Refresh'}
            </button>
            
            <div className="text-sm text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 px-3 py-1.5 rounded-lg border dark:border-gray-700">
              Updated: {lastUpdate.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>

      {/* Статус API */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 rounded-xl border border-blue-200 dark:border-blue-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${opportunities.length > 0 ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`}></div>
            <div>
              <span className="font-medium">API Status:</span>
              <span className="ml-2">
                {opportunities.length > 0 
                  ? `Connected (${opportunities.length} opportunities found)` 
                  : 'Connected (scanning markets...)'}
              </span>
            </div>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Auto-refresh every 60s
          </div>
        </div>
      </div>

      {/* Статистичні картки */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-lg border dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm text-gray-500 dark:text-gray-400">Active Opportunities</div>
            <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
              <Zap className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">{filteredAndSortedOpportunities.length}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">filtered from {opportunities.length}</div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-lg border dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm text-gray-500 dark:text-gray-400">Total Profit</div>
            <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">${totalProfit.toFixed(2)}</div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-lg border dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm text-gray-500 dark:text-gray-400">Avg. Profit %</div>
            <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{avgProfitPercentage.toFixed(2)}%</div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-lg border dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm text-gray-500 dark:text-gray-400">Best Spread</div>
            <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-amber-600 dark:text-amber-400" />
            </div>
          </div>
          <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">
            {bestOpportunity ? `${bestOpportunity.profitPercentage.toFixed(2)}%` : '0.00%'}
          </div>
        </div>
      </div>

      {/* Панель фільтрів */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-lg border dark:border-gray-700 mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Filter className="w-5 h-5 text-gray-500" />
            <h3 className="font-medium text-gray-900 dark:text-white">Filters</h3>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <div>
              <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">Filter by Coin</label>
              <select 
                value={selectedCoin}
                onChange={(e) => setSelectedCoin(e.target.value)}
                className="w-full md:w-40 p-2.5 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg text-sm"
              >
                <option value="ALL">All Coins</option>
                <option value="BTC">Bitcoin (BTC)</option>
                <option value="ETH">Ethereum (ETH)</option>
                <option value="SOL">Solana (SOL)</option>
                <option value="DOT">Polkadot (DOT)</option>
                <option value="AVAX">Avalanche (AVAX)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">Min. Profit %</label>
              <div className="flex items-center gap-2">
                <input 
                  type="range" 
                  min="0" 
                  max="2" 
                  step="0.1"
                  value={minProfitFilter}
                  onChange={(e) => setMinProfitFilter(parseFloat(e.target.value))}
                  className="w-32"
                />
                <span className="text-sm font-medium w-12">{minProfitFilter.toFixed(1)}%</span>
              </div>
            </div>
            
            <div className="flex items-end">
              <button 
                onClick={() => {
                  setSelectedCoin('ALL');
                  setMinProfitFilter(0);
                }}
                className="px-4 py-2.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Основна таблиця арбітражів */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border dark:border-gray-700 overflow-hidden">
        <div className="p-5 border-b dark:border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Arbitrage Opportunities
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Click on column headers to sort. Showing {filteredAndSortedOpportunities.length} of {opportunities.length} opportunities.
              </p>
            </div>
            
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Sorted by: <span className="font-medium">{sortField}</span> ({sortDirection})
            </div>
          </div>
        </div>
        
        {loading ? (
          <div className="py-12">
            <Loader />
          </div>
        ) : filteredAndSortedOpportunities.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th 
                    className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                    onClick={() => handleSort('coin')}
                  >
                    <div className="flex items-center gap-1">
                      Coin
                      <ArrowUpDown className="w-4 h-4" />
                      {sortField === 'coin' && (
                        sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                    onClick={() => handleSort('buyExchange')}
                  >
                    <div className="flex items-center gap-1">
                      Buy Exchange
                      <ArrowUpDown className="w-4 h-4" />
                      {sortField === 'buyExchange' && (
                        sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                    onClick={() => handleSort('sellExchange')}
                  >
                    <div className="flex items-center gap-1">
                      Sell Exchange
                      <ArrowUpDown className="w-4 h-4" />
                      {sortField === 'sellExchange' && (
                        sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                    onClick={() => handleSort('buyPrice')}
                  >
                    <div className="flex items-center gap-1">
                      Buy Price
                      <ArrowUpDown className="w-4 h-4" />
                      {sortField === 'buyPrice' && (
                        sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                    onClick={() => handleSort('sellPrice')}
                  >
                    <div className="flex items-center gap-1">
                      Sell Price
                      <ArrowUpDown className="w-4 h-4" />
                      {sortField === 'sellPrice' && (
                        sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                    onClick={() => handleSort('profitPercentage')}
                  >
                    <div className="flex items-center gap-1">
                      Profit %
                      <ArrowUpDown className="w-4 h-4" />
                      {sortField === 'profitPercentage' && (
                        sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                    onClick={() => handleSort('profit')}
                  >
                    <div className="flex items-center gap-1">
                      Profit
                      <ArrowUpDown className="w-4 h-4" />
                      {sortField === 'profit' && (
                        sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredAndSortedOpportunities.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                          {item.coin.substring(0, 3)}
                        </div>
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">{item.coin}</div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="font-medium">{item.buyExchange}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span className="font-medium">{item.sellExchange}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="font-mono">${item.buyPrice.toFixed(4)}</div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="font-mono">${item.sellPrice.toFixed(4)}</div>
                    </td>
                    <td className="py-4 px-4">
                      <div className={`px-3 py-1 rounded-full text-sm font-medium inline-flex items-center gap-1 ${
                        item.profitPercentage >= 0.5 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                          : item.profitPercentage >= 0.2
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                      }`}>
                        {item.profitPercentage > 0 ? '+' : ''}{item.profitPercentage.toFixed(2)}%
                        {item.profitPercentage >= 0.5 && <TrendingUp className="w-3 h-3" />}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="font-bold text-green-600 dark:text-green-400">
                        ${item.profit.toFixed(2)}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex gap-2">
                        <button className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg text-sm font-medium hover:opacity-90">
                          Execute
                        </button>
                        <button className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-700">
                          Details
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="text-gray-500 dark:text-gray-400 mb-4">
              {opportunities.length === 0 
                ? 'No arbitrage opportunities found in the market. Try again later.' 
                : 'No opportunities match your current filters. Try adjusting them.'
              }
            </div>
            {opportunities.length === 0 && (
              <button 
                onClick={fetchData}
                className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:opacity-90"
              >
                Scan Again
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Arbitrage;