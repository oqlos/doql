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
