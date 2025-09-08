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
