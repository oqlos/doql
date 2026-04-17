const BASE = '/api/v1';

async function request<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...opts.headers as Record<string, string> },
    ...opts,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  list:   <T>(resource: string) => request<T[]>(`/${resource}`),
  get:    <T>(resource: string, id: string) => request<T>(`/${resource}/${id}`),
  create: <T>(resource: string, data: Partial<T>) => request<T>(`/${resource}`, { method: 'POST', body: JSON.stringify(data) }),
  update: <T>(resource: string, id: string, data: Partial<T>) => request<T>(`/${resource}/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  remove: (resource: string, id: string) => request<void>(`/${resource}/${id}`, { method: 'DELETE' }),
};
