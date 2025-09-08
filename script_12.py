# Создаем Redux store и хуки

# Main store
store_index = """import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

import authSlice from './authSlice';
import studySlice from './studySlice';
import appSlice from './appSlice';
import userSlice from './userSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    study: studySlice,
    app: appSlice,
    user: userSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
"""

# Auth slice
auth_slice = """import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { toast } from 'react-hot-toast';

import { AuthState, AuthTokens, LoginCredentials, RegisterData, User } from '@/types/auth';
import apiService from '@/services/api';

const initialState: AuthState = {
  user: undefined,
  tokens: undefined,
  isAuthenticated: false,
  isLoading: false,
  error: undefined,
};

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await apiService.post<AuthTokens>('/auth/login', credentials);
      
      // Store tokens
      localStorage.setItem('accessToken', response.accessToken);
      localStorage.setItem('refreshToken', response.refreshToken);
      
      // Set auth header
      apiService.setAuthToken(response.accessToken);
      
      // Fetch user data
      const userResponse = await apiService.get<User>('/users/me');
      
      return { tokens: response, user: userResponse };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error?.message || 'Login failed');
    }
  }
);

export const registerUser = createAsyncThunk(
  'auth/register',
  async (userData: RegisterData, { rejectWithValue }) => {
    try {
      const response = await apiService.post<AuthTokens>('/auth/register', userData);
      
      // Store tokens
      localStorage.setItem('accessToken', response.accessToken);
      localStorage.setItem('refreshToken', response.refreshToken);
      
      // Set auth header
      apiService.setAuthToken(response.accessToken);
      
      // Fetch user data
      const userResponse = await apiService.get<User>('/users/me');
      
      toast.success('Регистрация успешна! Добро пожаловать в PairLingua!');
      
      return { tokens: response, user: userResponse };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error?.message || 'Registration failed');
    }
  }
);

export const checkAuth = createAsyncThunk(
  'auth/checkAuth',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        throw new Error('No token found');
      }
      
      apiService.setAuthToken(token);
      const userResponse = await apiService.get<User>('/users/me');
      
      return userResponse;
    } catch (error: any) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      apiService.removeAuthToken();
      return rejectWithValue('Authentication check failed');
    }
  }
);

export const logoutUser = createAsyncThunk(
  'auth/logout',
  async (_, { getState }) => {
    try {
      const { auth } = getState() as { auth: AuthState };
      
      if (auth.tokens) {
        await apiService.post('/auth/logout', {
          refreshToken: auth.tokens.refreshToken,
        });
      }
    } catch (error) {
      // Ignore logout errors, still proceed with client-side logout
      console.warn('Logout request failed:', error);
    } finally {
      // Clean up client-side
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      apiService.removeAuthToken();
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = undefined;
      state.tokens = undefined;
      state.isAuthenticated = false;
      state.isLoading = false;
      state.error = undefined;
      
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      apiService.removeAuthToken();
    },
    refreshTokens: (state, action: PayloadAction<AuthTokens>) => {
      state.tokens = action.payload;
    },
    clearError: (state) => {
      state.error = undefined;
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = undefined;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.tokens = action.payload.tokens;
        state.isAuthenticated = true;
        state.error = undefined;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      });

    // Register
    builder
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = undefined;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.tokens = action.payload.tokens;
        state.isAuthenticated = true;
        state.error = undefined;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      });

    // Check auth
    builder
      .addCase(checkAuth.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(checkAuth.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = undefined;
      })
      .addCase(checkAuth.rejected, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = undefined;
        state.tokens = undefined;
      });

    // Logout
    builder.addCase(logoutUser.fulfilled, (state) => {
      state.user = undefined;
      state.tokens = undefined;
      state.isAuthenticated = false;
      state.isLoading = false;
      state.error = undefined;
    });
  },
});

export const { logout, refreshTokens, clearError, updateUser } = authSlice.actions;
export default authSlice.reducer;
"""

# Study slice
study_slice = """import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { toast } from 'react-hot-toast';

import { StudyState, StudySession, ReviewBatch, ReviewBatchResponse, StudyCard, ExerciseType } from '@/types/study';
import apiService from '@/services/api';

const initialState: StudyState = {
  currentSession: undefined,
  selectedCard: undefined,
  selectedCards: [],
  gameMode: 'matching',
  isSubmitting: false,
  score: 0,
  streak: 0,
  accuracy: 0,
  timeElapsed: 0,
  cardsCompleted: 0,
  errors: 0,
};

// Async thunks
export const fetchDueCards = createAsyncThunk(
  'study/fetchDueCards',
  async (params: { limit?: number; includeNew?: boolean; exerciseTypes?: ExerciseType[]; cefrLevels?: string[] }, { rejectWithValue }) => {
    try {
      const queryParams = new URLSearchParams();
      
      if (params.limit) queryParams.append('limit', params.limit.toString());
      if (params.includeNew !== undefined) queryParams.append('include_new', params.includeNew.toString());
      if (params.exerciseTypes?.length) {
        params.exerciseTypes.forEach(type => queryParams.append('exercise_types', type));
      }
      if (params.cefrLevels?.length) {
        params.cefrLevels.forEach(level => queryParams.append('cefr_levels', level));
      }
      
      const response = await apiService.get<StudySession>(`/study/cards/due?${queryParams.toString()}`);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error?.message || 'Failed to fetch cards');
    }
  }
);

export const submitReviews = createAsyncThunk(
  'study/submitReviews',
  async (reviewBatch: ReviewBatch, { rejectWithValue }) => {
    try {
      const response = await apiService.post<ReviewBatchResponse>('/study/cards/review', reviewBatch);
      
      // Show success message with points earned
      if (response.totalPointsEarned > 0) {
        toast.success(`+${response.totalPointsEarned} очков! Точность: ${response.accuracy.toFixed(1)}%`);
      }
      
      // Show achievements
      if (response.achievementsUnlocked.length > 0) {
        response.achievementsUnlocked.forEach(achievement => {
          toast.success(`🏆 Достижение разблокировано: ${achievement}`, { duration: 5000 });
        });
      }
      
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error?.message || 'Failed to submit reviews');
    }
  }
);

export const replaceCard = createAsyncThunk(
  'study/replaceCard',
  async (params: { sessionId: string; completedWordPairId: number }, { rejectWithValue }) => {
    try {
      const response = await apiService.post(`/study/session/replace`, params);
      return response.newCard as StudyCard;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error?.message || 'Failed to replace card');
    }
  }
);

const studySlice = createSlice({
  name: 'study',
  initialState,
  reducers: {
    setGameMode: (state, action: PayloadAction<ExerciseType>) => {
      state.gameMode = action.payload;
    },
    selectCard: (state, action: PayloadAction<StudyCard>) => {
      state.selectedCard = action.payload;
    },
    toggleCardSelection: (state, action: PayloadAction<number>) => {
      const cardId = action.payload;
      const index = state.selectedCards.indexOf(cardId);
      
      if (index >= 0) {
        state.selectedCards.splice(index, 1);
      } else {
        state.selectedCards.push(cardId);
      }
    },
    clearCardSelection: (state) => {
      state.selectedCards = [];
      state.selectedCard = undefined;
    },
    incrementScore: (state, action: PayloadAction<number>) => {
      state.score += action.payload;
    },
    incrementStreak: (state) => {
      state.streak += 1;
    },
    resetStreak: (state) => {
      state.streak = 0;
    },
    incrementTimeElapsed: (state, action: PayloadAction<number>) => {
      state.timeElapsed += action.payload;
    },
    incrementCardsCompleted: (state) => {
      state.cardsCompleted += 1;
    },
    incrementErrors: (state) => {
      state.errors += 1;
    },
    updateAccuracy: (state) => {
      const total = state.cardsCompleted;
      if (total > 0) {
        state.accuracy = ((total - state.errors) / total) * 100;
      }
    },
    resetSession: (state) => {
      state.currentSession = undefined;
      state.selectedCard = undefined;
      state.selectedCards = [];
      state.score = 0;
      state.streak = 0;
      state.accuracy = 0;
      state.timeElapsed = 0;
      state.cardsCompleted = 0;
      state.errors = 0;
    },
    removeCardFromSession: (state, action: PayloadAction<number>) => {
      if (state.currentSession) {
        state.currentSession.cards = state.currentSession.cards.filter(
          card => card.id !== action.payload
        );
      }
    },
    addCardToSession: (state, action: PayloadAction<StudyCard>) => {
      if (state.currentSession) {
        state.currentSession.cards.push(action.payload);
      }
    },
  },
  extraReducers: (builder) => {
    // Fetch due cards
    builder
      .addCase(fetchDueCards.pending, (state) => {
        state.isSubmitting = true;
      })
      .addCase(fetchDueCards.fulfilled, (state, action) => {
        state.isSubmitting = false;
        state.currentSession = action.payload;
        // Reset session stats when loading new cards
        state.score = 0;
        state.streak = 0;
        state.accuracy = 0;
        state.timeElapsed = 0;
        state.cardsCompleted = 0;
        state.errors = 0;
      })
      .addCase(fetchDueCards.rejected, (state) => {
        state.isSubmitting = false;
      });

    // Submit reviews
    builder
      .addCase(submitReviews.pending, (state) => {
        state.isSubmitting = true;
      })
      .addCase(submitReviews.fulfilled, (state, action) => {
        state.isSubmitting = false;
        
        // Update stats based on response
        state.score += action.payload.totalPointsEarned;
        
        if (action.payload.streakUpdated) {
          state.streak += 1;
        }
        
        // Update accuracy
        state.accuracy = action.payload.accuracy;
      })
      .addCase(submitReviews.rejected, (state) => {
        state.isSubmitting = false;
      });

    // Replace card
    builder
      .addCase(replaceCard.fulfilled, (state, action) => {
        if (state.currentSession) {
          state.currentSession.cards.push(action.payload);
        }
      });
  },
});

export const {
  setGameMode,
  selectCard,
  toggleCardSelection,
  clearCardSelection,
  incrementScore,
  incrementStreak,
  resetStreak,
  incrementTimeElapsed,
  incrementCardsCompleted,
  incrementErrors,
  updateAccuracy,
  resetSession,
  removeCardFromSession,
  addCardToSession,
} = studySlice.actions;

export default studySlice.reducer;
"""

# App slice
app_slice = """import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AppState {
  isInitialized: boolean;
  isLoading: boolean;
  theme: 'light' | 'dark';
  language: 'ru' | 'es' | 'en';
  sidebarOpen: boolean;
  notifications: Notification[];
  deviceInfo: {
    isMobile: boolean;
    isTablet: boolean;
    isDesktop: boolean;
  };
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

const initialState: AppState = {
  isInitialized: false,
  isLoading: false,
  theme: 'light',
  language: 'ru',
  sidebarOpen: false,
  notifications: [],
  deviceInfo: {
    isMobile: false,
    isTablet: false,
    isDesktop: true,
  },
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    initializeApp: (state) => {
      state.isLoading = true;
      
      // Load theme from localStorage
      const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
      if (savedTheme) {
        state.theme = savedTheme;
      }
      
      // Load language from localStorage
      const savedLanguage = localStorage.getItem('language') as 'ru' | 'es' | 'en' | null;
      if (savedLanguage) {
        state.language = savedLanguage;
      }
      
      // Detect device type
      const userAgent = navigator.userAgent;
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
      const isTablet = /iPad|Android/i.test(userAgent) && window.innerWidth >= 768;
      
      state.deviceInfo = {
        isMobile: isMobile && !isTablet,
        isTablet,
        isDesktop: !isMobile,
      };
      
      state.isInitialized = true;
      state.isLoading = false;
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
      localStorage.setItem('theme', action.payload);
      
      // Update document class for Tailwind dark mode
      if (action.payload === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },
    setLanguage: (state, action: PayloadAction<'ru' | 'es' | 'en'>) => {
      state.language = action.payload;
      localStorage.setItem('language', action.payload);
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id' | 'timestamp' | 'read'>>) => {
      const notification: Notification = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        read: false,
      };
      state.notifications.unshift(notification);
      
      // Keep only last 50 notifications
      if (state.notifications.length > 50) {
        state.notifications = state.notifications.slice(0, 50);
      }
    },
    markNotificationAsRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification) {
        notification.read = true;
      }
    },
    markAllNotificationsAsRead: (state) => {
      state.notifications.forEach(notification => {
        notification.read = true;
      });
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    updateDeviceInfo: (state) => {
      const userAgent = navigator.userAgent;
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
      const isTablet = /iPad|Android/i.test(userAgent) && window.innerWidth >= 768;
      
      state.deviceInfo = {
        isMobile: isMobile && !isTablet,
        isTablet,
        isDesktop: !isMobile,
      };
    },
  },
});

export const {
  initializeApp,
  setTheme,
  setLanguage,
  toggleSidebar,
  setSidebarOpen,
  addNotification,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  removeNotification,
  clearNotifications,
  setLoading,
  updateDeviceInfo,
} = appSlice.actions;

export default appSlice.reducer;
"""

# User slice (placeholder)
user_slice = """import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { User, UserStats } from '@/types';
import apiService from '@/services/api';

interface UserState {
  stats?: UserStats;
  isLoadingStats: boolean;
  achievements: any[];
  isLoadingAchievements: boolean;
}

const initialState: UserState = {
  stats: undefined,
  isLoadingStats: false,
  achievements: [],
  isLoadingAchievements: false,
};

// Async thunks
export const fetchUserStats = createAsyncThunk(
  'user/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.get<UserStats>('/users/me/stats');
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error?.message || 'Failed to fetch stats');
    }
  }
);

export const fetchUserAchievements = createAsyncThunk(
  'user/fetchAchievements',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.get('/achievements/me');
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.error?.message || 'Failed to fetch achievements');
    }
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearUserData: (state) => {
      state.stats = undefined;
      state.achievements = [];
    },
  },
  extraReducers: (builder) => {
    // Fetch stats
    builder
      .addCase(fetchUserStats.pending, (state) => {
        state.isLoadingStats = true;
      })
      .addCase(fetchUserStats.fulfilled, (state, action) => {
        state.isLoadingStats = false;
        state.stats = action.payload;
      })
      .addCase(fetchUserStats.rejected, (state) => {
        state.isLoadingStats = false;
      });

    // Fetch achievements
    builder
      .addCase(fetchUserAchievements.pending, (state) => {
        state.isLoadingAchievements = true;
      })
      .addCase(fetchUserAchievements.fulfilled, (state, action) => {
        state.isLoadingAchievements = false;
        state.achievements = action.payload;
      })
      .addCase(fetchUserAchievements.rejected, (state) => {
        state.isLoadingAchievements = false;
      });
  },
});

export const { clearUserData } = userSlice.actions;
export default userSlice.reducer;
"""

# useAuth hook
use_auth = """import { useSelector } from 'react-redux';
import { RootState } from '@/store';

export const useAuth = () => {
  const { user, isAuthenticated, isLoading, error } = useSelector((state: RootState) => state.auth);
  
  return {
    user,
    isAuthenticated,
    isLoading,
    error,
  };
};
"""

# useStudy hook
use_study = """import { useSelector, useDispatch } from 'react-redux';
import { useCallback } from 'react';
import { RootState, AppDispatch } from '@/store';
import { 
  fetchDueCards, 
  submitReviews, 
  setGameMode,
  selectCard,
  toggleCardSelection,
  clearCardSelection,
  resetSession 
} from '@/store/studySlice';
import { StudyCard, ReviewItem, ExerciseType } from '@/types/study';

export const useStudy = () => {
  const dispatch = useDispatch<AppDispatch>();
  const studyState = useSelector((state: RootState) => state.study);
  
  const loadDueCards = useCallback(async (params?: {
    limit?: number;
    includeNew?: boolean;
    exerciseTypes?: ExerciseType[];
    cefrLevels?: string[];
  }) => {
    return dispatch(fetchDueCards(params || {}));
  }, [dispatch]);
  
  const submitStudyReviews = useCallback(async (reviews: ReviewItem[], sessionId?: string) => {
    return dispatch(submitReviews({
      items: reviews,
      sessionId
    }));
  }, [dispatch]);
  
  const changeGameMode = useCallback((mode: ExerciseType) => {
    dispatch(setGameMode(mode));
  }, [dispatch]);
  
  const selectStudyCard = useCallback((card: StudyCard) => {
    dispatch(selectCard(card));
  }, [dispatch]);
  
  const toggleStudyCardSelection = useCallback((cardId: number) => {
    dispatch(toggleCardSelection(cardId));
  }, [dispatch]);
  
  const clearStudyCardSelection = useCallback(() => {
    dispatch(clearCardSelection());
  }, [dispatch]);
  
  const resetStudySession = useCallback(() => {
    dispatch(resetSession());
  }, [dispatch]);
  
  return {
    ...studyState,
    loadDueCards,
    submitStudyReviews,
    changeGameMode,
    selectStudyCard,
    toggleStudyCardSelection,
    clearStudyCardSelection,
    resetStudySession,
  };
};
"""

# Записываем Redux store и хуки
with open("pairlingua/frontend/src/store/index.ts", "w") as f:
    f.write(store_index)

with open("pairlingua/frontend/src/store/authSlice.ts", "w") as f:
    f.write(auth_slice)

with open("pairlingua/frontend/src/store/studySlice.ts", "w", encoding="utf-8") as f:
    f.write(study_slice)

with open("pairlingua/frontend/src/store/appSlice.ts", "w") as f:
    f.write(app_slice)

with open("pairlingua/frontend/src/store/userSlice.ts", "w") as f:
    f.write(user_slice)

with open("pairlingua/frontend/src/hooks/useAuth.ts", "w") as f:
    f.write(use_auth)

with open("pairlingua/frontend/src/hooks/useStudy.ts", "w") as f:
    f.write(use_study)

print("✅ Redux store и хуки созданы")
print("🏪 Store с auth, study, app, user слайсами")
print("🔄 Async thunks для API взаимодействия")
print("🪝 Типизированные хуки useAuth, useStudy")
print("📱 Поддержка мобильных устройств")