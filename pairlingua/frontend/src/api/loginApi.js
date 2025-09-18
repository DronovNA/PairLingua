export async function onLogin({ email, password }) {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // важно для отправки и получения куки
    body: JSON.stringify({ email, password })
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Login failed');
  }
  return await response.json(); // {message: "Login successful"} или другой ответ от сервера
}

export async function refreshTokens() {
  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    credentials: 'include'
  });
  if (!response.ok) throw new Error('Refresh failed');
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
