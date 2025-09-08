import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
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
