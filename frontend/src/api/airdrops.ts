export const airdropsApi = {
  async getActiveAirdrops() {
    // TODO: Підключити до бекенду коли буде готово
    return [
      { name: 'StarkNet', tier: 'S', reward: '$500-5000', deadline: '2024-03-15' },
      { name: 'zkSync', tier: 'A', reward: '$200-2000', deadline: '2024-02-28' },
    ]
  },
}