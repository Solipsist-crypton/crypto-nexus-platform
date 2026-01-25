// frontend/src/features/profile/hooks/useProfileData.ts
import { useState, useEffect } from 'react';
import { fetchTrades, fetchStats } from '../../../services/futuresApi';

interface ProfileData {
  user: {
    name: string;
    avatar?: string;
    joinDate: string;
    tier: 'free' | 'pro' | 'elite';
  };
  virtualBalance: number;
  totalDeposits: number;
  totalWithdrawals: number;
}

export const useProfileData = () => {
  const [profileData, setProfileData] = useState<ProfileData>({
    user: {
      name: 'Крипто Трейдер',
      joinDate: 'січня 2024',
      tier: 'pro'
    },
    virtualBalance: 25000,
    totalDeposits: 30000,
    totalWithdrawals: 5000
  });

  const [trades, setTrades] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [tradesData, statsData] = await Promise.all([
        fetchTrades(),
        fetchStats()
      ]);

      setTrades(tradesData.trades || []);
      setStats(statsData || {});
      
      // Симуляція додаткових даних для профілю
      if (tradesData.trades?.length > 0) {
        const activeTrades = tradesData.trades.filter((t: any) => t.status === 'active');
        const totalPnL = activeTrades.reduce((sum: number, trade: any) => sum + (trade.pnl_percentage || 0), 0);
        
        setProfileData(prev => ({
          ...prev,
          virtualBalance: Math.max(0, 25000 + (25000 * totalPnL / 100))
        }));
      }
      
    } catch (err: any) {
      setError(err.message || 'Помилка завантаження даних');
      console.error('Помилка завантаження профілю:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Оновлення кожні 30 секунд
    return () => clearInterval(interval);
  }, []);

  return {
    profileData,
    trades,
    stats,
    isLoading,
    error,
    refreshData: loadData
  };
};