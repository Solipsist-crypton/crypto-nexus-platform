import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { BarChart3, TrendingUp, Gift, Home } from 'lucide-react';

export default function Layout() {
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <Home size={20} /> },
    { path: '/arbitrage', label: 'Arbitrage', icon: <TrendingUp size={20} /> },
    { path: '/futures', label: 'Futures', icon: <BarChart3 size={20} /> },
    { path: '/airdrops', label: 'Airdrops', icon: <Gift size={20} /> },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 border-r border-gray-800 bg-gray-900/50 backdrop-blur-lg p-6">
        <div className="mb-10">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            Crypto Nexus
          </h1>
          <p className="text-gray-400 text-sm">v3.0 • Quant Platform</p>
        </div>

        <nav className="space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className="flex items-center gap-3 rounded-lg px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-8">
        <Outlet />
      </main>
    </div>
  );
}