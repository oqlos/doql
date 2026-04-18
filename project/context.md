# System Architecture Analysis

## Overview

- **Project**: .
- **Primary Language**: python
- **Languages**: python: 117, shell: 3, javascript: 3, typescript: 1
- **Analysis Mode**: static
- **Total Functions**: 515
- **Total Classes**: 27
- **Modules**: 124
- **Entry Points**: 0

## Architecture by Module

### doql.parsers.registry
- **Functions**: 24
- **File**: `registry.py`

### doql.cli.commands.workspace
- **Functions**: 23
- **Classes**: 1
- **File**: `workspace.py`

### doql.importers.yaml_importer
- **Functions**: 22
- **File**: `yaml_importer.py`

### doql.parsers.css_mappers
- **Functions**: 19
- **File**: `css_mappers.py`

### doql.exporters.css.renderers
- **Functions**: 17
- **File**: `renderers.py`

### playground.pyodide-bridge
- **Functions**: 15
- **File**: `pyodide-bridge.js`

### doql.adopt.scanner.interfaces
- **Functions**: 14
- **File**: `interfaces.py`

### doql.parsers.extractors
- **Functions**: 14
- **File**: `extractors.py`

### doql.lsp_server
- **Functions**: 13
- **File**: `lsp_server.py`

### doql.cli.commands.doctor
- **Functions**: 12
- **Classes**: 2
- **File**: `doctor.py`

### doql.exporters.markdown.writers
- **Functions**: 11
- **File**: `writers.py`

### doql.generators.integrations_gen
- **Functions**: 11
- **File**: `integrations_gen.py`

### playground.renderers
- **Functions**: 10
- **File**: `renderers.js`

### doql.cli.commands.plan
- **Functions**: 10
- **File**: `plan.py`

### doql.adopt.scanner.workflows
- **Functions**: 10
- **File**: `workflows.py`

### doql.parsers.validators
- **Functions**: 10
- **File**: `validators.py`

### playground.app
- **Functions**: 9
- **File**: `app.js`

### doql.exporters.css
- **Functions**: 9
- **File**: `__init__.py`

### doql.exporters.markdown.sections
- **Functions**: 8
- **File**: `sections.py`

### doql.generators.web_gen
- **Functions**: 8
- **File**: `__init__.py`

## Key Entry Points

Main execution flows into the system:

## Process Flows

Key execution flows identified:

## Key Classes

### doql.cli.commands.doctor.DoctorReport
- **Methods**: 4
- **Key Methods**: doql.cli.commands.doctor.DoctorReport.add, doql.cli.commands.doctor.DoctorReport.ok, doql.cli.commands.doctor.DoctorReport.warnings, doql.cli.commands.doctor.DoctorReport.failures

### doql.cli.commands.doctor.Check
- **Methods**: 0

### doql.cli.context.BuildContext
> Build context for doql commands.
- **Methods**: 0

### doql.cli.commands.workspace.DoqlProject
> Minimal project descriptor (used when taskfile is not installed).
- **Methods**: 0

### doql.plugins.Plugin
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

## Data Transformation Functions

Key functions that process and transform data:

### doql.lsp_server._parse_doc
> Safely parse a document from its text content.
- **Output to**: doql_parser.parse_text

### doql.cli.main.create_parser
> Create and configure the argument parser with all subcommands.
- **Output to**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument, p.add_subparsers

### doql.cli.commands.validate.cmd_validate
> Validate .doql file and .env configuration.

Returns:
    0 if validation passes, 1 if there are err
- **Output to**: None.resolve, getattr, print, sum, sum

### doql.cli.commands.doctor._check_parse
> Parse the .doql file and report errors.
- **Output to**: report.add, doql_parser.parse_file, report.add, report.add, len

### doql.cli.commands.adopt._validate_output_written
> Check that output file was written successfully.
- **Output to**: print, print, output.exists, output.stat

### doql.cli.commands.workspace._parse_doql
- **Output to**: re.findall, re.findall, re.findall, re.findall, re.search

### doql.cli.commands.workspace._cmd_validate
- **Output to**: doql.cli.commands.workspace._cmd_analyze, None.resolve, _tf_discover, doql.cli.commands.workspace._print, _tf_validate

### doql.cli.commands.workspace.register_parser
> Register `workspace` subcommands on the main doql parser.
- **Output to**: sub.add_parser, ws.add_subparsers, ws_sub.add_parser, _add_common, p.add_argument

### doql.adopt.scanner.metadata._parse_pyproject
> Extract metadata from pyproject.toml (stdlib tomllib).
- **Output to**: data.get, project.get, project.get, project.get, scripts.items

### doql.adopt.scanner.metadata._parse_package_json
> Extract metadata from package.json.
- **Output to**: json.loads, data.get, data.get, path.read_text

### doql.adopt.scanner.metadata._parse_goal_yaml
> Extract metadata from goal.yaml if present.
- **Output to**: yaml.safe_load, path.read_text

### doql.parsers.css_tokenizer._parse_declarations
> Extract property: value pairs from a CSS block body (top-level only).

Handles multi-line declaratio
- **Output to**: body.splitlines, line.strip, re.match, doql.parsers.css_utils._strip_quotes, line.count

### doql.adopt.scanner.workflows._parse_makefile_deps
> Split the ``deps`` portion of ``target: dep1 dep2 ## comment``.

Strips trailing ``## help`` comment
- **Output to**: deps_raw.split, text.split, tok.startswith

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

### doql.parsers.css_transformers._convert_indent_to_braces
> Convert indent-based SASS blocks to brace-delimited CSS.
- **Output to**: line.strip, stripped.endswith, is_step_line, re.match, stripped.endswith

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

### doql.parsers.css_parser._parse_selector
> Parse a CSS-like selector into structured form.

Examples:
    "app" → type="app"
    'entity[name="
- **Output to**: None.split, ParsedSelector, re.match, re.finditer, selector.strip

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `doql.cli.main.create_parser` - 67 calls
- `doql.cli.commands.workspace.register_parser` - 30 calls
- `doql.cli.sync.cmd_sync` - 23 calls
- `doql.generators.desktop_gen.generate` - 23 calls
- `doql.generators.api_gen.alembic.gen_initial_migration` - 23 calls
- `doql.cli.commands.init.cmd_init` - 22 calls
- `doql.cli.commands.run.cmd_run` - 22 calls
- `doql.adopt.scanner.databases.scan_databases` - 22 calls
- `doql.generators.mobile_gen.generate` - 21 calls
- `doql.cli.lockfile.spec_section_hashes` - 19 calls
- `doql.lsp_server.document_symbols` - 19 calls
- `doql.cli.commands.export.cmd_export` - 19 calls
- `doql.cli.commands.doctor.cmd_doctor` - 19 calls
- `doql.cli.sync.determine_regeneration_set` - 18 calls
- `doql.adopt.scanner.integrations.scan_integrations` - 18 calls
- `doql.lsp_server.hover` - 17 calls
- `doql.cli.commands.publish.cmd_publish` - 17 calls
- `doql.generators.workflow_gen.generate` - 16 calls
- `doql.parsers.validators.validate` - 16 calls
- `doql.importers.yaml_importer.import_yaml` - 15 calls
- `doql.lsp_server.definition` - 15 calls
- `doql.cli.commands.validate.cmd_validate` - 15 calls
- `doql.parsers.blocks.split_blocks` - 15 calls
- `doql.cli.commands.plan.cmd_plan` - 14 calls
- `doql.cli.commands.import_cmd.cmd_import` - 14 calls
- `doql.generators.export_ts_sdk.run` - 14 calls
- `doql.adopt.scanner.roles.scan_roles` - 14 calls
- `doql.parsers.extractors.extract_entity_fields` - 14 calls
- `doql.cli.commands.adopt.cmd_adopt` - 13 calls
- `doql.lsp_server.completion` - 12 calls
- `doql.generators.i18n_gen.generate` - 12 calls
- `doql.generators.report_gen.generate` - 12 calls
- `doql.adopt.scanner.scan_project` - 12 calls
- `doql.cli.commands.generate.cmd_generate` - 11 calls
- `doql.generators.document_gen.generate` - 11 calls
- `doql.generators.api_gen.models.gen_models` - 11 calls
- `doql.exporters.markdown.export_markdown` - 10 calls
- `doql.generators.web_gen.generate` - 10 calls
- `doql.adopt.scanner.entities.scan_entities` - 10 calls
- `doql.parsers.extractors.extract_val` - 10 calls

## System Interactions

How components interact:

```mermaid
graph TD
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.