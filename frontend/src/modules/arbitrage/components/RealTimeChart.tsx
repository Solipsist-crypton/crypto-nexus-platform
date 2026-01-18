import React from 'react'

interface RealTimeChartProps {
  data?: any[]
}

const RealTimeChart: React.FC<{ data?: any[] }> = ({ data = [] }) => {
  return (
    <div className="p-4 border rounded-lg bg-white">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Profit Trends</h3>
        <div className="flex gap-2">
          {['24h', '7d', '30d'].map((period) => (
            <button
              key={period}
              className="px-3 py-1 text-sm rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700"
            >
              {period}
            </button>
          ))}
        </div>
      </div>
      
      <div className="h-64 flex flex-col items-center justify-center bg-gray-50 rounded-lg">
        {data.length > 0 ? (
          <>
            <div className="text-gray-900 font-medium mb-2">Real-time Chart</div>
            <div className="text-sm text-gray-600">
              {data.length} opportunities loaded
            </div>
            <div className="mt-4 text-xs text-gray-500">
              Chart updates every 30 seconds
            </div>
          </>
        ) : (
          <>
            <div className="text-gray-500 mb-2">Waiting for data...</div>
            <div className="animate-pulse text-sm text-gray-400">
              Connect to arbitrage API
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default RealTimeChart