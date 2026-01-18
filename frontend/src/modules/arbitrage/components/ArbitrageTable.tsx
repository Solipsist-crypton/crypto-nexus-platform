import React from 'react'
import { ExternalLink, ArrowUpRight, AlertCircle } from 'lucide-react'

interface ArbitrageTableProps {
  data: any[]
}

const ArbitrageTable: React.FC<ArbitrageTableProps> = ({ data }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-800">
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600 dark:text-gray-400">
              Coin
            </th>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600 dark:text-gray-400">
              Buy/Sell
            </th>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600 dark:text-gray-400">
              Prices
            </th>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600 dark:text-gray-400">
              Profit
            </th>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600 dark:text-gray-400">
              Fees
            </th>
            <th className="py-3 px-4 text-left text-sm font-semibold text-gray-600 dark:text-gray-400">
              Action
            </th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr
              key={item.id}
              className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <td className="py-4 px-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                    {item.coin.substring(0, 2)}
                  </div>
                  <div>
                    <div className="font-medium">{item.coin}</div>
                    <div className="text-xs text-gray-500">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </td>
              <td className="py-4 px-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <ArrowUpRight size={14} className="text-green-500" />
                    <span className="text-sm">Buy: {item.buyExchange}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <ArrowUpRight size={14} className="text-red-500 rotate-180" />
                    <span className="text-sm">Sell: {item.sellExchange}</span>
                  </div>
                </div>
              </td>
              <td className="py-4 px-4">
                <div className="space-y-1">
                  <div className="text-sm">
                    Buy: ${item.buyPrice.toFixed(2)}
                  </div>
                  <div className="text-sm">
                    Sell: ${item.sellPrice.toFixed(2)}
                  </div>
                </div>
              </td>
              <td className="py-4 px-4">
                <div className="space-y-1">
                  <div className={`font-semibold ${item.profit > 0 ? 'profit-positive' : 'profit-negative'}`}>
                    ${item.profit.toFixed(2)}
                  </div>
                  <div className={`text-sm ${item.profitPercentage > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {item.profitPercentage > 0 ? '+' : ''}{item.profitPercentage.toFixed(2)}%
                  </div>
                </div>
              </td>
              <td className="py-4 px-4">
                <div className="text-sm">${item.fees.toFixed(2)}</div>
              </td>
              <td className="py-4 px-4">
                <div className="flex gap-2">
                  <button className="btn-primary text-sm px-3 py-1.5">
                    Execute
                  </button>
                  <button className="p-1.5 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                    <ExternalLink size={16} />
                  </button>
                  <button className="p-1.5 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                    <AlertCircle size={16} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ArbitrageTable