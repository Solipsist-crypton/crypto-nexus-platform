const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export interface ArbitrageOpportunity {
  coin: string;
  buy_exchange: string;
  sell_exchange: string;
  buy_price: number;
  sell_price: number;
  price_difference: number;
  price_difference_percent: number;
  net_profit_percent: number;
  timestamp: string;
}

export interface CoinPrices {
  coin: string;
  prices: Record<string, number>;
  best_opportunity: ArbitrageOpportunity | null;
  all_opportunities: ArbitrageOpportunity[];
  timestamp: string;
}

export interface ScanResult {
  opportunities: any[];
  total_scanned: number;
  found_opportunities: number;
  threshold: number;
}

// Найкраща можливість
export const fetchBestOpportunity = async (): Promise<ArbitrageOpportunity | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/arbitrage/best`);
    if (!response.ok) throw new Error('Network response was not ok');
    
    const data = await response.json();
    return data.success ? data.data : null;
  } catch (error) {
    console.error('Error fetching best opportunity:', error);
    return null;
  }
};

// Сканування всіх монет
export const fetchAllOpportunities = async (threshold = 0.1): Promise<any[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/arbitrage/scan?threshold=${threshold}`);
    if (!response.ok) throw new Error('Network response was not ok');
    
    const data = await response.json();
    return data.success ? data.data.opportunities : [];
  } catch (error) {
    console.error('Error fetching all opportunities:', error);
    return [];
  }
};

// Порівняння конкретної монети
export const fetchCoinPrices = async (coin: string): Promise<CoinPrices | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/arbitrage/compare/${coin}`);
    if (!response.ok) throw new Error('Network response was not ok');
    
    const data = await response.json();
    return data.success ? data.data : null;
  } catch (error) {
    console.error(`Error fetching prices for ${coin}:`, error);
    return null;
  }
};

// Калькулятор арбітражу
export const calculateArbitrage = async (
  coin: string,
  buyExchange: string,
  sellExchange: string,
  amount: number = 1.0
): Promise<any> => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/arbitrage/calculate/${coin}/${buyExchange}/${sellExchange}/${amount}`
    );
    if (!response.ok) throw new Error('Network response was not ok');
    
    const data = await response.json();
    return data.success ? data.data : null;
  } catch (error) {
    console.error('Error calculating arbitrage:', error);
    return null;
  }
};

// Статус всіх бірж
export const fetchExchangeStatus = async () => {
  const exchanges = ['binance', 'kraken', 'bybit', 'okx'];
  const statuses = await Promise.all(
    exchanges.map(async (exchange) => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/${exchange}/health`);
        if (!response.ok) return { exchange, status: 'error' };
        const data = await response.json();
        return { exchange: exchange.charAt(0).toUpperCase() + exchange.slice(1), ...data };
      } catch {
        return { exchange, status: 'error' };
      }
    })
  );
  return statuses;
};