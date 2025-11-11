import React, { useState, useEffect } from 'react';
import { fetchWordPairs } from '../api/get_pairApi';
import { useNavigate } from 'react-router-dom';

const initialStats = {
  score: 0,
  best: 10,
  streak: 0,
  accuracy: 0,
  progress: 0,
  isError: false,
};

function MainGamePage() {
  const [stats, setStats] = useState(initialStats);
  const [pairs, setPairs] = useState([]);
  const [selectedEs, setSelectedEs] = useState(null);
  const [selectedRu, setSelectedRu] = useState(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  // Однократная загрузка при маунте (старте компонента)
  useEffect(() => {
    loadPairs();
    // eslint-disable-next-line
  }, []);

  // Функция загрузки пары
  const loadPairs = async () => {
    setLoading(true);
    try {
      const data = await fetchWordPairs(5);
      setPairs(data);
      setError('');
    } catch (err) {
      setError(err.message || 'Ошибка загрузки');
    }
    setLoading(false);
  };

  // После угадывания пары обновляем статистику и список
  useEffect(() => {
    if (selectedEs && selectedRu) {
      const isCorrect = selectedEs.id === selectedRu.id;
      setStats((prev) => {
        const newScore = isCorrect ? prev.score + 1 : prev.score;
        const newStreak = isCorrect ? prev.streak + 1 : 0;
        const newProgress = prev.progress + 1;
        const accuracy = newProgress > 0
          ? Math.round((newScore / newProgress) * 100)
          : 0;
        return {
          ...prev,
          score: newScore,
          streak: newStreak,
          progress: newProgress,
          accuracy,
          isError: !isCorrect,
        };
      });

      setResult(isCorrect ? 'Верно!' : 'Ошибка!');

      if (isCorrect) {
        setPairs((prevPairs) => {
          const newPairs = prevPairs.filter(pair => pair.id !== selectedEs.id);
          // Если все пары закончились, сразу загружаем новые:
          if (newPairs.length === 0) {
            setTimeout(() => {
              loadPairs();
            }, 1200); // чуть позже, чтобы не было резкого скачка UI
          }
          return newPairs;
        });
      }

      setTimeout(() => {
        setSelectedEs(null);
        setSelectedRu(null);
        setResult('');
      }, 1100);
    }
  }, [selectedEs, selectedRu]);

  function shuffle(array) {
    return array
      .map((value) => ({ value, sort: Math.random() }))
      .sort((a, b) => a.sort - b.sort)
      .map(({ value }) => value);
  }

  const handleSelectEs = (word) => setSelectedEs(word);
  const handleSelectRu = (word) => setSelectedRu(word);

  const handleNewGame = () => {
    setStats(initialStats);
    setResult('');
    setSelectedEs(null);
    setSelectedRu(null);
    loadPairs();
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div style={{ color: 'red' }}>Ошибка: {error}</div>;

  return (
    <div className="main-game-container">
      <header>
        <h1 style={{ color: '#269' }}>PairLingua</h1>
        <button className="main-btn" onClick={handleNewGame}>
          Новая игра
        </button>
        <button className="main-btn" onClick={() => navigate('/dictionary')}>
          Перейти в словарь
        </button>
      </header>

      <section className="stats-row">
        <StatCard name="Очки" value={stats.score} />
        <StatCard name="Лучший результат" value={stats.best} />
        <StatCard name="Серия" value={stats.streak} />
        <StatCard name="Точность" value={stats.accuracy + '%'} />
      </section>

      <div className="progress-bar">
        <div
          className="progress-current"
          style={{ width: `${Math.min(stats.progress * 20, 100)}%` }}
        />
      </div>

      <div className="instruction">
        Кликните на <b>испанское</b> слово, затем на его <b>русский</b> перевод
      </div>

      <div className="pairs-glass-card">
        <div className="pairs-head-row">
          <div className="pairs-col-title">Es</div>
          <div className="pairs-col-title">Ru</div>
        </div>
        <div className="pairs-cols">
          <div className="pairs-col">
            {pairs.map(p => (
              <button
                key={p.id}
                className={`word-match-btn ${selectedEs && selectedEs.id === p.id ? 'selected' : ''}`}
                onClick={() => handleSelectEs(p)}
                disabled={Boolean(selectedEs)}
              >
                {p.spanish_word}
              </button>
            ))}
          </div>
          <div className="pairs-col">
            {shuffle(pairs).map(p => (
              <button
                key={p.id}
                className={`word-match-btn ${selectedRu && selectedRu.id === p.id ? 'selected' : ''}`}
                onClick={() => handleSelectRu(p)}
                disabled={Boolean(selectedRu)}
              >
                {p.russian_word}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ name, value }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-name">{name}</div>
    </div>
  );
}

export default MainGamePage;
