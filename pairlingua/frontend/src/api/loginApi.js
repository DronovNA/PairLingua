export async function onLogin({ email, password }) {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password })
  });
  if (!response.ok) {
    const err = await response.json();

    // Если detail - массив ошибок, собрать сообщения
    let errorMessage = 'Login failed';
    if (err.detail && Array.isArray(err.detail)) {
      errorMessage = err.detail.map(e => e.msg || JSON.stringify(e)).join('; ');
    } else if (typeof err.detail === 'string') {
      errorMessage = err.detail;
    }
    throw new Error(errorMessage);
  }
  return await response.json();
}

// Универсальный fetch с автоматическим обновлением токенов
export async function fetchWithAuth(url, options = {}, retry = true) {
  const response = await fetch(url, {
    ...options,
    credentials: 'include',
  });

  if (response.status === 401 && retry) {
    try {
      await refreshTokens();
      return fetchWithAuth(url, options, false);
    } catch (e) {
      throw new Error('Сессия истекла, требуется повторный вход');
    }
  }

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Ошибка сети');
  }

  return response.json();
}
