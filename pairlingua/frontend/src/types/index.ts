// Base types
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
