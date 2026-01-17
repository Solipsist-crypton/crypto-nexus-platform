import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/arbitrage', label: '🔍 Арбітраж', description: 'Моніторинг арбітражних можливостей' },
    { path: '/futures', label: '📈 Ф\'ючерсні сигнали', description: 'AI-генеровані торгові сигнали', comingSoon: true },
    { path: '/airdrops', label: '🎁 Airdrop Farming', description: 'Копітрейдинг та фармінг', comingSoon: true },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-900">🚀 Crypto Nexus</h1>
          <p className="text-sm text-gray-600 mt-1">Комплексна криптоплатформа</p>
        </div>
        
        <nav className="mt-6">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.comingSoon ? '#' : item.path}
                className={`flex items-center px-6 py-3 text-sm font-medium ${
                  isActive
                    ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600'
                    : 'text-gray-700 hover:bg-gray-50'
                } ${item.comingSoon ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="flex-1">
                  <div className="flex items-center">
                    <span className="mr-3">{item.label.split(' ')[0]}</span>
                    <span>{item.label.split(' ').slice(1).join(' ')}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{item.description}</p>
                </div>
                {item.comingSoon && (
                  <span className="ml-2 px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                    Скоро
                  </span>
                )}
                {isActive && (
                  <div className="ml-2 w-2 h-2 bg-blue-600 rounded-full"></div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Статус бекенду */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Статус бекенду</span>
            <span className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              <span className="text-sm text-green-600">Онлайн</span>
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        <header className="bg-white shadow-sm">
          <div className="px-8 py-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-800">
                {navItems.find(item => item.path === location.pathname)?.label || 'Панель управління'}
              </h2>
              <div className="flex items-center space-x-4">
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Оновити дані
                </button>
                <span className="text-sm text-gray-500">
                  Оновлено: {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>
        </header>

        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;