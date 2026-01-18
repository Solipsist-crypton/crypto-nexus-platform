export const futuresApi = {
  async getSignals() {
    // TODO: Підключити до бекенду коли буде готово
    return [
      { symbol: 'BTC/USDT', signal: 'BUY', confidence: 85 },
      { symbol: 'ETH/USDT', signal: 'SELL', confidence: 72 },
    ]
  },
}