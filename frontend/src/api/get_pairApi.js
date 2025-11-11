import { fetchWithAuth } from './loginApi';

export async function fetchWordPairs(limit = 5) {
  return fetchWithAuth(`/api/v1/words/pairs/random_simple?limit=${limit}`, {
    method: 'GET'
  });
}
