import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// Имитация API
const mockStats = {
  score: 0,
  best: 10,
  streak: 2,
  accuracy: 0,
};
const mockPairs = [
  { id: 1, es: 'gato', ru: 'кот' },
  { id: 2, es: 'libro', ru: 'книга' },
  { id: 3, es: 'verde', ru: 'зелёный' },
  // ... добавь свои слова
];

function MainGamePage() {
  const [stats, setStats] = useState(mockStats);
  const [pairs, setPairs] = useState([]);
  const [selectedEs, setSelectedEs] = useState(null);
  const [selectedRu, setSelectedRu] = useState(null);
  const [result, setResult] = useState('');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Здесь наружный API fetch мог бы работать! Например, /api/game/pairs
    setPairs(mockPairs.sort(() => Math.random() - 0.5));
  }, []);

  // Проверка пар
  const handleSelectEs = (pair) => setSelectedEs(pair);
  const handleSelectRu = (pair) => setSelectedRu(pair);

  useEffect(() => {
    if (selectedEs && selectedRu) {
      if (selectedEs.id === selectedRu.id) {
        setResult('Верно!');
        setStats((s) => ({ ...s, score: s.score + 1, streak: s.streak + 1, accuracy: Math.round(((s.score + 1) / (progress + 1)) * 100) }));
      } else {
        setResult('Ошибка!');
        setStats((s) => ({ ...s, streak: 0, accuracy: Math.round((s.score / (progress + 1)) * 100) }));
      }
      setProgress((p) => p + 1);
      setTimeout(() => {
        setSelectedEs(null);
        setSelectedRu(null);
        setResult('');
        setPairs((ps) => ps.sort(() => Math.random() - 0.5));
      }, 1100);
    }
  }, [selectedEs, selectedRu]);

  return (
    <div className="main-game-container">
      <header>
        <h1 style={{color: '#269'}}>PairLingua</h1>
        <p style={{marginBottom: 18}}>Изучай испанский играючи</p>
        <button className="main-btn" onClick={() => window.location.reload()}>Новая игра</button>
      </header>

      <section className="stats-row">
        <StatCard name="Очки" value={stats.score} />
        <StatCard name="Лучший результат" value={stats.best} />
        <StatCard name="Серия" value={stats.streak} />
        <StatCard name="Точность" value={stats.accuracy + '%'}/>
      </section>

      <div className="progress-bar">
        <div className="progress-current" style={{width: `${Math.min(progress*12,100)}%`}}></div>
      </div>
      <div className="instruction">
        Кликните на <b>испанское</b> слово, затем на его <b>русский</b> перевод
      </div>
      <section className="word-match-row">
        <WordColumn
          words={pairs.map(p=>({id:p.id, value:p.es}))}
          lang="Español"
          selected={selectedEs}
          onSelectWord={pair => handleSelectEs(pairs.find(p=>p.es===pair.value))}
        />
        <WordColumn
          words={pairs.map(p=>({id:p.id, value:p.ru}))}
          lang="Русский"
          selected={selectedRu}
          onSelectWord={pair => handleSelectRu(pairs.find(p=>p.ru===pair.value))}
        />
      </section>
      <div className="result-box">{result}</div>
    </div>
  );
}

// Мои карточки статистики
function StatCard({name, value}) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-name">{name}</div>
    </div>
  );
}

// Колонка слов
function WordColumn({words, lang, selected, onSelectWord}) {
  return (
    <div className="word-column">
      <div className="column-title">{lang}</div>
      {words.map((w) => (
        <button
          key={w.id}
          className={`word-btn ${selected && selected.value===w.value ? "selected-word":""}`}
          onClick={() => onSelectWord(w)}
          disabled={Boolean(selected)}
        >
          {w.value}
        </button>
      ))}
    </div>
  );
}

export default MainGamePage;
