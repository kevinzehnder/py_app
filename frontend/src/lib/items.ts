import { apiFetch } from './api';

export type Item = {
  id: string;
  name: string;
  description: string;
  active: boolean;
};

export type ItemCreate = {
  name: string;
  description: string;
  active: boolean;
};

export async function listItems(page = 0, perPage = 20): Promise<{ items: Item[]; total: number }> {
  const res = await apiFetch(`/api/items/?page=${page}&perPage=${perPage}`);
  if (!res.ok) throw new Error(`${res.status}`);
  const total = parseInt(res.headers.get('X-Total-Count') ?? '0', 10);
  const items = (await res.json()) as Item[];
  return { items, total };
}

export async function createItem(data: ItemCreate): Promise<Item> {
  const res = await apiFetch('/api/items/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json() as Promise<Item>;
}

export async function updateItem(id: string, data: ItemCreate): Promise<Item> {
  const res = await apiFetch(`/api/items/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json() as Promise<Item>;
}

export async function deleteItem(id: string): Promise<void> {
  const res = await apiFetch(`/api/items/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`${res.status}`);
}
