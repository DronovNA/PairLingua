import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';

import { RootState } from './store';
import { checkAuth } from './store/authSlice';
import { initializeApp } from './store/appSlice';

// Components
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/UI/LoadingSpinner';
import ErrorBoundary from './components/UI/ErrorBoundary';

// Pages
import HomePage from './pages/HomePage';
import StudyPage from './pages/StudyPage';
import ProfilePage from './pages/ProfilePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import StatsPage from './pages/StatsPage';
import AchievementsPage from './pages/AchievementsPage';
import NotFoundPage from './pages/NotFoundPage';

// Hooks
import { useAuth } from './hooks/useAuth';

const App: React.FC = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { isInitialized, isLoading: appLoading } = useSelector((state: RootState) => state.app);

  useEffect(() => {
    // Initialize app
    dispatch(initializeApp());
    
    // Check authentication on app start
    const token = localStorage.getItem('accessToken');
    if (token) {
      dispatch(checkAuth());
    }
  }, [dispatch]);

  // Show loading screen while app is initializing
  if (!isInitialized || appLoading || authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-lg text-gray-600">Загрузка PairLingua...</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* Public routes */}
          <Route 
            path="/login" 
            element={
              !isAuthenticated ? <LoginPage /> : <Navigate to="/study" replace />
            } 
          />
          <Route 
            path="/register" 
            element={
              !isAuthenticated ? <RegisterPage /> : <Navigate to="/study" replace />
            } 
          />
          
          {/* Protected routes */}
          <Route
            path="/*"
            element={
              isAuthenticated ? (
                <Layout>
                  <Routes>
                    <Route path="/" element={<Navigate to="/study" replace />} />
                    <Route path="/home" element={<HomePage />} />
                    <Route path="/study" element={<StudyPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/stats" element={<StatsPage />} />
                    <Route path="/achievements" element={<AchievementsPage />} />
                    <Route path="/404" element={<NotFoundPage />} />
                    <Route path="*" element={<Navigate to="/404" replace />} />
                  </Routes>
                </Layout>
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </div>
    </ErrorBoundary>
  );
};

export default App;
