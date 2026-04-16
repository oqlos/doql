"""Generate mkdocs documentation site from DoqlSpec."""
from __future__ import annotations

import pathlib

from ..parser import DoqlSpec


def generate(spec: DoqlSpec, out: pathlib.Path) -> None:
    """Generate documentation files into *out* directory."""
    out.mkdir(parents=True, exist_ok=True)
    index = out / "index.md"
    index.write_text(
        f"# {spec.app_name}\n\n"
        f"Auto-generated documentation.\n\n"
        f"## Entities\n\n"
        + "\n".join(f"- **{e.name}**" for e in spec.entities)
        + "\n\n## Interfaces\n\n"
        + "\n".join(f"- **{i.name}** ({i.type})" for i in spec.interfaces)
        + "\n",
        encoding="utf-8",
    )
    # TODO: Faza 2 — mkdocs.yml, per-entity pages, API docs
    print(f"    → {index.relative_to(out.parent)}")
