export async function onRegister({ email, password }) {
  const response = await fetch('/api/v1/auth/register', {
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
