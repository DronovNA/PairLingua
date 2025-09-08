import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, RefreshCw, Settings, BarChart3 } from 'lucide-react';

import { useStudy } from '@/hooks/useStudy';
import { useAuth } from '@/hooks/useAuth';
import LoadingSpinner from '@/components/UI/LoadingSpinner';
import GameBoard from '@/components/Study/GameBoard';
import MatchingExercise from '@/components/Study/MatchingExercise';

const StudyPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { 
    currentSession, 
    isSubmitting, 
    gameMode, 
    score, 
    streak, 
    accuracy,
    loadDueCards,
    changeGameMode,
    resetStudySession
  } = useStudy();

  const [isInitialLoading, setIsInitialLoading] = useState(true);

  useEffect(() => {
    const initializeStudy = async () => {
      setIsInitialLoading(true);
      try {
        await loadDueCards({ limit: 5, includeNew: true });
      } finally {
        setIsInitialLoading(false);
      }
    };

    initializeStudy();
  }, [loadDueCards]);

  const handleStartNewSession = async () => {
    resetStudySession();
    await loadDueCards({ limit: 5, includeNew: true });
  };

  const handleGameModeChange = (mode: 'matching' | 'multiple_choice' | 'typing') => {
    changeGameMode(mode);
  };

  if (isInitialLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-96">
        <LoadingSpinner size="large" />
        <p className="mt-4 text-lg text-gray-600">Загружаем карточки для изучения...</p>
      </div>
    );
  }

  if (!currentSession || currentSession.cards.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Play size={32} className="text-primary-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Отличная работа!
        </h2>
        <p className="text-gray-600 mb-8 max-w-md mx-auto">
          У вас нет карточек для повторения. Возвращайтесь завтра или начните новую сессию.
        </p>
        <div className="space-x-4">
          <button
            onClick={handleStartNewSession}
            className="btn-primary inline-flex items-center space-x-2"
          >
            <RefreshCw size={16} />
            <span>Новая сессия</span>
          </button>
          <button
            onClick={() => navigate('/stats')}
            className="btn-secondary inline-flex items-center space-x-2"
          >
            <BarChart3 size={16} />
            <span>Статистика</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Обучение
          </h1>
          <p className="text-gray-600 mt-1">
            Изучайте новые слова и повторяйте изученные
          </p>
        </div>
        <div className="flex items-center space-x-4 mt-4 sm:mt-0">
          <button
            onClick={() => navigate('/stats')}
            className="btn-secondary inline-flex items-center space-x-2"
          >
            <BarChart3 size={16} />
            <span className="hidden sm:inline">Статистика</span>
          </button>
          <button className="btn-secondary inline-flex items-center space-x-2">
            <Settings size={16} />
            <span className="hidden sm:inline">Настройки</span>
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-primary-600">{score}</div>
          <div className="text-sm text-gray-600">Очки</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-success-600">{streak}</div>
          <div className="text-sm text-gray-600">Серия</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-secondary-600">{accuracy.toFixed(1)}%</div>
          <div className="text-sm text-gray-600">Точность</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">{currentSession.cards.length}</div>
          <div className="text-sm text-gray-600">Осталось</div>
        </div>
      </div>

      {/* Game Mode Selector */}
      <div className="flex space-x-2">
        {[
          { mode: 'matching', label: 'Сопоставление' },
          { mode: 'multiple_choice', label: 'Выбор' },
          { mode: 'typing', label: 'Ввод' },
        ].map(({ mode, label }) => (
          <button
            key={mode}
            onClick={() => handleGameModeChange(mode as any)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              gameMode === mode
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Game Area */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        {gameMode === 'matching' ? (
          <MatchingExercise />
        ) : (
          <GameBoard />
        )}
      </div>

      {/* Progress */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Прогресс сессии</span>
          <span className="text-sm text-gray-500">
            {currentSession.totalDue - currentSession.cards.length} из {currentSession.totalDue}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ 
              width: `${((currentSession.totalDue - currentSession.cards.length) / currentSession.totalDue) * 100}%` 
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default StudyPage;
