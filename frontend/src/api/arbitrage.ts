import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

interface ArbitrageOpportunity {
  id: string
  coin: string
  buyExchange: string
  sellExchange: string
  buyPrice: number
  sellPrice: number
  amount: number
  profit: number
  profitPercentage: number
  fees: number
  timestamp: string
}

interface CalculateRequest {
  coin: string
  buyExchange: string
  sellExchange: string
  amount: number
}

export const arbitrageApi = {
  // Отримання всіх можливостей (з вашого бекенду)
  async getOpportunities(): Promise<ArbitrageOpportunity[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/arbitrage/scan`)
      return response.data
    } catch (error) {
      console.error('Error fetching opportunities:', error)
      // Повертаємо тестові дані для розробки
      return this.getMockOpportunities()
    }
  },

  // Детальний розрахунок (з вашого бекенду)
  async calculateOpportunity(data: CalculateRequest): Promise<any> {
    try {
      const { coin, buyExchange, sellExchange, amount } = data
      const response = await axios.get(
        `${API_BASE_URL}/api/arbitrage/calculate/${coin}/${buyExchange}/${sellExchange}/${amount}`
      )
      return response.data
    } catch (error) {
      console.error('Error calculating opportunity:', error)
      throw error
    }
  },

  // Отримання списку бірж
  async getExchanges(): Promise<string[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/exchanges`)
      return response.data
    } catch (error) {
      console.error('Error fetching exchanges:', error)
      return ['Binance', 'Kraken', 'Coinbase', 'KuCoin', 'OKX']
    }
  },

  // Тестові дані для розробки
  getMockOpportunities(): ArbitrageOpportunity[] {
    return [
      {
        id: '1',
        coin: 'BTC/USDT',
        buyExchange: 'Binance',
        sellExchange: 'Kraken',
        buyPrice: 43210.50,
        sellPrice: 43300.25,
        amount: 1.5,
        profit: 134.63,
        profitPercentage: 0.21,
        fees: 32.41,
        timestamp: new Date().toISOString(),
      },
      {
        id: '2',
        coin: 'ETH/USDT',
        buyExchange: 'Coinbase',
        sellExchange: 'Binance',
        buyPrice: 2540.30,
        sellPrice: 2560.80,
        amount: 10,
        profit: 205.00,
        profitPercentage: 0.81,
        fees: 38.10,
        timestamp: new Date().toISOString(),
      },
      {
        id: '3',
        coin: 'SOL/USDT',
        buyExchange: 'KuCoin',
        sellExchange: 'OKX',
        buyPrice: 102.45,
        sellPrice: 103.20,
        amount: 50,
        profit: 37.50,
        profitPercentage: 0.73,
        fees: 7.65,
        timestamp: new Date().toISOString(),
      },
    ]
  },
}