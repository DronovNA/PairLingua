import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import RegistrationForm from './components/RegistrationForm';
import MainGamePage from './components/MainGamePage';
import DictionaryPage from './components/DictionaryPage';
import { onLogin } from './api/loginApi';
import { onRegister } from './api/registerApi';

import { ToastContainer, toast, Bounce } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { getErrorMessage } from './utils/errorUtils';


function AppContent() {
  const location = useLocation();

  const handleLogin = async (credentials) => {
    try {
      const user = await onLogin(credentials);
      toast.success('Вход выполнен успешно!');
      return user;
    } catch (err) {
      toast.error(getErrorMessage(err));
      throw err;
    }
  };

  const handleRegister = async (credentials) => {
    try {
      const user = await onRegister(credentials);
      toast.success('Регистрация успешна!');
      return user;
    } catch (err) {
      toast.error(getErrorMessage(err));
      throw err;
    }
  };

  return (
    <>
      <nav style={{ padding: '10px', borderBottom: '1px solid #ccc' }}>
        <Link to="/login" style={{ marginRight: 10 }}>Вход</Link>
        <Link to="/register">Регистрация</Link>
        {location.pathname !== '/login' && location.pathname !== '/register' && (
          <Link to="/dictionary">Словарь</Link>
        )}
      </nav>
      <Routes>
        <Route path="/login" element={<LoginForm onLogin={handleLogin} />} />
        <Route path="/register" element={<RegistrationForm onRegister={handleRegister} />} />
        <Route path="/game" element={<MainGamePage />} />
        <Route path="/dictionary" element={<DictionaryPage />} />
        <Route path="*" element={<LoginForm onLogin={handleLogin} />} />
      </Routes>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
        transition={Bounce}
      />
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
