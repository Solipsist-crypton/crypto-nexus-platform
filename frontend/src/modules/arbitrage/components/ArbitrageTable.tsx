import React from 'react';
import { ExternalLink, TrendingUp, TrendingDown } from 'lucide-react';
import { ArbitrageOpportunity } from '../../../api/arbitrage';

interface Props {
  data: ArbitrageOpportunity[];
}

const ArbitrageTable: React.FC<Props> = ({ data }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="bg-gray-50">
    <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 rounded-l-lg">Coin</th>
    <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700">Exchanges</th>
    <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700">Price Difference</th>
    <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700">Profit</th>
    <th className="py-3 px-4 text-left text-sm font-semibold text-gray-700 rounded-r-lg">Action</th>
  </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-4 px-4">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    {item.coin.split('/')[0].substring(0, 3)}
                  </div>
                  <div className="ml-3">
                    <div className="font-medium">{item.coin}</div>
                    <div className="text-xs text-gray-500">
                      Vol: ${(item.volume / 1000000).toFixed(1)}M
                    </div>
                  </div>
                </div>
              </td>
              <td className="py-4 px-4">
                <div className="space-y-1">
                  <div className="flex items-center text-sm">
                    <span className="text-green-600">BUY:</span>
                    <span className="ml-2 font-medium">{item.buyExchange}</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <span className="text-red-600">SELL:</span>
                    <span className="ml-2 font-medium">{item.sellExchange}</span>
                  </div>
                </div>
              </td>
              <td className="py-4 px-4">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  item.profitPercentage > 0.5 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {item.profitPercentage > 0.5 ? (
                    <TrendingUp className="w-4 h-4 mr-1" />
                  ) : (
                    <TrendingDown className="w-4 h-4 mr-1" />
                  )}
                  {item.profitPercentage.toFixed(2)}%
                </div>
              </td>
              <td className="py-4 px-4">
                <div className="text-lg font-bold text-green-600">
                  ${item.profit.toFixed(2)}
                </div>
              </td>
              <td className="py-4 px-4">
                <button className="btn-primary flex items-center gap-2 text-sm px-3 py-1.5">
                  <ExternalLink className="w-4 h-4" />
                  Execute
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ArbitrageTable;