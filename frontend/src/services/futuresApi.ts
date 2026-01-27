// frontend/src/services/futuresApi.ts
const API_BASE = 'http://localhost:5000/api/futures';
const HISTORY_API_BASE = 'http://localhost:5000/api/history';

// Генерація AI-сигналу
export const generateSignal = async (symbol: string): Promise<any> => {
  try {
    // ВАЖЛИВО: Це POST запит чи GET? Зараз це POST
    const response = await fetch(
      `${API_BASE}/signals/generate?symbol=${encodeURIComponent(symbol)}`,
      {
        method: 'POST', // ← перевір чи це дійсно POST
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
    console.error('Помилка генерації сигналу:', error);
    // Не кидаємо помилку далі - показуємо користувачеві
    throw new Error('Не вдалося згенерувати сигнал. Спробуйте ще раз.');
  }
};

// Створення віртуальної угоди
export const createVirtualTrade = async (signalId: number): Promise<any> => {
  try {
    const response = await fetch(
      `${API_BASE}/entry-points/enter/${signalId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Помилка: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Помилка створення угоди:', error);
    throw new Error('Не вдалося створити угоду. Перевірте з\'єднання.');
  }
};

// Отримання списку угод
export const fetchTrades = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE}/virtual-trades`);
    
    if (!response.ok) {
      // Якщо 404 або інша помилка - повертаємо пустий масив
      console.warn(`API повернуло помилку ${response.status} для /virtual-trades`);
      return { trades: [] };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Помилка завантаження угод:', error);
    // Завжди повертаємо об'єкт з trades для безпеки
    return { trades: [] };
  }
};

// Отримання статистики
export const fetchStats = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE}/virtual-trades/statistics`);
    
    if (!response.ok) {
      console.warn(`API помилка ${response.status} для статистики`);
      // Повертаємо демо-статистику
      return {
        active_trades: 0,
        closed_trades: 0,
        win_rate: "0",
        total_pnl: "0",
        total_profit: "0",
        total_loss: "0"
      };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Помилка завантаження статистики:', error);
    return {
      active_trades: 0,
      closed_trades: 0,
      win_rate: "0",
      total_pnl: "0",
      total_profit: "0",
      total_loss: "0"
    };
  }
};

// === НОВІ ФУНКЦІЇ ДЛЯ ГРАФІКІВ ===

// Отримати історичні дані для угоди
export const fetchTradeHistory = async (tradeId: number, interval: string = '1h', limit: number = 24): Promise<any> => {
  try {
    const response = await fetch(
      `${HISTORY_API_BASE}/trade/${tradeId}?interval=${interval}&limit=${limit}`,
      // ↑↑↑ ВИПРАВЛЕНО: Використовуємо HISTORY_API_BASE
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      // Якщо 404 - значить роутер не підключений або інтернету немає
      console.warn(`API history повернуло ${response.status} для trade ${tradeId}`);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Помилка завантаження історії:', error);
    return null; // Для активації симуляції
  }
};

// Отримати реальні дані з біржі (опційно)
export const fetchMarketData = async (symbol: string, interval: string = '1h', limit: number = 24): Promise<any> => {
  try {
    const cleanSymbol = symbol.split(':')[0].replace('/', '').toUpperCase();
    
    // Додаємо USDT якщо потрібно
    const finalSymbol = cleanSymbol.endsWith('USDT') ? cleanSymbol : `${cleanSymbol}USDT`;
    
    const response = await fetch(
      `https://api.binance.com/api/v3/klines?symbol=${finalSymbol}&interval=${interval}&limit=${limit}`,
      {
        method: 'GET',
      }
    );

    if (!response.ok) {
      console.warn(`Binance API error: ${response.status} для ${finalSymbol}`);
      return null;
    }

    const data = await response.json();
    
    return data.map((kline: any[]) => ({
      time: new Date(kline[0]).toISOString(),
      open: parseFloat(kline[1]),
      high: parseFloat(kline[2]),
      low: parseFloat(kline[3]),
      close: parseFloat(kline[4]),
      volume: parseFloat(kline[5]),
      price: parseFloat(kline[4])
    }));
  } catch (error) {
    console.error('Помилка завантаження даних з Binance:', error);
    return null;
  }
};

// ===== ДОДАТКОВІ ФУНКЦІЇ ЯКЩО ПОТРІБНІ =====

// Тестування API (для дебагу)
export const testAPI = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE}/health`); // або просто API_BASE
    return response.ok;
  } catch (error) {
    console.error('API не доступне:', error);
    return false;
  }
};

// Отримати список доступних монет (якщо є такий API)
export const fetchAvailableSymbols = async (): Promise<string[]> => {
  try {
    // Якщо є ендпоінт для монет
    const response = await fetch(`${API_BASE}/symbols`);
    if (response.ok) {
      const data = await response.json();
      return data.symbols || [];
    }
  } catch (error) {
    console.error('Помилка завантаження символів:', error);
  }
  
  // Повертаємо дефолтний список як fallback
  return ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 
          'BNB/USDT', 'AVAX/USDT', 'DOGE/USDT', 'LINK/USDT', 'NEAR/USDT'];
};