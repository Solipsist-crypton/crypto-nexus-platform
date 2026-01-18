import React from 'react'

const Loader: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="relative">
        <div className="w-12 h-12 border-4 border-gray-200 rounded-full"></div>
        <div className="absolute top-0 left-0 w-12 h-12 border-4 border-blue-500 rounded-full 
                       animate-spin border-t-transparent"></div>
      </div>
      <p className="mt-4 text-gray-700 font-medium">Loading arbitrage data</p>
      <p className="text-sm text-gray-500 mt-1">Fetching from backend API...</p>
      <div className="mt-2 text-xs text-gray-400">
        If this takes too long, check backend connection
      </div>
    </div>
  );
};

export default Loader