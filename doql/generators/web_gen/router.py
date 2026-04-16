"""React Router configuration generation (App.tsx)."""
from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

from .common import _kebab

if TYPE_CHECKING:
    from ...parsers import DoqlSpec


def _gen_app(spec: DoqlSpec) -> str:
    """Generate App.tsx with React Router routes."""
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
