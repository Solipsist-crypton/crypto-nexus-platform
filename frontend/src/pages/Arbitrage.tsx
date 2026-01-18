import React, { useState, useEffect } from 'react'
import { RefreshCw, Filter, Download } from 'lucide-react'
import { arbitrageApi } from '../api/arbitrage'
import ArbitrageTable from '../modules/arbitrage/components/ArbitrageTable'
import ArbitrageCalculator from '../modules/arbitrage/components/Calculator'
import RealTimeChart from '../modules/arbitrage/components/RealTimeChart'
import Loader from '../modules/arbitrage/components/common/Loader'

const Arbitrage: React.FC = () => {
  const [opportunities, setOpportunities] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCoin, setSelectedCoin] = useState<string>('BTC')
  const [timeRange, setTimeRange] = useState<string>('24h')

  const fetchOpportunities = async () => {
    setLoading(true)
    try {
      const data = await arbitrageApi.getOpportunities()
      setOpportunities(data)
    } catch (error) {
      console.error('Failed to fetch opportunities:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOpportunities()
    const interval = setInterval(fetchOpportunities, 30000) // Оновлення кожні 30 секунд
    return () => clearInterval(interval)
  }, [])

  const totalProfit = opportunities.reduce((sum, opp) => sum + opp.profit, 0)
  const avgProfit = opportunities.length > 0 ? totalProfit / opportunities.length : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Arbitrage Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time cryptocurrency arbitrage opportunities across multiple exchanges
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchOpportunities}
            disabled={loading}
            className="btn-primary flex items-center gap-2"
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            {loading ? 'Updating...' : 'Refresh'}
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Filter size={18} />
            Filter
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download size={18} />
            Export
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Active Opportunities', value: opportunities.length, change: '+3' },
          { label: 'Total Profit', value: `$${totalProfit.toFixed(2)}`, change: '+12%' },
          { label: 'Avg. Profit', value: `$${avgProfit.toFixed(2)}`, change: '+5%' },
          { label: 'Success Rate', value: '94%', change: '+2%' },
        ].map((stat, index) => (
          <div
            key={index}
            className="glass-card rounded-xl p-4"
          >
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              {stat.label}
            </div>
            <div className="flex items-baseline justify-between">
              <div className="text-2xl font-bold">{stat.value}</div>
              <div className="text-sm px-2 py-1 rounded-full bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300">
                {stat.change}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Calculator */}
        <div className="lg:col-span-1">
          <ArbitrageCalculator />
        </div>

        {/* Right Column - Chart & Table */}
        <div className="lg:col-span-2 space-y-6">
          {/* Chart */}
          <div className="glass-card rounded-xl p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Profit Trends</h2>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="text-sm bg-transparent border rounded-lg px-3 py-1"
              >
                <option value="1h">1 Hour</option>
                <option value="24h">24 Hours</option>
                <option value="7d">7 Days</option>
                <option value="30d">30 Days</option>
              </select>
            </div>
            <RealTimeChart data={opportunities} />
          </div>

          {/* Table */}
          <div className="glass-card rounded-xl p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Arbitrage Opportunities</h2>
              <div className="flex gap-2">
                <select
                  value={selectedCoin}
                  onChange={(e) => setSelectedCoin(e.target.value)}
                  className="text-sm bg-transparent border rounded-lg px-3 py-1"
                >
                  <option value="ALL">All Coins</option>
                  <option value="BTC">Bitcoin</option>
                  <option value="ETH">Ethereum</option>
                  <option value="SOL">Solana</option>
                </select>
              </div>
            </div>
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <Loader />
              </div>
            ) : (
              <ArbitrageTable data={opportunities} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Arbitrage