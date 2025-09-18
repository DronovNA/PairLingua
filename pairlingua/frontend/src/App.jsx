import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import RegistrationForm from './components/RegistrationForm';
import MainGamePage from './components/MainGamePage';
import DictionaryPage from './components/DictionaryPage';
import { onLogin } from './api/loginApi';
import { onRegister } from './api/registerApi';

function App() {
  const handleLogin = async (credentials) => {
    try {
      const user = await onLogin(credentials);
      alert('Успешный вход: ' + JSON.stringify(user));
    } catch (err) {
      throw err;
    }
  };

  const handleRegister = async (credentials) => {
    try {
      const user = await onRegister(credentials);
      alert('Регистрация успешна: ' + JSON.stringify(user));
    } catch (err) {
      throw err;
    }
  };

  return (
    <BrowserRouter>
      <nav style={{ padding: '10px', borderBottom: '1px solid #ccc' }}>
        <Link to="/login" style={{ marginRight: 10 }}>Вход</Link>
        <Link to="/register">Регистрация</Link>
        <Link to="/dictionary">Словарь</Link>
      </nav>
      <Routes>
        <Route path="/login" element={<LoginForm onLogin={handleLogin} />} />
        <Route path="/register" element={<RegistrationForm onRegister={handleRegister} />} />
        <Route path="/game" element={<MainGamePage />} />
        <Route path="/dictionary" element={<DictionaryPage />} />
        <Route path="*" element={<LoginForm onLogin={handleLogin} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
