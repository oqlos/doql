"""Config files generation for React + Vite frontend."""
from __future__ import annotations

import json
import textwrap
from typing import TYPE_CHECKING

from .common import _kebab

if TYPE_CHECKING:
    from ...parsers import DoqlSpec


def _gen_package_json(spec: DoqlSpec) -> str:
    """Generate package.json with dependencies."""
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
    """Generate vite.config.ts."""
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
    """Generate tailwind.config.js."""
    return textwrap.dedent("""\
        /** @type {import('tailwindcss').Config} */
        export default {
          content: ['./index.html', './src/**/*.{ts,tsx}'],
          theme: { extend: {} },
          plugins: [],
        }
    """)


def _gen_postcss_config() -> str:
    """Generate postcss.config.js."""
    return textwrap.dedent("""\
        export default {
          plugins: {
            tailwindcss: {},
            autoprefixer: {},
          },
        }
    """)


def _gen_tsconfig() -> str:
    """Generate tsconfig.json."""
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
    """Generate index.html."""
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
