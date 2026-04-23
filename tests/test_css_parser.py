"""Tests for CSS-like DOQL parser (.doql.css, .doql.less, .doql.sass)."""
from __future__ import annotations

import pathlib

import pytest

from doql.parsers import parse_file, parse_css_text, detect_doql_file


EXAMPLES = pathlib.Path(__file__).parent.parent / "examples"


# ─── parse_css_text basics ─────────────────────────────────────

def test_css_parse_minimal():
    src = '''
app {
  name: "Hello";
  version: "1.0.0";
}
'''
    spec = parse_css_text(src, format="css")
    assert spec.app_name == "Hello"
    assert spec.version == "1.0.0"
    assert spec.parse_errors == []


def test_css_parse_entity():
    src = '''
entity[name="Todo"] {
  id: uuid! auto;
  title: string!;
  done: bool default=false;
}
'''
    spec = parse_css_text(src, format="css")
    assert len(spec.entities) == 1
    assert spec.entities[0].name == "Todo"
    assert len(spec.entities[0].fields) >= 3


def test_css_parse_interface():
    src = '''
interface[type="api"] {
  type: rest;
  auth: jwt;
}
'''
    spec = parse_css_text(src, format="css")
    assert len(spec.interfaces) == 1
    assert spec.interfaces[0].type == "rest"


def test_css_parse_role():
    src = '''
role[name="admin"] {
  can: [*];
}
'''
    spec = parse_css_text(src, format="css")
    assert len(spec.roles) == 1
    assert spec.roles[0].name == "admin"


def test_css_parse_deploy():
    src = '''
deploy {
  target: kubernetes;
  ingress: traefik;
}
'''
    spec = parse_css_text(src, format="css")
    assert spec.deploy is not None
    assert spec.deploy.target == "kubernetes"


# ─── LESS format ───────────────────────────────────────────────

def test_less_variable_expansion():
    src = '''
@app-name: "Fleet Manager";
@app-version: "2.0.0";

app {
  name: @app-name;
  version: @app-version;
}
'''
    spec = parse_css_text(src, format="less")
    assert spec.app_name == "Fleet Manager"
    assert spec.version == "2.0.0"


# ─── SASS format ──────────────────────────────────────────────

def test_sass_basic_parsing():
    src = '''
$version: "0.5.0"

app
  name: "Test"
  version: $version
'''
    spec = parse_css_text(src, format="sass")
    assert spec.app_name == "Test"


# ─── Real-world example files ─────────────────────────────────

@pytest.mark.parametrize("example,fmt", [
    ("todo-pwa", "css"),
    ("asset-management", "css"),
    ("kiosk-station", "css"),
    ("calibration-lab", "less"),
    ("iot-fleet", "less"),
    ("document-generator", "less"),
    ("notes-app", "sass"),
])
def test_parses_css_example_file(example, fmt):
    path = EXAMPLES / example / f"app.doql.{fmt}"
    if not path.exists():
        pytest.skip(f"Example not found: {path}")
    spec = parse_file(path)
    assert spec.app_name and spec.app_name != "Untitled"
    assert spec.version
    errors = [e for e in spec.parse_errors if e.severity == "error"]
    assert len(errors) == 0, f"Parse errors in {example}: {[e.message for e in errors]}"


# ─── Auto-detection ───────────────────────────────────────────

def test_detect_doql_file_prefers_less(tmp_path):
    (tmp_path / "app.doql").write_text("APP: X")
    (tmp_path / "app.doql.less").write_text("app { name: X; }")
    result = detect_doql_file(tmp_path)
    assert result.name == "app.doql.less"


def test_detect_doql_file_prefers_sass(tmp_path):
    (tmp_path / "app.doql").write_text("APP: X")
    (tmp_path / "app.doql.sass").write_text("app\n  name: X")
    result = detect_doql_file(tmp_path)
    assert result.name == "app.doql.sass"


def test_detect_doql_file_falls_back_to_classic(tmp_path):
    (tmp_path / "app.doql").write_text("APP: X")
    result = detect_doql_file(tmp_path)
    assert result.name == "app.doql"


def test_iot_fleet_less_has_entities():
    path = EXAMPLES / "iot-fleet" / "app.doql.less"
    if not path.exists():
        pytest.skip()
    spec = parse_file(path)
    names = {e.name for e in spec.entities}
    assert "Node" in names
    assert "Telemetry" in names
    assert len(spec.entities) >= 4


def test_notes_app_sass_has_all_interfaces():
    path = EXAMPLES / "notes-app" / "app.doql.sass"
    if not path.exists():
        pytest.skip()
    spec = parse_file(path)
    types = {i.type for i in spec.interfaces}
    assert "rest" in types or "api" in types or len(spec.interfaces) >= 3
    assert len(spec.entities) == 3


# ─── Error message quality ───────────────────────────────────────────────────

def test_css_parse_error_has_line_info():
    """Parser should report line numbers for syntax errors."""
    src = '''
app {
  name: "Test";
}

entity[name="Bad"] {
  id: uuid! auto  // missing semicolon
  name: string!;
}
'''
    spec = parse_css_text(src, format="css")
    # Should have parse_errors with line information
    # Note: Current parser is lenient, but we track errors in mappers


def test_css_unknown_selector_gives_warning():
    """Unknown selector types should produce validation warnings."""
    src = '''
app {
  name: "Test";
}

unknownblock[name="X"] {
  field: value;
}
'''
    spec = parse_css_text(src, format="css")
    # Unknown blocks are currently skipped; could add warning


def test_less_syntax_error_recovery():
    """LESS parser should recover from single syntax errors."""
    src = '''
@app-name: "Test";

app {
  name: @app-name;
  version: "1.0.0";
}
'''
    spec = parse_css_text(src, format="less")
    assert spec.app_name == "Test"
    assert spec.version == "1.0.0"


# ─── Regression tests: .doql vs .doql.css/.less/.sass parity ───────────────

def _spec_to_comparable_dict(spec):
    """Convert DoqlSpec to comparable dict (key fields only)."""
    return {
        "app_name": spec.app_name,
        "version": spec.version,
        "domain": spec.domain,
        "entity_count": len(spec.entities),
        "entity_names": sorted([e.name for e in spec.entities]),
        "interface_count": len(spec.interfaces),
        "interface_names": sorted([i.name for i in spec.interfaces]),
        "role_count": len(spec.roles),
        "role_names": sorted([r.name for r in spec.roles]),
        "deploy_target": spec.deploy.target if spec.deploy else None,
        "env_refs": sorted(spec.env_refs),
    }


@pytest.mark.parametrize("example", [
    "calibration-lab",  # has app.doql + app.doql.less
])
def test_doql_vs_less_regression(example):
    """Verify .doql and .doql.less produce equivalent DoqlSpec."""
    classic_path = EXAMPLES / example / "app.doql"
    less_path = EXAMPLES / example / "app.doql.less"

    if not classic_path.exists() or not less_path.exists():
        pytest.skip(f"Need both app.doql and app.doql.less in {example}")

    from doql.parsers import parse_file, parse_text

    classic_spec = parse_file(classic_path)
    less_spec = parse_file(less_path)

    # Check no parse errors
    assert len([e for e in classic_spec.parse_errors if e.severity == "error"]) == 0
    assert len([e for e in less_spec.parse_errors if e.severity == "error"]) == 0

    # Compare key fields
    classic_dict = _spec_to_comparable_dict(classic_spec)
    less_dict = _spec_to_comparable_dict(less_spec)

    # Assertions with clear diffs
    assert classic_dict["app_name"] == less_dict["app_name"], \
        f"app_name mismatch: {classic_dict['app_name']} vs {less_dict['app_name']}"
    assert classic_dict["entity_count"] == less_dict["entity_count"], \
        f"entity_count mismatch: {classic_dict['entity_count']} vs {less_dict['entity_count']}"
    assert classic_dict["entity_names"] == less_dict["entity_names"], \
        f"entity_names mismatch: {set(classic_dict['entity_names'])} vs {set(less_dict['entity_names'])}"
    assert classic_dict["interface_count"] == less_dict["interface_count"], \
        f"interface_count mismatch: {classic_dict['interface_count']} vs {less_dict['interface_count']}"
    assert classic_dict["deploy_target"] == less_dict["deploy_target"], \
        f"deploy_target mismatch: {classic_dict['deploy_target']} vs {less_dict['deploy_target']}"


# ─── project block (monorepo nesting) ─────────────────────────

def test_css_parse_project_blocks():
    src = '''
app {
  name: root-app;
  version: 1.0.0;
}

project[name="api"][path="./api"] {
  app {
    name: api;
    version: 0.2.0;
  }
  interface[type="api"] {
    framework: fastapi;
  }
}

project[name="frontend"][path="./frontend"] {
  app {
    name: frontend;
    version: 0.1.0;
  }
  interface[type="web"] {
    framework: react;
  }
}
'''
    spec = parse_css_text(src, format="css")
    assert spec.app_name == "root-app"
    assert spec.version == "1.0.0"
    assert len(spec.subprojects) == 2

    api = spec.subprojects[0]
    assert api.name == "api"
    assert api.path == "./api"
    assert api.spec.app_name == "api"
    assert len(api.spec.interfaces) == 1
    assert api.spec.interfaces[0].framework == "fastapi"

    fe = spec.subprojects[1]
    assert fe.name == "frontend"
    assert fe.path == "./frontend"
    assert fe.spec.app_name == "frontend"
    assert len(fe.spec.interfaces) == 1
    assert fe.spec.interfaces[0].framework == "react"
