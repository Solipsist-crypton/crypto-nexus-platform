import React from 'react'

const Loader: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-gray-300 rounded-full"></div>
        <div className="absolute top-0 left-0 w-16 h-16 border-4 border-blue-600 rounded-full animate-spin border-t-transparent"></div>
      </div>
      <p className="mt-4 text-gray-600 font-medium">Завантаження даних...</p>
      <p className="text-sm text-gray-500 mt-1">Звертаємось до API арбітражу</p>
    </div>
  )
}

export default Loader