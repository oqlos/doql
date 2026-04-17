<!-- code2docs:start --># doql

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-391-green)
> **391** functions | **23** classes | **109** files | CC̄ = 3.2

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

## Generated Output

When you run `doql`, the following files are produced:

```
<project>/
├── README.md                 # Main project README (auto-generated sections)
├── docs/
│   ├── api.md               # Consolidated API reference
│   ├── modules.md           # Module documentation with metrics
│   ├── architecture.md      # Architecture overview with diagrams
│   ├── dependency-graph.md  # Module dependency graphs
│   ├── coverage.md          # Docstring coverage report
│   ├── getting-started.md   # Getting started guide
│   ├── configuration.md    # Configuration reference
│   └── api-changelog.md    # API change tracking
├── examples/
│   ├── quickstart.py       # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── CONTRIBUTING.md         # Contribution guidelines
└── mkdocs.yml             # MkDocs site configuration
```

## Configuration

Create `doql.yaml` in your project root (or run `doql init`):

```yaml
project:
  name: my-project
  source: ./
  output: ./docs/

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  badges:
    - version
    - python
    - coverage
  sync_markers: true

docs:
  api_reference: true
  module_docs: true
  architecture: true
  changelog: true

examples:
  auto_generate: true
  from_entry_points: true

sync:
  strategy: markers    # markers | full | git-diff
  watch: false
  ignore:
    - "tests/"
    - "__pycache__"
```

## Sync Markers

doql can update only specific sections of an existing README using HTML comment markers:

```markdown
<!-- doql:start -->
# Project Title
... auto-generated content ...
<!-- doql:end -->
```

Content outside the markers is preserved when regenerating. Enable this with `sync_markers: true` in your configuration.

## Architecture

```
doql/
├── tree├── doql/├── project        ├── base            ├── metrics    ├── _shared/            ├── device_registry        ├── readme            ├── ota            ├── migration            ├── tenant            ├── traceability        ├── doql_plugin_gxp/        ├── doql_plugin_erp/            ├── certificate        ├── doql_plugin_iso17025/            ├── migration    ├── serve            ├── uncertainty            ├── drift_monitor        ├── doql_plugin_fleet/    ├── renderers    ├── app    ├── pyodide-bridge    ├── cli/        ├── extension    ├── parser    ├── importers/        ├── lockfile        ├── yaml_importer    ├── lsp_server        ├── sync            ├── render        ├── main            ├── validate            ├── plan            ├── export            ├── init            ├── kiosk            ├── query        ├── commands/            ├── quadlet            ├── generate            ├── deploy            ├── import_cmd            ├── run        ├── css_exporter            ├── docs    ├── exporters/        ├── markdown_exporter        ├── yaml_exporter            ├── format_convert            ├── helpers        ├── css/            ├── writers        ├── markdown/            ├── renderers        ├── docs_gen            ├── sections        ├── infra_gen        ├── ci_gen        ├── export_postman        ├── integrations_gen    ├── generators/        ├── desktop_gen        ├── export_ts_sdk        ├── document_gen        ├── deploy        ├── workflow_gen        ├── i18n_gen        ├── api_gen/        ├── web_gen/        ├── report_gen        ├── mobile_gen            ├── config            ├── pwa            ├── common            ├── components        ├── context            ├── router            ├── core            ├── pages            ├── common            ├── alembic            ├── routes            ├── auth            ├── schemas            ├── database            ├── main        ├── clean    ├── utils/            ├── models        ├── naming        ├── css_tokenizer        ├── blocks        ├── css_parser        ├── extractors        ├── css_transformers    ├── parsers/        ├── registry        ├── validators        ├── css_mappers        ├── css_utils    ├── plugins        ├── models```

## API Overview

### Classes

- **`BuildContext`** — Build context for doql commands.
- **`CssBlock`** — Single CSS-like rule: selector + key-value declarations.
- **`ParsedSelector`** — Decomposed CSS selector.
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
- **`DoqlSpec`** — —

### Functions

- `usage()` — —
- `plugin_generate(out, modules, readme_content)` — Common plugin generate() — iterates over modules dict and writes files.
- `generate_readme(plugin_name, modules, description, usage_extra)` — Generate standard README.md content for a doql plugin.
- `generate()` — Generate traceability.py module content.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate()` — Generate certificate.py module content.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate()` — Generate migration.py module content.
- `generate()` — Generate uncertainty.py module content.
- `generate()` — Generate drift_monitor.py module content.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
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
- `pyodide()` — —
- `buildFn()` — —
- `debounceTimer()` — —
- `initElements()` — —
- `isReady()` — —
- `debouncedBuild()` — —
- `executeBuild()` — —
- `r()` — —
- `bootPyodide()` — —
- `version()` — —
- `activate()` — —
- `config()` — —
- `serverPath()` — —
- `deactivate()` — —
- `spec_section_hashes(spec, ctx)` — Compute per-section hashes for diff detection.
- `read_lockfile(ctx)` — Read and parse lockfile if it exists.
- `diff_sections(old_hashes, new_hashes)` — Return dict of changed/added/removed section keys.
- `write_lockfile(spec, ctx)` — Write current spec hashes to lockfile.
- `import_yaml(data)` — Build a DoqlSpec from a YAML-style dictionary.
- `import_yaml_text(text)` — Parse YAML text and return a DoqlSpec.
- `import_yaml_file(path)` — Read a YAML file and return a DoqlSpec.
- `did_open(ls, params)` — —
- `did_change(ls, params)` — —
- `did_save(ls, params)` — —
- `completion(ls, params)` — —
- `hover(ls, params)` — —
- `definition(ls, params)` — —
- `document_symbols(ls, params)` — —
- `main()` — —
- `determine_regeneration_set(diff_result, spec)` — Determine which generators need to re-run based on diff.
- `regenerate_api(spec, env_vars, build_dir)` — Regenerate API section if needed.
- `regenerate_web(spec, env_vars, build_dir)` — Regenerate Web section if needed.
- `regenerate_infra(spec, env_vars, build_dir)` — Regenerate Infrastructure section.
- `regenerate_documents(spec, env_vars, build_dir, project_root)` — Regenerate Documents section if needed.
- `regenerate_reports(spec, env_vars, build_dir)` — Regenerate Reports section if needed.
- `regenerate_i18n(spec, env_vars, build_dir)` — Regenerate i18n section if needed.
- `regenerate_integrations(spec, env_vars, build_dir)` — Regenerate Integrations section if needed.
- `run_generators(regen, spec, env_vars, ctx)` — Run selected generators based on regen set.
- `cmd_sync(args)` — Selective rebuild — only regenerate sections that changed since last build.
- `cmd_render(args)` — Render a template with DATA sources.
- `create_parser()` — Create and configure the argument parser with all subcommands.
- `main()` — Main entry point for doql CLI.
- `cmd_validate(args)` — Validate .doql file and .env configuration.
- `cmd_plan(args)` — Show dry-run plan of what would be generated.
- `cmd_export(args)` — Export project specification to various formats.
- `cmd_init(args)` — Create new project from template.
- `cmd_kiosk(args)` — Manage kiosk appliance installation.
- `cmd_query(args)` — Query a DATA source and output as JSON.
- `cmd_quadlet(args)` — Manage Podman Quadlet containers.
- `cmd_generate(args)` — Generate a single document/artifact.
- `cmd_deploy(args)` — Deploy project to target environment.
- `cmd_import(args)` — Import a YAML spec file and convert to DOQL format.
- `cmd_run(args)` — Run project locally in dev mode using docker-compose.
- `cmd_docs(args)` — Generate documentation site from .doql spec.
- `spec_to_dict(spec)` — Convert DoqlSpec to a cleaned dictionary suitable for YAML/JSON.
- `export_yaml(spec, out)` — Write DoqlSpec as YAML to the given stream.
- `export_yaml_file(spec, path)` — Write DoqlSpec as YAML to a file.
- `export_css(spec, out)` — Write DoqlSpec as .doql.css format.
- `export_less(spec, out)` — Write DoqlSpec as .doql.less format.
- `export_sass(spec, out)` — Write DoqlSpec as .doql.sass format.
- `export_css_file(spec, path, fmt)` — Write DoqlSpec to a CSS-like file. fmt is 'css', 'less', or 'sass'.
- `export_markdown(spec, out)` — Write DoqlSpec as Markdown documentation to the given stream.
- `export_markdown_file(spec, path)` — Write DoqlSpec as Markdown to a file.
- `generate(spec, out)` — Generate documentation files into *out* directory.
- `generate(spec, env_vars, out)` — Generate infra layer files into *out* directory.
- `generate(spec, env_vars, out)` — Generate CI configuration files.
- `run(spec, out)` — Write Postman collection JSON to the given stream.
- `generate(spec, env_vars, out)` — Generate integration service modules.
- `generate(spec, env_vars, out)` — Generate desktop (Tauri) layer files into *out* directory.
- `run(spec, out)` — Write TypeScript SDK to the given stream.
- `generate(spec, env_vars, out, project_root)` — Generate document rendering pipeline into *out* directory.
- `run(ctx, target_env)` — Deploy the built application.
- `generate(spec, env_vars, out)` — Generate workflow engine modules.
- `generate(spec, env_vars, out)` — Generate i18n translation files.
- `generate(spec, env_vars, out)` — Generate report scripts into *out* directory.
- `generate(spec, env_vars, out)` — Generate mobile PWA into *out* directory.
- `build_context(args)` — Create BuildContext from CLI arguments.
- `load_spec(ctx)` — Parse spec and env, return (spec, env_vars).
- `scaffold_from_template(template, target)` — Copy scaffold template to target directory.
- `estimate_file_count(iface)` — Rough estimate of file count per interface type.
- `generate(spec, env_vars, out)` — Generate React + Vite + TailwindCSS frontend into *out* directory.
- `sa_type(f)` — Get SQLAlchemy type for a field.
- `py_type(f)` — Get Python/Pydantic type for a field.
- `py_default(f)` — Get default value assignment for a field.
- `safe_name(name)` — Escape Python reserved keywords by appending underscore.
- `snake(name)` — Convert CamelCase to snake_case.
- `gen_alembic_ini()` — Generate alembic.ini configuration file.
- `gen_alembic_env()` — Generate alembic/env.py migration environment.
- `gen_initial_migration(spec)` — Generate initial Alembic migration with all tables.
- `gen_routes(spec)` — Generate CRUD routes for all entities in the spec.
- `gen_auth(spec)` — Generate JWT authentication module.
- `gen_schemas(spec)` — Generate Pydantic schemas from DoqlSpec using delegation pattern.
- `gen_database(spec, env_vars)` — Generate database.py with SQLAlchemy engine and session.
- `gen_main(spec)` — Generate FastAPI main application file.
- `gen_requirements(has_auth)` — Generate requirements.txt with pinned dependencies.
- `gen_models(spec)` — Generate SQLAlchemy ORM models from DoqlSpec.
- `snake(name)` — Convert CamelCase to snake_case (also handles spaces).
- `kebab(name)` — Convert CamelCase or snake_case to kebab-case.
- `generate(spec, env_vars, out)` — Generate API layer files into *out* directory.
- `export_openapi(spec, out)` — Write OpenAPI 3.1 JSON to the given stream.
- `split_blocks(text)` — Split .doql text into (keyword, rest_of_header, body, start_line) blocks.
- `apply_block(spec, keyword, header, body)` — Apply a single parsed block to *spec* using the registry dispatch.
- `parse_css_file(path)` — Parse a .doql.css / .doql.less / .doql.sass file into DoqlSpec.
- `parse_css_text(text, format)` — Parse CSS-like DOQL source text into a DoqlSpec.
- `extract_val(body, key)` — Extract 'key: value' from an indented block body.
- `extract_list(body, key)` — Extract 'key: [a, b, c]' or 'key: value' from body.
- `extract_yaml_list(body, key)` — Extract YAML-style list items under a key: header.
- `extract_pages(body)` — Extract PAGE definitions from INTERFACE body.
- `extract_entity_fields(body)` — Extract field definitions from ENTITY body.
- `collect_env_refs(text)` — Find all env.VAR_NAME references in the text.
- `detect_doql_file(root)` — Auto-detect the DOQL spec file in a project directory.
- `parse_file(path)` — Parse a .doql / .doql.css / .doql.less / .doql.sass file into a DoqlSpec.
- `parse_text(text)` — Parse .doql source text into a DoqlSpec (in-memory, no disk I/O).
- `parse_env(path)` — Parse a .env file into a dict. Missing file → empty dict.
- `register(keyword)` — Decorator to register a block handler for a keyword.
- `get_handler(keyword)` — Get the handler for a keyword, or None if not registered.
- `list_registered()` — Return list of registered keywords.
- `validate(spec, env_vars, project_root)` — Validate a parsed DoqlSpec against env vars and internal consistency.
- `discover_plugins(project_root)` — Discover all plugins — entry-point + local.
- `run_plugins(spec, env_vars, build_dir, project_root)` — Run all discovered plugins. Returns count of plugins executed.


## Project Structure

📦 `doql`
📦 `doql.cli`
📦 `doql.cli.commands`
📄 `doql.cli.commands.deploy` (1 functions)
📄 `doql.cli.commands.docs` (1 functions)
📄 `doql.cli.commands.export` (1 functions)
📄 `doql.cli.commands.generate` (1 functions)
📄 `doql.cli.commands.import_cmd` (1 functions)
📄 `doql.cli.commands.init` (1 functions)
📄 `doql.cli.commands.kiosk` (1 functions)
📄 `doql.cli.commands.plan` (10 functions)
📄 `doql.cli.commands.quadlet` (1 functions)
📄 `doql.cli.commands.query` (1 functions)
📄 `doql.cli.commands.render` (1 functions)
📄 `doql.cli.commands.run` (1 functions)
📄 `doql.cli.commands.validate` (1 functions)
📄 `doql.cli.context` (4 functions, 1 classes)
📄 `doql.cli.lockfile` (4 functions)
📄 `doql.cli.main` (2 functions)
📄 `doql.cli.sync` (10 functions)
📦 `doql.exporters`
📦 `doql.exporters.css` (9 functions)
📄 `doql.exporters.css.format_convert` (2 functions)
📄 `doql.exporters.css.helpers` (3 functions)
📄 `doql.exporters.css.renderers` (14 functions)
📄 `doql.exporters.css_exporter`
📦 `doql.exporters.markdown` (2 functions)
📄 `doql.exporters.markdown.sections` (7 functions)
📄 `doql.exporters.markdown.writers` (10 functions)
📄 `doql.exporters.markdown_exporter`
📄 `doql.exporters.yaml_exporter` (3 functions)
📦 `doql.generators`
📦 `doql.generators.api_gen` (5 functions)
📄 `doql.generators.api_gen.alembic` (3 functions)
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
📄 `doql.generators.infra_gen` (5 functions)
📄 `doql.generators.integrations_gen` (11 functions)
📄 `doql.generators.mobile_gen` (8 functions)
📄 `doql.generators.report_gen` (2 functions)
📦 `doql.generators.web_gen` (8 functions)
📄 `doql.generators.web_gen.common`
📄 `doql.generators.web_gen.components` (1 functions)
📄 `doql.generators.web_gen.config` (6 functions)
📄 `doql.generators.web_gen.core` (3 functions)
📄 `doql.generators.web_gen.pages` (3 functions)
📄 `doql.generators.web_gen.pwa` (3 functions)
📄 `doql.generators.web_gen.router` (1 functions)
📄 `doql.generators.workflow_gen` (6 functions)
📦 `doql.importers`
📄 `doql.importers.yaml_importer` (22 functions)
📄 `doql.lsp_server` (13 functions)
📄 `doql.parser`
📦 `doql.parsers` (5 functions)
📄 `doql.parsers.blocks` (2 functions)
📄 `doql.parsers.css_mappers` (12 functions)
📄 `doql.parsers.css_parser` (6 functions)
📄 `doql.parsers.css_tokenizer` (2 functions)
📄 `doql.parsers.css_transformers` (7 functions)
📄 `doql.parsers.css_utils` (4 functions, 2 classes)
📄 `doql.parsers.extractors` (14 functions)
📄 `doql.parsers.models` (19 classes)
📄 `doql.parsers.registry` (24 functions)
📄 `doql.parsers.validators` (9 functions)
📄 `doql.plugins` (4 functions, 1 classes)
📦 `doql.utils`
📄 `doql.utils.clean` (1 functions)
📄 `doql.utils.naming` (2 functions)
📄 `playground.app` (9 functions)
📄 `playground.pyodide-bridge` (13 functions)
📄 `playground.renderers` (10 functions)
📄 `playground.serve`
📦 `plugins._shared`
📄 `plugins._shared.base` (1 functions)
📄 `plugins._shared.readme` (1 functions)
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
📄 `project`
📄 `tree`
📄 `vscode-doql.src.extension` (4 functions)

## Requirements

- Python >= >=3.10
- click >=8.1- pydantic >=2.0- pyyaml >=6.0- jinja2 >=3.1- rich >=13.0- httpx >=0.25- goal >=2.1.0- costs >=0.1.20- pfix >=0.1.60

## Contributing

**Contributors:**
- Tom Sapletta

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

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

- 📖 [Full Documentation](https://github.com/oqlos/doql/tree/main/docs) — API reference, module docs, architecture
- 🚀 [Getting Started](https://github.com/oqlos/doql/blob/main/docs/getting-started.md) — Quick start guide
- 📚 [API Reference](https://github.com/oqlos/doql/blob/main/docs/api.md) — Complete API documentation
- 🔧 [Configuration](https://github.com/oqlos/doql/blob/main/docs/configuration.md) — Configuration options
- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `docs/api.md` | Consolidated API reference | [View](./docs/api.md) |
| `docs/modules.md` | Module reference with metrics | [View](./docs/modules.md) |
| `docs/architecture.md` | Architecture with diagrams | [View](./docs/architecture.md) |
| `docs/dependency-graph.md` | Dependency graphs | [View](./docs/dependency-graph.md) |
| `docs/coverage.md` | Docstring coverage report | [View](./docs/coverage.md) |
| `docs/getting-started.md` | Getting started guide | [View](./docs/getting-started.md) |
| `docs/configuration.md` | Configuration reference | [View](./docs/configuration.md) |
| `docs/api-changelog.md` | API change tracking | [View](./docs/api-changelog.md) |
| `CONTRIBUTING.md` | Contribution guidelines | [View](./CONTRIBUTING.md) |
| `examples/` | Usage examples | [Browse](./examples) |
| `mkdocs.yml` | MkDocs configuration | — |

<!-- code2docs:end -->