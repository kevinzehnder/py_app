import { useAuthStore } from '../stores/auth';

export async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const token = useAuthStore.getState().bearerToken;
  const headers = new Headers(init?.headers);
  if (token !== '') {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return fetch(input, {
    ...init,
    credentials: 'same-origin',
    headers,
  });
}
