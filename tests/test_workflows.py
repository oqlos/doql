"""Declared workflows and dependencies, read without a device scan."""
from __future__ import annotations

import pathlib

import pytest

from doql.workflows import (
    command_drift,
    declared_dependencies,
    find_declaration,
    workflow_commands,
)

DECLARATION = """
app { name: example; version: 1.0.0; }

dependencies {
  runtime: git, gh>=2.96.0;
  test: pytest>=8, ruff>=0.12;
}

workflow[name="doctor-setup"] {
  trigger: manual;
  step-1: run cmd=python -m pip install -e ".[test]";
}

workflow[name="doctor-test"] {
  trigger: manual;
  step-1: run cmd=python -m pytest -q;
}
"""


@pytest.fixture
def project(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "app.doql.less").write_text(DECLARATION, encoding="utf-8")
    return tmp_path


def test_workflows_are_returned_as_argument_vectors(project: pathlib.Path) -> None:
    workflows = workflow_commands(project)

    assert workflows["doctor-setup"] == (("python", "-m", "pip", "install", "-e", ".[test]"),)
    assert workflows["doctor-test"] == (("python", "-m", "pytest", "-q"),)


def test_a_declaration_file_may_be_passed_directly(project: pathlib.Path) -> None:
    assert workflow_commands(project / "app.doql.less") == workflow_commands(project)


def test_dependency_groups_are_split_into_entries(project: pathlib.Path) -> None:
    dependencies = declared_dependencies(project)

    assert dependencies["runtime"] == ("git", "gh>=2.96.0")
    assert dependencies["test"] == ("pytest>=8", "ruff>=0.12")


def test_a_project_without_a_declaration_is_empty_rather_than_an_error(tmp_path: pathlib.Path) -> None:
    assert find_declaration(tmp_path) is None
    assert workflow_commands(tmp_path) == {}
    assert declared_dependencies(tmp_path) == {}


def test_a_matching_caller_reports_no_drift(project: pathlib.Path) -> None:
    declared = workflow_commands(project)

    assert command_drift({"doctor-test": [("python", "-m", "pytest", "-q")]}, declared) == ()


def test_extra_arguments_are_not_drift(project: pathlib.Path) -> None:
    """A caller may add to a declared command without contradicting it."""
    declared = workflow_commands(project)
    configured = {"doctor-setup": [("python", "-m", "pip", "install", "/opt/vendored", "-e", ".[test]")]}

    assert command_drift(configured, declared) == ()


def test_a_different_command_is_drift(project: pathlib.Path) -> None:
    declared = workflow_commands(project)

    drift = command_drift({"doctor-test": [("make", "test")]}, declared)

    assert len(drift) == 1
    assert "make test" in drift[0]
    assert "python -m pytest -q" in drift[0]


def test_workflows_neither_side_shares_are_ignored(project: pathlib.Path) -> None:
    declared = workflow_commands(project)

    assert command_drift({"deploy": [("./deploy.sh",)]}, declared) == ()
