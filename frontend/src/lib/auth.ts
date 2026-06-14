import { apiFetch } from './api';

export type MeResponse = {
  subject: string;
  email: string;
  name: string;
  role: 'admin' | 'editor' | 'viewer';
};

export async function getMe(): Promise<MeResponse> {
  const res = await apiFetch('/api/auth/me');
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json() as Promise<MeResponse>;
}

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  if (!res.ok) throw new Error('Invalid credentials');
  const data = (await res.json()) as { access_token: string };
  return data.access_token;
}
