// frontend/src/pages/Futures.tsx
import React, { useState, useEffect } from 'react';
import CoinList from '../components/futures/CoinList';
import SignalDisplay from '../components/futures/SignalDisplay';
import VirtualTradesTable from '../components/futures/VirtualTradesTable';
import StatsCards from '../components/futures/StatsCards';
import { generateSignal, createVirtualTrade, fetchTrades, fetchStats, fetchTradeHistory } from '../services/futuresApi';

const FuturesPage: React.FC = () => {
  const [activeSignal, setActiveSignal] = useState<any>(null);
  const [tradeHistory, setTradeHistory] = useState<any>(null);
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
    setTradeHistory(null);
    
    try {
      const data = await generateSignal(symbol);
      
      if (data.status === 'success') {
        setActiveSignal(data.signal);
        console.log('✅ Сигнал згенеровано:', data.signal);
        
        // Якщо є активні угоди для цього символу, завантажити історію
        const activeTrade = trades.find(t => 
          t.symbol === symbol && t.status === 'active'
        );
        if (activeTrade) {
          const history = await fetchTradeHistory(activeTrade.id);
          if (history) {
            setTradeHistory(history);
          }
        }
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

  const handleTrack = async () => {
    setLoading(true);
    try {
      if (!activeSignal) {
        alert('❌ Немає активного сигналу!');
        return;
      }
      
      console.log('🎯 Tracking signal:', activeSignal);
      
      const result = await createVirtualTrade(
        activeSignal.id,
        activeSignal.entry_price,
        activeSignal.take_profit,
        activeSignal.stop_loss
      );
      
      if (result.status === 'success') {
        alert('✅ Віртуальну угоду створено!');
        await loadData();
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
              <SignalDisplay 
                signal={activeSignal}
                onTrack={handleTrack}
                loading={loading}
                analyzing={analyzing}
              />
            </div>
          </div>
        </div>

        {/* Таблица угод */}
        <div className="bg-gray-800 rounded-xl p-5 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold flex items-center">
              <span className="text-orange-400 mr-2">📋</span> Мої Віртуальні Угоди
            </h2>
            <button 
              onClick={loadData}
              className="text-sm bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded transition-colors"
            >
              Оновити
            </button>
          </div>
          <VirtualTradesTable trades={trades} />
        </div>
      </div>
    </div>
  );
};

export default FuturesPage;