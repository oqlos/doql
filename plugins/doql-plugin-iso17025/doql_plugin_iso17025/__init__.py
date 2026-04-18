"""doql-plugin-iso17025 — ISO/IEC 17025:2017 compliance add-on for calibration laboratories.

Generates:
  build/plugins/iso17025/
  ├── traceability.py        — ISO 17025 §6.5: metrological traceability chain (SI → national standard → reference → DUT)
  ├── uncertainty.py         — GUM-compliant uncertainty budget calculator (type A + type B + combined)
  ├── certificate.py         — digitally signed calibration certificate generator
  ├── drift_monitor.py       — trend analysis for reference standards (CMC validation)
  ├── migration.py           — Alembic migration for calibration_records + standards tables
  └── README.md              — integration + compliance notes
"""
from __future__ import annotations

import pathlib

from doql_plugin_shared import plugin_generate, generate_readme

from . import traceability, uncertainty, certificate, drift_monitor, migration


def generate(spec, env_vars, out: pathlib.Path, project_root: pathlib.Path) -> None:
    """Entry point called by doql's plugin runner."""
    modules = {
        "__init__.py": lambda: '"""doql-plugin-iso17025 compliance module."""\n',
        "traceability.py": traceability.generate,
        "uncertainty.py": uncertainty.generate,
        "certificate.py": certificate.generate,
        "drift_monitor.py": drift_monitor.generate,
        "migration.py": migration.generate,
    }

    readme = generate_readme(
        plugin_name="iso17025",
        modules=["traceability.py", "uncertainty.py", "certificate.py", "drift_monitor.py", "migration.py"],
        description="ISO/IEC 17025:2017 compliance add-on for calibration laboratories.",
        usage_extra="\n## Compliance\n\nCovers ISO 17025 §6.5 (traceability), §6.4.10/§7.7 (drift), §7.8 (certificates)",
    )

    plugin_generate(out, modules, readme)
