<!-- code2docs:start --># doql

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-196-green)
> **196** functions | **21** classes | **30** files | CC̄ = 4.1

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
├── tree├── project        ├── doql_plugin_erp/    ├── serve        ├── doql_plugin_fleet/        ├── doql_plugin_gxp/        ├── extension        ├── doql_plugin_iso17025/├── doql/    ├── app    ├── lsp_server        ├── docs_gen        ├── infra_gen        ├── integrations_gen        ├── ci_gen        ├── export_postman        ├── desktop_gen    ├── generators/        ├── document_gen        ├── export_ts_sdk        ├── workflow_gen        ├── deploy        ├── i18n_gen        ├── mobile_gen        ├── api_gen        ├── web_gen        ├── report_gen    ├── cli    ├── plugins    ├── parser```

## API Overview

### Classes

- **`BuildContext`** — —
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

- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `activate()` — —
- `config()` — —
- `serverPath()` — —
- `deactivate()` — —
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
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
- `bootPyodide()` — —
- `version()` — —
- `scheduleBuild()` — —
- `runBuild()` — —
- `r()` — —
- `renderFatal()` — —
- `renderDiagnostics()` — —
- `loc()` — —
- `renderAst()` — —
- `renderEnv()` — —
- `refs()` — —
- `keys()` — —
- `marker()` — —
- `renderFiles()` — —
- `escapeHtml()` — —
- `did_open(ls, params)` — —
- `did_change(ls, params)` — —
- `did_save(ls, params)` — —
- `completion(ls, params)` — —
- `hover(ls, params)` — —
- `definition(ls, params)` — —
- `document_symbols(ls, params)` — —
- `main()` — —
- `generate(spec, out)` — Generate documentation files into *out* directory.
- `generate(spec, env_vars, out)` — Generate infra layer files into *out* directory.
- `generate(spec, env_vars, out)` — Generate integration service modules.
- `generate(spec, env_vars, out)` — Generate CI configuration files.
- `run(spec, out)` — Write Postman collection JSON to the given stream.
- `generate(spec, env_vars, out)` — Generate desktop (Tauri) layer files into *out* directory.
- `generate(spec, env_vars, out, project_root)` — Generate document rendering pipeline into *out* directory.
- `run(spec, out)` — Write TypeScript SDK to the given stream.
- `generate(spec, env_vars, out)` — Generate workflow engine modules.
- `run(ctx, target_env)` — Deploy the built application.
- `generate(spec, env_vars, out)` — Generate i18n translation files.
- `generate(spec, env_vars, out)` — Generate mobile PWA into *out* directory.
- `generate(spec, env_vars, out)` — Generate API layer files into *out* directory.
- `export_openapi(spec, out)` — Write OpenAPI 3.1 JSON to the given stream.
- `generate(spec, env_vars, out)` — Generate React + Vite + TailwindCSS frontend into *out* directory.
- `generate(spec, env_vars, out)` — Generate report scripts into *out* directory.
- `cmd_init(args)` — —
- `cmd_validate(args)` — —
- `cmd_plan(args)` — —
- `cmd_build(args)` — —
- `cmd_run(args)` — —
- `cmd_deploy(args)` — —
- `cmd_sync(args)` — Selective rebuild — only regenerate sections that changed since last build.
- `cmd_export(args)` — —
- `cmd_generate(args)` — —
- `cmd_render(args)` — —
- `cmd_query(args)` — —
- `cmd_kiosk(args)` — —
- `cmd_quadlet(args)` — —
- `cmd_docs(args)` — —
- `main()` — —
- `discover_plugins(project_root)` — Discover all plugins — entry-point + local.
- `run_plugins(spec, env_vars, build_dir, project_root)` — Run all discovered plugins. Returns count of plugins executed.
- `parse_file(path)` — Parse a .doql file into a DoqlSpec.
- `parse_text(text)` — Parse .doql source text into a DoqlSpec (in-memory, no disk I/O).
- `parse_env(path)` — Parse a .env file into a dict. Missing file → empty dict.
- `validate(spec, env_vars, project_root)` — Validate a parsed DoqlSpec against env vars and internal consistency.


## Project Structure

📦 `doql`
📄 `doql.cli` (23 functions, 1 classes)
📦 `doql.generators`
📄 `doql.generators.api_gen` (17 functions)
📄 `doql.generators.ci_gen` (2 functions)
📄 `doql.generators.deploy` (1 functions)
📄 `doql.generators.desktop_gen` (8 functions)
📄 `doql.generators.docs_gen` (1 functions)
📄 `doql.generators.document_gen` (4 functions)
📄 `doql.generators.export_postman` (1 functions)
📄 `doql.generators.export_ts_sdk` (1 functions)
📄 `doql.generators.i18n_gen` (4 functions)
📄 `doql.generators.infra_gen` (5 functions)
📄 `doql.generators.integrations_gen` (7 functions)
📄 `doql.generators.mobile_gen` (8 functions)
📄 `doql.generators.report_gen` (2 functions)
📄 `doql.generators.web_gen` (20 functions)
📄 `doql.generators.workflow_gen` (7 functions)
📄 `doql.lsp_server` (12 functions)
📄 `doql.parser` (12 functions, 19 classes)
📄 `doql.plugins` (4 functions, 1 classes)
📄 `playground.app` (27 functions)
📄 `playground.serve`
📦 `plugins.doql-plugin-erp.doql_plugin_erp` (6 functions)
📦 `plugins.doql-plugin-fleet.doql_plugin_fleet` (7 functions)
📦 `plugins.doql-plugin-gxp.doql_plugin_gxp` (6 functions)
📦 `plugins.doql-plugin-iso17025.doql_plugin_iso17025` (7 functions)
📄 `project`
📄 `tree`
📄 `vscode-doql.src.extension` (4 functions)

## Requirements

- Python >= >=3.10
- click >=8.1- pydantic >=2.0- pyyaml >=6.0- jinja2 >=3.1- rich >=13.0- httpx >=0.25

## Contributing

**Contributors:**
- Tom Softreck <tom@sapletta.com>
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>

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