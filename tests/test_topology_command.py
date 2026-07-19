from __future__ import annotations

import argparse
import json

from doql.cli.commands.topology import TOPOLOGY_SCHEMA, cmd_topology
from doql.cli.main import create_parser


def _args(path, main_domain=""):
    return argparse.Namespace(dir=str(path.parent), file=path.name, main_domain=main_domain)


def test_topology_command_emits_versioned_json(tmp_path, capsys):
    source = tmp_path / "topology.doql.less"
    source.write_text('''
site[domain="example.com"] { source: www; remote_path: /httpdocs; }
site[domain="docs.example.com"] { source: docs; }
''')

    assert cmd_topology(_args(source, "example.com")) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == TOPOLOGY_SCHEMA
    assert payload["profile"] == "doql:site-topology/v1"
    assert payload["ok"] is True
    assert payload["sites"] == [
        {"domain": "example.com", "source": "www", "remote_path": "/httpdocs", "is_main": True},
        {"domain": "docs.example.com", "source": "docs", "remote_path": None, "is_main": False},
    ]


def test_topology_command_fails_closed_for_mapping_error(tmp_path, capsys):
    source = tmp_path / "broken.doql.less"
    source.write_text('site { source: docs; }')

    assert cmd_topology(_args(source)) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["sites"] == []
    assert payload["diagnostics"][0]["severity"] == "error"


def test_cli_registers_topology_subcommand():
    args = create_parser().parse_args(["-f", "sites.doql.less", "topology", "--main-domain", "example.com"])
    assert args.func is cmd_topology
    assert args.file == "sites.doql.less"
