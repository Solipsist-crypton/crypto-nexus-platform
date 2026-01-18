import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ArbitrageOpportunity {
  id: string;
  coin: string;
  buyExchange: string;
  sellExchange: string;
  buyPrice: number;
  sellPrice: number;
  profit: number;
  profitPercentage: number;
  volume: number;
  timestamp: string;
}

export const arbitrageApi = {
  async getOpportunities(): Promise<ArbitrageOpportunity[]> {
    try {
      const response = await axios.get(`${API_URL}/api/arbitrage/scan`);
      const apiData = response.data;
      
      if (apiData.success && apiData.data?.opportunities) {
        // Використовуємо Set для унікальних можливостей
        const uniqueOpportunities = new Map<string, ArbitrageOpportunity>();
        
        apiData.data.opportunities.forEach((coinData: any) => {
          // Обробляємо ВСІ можливості з all_opportunities
          if (coinData.all_opportunities && Array.isArray(coinData.all_opportunities)) {
            coinData.all_opportunities.forEach((opp: any) => {
              // Створюємо унікальний ключ
              const uniqueKey = `${coinData.coin}-${opp.buy_exchange}-${opp.sell_exchange}`;
              
              if (!uniqueOpportunities.has(uniqueKey)) {
                uniqueOpportunities.set(uniqueKey, {
                  id: uniqueKey,
                  coin: coinData.coin + '/USDT',
                  buyExchange: opp.buy_exchange,
                  sellExchange: opp.sell_exchange,
                  buyPrice: opp.buy_price,
                  sellPrice: opp.sell_price,
                  // Більш точний розрахунок прибутку для 1000 одиниць
                  profit: Number(((opp.sell_price - opp.buy_price) * 1000).toFixed(2)),
                  profitPercentage: opp.net_profit_percent,
                  volume: 1000000,
                  timestamp: opp.timestamp,
                });
              }
            });
          }
        });
        
        // Конвертуємо Map назад в масив
        const opportunities = Array.from(uniqueOpportunities.values());
        
        console.log(`✅ Found ${opportunities.length} UNIQUE opportunities`);
        return opportunities;
      }
      
      return this.getMockData();
    } catch (error) {
      console.error('API Error:', error);
      return this.getMockData();
    }
  },


  // Розрахувати конкретну можливість
  async calculate(coin: string, buyExchange: string, sellExchange: string, amount: number) {
    const response = await axios.get(
      `${API_URL}/api/arbitrage/calculate/${coin}/${buyExchange}/${sellExchange}/${amount}`
    );
    return response.data;
  },

  // Тестові дані для розробки
  getMockData() {
    console.log('⚠️ Using mock data - API not available');
    return [
      {
        id: '1',
        coin: 'BTC/USDT',
        buyExchange: 'Binance',
        sellExchange: 'Kraken',
        buyPrice: 43210.50,
        sellPrice: 43300.25,
        profit: 134.63,
        profitPercentage: 0.31,
        volume: 2500000,
        timestamp: new Date().toISOString(),
      },
      {
        id: '2',
        coin: 'ETH/USDT',
        buyExchange: 'Coinbase',
        sellExchange: 'Binance',
        buyPrice: 2540.30,
        sellPrice: 2560.80,
        profit: 205.00,
        profitPercentage: 0.81,
        volume: 1200000,
        timestamp: new Date().toISOString(),
      },
      {
        id: '3',
        coin: 'SOL/USDT',
        buyExchange: 'KuCoin',
        sellExchange: 'OKX',
        buyPrice: 102.45,
        sellPrice: 103.20,
        profit: 37.50,
        profitPercentage: 0.73,
        volume: 500000,
        timestamp: new Date().toISOString(),
      },
    ];
  }
};
