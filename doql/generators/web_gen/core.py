"""Core source files generation (main.tsx, index.css, api.ts)."""
from __future__ import annotations

import textwrap


def _gen_main_tsx() -> str:
    """Generate main.tsx - React entry point."""
    return textwrap.dedent("""\
        import React from 'react'
        import ReactDOM from 'react-dom/client'
        import { BrowserRouter } from 'react-router-dom'
        import App from './App'
        import './index.css'

        ReactDOM.createRoot(document.getElementById('root')!).render(
          <React.StrictMode>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </React.StrictMode>,
        )
    """)


def _gen_index_css() -> str:
    """Generate index.css - Tailwind directives."""
    return textwrap.dedent("""\
        @tailwind base;
        @tailwind components;
        @tailwind utilities;
    """)


def _gen_api_ts() -> str:
    """Generate api.ts - API client wrapper."""
    return textwrap.dedent("""\
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
    """)
