# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/oqlos/doql
- **Primary Language**: python
- **Languages**: python: 157, yaml: 32, json: 16, yml: 14, doql: 13
- **Analysis Mode**: static
- **Total Functions**: 1430
- **Total Classes**: 31
- **Modules**: 247
- **Entry Points**: 973

## Architecture by Module

### project.map.toon
- **Functions**: 1439
- **File**: `map.toon.yaml`

### doql.parsers.registry
- **Functions**: 30
- **File**: `registry.py`

### doql.importers.yaml_importer
- **Functions**: 22
- **File**: `yaml_importer.py`

### doql.exporters.css.renderers
- **Functions**: 19
- **File**: `renderers.py`

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

### doql.cli.commands.doctor.checks
- **Functions**: 12
- **File**: `checks.py`

### doql.cli.commands.adopt
- **Functions**: 11
- **File**: `adopt.py`

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

### playground.renderers
- **Functions**: 10
- **File**: `renderers.js`

### doql.cli.commands.plan
- **Functions**: 10
- **File**: `plan.py`

### playground.app
- **Functions**: 9
- **File**: `app.js`

### doql.exporters.css
- **Functions**: 9
- **File**: `__init__.py`

### doql.adopt.scanner.deploy
- **Functions**: 9
- **File**: `deploy.py`

### doql.cli.commands.workspace.analyze
- **Functions**: 9
- **File**: `analyze.py`

## Key Entry Points

Main execution flows into the system:

### doql.cli.commands.workspace.register_parser
> Register `workspace` subcommands on the main doql parser.
- **Calls**: sub.add_parser, ws.add_subparsers, ws_sub.add_parser, _add_common, p.add_argument, p.add_argument, p.set_defaults, ws_sub.add_parser

### doql.cli.commands.drift.render._render_rich
> Pretty-print a drift report with rich. Falls back silently if rich
is unavailable (we pulled it in as a hard dep, but be robust).
- **Calls**: Console, console.print, summary.get, summary.get, summary.get, None.join, console.print, Table

### doql.parsers.css_transformers.indent._convert_indent_to_braces
> Convert indent-based SASS blocks to brace-delimited CSS.
- **Calls**: len, line.rstrip, doql.parsers.css_transformers.indent._close_indent_blocks, project.map.toon._is_step_line, project.map.toon._is_selector_starter, indent_stack.pop, result_lines.append, len

### doql.cli.sync.cmd_sync
> Selective rebuild — only regenerate sections that changed since last build.
- **Calls**: doql.cli.context.build_context, doql.cli.context.load_spec, doql.cli.lockfile.read_lockfile, doql.cli.lockfile.spec_section_hashes, doql.cli.lockfile.diff_sections, doql.cli.sync.determine_regeneration_set, print, print

### doql.generators.desktop_gen.generate
> Generate desktop (Tauri) layer files into *out* directory.
- **Calls**: next, None.write_text, None.write_text, None.write_text, None.write_text, None.write_text, print, print

### doql.cli.commands.init.cmd_init
> Create new project from template.

With --list-templates, shows available templates and exits.
- **Calls**: getattr, pathlib.Path, target.exists, print, doql.cli.context.scaffold_from_template, print, print, print

### doql.cli.commands.run.cmd_run
> Run project locally in dev mode.

With -f <file>: build on-the-fly into .doql/ and run target.
Without -f: use existing project build/ directory.
With
- **Calls**: getattr, getattr, getattr, subprocess.call, None.resolve, doql.cli.commands.run._workspace_for_file, workspace.mkdir, print

### doql.generators.mobile_gen.generate
> Generate mobile PWA into *out* directory.
- **Calls**: next, out.mkdir, None.write_text, None.write_text, None.write_text, None.write_text, None.write_text, doql.generators.mobile_gen._gen_icons

### doql.cli.commands.doctor.cmd_doctor
> Run comprehensive project health check.
- **Calls**: None.resolve, getattr, getattr, print, DoctorReport, project.map.toon._check_parse, project.map.toon._check_env, project.map.toon._check_files

### doql.generators.infra_gen.docker._gen_docker_compose
- **Calls**: doql.utils.naming.slug, env_vars.get, any, lines.append, None.write_text, print, textwrap.dedent, None.write_text

### doql.lsp_server.document_symbols
- **Calls**: server.feature, ls.workspace.get_text_document, doql.lsp_server._parse_doc, doql.lsp_server._find_line_col, lsp.Range, _mkrange, symbols.append, _mkrange

### doql.cli.commands.drift.cmd_drift
> Compare intended (``app.doql``) with actual device scan.
- **Calls**: None.resolve, getattr, getattr, getattr, doql.drift.detector.detect_drift, intended_file.exists, print, project.map.toon._report_to_json

### doql.generators.infra_gen.kubernetes._gen_kubernetes
- **Calls**: doql.utils.naming.slug, textwrap.dedent, None.write_text, print, textwrap.dedent, None.write_text, print, textwrap.dedent

### doql.parsers.validators.validate
> Validate a parsed DoqlSpec against env vars and internal consistency.
- **Calls**: issues.extend, issues.extend, issues.extend, issues.extend, issues.extend, issues.extend, doql.parsers.validators._validate_app_name, doql.parsers.validators._validate_env_refs

### doql.generators.infra_gen.quadlet._gen_quadlet
- **Calls**: doql.utils.naming.slug, env_vars.get, textwrap.dedent, None.write_text, print, textwrap.dedent, None.write_text, print

### doql.cli.commands.publish.cmd_publish
> Publish project artifacts to registries.
- **Calls**: doql.cli.context.build_context, doql.cli.context.load_spec, getattr, getattr, print, print, list, print

### doql.generators.workflow_gen.generate
> Generate workflow engine modules.
- **Calls**: wf_dir.mkdir, None.write_text, None.write_text, print, None.write_text, print, None.write_text, print

### doql.lsp_server.definition
- **Calls**: server.feature, ls.workspace.get_text_document, doql.lsp_server._word_at, re.compile, pattern.search, None.count, None.find, lsp.Location

### doql.cli.commands.deploy.cmd_deploy
> Deploy project to target environment.

Priority: redeploy API → redeploy CLI → @directives → docker-compose.
Install redeploy support: pip install doq
- **Calls**: doql.cli.context.build_context, doql.cli.context.load_spec, getattr, getattr, print, migration_yaml.exists, deploy_gen.run, getattr

### doql.cli.commands.workspace.analyze._cmd_fix
- **Calls**: None.resolve, _tf_discover, project.map.toon._print, project.map.toon._print, project.map.toon._print, _tf_filter, _tf_fix, None.expanduser

### doql.cli.commands.plan.cmd_plan
> Show dry-run plan of what would be generated.

Displays project overview including entities, data sources, interfaces,
and estimated file counts per i
- **Calls**: None.resolve, doql_parser.parse_file, doql.cli.commands.plan._print_header, doql.cli.commands.plan._print_entities, doql.cli.commands.plan._print_data_sources, doql.cli.commands.plan._print_documents, doql.cli.commands.plan._print_api_clients, doql.cli.commands.plan._print_summary

### doql.cli.commands.import_cmd.cmd_import
> Import a YAML spec file and convert to DOQL format.
- **Calls**: None.resolve, getattr, doql.importers.yaml_importer.import_yaml_file, print, source.exists, print, None.resolve, None.replace

### doql.generators.ci_gen.generate
> Generate CI configuration files based on ci_configs or fallback to GitHub Actions.
- **Calls**: gh_dir.mkdir, None.write_text, print, doql.generators.ci_gen._gen_github_action, None.write_text, print, doql.generators.ci_gen._gen_gitlab_ci, None.write_text

### doql.generators.export_ts_sdk.run
> Write TypeScript SDK to the given stream.
- **Calls**: out.write, out.write, out.write, name.lower, out.write, out.write, out.write, out.write

### doql.parsers.registry._handle_data
- **Calls**: doql.parsers.registry.register, None.strip, spec.data_sources.append, doql.parsers.extractors.extract_val, DataSource, header.split, doql.parsers.extractors.extract_val, doql.parsers.extractors.extract_val

### doql.cli.commands.export.cmd_export
> Export project specification to various formats.
- **Calls**: None.resolve, getattr, _EXPORTERS.get, doql_parser.parse_file, getattr, doql.parsers.detect_doql_file, print, open

### doql.parsers.registry._handle_api_client
- **Calls**: doql.parsers.registry.register, None.strip, doql.parsers.extractors.extract_val, spec.api_clients.append, ApiClient, header.split, doql.parsers.extractors.extract_val, doql.parsers.extractors.extract_val

### doql.parsers.css_mappers.entity._map_data_source
> Map CSS block to DataSource definition.
- **Calls**: sel.attributes.get, DataSource, spec.data_sources.append, block.declarations.get, block.declarations.get, block.declarations.get, block.declarations.get, block.declarations.get

### doql.cli.commands.workspace.run._cmd_run
> Run `doql <action>` in each project with app.doql.css.
- **Calls**: None.resolve, doql.cli.commands.workspace.run._select_run_projects, project.map.toon._print, enumerate, doql.cli.commands.workspace.run._print_run_summary, project.map.toon._print, doql.cli.commands.workspace.run._print_dry_run_commands, doql.cli.commands.workspace.run._execute_single_project

### doql.lsp_server.completion
- **Calls**: server.feature, ls.workspace.get_text_document, doql.lsp_server._parse_doc, lsp.CompletionList, lsp.CompletionOptions, items.append, items.append, lsp.CompletionItem

## Process Flows

Key execution flows identified:

### Flow 1: register_parser
```
register_parser [doql.cli.commands.workspace]
```

### Flow 2: _render_rich
```
_render_rich [doql.cli.commands.drift.render]
```

### Flow 3: _convert_indent_to_braces
```
_convert_indent_to_braces [doql.parsers.css_transformers.indent]
  └─> _close_indent_blocks
  └─ →> _is_step_line
  └─ →> _is_selector_starter
```

### Flow 4: cmd_sync
```
cmd_sync [doql.cli.sync]
  └─ →> build_context
      └─ →> detect_doql_file
  └─ →> load_spec
  └─ →> read_lockfile
```

### Flow 5: generate
```
generate [doql.generators.desktop_gen]
```

### Flow 6: cmd_init
```
cmd_init [doql.cli.commands.init]
  └─ →> scaffold_from_template
```

### Flow 7: cmd_run
```
cmd_run [doql.cli.commands.run]
```

### Flow 8: cmd_doctor
```
cmd_doctor [doql.cli.commands.doctor]
```

### Flow 9: _gen_docker_compose
```
_gen_docker_compose [doql.generators.infra_gen.docker]
  └─ →> slug
```

### Flow 10: document_symbols
```
document_symbols [doql.lsp_server]
  └─> _parse_doc
  └─> _find_line_col
```

## Key Classes

### doql.cli.commands.doctor.report.DoctorReport
- **Methods**: 4
- **Key Methods**: doql.cli.commands.doctor.report.DoctorReport.add, doql.cli.commands.doctor.report.DoctorReport.ok, doql.cli.commands.doctor.report.DoctorReport.warnings, doql.cli.commands.doctor.report.DoctorReport.failures

### doql.plugins.Plugin
- **Methods**: 0

### doql.cli.context.BuildContext
> Build context for doql commands.
- **Methods**: 0

### doql.parsers.css_utils.CssBlock
> Single CSS-like rule: selector + key-value declarations.
- **Methods**: 0

### doql.parsers.css_utils.ParsedSelector
> Decomposed CSS selector.
- **Methods**: 0

### doql.parsers.models.DoqlParseError
> Raised when a .doql file cannot be parsed.
- **Methods**: 0
- **Inherits**: Exception

### doql.parsers.models.ValidationIssue
- **Methods**: 0

### doql.parsers.models.EntityField
- **Methods**: 0

### doql.parsers.models.Entity
- **Methods**: 0

### doql.parsers.models.DataSource
- **Methods**: 0

### doql.parsers.models.Template
- **Methods**: 0

### doql.parsers.models.Document
- **Methods**: 0

### doql.parsers.models.Report
- **Methods**: 0

### doql.parsers.models.Database
- **Methods**: 0

### doql.parsers.models.ApiClient
- **Methods**: 0

### doql.parsers.models.Webhook
- **Methods**: 0

### doql.parsers.models.Page
- **Methods**: 0

### doql.parsers.models.Interface
- **Methods**: 0

### doql.parsers.models.Integration
- **Methods**: 0

### doql.parsers.models.WorkflowStep
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### doql.lsp_server._parse_doc
> Safely parse a document from its text content.
- **Output to**: doql_parser.parse_text

### doql.drift.detector.parse_intended
> Parse a ``.doql.less`` file into an :class:`opstree.PartialSnapshot`.

Raises :class:`FileNotFoundEr
- **Output to**: require_op3, path.read_text, partial.model_copy, path.is_file, FileNotFoundError

### doql.cli.commands.validate.cmd_validate
> Validate .doql file and .env configuration.

Returns:
    0 if validation passes, 1 if there are err
- **Output to**: None.resolve, getattr, print, doql.cli.commands.validate._print_issues, doql.parsers.detect_doql_file

### doql.cli.commands.adopt._validate_output_written
> Check that output file was written successfully.
- **Output to**: print, print, output.exists, output.stat

### doql.adopt.scanner.metadata._parse_pyproject
> Extract metadata from pyproject.toml (stdlib tomllib).
- **Output to**: data.get, project.get, project.get, project.get, doql.adopt.scanner.metadata._extract_authors

### doql.adopt.scanner.metadata._parse_package_json
> Extract metadata from package.json.
- **Output to**: json.loads, data.get, data.get, path.read_text

### doql.adopt.scanner.metadata._parse_goal_yaml
> Extract metadata from goal.yaml if present.
- **Output to**: yaml.safe_load, path.read_text

### doql.adopt.scanner.workflows._parse_makefile_deps
> Split the ``deps`` portion of ``target: dep1 dep2 ## comment``.

Strips trailing ``## help`` comment
- **Output to**: deps_raw.split, text.split, tok.startswith

### doql.parsers.css_tokenizer._process_decl_line
> Process one stripped declaration line; return updated (pending_key, pending_value).
- **Output to**: re.match, None.endswith, None.endswith, doql.parsers.css_tokenizer._consume_pending, m.group

### doql.parsers.css_tokenizer._parse_declarations
> Extract property: value pairs from a CSS block body (top-level only).

Handles multi-line declaratio
- **Output to**: body.splitlines, line.strip, line.count, line.count, s.strip

### doql.parsers.css_parser.parse_css_file
> Parse a .doql.css / .doql.less / .doql.sass file into DoqlSpec.
- **Output to**: path.read_text, doql.parsers.css_parser.parse_css_text, path.exists, DoqlParseError, doql.parsers.css_parser._detect_format

### doql.parsers.css_parser.parse_css_text
> Parse CSS-like DOQL source text into a DoqlSpec.
- **Output to**: doql.parsers.css_utils._strip_comments, doql.parsers.css_tokenizer._tokenise_css, doql.parsers.css_parser._map_to_spec, doql.parsers.extractors.collect_env_refs, project.map.toon._resolve_less_vars

### doql.parsers.css_parser._detect_format
> Detect format from file extension.
- **Output to**: path.name.lower, name.endswith, name.endswith

### doql.parsers.extractors._extract_page_from_format1
> Extract pages using PAGE keyword format.
- **Output to**: re.finditer, m.group, m.end, re.search, re.search

### doql.parsers.extractors._extract_page_from_format2
> Extract pages using PAGES: YAML list format.
- **Output to**: re.search, len, re.search, first_item.group, re.compile

### doql.parsers.extractors._parse_field_flags
> Parse field flags from type string.
- **Output to**: ftype_raw.lower, ftype_raw.lower, ftype_raw.lower

### doql.parsers.extractors._parse_field_ref
> Extract reference entity from type string.
- **Output to**: re.search, ref_m.group

### doql.parsers.extractors._parse_field_default
> Extract default value from type string.
- **Output to**: re.search, default_m.group

### doql.parsers.extractors._parse_field_type
> Extract clean base type from type string.
- **Output to**: re.split

### doql.parsers._is_css_format
> Check if a path uses one of the CSS-like DOQL formats.
- **Output to**: path.name.lower, any, name.endswith

### doql.parsers.parse_file
> Parse a .doql / .doql.css / .doql.less / .doql.sass file into a DoqlSpec.
- **Output to**: doql.parsers._is_css_format, doql.parsers.parse_text, path.exists, DoqlParseError, doql.parsers.css_parser.parse_css_file

### doql.parsers.parse_text
> Parse .doql source text into a DoqlSpec (in-memory, no disk I/O).

Uses error recovery: malformed bl
- **Output to**: DoqlSpec, doql.parsers.extractors.collect_env_refs, doql.parsers.blocks.split_blocks, doql.parsers.blocks.apply_block, spec.parse_errors.append

### doql.parsers.parse_env
> Parse a .env file into a dict. Missing file → empty dict.
- **Output to**: None.splitlines, path.exists, line.strip, path.read_text, line.startswith

### doql.parsers.css_utils._parse_list
> Parse '[a, b, c]' or 'a, b, c' into a list.
- **Output to**: None.strip, None.strip, val.strip, val.split, v.strip

### doql.parsers.css_utils._parse_selector
> Parse a CSS-like selector into structured form.

Examples:
    "app" → type="app"
    'entity[name="
- **Output to**: None.split, ParsedSelector, re.match, selector.strip, None.lower

## Behavioral Patterns

### recursion__clean
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: doql.utils.clean._clean

### recursion__walk_projects
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: doql.cli.commands.workspace.discovery._walk_projects

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `doql.cli.main.create_parser` - 84 calls
- `doql.cli.commands.workspace.register_parser` - 30 calls
- `doql.cli.sync.cmd_sync` - 23 calls
- `doql.generators.desktop_gen.generate` - 23 calls
- `doql.cli.lockfile.spec_section_hashes` - 22 calls
- `doql.cli.commands.init.cmd_init` - 22 calls
- `doql.cli.commands.run.cmd_run` - 22 calls
- `doql.generators.mobile_gen.generate` - 21 calls
- `doql.cli.commands.doctor.cmd_doctor` - 21 calls
- `doql.lsp_server.document_symbols` - 19 calls
- `doql.cli.commands.drift.cmd_drift` - 19 calls
- `doql.cli.sync.determine_regeneration_set` - 18 calls
- `doql.parsers.validators.validate` - 18 calls
- `doql.adopt.scanner.interfaces.cli.scan_python_cli` - 18 calls
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
- `doql.adopt.scanner.interfaces.desktop.scan_desktop` - 14 calls
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
- `doql.adopt.scanner.interfaces.mobile.scan_mobile` - 11 calls
- `doql.exporters.markdown.export_markdown` - 10 calls
- `doql.generators.web_gen.generate` - 10 calls

## System Interactions

How components interact:

```mermaid
graph TD
    register_parser --> add_parser
    register_parser --> add_subparsers
    register_parser --> _add_common
    register_parser --> add_argument
    _render_rich --> Console
    _render_rich --> print
    _render_rich --> get
    _convert_indent_to_b --> len
    _convert_indent_to_b --> rstrip
    _convert_indent_to_b --> _close_indent_blocks
    _convert_indent_to_b --> _is_step_line
    _convert_indent_to_b --> _is_selector_starter
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
    cmd_run --> getattr
    cmd_run --> call
    cmd_run --> resolve
    generate --> mkdir
    cmd_doctor --> resolve
    cmd_doctor --> getattr
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.