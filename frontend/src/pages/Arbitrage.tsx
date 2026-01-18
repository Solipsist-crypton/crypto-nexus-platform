import React, { useState, useEffect } from 'react';
import { RefreshCw, TrendingUp, DollarSign, BarChart3, Zap } from 'lucide-react';
import { arbitrageApi, ArbitrageOpportunity } from '../api/arbitrage';
import ArbitrageTable from '../modules/arbitrage/components/ArbitrageTable';
import ArbitrageCalculator from '../modules/arbitrage/components/Calculator';
import RealTimeChart from '../modules/arbitrage/components/RealTimeChart';
import Loader from '../modules/arbitrage/components/common/Loader';

const Arbitrage: React.FC = () => {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

const fetchData = async () => {
  console.log(`⏰ Fetch at: ${new Date().toLocaleTimeString()}`);
  setLoading(true);
  try {
    console.log('🔄 Starting fetch...');
    const data = await arbitrageApi.getOpportunities();
    
    // ДЕБАГ
    console.log('📊 Received data type:', typeof data);
    console.log('📊 Is array?:', Array.isArray(data));
    console.log('📊 Data length:', data?.length || 0);
    console.log('📊 First item:', data?.[0]);
    
    if (Array.isArray(data) && data.length > 0) {
      setOpportunities(data);
      console.log('✅ Data set successfully');
    } else {
      console.warn('⚠️ No data or empty array');
      setOpportunities([]);
    }
    
    setLastUpdate(new Date());
  } catch (error) {
    console.error('💥 Fetch failed:', error);
    setOpportunities([]);
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    console.log('✅ Component mounted, starting auto-refresh');
    fetchData();
    
    const intervalId = setInterval(fetchData, 10000);
    
    return () => {
      clearInterval(intervalId);
      console.log('🔄 Auto-refresh stopped');
    };
  }, []);

  // Розрахунок статистики
  const totalProfit = opportunities.reduce((sum, opp) => sum + opp.profit, 0);
  const avgProfit = opportunities.length > 0 ? totalProfit / opportunities.length : 0;
  const bestOpportunity = opportunities.length > 0 
    ? opportunities.reduce((best, opp) => opp.profitPercentage > best.profitPercentage ? opp : best)
    : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-4 md:p-6">
      {/* Заголовок та керування */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
              📊 Arbitrage Monitor
            </h1>
            <p className="text-gray-600">
              Real-time cryptocurrency arbitrage opportunities across exchanges
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={fetchData}
              disabled={loading}
              className="btn-primary flex items-center gap-2 px-4 py-2.5"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Updating...' : 'Refresh'}
            </button>
            
            <div className="text-sm text-gray-500 bg-white px-3 py-1.5 rounded-lg">
              Updated: {lastUpdate.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>

      {/* Статистичні картки */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="card bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Active Opportunities</p>
              <p className="text-2xl font-bold mt-1">{opportunities.length}</p>
            </div>
            <Zap className="w-8 h-8 opacity-80" />
          </div>
        </div>
        
        <div className="card bg-gradient-to-r from-green-500 to-emerald-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-emerald-100 text-sm">Total Profit</p>
              <p className="text-2xl font-bold mt-1">${totalProfit.toFixed(2)}</p>
            </div>
            <DollarSign className="w-8 h-8 opacity-80" />
          </div>
        </div>
        
        <div className="card bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Avg. Profit</p>
              <p className="text-2xl font-bold mt-1">${avgProfit.toFixed(2)}</p>
            </div>
            <TrendingUp className="w-8 h-8 opacity-80" />
          </div>
        </div>
        
        <div className="card bg-gradient-to-r from-amber-500 to-orange-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-amber-100 text-sm">Best Opportunity</p>
              <p className="text-2xl font-bold mt-1">
                {bestOpportunity ? `${bestOpportunity.profitPercentage.toFixed(2)}%` : 'N/A'}
              </p>
            </div>
            <BarChart3 className="w-8 h-8 opacity-80" />
          </div>
        </div>
      </div>
      <div className="mb-4 p-4 bg-gray-50 rounded-lg border">
  <div className="flex items-center justify-between">
    <div className="flex items-center gap-3">
      <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
      <span className="font-medium">API Status: Connected</span>
    </div>
    <button 
      onClick={() => {
        console.log('Manual refresh...');
        fetchData();
      }}
      className="text-sm text-blue-600 hover:underline"
    >
      Debug: Check Console (F12)
    </button>
  </div>
  <div className="mt-2 text-sm text-gray-600">
    Backend API is returning data. Check browser console for details.
  </div>
</div>
<div className="mb-6">
  <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
    <div className={`w-3 h-3 rounded-full ${
      opportunities.length > 0 ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
    }`}></div>
    <div className="text-sm">
      <span className="font-medium">Backend Status:</span>
      <span className="ml-2">
        {opportunities.length > 0 
          ? `Connected (${opportunities.length} opportunities)` 
          : 'Connecting to API...'}
      </span>
    </div>
    <a 
      href="http://localhost:5000/api/arbitrage/scan" 
      target="_blank"
      className="ml-auto text-sm text-blue-600 hover:underline"
    >
      Test API →
    </a>
  </div>
</div>
      {/* Основний контент */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Графік */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Profit Trends</h2>
              <div className="flex gap-2">
                {['24h', '7d', '30d'].map((period) => (
                  <button
                    key={period}
                    className="px-3 py-1 text-sm rounded-lg bg-gray-100 hover:bg-gray-200"
                  >
                    {period}
                  </button>
                ))}
              </div>
            </div>
            <RealTimeChart data={opportunities} />
          </div>
        </div>

        {/* Калькулятор */}
        <div>
          <div className="card bg-gradient-to-br from-gray-900 to-gray-800 text-white">
            <h2 className="text-xl font-semibold mb-4">🚀 Quick Calculator</h2>
            <ArbitrageCalculator />
          </div>
        </div>
      </div>

      {/* Таблиця арбітражів */}
      <div className="mt-6">
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Latest Opportunities
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({opportunities.length} found)
              </span>
            </h2>
            <div className="text-sm text-gray-500">
              Auto-refresh in 60 seconds
            </div>
          </div>
          
          {loading ? (
            <div className="py-12">
              <Loader />
            </div>
          ) : opportunities.length > 0 ? (
            <ArbitrageTable data={opportunities} />
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No arbitrage opportunities found</p>
              <p className="text-sm mt-2">Check back later or adjust your filters</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Arbitrage;