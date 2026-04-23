# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/oqlos/doql
- **Primary Language**: python
- **Languages**: python: 124, md: 63, yaml: 31, json: 15, yml: 14
- **Analysis Mode**: static
- **Total Functions**: 2117
- **Total Classes**: 46
- **Modules**: 275
- **Entry Points**: 1639

## Architecture by Module

### SUMD
- **Functions**: 768
- **Classes**: 1
- **File**: `SUMD.md`

### project.map.toon
- **Functions**: 749
- **File**: `map.toon.yaml`

### doql.parsers.registry
- **Functions**: 30
- **File**: `registry.py`

### doql.parsers.css_mappers
- **Functions**: 28
- **File**: `css_mappers.py`

### doql.cli.commands.workspace
- **Functions**: 25
- **Classes**: 1
- **File**: `workspace.py`

### doql.importers.yaml_importer
- **Functions**: 22
- **File**: `yaml_importer.py`

### doql.cli.commands.doctor
- **Functions**: 20
- **Classes**: 2
- **File**: `doctor.py`

### SUMR
- **Functions**: 19
- **Classes**: 1
- **File**: `SUMR.md`

### doql.exporters.css.renderers
- **Functions**: 19
- **File**: `renderers.py`

### doql.adopt.scanner.interfaces
- **Functions**: 16
- **File**: `interfaces.py`

### playground.pyodide-bridge
- **Functions**: 15
- **File**: `pyodide-bridge.js`

### doql.lsp_server
- **Functions**: 15
- **File**: `lsp_server.py`

### doql.adopt.scanner.workflows
- **Functions**: 15
- **File**: `workflows.py`

### doql.parsers.extractors
- **Functions**: 14
- **File**: `extractors.py`

### doql.parsers.css_transformers
- **Functions**: 14
- **File**: `css_transformers.py`

### TODO
- **Functions**: 11
- **Classes**: 4
- **File**: `TODO.md`

### doql.exporters.markdown.writers
- **Functions**: 11
- **File**: `writers.py`

### doql.generators.integrations_gen
- **Functions**: 11
- **File**: `integrations_gen.py`

### doql.adopt.scanner.entities
- **Functions**: 11
- **File**: `entities.py`

### doql.parsers.validators
- **Functions**: 11
- **File**: `validators.py`

## Key Entry Points

Main execution flows into the system:

### doql.cli.commands.workspace.register_parser
> Register `workspace` subcommands on the main doql parser.
- **Calls**: sub.add_parser, ws.add_subparsers, ws_sub.add_parser, _add_common, p.add_argument, p.add_argument, p.set_defaults, ws_sub.add_parser

### doql.cli.sync.cmd_sync
> Selective rebuild — only regenerate sections that changed since last build.
- **Calls**: SUMD.build_context, SUMD.load_spec, SUMD.read_lockfile, SUMD.spec_section_hashes, SUMD.diff_sections, doql.cli.sync.determine_regeneration_set, print, print

### doql.generators.desktop_gen.generate
> Generate desktop (Tauri) layer files into *out* directory.
- **Calls**: next, None.write_text, None.write_text, None.write_text, None.write_text, None.write_text, print, print

### doql.cli.commands.init.cmd_init
> Create new project from template.

With --list-templates, shows available templates and exits.
- **Calls**: getattr, pathlib.Path, target.exists, print, SUMD.scaffold_from_template, print, print, print

### doql.cli.commands.drift.cmd_drift
> Entry point for ``doql drift``.
- **Calls**: getattr, getattr, print, None.resolve, SUMD.find_intended_file, list, SUMD.detect_drift, doql.cli.commands.drift._report_to_json

### doql.cli.commands.run.cmd_run
> Run project locally in dev mode.

With -f <file>: build on-the-fly into .doql/ and run target.
Without -f: use existing project build/ directory.
With
- **Calls**: getattr, getattr, getattr, subprocess.call, None.resolve, doql.cli.commands.run._workspace_for_file, workspace.mkdir, print

### doql.cli.commands.doctor.cmd_doctor
> Run comprehensive project health check.
- **Calls**: None.resolve, getattr, getattr, print, DoctorReport, doql.cli.commands.doctor._check_parse, doql.cli.commands.doctor._check_env, doql.cli.commands.doctor._check_files

### doql.generators.mobile_gen.generate
> Generate mobile PWA into *out* directory.
- **Calls**: next, out.mkdir, None.write_text, None.write_text, None.write_text, None.write_text, None.write_text, doql.generators.mobile_gen._gen_icons

### doql.lsp_server.document_symbols
- **Calls**: server.feature, ls.workspace.get_text_document, doql.lsp_server._parse_doc, doql.lsp_server._find_line_col, lsp.Range, _mkrange, symbols.append, _mkrange

### doql.exporters.css.format_convert._css_to_sass
> Convert CSS syntax to SASS (indented, no braces/semicolons).
- **Calls**: css_text.splitlines, line.rstrip, stripped.endswith, stripped.endswith, None.endswith, lines.append, None.join, lines.append

### doql.parsers.validators.validate
> Validate a parsed DoqlSpec against env vars and internal consistency.
- **Calls**: issues.extend, issues.extend, issues.extend, issues.extend, issues.extend, issues.extend, doql.parsers.validators._validate_app_name, doql.parsers.validators._validate_env_refs

### doql.cli.commands.publish.cmd_publish
> Publish project artifacts to registries.
- **Calls**: SUMD.build_context, SUMD.load_spec, getattr, getattr, print, print, list, print

### doql.generators.workflow_gen.generate
> Generate workflow engine modules.
- **Calls**: wf_dir.mkdir, None.write_text, None.write_text, print, None.write_text, print, None.write_text, print

### doql.lsp_server.definition
- **Calls**: server.feature, ls.workspace.get_text_document, doql.lsp_server._word_at, re.compile, pattern.search, None.count, None.find, lsp.Location

### doql.cli.commands.workspace._cmd_fix
- **Calls**: None.resolve, _tf_discover, doql.cli.commands.workspace._print, doql.cli.commands.workspace._print, doql.cli.commands.workspace._print, _tf_filter, _tf_fix, None.expanduser

### doql.cli.commands.deploy.cmd_deploy
> Deploy project to target environment.

Priority: redeploy API → redeploy CLI → @directives → docker-compose.
Install redeploy support: pip install doq
- **Calls**: SUMD.build_context, SUMD.load_spec, getattr, getattr, print, migration_yaml.exists, deploy_gen.run, getattr

### doql.parsers.blocks.split_blocks
> Split .doql text into (keyword, rest_of_header, body, start_line) blocks.
- **Calls**: list, enumerate, _BLOCK_RE.finditer, m.group, text.find, None.strip, None.count, blocks.append

### doql.cli.commands.plan.cmd_plan
> Show dry-run plan of what would be generated.

Displays project overview including entities, data sources, interfaces,
and estimated file counts per i
- **Calls**: None.resolve, doql_parser.parse_file, doql.cli.commands.plan._print_header, doql.cli.commands.plan._print_entities, doql.cli.commands.plan._print_data_sources, doql.cli.commands.plan._print_documents, doql.cli.commands.plan._print_api_clients, doql.cli.commands.plan._print_summary

### doql.cli.commands.import_cmd.cmd_import
> Import a YAML spec file and convert to DOQL format.
- **Calls**: None.resolve, getattr, SUMD.import_yaml_file, print, source.exists, print, None.resolve, None.replace

### doql.generators.ci_gen.generate
> Generate CI configuration files based on ci_configs or fallback to GitHub Actions.
- **Calls**: gh_dir.mkdir, None.write_text, print, doql.generators.ci_gen._gen_github_action, None.write_text, print, doql.generators.ci_gen._gen_gitlab_ci, None.write_text

### doql.generators.export_ts_sdk.run
> Write TypeScript SDK to the given stream.
- **Calls**: out.write, out.write, out.write, name.lower, out.write, out.write, out.write, out.write

### doql.parsers.extractors.extract_entity_fields
> Extract field definitions from ENTITY body.
- **Calls**: body.splitlines, line.strip, doql.parsers.extractors._should_skip_line, line.split, None.strip, doql.parsers.extractors._parse_field_flags, doql.parsers.extractors._parse_field_ref, doql.parsers.extractors._parse_field_default

### doql.parsers.registry._handle_data
- **Calls**: doql.parsers.registry.register, None.strip, spec.data_sources.append, SUMD.extract_val, DataSource, header.split, SUMD.extract_val, SUMD.extract_val

### doql.cli.commands.export.cmd_export
> Export project specification to various formats.
- **Calls**: None.resolve, getattr, _EXPORTERS.get, doql_parser.parse_file, getattr, SUMD.detect_doql_file, print, open

### doql.cli.commands.workspace._cmd_run
> Run `doql <action>` in each project with app.doql.css.
- **Calls**: None.resolve, doql.cli.commands.workspace._select_run_projects, doql.cli.commands.workspace._print, enumerate, doql.cli.commands.workspace._print_run_summary, doql.cli.commands.workspace._print, doql.cli.commands.workspace._print_dry_run_commands, doql.cli.commands.workspace._execute_single_project

### doql.parsers.registry._handle_api_client
- **Calls**: doql.parsers.registry.register, None.strip, SUMD.extract_val, spec.api_clients.append, ApiClient, header.split, SUMD.extract_val, SUMD.extract_val

### doql.parsers.css_mappers._map_data_source
> Map CSS block to DataSource definition.
- **Calls**: sel.attributes.get, DataSource, spec.data_sources.append, block.declarations.get, block.declarations.get, block.declarations.get, block.declarations.get, block.declarations.get

### doql.lsp_server.completion
- **Calls**: server.feature, ls.workspace.get_text_document, doql.lsp_server._parse_doc, lsp.CompletionList, lsp.CompletionOptions, items.append, items.append, lsp.CompletionItem

### doql.cli.commands.validate.cmd_validate
> Validate .doql file and .env configuration.

Returns:
    0 if validation passes, 1 if there are errors
- **Calls**: None.resolve, getattr, print, doql.cli.commands.validate._print_issues, SUMD.detect_doql_file, doql_parser.parse_file, doql_parser.parse_env, doql_parser.validate

### doql.cli.commands.workspace._cmd_list
- **Calls**: None.resolve, doql.cli.commands.workspace._discover_local, doql.cli.commands.workspace._filter_projects, doql.cli.commands.workspace._print_project_table, doql.cli.commands.workspace._print, root.exists, doql.cli.commands.workspace._print, doql.cli.commands.workspace._print

## Process Flows

Key execution flows identified:

### Flow 1: register_parser
```
register_parser [doql.cli.commands.workspace]
```

### Flow 2: cmd_sync
```
cmd_sync [doql.cli.sync]
  └─ →> build_context
  └─ →> load_spec
```

### Flow 3: generate
```
generate [doql.generators.desktop_gen]
```

### Flow 4: cmd_init
```
cmd_init [doql.cli.commands.init]
  └─ →> scaffold_from_template
```

### Flow 5: cmd_drift
```
cmd_drift [doql.cli.commands.drift]
  └─ →> find_intended_file
```

### Flow 6: cmd_run
```
cmd_run [doql.cli.commands.run]
```

### Flow 7: cmd_doctor
```
cmd_doctor [doql.cli.commands.doctor]
```

### Flow 8: document_symbols
```
document_symbols [doql.lsp_server]
  └─> _parse_doc
  └─> _find_line_col
```

### Flow 9: _css_to_sass
```
_css_to_sass [doql.exporters.css.format_convert]
```

### Flow 10: validate
```
validate [doql.parsers.validators]
```

## Key Classes

### doql.cli.commands.doctor.DoctorReport
- **Methods**: 4
- **Key Methods**: doql.cli.commands.doctor.DoctorReport.add, doql.cli.commands.doctor.DoctorReport.ok, doql.cli.commands.doctor.DoctorReport.warnings, doql.cli.commands.doctor.DoctorReport.failures

### SUMR.Plugin
- **Methods**: 0

### SUMD.Plugin
- **Methods**: 0

### OQLOS-REQUIREMENTS.Scenario
- **Methods**: 0

### OQLOS-REQUIREMENTS.Execution
- **Methods**: 0

### OQLOS-REQUIREMENTS.User
- **Methods**: 0

### OQLOS-REQUIREMENTS.Role
- **Methods**: 0

### OQLOS-REQUIREMENTS.Workflow
- **Methods**: 0

### OQLOS-REQUIREMENTS.Storage
- **Methods**: 0

### OQLOS-REQUIREMENTS.NotificationService
- **Methods**: 0

### OQLOS-REQUIREMENTS.AuditEntry
- **Methods**: 0

### OQLOS-REQUIREMENTS.WebhookDispatcher
- **Methods**: 0

### TODO.DiagnosticCheck
- **Methods**: 0

### TODO.BraceConverter
- **Methods**: 0

### TODO.FormatExtractor
- **Methods**: 0

### TODO.LessYamlAdapter
- **Methods**: 0

### doql.plugins.Plugin
- **Methods**: 0

### doql.cli.context.BuildContext
> Build context for doql commands.
- **Methods**: 0

### doql.cli.commands.workspace.DoqlProject
> Minimal project descriptor (used when taskfile is not installed).
- **Methods**: 0

### doql.cli.commands.doctor.Check
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### SUMR._parse_doc

### SUMD._parse_pyproject

### SUMD._parse_package_json

### SUMD._parse_goal_yaml

### SUMD._parse_makefile_deps

### SUMD._validate_output_written

### SUMD._check_parse

### SUMD.cmd_validate

### SUMD._parse_doql

### SUMD._cmd_validate

### SUMD.register_parser

### SUMD.create_parser

### SUMD.parse_intended

### SUMD._parse_doc

### SUMD._is_css_format

### SUMD.parse_file

### SUMD.parse_text

### SUMD.parse_env

### SUMD._parse_type_flags

### SUMD._parse_type_modifiers

### SUMD._parse_step_text

### SUMD._parse_selector

### SUMD.parse_css_file

### SUMD.parse_css_text

### SUMD._detect_format

## Behavioral Patterns

### recursion__walk_projects
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: doql.cli.commands.workspace._walk_projects

### recursion__clean
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: doql.utils.clean._clean

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `doql.cli.main.create_parser` - 83 calls
- `doql.cli.commands.workspace.register_parser` - 30 calls
- `doql.cli.sync.cmd_sync` - 23 calls
- `doql.generators.desktop_gen.generate` - 23 calls
- `doql.cli.lockfile.spec_section_hashes` - 22 calls
- `doql.cli.commands.init.cmd_init` - 22 calls
- `doql.cli.commands.drift.cmd_drift` - 22 calls
- `doql.cli.commands.run.cmd_run` - 22 calls
- `doql.cli.commands.doctor.cmd_doctor` - 21 calls
- `doql.generators.mobile_gen.generate` - 21 calls
- `doql.lsp_server.document_symbols` - 19 calls
- `doql.cli.sync.determine_regeneration_set` - 18 calls
- `doql.parsers.validators.validate` - 18 calls
- `doql.cli.commands.publish.cmd_publish` - 17 calls
- `doql.generators.workflow_gen.generate` - 16 calls
- `doql.lsp_server.definition` - 15 calls
- `doql.importers.yaml_importer.import_yaml` - 15 calls
- `doql.cli.commands.deploy.cmd_deploy` - 15 calls
- `doql.parsers.blocks.split_blocks` - 15 calls
- `doql.cli.commands.plan.cmd_plan` - 14 calls
- `doql.cli.commands.import_cmd.cmd_import` - 14 calls
- `doql.generators.ci_gen.generate` - 14 calls
- `doql.generators.export_ts_sdk.run` - 14 calls
- `doql.parsers.extractors.extract_entity_fields` - 14 calls
- `doql.cli.commands.export.cmd_export` - 13 calls
- `doql.lsp_server.completion` - 12 calls
- `doql.cli.commands.validate.cmd_validate` - 12 calls
- `doql.cli.commands.quadlet.cmd_quadlet` - 12 calls
- `doql.generators.i18n_gen.generate` - 12 calls
- `doql.generators.report_gen.generate` - 12 calls
- `doql.generators.api_gen.alembic.gen_initial_migration` - 12 calls
- `doql.adopt.scanner.scan_project` - 12 calls
- `doql.cli.commands.generate.cmd_generate` - 11 calls
- `doql.generators.document_gen.generate` - 11 calls
- `doql.generators.api_gen.models.gen_models` - 11 calls
- `doql.exporters.markdown.export_markdown` - 10 calls
- `doql.generators.web_gen.generate` - 10 calls
- `doql.parsers.extractors.extract_val` - 10 calls
- `doql.parsers.parse_env` - 10 calls
- `plugins.doql-plugin-fleet.doql_plugin_fleet.generate` - 9 calls

## System Interactions

How components interact:

```mermaid
graph TD
    register_parser --> add_parser
    register_parser --> add_subparsers
    register_parser --> _add_common
    register_parser --> add_argument
    cmd_sync --> build_context
    cmd_sync --> load_spec
    cmd_sync --> read_lockfile
    cmd_sync --> spec_section_hashes
    cmd_sync --> diff_sections
    generate --> next
    generate --> write_text
    cmd_init --> getattr
    cmd_init --> Path
    cmd_init --> exists
    cmd_init --> print
    cmd_init --> scaffold_from_templa
    cmd_drift --> getattr
    cmd_drift --> print
    cmd_drift --> resolve
    cmd_drift --> find_intended_file
    cmd_run --> getattr
    cmd_run --> call
    cmd_run --> resolve
    cmd_doctor --> resolve
    cmd_doctor --> getattr
    cmd_doctor --> print
    cmd_doctor --> DoctorReport
    generate --> mkdir
    document_symbols --> feature
    document_symbols --> get_text_document
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.