// frontend/src/pages/Futures.tsx
import React, { useState, useEffect } from 'react';
import CoinList from '../components/futures/CoinList';
import VirtualTradesTable from '../components/futures/VirtualTradesTable';
import StatsCards from '../components/futures/StatsCards';
import { generateSignal, createVirtualTrade, fetchTrades, fetchStats } from '../services/futuresApi';

const FuturesPage: React.FC = () => {
  const [activeSignal, setActiveSignal] = useState<any>(null);
  const [trades, setTrades] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  // Завантаження угод та статистики
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [tradesData, statsData] = await Promise.all([
        fetchTrades(),
        fetchStats()
      ]);
      setTrades(tradesData.trades || []);
      setStats(statsData || {});
    } catch (error) {
      console.error('Помилка завантаження даних:', error);
    }
  };

  const handleAnalyze = async (symbol: string) => {
    setAnalyzing(true);
    setActiveSignal(null);
    
    try {
      const data = await generateSignal(symbol);
      
      if (data.status === 'success') {
        setActiveSignal(data.signal);
        console.log('✅ Сигнал згенеровано:', data.signal);
      } else {
        alert(`❌ Помилка: ${data.error || 'Невідома помилка'}`);
      }
    } catch (error: any) {
      console.error('❌ Помилка аналізу:', error);
      alert(`❌ Помилка: ${error.message || 'Не вдалося згенерувати сигнал'}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleTrack = async (signalId: number) => {
    setLoading(true);
    try {
      const result = await createVirtualTrade(signalId);
      
      if (result.status === 'success') {
        alert('✅ Віртуальну угоду створено!');
        await loadData(); // Оновлюємо дані
      } else {
        alert(`❌ Помилка: ${result.detail || 'Не вдалося створити угоду'}`);
      }
    } catch (error: any) {
      console.error('❌ Помилка створення угоди:', error);
      alert(`❌ Помилка: ${error.message || 'Помилка з\'єднання'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Заголовок */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            <span className="text-green-400">📈</span> AI Ф'ючерсні Сигнали
          </h1>
          <p className="text-gray-400">Професійна система віртуального тестування</p>
        </div>

        {/* Карточки статистики */}
        <div className="mb-8">
          <StatsCards stats={stats} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Ліва колонка: Список монет */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 rounded-xl p-5 shadow-lg">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <span className="text-yellow-400 mr-2">💰</span> Оберіть монету
              </h2>
              <CoinList onAnalyze={handleAnalyze} analyzing={analyzing} />
            </div>
          </div>

          {/* Центральна колонка: AI Сигнал */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-xl p-5 shadow-lg">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <span className="text-purple-400 mr-2">🤖</span> AI Сигнал
              </h2>
            </div>
          </div>
        </div>

        {/* Таблица угод */}
        <div className="bg-gray-800 rounded-xl p-5 shadow-lg">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <span className="text-orange-400 mr-2">📋</span> Мої Віртуальні Угоди
          </h2>
          <VirtualTradesTable trades={trades} />
        </div>
      </div>
    </div>
  );
};

export default FuturesPage;