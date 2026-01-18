import React, { useState } from 'react'

const ArbitrageCalculator: React.FC = () => {
  const [amount, setAmount] = useState('1000')

  return (
    <div className="p-4 border rounded-lg bg-white shadow">
      <h3 className="text-lg font-bold mb-4">💰 Калькулятор арбітражу</h3>
      <div className="space-y-3">
        <div>
          <label className="block text-sm mb-1">Сума (USD)</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="1000"
          />
        </div>
        <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          Розрахувати
        </button>
        <div className="mt-4 p-3 bg-gray-50 rounded">
          <p className="text-sm">Прибуток: <span className="font-bold">$24.50</span></p>
          <p className="text-sm">Рентабельність: <span className="text-green-600 font-bold">2.45%</span></p>
        </div>
      </div>
    </div>
  )
}

export default ArbitrageCalculator