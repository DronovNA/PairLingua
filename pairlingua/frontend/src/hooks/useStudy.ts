import { useSelector, useDispatch } from 'react-redux';
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
