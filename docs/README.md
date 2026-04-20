<!-- code2docs:start --># doql

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-566-green)
> **566** functions | **27** classes | **129** files | CC̄ = 3.5

> Auto-generated project documentation from source code analysis.

**Author:** Softreck  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/oqlos/doql](https://github.com/oqlos/doql)

## Installation

### From PyPI

```bash
pip install doql
```

### From Source

```bash
git clone https://github.com/oqlos/doql
cd doql
pip install -e .
```

### Optional Extras

```bash
pip install doql[dev]    # development tools
pip install doql[api]    # api features
pip install doql[lsp]    # lsp features
pip install doql[deploy]    # deploy features
```

## Quick Start

### CLI Usage

```bash
# Generate full documentation for your project
doql ./my-project

# Only regenerate README
doql ./my-project --readme-only

# Preview what would be generated (no file writes)
doql ./my-project --dry-run

# Check documentation health
doql check ./my-project

# Sync — regenerate only changed modules
doql sync ./my-project
```

### Python API

```python
from doql import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```




## Architecture

```
doql/
├── tree
├── project
├── doql/
        ├── doql_plugin_shared/
            ├── drift_monitor
    ├── serve
    ├── pyodide-bridge
    ├── renderers
    ├── app
        ├── extension
    ├── cli/
            ├── base
            ├── readme
    ├── parser
    ├── importers/
        ├── doql_plugin_gxp/
            ├── metrics
            ├── tenant
        ├── __main__
            ├── ota
        ├── sync
    ├── lsp_server
        ├── main
            ├── render
        ├── lockfile
        ├── yaml_importer
            ├── validate
            ├── export
            ├── query
            ├── init
            ├── kiosk
            ├── plan
        ├── commands/
            ├── generate
            ├── adopt
            ├── quadlet
            ├── uncertainty
            ├── deploy
            ├── import_cmd
        ├── css_exporter
    ├── exporters/
            ├── docs
        ├── doql_plugin_fleet/
        ├── markdown_exporter
        ├── yaml_exporter
            ├── run
            ├── helpers
            ├── publish
        ├── markdown/
            ├── writers
        ├── css/
            ├── format_convert
        ├── docs_gen
        ├── ci_gen
        ├── export_postman
            ├── sections
    ├── generators/
        ├── infra_gen
        ├── document_gen
        ├── desktop_gen
        ├── export_ts_sdk
            ├── migration
        ├── deploy
        ├── api_gen/
        ├── web_gen/
            ├── renderers
        ├── workflow_gen
        ├── integrations_gen
        ├── i18n_gen
            ├── codegen
            ├── common
        ├── mobile_gen
            ├── components
            ├── pwa
            ├── config
            ├── router
            ├── core
        ├── doql_plugin_iso17025/
        ├── report_gen
            ├── doctor
            ├── pages
            ├── auth
            ├── database
            ├── alembic
            ├── schemas
    ├── utils/
            ├── common
        ├── naming
        ├── clean
        ├── scanner/
            ├── routes
        ├── emitter
            ├── main
    ├── adopt/
            ├── integrations
            ├── device_registry
            ├── models
            ├── roles
            ├── databases
            ├── deploy
            ├── metadata
            ├── utils
        ├── blocks
            ├── certificate
            ├── migration
        ├── css_tokenizer
            ├── workflows
            ├── interfaces
    ├── parsers/
            ├── entities
            ├── environments
        ├── context
        ├── css_parser
            ├── traceability
        ├── validators
        ├── extractors
        ├── css_transformers
        ├── registry
        ├── doql_plugin_erp/
        ├── css_mappers
        ├── css_utils
            ├── workspace
    ├── plugins
        ├── models
```

## API Overview

### Classes

- **`Check`** — —
- **`DoctorReport`** — —
- **`BuildContext`** — Build context for doql commands.
- **`CssBlock`** — Single CSS-like rule: selector + key-value declarations.
- **`ParsedSelector`** — Decomposed CSS selector.
- **`DoqlProject`** — Minimal project descriptor (used when taskfile is not installed).
- **`Plugin`** — —
- **`DoqlParseError`** — Raised when a .doql file cannot be parsed.
- **`ValidationIssue`** — —
- **`EntityField`** — —
- **`Entity`** — —
- **`DataSource`** — —
- **`Template`** — —
- **`Document`** — —
- **`Report`** — —
- **`Database`** — —
- **`ApiClient`** — —
- **`Webhook`** — —
- **`Page`** — —
- **`Interface`** — —
- **`Integration`** — —
- **`WorkflowStep`** — —
- **`Workflow`** — —
- **`Role`** — —
- **`Deploy`** — —
- **`Environment`** — —
- **`DoqlSpec`** — —

### Functions

- `usage()` — —
- `generate()` — Generate drift_monitor.py module content.
- `pyodide()` — —
- `buildFn()` — —
- `debounceTimer()` — —
- `initElements()` — —
- `isReady()` — —
- `debouncedBuild()` — —
- `executeBuild()` — —
- `r()` — —
- `resp()` — —
- `src()` — —
- `bootPyodide()` — —
- `version()` — —
- `escapeHtml()` — —
- `renderFatal()` — —
- `renderDiagnostics()` — —
- `loc()` — —
- `renderAst()` — —
- `renderEnv()` — —
- `refs()` — —
- `keys()` — —
- `marker()` — —
- `renderFiles()` — —
- `TAB_NAMES()` — —
- `activateTab()` — —
- `tabFromHash()` — —
- `name()` — —
- `initial()` — —
- `key()` — —
- `updateStats()` — —
- `lines()` — —
- `chars()` — —
- `activate()` — —
- `config()` — —
- `serverPath()` — —
- `deactivate()` — —
- `plugin_generate(out, modules, readme_content)` — Common plugin generate() — iterates over modules dict and writes files.
- `generate_readme(plugin_name, modules, description, usage_extra)` — Generate standard README.md content for a doql plugin.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `determine_regeneration_set(diff_result, spec)` — Determine which generators need to re-run based on diff.
- `run_generators(regen, spec, env_vars, ctx)` — Run selected generators based on regen set. Returns count of generators run.
- `cmd_sync(args)` — Selective rebuild — only regenerate sections that changed since last build.
- `did_open(ls, params)` — —
- `did_change(ls, params)` — —
- `did_save(ls, params)` — —
- `completion(ls, params)` — —
- `hover(ls, params)` — —
- `definition(ls, params)` — —
- `document_symbols(ls, params)` — —
- `main()` — —
- `create_parser()` — Create and configure the argument parser with all subcommands.
- `main()` — Main entry point for doql CLI.
- `cmd_render(args)` — Render a template with DATA sources.
- `spec_section_hashes(spec, ctx)` — Compute per-section hashes for diff detection.
- `read_lockfile(ctx)` — Read and parse lockfile if it exists.
- `diff_sections(old_hashes, new_hashes)` — Return dict of changed/added/removed section keys.
- `write_lockfile(spec, ctx)` — Write current spec hashes to lockfile.
- `import_yaml(data)` — Build a DoqlSpec from a YAML-style dictionary.
- `import_yaml_text(text)` — Parse YAML text and return a DoqlSpec.
- `import_yaml_file(path)` — Read a YAML file and return a DoqlSpec.
- `cmd_validate(args)` — Validate .doql file and .env configuration.
- `cmd_export(args)` — Export project specification to various formats.
- `cmd_query(args)` — Query a DATA source and output as JSON.
- `cmd_init(args)` — Create new project from template.
- `cmd_kiosk(args)` — Manage kiosk appliance installation.
- `cmd_plan(args)` — Show dry-run plan of what would be generated.
- `cmd_generate(args)` — Generate a single document/artifact.
- `cmd_adopt(args)` — Scan *target* directory, produce app.doql.{css|less|sass}.
- `cmd_quadlet(args)` — Manage Podman Quadlet containers.
- `generate()` — Generate uncertainty.py module content.
- `cmd_deploy(args)` — Deploy project to target environment.
- `cmd_import(args)` — Import a YAML spec file and convert to DOQL format.
- `cmd_docs(args)` — Generate documentation site from .doql spec.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `spec_to_dict(spec)` — Convert DoqlSpec to a cleaned dictionary suitable for YAML/JSON.
- `export_yaml(spec, out)` — Write DoqlSpec as YAML to the given stream.
- `export_yaml_file(spec, path)` — Write DoqlSpec as YAML to a file.
- `cmd_run(args)` — Run project locally in dev mode.
- `cmd_publish(args)` — Publish project artifacts to registries.
- `export_markdown(spec, out)` — Write DoqlSpec as Markdown documentation to the given stream.
- `export_markdown_file(spec, path)` — Write DoqlSpec as Markdown to a file.
- `export_css(spec, out)` — Write DoqlSpec as .doql.css format.
- `export_less(spec, out)` — Write DoqlSpec as .doql.less format.
- `export_sass(spec, out)` — Write DoqlSpec as .doql.sass format.
- `export_css_file(spec, path, fmt)` — Write DoqlSpec to a CSS-like file. fmt is 'css', 'less', or 'sass'.
- `generate(spec, out)` — Generate documentation files into *out* directory.
- `generate(spec, env_vars, out)` — Generate CI configuration files.
- `run(spec, out)` — Write Postman collection JSON to the given stream.
- `generate(spec, env_vars, out)` — Generate infra layer files into *out* directory.
- `generate(spec, env_vars, out, project_root)` — Generate document rendering pipeline into *out* directory.
- `generate(spec, env_vars, out)` — Generate desktop (Tauri) layer files into *out* directory.
- `run(spec, out)` — Write TypeScript SDK to the given stream.
- `generate()` — Generate migration.py module content.
- `run(ctx, target_env)` — Deploy the built application.
- `generate(spec, env_vars, out)` — Generate workflow engine modules.
- `generate(spec, env_vars, out)` — Generate integration service modules.
- `generate(spec, env_vars, out)` — Generate i18n translation files.
- `write_code_block(content, path)` — Write a code block to file, creating parent directories if needed.
- `generate_file_from_template(template_name, variables, output_path)` — Generate a file from a template with variable substitution.
- `generate(spec, env_vars, out)` — Generate mobile PWA into *out* directory.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate(spec, env_vars, out)` — Generate report scripts into *out* directory.
- `cmd_doctor(args)` — Run comprehensive project health check.
- `gen_auth(spec)` — Generate JWT authentication module.
- `gen_database(spec, env_vars)` — Generate database.py with SQLAlchemy engine and session.
- `gen_alembic_ini()` — Generate alembic.ini configuration file.
- `gen_alembic_env()` — Generate alembic/env.py migration environment.
- `gen_initial_migration(spec)` — Generate initial Alembic migration with all tables.
- `generate(spec, env_vars, out)` — Generate React + Vite + TailwindCSS frontend into *out* directory.
- `gen_schemas(spec)` — Generate Pydantic schemas from DoqlSpec using delegation pattern.
- `sa_type(f)` — Get SQLAlchemy type for a field.
- `py_type(f)` — Get Python/Pydantic type for a field.
- `py_default(f)` — Get default value assignment for a field.
- `safe_name(name)` — Return a valid Python identifier from *name*.
- `snake(name)` — Convert CamelCase to snake_case.
- `snake(name)` — Convert CamelCase to snake_case (also handles spaces).
- `kebab(name)` — Convert CamelCase or snake_case to kebab-case.
- `gen_routes(spec)` — Generate CRUD routes for all entities in the spec.
- `emit_css(spec, output)` — Write *spec* as `app.doql.css` to *output* path.
- `emit_spec(spec, output, fmt)` — Write *spec* to *output* path in given format (css/less/sass).
- `gen_main(spec)` — Generate FastAPI main application file.
- `gen_requirements(has_auth)` — Generate requirements.txt with pinned dependencies.
- `scan_project(root)` — Scan *root* directory and return a reverse-engineered DoqlSpec.
- `scan_integrations(root, spec)` — Detect external integrations from .env and code.
- `generate(spec, env_vars, out)` — Generate API layer files into *out* directory.
- `export_openapi(spec, out)` — Write OpenAPI 3.1 JSON to the given stream.
- `gen_models(spec)` — Generate SQLAlchemy ORM models from DoqlSpec.
- `scan_roles(root, spec)` — Detect roles from env vars or code patterns.
- `scan_databases(root, spec)` — Detect database setup from docker-compose, .env, config files.
- `scan_deploy(root, spec)` — Detect deployment infrastructure.
- `scan_metadata(root, spec)` — Extract app name, version, domain from config files.
- `load_yaml(path)` — Safely load a YAML file.
- `find_compose(root)` — Find docker-compose file.
- `find_dockerfiles(root)` — Find all Dockerfiles.
- `camel_to_kebab(name)` — Convert CamelCase/PascalCase to kebab-case.
- `snake_to_pascal(name)` — Convert snake_case to PascalCase.
- `normalize_python_type(t)` — Normalize Python type annotations to DOQL types.
- `normalize_sqlalchemy_type(t)` — Normalize SQLAlchemy Column types to DOQL types.
- `normalize_sql_type(t)` — Normalize SQL column types to DOQL types using pattern matching.
- `split_blocks(text)` — Split .doql text into (keyword, rest_of_header, body, start_line) blocks.
- `apply_block(spec, keyword, header, body)` — Apply a single parsed block to *spec* using the registry dispatch.
- `generate()` — Generate certificate.py module content.
- `scan_workflows(root, spec)` — Promote Makefile / Taskfile.yml targets and Python CLI commands to ``WORKFLOW`` blocks.
- `scan_interfaces(root, spec)` — Detect service interfaces from project structure.
- `detect_doql_file(root)` — Auto-detect the DOQL spec file in a project directory.
- `parse_file(path)` — Parse a .doql / .doql.css / .doql.less / .doql.sass file into a DoqlSpec.
- `parse_text(text)` — Parse .doql source text into a DoqlSpec (in-memory, no disk I/O).
- `parse_env(path)` — Parse a .env file into a dict. Missing file → empty dict.
- `scan_entities(root, spec)` — Detect entities from Python models / schemas or SQL files.
- `scan_environments(root, spec)` — Detect environments from .env files and docker-compose variants.
- `build_context(args)` — Create BuildContext from CLI arguments.
- `load_spec(ctx)` — Parse spec and env, return (spec, env_vars).
- `scaffold_from_template(template, target)` — Copy scaffold template to target directory.
- `estimate_file_count(iface)` — Rough estimate of file count per interface type.
- `parse_css_file(path)` — Parse a .doql.css / .doql.less / .doql.sass file into DoqlSpec.
- `parse_css_text(text, format)` — Parse CSS-like DOQL source text into a DoqlSpec.
- `generate()` — Generate traceability.py module content.
- `validate(spec, env_vars, project_root)` — Validate a parsed DoqlSpec against env vars and internal consistency.
- `extract_val(body, key)` — Extract 'key: value' from an indented block body.
- `extract_list(body, key)` — Extract 'key: [a, b, c]' or 'key: value' from body.
- `extract_yaml_list(body, key)` — Extract YAML-style list items under a key: header.
- `extract_pages(body)` — Extract PAGE definitions from INTERFACE body.
- `extract_entity_fields(body)` — Extract field definitions from ENTITY body.
- `collect_env_refs(text)` — Find all env.VAR_NAME references in the text.
- `register(keyword)` — Decorator to register a block handler for a keyword.
- `get_handler(keyword)` — Get the handler for a keyword, or None if not registered.
- `list_registered()` — Return list of registered keywords.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `cmd_workspace(args)` — Dispatch to the right workspace subcommand.
- `register_parser(sub)` — Register `workspace` subcommands on the main doql parser.
- `discover_plugins(project_root)` — Discover all plugins — entry-point + local.
- `run_plugins(spec, env_vars, build_dir, project_root)` — Run all discovered plugins. Returns count of plugins executed.


## Project Structure

📦 `doql`
📦 `doql.adopt`
📄 `doql.adopt.emitter` (2 functions)
📦 `doql.adopt.scanner` (1 functions)
📄 `doql.adopt.scanner.databases` (4 functions)
📄 `doql.adopt.scanner.deploy` (8 functions)
📄 `doql.adopt.scanner.entities` (9 functions)
📄 `doql.adopt.scanner.environments` (6 functions)
📄 `doql.adopt.scanner.integrations` (1 functions)
📄 `doql.adopt.scanner.interfaces` (15 functions)
📄 `doql.adopt.scanner.metadata` (4 functions)
📄 `doql.adopt.scanner.roles` (2 functions)
📄 `doql.adopt.scanner.utils` (8 functions)
📄 `doql.adopt.scanner.workflows` (15 functions)
📦 `doql.cli`
📄 `doql.cli.__main__`
📦 `doql.cli.commands`
📄 `doql.cli.commands.adopt` (5 functions)
📄 `doql.cli.commands.deploy` (4 functions)
📄 `doql.cli.commands.docs` (1 functions)
📄 `doql.cli.commands.doctor` (19 functions, 2 classes)
📄 `doql.cli.commands.export` (1 functions)
📄 `doql.cli.commands.generate` (1 functions)
📄 `doql.cli.commands.import_cmd` (1 functions)
📄 `doql.cli.commands.init` (1 functions)
📄 `doql.cli.commands.kiosk` (1 functions)
📄 `doql.cli.commands.plan` (10 functions)
📄 `doql.cli.commands.publish` (5 functions)
📄 `doql.cli.commands.quadlet` (3 functions)
📄 `doql.cli.commands.query` (1 functions)
📄 `doql.cli.commands.render` (1 functions)
📄 `doql.cli.commands.run` (7 functions)
📄 `doql.cli.commands.validate` (2 functions)
📄 `doql.cli.commands.workspace` (25 functions, 1 classes)
📄 `doql.cli.context` (4 functions, 1 classes)
📄 `doql.cli.lockfile` (5 functions)
📄 `doql.cli.main` (2 functions)
📄 `doql.cli.sync` (4 functions)
📦 `doql.exporters`
📦 `doql.exporters.css` (9 functions)
📄 `doql.exporters.css.format_convert` (3 functions)
📄 `doql.exporters.css.helpers` (3 functions)
📄 `doql.exporters.css.renderers` (17 functions)
📄 `doql.exporters.css_exporter`
📦 `doql.exporters.markdown` (2 functions)
📄 `doql.exporters.markdown.sections` (8 functions)
📄 `doql.exporters.markdown.writers` (11 functions)
📄 `doql.exporters.markdown_exporter`
📄 `doql.exporters.yaml_exporter` (3 functions)
📦 `doql.generators`
📦 `doql.generators.api_gen` (5 functions)
📄 `doql.generators.api_gen.alembic` (4 functions)
📄 `doql.generators.api_gen.auth` (1 functions)
📄 `doql.generators.api_gen.common` (5 functions)
📄 `doql.generators.api_gen.database` (1 functions)
📄 `doql.generators.api_gen.main` (2 functions)
📄 `doql.generators.api_gen.models` (2 functions)
📄 `doql.generators.api_gen.routes` (7 functions)
📄 `doql.generators.api_gen.schemas` (5 functions)
📄 `doql.generators.ci_gen` (2 functions)
📄 `doql.generators.deploy` (1 functions)
📄 `doql.generators.desktop_gen` (7 functions)
📄 `doql.generators.docs_gen` (1 functions)
📄 `doql.generators.document_gen` (4 functions)
📄 `doql.generators.export_postman` (1 functions)
📄 `doql.generators.export_ts_sdk` (1 functions)
📄 `doql.generators.i18n_gen` (3 functions)
📄 `doql.generators.infra_gen` (7 functions)
📄 `doql.generators.integrations_gen` (11 functions)
📄 `doql.generators.mobile_gen` (8 functions)
📄 `doql.generators.report_gen` (2 functions)
📄 `doql.generators.utils.codegen` (2 functions)
📦 `doql.generators.web_gen` (8 functions)
📄 `doql.generators.web_gen.common`
📄 `doql.generators.web_gen.components` (1 functions)
📄 `doql.generators.web_gen.config` (6 functions)
📄 `doql.generators.web_gen.core` (3 functions)
📄 `doql.generators.web_gen.pages` (4 functions)
📄 `doql.generators.web_gen.pwa` (3 functions)
📄 `doql.generators.web_gen.router` (1 functions)
📄 `doql.generators.workflow_gen` (8 functions)
📦 `doql.importers`
📄 `doql.importers.yaml_importer` (22 functions)
📄 `doql.lsp_server` (15 functions)
📄 `doql.parser`
📦 `doql.parsers` (5 functions)
📄 `doql.parsers.blocks` (2 functions)
📄 `doql.parsers.css_mappers` (22 functions)
📄 `doql.parsers.css_parser` (6 functions)
📄 `doql.parsers.css_tokenizer` (5 functions)
📄 `doql.parsers.css_transformers` (14 functions)
📄 `doql.parsers.css_utils` (4 functions, 2 classes)
📄 `doql.parsers.extractors` (14 functions)
📄 `doql.parsers.models` (20 classes)
📄 `doql.parsers.registry` (24 functions)
📄 `doql.parsers.validators` (10 functions)
📄 `doql.plugins` (4 functions, 1 classes)
📦 `doql.utils`
📄 `doql.utils.clean` (1 functions)
📄 `doql.utils.naming` (2 functions)
📄 `playground.app` (9 functions)
📄 `playground.pyodide-bridge` (15 functions)
📄 `playground.renderers` (10 functions)
📄 `playground.serve`
📦 `plugins.doql-plugin-erp.doql_plugin_erp` (6 functions)
📦 `plugins.doql-plugin-fleet.doql_plugin_fleet` (2 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.device_registry` (1 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.metrics` (1 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.migration` (1 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.ota` (1 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.tenant` (1 functions)
📦 `plugins.doql-plugin-gxp.doql_plugin_gxp` (6 functions)
📦 `plugins.doql-plugin-iso17025.doql_plugin_iso17025` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.certificate` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.drift_monitor` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.migration` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.traceability` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.uncertainty` (1 functions)
📦 `plugins.doql-plugin-shared.doql_plugin_shared`
📄 `plugins.doql-plugin-shared.doql_plugin_shared.base` (1 functions)
📄 `plugins.doql-plugin-shared.doql_plugin_shared.readme` (1 functions)
📄 `project`
📄 `tree`
📄 `vscode-doql.src.extension` (4 functions)

## Requirements

- Python >= >=3.10
- click >=8.1- pydantic >=2.0- pyyaml >=6.0- jinja2 >=3.1- rich >=13.0- httpx >=0.25- goal >=2.1.0- costs >=0.1.20- pfix >=0.1.60- tomli >=2.0; python_version < '3.11'- testql >=0.1.1

## Contributing

**Contributors:**
- Tom Sapletta

We welcome contributions! Open an issue or pull request to get started.
### Development Setup

```bash
# Clone the repository
git clone https://github.com/oqlos/doql
cd doql

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `examples` | Usage examples and code samples | [View](./examples) |

<!-- code2docs:end -->