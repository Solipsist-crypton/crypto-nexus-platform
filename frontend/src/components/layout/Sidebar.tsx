// frontend/src/components/layout/Sidebar.tsx (оновлений)
import React from 'react'
import { Home, TrendingUp, Rocket, Gift, Settings, Bell } from 'lucide-react'

const Sidebar: React.FC = () => {
  const menuItems = [
    { icon: <Home size={20} />, label: 'Dashboard', active: false },
    { icon: <TrendingUp size={20} />, label: 'Arbitrage', active: true },
    { icon: <Rocket size={20} />, label: 'Futures', active: false },
    { icon: <Gift size={20} />, label: 'Airdrops', active: false },
    { icon: <Bell size={20} />, label: 'Alerts', active: false },
    { icon: <Settings size={20} />, label: 'Settings', active: false },
  ]

  return (
    <div className="hidden lg:flex flex-col w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      <div className="p-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600"></div>
          <div>
            <div className="font-bold text-lg">Crypto Nexus</div>
            <div className="text-sm text-gray-500">Professional Edition</div>
          </div>
        </div>
      </div>
      
      <nav className="flex-1 px-4">
        {menuItems.map((item) => (
          <a
            key={item.label}
            href={`/${item.label.toLowerCase()}`}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
              item.active 
                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' 
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
            {item.active && (
              <div className="ml-auto w-2 h-2 bg-blue-500 rounded-full"></div>
            )}
          </a>
        ))}
      </nav>
      
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-sm text-gray-500 mb-2">Active Bots</div>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm">Arbitrage Scanner</span>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
          <div className="text-xs text-gray-500">Updated just now</div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar