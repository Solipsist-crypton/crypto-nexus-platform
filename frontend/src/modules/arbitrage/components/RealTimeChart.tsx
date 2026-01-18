import React from 'react'

interface RealTimeChartProps {
  data?: any[]
}

const RealTimeChart: React.FC<RealTimeChartProps> = ({ data }) => {
  return (
    <div className="p-4 border rounded-lg bg-white shadow">
      <h3 className="text-lg font-bold mb-4">📈 Графік арбітражу</h3>
      <div className="h-48 flex items-center justify-center bg-gray-50 rounded">
        <div className="text-center">
          <div className="text-gray-500 mb-2">Графік у реальному часі</div>
          <div className="text-sm text-gray-400">Дані оновлюються кожні 30 секунд</div>
        </div>
      </div>
      <div className="mt-4 flex justify-between text-sm">
        <span className="text-green-600">▲ Макс: $145.20</span>
        <span className="text-gray-500">Середнє: $89.40</span>
        <span className="text-red-600">▼ Мін: $32.10</span>
      </div>
    </div>
  )
}

export default RealTimeChart