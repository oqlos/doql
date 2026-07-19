from io import StringIO

import pytest

from doql.digital_twin import DigitalTwinAccessError, project_self_view
from doql.exporters.css import export_css
from doql.importers.yaml_importer import import_yaml
from doql.parsers import parse_css_text, validate


SOURCE = '''
app { name: "Twin"; version: "1.0.0"; }
digital-twin[name="self"] {
  source: "twin://actor/digital-twin/query/self";
  subject: self;
  subject-field: principal;
  roles: [*];
  fields: [principal, display_name, roles, tasks];
  redact: [personal_email];
  authorization: aql+subject;
  read-only: true;
  audit: true;
}
'''


def test_parse_validate_and_roundtrip_self_view():
    spec = parse_css_text(SOURCE)
    assert not [item for item in validate(spec, {}) if item.severity == "error"]
    twin = spec.digital_twins[0]
    assert twin.subject == "self" and twin.roles == ["*"]
    output = StringIO()
    export_css(spec, output)
    reparsed = parse_css_text(output.getvalue())
    assert reparsed.digital_twins[0].fields == twin.fields
    imported = import_yaml({"app_name": "Twin", "digital_twins": [twin.__dict__]})
    assert imported.digital_twins[0].authorization == "aql+subject"


def test_projection_is_allowlisted_and_subject_bound():
    view = parse_css_text(SOURCE).digital_twins[0]
    record = {"principal": "human:alice", "display_name": "Alice", "roles": ["dev"], "tasks": ["T-1"], "personal_email": "private@example.test", "secret": "never"}
    events = []
    result = project_self_view(
        view,
        authenticated_subject="human:alice",
        actor_roles=["dev"],
        record=record,
        aql_authorized=True,
        audit_sink=events.append,
    )
    assert result == {"principal": "human:alice", "display_name": "Alice", "roles": ["dev"], "tasks": ["T-1"]}
    assert events == [{
        "schema": "doql.digital-twin.access/v1",
        "view": "self",
        "subject": "human:alice",
        "authorization": "aql+subject",
        "roles": ["dev"],
        "projected_fields": ["display_name", "principal", "roles", "tasks"],
        "redacted_paths": [],
    }]
    with pytest.raises(DigitalTwinAccessError, match="subject_mismatch"):
        project_self_view(view, authenticated_subject="human:bob", actor_roles=["dev"], record=record, aql_authorized=True, audit_sink=events.append)


def test_projection_requires_aql_evidence_and_audit_sink():
    view = parse_css_text(SOURCE).digital_twins[0]
    record = {"principal": "human:alice"}
    with pytest.raises(DigitalTwinAccessError, match="aql_authorization_required"):
        project_self_view(view, authenticated_subject="human:alice", actor_roles=["dev"], record=record, audit_sink=lambda _event: None)
    with pytest.raises(DigitalTwinAccessError, match="audit_sink_required"):
        project_self_view(view, authenticated_subject="human:alice", actor_roles=["dev"], record=record, aql_authorized=True)


def test_projection_redacts_nested_secrets_and_rejects_cycles():
    view = parse_css_text(SOURCE.replace("tasks];", "tasks, profile];").replace("personal_email];", "personal_email, profile.home_address];")).digital_twins[0]
    events = []
    record = {
        "principal": "human:alice",
        "profile": {"city": "Warsaw", "api_token": "never", "home_address": "private"},
    }
    result = project_self_view(view, authenticated_subject="human:alice", actor_roles=["dev"], record=record, aql_authorized=True, audit_sink=events.append)
    assert result["profile"] == {"city": "Warsaw"}
    assert events[0]["redacted_paths"] == ["profile.api_token", "profile.home_address"]
    cyclic = {"principal": "human:alice"}
    cyclic["profile"] = cyclic
    with pytest.raises(DigitalTwinAccessError, match="projection_cycle"):
        project_self_view(view, authenticated_subject="human:alice", actor_roles=["dev"], record=cyclic, aql_authorized=True, audit_sink=events.append)
    oversized = {"principal": "human:alice", "profile": list(range(10_001))}
    with pytest.raises(DigitalTwinAccessError, match="projection_size_exceeded"):
        project_self_view(view, authenticated_subject="human:alice", actor_roles=["dev"], record=oversized, aql_authorized=True, audit_sink=events.append)


def test_validator_rejects_cross_subject_writable_or_secret_projection():
    spec = parse_css_text('''
app { name: "Bad"; }
digital-twin[name="bad"] { source: "x"; subject: any; fields: [api_token]; authorization: none; read-only: false; audit: false; }
''')
    errors = [item.message for item in validate(spec, {}) if item.severity == "error"]
    assert "Only subject=self is safe in v1" in errors
    assert "Digital twin self view must be read-only" in errors
    assert "Digital twin access must be audited" in errors
    assert "Sensitive field 'api_token' cannot be exposed" in errors


def test_runtime_rejects_an_unvalidated_sensitive_allowlist():
    view = parse_css_text(SOURCE).digital_twins[0]
    view.fields.append("nested.api_token")
    with pytest.raises(DigitalTwinAccessError, match="field_allowlist_invalid"):
        project_self_view(
            view,
            authenticated_subject="human:alice",
            actor_roles=["dev"],
            record={"principal": "human:alice"},
            aql_authorized=True,
            audit_sink=lambda _event: None,
        )
