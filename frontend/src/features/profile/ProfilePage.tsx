// frontend/src/features/profile/ProfilePage.tsx
import React, { useState, useEffect } from 'react';
import ProfileHeader from './components/ProfileHeader';
import StatsDashboard from './components/StatsDashboard';
import EquityChart from './components/EquityChart';
import PerformanceChart from './components/PerformanceChart';
import TradesTable from './components/TradesTable';
import AIInsights from './components/AIInsights';
import { useProfileData } from './hooks/useProfileData';

const ProfilePage: React.FC = () => {
  const { 
    profileData, 
    trades, 
    stats, 
    isLoading, 
    error,
    refreshData 
  } = useProfileData();

  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d' | 'all'>('30d');

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-4 md:p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            {/* Skeleton loader */}
            <div className="h-24 bg-gray-800 rounded-xl mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div className="h-64 bg-gray-800 rounded-xl"></div>
              <div className="h-64 bg-gray-800 rounded-xl"></div>
            </div>
            <div className="h-96 bg-gray-800 rounded-xl"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-4 md:p-6">
        <div className="max-w-7xl mx-auto text-center py-20">
          <div className="text-6xl mb-4">😕</div>
          <h1 className="text-2xl font-bold mb-2">Помилка завантаження</h1>
          <p className="text-gray-400 mb-6">{error}</p>
          <button
            onClick={refreshData}
            className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-medium"
          >
            Спробувати знову
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-black text-white p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <ProfileHeader 
          user={profileData.user}
          onRefresh={refreshData}
        />

        {/* Timeframe Selector */}
        <div className="mb-6 flex justify-end">
          <div className="inline-flex rounded-lg bg-gray-800 p-1">
            {(['7d', '30d', '90d', 'all'] as const).map((period) => (
              <button
                key={period}
                onClick={() => setTimeframe(period)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  timeframe === period
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {period === '7d' ? '7 днів' : 
                 period === '30d' ? '30 днів' : 
                 period === '90d' ? '90 днів' : 'Весь час'}
              </button>
            ))}
          </div>
        </div>

        {/* Stats Dashboard */}
        <div className="mb-8">
          <StatsDashboard stats={stats} timeframe={timeframe} />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700/50 shadow-2xl">
            <EquityChart trades={trades} timeframe={timeframe} />
          </div>
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700/50 shadow-2xl">
            <PerformanceChart trades={trades} timeframe={timeframe} />
          </div>
        </div>

        {/* AI Insights */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 backdrop-blur-lg rounded-2xl p-6 border border-purple-700/30 shadow-2xl">
            <AIInsights stats={stats} trades={trades} />
          </div>
        </div>

        {/* Trades Table */}
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700/50 shadow-2xl">
          <TradesTable trades={trades} />
        </div>

        {/* Footer Note */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>ℹ️ Всі дані оновлюються в реальному часі. Останнє оновлення: {new Date().toLocaleTimeString('uk-UA')}</p>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;