import { createSlice, PayloadAction } from '@reduxjs/toolkit';

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
