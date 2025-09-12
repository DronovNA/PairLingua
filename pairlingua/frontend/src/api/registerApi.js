export async function onRegister({ email, password }) {
  const response = await fetch('http://127.0.0.1:8000/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.message || 'Ошибка регистрации');
  }

  return await response.json();
}
