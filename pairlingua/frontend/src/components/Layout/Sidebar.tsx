import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { 
  Home, 
  BookOpen, 
  BarChart3, 
  Trophy, 
  User, 
  Settings,
  Gamepad2,
  Brain
} from 'lucide-react';

import { RootState } from '@/store';
import { useAuth } from '@/hooks/useAuth';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const { sidebarOpen } = useSelector((state: RootState) => state.app);

  const menuItems = [
    { icon: Home, label: 'Главная', path: '/home' },
    { icon: Brain, label: 'Обучение', path: '/study' },
    { icon: BarChart3, label: 'Статистика', path: '/stats' },
    { icon: Trophy, label: 'Достижения', path: '/achievements' },
    { icon: User, label: 'Профиль', path: '/profile' },
  ];

  const isActiveRoute = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="h-full bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <Gamepad2 size={20} className="text-white" />
          </div>
          {sidebarOpen && (
            <div>
              <h1 className="text-lg font-bold text-gray-900">PairLingua</h1>
              <p className="text-xs text-gray-500">Изучение испанского</p>
            </div>
          )}
        </div>
      </div>

      {/* User info */}
      {sidebarOpen && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
              <User size={20} className="text-primary-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.nickname || 'Пользователь'}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {user?.email}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = isActiveRoute(item.path);

          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`
                w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors
                ${isActive 
                  ? 'bg-primary-100 text-primary-700 font-medium' 
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }
              `}
            >
              <Icon size={20} />
              {sidebarOpen && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className={`text-xs text-gray-500 ${sidebarOpen ? 'text-center' : 'hidden'}`}>
          PairLingua v1.0.0
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
