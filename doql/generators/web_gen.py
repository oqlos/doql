"""Generate React + Vite + TailwindCSS frontend from DoqlSpec.

DEPRECATED: This module is kept for backward compatibility.
Please use `doql.generators.web_gen` (the package) instead.

The generator has been refactored into a modular package:
  - doql.generators.web_gen.common      — Utility functions (snake, kebab)
  - doql.generators.web_gen.config      — Config files (package.json, vite, etc.)
  - doql.generators.web_gen.core        — Core source files (main.tsx, api.ts)
  - doql.generators.web_gen.components  — React components (Layout)
  - doql.generators.web_gen.pages       — Page components (Dashboard, EntityPage)
  - doql.generators.web_gen.router      — React Router (App.tsx)
  - doql.generators.web_gen.pwa         — PWA support (manifest, sw.js)
"""
from __future__ import annotations

# Re-export from the new package for backward compatibility
from .web_gen import generate  # noqa: F401

# Also export the internal functions that were previously importable
from .web_gen.common import _snake, _kebab  # noqa: F401
from .web_gen.config import (
    _gen_package_json,
    _gen_vite_config,
    _gen_tailwind_config,
    _gen_postcss_config,
    _gen_tsconfig,
    _gen_index_html,
)  # noqa: F401
from .web_gen.core import _gen_main_tsx, _gen_index_css, _gen_api_ts  # noqa: F401
from .web_gen.components import _gen_layout  # noqa: F401
from .web_gen.pages import _gen_dashboard, _gen_entity_page, _field_input  # noqa: F401
from .web_gen.router import _gen_app  # noqa: F401
from .web_gen.pwa import _gen_manifest, _gen_service_worker, _gen_sw_register  # noqa: F401
