import React from 'react'
import { ArrowRight, Zap, Shield, BarChart } from 'lucide-react'

const Home: React.FC = () => {
  const features = [
    {
      icon: <Zap className="w-8 h-8" />,
      title: 'Real-time Arbitrage',
      description: 'Monitor price differences across 50+ exchanges in real-time',
    },
    {
      icon: <BarChart className="w-8 h-8" />,
      title: 'AI Futures Signals',
      description: 'Smart trading signals with 85%+ accuracy rate',
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Airdrop Farming',
      description: 'Automated airdrop participation with ROI tracking',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-12 md:py-20">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          <span className="gradient-text">Crypto Nexus</span> Platform
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
          Advanced cryptocurrency trading platform with arbitrage monitoring, 
          futures signals, and airdrop farming—all in one place.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="btn-primary flex items-center justify-center gap-2">
            Start Arbitrage <ArrowRight size={20} />
          </button>
          <button className="btn-secondary">Explore Features</button>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {features.map((feature, index) => (
          <div
            key={index}
            className="glass-card rounded-xl p-6 hover:scale-105 transition-transform duration-300"
          >
            <div className="text-blue-500 dark:text-blue-400 mb-4">
              {feature.icon}
            </div>
            <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
            <p className="text-gray-600 dark:text-gray-400">
              {feature.description}
            </p>
          </div>
        ))}
      </div>

      {/* Stats Section */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl p-8 mb-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { value: '500+', label: 'Coins Tracked' },
            { value: '50+', label: 'Exchanges' },
            { value: '99.9%', label: 'Uptime' },
            { value: '< 100ms', label: 'Latency' },
          ].map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl font-bold mb-2 gradient-text">
                {stat.value}
              </div>
              <div className="text-gray-600 dark:text-gray-400">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">Ready to Start?</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Join thousands of traders using Crypto Nexus Platform
        </p>
        <button className="btn-primary px-8 py-3 text-lg">
          Get Started Free
        </button>
      </div>
    </div>
  )
}

export default Home