import React from 'react'
import {
  Home,
  TrendingUp,
  Rocket,
  Gift,
  BarChart3,
  Settings,
  HelpCircle,
} from 'lucide-react'

const Sidebar: React.FC = () => {
  const menuItems = [
    { icon: <Home size={20} />, label: 'Dashboard', path: '/' },
    { icon: <TrendingUp size={20} />, label: 'Arbitrage', path: '/arbitrage' },
    { icon: <Rocket size={20} />, label: 'Futures', path: '/futures' },
    { icon: <Gift size={20} />, label: 'Airdrops', path: '/airdrops' },
    { icon: <BarChart3 size={20} />, label: 'Analytics', path: '/analytics' },
    { icon: <Settings size={20} />, label: 'Settings', path: '/settings' },
    { icon: <HelpCircle size={20} />, label: 'Help', path: '/help' },
  ]

  const stats = [
    { label: 'Active Opportunities', value: '24', change: '+3' },
    { label: 'Total Profit', value: '$2,450', change: '+12%' },
    { label: 'Success Rate', value: '94%', change: '+2%' },
  ]

  return (
    <aside className="hidden lg:flex flex-col w-64 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
      {/* Navigation */}
      <nav className="flex-1 p-4">
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-4 uppercase tracking-wider">
            Navigation
          </h2>
          <ul className="space-y-2">
            {menuItems.map((item) => (
              <li key={item.label}>
                <a
                  href={item.path}
                  className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 transition-colors"
                >
                  {item.icon}
                  <span>{item.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Quick Stats */}
        <div>
          <h2 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-4 uppercase tracking-wider">
            Quick Stats
          </h2>
          <div className="space-y-3">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3"
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {stat.label}
                  </span>
                  <span className="text-xs px-2 py-1 rounded-full bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300">
                    {stat.change}
                  </span>
                </div>
                <div className="text-xl font-semibold mt-1">{stat.value}</div>
              </div>
            ))}
          </div>
        </div>
      </nav>

      {/* Recent Activity */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-800">
        <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-3">
          Recent Activity
        </h3>
        <div className="space-y-2">
          {[
            { text: 'ETH arbitrage found', time: '2 min ago' },
            { text: 'BTC futures updated', time: '15 min ago' },
            { text: 'New airdrop added', time: '1 hour ago' },
          ].map((activity, index) => (
            <div
              key={index}
              className="text-sm text-gray-600 dark:text-gray-400 flex justify-between"
            >
              <span>{activity.text}</span>
              <span className="text-xs text-gray-500">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}

export default Sidebar