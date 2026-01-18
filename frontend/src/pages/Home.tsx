// frontend/src/pages/Home.tsx
import React from 'react'
import { ArrowRight, Zap, Shield, TrendingUp, Users, BarChart3 } from 'lucide-react'

const Home: React.FC = () => {
  const features = [
    { icon: <Zap className="w-6 h-6" />, title: 'Real-time Monitoring', desc: 'Track 50+ exchanges live' },
    { icon: <TrendingUp className="w-6 h-6" />, title: 'AI Signals', desc: '85% accuracy rate' },
    { icon: <Shield className="w-6 h-6" />, title: 'Secure', desc: 'Bank-level encryption' },
    { icon: <Users className="w-6 h-6" />, title: 'Community', desc: '10k+ active traders' },
    { icon: <BarChart3 className="w-6 h-6" />, title: 'Analytics', desc: 'Advanced insights' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Crypto Nexus Platform
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          Professional cryptocurrency trading platform with advanced arbitrage, 
          futures signals, and airdrop farming.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="px-8 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold hover:opacity-90 transition-all flex items-center justify-center gap-2">
            Start Arbitrage <ArrowRight className="w-5 h-5" />
          </button>
          <button className="px-8 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl font-semibold hover:bg-gray-50 dark:hover:bg-gray-800 transition-all">
            View Demo
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
        {[
          { value: '500+', label: 'Coins' },
          { value: '50+', label: 'Exchanges' },
          { value: '99.9%', label: 'Uptime' },
          { value: '10K+', label: 'Users' },
        ].map((stat, idx) => (
          <div key={idx} className="bg-white dark:bg-gray-800 rounded-2xl p-6 text-center shadow-lg">
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{stat.value}</div>
            <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Features */}
      <div className="mb-16">
        <h2 className="text-3xl font-bold text-center mb-10">Why Choose Our Platform</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feat, idx) => (
            <div key={idx} className="bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-blue-500 dark:text-blue-400 mb-4">{feat.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{feat.title}</h3>
              <p className="text-gray-600 dark:text-gray-400">{feat.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Home