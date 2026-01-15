import React from 'react';

export default function Dashboard() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-2">Active Opportunities</h3>
          <p className="text-3xl font-bold text-green-400">15</p>
        </div>
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-2">Portfolio Value</h3>
          <p className="text-3xl font-bold text-cyan-400">$42,850</p>
        </div>
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-2">Daily P&L</h3>
          <p className="text-3xl font-bold text-green-400">+$1,240</p>
        </div>
      </div>

      <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-800">
        <h2 className="text-xl font-bold mb-4">System Status</h2>
        <p className="text-gray-300">🚀 Backend API: Connected</p>
        <p className="text-gray-300">📊 CoinGecko: Ready</p>
        <p className="text-gray-300">🔄 Arbitrage Engine: Starting...</p>
      </div>
    </div>
  );
}