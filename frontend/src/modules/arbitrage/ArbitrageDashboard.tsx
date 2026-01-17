import React, { useState, useEffect } from 'react';
import BestOpportunityCard from './components/BestOpportunityCard';
import PriceComparisonTable from './components/PriceComparisonTable';
import ArbitrageCalculator from './components/ArbitrageCalculator';
import { fetchBestOpportunity, fetchAllOpportunities } from './services/api';

const ArbitrageDashboard: React.FC = () => {
  const [bestOpportunity, setBestOpportunity] = useState<any>(null);
  const [allOpportunities, setAllOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [best, all] = await Promise.all([
          fetchBestOpportunity(),
          fetchAllOpportunities()
        ]);
        setBestOpportunity(best);
        setAllOpportunities(all);
      } catch (error) {
        console.error('Помилка завантаження даних:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
    // Оновлення кожні 30 секунд
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">🔍 Арбітражний моніторинг</h1>
        <p className="text-gray-600 mt-2">
          Знаходьте прибуткові арбітражні можливості між різними біржами
        </p>
      </div>

      {/* Найкраща можливість */}
      <BestOpportunityCard opportunity={bestOpportunity} />

      {/* Всі можливості */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📊 Всі арбітражні можливості</h2>
        <PriceComparisonTable opportunities={allOpportunities} />
      </div>

      {/* Калькулятор арбітражу */}
      <ArbitrageCalculator />
    </div>
  );
};

export default ArbitrageDashboard;