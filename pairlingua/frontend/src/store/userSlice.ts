import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
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
