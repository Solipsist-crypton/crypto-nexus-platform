// frontend/src/components/futures/CoinList.tsx
import React from 'react';

interface CoinListProps {
  onAnalyze: (symbol: string) => void;
  analyzing: boolean;
}

const CoinList: React.FC<CoinListProps> = ({ onAnalyze, analyzing }) => {
  const coins = [
    { symbol: 'BTC/USDT:USDT', name: 'Bitcoin', icon: '₿' },
    { symbol: 'ETH/USDT:USDT', name: 'Ethereum', icon: 'Ξ' },
    { symbol: 'SOL/USDT:USDT', name: 'Solana', icon: '◎' },
    { symbol: 'XRP/USDT:USDT', name: 'Ripple', icon: 'X' },
    { symbol: 'ADA/USDT:USDT', name: 'Cardano', icon: 'A' },
  ];

  return (
    <div className="space-y-3">
      {coins.map((coin) => (
        <div
          key={coin.symbol}
          className="bg-gray-700 hover:bg-gray-600 transition-colors p-4 rounded-lg cursor-pointer group"
          onClick={() => !analyzing && onAnalyze(coin.symbol)}
        >
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="text-2xl mr-3">{coin.icon}</div>
              <div>
                <div className="font-bold">{coin.symbol.split(':')[0]}</div>
                <div className="text-sm text-gray-400">{coin.name}</div>
              </div>
            </div>
            <button
              disabled={analyzing}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                analyzing
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 group-hover:scale-105'
              }`}
              onClick={(e) => {
                e.stopPropagation();
                if (!analyzing) onAnalyze(coin.symbol);
              }}
            >
              {analyzing ? (
                <span className="flex items-center">
                  <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                  Аналіз...
                </span>
              ) : (
                <span className="flex items-center">
                  <span className="mr-2">🔍</span> Аналізувати
                </span>
              )}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CoinList;