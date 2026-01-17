import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import ArbitrageDashboard from './modules/arbitrage/ArbitrageDashboard';
import FuturesDashboard from './modules/futures/FuturesDashboard';
import AirdropsDashboard from './modules/airdrops/AirdropsDashboard';

const App: React.FC = () => {
  return (
    <Router>
      <MainLayout>
        <Routes>
          {/* Активний модуль */}
          <Route path="/arbitrage" element={<ArbitrageDashboard />} />
          
          {/* Майбутні модулі (заглушки) */}
          <Route path="/futures" element={
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">📈 Ф'ючерсні сигнали</h2>
              <p className="text-gray-600 mb-8">Модуль в розробці. Скоро тут з'являться AI-генеровані торгові сигнали.</p>
              <div className="inline-block px-6 py-3 bg-yellow-100 text-yellow-800 rounded-lg">
                ⏳ Очікуйте у наступних оновленнях
              </div>
            </div>
          } />
          
          <Route path="/airdrops" element={
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">🎁 Airdrop Farming</h2>
              <p className="text-gray-600 mb-8">Модуль в розробці. Скоро тут з'явиться копітрейдинг та фармінг аердропів.</p>
              <div className="inline-block px-6 py-3 bg-yellow-100 text-yellow-800 rounded-lg">
                ⏳ Очікуйте у наступних оновленнях
              </div>
            </div>
          } />
          
          {/* Перенаправлення на арбітраж за замовчуванням */}
          <Route path="/" element={<Navigate to="/arbitrage" replace />} />
        </Routes>
      </MainLayout>
    </Router>
  );
};

export default App;