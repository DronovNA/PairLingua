import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Menu, Search, Bell, User, LogOut, Settings, BarChart3 } from 'lucide-react';

import { RootState } from '@/store';
import { toggleSidebar } from '@/store/appSlice';
import { logoutUser } from '@/store/authSlice';
import { useAuth } from '@/hooks/useAuth';

const Header: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { deviceInfo } = useSelector((state: RootState) => state.app);

  const handleLogout = () => {
    dispatch(logoutUser());
    navigate('/login');
  };

  const handleMenuToggle = () => {
    dispatch(toggleSidebar());
  };

  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
      <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          <button
            onClick={handleMenuToggle}
            className="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <Menu size={20} />
          </button>

          {!deviceInfo.isMobile && (
            <div className="hidden sm:flex items-center space-x-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input
                  type="text"
                  placeholder="Поиск слов..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-64"
                />
              </div>
            </div>
          )}
        </div>

        {/* Center - Logo/Title */}
        <div className="flex-1 flex justify-center sm:justify-start">
          <h1 className="text-xl font-bold text-primary-600 sm:hidden">
            PairLingua
          </h1>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-2 sm:space-x-4">
          {/* Notifications */}
          <button className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell size={20} />
            <span className="absolute top-1 right-1 block h-2 w-2 bg-red-500 rounded-full"></span>
          </button>

          {/* Stats quick view */}
          <button 
            onClick={() => navigate('/stats')}
            className="hidden sm:flex items-center space-x-2 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <BarChart3 size={20} />
            <span className="text-sm">Статистика</span>
          </button>

          {/* User menu */}
          <div className="relative group">
            <button className="flex items-center space-x-2 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <User size={16} className="text-primary-600" />
              </div>
              {!deviceInfo.isMobile && (
                <span className="text-sm font-medium text-gray-700">
                  {user?.nickname || user?.email?.split('@')[0]}
                </span>
              )}
            </button>

            {/* Dropdown menu */}
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
              <div className="py-2">
                <button
                  onClick={() => navigate('/profile')}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <Settings size={16} />
                  <span>Профиль</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-left text-red-600 hover:bg-red-50 transition-colors"
                >
                  <LogOut size={16} />
                  <span>Выйти</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
