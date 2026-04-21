"""Regression tests for backward-compatibility re-export shims.

The ``doql.exporters.css_exporter`` and ``doql.exporters.markdown_exporter``
modules are thin facades that re-export symbols from the new subpackages.
If someone imports from the old locations (pre-session-11), their code must
still work.
"""
from __future__ import annotations

import pytest


# ── css_exporter shim ───────────────────────────────────────


def test_css_exporter_shim_re_exports_public_api() -> None:
    """All public entry points from the old module must be importable."""
    from doql.exporters.css_exporter import (
        export_css, export_less, export_sass, export_css_file,
    )
    assert callable(export_css)
    assert callable(export_less)
    assert callable(export_sass)
    assert callable(export_css_file)


def test_css_exporter_shim_re_exports_renderers() -> None:
    """Internal renderers used by downstream generators must stay reachable."""
    from doql.exporters.css_exporter import (
        _render_app, _render_entity, _render_interface,
        _render_workflow, _render_deploy,
    )
    assert callable(_render_app)
    assert callable(_render_entity)


def test_css_exporter_shim_re_exports_format_helpers() -> None:
    """LESS/SASS conversion helpers must remain importable."""
    from doql.exporters.css_exporter import _css_to_less, _css_to_sass
    assert callable(_css_to_less)
    assert callable(_css_to_sass)


# ── markdown_exporter shim ──────────────────────────────────


def test_markdown_exporter_shim_re_exports_public_api() -> None:
    from doql.exporters.markdown_exporter import (
        export_markdown, export_markdown_file,
    )
    assert callable(export_markdown)
    assert callable(export_markdown_file)


def test_markdown_exporter_shim_re_exports_writers() -> None:
    """Internal writer functions used by docs generators must stay reachable."""
    from doql.exporters.markdown_exporter import (
        _write_entities, _write_interfaces, _write_workflows,
        _write_deployment,
    )
    assert callable(_write_entities)
    assert callable(_write_interfaces)


def test_markdown_exporter_shim_re_exports_helpers() -> None:
    from doql.exporters.markdown_exporter import _h, _field_type_str
    assert callable(_h)
    assert callable(_field_type_str)


# ── round-trip sanity through shim ────────────────────────────


def test_css_shim_roundtrip_matches_direct_subpackage(tmp_path) -> None:
    """Exporting through the shim must produce identical output to the
    direct subpackage import.
    """
    from doql.parsers.models import DoqlSpec
    from doql.exporters.css_exporter import export_css
    from doql.exporters.css import export_css as direct_export_css

    spec = DoqlSpec(app_name="shim-test", version="0.0.1")

    out_shim = tmp_path / "shim.css"
    out_direct = tmp_path / "direct.css"

    with out_shim.open("w") as f:
        export_css(spec, f)
    with out_direct.open("w") as f:
        direct_export_css(spec, f)

    assert out_shim.read_text() == out_direct.read_text()
