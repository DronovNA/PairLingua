# Создаем недостающие директории и файлы
import os

# Создаем недостающие директории
pages_dir = "pairlingua/frontend/src/pages"
os.makedirs(pages_dir, exist_ok=True)

# Также создадим остальные компонентные директории
component_dirs = [
    "pairlingua/frontend/src/components/Layout",
    "pairlingua/frontend/src/components/UI", 
    "pairlingua/frontend/src/components/Auth",
    "pairlingua/frontend/src/components/Study",
    "pairlingua/frontend/src/components/Profile"
]

for dir_path in component_dirs:
    os.makedirs(dir_path, exist_ok=True)

# Теперь записываем компоненты
layout_component = """import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';

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
      
      if (deviceInfo.isMobile && sidebarOpen) {
        dispatch(setSidebarOpen(false));
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [dispatch, deviceInfo.isMobile, sidebarOpen]);

  const handleBackdropClick = () => {
    if (deviceInfo.isMobile && sidebarOpen) {
      dispatch(setSidebarOpen(false));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
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

      {deviceInfo.isMobile && sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity"
          onClick={handleBackdropClick}
        />
      )}

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

header_component = """import React from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';

import { toggleSidebar } from '@/store/appSlice';
import { logoutUser } from '@/store/authSlice';
import { useAuth } from '@/hooks/useAuth';

const Header: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useAuth();

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
        <div className="flex items-center space-x-4">
          <button
            onClick={handleMenuToggle}
            className="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          >
            ☰
          </button>
        </div>

        <div className="flex-1 flex justify-center sm:justify-start">
          <h1 className="text-xl font-bold text-primary-600 sm:hidden">
            PairLingua
          </h1>
        </div>

        <div className="flex items-center space-x-2 sm:space-x-4">
          <button className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
            🔔
            <span className="absolute top-1 right-1 block h-2 w-2 bg-red-500 rounded-full"></span>
          </button>

          <div className="relative group">
            <button className="flex items-center space-x-2 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                👤
              </div>
              <span className="text-sm font-medium text-gray-700 hidden sm:block">
                {user?.nickname || user?.email?.split('@')[0]}
              </span>
            </button>

            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
              <div className="py-2">
                <button
                  onClick={() => navigate('/profile')}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  ⚙️ <span>Профиль</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-left text-red-600 hover:bg-red-50 transition-colors"
                >
                  🚪 <span>Выйти</span>
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

sidebar_component = """import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

import { RootState } from '@/store';
import { useAuth } from '@/hooks/useAuth';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const { sidebarOpen } = useSelector((state: RootState) => state.app);

  const menuItems = [
    { icon: '🏠', label: 'Главная', path: '/home' },
    { icon: '🧠', label: 'Обучение', path: '/study' },
    { icon: '📊', label: 'Статистика', path: '/stats' },
    { icon: '🏆', label: 'Достижения', path: '/achievements' },
    { icon: '👤', label: 'Профиль', path: '/profile' },
  ];

  const isActiveRoute = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="h-full bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            🎮
          </div>
          {sidebarOpen && (
            <div>
              <h1 className="text-lg font-bold text-gray-900">PairLingua</h1>
              <p className="text-xs text-gray-500">Изучение испанского</p>
            </div>
          )}
        </div>
      </div>

      {sidebarOpen && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
              👤
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

      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
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
              <span>{item.icon}</span>
              {sidebarOpen && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>

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

# Простые страницы-заглушки для тестирования
study_page = """import React, { useEffect, useState } from 'react';
import { useStudy } from '@/hooks/useStudy';
import LoadingSpinner from '@/components/UI/LoadingSpinner';

const StudyPage: React.FC = () => {
  const { 
    currentSession, 
    isSubmitting, 
    score, 
    streak, 
    accuracy,
    loadDueCards
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

  if (isInitialLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-96">
        <LoadingSpinner size="large" />
        <p className="mt-4 text-lg text-gray-600">Загружаем карточки для изучения...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Обучение</h1>
          <p className="text-gray-600 mt-1">Изучайте новые слова и повторяйте изученные</p>
        </div>
      </div>

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
          <div className="text-2xl font-bold text-gray-900">{currentSession?.cards.length || 0}</div>
          <div className="text-sm text-gray-600">Осталось</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-xl font-semibold mb-4">Игровая область</h2>
        {currentSession?.cards.length ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {currentSession.cards.slice(0, 4).map((card) => (
              <div key={card.id} className="p-4 border border-gray-200 rounded-lg">
                <div className="text-lg font-medium text-gray-900">{card.spanishWord}</div>
                <div className="text-gray-600">{card.russianWord}</div>
                <div className="text-xs text-gray-500 mt-2">{card.cefrLevel}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">Нет карточек для изучения</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudyPage;
"""

login_page = """import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useDispatch } from 'react-redux';
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
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
            🎮
          </div>
          <h1 className="text-3xl font-bold text-gray-900">PairLingua</h1>
          <p className="text-gray-600 mt-2">Изучение испанского языка</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Вход в систему</h2>
            <p className="text-gray-600 mt-1">Войдите в свой аккаунт</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <input
                  {...register('email', {
                    required: 'Email обязателен',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}$/i,
                      message: 'Некорректный email'
                    }
                  })}
                  type="email"
                  placeholder="your@email.com"
                  className={`input-field ${errors.email ? 'input-error' : ''}`}
                />
              </div>
              {errors.email && (
                <p className="text-error-600 text-sm mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Пароль
              </label>
              <div className="relative">
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
                  className={`input-field ${errors.password ? 'input-error' : ''}`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
              {errors.password && (
                <p className="text-error-600 text-sm mt-1">{errors.password.message}</p>
              )}
            </div>

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

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Нет аккаунта?{' '}
              <Link to="/register" className="text-primary-600 hover:text-primary-500 font-medium">
                Зарегистрироваться
              </Link>
            </p>
          </div>
        </div>

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

# Остальные простые страницы
register_page = """import React from 'react';
import { Link } from 'react-router-dom';

const RegisterPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Регистрация</h1>
          <p className="text-gray-600 mt-2">Создайте новый аккаунт</p>
        </div>
        
        <div className="text-center">
          <p className="text-gray-600">Страница в разработке</p>
          <Link to="/login" className="text-primary-600 hover:text-primary-500 font-medium">
            Вернуться к входу
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
"""

other_pages = """import React from 'react';

export const HomePage: React.FC = () => (
  <div className="text-center py-12">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Добро пожаловать в PairLingua!</h1>
    <p className="text-gray-600">Страница в разработке</p>
  </div>
);

export const ProfilePage: React.FC = () => (
  <div className="text-center py-12">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Профиль</h1>
    <p className="text-gray-600">Страница в разработке</p>
  </div>
);

export const StatsPage: React.FC = () => (
  <div className="text-center py-12">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Статистика</h1>
    <p className="text-gray-600">Страница в разработке</p>
  </div>
);

export const AchievementsPage: React.FC = () => (
  <div className="text-center py-12">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Достижения</h1>
    <p className="text-gray-600">Страница в разработке</p>
  </div>
);

export const NotFoundPage: React.FC = () => (
  <div className="text-center py-12">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">404 - Страница не найдена</h1>
    <p className="text-gray-600">Запрашиваемая страница не существует</p>
  </div>
);
"""

# Записываем все компоненты
with open("pairlingua/frontend/src/components/Layout/Layout.tsx", "w") as f:
    f.write(layout_component)

with open("pairlingua/frontend/src/components/Layout/Header.tsx", "w", encoding="utf-8") as f:
    f.write(header_component)

with open("pairlingua/frontend/src/components/Layout/Sidebar.tsx", "w", encoding="utf-8") as f:
    f.write(sidebar_component)

with open("pairlingua/frontend/src/components/UI/LoadingSpinner.tsx", "w") as f:
    f.write(loading_spinner)

with open("pairlingua/frontend/src/pages/StudyPage.tsx", "w") as f:
    f.write(study_page)

with open("pairlingua/frontend/src/pages/LoginPage.tsx", "w", encoding="utf-8") as f:
    f.write(login_page)

with open("pairlingua/frontend/src/pages/RegisterPage.tsx", "w") as f:
    f.write(register_page)

# Записываем остальные страницы в один файл, затем разделим
with open("pairlingua/frontend/src/pages/index.ts", "w") as f:
    f.write(other_pages)

# Создаем отдельные файлы для каждой страницы
page_components = [
    ("HomePage", "export const HomePage"),
    ("ProfilePage", "export const ProfilePage"), 
    ("StatsPage", "export const StatsPage"),
    ("AchievementsPage", "export const AchievementsPage"),
    ("NotFoundPage", "export const NotFoundPage")
]

for name, export_line in page_components:
    content = other_pages.split(f"{export_line}")[1].split("export const")[0].strip()
    if content.startswith(":"):
        content = content[1:].strip()
    
    page_content = f"""import React from 'react';

const {name}: React.FC = () => {content}

export default {name};
"""
    
    with open(f"pairlingua/frontend/src/pages/{name}.tsx", "w") as f:
        f.write(page_content)

print("✅ Frontend компоненты и страницы созданы")
print("🏗️ Layout с Header и Sidebar")
print("📱 Responsive компоненты") 
print("🔐 Страницы Login/Register")
print("🎯 Базовая структура всех основных страниц")