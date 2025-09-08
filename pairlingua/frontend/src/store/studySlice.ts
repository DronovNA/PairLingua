import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
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
