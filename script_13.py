# Создаем основные UI компоненты и страницы

# Layout component
layout_component = """import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Outlet } from 'react-router-dom';

import { RootState } from '@/store';
import { setSidebarOpen, updateDeviceInfo } from '@/store/appSlice';
import Header from './Header';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const dispatch = useDispatch();
  const { sidebarOpen, deviceInfo } = useSelector((state: RootState) => state.app);

  useEffect(() => {
    const handleResize = () => {
      dispatch(updateDeviceInfo());
      
      // Auto-close sidebar on mobile when window is resized
      if (deviceInfo.isMobile && sidebarOpen) {
        dispatch(setSidebarOpen(false));
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [dispatch, deviceInfo.isMobile, sidebarOpen]);

  // Close sidebar when clicking outside on mobile
  const handleBackdropClick = () => {
    if (deviceInfo.isMobile && sidebarOpen) {
      dispatch(setSidebarOpen(false));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`
        ${deviceInfo.isMobile 
          ? `fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out ${
              sidebarOpen ? 'translate-x-0' : '-translate-x-full'
            }`
          : `relative ${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300`
        }
      `}>
        <Sidebar />
      </div>

      {/* Mobile backdrop */}
      {deviceInfo.isMobile && sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity"
          onClick={handleBackdropClick}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
"""

# Header component
header_component = """import React from 'react';
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
"""

# Sidebar component
sidebar_component = """import React from 'react';
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
"""

# LoadingSpinner component
loading_spinner = """import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'white' | 'gray';
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium', 
  color = 'primary',
  className = ''
}) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  };

  const colorClasses = {
    primary: 'border-primary-200 border-t-primary-600',
    white: 'border-white/20 border-t-white',
    gray: 'border-gray-200 border-t-gray-600'
  };

  return (
    <div 
      className={`
        ${sizeClasses[size]} 
        ${colorClasses[color]} 
        border-2 border-solid rounded-full animate-spin
        ${className}
      `}
    />
  );
};

export default LoadingSpinner;
"""

# StudyPage component
study_page = """import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, RefreshCw, Settings, BarChart3 } from 'lucide-react';

import { useStudy } from '@/hooks/useStudy';
import { useAuth } from '@/hooks/useAuth';
import LoadingSpinner from '@/components/UI/LoadingSpinner';
import GameBoard from '@/components/Study/GameBoard';
import MatchingExercise from '@/components/Study/MatchingExercise';

const StudyPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { 
    currentSession, 
    isSubmitting, 
    gameMode, 
    score, 
    streak, 
    accuracy,
    loadDueCards,
    changeGameMode,
    resetStudySession
  } = useStudy();

  const [isInitialLoading, setIsInitialLoading] = useState(true);

  useEffect(() => {
    const initializeStudy = async () => {
      setIsInitialLoading(true);
      try {
        await loadDueCards({ limit: 5, includeNew: true });
      } finally {
        setIsInitialLoading(false);
      }
    };

    initializeStudy();
  }, [loadDueCards]);

  const handleStartNewSession = async () => {
    resetStudySession();
    await loadDueCards({ limit: 5, includeNew: true });
  };

  const handleGameModeChange = (mode: 'matching' | 'multiple_choice' | 'typing') => {
    changeGameMode(mode);
  };

  if (isInitialLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-96">
        <LoadingSpinner size="large" />
        <p className="mt-4 text-lg text-gray-600">Загружаем карточки для изучения...</p>
      </div>
    );
  }

  if (!currentSession || currentSession.cards.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Play size={32} className="text-primary-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Отличная работа!
        </h2>
        <p className="text-gray-600 mb-8 max-w-md mx-auto">
          У вас нет карточек для повторения. Возвращайтесь завтра или начните новую сессию.
        </p>
        <div className="space-x-4">
          <button
            onClick={handleStartNewSession}
            className="btn-primary inline-flex items-center space-x-2"
          >
            <RefreshCw size={16} />
            <span>Новая сессия</span>
          </button>
          <button
            onClick={() => navigate('/stats')}
            className="btn-secondary inline-flex items-center space-x-2"
          >
            <BarChart3 size={16} />
            <span>Статистика</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Обучение
          </h1>
          <p className="text-gray-600 mt-1">
            Изучайте новые слова и повторяйте изученные
          </p>
        </div>
        <div className="flex items-center space-x-4 mt-4 sm:mt-0">
          <button
            onClick={() => navigate('/stats')}
            className="btn-secondary inline-flex items-center space-x-2"
          >
            <BarChart3 size={16} />
            <span className="hidden sm:inline">Статистика</span>
          </button>
          <button className="btn-secondary inline-flex items-center space-x-2">
            <Settings size={16} />
            <span className="hidden sm:inline">Настройки</span>
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-primary-600">{score}</div>
          <div className="text-sm text-gray-600">Очки</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-success-600">{streak}</div>
          <div className="text-sm text-gray-600">Серия</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-secondary-600">{accuracy.toFixed(1)}%</div>
          <div className="text-sm text-gray-600">Точность</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">{currentSession.cards.length}</div>
          <div className="text-sm text-gray-600">Осталось</div>
        </div>
      </div>

      {/* Game Mode Selector */}
      <div className="flex space-x-2">
        {[
          { mode: 'matching', label: 'Сопоставление' },
          { mode: 'multiple_choice', label: 'Выбор' },
          { mode: 'typing', label: 'Ввод' },
        ].map(({ mode, label }) => (
          <button
            key={mode}
            onClick={() => handleGameModeChange(mode as any)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              gameMode === mode
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Game Area */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        {gameMode === 'matching' ? (
          <MatchingExercise />
        ) : (
          <GameBoard />
        )}
      </div>

      {/* Progress */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Прогресс сессии</span>
          <span className="text-sm text-gray-500">
            {currentSession.totalDue - currentSession.cards.length} из {currentSession.totalDue}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ 
              width: `${((currentSession.totalDue - currentSession.cards.length) / currentSession.totalDue) * 100}%` 
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default StudyPage;
"""

# LoginPage component
login_page = """import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useDispatch } from 'react-redux';
import { Eye, EyeOff, Mail, Lock, Gamepad2 } from 'lucide-react';
import toast from 'react-hot-toast';

import { loginUser } from '@/store/authSlice';
import { AppDispatch } from '@/store';
import { LoginCredentials } from '@/types/auth';
import LoadingSpinner from '@/components/UI/LoadingSpinner';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginCredentials>();

  const onSubmit = async (data: LoginCredentials) => {
    setIsLoading(true);
    
    try {
      const result = await dispatch(loginUser(data));
      
      if (loginUser.fulfilled.match(result)) {
        toast.success('Добро пожаловать в PairLingua!');
        navigate('/study');
      } else {
        toast.error(result.payload as string || 'Ошибка входа');
      }
    } catch (error) {
      toast.error('Произошла ошибка при входе');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
            <Gamepad2 size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">PairLingua</h1>
          <p className="text-gray-600 mt-2">Изучение испанского языка</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Вход в систему</h2>
            <p className="text-gray-600 mt-1">Войдите в свой аккаунт</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input
                  {...register('email', {
                    required: 'Email обязателен',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Некорректный email'
                    }
                  })}
                  type="email"
                  placeholder="your@email.com"
                  className={`input-field pl-10 ${errors.email ? 'input-error' : ''}`}
                />
              </div>
              {errors.email && (
                <p className="text-error-600 text-sm mt-1">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Пароль
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input
                  {...register('password', {
                    required: 'Пароль обязателен',
                    minLength: {
                      value: 6,
                      message: 'Пароль должен содержать минимум 6 символов'
                    }
                  })}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Ваш пароль"
                  className={`input-field pl-10 pr-10 ${errors.password ? 'input-error' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && (
                <p className="text-error-600 text-sm mt-1">{errors.password.message}</p>
              )}
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                <span className="ml-2 text-sm text-gray-600">Запомнить меня</span>
              </label>
              <Link to="/forgot-password" className="text-sm text-primary-600 hover:text-primary-500">
                Забыли пароль?
              </Link>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary py-3 text-base font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <LoadingSpinner size="small" color="white" />
                  <span>Вход...</span>
                </div>
              ) : (
                'Войти'
              )}
            </button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Нет аккаунта?{' '}
              <Link to="/register" className="text-primary-600 hover:text-primary-500 font-medium">
                Зарегистрироваться
              </Link>
            </p>
          </div>
        </div>

        {/* Demo Account */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Демо-аккаунт: demo@pairlingua.com / demo123
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
"""

# Записываем компоненты
with open("pairlingua/frontend/src/components/Layout/Layout.tsx", "w") as f:
    f.write(layout_component)

with open("pairlingua/frontend/src/components/Layout/Header.tsx", "w") as f:
    f.write(header_component)

with open("pairlingua/frontend/src/components/Layout/Sidebar.tsx", "w") as f:
    f.write(sidebar_component)

with open("pairlingua/frontend/src/components/UI/LoadingSpinner.tsx", "w") as f:
    f.write(loading_spinner)

with open("pairlingua/frontend/src/pages/StudyPage.tsx", "w") as f:
    f.write(study_page)

with open("pairlingua/frontend/src/pages/LoginPage.tsx", "w") as f:
    f.write(login_page)

print("✅ UI компоненты созданы")
print("🏗️ Layout с адаптивной боковой панелью")
print("📱 Responsive дизайн для мобильных устройств")
print("🔐 Страница входа с валидацией форм")
print("🎯 Страница обучения с игровыми элементами")