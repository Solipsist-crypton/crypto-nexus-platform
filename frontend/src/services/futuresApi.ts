// frontend/src/services/futuresApi.ts
const API_BASE = 'http://localhost:5000/api/futures';

// Генерація AI-сигналу
export const generateSignal = async (symbol: string): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE}/signals/generate?symbol=${encodeURIComponent(symbol)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `API помилка: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Помилка генерації сигналу:', error);
    throw error;
  }
};

// Створення віртуальної угоди
export const createVirtualTrade = async (signalId: number): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE}/entry-points/enter/${signalId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Помилка: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Помилка створення угоди:', error);
    throw error;
  }
};

// Отримання списку угод
export const fetchTrades = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE}/virtual-trades`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Помилка: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Помилка завантаження угод:', error);
    return { trades: [] };
  }
};

// Отримання статистики
export const fetchStats = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE}/virtual-trades/statistics`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Помилка: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Помилка завантаження статистики:', error);
    return {
      active_trades: 0,
      closed_trades: 0,
      win_rate: "0",
      total_pnl: "0",
    };
  }
};