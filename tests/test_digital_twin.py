from io import StringIO

import pytest

from doql.digital_twin import DigitalTwinAccessError, project_self_view
from doql.exporters.css import export_css
from doql.importers.yaml_importer import import_yaml
from doql.parsers import parse_css_text, validate


SOURCE = '''
app { name: "Twin"; version: "1.0.0"; }
digital-twin[name="self"] {
  source: "identity://actor/digital-twin/query/self";
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
    result = project_self_view(view, authenticated_subject="human:alice", actor_roles=["dev"], record=record)
    assert result == {"principal": "human:alice", "display_name": "Alice", "roles": ["dev"], "tasks": ["T-1"]}
    with pytest.raises(DigitalTwinAccessError, match="subject_mismatch"):
        project_self_view(view, authenticated_subject="human:bob", actor_roles=["dev"], record=record)


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
