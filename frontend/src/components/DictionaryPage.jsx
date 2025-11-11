import React, { useEffect, useState } from 'react';
import {
  getWordPairs,
  addWordPair,
  updateWordPair,
  deleteWordPair
} from '../api/wordApi';
import { Link } from 'react-router-dom';


const emptyForm = { spanish_word: '', russian_word: '' };

function DictionaryPage() {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm);
  const [editId, setEditId] = useState(null);

  useEffect(() => {
    fetchWords();
  }, []);

  async function fetchWords() {
    setLoading(true);
    try {
      const data = await getWordPairs();
      setWords(data);
      setError('');
    } catch (err) {
      setError(err.message || 'Loading error');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const payload = {
        spanish_word: form.spanish_word,
        russian_word: form.russian_word,
      };
      if (editId) {
        await updateWordPair(editId, payload);
        setEditId(null);
      } else {
        await addWordPair(payload);
      }
      setForm(emptyForm);
      fetchWords();
    } catch (err) {
      setError(err.message || 'Save error');
    }
  }

  function handleEdit(word) {
    setEditId(word.id);
    setForm({ spanish_word: word.spanish_word, russian_word: word.russian_word });
  }

  async function handleDelete(id) {
    if (!window.confirm('Удалить пару?')) return;
    try {
      await deleteWordPair(id);
      fetchWords();
    } catch (err) {
      setError(err.message || 'Delete error');
    }
  }

  function handleCancelEdit() {
    setEditId(null);
    setForm(emptyForm);
  }

  return (
    <div className="main-game-container">
        <Link to="/game" className="home-btn" title="На главную" style={{ display: 'inline-flex', marginBottom: '16px' }}>
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2 2 12h3v8h6v-6h2v6h6v-8h3z"/></svg>
        </Link>
      <h2>Словарь</h2>
      {loading && <div>Загрузка...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}

      <form className="glass-card" style={{ marginBottom: 32 }} onSubmit={handleSubmit}>
        <h3>{editId ? 'Редактировать пару' : 'Добавить пару'}</h3>
        <label>
          <span>Испанский</span>
          <input
            type="text"
            value={form.spanish_word}
            onChange={e => setForm({ ...form, spanish_word: e.target.value })}
            required
          />
        </label>
        <label>
          <span>Русский</span>
          <input
            type="text"
            value={form.russian_word}
            onChange={e => setForm({ ...form, russian_word: e.target.value })}
            required
          />
        </label>
        <button className="main-btn" type="submit">
          {editId ? 'Сохранить' : 'Добавить'}
        </button>
        {editId && (
          <button className="main-btn" type="button" onClick={handleCancelEdit}>
            Отмена
          </button>
        )}
      </form>

      <div className="word-list glass-card">
        <h3>Пары слов</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>Испанский</th>
              <th>Русский</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {words.length === 0 && (
              <tr>
                <td colSpan={3} style={{ textAlign: 'center' }}>
                  Нет слов
                </td>
              </tr>
            )}
            {words.map(word => (
              <tr key={word.id}>
                <td>{word.spanish_word}</td>
                <td>{word.russian_word}</td>
                <td>
                  <button
                    className="main-btn"
                    onClick={() => handleEdit(word)}
                    style={{ fontSize: '0.85em', marginRight: 4 }}
                  >
                    ✏️
                  </button>
                  <button
                    className="main-btn"
                    style={{ fontSize: '0.85em' }}
                    onClick={() => handleDelete(word.id)}
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DictionaryPage;
