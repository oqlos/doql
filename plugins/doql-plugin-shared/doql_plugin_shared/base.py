"""Base plugin utilities — shared code generation patterns."""
from __future__ import annotations

import pathlib
from typing import Callable


def plugin_generate(
    out: pathlib.Path,
    modules: dict[str, Callable[[], str]],
    readme_content: str | None = None,
) -> None:
    """Common plugin generate() — iterates over modules dict and writes files.

    Args:
        out: Output directory for generated files
        modules: Dict mapping filenames to generator functions that return content
        readme_content: Optional README.md content (if None, no README is generated)
    """
    out.mkdir(parents=True, exist_ok=True)

    for filename, generator_fn in modules.items():
        content = generator_fn()
        path = out / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    if readme_content:
        (out / "README.md").write_text(readme_content, encoding="utf-8")
