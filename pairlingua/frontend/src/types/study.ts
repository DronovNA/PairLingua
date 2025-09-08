export interface StudyCard {
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
