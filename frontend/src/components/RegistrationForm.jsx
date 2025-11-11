import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function RegistrationForm({ onRegister }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    if (!email || !password || !confirm) {
      setError('Заполните все поля');
      return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Введите корректный email');
      return;
    }
    if (password !== confirm) {
      setError('Пароли не совпадают');
      return;
    }
    try {
      await onRegister({ email, password });
      alert('Регистрация успешна!');
      navigate('/login');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="glass-card">
      <h2>Регистрация в PairLingua</h2>
      <form onSubmit={handleSubmit} autoComplete="on">
        <label htmlFor="reg-email">Email</label>
        <input
          type="email"
          id="reg-email"
          value={email}
          placeholder="Введите ваш email"
          onChange={e => setEmail(e.target.value)}
          autoComplete="email"
          required
        />
        <label htmlFor="reg-pass">Пароль</label>
        <input
          type="password"
          id="reg-pass"
          value={password}
          placeholder="Придумайте пароль"
          onChange={e => setPassword(e.target.value)}
          autoComplete="new-password"
          required
        />
        <label htmlFor="reg-confirm">Подтвердите пароль</label>
        <input
          type="password"
          id="reg-confirm"
          value={confirm}
          placeholder="Ещё раз пароль"
          onChange={e => setConfirm(e.target.value)}
          required
        />
        <div className="error">{error}</div>
        <button type="submit">Зарегистрироваться</button>
      </form>
    </div>
  );
}

export default RegistrationForm;
