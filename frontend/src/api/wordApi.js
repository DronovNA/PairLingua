const BASE_URL = '/api/v1/words/pairs';

export async function getWordPairs() {
  const res = await fetch(BASE_URL, { credentials: 'include' });
  if (!res.ok) throw new Error('Failed to load');
  return res.json();
}

export async function addWordPair(wordData) {
  const res = await fetch(BASE_URL, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(wordData)
  });
  if (!res.ok) throw new Error('Failed to add');
  return res.json();
}

export async function updateWordPair(id, wordData) {
  const res = await fetch(`${BASE_URL}/${id}`, {
    method: 'PATCH',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(wordData)
  });
  if (!res.ok) throw new Error('Failed to update');
  return res.json();
}

export async function deleteWordPair(id) {
  const res = await fetch(`${BASE_URL}/${id}`, {
    method: 'DELETE',
    credentials: 'include'
  });
  if (!res.ok) throw new Error('Failed to delete');
  return res.json();
}
