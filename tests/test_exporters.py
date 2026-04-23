"""Tests for YAML / Markdown / CSS exporters and YAML importer."""
from __future__ import annotations

import io
import pathlib
import textwrap

import pytest
import yaml

from doql.parsers import parse_text, parse_file, detect_doql_file
from doql.parsers.models import (
    DoqlSpec, Entity, EntityField, Interface, Page,
    Workflow, WorkflowStep, Role, Deploy, Integration,
)
from doql.exporters.yaml_exporter import export_yaml, spec_to_dict
from doql.exporters.markdown_exporter import export_markdown
from doql.exporters.css_exporter import export_css, export_less, export_sass
from doql.importers.yaml_importer import import_yaml, import_yaml_text


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture
def sample_spec() -> DoqlSpec:
    """Minimal but representative DoqlSpec for testing."""
    return DoqlSpec(
        app_name="Test App",
        version="1.0.0",
        domain="example.com",
        languages=["en", "pl"],
        entities=[
            Entity(
                name="Item",
                fields=[
                    EntityField(name="id", type="uuid", required=True, auto=True),
                    EntityField(name="title", type="string", required=True),
                    EntityField(name="done", type="bool", default="false"),
                    EntityField(name="owner", type="uuid", ref="User"),
                ],
            ),
        ],
        interfaces=[
            Interface(
                name="web",
                type="spa",
                framework="react",
                pwa=True,
                pages=[
                    Page(name="home", layout="grid", path="/", public=True),
                    Page(name="items", layout="table", path="/items"),
                ],
            ),
        ],
        workflows=[
            Workflow(
                name="notify",
                trigger="item.created",
                steps=[
                    WorkflowStep(action="send_email", target="owner"),
                ],
            ),
        ],
        roles=[
            Role(name="admin", permissions=["full_access"]),
            Role(name="user", permissions=["read Item", "create Item"]),
        ],
        integrations=[
            Integration(name="email", type="email", config={"host": "smtp.example.com"}),
        ],
        deploy=Deploy(target="docker-compose"),
    )


# ── YAML Exporter Tests ──────────────────────────────────────

class TestYamlExporter:
    def test_export_basic_fields(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_yaml(sample_spec, buf)
        data = yaml.safe_load(buf.getvalue())
        assert data["app_name"] == "Test App"
        assert data["version"] == "1.0.0"
        assert data["domain"] == "example.com"
        assert data["languages"] == ["en", "pl"]

    def test_export_entities(self, sample_spec: DoqlSpec):
        data = spec_to_dict(sample_spec)
        assert len(data["entities"]) == 1
        e = data["entities"][0]
        assert e["name"] == "Item"
        assert len(e["fields"]) == 4
        assert e["fields"][0]["name"] == "id"
        assert e["fields"][0]["required"] is True
        assert e["fields"][0]["auto"] is True

    def test_export_interfaces(self, sample_spec: DoqlSpec):
        data = spec_to_dict(sample_spec)
        iface = data["interfaces"][0]
        assert iface["name"] == "web"
        assert iface["type"] == "spa"
        assert iface["pwa"] is True
        assert len(iface["pages"]) == 2

    def test_export_workflows(self, sample_spec: DoqlSpec):
        data = spec_to_dict(sample_spec)
        wf = data["workflows"][0]
        assert wf["name"] == "notify"
        assert wf["trigger"] == "item.created"
        assert len(wf["steps"]) == 1

    def test_export_roles(self, sample_spec: DoqlSpec):
        data = spec_to_dict(sample_spec)
        assert len(data["roles"]) == 2
        assert data["roles"][0]["name"] == "admin"

    def test_export_deploy(self, sample_spec: DoqlSpec):
        data = spec_to_dict(sample_spec)
        assert data["deploy"]["target"] == "docker-compose"

    def test_clean_removes_empty_and_none(self):
        spec = DoqlSpec(app_name="Empty")
        data = spec_to_dict(spec)
        assert "entities" not in data
        assert "parse_errors" not in data
        assert data["app_name"] == "Empty"


# ── Markdown Exporter Tests ──────────────────────────────────

class TestMarkdownExporter:
    def test_export_has_title(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_markdown(sample_spec, buf)
        md = buf.getvalue()
        assert "# Test App" in md

    def test_export_has_entities(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_markdown(sample_spec, buf)
        md = buf.getvalue()
        assert "### Entity: Item" in md
        assert "`id`" in md
        assert "`title`" in md

    def test_export_has_interfaces(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_markdown(sample_spec, buf)
        md = buf.getvalue()
        assert "### Interface: web" in md
        assert "**Framework:** react" in md

    def test_export_has_workflows(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_markdown(sample_spec, buf)
        md = buf.getvalue()
        assert "### Workflow: notify" in md
        assert "`send_email`" in md

    def test_export_has_roles(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_markdown(sample_spec, buf)
        md = buf.getvalue()
        assert "### admin" in md
        assert "- full_access" in md

    def test_export_has_deploy(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_markdown(sample_spec, buf)
        md = buf.getvalue()
        assert "docker-compose" in md

    def test_export_minimal_spec(self):
        spec = DoqlSpec(app_name="Tiny")
        buf = io.StringIO()
        export_markdown(spec, buf)
        md = buf.getvalue()
        assert "# Tiny" in md


# ── CSS Exporter Tests ────────────────────────────────────────

class TestCssExporter:
    def test_export_app_block(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_css(sample_spec, buf)
        css = buf.getvalue()
        assert 'name: "Test App";' in css
        assert 'version: "1.0.0";' in css
        assert "domain: example.com;" in css

    def test_export_entity_block(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_css(sample_spec, buf)
        css = buf.getvalue()
        assert 'entity[name="Item"]' in css
        assert "id: uuid! auto;" in css
        assert "title: string!;" in css
        assert "done: bool default=false;" in css
        assert "owner: uuid ref=User;" in css

    def test_export_interface_and_pages(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_css(sample_spec, buf)
        css = buf.getvalue()
        assert 'interface[type="web"]' in css
        assert 'page[name="home"]' in css
        assert "public: true;" in css

    def test_export_workflow(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_css(sample_spec, buf)
        css = buf.getvalue()
        assert 'workflow[name="notify"]' in css
        assert "item.created" in css

    def test_export_roles(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_css(sample_spec, buf)
        css = buf.getvalue()
        assert 'role[name="admin"]' in css
        assert "permit: full_access;" in css

    def test_export_deploy_no_duplicate(self, sample_spec: DoqlSpec):
        """Deploy target should appear only once."""
        buf = io.StringIO()
        export_css(sample_spec, buf)
        css = buf.getvalue()
        assert css.count("target: docker-compose;") == 1

    def test_export_less_format(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_less(sample_spec, buf)
        less = buf.getvalue()
        assert less.startswith("// LESS format")
        assert 'name: "Test App";' in less

    def test_export_sass_format(self, sample_spec: DoqlSpec):
        buf = io.StringIO()
        export_sass(sample_spec, buf)
        sass = buf.getvalue()
        # SASS should have no braces or semicolons
        assert "{" not in sass
        assert "}" not in sass
        assert ";" not in sass
        assert 'name: "Test App"' in sass


# ── YAML Importer Tests ──────────────────────────────────────

class TestYamlImporter:
    def test_roundtrip_yaml(self, sample_spec: DoqlSpec):
        """Export → import should produce equivalent spec."""
        buf = io.StringIO()
        export_yaml(sample_spec, buf)
        reimported = import_yaml_text(buf.getvalue())
        assert reimported.app_name == sample_spec.app_name
        assert reimported.version == sample_spec.version
        assert reimported.domain == sample_spec.domain
        assert reimported.languages == sample_spec.languages
        assert len(reimported.entities) == len(sample_spec.entities)
        assert reimported.entities[0].name == "Item"
        assert len(reimported.entities[0].fields) == 4

    def test_import_entities(self):
        yaml_text = textwrap.dedent("""\
        app_name: Demo
        entities:
          - name: Thing
            fields:
              - name: id
                type: uuid
                required: true
                auto: true
              - name: label
                type: string
                required: true
        """)
        spec = import_yaml_text(yaml_text)
        assert spec.app_name == "Demo"
        assert len(spec.entities) == 1
        assert spec.entities[0].name == "Thing"
        assert spec.entities[0].fields[0].auto is True

    def test_import_interfaces_with_pages(self):
        yaml_text = textwrap.dedent("""\
        app_name: UI Test
        interfaces:
          - name: web
            type: spa
            pages:
              - name: home
                layout: grid
                path: /
                public: true
        """)
        spec = import_yaml_text(yaml_text)
        assert len(spec.interfaces) == 1
        assert spec.interfaces[0].pages[0].name == "home"
        assert spec.interfaces[0].pages[0].public is True

    def test_import_workflows(self):
        yaml_text = textwrap.dedent("""\
        app_name: WF Test
        workflows:
          - name: notify
            trigger: item.created
            steps:
              - action: send_email
                target: owner
        """)
        spec = import_yaml_text(yaml_text)
        assert len(spec.workflows) == 1
        assert spec.workflows[0].steps[0].action == "send_email"

    def test_import_roles(self):
        yaml_text = textwrap.dedent("""\
        app_name: Role Test
        roles:
          - name: admin
            permissions:
              - full_access
          - name: user
            permissions:
              - read Item
        """)
        spec = import_yaml_text(yaml_text)
        assert len(spec.roles) == 2
        assert spec.roles[0].permissions == ["full_access"]

    def test_import_deploy(self):
        yaml_text = textwrap.dedent("""\
        app_name: Deploy Test
        deploy:
          target: quadlet
          rootless: true
        """)
        spec = import_yaml_text(yaml_text)
        assert spec.deploy.target == "quadlet"
        assert spec.deploy.rootless is True

    def test_import_from_dict(self):
        data = {
            "app_name": "Dict Test",
            "version": "2.0.0",
            "entities": [
                {"name": "Foo", "fields": [{"name": "id", "type": "uuid", "required": True}]}
            ],
        }
        spec = import_yaml(data)
        assert spec.app_name == "Dict Test"
        assert spec.version == "2.0.0"
        assert spec.entities[0].fields[0].required is True

    def test_invalid_yaml_root(self):
        with pytest.raises(ValueError, match="mapping"):
            import_yaml_text("- just a list")


# ── Real Example Round-trip Tests ─────────────────────────────

EXAMPLES_DIR = pathlib.Path(__file__).parent.parent / "examples"


@pytest.mark.parametrize("example", [
    "todo-pwa", "asset-management", "document-generator",
    "e-commerce-shop", "crm-contacts", "blog-cms",
])
def test_yaml_roundtrip_real_example(example: str):
    """Parse real example → export YAML → import → compare."""
    root = EXAMPLES_DIR / example
    spec = parse_file(root / "app.doql")

    buf = io.StringIO()
    export_yaml(spec, buf)
    reimported = import_yaml_text(buf.getvalue())

    assert reimported.app_name == spec.app_name
    assert reimported.version == spec.version
    assert len(reimported.entities) == len(spec.entities)
    for orig, re in zip(spec.entities, reimported.entities):
        assert orig.name == re.name
        assert len(orig.fields) == len(re.fields)


@pytest.mark.parametrize("example", [
    "todo-pwa", "asset-management", "e-commerce-shop",
])
def test_css_export_real_example(example: str):
    """Parse real example → export CSS → verify key blocks present."""
    root = EXAMPLES_DIR / example
    spec = parse_file(root / "app.doql")

    buf = io.StringIO()
    export_css(spec, buf)
    css = buf.getvalue()

    assert f'name: "{spec.app_name}"' in css
    for e in spec.entities:
        assert f'entity[name="{e.name}"]' in css


@pytest.mark.parametrize("example", [
    "todo-pwa", "document-generator", "blog-cms",
])
def test_markdown_export_real_example(example: str):
    """Parse real example → export Markdown → verify sections."""
    root = EXAMPLES_DIR / example
    spec = parse_file(root / "app.doql")

    buf = io.StringIO()
    export_markdown(spec, buf)
    md = buf.getvalue()

    assert f"# {spec.app_name}" in md
    for e in spec.entities:
        assert f"### Entity: {e.name}" in md


def test_css_export_project_blocks():
    """Render DoqlSpec with subprojects → verify nested project blocks."""
    from doql.parsers.models import Subproject, DoqlSpec, Interface

    root = DoqlSpec(app_name="root", version="1.0.0")
    api = DoqlSpec(app_name="api", version="0.2.0")
    api.interfaces.append(Interface(name="api", type="rest", framework="fastapi"))
    root.subprojects.append(Subproject(name="api", spec=api, path="./api"))

    buf = io.StringIO()
    export_css(root, buf)
    css = buf.getvalue()

    assert 'project[name="api"][path="./api"] {' in css
    assert 'name: "api";' in css
    assert 'framework: fastapi;' in css
    assert 'name: "root";' in css
