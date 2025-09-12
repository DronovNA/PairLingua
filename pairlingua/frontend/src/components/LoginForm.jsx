import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';  // <- импортируем

function LoginForm({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();  // <- вызываем хук

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password) {
      setError('Пожалуйста, заполните все поля');
      return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Введите корректный email');
      return;
    }
    try {
      await onLogin({ email, password });
      navigate('/game');  // <- редирект на главную игру после успешного лога
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="glass-card">
      <h2>Войти в PairLingua</h2>
      <form onSubmit={handleSubmit} autoComplete="on">
        <label htmlFor="login-email">Email</label>
        <input
          type="email"
          id="login-email"
          value={email}
          placeholder="Введите ваш email"
          onChange={e => setEmail(e.target.value)}
          autoComplete="email"
          required
        />
        <label htmlFor="login-pass">Пароль</label>
        <input
          type="password"
          id="login-pass"
          value={password}
          placeholder="Пароль"
          onChange={e => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
        <div className="error">{error}</div>
        <button type="submit">Войти</button>
      </form>
    </div>
  );
}

export default LoginForm;
