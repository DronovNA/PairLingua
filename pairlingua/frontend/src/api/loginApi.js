export async function onLogin({ email, password }) {
  const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login', {
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
  const response = await fetch('http://127.0.0.1:8000/api/v1/auth/refresh', {
    method: 'POST',
    credentials: 'include'
  });
  if (!response.ok) throw new Error('Refresh failed');
  return await response.json();
}
