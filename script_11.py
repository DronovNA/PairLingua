# Создаем основные React компоненты

# Main index.tsx
index_tsx = """import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { Toaster } from 'react-hot-toast';

import './index.css';
import App from './App';
import { store } from './store';
import reportWebVitals from './utils/reportWebVitals';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#fff',
                color: '#374151',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              },
              success: {
                style: {
                  background: '#10b981',
                  color: '#fff',
                },
              },
              error: {
                style: {
                  background: '#ef4444',
                  color: '#fff',
                },
              },
            }}
          />
        </BrowserRouter>
        {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
      </QueryClientProvider>
    </Provider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
"""

# Main App.tsx
app_tsx = """import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';

import { RootState } from './store';
import { checkAuth } from './store/authSlice';
import { initializeApp } from './store/appSlice';

// Components
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/UI/LoadingSpinner';
import ErrorBoundary from './components/UI/ErrorBoundary';

// Pages
import HomePage from './pages/HomePage';
import StudyPage from './pages/StudyPage';
import ProfilePage from './pages/ProfilePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import StatsPage from './pages/StatsPage';
import AchievementsPage from './pages/AchievementsPage';
import NotFoundPage from './pages/NotFoundPage';

// Hooks
import { useAuth } from './hooks/useAuth';

const App: React.FC = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { isInitialized, isLoading: appLoading } = useSelector((state: RootState) => state.app);

  useEffect(() => {
    // Initialize app
    dispatch(initializeApp());
    
    // Check authentication on app start
    const token = localStorage.getItem('accessToken');
    if (token) {
      dispatch(checkAuth());
    }
  }, [dispatch]);

  // Show loading screen while app is initializing
  if (!isInitialized || appLoading || authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-lg text-gray-600">Загрузка PairLingua...</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* Public routes */}
          <Route 
            path="/login" 
            element={
              !isAuthenticated ? <LoginPage /> : <Navigate to="/study" replace />
            } 
          />
          <Route 
            path="/register" 
            element={
              !isAuthenticated ? <RegisterPage /> : <Navigate to="/study" replace />
            } 
          />
          
          {/* Protected routes */}
          <Route
            path="/*"
            element={
              isAuthenticated ? (
                <Layout>
                  <Routes>
                    <Route path="/" element={<Navigate to="/study" replace />} />
                    <Route path="/home" element={<HomePage />} />
                    <Route path="/study" element={<StudyPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/stats" element={<StatsPage />} />
                    <Route path="/achievements" element={<AchievementsPage />} />
                    <Route path="/404" element={<NotFoundPage />} />
                    <Route path="*" element={<Navigate to="/404" replace />} />
                  </Routes>
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </div>
    </ErrorBoundary>
  );
};

export default App;
"""

# Types definitions
types_index = """// Base types
export interface User {
  id: string;
  email: string;
  nickname?: string;
  locale: string;
  timezone: string;
  isActive: boolean;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
  profile?: UserProfile;
}

export interface UserProfile {
  userId: string;
  avatarUrl?: string;
  bio?: string;
  dailyGoal: string;
  difficultyPreference: string;
  notificationEnabled: boolean;
  settings: Record<string, any>;
}

export interface UserStats {
  totalCards: number;
  cardsDue: number;
  cardsLearned: number;
  accuracy: number;
  currentStreak: number;
  longestStreak: number;
  totalStudyTimeMinutes: number;
  lastStudyDate?: string;
  levelProgress: Record<string, number>;
  weeklyStats: Array<{
    date: string;
    reviews: number;
    correct: number;
    accuracy: number;
  }>;
}

export interface WordPair {
  id: number;
  spanishWord: string;
  russianWord: string;
  audioUrl?: string;
  cefrLevel?: string;
  frequencyRank?: number;
  tags: string[];
  examples: Array<{
    es: string;
    ru: string;
  }>;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface StudyCard {
  id: number;
  spanishWord: string;
  russianWord?: string; // Hidden for some exercise types
  audioUrl?: string;
  cefrLevel?: string;
  type: 'matching' | 'multiple_choice' | 'typing' | 'audio';
  distractors: string[];
  easeFactor: number;
  dueDate?: string;
  isNew: boolean;
  reviewCount: number;
}

export interface ReviewItem {
  wordPairId: number;
  quality: number; // 0-5 SM-2 quality score
  responseTimeMs?: number;
  source: string;
}

export interface ReviewResult {
  wordPairId: number;
  correct: boolean;
  newEaseFactor: number;
  newIntervalDays: number;
  nextReviewDate: string;
  pointsEarned: number;
}

export interface StudySession {
  sessionId: string;
  cards: StudyCard[];
  totalDue: number;
  estimatedTimeMinutes: number;
}

export interface Achievement {
  id: number;
  code: string;
  title: string;
  description: string;
  icon: string;
  category: string;
  difficulty: string;
  points: number;
  earnedAt?: string;
  contextData?: string;
}

// API Response types
export interface ApiResponse<T = any> {
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
    traceId?: string;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  nickname?: string;
  locale?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

// UI State types
export interface UIState {
  theme: 'light' | 'dark';
  language: 'ru' | 'es' | 'en';
  sidebarOpen: boolean;
  loading: boolean;
  error?: string;
}

export interface StudyState {
  currentSession?: StudySession;
  selectedCard?: StudyCard;
  selectedCards: number[];
  gameMode: 'matching' | 'multiple_choice' | 'typing';
  isSubmitting: boolean;
  score: number;
  streak: number;
  accuracy: number;
  timeElapsed: number;
}

// Form types
export interface ContactForm {
  name: string;
  email: string;
  message: string;
}

export interface PasswordChangeForm {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

// Error types
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
}

// Chart data types
export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }>;
}

// Exercise types
export type ExerciseType = 'matching' | 'multiple_choice' | 'typing' | 'audio';

export interface ExerciseResult {
  cardId: number;
  correct: boolean;
  responseTime: number;
  attempts: number;
}

// Notification types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

// Device and responsive types
export type BreakPoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

export interface DeviceInfo {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  breakpoint: BreakPoint;
}

// Search and filter types
export interface SearchFilters {
  query?: string;
  cefrLevel?: string;
  tags?: string[];
  difficulty?: string;
  category?: string;
}

export interface SortOption {
  key: string;
  label: string;
  direction: 'asc' | 'desc';
}
"""

# Auth types
auth_types = """export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  nickname?: string;
  locale?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface AuthState {
  user?: User;
  tokens?: AuthTokens;
  isAuthenticated: boolean;
  isLoading: boolean;
  error?: string;
}

export interface User {
  id: string;
  email: string;
  nickname?: string;
  locale: string;
  timezone: string;
  isActive: boolean;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
  profile?: UserProfile;
}

export interface UserProfile {
  userId: string;
  avatarUrl?: string;
  bio?: string;
  dailyGoal: string;
  difficultyPreference: string;
  notificationEnabled: boolean;
  settings: Record<string, any>;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  newPassword: string;
}
"""

# Study types
study_types = """export interface StudyCard {
  id: number;
  spanishWord: string;
  russianWord?: string;
  audioUrl?: string;
  cefrLevel?: string;
  type: ExerciseType;
  distractors: string[];
  easeFactor: number;
  dueDate?: string;
  isNew: boolean;
  reviewCount: number;
}

export interface StudySession {
  sessionId: string;
  cards: StudyCard[];
  totalDue: number;
  estimatedTimeMinutes: number;
}

export interface ReviewItem {
  wordPairId: number;
  quality: number;
  responseTimeMs?: number;
  source: string;
}

export interface ReviewBatch {
  items: ReviewItem[];
  sessionId?: string;
}

export interface ReviewResult {
  wordPairId: number;
  correct: boolean;
  newEaseFactor: number;
  newIntervalDays: number;
  nextReviewDate: string;
  pointsEarned: number;
}

export interface ReviewBatchResponse {
  results: ReviewResult[];
  totalPointsEarned: number;
  accuracy: number;
  streakUpdated: boolean;
  achievementsUnlocked: string[];
}

export type ExerciseType = 'matching' | 'multiple_choice' | 'typing' | 'audio';

export interface StudyState {
  currentSession?: StudySession;
  selectedCard?: StudyCard;
  selectedCards: number[];
  gameMode: ExerciseType;
  isSubmitting: boolean;
  score: number;
  streak: number;
  accuracy: number;
  timeElapsed: number;
  cardsCompleted: number;
  errors: number;
}

export interface StudySettings {
  exerciseTypes: ExerciseType[];
  cefrLevels: string[];
  cardsPerSession: number;
  includeNew: boolean;
  audioEnabled: boolean;
  showHints: boolean;
}
"""

# API Service
api_service = """import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

import { AuthTokens, ApiResponse } from '@/types';
import { store } from '@/store';
import { logout, refreshTokens } from '@/store/authSlice';

class ApiService {
  private api: AxiosInstance;
  private isRefreshing = false;
  private refreshSubscribers: Array<(token: string) => void> = [];

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for handling errors and token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // If already refreshing, wait for it to complete
            return new Promise((resolve) => {
              this.refreshSubscribers.push((token: string) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                resolve(this.api(originalRequest));
              });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (!refreshToken) {
              throw new Error('No refresh token');
            }

            const response = await this.api.post('/auth/refresh', {
              refreshToken,
            });

            const tokens: AuthTokens = response.data;
            
            localStorage.setItem('accessToken', tokens.accessToken);
            localStorage.setItem('refreshToken', tokens.refreshToken);
            
            store.dispatch(refreshTokens(tokens));

            // Retry all queued requests
            this.refreshSubscribers.forEach((callback) => {
              callback(tokens.accessToken);
            });
            this.refreshSubscribers = [];

            originalRequest.headers.Authorization = `Bearer ${tokens.accessToken}`;
            return this.api(originalRequest);
          } catch (refreshError) {
            // Refresh failed, logout user
            store.dispatch(logout());
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            
            toast.error('Сессия истекла. Войдите в систему заново.');
            window.location.href = '/login';
            
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        // Handle other errors
        if (error.response) {
          const errorMessage = error.response.data?.error?.message || 'Произошла ошибка';
          
          if (error.response.status >= 500) {
            toast.error('Ошибка сервера. Попробуйте позже.');
          } else if (error.response.status >= 400) {
            toast.error(errorMessage);
          }
        } else if (error.request) {
          toast.error('Нет подключения к серверу');
        }

        return Promise.reject(error);
      }
    );
  }

  // Generic request method
  private async request<T>(config: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api(config);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // HTTP Methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ method: 'GET', url, ...config });
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ method: 'POST', url, data, ...config });
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ method: 'PUT', url, data, ...config });
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ method: 'PATCH', url, data, ...config });
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ method: 'DELETE', url, ...config });
  }

  // Utility methods
  setAuthToken(token: string) {
    this.api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  removeAuthToken() {
    delete this.api.defaults.headers.common['Authorization'];
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.get('/health');
  }
}

export const apiService = new ApiService();
export default apiService;
"""

# Записываем React файлы
with open("pairlingua/frontend/src/index.tsx", "w") as f:
    f.write(index_tsx)

with open("pairlingua/frontend/src/App.tsx", "w") as f:
    f.write(app_tsx)

with open("pairlingua/frontend/src/types/index.ts", "w") as f:
    f.write(types_index)

with open("pairlingua/frontend/src/types/auth.ts", "w") as f:
    f.write(auth_types)

with open("pairlingua/frontend/src/types/study.ts", "w") as f:
    f.write(study_types)

with open("pairlingua/frontend/src/services/api.ts", "w") as f:
    f.write(api_service)

print("✅ Основные React файлы созданы")
print("⚛️ App.tsx с роутингом и защищёнными маршрутами")
print("📝 TypeScript типы для всех сущностей")
print("🌐 API сервис с автообновлением токенов")
print("🔒 Interceptors для аутентификации")