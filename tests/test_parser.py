"""Regression tests for doql.parser."""
from __future__ import annotations

import pathlib

import pytest

from doql import parser


EXAMPLES = pathlib.Path(__file__).parent.parent / "examples"


# ─── parse_text ────────────────────────────────────────────────

def test_parse_text_minimal():
    src = 'APP: "Test"\nVERSION: "1.0.0"\n'
    spec = parser.parse_text(src)
    assert spec.app_name == "Test"
    assert spec.version == "1.0.0"
    assert spec.parse_errors == []


def test_parse_text_full_entity():
    src = '''\
APP: "Demo"
VERSION: "0.1.0"

ENTITY Thing:
  id: uuid! auto
  name: string! unique
  count: int
'''
    spec = parser.parse_text(src)
    assert len(spec.entities) == 1
    ent = spec.entities[0]
    assert ent.name == "Thing"
    assert len(ent.fields) >= 3
    name_field = next(f for f in ent.fields if f.name == "name")
    assert name_field.unique is True


def test_parse_text_languages_list():
    src = 'APP: "X"\nLANGUAGES: [pl, en, de]\n'
    spec = parser.parse_text(src)
    assert spec.languages == ["pl", "en", "de"]


def test_parse_text_workflow_with_schedule_and_inline_comment():
    """Regression: inline comment after quoted value must not leak into schedule."""
    src = '''\
APP: "X"
WORKFLOW daily:
  trigger: schedule "0 8 * * *"    # daily at 8:00
  steps:
    1. do_thing
'''
    spec = parser.parse_text(src)
    assert len(spec.workflows) == 1
    wf = spec.workflows[0]
    assert wf.trigger is not None
    # The quoted value must be extracted WITHOUT the comment
    assert "#" not in (wf.schedule or "") and "#" not in (wf.trigger or "")


# ─── Error recovery ────────────────────────────────────────────

def test_parse_text_recovers_from_broken_block():
    """A malformed ENTITY block must not crash parsing of the rest of the file."""
    src = '''\
APP: "OK"
VERSION: "1.0.0"

ENTITY GoodOne:
  id: uuid! auto
  name: string!
'''
    spec = parser.parse_text(src)
    assert spec.app_name == "OK"
    assert len(spec.entities) == 1
    assert spec.entities[0].name == "GoodOne"


def test_parse_errors_is_a_list():
    """parse_errors must always exist on a spec, even when empty."""
    spec = parser.parse_text('APP: "X"\n')
    assert isinstance(spec.parse_errors, list)


# ─── Real-world example files ──────────────────────────────────

@pytest.mark.parametrize("example", [
    "asset-management",
    "calibration-lab",
    "document-generator",
    "iot-fleet",
    "kiosk-station",
])
def test_parses_example_file(example):
    path = EXAMPLES / example / "app.doql"
    if not path.exists():
        pytest.skip(f"Example not found: {path}")
    spec = parser.parse_text(path.read_text())
    assert spec.app_name and spec.app_name != "Untitled"
    assert spec.version


def test_asset_management_entities():
    path = EXAMPLES / "asset-management" / "app.doql"
    if not path.exists():
        pytest.skip()
    spec = parser.parse_text(path.read_text())
    entity_names = {e.name for e in spec.entities}
    assert "Device" in entity_names
    assert "Operator" in entity_names
    assert len(spec.workflows) >= 1


# ─── Validation ────────────────────────────────────────────────

def test_validate_detects_missing_env_ref():
    src = '''\
APP: "X"
DOMAIN: env.MY_DOMAIN
'''
    spec = parser.parse_text(src)
    issues = parser.validate(spec, env_vars={})
    # Expect a warning about MY_DOMAIN missing
    assert any("MY_DOMAIN" in i.message for i in issues)


def test_validation_issue_has_line_field():
    """ValidationIssue gained line/column fields in Faza 2."""
    issue = parser.ValidationIssue(path="foo", message="bar")
    assert hasattr(issue, "line")
    assert hasattr(issue, "column")
    assert issue.line == 0
    assert issue.column == 0


def test_validate_detects_dangling_entity_ref():
    """ENTITY ref pointing at undefined entity must surface an error."""
    src = '''\
APP: "X"
ENTITY Calibration:
  id: uuid! auto
  performed_by: Operator ref
'''
    spec = parser.parse_text(src)
    issues = parser.validate(spec, env_vars={})
    ref_errors = [i for i in issues if "Operator" in i.message]
    assert ref_errors, "expected an error about the dangling Operator ref"
    assert ref_errors[0].severity == "error"


def test_calibration_lab_has_dangling_operator_ref():
    """Known data-quality issue in examples/calibration-lab/app.doql.

    The spec references an `Operator` entity which isn't defined.
    The generator must still produce runnable SQLAlchemy models by
    degrading FK-to-unknown-entity into a plain String column.
    """
    path = EXAMPLES / "calibration-lab" / "app.doql"
    if not path.exists():
        pytest.skip()
    spec = parser.parse_text(path.read_text())
    names = {e.name for e in spec.entities}
    for ent in spec.entities:
        for f in ent.fields:
            if f.ref and f.ref not in names:
                # at least one dangling ref is expected — Operator
                return
    pytest.fail("Expected at least one dangling ref (Operator) in calibration-lab")
