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

// === НОВІ ФУНКЦІЇ ДЛЯ ГРАФІКІВ ===

// Отримати історичні дані для угоди
export const fetchTradeHistory = async (tradeId: number, interval: string = '1h', limit: number = 24): Promise<any> => {
  try {
    const response = await fetch(
      `${API_BASE}/trade/${tradeId}/history?interval=${interval}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `API помилка: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Помилка завантаження історії:', error);
    // Повертаємо пусті дані, фронтенд згенерує демо
    return null;
  }
};

// Отримати реальні дані з біржі
export const fetchMarketData = async (symbol: string, interval: string = '1h', limit: number = 24): Promise<any> => {
  try {
    // Очищаємо символ для Binance API
    const cleanSymbol = symbol.split(':')[0].replace('/', '');
    
    const response = await fetch(
      `https://api.binance.com/api/v3/klines?symbol=${cleanSymbol}&interval=${interval}&limit=${limit}`,
      {
        method: 'GET',
      }
    );

    if (!response.ok) {
      throw new Error(`Binance API error: ${response.status}`);
    }

    const data = await response.json();
    
    // Форматуємо відповідно до нашої структури
    return data.map((kline: any[]) => ({
      time: new Date(kline[0]).toISOString(),
      open: parseFloat(kline[1]),
      high: parseFloat(kline[2]),
      low: parseFloat(kline[3]),
      close: parseFloat(kline[4]),
      volume: parseFloat(kline[5]),
      price: parseFloat(kline[4]) // для сумісності
    }));
  } catch (error) {
    console.error('Помилка завантаження даних з біржі:', error);
    return null;
  }
};