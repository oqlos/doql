"""Generate React + Vite + TailwindCSS frontend from DoqlSpec.

Produces:
  web/
  ├── package.json
  ├── vite.config.ts
  ├── tailwind.config.js
  ├── postcss.config.js
  ├── tsconfig.json
  ├── index.html
  ├── src/
  │   ├── main.tsx
  │   ├── App.tsx           — React Router with all pages
  │   ├── api.ts            — fetch wrapper for /api/v1
  │   ├── components/
  │   │   └── Layout.tsx    — sidebar + header
  │   └── pages/
  │       ├── Dashboard.tsx
  │       └── <Entity>Page.tsx   — per-entity CRUD
  └── README.md
"""
from __future__ import annotations

import json
import pathlib
import re
import textwrap

from ..parser import DoqlSpec, Entity, EntityField, Interface, Page


def _snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _kebab(name: str) -> str:
    return _snake(name).replace("_", "-")


# ────────────────────────────────────────────────────────
# Config files
# ────────────────────────────────────────────────────────

def _gen_package_json(spec: DoqlSpec) -> str:
    pkg = {
        "name": _kebab(spec.app_name),
        "version": spec.version,
        "private": True,
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "tsc && vite build",
            "preview": "vite preview",
        },
        "dependencies": {
            "react": "^18.3.0",
            "react-dom": "^18.3.0",
            "react-router-dom": "^6.23.0",
            "lucide-react": "^0.400.0",
        },
        "devDependencies": {
            "@types/react": "^18.3.0",
            "@types/react-dom": "^18.3.0",
            "@vitejs/plugin-react": "^4.3.0",
            "autoprefixer": "^10.4.0",
            "postcss": "^8.4.0",
            "tailwindcss": "^3.4.0",
            "typescript": "^5.5.0",
            "vite": "^5.4.0",
        },
    }
    return json.dumps(pkg, indent=2)


def _gen_vite_config() -> str:
    return textwrap.dedent("""\
        import { defineConfig } from 'vite'
        import react from '@vitejs/plugin-react'

        export default defineConfig({
          plugins: [react()],
          server: {
            proxy: {
              '/api': 'http://localhost:8000',
            },
          },
        })
    """)


def _gen_tailwind_config() -> str:
    return textwrap.dedent("""\
        /** @type {import('tailwindcss').Config} */
        export default {
          content: ['./index.html', './src/**/*.{ts,tsx}'],
          theme: { extend: {} },
          plugins: [],
        }
    """)


def _gen_postcss_config() -> str:
    return textwrap.dedent("""\
        export default {
          plugins: {
            tailwindcss: {},
            autoprefixer: {},
          },
        }
    """)


def _gen_tsconfig() -> str:
    return json.dumps({
        "compilerOptions": {
            "target": "ES2020",
            "useDefineForClassFields": True,
            "lib": ["ES2020", "DOM", "DOM.Iterable"],
            "module": "ESNext",
            "skipLibCheck": True,
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True,
            "jsx": "react-jsx",
            "strict": True,
        },
        "include": ["src"],
    }, indent=2)


def _gen_index_html(spec: DoqlSpec) -> str:
    return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>{spec.app_name}</title>
        </head>
        <body class="bg-gray-50 text-gray-900">
          <div id="root"></div>
          <script type="module" src="/src/main.tsx"></script>
        </body>
        </html>
    """)


def _gen_main_tsx() -> str:
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
    return textwrap.dedent("""\
        @tailwind base;
        @tailwind components;
        @tailwind utilities;
    """)


# ────────────────────────────────────────────────────────
# API client
# ────────────────────────────────────────────────────────

def _gen_api_ts() -> str:
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


# ────────────────────────────────────────────────────────
# Layout
# ────────────────────────────────────────────────────────

def _gen_layout(spec: DoqlSpec, pages: list[Page], entities: list[Entity]) -> str:
    nav_items = []
    nav_items.append("  { path: '/', label: 'Dashboard', icon: 'LayoutDashboard' },")
    for ent in entities:
        slug = _kebab(ent.name) + "s"
        nav_items.append(f"  {{ path: '/{slug}', label: '{ent.name}s', icon: 'List' }},")
    nav_block = "\n".join(nav_items)

    return textwrap.dedent(f"""\
        import React from 'react';
        import {{ Link, Outlet, useLocation }} from 'react-router-dom';
        import {{ LayoutDashboard, List, Menu, X }} from 'lucide-react';

        const NAV = [
        {nav_block}
        ];

        const icons: Record<string, React.ElementType> = {{ LayoutDashboard, List }};

        export default function Layout() {{
          const location = useLocation();
          const [open, setOpen] = React.useState(false);

          return (
            <div className="flex h-screen">
              {{/* Sidebar */}}
              <aside className={{`${{open ? 'translate-x-0' : '-translate-x-full'}} md:translate-x-0 fixed md:static z-30 w-64 h-full bg-white border-r transition-transform`}}>
                <div className="p-4 border-b font-bold text-lg">{spec.app_name}</div>
                <nav className="p-2 space-y-1">
                  {{NAV.map((item) => {{
                    const Icon = icons[item.icon] || List;
                    const active = location.pathname === item.path;
                    return (
                      <Link
                        key={{item.path}}
                        to={{item.path}}
                        onClick={{() => setOpen(false)}}
                        className={{`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${{active ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'}}`}}
                      >
                        <Icon size={{18}} />
                        {{item.label}}
                      </Link>
                    );
                  }})}}
                </nav>
              </aside>

              {{/* Main */}}
              <div className="flex-1 flex flex-col overflow-hidden">
                <header className="md:hidden flex items-center gap-3 p-3 border-b bg-white">
                  <button onClick={{() => setOpen(!open)}}>
                    {{open ? <X size={{20}} /> : <Menu size={{20}} />}}
                  </button>
                  <span className="font-semibold">{spec.app_name}</span>
                </header>
                <main className="flex-1 overflow-auto p-6">
                  <Outlet />
                </main>
              </div>
            </div>
          );
        }}
    """)


# ────────────────────────────────────────────────────────
# Dashboard
# ────────────────────────────────────────────────────────

def _gen_dashboard(spec: DoqlSpec) -> str:
    cards = []
    for ent in spec.entities:
        slug = _kebab(ent.name) + "s"
        cards.append(textwrap.dedent(f"""\
              <Link to="/{slug}" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
                <h3 className="text-sm text-gray-500">{ent.name}s</h3>
                <p className="text-2xl font-bold mt-1">{{counts['{slug}'] ?? '…'}}</p>
              </Link>"""))
    cards_block = "\n".join(cards)

    fetch_lines = []
    for ent in spec.entities:
        slug = _kebab(ent.name) + "s"
        fetch_lines.append(f"      api.list('{slug}').then((d: any[]) => setCounts(c => ({{...c, '{slug}': d.length}})));")
    fetch_block = "\n".join(fetch_lines)

    return textwrap.dedent(f"""\
        import React from 'react';
        import {{ Link }} from 'react-router-dom';
        import {{ api }} from '../api';

        export default function Dashboard() {{
          const [counts, setCounts] = React.useState<Record<string, number>>({{}}); 

          React.useEffect(() => {{
        {fetch_block}
          }}, []);

          return (
            <div>
              <h1 className="text-2xl font-bold mb-6">{spec.app_name}</h1>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards_block}
              </div>
            </div>
          );
        }}
    """)


# ────────────────────────────────────────────────────────
# Entity CRUD page
# ────────────────────────────────────────────────────────

def _field_input(f: EntityField) -> str:
    if f.auto or f.computed:
        return ""
    input_type = "text"
    if f.type in ("int", "float"):
        input_type = "number"
    if f.type == "date":
        input_type = "date"
    if f.type == "datetime":
        input_type = "datetime-local"
    if f.type == "bool":
        return (
            f'          <label className="flex items-center gap-2">'
            f'<input type="checkbox" name="{f.name}" checked={{!!form.{f.name}}} '
            f'onChange={{e => setForm({{...form, {f.name}: e.target.checked}})}} />'
            f' {f.name}</label>'
        )
    return (
        f'          <input name="{f.name}" placeholder="{f.name}" type="{input_type}" '
        f'value={{form.{f.name} || ""}} '
        f'onChange={{e => setForm({{...form, {f.name}: e.target.value}})}} '
        f'className="border rounded px-3 py-2 text-sm" />'
    )


def _gen_entity_page(ent: Entity) -> str:
    slug = _kebab(ent.name) + "s"
    visible_fields = [f for f in ent.fields if not f.computed]
    form_fields = [f for f in ent.fields if not f.auto and not f.computed]
    headers = " ".join(f'<th className="text-left p-2 text-xs text-gray-500 uppercase">{f.name}</th>' for f in visible_fields[:8])
    cells = " ".join(f'<td className="p-2 text-sm">{{String(item.{f.name} ?? "")}}</td>' for f in visible_fields[:8])
    form_init = ", ".join(f"{f.name}: ''" for f in form_fields)
    inputs = "\n".join(filter(None, (_field_input(f) for f in form_fields)))

    return textwrap.dedent(f"""\
        import React from 'react';
        import {{ api }} from '../api';

        interface {ent.name} {{
          {"; ".join(f"{f.name}: any" for f in visible_fields)};
        }}

        export default function {ent.name}Page() {{
          const [items, setItems] = React.useState<{ent.name}[]>([]);
          const [showForm, setShowForm] = React.useState(false);
          const [form, setForm] = React.useState<any>({{ {form_init} }});

          const load = () => api.list<{ent.name}>('{slug}').then(setItems).catch(console.error);
          React.useEffect(() => {{ load(); }}, []);

          const handleSubmit = async (e: React.FormEvent) => {{
            e.preventDefault();
            await api.create('{slug}', form);
            setForm({{ {form_init} }});
            setShowForm(false);
            load();
          }};

          const handleDelete = async (id: string) => {{
            if (!confirm('Delete?')) return;
            await api.remove('{slug}', id);
            load();
          }};

          return (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h1 className="text-2xl font-bold">{ent.name}s</h1>
                <button onClick={{() => setShowForm(!showForm)}} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
                  {{showForm ? 'Cancel' : '+ New'}}
                </button>
              </div>

              {{showForm && (
                <form onSubmit={{handleSubmit}} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
        {inputs}
                  <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
                </form>
              )}}

              <div className="bg-white rounded-xl border overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b"><tr>{headers}<th></th></tr></thead>
                  <tbody>
                    {{items.map((item) => (
                      <tr key={{item.id}} className="border-b last:border-0 hover:bg-gray-50">
                        {cells}
                        <td className="p-2">
                          <button onClick={{() => handleDelete(item.id)}} className="text-red-500 text-xs hover:underline">Delete</button>
                        </td>
                      </tr>
                    ))}}
                    {{items.length === 0 && <tr><td colSpan={{99}} className="p-8 text-center text-gray-400">No items yet</td></tr>}}
                  </tbody>
                </table>
              </div>
            </div>
          );
        }}
    """)


# ────────────────────────────────────────────────────────
# App.tsx (router)
# ────────────────────────────────────────────────────────

def _gen_app(spec: DoqlSpec) -> str:
    imports = ["import { Routes, Route } from 'react-router-dom';"]
    imports.append("import Layout from './components/Layout';")
    imports.append("import Dashboard from './pages/Dashboard';")
    for ent in spec.entities:
        imports.append(f"import {ent.name}Page from './pages/{ent.name}Page';")

    routes = ['        <Route path="/" element={<Dashboard />} />']
    for ent in spec.entities:
        slug = _kebab(ent.name) + "s"
        routes.append(f'        <Route path="/{slug}" element={{<{ent.name}Page />}} />')

    return (
        "\n".join(imports)
        + "\n\n"
        + textwrap.dedent("""\
            export default function App() {
              return (
                <Routes>
                  <Route element={<Layout />}>
            """)
        + "\n".join(routes)
        + "\n"
        + textwrap.dedent("""\
                  </Route>
                </Routes>
              );
            }
        """)
    )


# ────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────

def generate(spec: DoqlSpec, env_vars: dict[str, str], out: pathlib.Path) -> None:
    """Generate React + Vite + TailwindCSS frontend into *out* directory."""
    web_iface = next((i for i in spec.interfaces if i.name == "web"), None)
    if not web_iface and not spec.entities:
        (out / "README.md").write_text(
            f"# {spec.app_name} — Web\n\nNo web interface or entities defined.\n",
            encoding="utf-8",
        )
        print(f"    → web/ (no web interface, skipped)")
        return

    src = out / "src"
    components = src / "components"
    pages = src / "pages"
    for d in [src, components, pages]:
        d.mkdir(parents=True, exist_ok=True)

    web_pages = web_iface.pages if web_iface else []

    # Config files
    files = {
        "package.json":      _gen_package_json(spec),
        "vite.config.ts":    _gen_vite_config(),
        "tailwind.config.js": _gen_tailwind_config(),
        "postcss.config.js": _gen_postcss_config(),
        "tsconfig.json":     _gen_tsconfig(),
        "index.html":        _gen_index_html(spec),
    }
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
        print(f"    → web/{name}")

    # Source files
    (src / "main.tsx").write_text(_gen_main_tsx(), encoding="utf-8")
    (src / "index.css").write_text(_gen_index_css(), encoding="utf-8")
    (src / "api.ts").write_text(_gen_api_ts(), encoding="utf-8")
    (src / "App.tsx").write_text(_gen_app(spec), encoding="utf-8")
    print(f"    → web/src/main.tsx, App.tsx, api.ts, index.css")

    # Layout
    (components / "Layout.tsx").write_text(
        _gen_layout(spec, web_pages, spec.entities), encoding="utf-8",
    )
    print(f"    → web/src/components/Layout.tsx")

    # Dashboard
    (pages / "Dashboard.tsx").write_text(_gen_dashboard(spec), encoding="utf-8")
    print(f"    → web/src/pages/Dashboard.tsx")

    # Entity pages
    for ent in spec.entities:
        (pages / f"{ent.name}Page.tsx").write_text(_gen_entity_page(ent), encoding="utf-8")
        print(f"    → web/src/pages/{ent.name}Page.tsx")

    # README
    (out / "README.md").write_text(
        f"# {spec.app_name} — Web\n\n"
        f"Generated by `doql build`. React + Vite + TailwindCSS.\n\n"
        f"## Quick start\n\n"
        f"```bash\ncd build/web\nnpm install\nnpm run dev\n```\n\n"
        f"## Pages\n\n"
        f"- **Dashboard** — entity counts overview\n"
        + "\n".join(f"- **{e.name}s** — CRUD list/create/delete" for e in spec.entities)
        + "\n",
        encoding="utf-8",
    )
    print(f"    → web/README.md")
