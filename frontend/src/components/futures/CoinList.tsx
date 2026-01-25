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
    { symbol: 'BNB/USDT:USDT', name: 'Binance Coin', icon: '⎈' },
    { symbol: 'AVAX/USDT:USDT', name: 'Avalanche', icon: '❄️' },
    { symbol: 'DOGE/USDT:USDT', name: 'Dogecoin', icon: '🐕' },
    { symbol: 'LINK/USDT:USDT', name: 'Chainlink', icon: '🔗' },
    { symbol: 'NEAR/USDT:USDT', name: 'Near Protocol', icon: '🌐' },
  ];

  return (
    <div>
      {/* Заголовок */}
      <div className="text-xs text-gray-400 font-medium px-2 py-1 mb-2">
        Доступні монети ({coins.length})
      </div>
      
      {/* Контейнер з фіксованою висотою та inline стилями для скролбара */}
      <div 
        className="overflow-y-auto pr-1"
        style={{
          height: '380px',
          scrollbarWidth: 'thin',
          scrollbarColor: '#4B5563 #1F2937',
        }}
      >
        {/* Inline стилі для Webkit браузерів */}
        <style>
          {`
            .scroll-container::-webkit-scrollbar {
              width: 6px;
            }
            .scroll-container::-webkit-scrollbar-track {
              background: #1F2937;
              border-radius: 3px;
            }
            .scroll-container::-webkit-scrollbar-thumb {
              background: #4B5563;
              border-radius: 3px;
            }
            .scroll-container::-webkit-scrollbar-thumb:hover {
              background: #6B7280;
            }
          `}
        </style>
        
        <div className="scroll-container space-y-1">
          {coins.map((coin) => (
            <div
              key={coin.symbol}
              className="flex items-center justify-between p-3 hover:bg-gray-700/50 transition-colors rounded-lg group cursor-pointer"
              onClick={() => !analyzing && onAnalyze(coin.symbol)}
            >
              {/* Ліва частина - іконка та назва */}
              <div className="flex items-center min-w-0 flex-1">
                <div className="text-xl mr-3 w-6 text-center">{coin.icon}</div>
                <div className="min-w-0">
                  <div className="font-medium text-sm truncate">
                    {coin.symbol.split(':')[0]}
                  </div>
                  <div className="text-xs text-gray-400 truncate">
                    {coin.name}
                  </div>
                </div>
              </div>
              
              {/* Кнопка аналізу */}
              <button
                disabled={analyzing}
                className={`
                  ml-2 px-3 py-1.5 rounded-md text-xs font-medium 
                  transition-all whitespace-nowrap flex-shrink-0
                  ${analyzing
                    ? 'bg-gray-600 cursor-not-allowed opacity-70'
                    : 'bg-blue-600 hover:bg-blue-700 active:scale-95'
                  }
                `}
                onClick={(e) => {
                  e.stopPropagation();
                  if (!analyzing) onAnalyze(coin.symbol);
                }}
              >
                {analyzing ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1.5"></div>
                    <span>...</span>
                  </div>
                ) : (
                  <div className="flex items-center">
                    <span className="mr-1.5">📊</span>
                    <span>Аналіз</span>
                  </div>
                )}
              </button>
            </div>
          ))}
        </div>
      </div>
      
      {/* Підказка */}
      <div className="text-xs text-gray-500 text-center pt-2 border-t border-gray-800/50 mt-2">
        Натисніть на монету для аналізу
      </div>
    </div>
  );
};

export default CoinList;