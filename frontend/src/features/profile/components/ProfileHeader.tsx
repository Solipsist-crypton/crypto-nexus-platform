// frontend/src/features/profile/components/ProfileHeader.tsx
import React from 'react';
import { Bell, Settings, RefreshCw, TrendingUp } from 'lucide-react';

interface ProfileHeaderProps {
  user: {
    name: string;
    avatar?: string;
    joinDate: string;
    tier: 'free' | 'pro' | 'elite';
  };
  onRefresh: () => void;
}

const ProfileHeader: React.FC<ProfileHeaderProps> = ({ user, onRefresh }) => {
  const tierColors = {
    free: 'text-gray-400 bg-gray-800',
    pro: 'text-blue-400 bg-blue-900/30',
    elite: 'text-yellow-400 bg-yellow-900/30'
  };

  const tierLabels = {
    free: 'Free',
    pro: 'Pro',
    elite: 'Elite'
  };

  return (
    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
      {/* User Info */}
      <div className="flex items-center gap-4">
        <div className="relative">
          <div className="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-2xl font-bold">
            {user.avatar ? (
              <img src={user.avatar} alt={user.name} className="w-full h-full rounded-full" />
            ) : (
              user.name.charAt(0).toUpperCase()
            )}
          </div>
          <div className={`absolute -bottom-1 -right-1 px-2 py-1 rounded-full text-xs font-bold ${tierColors[user.tier]}`}>
            {tierLabels[user.tier]}
          </div>
        </div>
        
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">{user.name}</h1>
          <div className="flex items-center gap-2 text-gray-400">
            <TrendingUp className="w-4 h-4" />
            <span>Трейдер з {user.joinDate}</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="hidden sm:inline">Оновити</span>
        </button>
        
        <button className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors relative">
          <Bell className="w-5 h-5" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
        </button>
        
        <button className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default ProfileHeader;