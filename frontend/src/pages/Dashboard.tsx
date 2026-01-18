import React from 'react'
import { TrendingUp, Users, DollarSign, Activity } from 'lucide-react'

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text">Welcome Back!</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Your cryptocurrency dashboard with all important metrics
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { icon: <DollarSign />, label: 'Total Balance', value: '$42,589.23', change: '+5.2%' },
          { icon: <TrendingUp />, label: 'Today\'s Profit', value: '$1,234.56', change: '+12.4%' },
          { icon: <Activity />, label: 'Active Trades', value: '18', change: '+3' },
          { icon: <Users />, label: 'Followers', value: '1,234', change: '+45' },
        ].map((stat, index) => (
          <div key={index} className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-blue-100 dark:bg-blue-900">
                <div className="text-blue-600 dark:text-blue-400">
                  {stat.icon}
                </div>
              </div>
              <div className="text-sm px-3 py-1 rounded-full bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300">
                {stat.change}
              </div>
            </div>
            <div className="text-2xl font-bold mb-1">{stat.value}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Coming Soon Modules */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass-card rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4">🚧 Futures Signals (Coming Soon)</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            AI-powered futures trading signals with advanced analytics.
          </p>
          <div className="text-sm text-blue-500 dark:text-blue-400">
            Expected release: Q2 2024
          </div>
        </div>

        <div className="glass-card rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4">🎁 Airdrop Farming (Coming Soon)</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Automated airdrop participation and ROI tracking.
          </p>
          <div className="text-sm text-blue-500 dark:text-blue-400">
            Expected release: Q2 2024
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard