# Rodzina OQL — paczka kompletna

Declarative OQL — build complete applications from a single .doql file

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `doql`
- **version**: `1.0.35`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, src(3 mod), project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: doql;
  version: 1.0.35;
}

dependencies {
  runtime: "click>=8.1, pydantic>=2.0, pyyaml>=6.0, jinja2>=3.1, rich>=13.0, httpx>=0.25, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60, tomli>=2.0; python_version < '3.11', testql>=0.1.1";
  dev: "pytest>=7.4, pytest-asyncio, pytest-cov>=4.0, ruff, mypy, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="doql"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=pip install -e plugins/doql-plugin-shared -e plugins/doql-plugin-gxp -e plugins/doql-plugin-iso17025 -e plugins/doql-plugin-fleet -e plugins/doql-plugin-erp -e .[dev];
}

workflow[name="deps:update"] {
  trigger: manual;
  step-1: run cmd=PIP="pip"
[ -f "{{.PWD}}/.venv/bin/pip" ] && PIP="{{.PWD}}/.venv/bin/pip"
$PIP install --upgrade pip
OUTDATED=$($PIP list --outdated --format=columns 2>/dev/null | tail -n +3 | awk '{print $1}')
if [ -z "$OUTDATED" ]; then
  echo "✅ All packages are up to date."
else
  echo "📦 Upgrading: $OUTDATED"
  echo "$OUTDATED" | xargs $PIP install --upgrade
  echo "✅ Done."
fi
echo "🔌 Reinstalling local plugins..."
$PIP install -e plugins/doql-plugin-shared -e plugins/doql-plugin-gxp -e plugins/doql-plugin-iso17025 -e plugins/doql-plugin-fleet -e plugins/doql-plugin-erp -e .[dev] -q;
}

workflow[name="quality"] {
  trigger: manual;
  step-1: run cmd=pyqual run;
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=pytest -q;
}

workflow[name="quality:fix"] {
  trigger: manual;
  step-1: run cmd=pyqual run --fix;
}

workflow[name="quality:report"] {
  trigger: manual;
  step-1: run cmd=pyqual report;
}

workflow[name="build"] {
  trigger: manual;
  step-1: run cmd=python -m build;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
}

workflow[name="structure"] {
  trigger: manual;
  step-1: run cmd=echo "📁 Analyzing project structure..."
python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force
echo "🎨 Exporting to LESS format..."
doql export --format less -o {{.DOQL_OUTPUT}}
echo "✅ Structure generated: app.doql.css + {{.DOQL_OUTPUT}}";
}

workflow[name="doql:adopt"] {
  trigger: manual;
  step-1: run cmd=python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force;
  step-2: run cmd=echo "✅ Captured in app.doql.css";
}

workflow[name="doql:export"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "app.doql.css" ]; then
  echo "❌ app.doql.css not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd=doql export --format less -o {{.DOQL_OUTPUT}};
  step-3: run cmd=echo "✅ Exported to {{.DOQL_OUTPUT}}";
}

workflow[name="doql:validate"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
  exit 1
fi;
  step-2: run cmd=python3 -m doql.cli validate;
}

workflow[name="doql:doctor"] {
  trigger: manual;
  step-1: run cmd=python3 -m doql.cli doctor {{.PWD}};
}

workflow[name="doql:build"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
  exit 1
fi;
  step-2: run cmd=# Regenerate LESS from CSS if CSS exists
if [ -f "app.doql.css" ]; then
  doql export --format less -o {{.DOQL_OUTPUT}}
fi;
  step-3: run cmd=python3 -m doql.cli build app.doql.css --out build/;
}

workflow[name="help"] {
  trigger: manual;
  step-1: run cmd=task --list;
}

workflow[name="cross-quality"] {
  trigger: manual;
  step-1: run cmd=echo "🧪 doql quality gate   — cc≤12, critical=0"
pyqual run;
  step-2: run cmd=echo "🧪 redeploy quality gate — cc≤15, critical≤80"
cd "{{.REDEPLOY_ROOT}}" && make quality-check;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.10;
}
```

### Source Modules

- `doql.cli`
- `doql.parser`
- `doql.plugins`

## Interfaces

### CLI Entry Points

- `doql`
- `doql-lsp`

### testql Scenarios

#### `testql-scenarios/generated-api-integration.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-api-integration.testql.toon.yaml
# SCENARIO: API Integration Tests
# TYPE: api
# GENERATED: true

CONFIG[3]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 30000
  retry_count, 3

API[4]{method, endpoint, expected_status}:
  GET, /health, 200
  GET, /api/v1/status, 200
  POST, /api/v1/test, 201
  GET, /api/v1/docs, 200

ASSERT[2]{field, operator, expected}:
  status, ==, ok
  response_time, <, 1000
```

#### `testql-scenarios/generated-api-smoke.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-api-smoke.testql.toon.yaml
# SCENARIO: Auto-generated API Smoke Tests
# TYPE: api
# GENERATED: true
# DETECTORS: FastAPIDetector, ConfigEndpointDetector

CONFIG[4]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 10000
  retry_count, 3
  detected_frameworks, FastAPIDetector, ConfigEndpointDetector

# REST API Endpoints (10 unique)
API[10]{method, endpoint, expected_status}:
  GET, /api/v1/notebooks, 200
  POST, /api/v1/notebooks, 201
  GET, /api/v1/notes, 200
  POST, /api/v1/notes, 201
  GET, /api/v1/tags, 200
  POST, /api/v1/tags, 201
  POST, /auth/register, 201
  POST, /auth/login, 201
  GET, /auth/me, 200
  GET, /health, 200

ASSERT[2]{field, operator, expected}:
  status, <, 500
  response_time, <, 2000

# Summary by Framework:
#   fastapi: 19 endpoints
#   docker: 1 endpoints
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

LOG[8]{message}:
  "Test: test_fastapi_dependency_alone_does_not_create_api_interface"
  "Test: test_fastapi_with_main_py_creates_api"
  "Test: test_api_entry_point_in_scripts_creates_api"
  "Test: test_api_boot_and_health"
  "Test: test_fastapi_dependency_alone_does_not_create_api_interface"
  "Test: test_fastapi_with_main_py_creates_api"
  "Test: test_api_entry_point_in_scripts_creates_api"
  "Test: test_api_boot_and_health"
```

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
# Taskfile.yml — doql project runner
# https://taskfile.dev

version: "3"

vars:
  APP_NAME: doql
  DOQL_OUTPUT: app.doql.less
  REDEPLOY_ROOT: "../../maskservice/redeploy"

env:
  PYTHONPATH: "{{.PWD}}"

tasks:
  # ─────────────────────────────────────────────────────────────────────────────
  # Development
  # ─────────────────────────────────────────────────────────────────────────────

  install:
    desc: Install Python dependencies (editable)
    cmds:
      - pip install -e plugins/doql-plugin-shared -e plugins/doql-plugin-gxp -e plugins/doql-plugin-iso17025 -e plugins/doql-plugin-fleet -e plugins/doql-plugin-erp -e .[dev]

  deps:update:
    desc: Upgrade all outdated Python packages in the active / project venv (including plugins)
    cmds:
      - |
        PIP="pip"
        [ -f "{{.PWD}}/.venv/bin/pip" ] && PIP="{{.PWD}}/.venv/bin/pip"
        $PIP install --upgrade pip
        OUTDATED=$($PIP list --outdated --format=columns 2>/dev/null | tail -n +3 | awk '{print $1}')
        if [ -z "$OUTDATED" ]; then
          echo "✅ All packages are up to date."
        else
          echo "📦 Upgrading: $OUTDATED"
          echo "$OUTDATED" | xargs $PIP install --upgrade
          echo "✅ Done."
        fi
        echo "🔌 Reinstalling local plugins..."
        $PIP install -e plugins/doql-plugin-shared -e plugins/doql-plugin-gxp -e plugins/doql-plugin-iso17025 -e plugins/doql-plugin-fleet -e plugins/doql-plugin-erp -e .[dev] -q

  quality:
    desc: Run pyqual quality pipeline
    cmds:
      - pyqual run

  test:
    desc: Run pytest suite
    cmds:
      - pytest -q

  quality:fix:
    desc: Run pyqual with auto-fix
    cmds:
      - pyqual run --fix

  quality:report:
    desc: Generate pyqual quality report
    cmds:
      - pyqual report

  build:
    desc: Build wheel + sdist
    cmds:
      - python -m build

  clean:
    desc: Remove build artefacts
    cmds:
      - rm -rf build/ dist/ *.egg-info

  all:
    desc: Run install, quality check
    cmds:
      - task: install
      - task: quality

  # ─────────────────────────────────────────────────────────────────────────────
  # Doql Self-Integration (doql analyzing itself)
  # ─────────────────────────────────────────────────────────────────────────────

  structure:
    desc: Generate project structure (app.doql.css + app.doql.less)
    cmds:
      - |
        echo "📁 Analyzing project structure..."
        python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force
        echo "🎨 Exporting to LESS format..."
        doql export --format less -o {{.DOQL_OUTPUT}}
        echo "✅ Structure generated: app.doql.css + {{.DOQL_OUTPUT}}"

  doql:adopt:
    desc: Reverse-engineer doql project structure (CSS only)
    cmds:
      - python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force
      - echo "✅ Captured in app.doql.css"

  doql:export:
    desc: Export to LESS format
    cmds:
      - |
        if [ ! -f "app.doql.css" ]; then
          echo "❌ app.doql.css not found. Run: task structure"
          exit 1
        fi
      - doql export --format less -o {{.DOQL_OUTPUT}}
      - echo "✅ Exported to {{.DOQL_OUTPUT}}"

  doql:validate:
    desc: Validate app.doql.less syntax
    cmds:
      - |
        if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
          echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
          exit 1
        fi
      - python3 -m doql.cli validate

  doql:doctor:
    desc: Run doql health checks
    cmds:
      - python3 -m doql.cli doctor {{.PWD}}

  doql:build:
    desc: Generate code from app.doql.less
    cmds:
      - |
        if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
          echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
          exit 1
        fi
      - |
        # Regenerate LESS from CSS if CSS exists
        if [ -f "app.doql.css" ]; then
          doql export --format less -o {{.DOQL_OUTPUT}}
        fi
      - python3 -m doql.cli build app.doql.css --out build/

  analyze:
    desc: Full doql analysis (adopt + validate + doctor)
    cmds:
      - task: doql:adopt
      - task: doql:validate
      - task: doql:doctor

  # ─────────────────────────────────────────────────────────────────────────────
  # Utility
  # ─────────────────────────────────────────────────────────────────────────────

  help:
    desc: Show available tasks
    cmds:
      - task --list

  # ─────────────────────────────────────────────────────────────────────────────
  # Cross-project quality gate (doql + redeploy)
  # Trend: redeploy catches up to doql, never the other way around.
  # ─────────────────────────────────────────────────────────────────────────────

  cross-quality:
    desc: Run quality gates for doql (strict) and redeploy (catching up)
    cmds:
      - |
        echo "🧪 doql quality gate   — cc≤12, critical=0"
        pyqual run
      - |
        echo "🧪 redeploy quality gate — cc≤15, critical≤80"
        cd "{{.REDEPLOY_ROOT}}" && make quality-check
```

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: doql-quality

  metrics:
    cc_max: 12
    vallm_pass_min: 55   # current: 58% - 3 vallm errors
    # coverage disabled - pytest_cov reports null (no data collected)

  stages:
    - name: analyze
      tool: code2llm-filtered

    - name: validate
      tool: vallm-filtered

    - name: prefact
      tool: prefact
      optional: true
      when: any_stage_fail
      timeout: 900

    - name: fix
      tool: llx-fix
      optional: true
      when: any_stage_fail
      timeout: 1800

    - name: security
      tool: bandit
      optional: true
      timeout: 120

    - name: test
      tool: pytest
      timeout: 600

    - name: push
      tool: git-push
      optional: true
      timeout: 120

  loop:
    max_iterations: 3
    on_fail: report
    ticket_backends:
      - markdown

  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
```

## Configuration

```yaml
project:
  name: doql
  version: 1.0.35
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
click>=8.1
pydantic>=2.0
pyyaml>=6.0
jinja2>=3.1
rich>=13.0
httpx>=0.25
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
tomli>=2.0; python_version < '3.11'
testql>=0.1.1
```

### Development

```text markpact:deps python scope=dev
pytest>=7.4
pytest-asyncio
pytest-cov>=4.0
ruff
mypy
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Deployment

```bash markpact:run
pip install doql

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`doql`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `doql/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# doql | 232f 27456L | python:190,less:17,css:14,shell:6,javascript:4,typescript:1 | 2026-06-05
# stats: 807 func | 42 cls | 232 mod | CC̄=3.8 | critical:34 | cycles:0
# alerts[5]: CC test_api_boot_and_health=17; CC _watch_files=15; CC scan_python_cli=14; CC check_api=14; CC test_css_parse_project_blocks=14
# hotspots[5]: test_api_boot_and_health fan=26; main fan=21; _do_build fan=20; check_api fan=20; cmd_doctor fan=17
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[232]:
  app.doql.less,151
  doql/__init__.py,92
  doql/adopt/__init__.py,11
  doql/adopt/device_scanner.py,133
  doql/adopt/emitter.py,19
  doql/adopt/scanner/__init__.py,59
  doql/adopt/scanner/databases.py,63
  doql/adopt/scanner/deploy.py,151
  doql/adopt/scanner/entities.py,186
  doql/adopt/scanner/environments.py,89
  doql/adopt/scanner/integrations.py,27
  doql/adopt/scanner/interfaces/__init__.py,23
  doql/adopt/scanner/interfaces/api.py,147
  doql/adopt/scanner/interfaces/cli.py,57
  doql/adopt/scanner/interfaces/desktop.py,36
  doql/adopt/scanner/interfaces/mobile.py,38
  doql/adopt/scanner/interfaces/web.py,89
  doql/adopt/scanner/metadata.py,107
  doql/adopt/scanner/roles.py,33
  doql/adopt/scanner/utils.py,101
  doql/adopt/scanner/workflows.py,264
  doql/adopt/scanner.py,46
  doql/cli/__init__.py,20
  doql/cli/__main__.py,10
  doql/cli/build.py,392
  doql/cli/commands/__init__.py,56
  doql/cli/commands/adopt.py,288
  doql/cli/commands/deploy.py,143
  doql/cli/commands/docs.py,22
  doql/cli/commands/doctor/__init__.py,79
  doql/cli/commands/doctor/checks.py,203
  doql/cli/commands/doctor/fixes.py,51
  doql/cli/commands/doctor/remote.py,68
  doql/cli/commands/doctor/report.py,45
  doql/cli/commands/drift/__init__.py,98
  doql/cli/commands/drift/export.py,36
  doql/cli/commands/drift/render.py,108
  doql/cli/commands/export.py,59
  doql/cli/commands/generate.py,35
  doql/cli/commands/import_cmd.py,46
  doql/cli/commands/init.py,44
  doql/cli/commands/kiosk.py,21
  doql/cli/commands/plan.py,116
  doql/cli/commands/publish.py,183
  doql/cli/commands/quadlet.py,113
  doql/cli/commands/query.py,32
  doql/cli/commands/render.py,27
  doql/cli/commands/run.py,167
  doql/cli/commands/validate.py,49
  doql/cli/commands/workspace/__init__.py,105
  doql/cli/commands/workspace/analyze.py,208
  doql/cli/commands/workspace/discovery.py,114
  doql/cli/commands/workspace/list.py,64
  doql/cli/commands/workspace/output.py,37
  doql/cli/commands/workspace/run.py,88
  doql/cli/context.py,67
  doql/cli/lockfile.py,84
  doql/cli/main.py,199
  doql/cli/sync.py,123
  doql/cli.py,63
  doql/drift/__init__.py,23
  doql/drift/detector.py,126
  doql/exporters/__init__.py,2
  doql/exporters/css/__init__.py,114
  doql/exporters/css/format_convert.py,68
  doql/exporters/css/helpers.py,40
  doql/exporters/css/renderers.py,368
  doql/exporters/css_exporter.py,17
  doql/exporters/markdown/__init__.py,41
  doql/exporters/markdown/sections.py,122
  doql/exporters/markdown/writers.py,102
  doql/exporters/markdown_exporter.py,13
  doql/exporters/yaml_exporter.py,37
  doql/generators/__init__.py,6
  doql/generators/api_gen/__init__.py,179
  doql/generators/api_gen/alembic.py,153
  doql/generators/api_gen/auth.py,155
  doql/generators/api_gen/common.py,85
  doql/generators/api_gen/database.py,42
  doql/generators/api_gen/main.py,75
  doql/generators/api_gen/models.py,83
  doql/generators/api_gen/routes.py,116
  doql/generators/api_gen/schemas.py,84
  doql/generators/api_gen.py,26
  doql/generators/ci_gen.py,242
  doql/generators/deploy.py,21
  doql/generators/desktop_gen.py,210
  doql/generators/docs_gen.py,25
  doql/generators/document_gen.py,183
  doql/generators/export_postman.py,26
  doql/generators/export_ts_sdk.py,27
  doql/generators/i18n_gen.py,169
  doql/generators/infra_gen/__init__.py,81
  doql/generators/infra_gen/docker.py,104
  doql/generators/infra_gen/kiosk.py,102
  doql/generators/infra_gen/kubernetes.py,120
  doql/generators/infra_gen/migration.py,74
  doql/generators/infra_gen/nginx.py,55
  doql/generators/infra_gen/quadlet.py,82
  doql/generators/infra_gen/terraform.py,69
  doql/generators/integrations_gen.py,337
  doql/generators/mobile_gen.py,459
  doql/generators/report_gen.py,143
  doql/generators/utils/codegen.py,68
  doql/generators/vite_gen.py,122
  doql/generators/web_gen/__init__.py,201
  doql/generators/web_gen/common.py,10
  doql/generators/web_gen/components.py,77
  doql/generators/web_gen/config.py,123
  doql/generators/web_gen/core.py,58
  doql/generators/web_gen/pages.py,167
  doql/generators/web_gen/pwa.py,110
  doql/generators/web_gen/router.py,44
  doql/generators/web_gen.py,35
  doql/generators/workflow_gen.py,319
  doql/importers/__init__.py,2
  doql/importers/yaml_importer.py,268
  doql/integrations/__init__.py,21
  doql/integrations/op3_bridge.py,75
  doql/lsp_server/__init__.py,74
  doql/lsp_server/completion.py,55
  doql/lsp_server/definition.py,43
  doql/lsp_server/diagnostics.py,93
  doql/lsp_server/hover.py,82
  doql/lsp_server/symbols.py,75
  doql/lsp_server/utils.py,42
  doql/parser.py,75
  doql/parsers/__init__.py,155
  doql/parsers/blocks.py,52
  doql/parsers/css_mappers/__init__.py,99
  doql/parsers/css_mappers/config.py,82
  doql/parsers/css_mappers/entity.py,111
  doql/parsers/css_mappers/infra.py,116
  doql/parsers/css_mappers/integration.py,22
  doql/parsers/css_mappers/interface.py,97
  doql/parsers/css_mappers/workflow.py,87
  doql/parsers/css_parser.py,138
  doql/parsers/css_tokenizer.py,130
  doql/parsers/css_transformers/__init__.py,31
  doql/parsers/css_transformers/indent.py,58
  doql/parsers/css_transformers/mixins.py,45
  doql/parsers/css_transformers/selectors.py,88
  doql/parsers/css_transformers/variables.py,46
  doql/parsers/css_utils.py,75
  doql/parsers/extractors.py,206
  doql/parsers/models.py,270
  doql/parsers/registry.py,332
  doql/parsers/validators.py,201
  doql/plugins.py,102
  doql/utils/__init__.py,7
  doql/utils/clean.py,21
  doql/utils/naming.py,55
  doql.sh,196
  examples/app.doql.less,60
  examples/asset-management/app.doql.css,229
  examples/asset-management/app.doql.less,235
  examples/asset-management.doql.css,531
  examples/blog-cms/app.doql.less,146
  examples/blog-cms.doql.css,138
  examples/calibration-lab/app.doql.less,318
  examples/calibration-lab.doql.css,174
  examples/crm-contacts/app.doql.less,171
  examples/crm-contacts.doql.css,125
  examples/document-generator/app.doql.less,321
  examples/document-generator.doql.css,107
  examples/e-commerce-shop/app.doql.less,130
  examples/e-commerce-shop.doql.css,177
  examples/iot-fleet/app.doql.less,329
  examples/iot-fleet.doql.css,166
  examples/kiosk-station/app.doql.css,75
  examples/kiosk-station/app.doql.less,73
  examples/kiosk-station.doql.css,384
  examples/notes-app.doql.css,71
  examples/todo-pwa/app.doql.css,27
  examples/todo-pwa/app.doql.less,29
  examples/todo-pwa.doql.css,37
  playground/app.js,213
  playground/doql_build.py,141
  playground/pyodide-bridge.js,147
  playground/renderers.js,94
  playground/serve.sh,16
  playground/style.css,238
  plugins/doql-plugin-erp/app.doql.less,60
  plugins/doql-plugin-erp/doql_plugin_erp/__init__.py,358
  plugins/doql-plugin-fleet/app.doql.less,60
  plugins/doql-plugin-fleet/doql_plugin_fleet/__init__.py,85
  plugins/doql-plugin-fleet/doql_plugin_fleet/device_registry.py,131
  plugins/doql-plugin-fleet/doql_plugin_fleet/metrics.py,101
  plugins/doql-plugin-fleet/doql_plugin_fleet/migration.py,82
  plugins/doql-plugin-fleet/doql_plugin_fleet/ota.py,73
  plugins/doql-plugin-fleet/doql_plugin_fleet/tenant.py,84
  plugins/doql-plugin-gxp/app.doql.less,60
  plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py,428
  plugins/doql-plugin-iso17025/app.doql.less,60
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/__init__.py,40
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py,136
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/drift_monitor.py,79
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/migration.py,75
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/traceability.py,94
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/uncertainty.py,127
  plugins/doql-plugin-shared/app.doql.less,60
  plugins/doql-plugin-shared/doql_plugin_shared/__init__.py,12
  plugins/doql-plugin-shared/doql_plugin_shared/base.py,30
  plugins/doql-plugin-shared/doql_plugin_shared/readme.py,38
  project.sh,49
  tests/__init__.py,1
  tests/env_manager.py,500
  tests/integration/__init__.py,2
  tests/integration/test_adopt_from_device.py,356
  tests/integration/test_build_from_device.py,283
  tests/integration/test_drift.py,290
  tests/integration/test_op3_bridge.py,165
  tests/playground_e2e.py,124
  tests/runtime_all_examples.sh,116
  tests/runtime_deploy.sh,66
  tests/runtime_smoke.py,92
  tests/test_adopt.py,489
  tests/test_css_parser.py,326
  tests/test_deploy.py,363
  tests/test_exporters.py,437
  tests/test_exporters_shims.py,93
  tests/test_generators.py,122
  tests/test_lsp.py,60
  tests/test_parser.py,207
  tests/test_parser_benchmark.py,217
  tests/test_plugins.py,119
  tests/test_runtime.py,245
  tests/test_workspace.py,170
  tree.sh,2
  vscode-doql/app.doql.less,75
  vscode-doql/src/extension.ts,52
  vscode-doql/test/vscode-doql.test.js,8
D:
  doql/__init__.py:
  doql/adopt/__init__.py:
  doql/adopt/device_scanner.py:
    e: _header,adopt_from_device_to_snapshot,adopt_from_device
    _header(target;snapshot;layers)
    adopt_from_device_to_snapshot(target)
    adopt_from_device(target)
  doql/adopt/emitter.py:
    e: emit_css,emit_spec
    emit_css(spec;output)
    emit_spec(spec;output;fmt)
  doql/adopt/scanner/__init__.py:
    e: scan_project
    scan_project(root)
  doql/adopt/scanner/databases.py:
    e: _db_name,_db_from_image,_scan_compose_databases,scan_databases
    _db_name(svc_name;db_type)
    _db_from_image(svc_name;image)
    _scan_compose_databases(root;spec)
    scan_databases(root;spec)
  doql/adopt/scanner/deploy.py:
    e: _detect_deployment_indicators,_determine_deploy_target,_apply_deploy_config_flags,_is_database_service,_extract_container_config,_extract_containers_from_compose,_detect_rootless,_emit_infrastructure_blocks,scan_deploy
    _detect_deployment_indicators(root)
    _determine_deploy_target(indicators;deploy;root)
    _apply_deploy_config_flags(indicators;deploy)
    _is_database_service(image)
    _extract_container_config(svc_name;svc)
    _extract_containers_from_compose(compose;deploy)
    _detect_rootless(spec)
    _emit_infrastructure_blocks(indicators;spec)
    scan_deploy(root;spec)
  doql/adopt/scanner/entities.py:
    e: _is_dto_name,_is_excluded_path,scan_entities,_classify_bases,_extract_entities_from_python,_extract_annotation_fields,_extract_sqlalchemy_fields,_extract_fields,_is_reserved_sql_keyword,_extract_sql_columns,_extract_entities_from_sql
    _is_dto_name(name)
    _is_excluded_path(path)
    scan_entities(root;spec)
    _classify_bases(bases_raw)
    _extract_entities_from_python(path;spec;seen)
    _extract_annotation_fields(stripped;entity)
    _extract_sqlalchemy_fields(stripped;entity)
    _extract_fields(text;start;entity)
    _is_reserved_sql_keyword(col_name)
    _extract_sql_columns(body)
    _extract_entities_from_sql(path;spec;seen)
  doql/adopt/scanner/environments.py:
    e: _detect_local_env,_extract_env_refs,_detect_env_files,_assign_ssh_host,_detect_compose_envs,scan_environments
    _detect_local_env(root;spec)
    _extract_env_refs(env_path;spec)
    _detect_env_files(root;spec)
    _assign_ssh_host(env;name;env_refs)
    _detect_compose_envs(root;spec)
    scan_environments(root;spec)
  doql/adopt/scanner/integrations.py:
    e: scan_integrations
    scan_integrations(root;spec)
  doql/adopt/scanner/interfaces/__init__.py:
    e: scan_interfaces
    scan_interfaces(root;spec)
  doql/adopt/scanner/interfaces/api.py:
    e: _detect_framework_from_pyproject,_detect_framework_from_main_py,_detect_framework_from_any_py,_find_api_main_file,_has_api_entry_point,_detect_api_auth,_detect_api_port,scan_python_api
    _detect_framework_from_pyproject(pyproj)
    _detect_framework_from_main_py(main_py)
    _detect_framework_from_any_py(root)
    _find_api_main_file(root)
    _has_api_entry_point(pyproj)
    _detect_api_auth(spec)
    _detect_api_port(spec)
    scan_python_api(root;spec)
  doql/adopt/scanner/interfaces/cli.py:
    e: scan_python_cli
    scan_python_cli(root;spec)
  doql/adopt/scanner/interfaces/desktop.py:
    e: scan_desktop
    scan_desktop(root;spec)
  doql/adopt/scanner/interfaces/mobile.py:
    e: scan_mobile
    scan_mobile(root;spec)
  doql/adopt/scanner/interfaces/web.py:
    e: _detect_web_framework,_scan_pages_dir,_extract_web_pages,scan_web_frontend
    _detect_web_framework(root)
    _scan_pages_dir(pdir;page_seen)
    _extract_web_pages(root)
    scan_web_frontend(root;spec)
  doql/adopt/scanner/metadata.py:
    e: scan_metadata,_extract_authors,_extract_keywords,_extract_urls,_extract_dependencies,_parse_pyproject,_parse_package_json,_parse_goal_yaml
    scan_metadata(root;spec)
    _extract_authors(project;spec)
    _extract_keywords(project;spec)
    _extract_urls(project;spec)
    _extract_dependencies(project;spec)
    _parse_pyproject(path;spec)
    _parse_package_json(path;spec)
    _parse_goal_yaml(path;spec)
  doql/adopt/scanner/roles.py:
    e: _scan_sql_roles,scan_roles
    _scan_sql_roles(root;spec)
    scan_roles(root;spec)
  doql/adopt/scanner/utils.py:
    e: load_yaml,find_compose,find_dockerfiles,camel_to_kebab,snake_to_pascal,normalize_python_type,normalize_sqlalchemy_type,normalize_sql_type
    load_yaml(path)
    find_compose(root)
    find_dockerfiles(root)
    camel_to_kebab(name)
    snake_to_pascal(name)
    normalize_python_type(t)
    normalize_sqlalchemy_type(t)
    normalize_sql_type(t)
  doql/adopt/scanner/workflows.py:
    e: scan_workflows,_is_valid_target,_build_steps_from_body,_create_workflow,_extract_makefile_workflows,_parse_makefile_deps,_build_taskfile_steps,_extract_taskfile_schedule,_build_workflow_from_task,_extract_taskfile_workflows,_find_cli_candidates,_detect_cli_command_name,_build_workflow_steps,_scan_cli_file_for_workflows,_extract_python_cli_workflows
    scan_workflows(root;spec)
    _is_valid_target(name;deps_raw;seen)
    _build_steps_from_body(body;deps_raw)
    _create_workflow(name;steps)
    _extract_makefile_workflows(path;spec)
    _parse_makefile_deps(deps_raw)
    _build_taskfile_steps(task)
    _extract_taskfile_schedule(task)
    _build_workflow_from_task(task_name;task)
    _extract_taskfile_workflows(path;spec)
    _find_cli_candidates(root)
    _detect_cli_command_name(root)
    _build_workflow_steps(cmd_name;cli_command)
    _scan_cli_file_for_workflows(cli_file;cli_command;seen;spec)
    _extract_python_cli_workflows(root;spec)
  doql/adopt/scanner.py:
  doql/cli/__init__.py:
  doql/cli/__main__.py:
  doql/cli/build.py:
    e: _watch_files,should_generate_interface,run_core_generators,run_document_generators,_run_conditional_generator,run_report_generators,run_i18n_generators,run_integration_generators,run_workflow_generators,run_ci_generator,run_vite_generator,run_plugins,_scan_device_for_build,_do_build,cmd_build,_merge_no_overwrite
    _watch_files(paths;callback)
    should_generate_interface(name;spec)
    run_core_generators(spec;env_vars;ctx;no_overwrite)
    run_document_generators(spec;env_vars;ctx)
    _run_conditional_generator(ctx;condition;label;output_path;generate_fn;spec;env_vars)
    run_report_generators(spec;env_vars;ctx)
    run_i18n_generators(spec;env_vars;ctx)
    run_integration_generators(spec;env_vars;ctx)
    run_workflow_generators(spec;env_vars;ctx)
    run_ci_generator(spec;env_vars;ctx)
    run_vite_generator(spec;env_vars;ctx)
    run_plugins(spec;env_vars;ctx)
    _scan_device_for_build(ctx;args)
    _do_build(args;ctx)
    cmd_build(args)
    _merge_no_overwrite(src;dst)
  doql/cli/commands/__init__.py:
  doql/cli/commands/adopt.py:
    e: _print_item,_print_scan_summary,_cleanup_empty_output,_validate_output_written,cmd_adopt,_discover_subprojects,_scan_and_emit_subproject,_write_root_manifest,_cmd_adopt_recursive,_cmd_adopt_from_directory,_cmd_adopt_from_device
    _print_item(label;count;items;display_names)
    _print_scan_summary(spec)
    _cleanup_empty_output(output)
    _validate_output_written(output)
    cmd_adopt(args)
    _discover_subprojects(root)
    _scan_and_emit_subproject(sub;fmt;args;root_spec;written)
    _write_root_manifest(root;args;fmt;root_spec;written)
    _cmd_adopt_recursive(args)
    _cmd_adopt_from_directory(args)
    _cmd_adopt_from_device(args;device)
  doql/cli/commands/deploy.py:
    e: _run_directive,_deploy_via_redeploy_api,_deploy_via_redeploy_cli,cmd_deploy
    _run_directive(label;command)
    _deploy_via_redeploy_api(migration_yaml;dry_run;plan_only)
    _deploy_via_redeploy_cli(migration_yaml;dry_run;plan_only)
    cmd_deploy(args)
  doql/cli/commands/docs.py:
    e: cmd_docs
    cmd_docs(args)
  doql/cli/commands/doctor/__init__.py:
    e: cmd_doctor
    cmd_doctor(args)
  doql/cli/commands/doctor/checks.py:
    e: _check_parse,_find_missing_env_refs,_check_env,_collect_missing_files,_check_files,_check_databases,_warn_unknown_entity_refs,_check_interfaces,_collect_required_tools,_check_tools,_check_deploy,_check_environments
    _check_parse(root;doql_file;report)
    _find_missing_env_refs(spec;env_vars)
    _check_env(root;spec;report)
    _collect_missing_files(root;spec)
    _check_files(root;spec;report)
    _check_databases(spec;report)
    _warn_unknown_entity_refs(iface;entity_names;report)
    _check_interfaces(spec;report)
    _collect_required_tools(spec)
    _check_tools(spec;report)
    _check_deploy(spec;report;root)
    _check_environments(spec;report)
  doql/cli/commands/doctor/fixes.py:
    e: _apply_fixes
    _apply_fixes(report;root;spec)
  doql/cli/commands/doctor/remote.py:
    e: _ssh_run,_check_remote_ssh,_check_remote_runtime,_check_remote
    _ssh_run(host;cmd)
    _check_remote_ssh(host;report)
    _check_remote_runtime(host;runtime;report)
    _check_remote(spec;env_name;report)
  doql/cli/commands/doctor/report.py:
    e: _print_report,Check,DoctorReport
    Check:
    DoctorReport: add(3),ok(0),warnings(0),failures(0)
    _print_report(report)
  doql/cli/commands/drift/__init__.py:
    e: cmd_drift
    cmd_drift(args)
  doql/cli/commands/drift/export.py:
    e: _report_to_json
    _report_to_json(report;intended_file;target)
  doql/cli/commands/drift/render.py:
    e: _change_style,_render_rich,_render_plain,_fmt_value
    _change_style(change_type)
    _render_rich(report;intended_file;target)
    _render_plain(report;intended_file;target)
    _fmt_value(value)
  doql/cli/commands/export.py:
    e: cmd_export
    cmd_export(args)
  doql/cli/commands/generate.py:
    e: cmd_generate
    cmd_generate(args)
  doql/cli/commands/import_cmd.py:
    e: cmd_import
    cmd_import(args)
  doql/cli/commands/init.py:
    e: cmd_init
    cmd_init(args)
  doql/cli/commands/kiosk.py:
    e: cmd_kiosk
    cmd_kiosk(args)
  doql/cli/commands/plan.py:
    e: _print_header,_print_entities,_print_data_sources,_print_documents,_print_api_clients,_print_interfaces,_print_workflows,_print_summary,_print_file_counts,cmd_plan
    _print_header(spec)
    _print_entities(spec)
    _print_data_sources(spec)
    _print_documents(spec)
    _print_api_clients(spec)
    _print_interfaces(spec)
    _print_workflows(spec)
    _print_summary(spec)
    _print_file_counts(spec)
    cmd_plan(args)
  doql/cli/commands/publish.py:
    e: _publish_pypi,_publish_npm,_publish_docker,_extract_changelog_notes,_publish_github,cmd_publish
    _publish_pypi(root;dry_run)
    _publish_npm(root;dry_run)
    _publish_docker(root;spec;dry_run)
    _extract_changelog_notes(root;version)
    _publish_github(root;spec;dry_run)
    cmd_publish(args)
  doql/cli/commands/quadlet.py:
    e: _install_via_redeploy_api,_install_via_systemctl,cmd_quadlet
    _install_via_redeploy_api(infra_dir;app;dry_run)
    _install_via_systemctl(infra_dir;app;dry_run)
    cmd_quadlet(args)
  doql/cli/commands/query.py:
    e: cmd_query
    cmd_query(args)
  doql/cli/commands/render.py:
    e: cmd_render
    cmd_render(args)
  doql/cli/commands/run.py:
    e: _build_into,_workspace_for_file,cmd_run,_run_api,_run_web,_run_desktop,_run_target
    _build_into(doql_file;workspace)
    _workspace_for_file(doql_file)
    cmd_run(args)
    _run_api(target_dir;port)
    _run_web(target_dir;port)
    _run_desktop(target_dir)
    _run_target(build_dir;target;port)
  doql/cli/commands/validate.py:
    e: _print_issues,cmd_validate
    _print_issues(issues)
    cmd_validate(args)
  doql/cli/commands/workspace/__init__.py:
    e: cmd_workspace,register_parser
    cmd_workspace(args)
    register_parser(sub)
  doql/cli/commands/workspace/analyze.py:
    e: _analyze_workflow_issues,_analyze_content_issues,_analyze_content_recs,_analyze_project,_output_csv,_output_table,_cmd_analyze,_cmd_validate,_cmd_fix
    _analyze_workflow_issues(content)
    _analyze_content_issues(content)
    _analyze_content_recs(content;project)
    _analyze_project(project)
    _output_csv(rows;output_path)
    _output_table(rows)
    _cmd_analyze(args)
    _cmd_validate(args)
    _cmd_fix(args)
  doql/cli/commands/workspace/discovery.py:
    e: _is_project,_parse_doql,_load_project_doql,_walk_projects,_discover_local,_filter_projects,DoqlProject
    DoqlProject:  # Minimal project descriptor (used when taskfile is not instal
    _is_project(d)
    _parse_doql(content)
    _load_project_doql(proj)
    _walk_projects(current;projects;max_depth;depth)
    _discover_local(root;max_depth)
    _filter_projects(projects;doql_only;has_workflow)
  doql/cli/commands/workspace/list.py:
    e: _print_project_table,_cmd_list
    _print_project_table(projects;root)
    _cmd_list(args)
  doql/cli/commands/workspace/output.py:
    e: _print
    _print(msg)
  doql/cli/commands/workspace/run.py:
    e: _select_run_projects,_execute_single_project,_print_dry_run_commands,_print_run_summary,_cmd_run
    _select_run_projects(root;max_depth;name_pattern)
    _execute_single_project(project;action;timeout;index;total)
    _print_dry_run_commands(projects;action)
    _print_run_summary(success;total)
    _cmd_run(args)
  doql/cli/context.py:
    e: build_context,load_spec,scaffold_from_template,estimate_file_count,BuildContext
    BuildContext:  # Build context for doql commands.
    build_context(args)
    load_spec(ctx)
    scaffold_from_template(template;target)
    estimate_file_count(iface)
  doql/cli/lockfile.py:
    e: _simple_items_hash,spec_section_hashes,read_lockfile,diff_sections,write_lockfile
    _simple_items_hash(items;key_prefix;val_fn;h_fn)
    spec_section_hashes(spec;ctx)
    read_lockfile(ctx)
    diff_sections(old_hashes;new_hashes)
    write_lockfile(spec;ctx)
  doql/cli/main.py:
    e: create_parser,main
    create_parser()
    main()
  doql/cli/sync.py:
    e: determine_regeneration_set,_run_interface_generators,run_generators,cmd_sync
    determine_regeneration_set(diff_result;spec)
    _run_interface_generators(regen;spec;env_vars;ctx)
    run_generators(regen;spec;env_vars;ctx)
    cmd_sync(args)
  doql/cli.py:
  doql/drift/__init__.py:
  doql/drift/detector.py:
    e: find_intended_file,_has_unsupported_intended,parse_intended,detect_drift
    find_intended_file(directory)
    _has_unsupported_intended(directory)
    parse_intended(path)
    detect_drift(target)
  doql/exporters/__init__.py:
  doql/exporters/css/__init__.py:
    e: _render_data_layer,_render_documentation_layer,_render_infrastructure_layer,_render_integration_layer,_render_css,export_css,export_less,export_sass,export_css_file
    _render_data_layer(spec)
    _render_documentation_layer(spec)
    _render_infrastructure_layer(spec)
    _render_integration_layer(spec)
    _render_css(spec)
    export_css(spec;out)
    export_less(spec;out)
    export_sass(spec;out)
    export_css_file(spec;path;fmt)
  doql/exporters/css/format_convert.py:
    e: _unquote_simple_value,_css_to_less,_css_to_sass
    _unquote_simple_value(full_prop;val)
    _css_to_less(css_text)
    _css_to_sass(css_text)
  doql/exporters/css/helpers.py:
    e: _indent,_prop,_field_line
    _indent(lines;level)
    _prop(key;value;quote_str)
    _field_line(f)
  doql/exporters/css/renderers.py:
    e: _render_app,_render_dependencies,_render_entity,_render_data_source,_render_template,_render_document,_render_report,_render_database,_render_api_client,_render_webhook,_build_interface_props,_build_page_props,_render_interface,_render_integration,_render_workflow,_render_role,_render_deploy,_render_environment,_render_project
    _render_app(spec)
    _render_dependencies(spec)
    _render_entity(e)
    _render_data_source(ds)
    _render_template(t)
    _render_document(d)
    _render_report(r)
    _render_database(db)
    _render_api_client(ac)
    _render_webhook(wh)
    _build_interface_props(iface)
    _build_page_props(p)
    _render_interface(iface)
    _render_integration(integ)
    _render_workflow(w)
    _render_role(role)
    _render_deploy(deploy)
    _render_environment(env)
    _render_project(sub)
  doql/exporters/css_exporter.py:
  doql/exporters/markdown/__init__.py:
    e: export_markdown,export_markdown_file
    export_markdown(spec;out)
    export_markdown_file(spec;path)
  doql/exporters/markdown/sections.py:
    e: _h,_field_type_str,_entity_section,_interface_section,_workflow_section,_config_section,_document_section,_report_section
    _h(level;text)
    _field_type_str(f)
    _entity_section(e)
    _interface_section(iface)
    _workflow_section(w)
    _config_section(name;title_prefix;fields)
    _document_section(d)
    _report_section(r)
  doql/exporters/markdown/writers.py:
    e: _write_header,_write_data_sources,_write_section,_write_entities,_write_interfaces,_write_documents,_write_reports,_write_workflows,_write_roles,_write_integrations,_write_deployment
    _write_header(spec;out)
    _write_data_sources(spec;out)
    _write_section(spec;out;attr_name;title;formatter)
    _write_entities(spec;out)
    _write_interfaces(spec;out)
    _write_documents(spec;out)
    _write_reports(spec;out)
    _write_workflows(spec;out)
    _write_roles(spec;out)
    _write_integrations(spec;out)
    _write_deployment(spec;out)
  doql/exporters/markdown_exporter.py:
  doql/exporters/yaml_exporter.py:
    e: spec_to_dict,export_yaml,export_yaml_file
    spec_to_dict(spec)
    export_yaml(spec;out)
    export_yaml_file(spec;path)
  doql/generators/__init__.py:
  doql/generators/api_gen/__init__.py:
    e: _write_api_files,_write_alembic_files,_write_api_readme,generate,export_openapi
    _write_api_files(out;spec;env_vars;has_auth)
    _write_alembic_files(out;spec)
    _write_api_readme(out;spec)
    generate(spec;env_vars;out)
    export_openapi(spec;out)
  doql/generators/api_gen/alembic.py:
    e: gen_alembic_ini,gen_alembic_env,_entity_table_columns,gen_initial_migration
    gen_alembic_ini()
    gen_alembic_env()
    _entity_table_columns(ent)
    gen_initial_migration(spec)
  doql/generators/api_gen/auth.py:
    e: gen_auth
    gen_auth(spec)
  doql/generators/api_gen/common.py:
    e: sa_type,py_type,py_default,safe_name,snake
    sa_type(f)
    py_type(f)
    py_default(f)
    safe_name(name)
    snake(name)
  doql/generators/api_gen/database.py:
    e: gen_database
    gen_database(spec;env_vars)
  doql/generators/api_gen/main.py:
    e: gen_main,gen_requirements
    gen_main(spec)
    gen_requirements(has_auth)
  doql/generators/api_gen/models.py:
    e: gen_models,_gen_column_def
    gen_models(spec)
    _gen_column_def(f;known_entities)
  doql/generators/api_gen/routes.py:
    e: gen_routes,_gen_entity_routes,_gen_list_route,_gen_get_route,_gen_create_route,_gen_update_route,_gen_delete_route
    gen_routes(spec)
    _gen_entity_routes(ent)
    _gen_list_route(name;plural)
    _gen_get_route(name;lower;plural)
    _gen_create_route(name;lower;plural)
    _gen_update_route(name;lower;plural)
    _gen_delete_route(name;lower;plural)
  doql/generators/api_gen/schemas.py:
    e: gen_schemas,_gen_entity_schemas,_gen_create_schema,_gen_response_schema,_gen_update_schema
    gen_schemas(spec)
    _gen_entity_schemas(ent)
    _gen_create_schema(ent)
    _gen_response_schema(ent)
    _gen_update_schema(ent)
  doql/generators/api_gen.py:
  doql/generators/ci_gen.py:
    e: _gen_github_action,_gen_gitlab_ci,_gen_jenkinsfile,generate
    _gen_github_action(spec)
    _gen_gitlab_ci(spec)
    _gen_jenkinsfile(spec)
    generate(spec;env_vars;out)
  doql/generators/deploy.py:
    e: run
    run(ctx;target_env)
  doql/generators/desktop_gen.py:
    e: _make_solid_png,_gen_cargo_toml,_gen_tauri_conf,_gen_main_rs,_gen_build_rs,_gen_package_json,generate
    _make_solid_png(width;height;rgb)
    _gen_cargo_toml(spec)
    _gen_tauri_conf(spec)
    _gen_main_rs(spec)
    _gen_build_rs()
    _gen_package_json(spec)
    generate(spec;env_vars;out)
  doql/generators/docs_gen.py:
    e: generate
    generate(spec;out)
  doql/generators/document_gen.py:
    e: _find_template,_gen_render_script,_gen_preview_html,generate
    _find_template(spec;name)
    _gen_render_script(doc;spec)
    _gen_preview_html(doc;spec;project_root)
    generate(spec;env_vars;out;project_root)
  doql/generators/export_postman.py:
    e: run
    run(spec;out)
  doql/generators/export_ts_sdk.py:
    e: run
    run(spec;out)
  doql/generators/i18n_gen.py:
    e: _humanize,_gen_translations,generate
    _humanize(name)
    _gen_translations(spec;lang)
    generate(spec;env_vars;out)
  doql/generators/infra_gen/__init__.py:
    e: _map_deploy_strategy,generate
    _map_deploy_strategy(doql_target)
    generate(spec;env_vars;out)
  doql/generators/infra_gen/docker.py:
    e: _gen_docker_compose
    _gen_docker_compose(spec;env_vars;out)
  doql/generators/infra_gen/kiosk.py:
    e: _gen_kiosk
    _gen_kiosk(spec;env_vars;out)
  doql/generators/infra_gen/kubernetes.py:
    e: _gen_kubernetes
    _gen_kubernetes(spec;env_vars;out)
  doql/generators/infra_gen/migration.py:
    e: _gen_migration_spec
    _gen_migration_spec(spec;env_vars;out)
  doql/generators/infra_gen/nginx.py:
    e: _gen_nginx
    _gen_nginx(spec;env_vars;out)
  doql/generators/infra_gen/quadlet.py:
    e: _gen_quadlet
    _gen_quadlet(spec;env_vars;out)
  doql/generators/infra_gen/terraform.py:
    e: _gen_terraform
    _gen_terraform(spec;env_vars;out)
  doql/generators/integrations_gen.py:
    e: _gen_email_service,_gen_slack_service,_gen_storage_service,_gen_notifications,_gen_api_client,_gen_webhook_dispatcher,_setup_services_dir,_generate_integration_services,_generate_api_clients,_generate_webhooks,generate
    _gen_email_service()
    _gen_slack_service()
    _gen_storage_service()
    _gen_notifications(integrations)
    _gen_api_client(client)
    _gen_webhook_dispatcher(webhooks)
    _setup_services_dir(out)
    _generate_integration_services(integrations;services_dir;generated)
    _generate_api_clients(spec;services_dir;generated)
    _generate_webhooks(spec;services_dir;generated)
    generate(spec;env_vars;out)
  doql/generators/mobile_gen.py:
    e: _gen_manifest,_gen_service_worker,_gen_index_html,_gen_app_js,_gen_style_css,_gen_icons,generate
    _gen_manifest(spec)
    _gen_service_worker(spec)
    _gen_index_html(spec)
    _gen_app_js(spec)
    _gen_style_css()
    _gen_icons(out;spec)
    generate(spec;env_vars;out)
  doql/generators/report_gen.py:
    e: _gen_report_script,generate
    _gen_report_script(rpt;spec)
    generate(spec;env_vars;out)
  doql/generators/utils/codegen.py:
    e: write_code_block,generate_file_from_template
    write_code_block(content;path)
    generate_file_from_template(template_name;variables;output_path)
  doql/generators/vite_gen.py:
    e: _gen_vite_config,_gen_tsconfig,_gen_index_html,generate
    _gen_vite_config(spec;env_vars;out)
    _gen_tsconfig(spec;out)
    _gen_index_html(spec;out)
    generate(spec;env_vars;out)
  doql/generators/web_gen/__init__.py:
    e: _setup_web_directories,_write_config_files,_write_core_files,_write_component_files,_write_page_files,_write_pwa_files,_write_readme,generate
    _setup_web_directories(out)
    _write_config_files(out;spec)
    _write_core_files(src;spec)
    _write_component_files(components;spec;web_pages)
    _write_page_files(pages;spec)
    _write_pwa_files(out;src;spec)
    _write_readme(out;spec;is_pwa)
    generate(spec;env_vars;out)
  doql/generators/web_gen/common.py:
  doql/generators/web_gen/components.py:
    e: _gen_layout
    _gen_layout(spec;pages;entities)
  doql/generators/web_gen/config.py:
    e: _gen_package_json,_gen_vite_config,_gen_tailwind_config,_gen_postcss_config,_gen_tsconfig,_gen_index_html
    _gen_package_json(spec)
    _gen_vite_config()
    _gen_tailwind_config()
    _gen_postcss_config()
    _gen_tsconfig()
    _gen_index_html(spec)
  doql/generators/web_gen/core.py:
    e: _gen_main_tsx,_gen_index_css,_gen_api_ts
    _gen_main_tsx()
    _gen_index_css()
    _gen_api_ts()
  doql/generators/web_gen/pages.py:
    e: _gen_dashboard,_field_input,_build_interface_body,_gen_entity_page
    _gen_dashboard(spec)
    _field_input(f)
    _build_interface_body(visible_fields)
    _gen_entity_page(ent)
  doql/generators/web_gen/pwa.py:
    e: _gen_manifest,_gen_service_worker,_gen_sw_register
    _gen_manifest(spec)
    _gen_service_worker(spec)
    _gen_sw_register()
  doql/generators/web_gen/router.py:
    e: _gen_app
    _gen_app(spec)
  doql/generators/web_gen.py:
  doql/generators/workflow_gen.py:
    e: _gen_engine,_step_fn_name,_gen_workflow_module,_extract_cron,_gen_scheduler,_gen_init,_gen_routes,generate
    _gen_engine()
    _step_fn_name(action)
    _gen_workflow_module(wf;spec)
    _extract_cron(sched)
    _gen_scheduler(spec)
    _gen_init(spec)
    _gen_routes(spec)
    generate(spec;env_vars;out)
  doql/importers/__init__.py:
  doql/importers/yaml_importer.py:
    e: _get,_build_entity_field,_build_entity,_build_data_source,_build_template,_build_document,_build_report,_build_database,_build_api_client,_build_webhook,_build_page,_build_interface,_build_integration,_build_workflow_step,_build_workflow,_build_role,_build_deploy,_import_metadata,_import_collection,import_yaml,import_yaml_text,import_yaml_file
    _get(d;key;default)
    _build_entity_field(data)
    _build_entity(data)
    _build_data_source(data)
    _build_template(data)
    _build_document(data)
    _build_report(data)
    _build_database(data)
    _build_api_client(data)
    _build_webhook(data)
    _build_page(data)
    _build_interface(data)
    _build_integration(data)
    _build_workflow_step(data)
    _build_workflow(data)
    _build_role(data)
    _build_deploy(data)
    _import_metadata(data;spec)
    _import_collection(data;spec;key;builder)
    import_yaml(data)
    import_yaml_text(text)
    import_yaml_file(path)
  doql/integrations/__init__.py:
  doql/integrations/op3_bridge.py:
    e: build_layer_tree,snapshot_to_less
    build_layer_tree(layer_ids)
    snapshot_to_less(snapshot;scope)
  doql/lsp_server/__init__.py:
    e: main
    main()
  doql/lsp_server/completion.py:
    e: completion
    completion(ls;params)
  doql/lsp_server/definition.py:
    e: definition
    definition(ls;params)
  doql/lsp_server/diagnostics.py:
    e: _diagnostics_for,_on_text_document_event,did_open,did_change,did_save
    _diagnostics_for(source;uri)
    _on_text_document_event(ls;uri)
    did_open(ls;params)
    did_change(ls;params)
    did_save(ls;params)
  doql/lsp_server/hover.py:
    e: _hover_field,_hover_entity,hover
    _hover_field(ent;f)
    _hover_entity(spec;word)
    hover(ls;params)
  doql/lsp_server/symbols.py:
    e: document_symbols
    document_symbols(ls;params)
  doql/lsp_server/utils.py:
    e: _parse_doc,_find_line_col,_word_at
    _parse_doc(source)
    _find_line_col(source;needle)
    _word_at(source;position)
  doql/parser.py:
  doql/parsers/__init__.py:
    e: _is_css_format,detect_doql_file,parse_file,parse_text,parse_env
    _is_css_format(path)
    detect_doql_file(root)
    parse_file(path)
    parse_text(text)
    parse_env(path)
  doql/parsers/blocks.py:
    e: split_blocks,apply_block
    split_blocks(text)
    apply_block(spec;keyword;header;body)
  doql/parsers/css_mappers/__init__.py:
    e: _map_project
    _map_project(spec;sel;block)
  doql/parsers/css_mappers/config.py:
    e: _map_config_block,_map_template,_map_document,_map_report
    _map_config_block(spec;sel;block;model_class;list_attr;defaults;list_fields)
    _map_template(spec;sel;block)
    _map_document(spec;sel;block)
    _map_report(spec;sel;block)
  doql/parsers/css_mappers/entity.py:
    e: _map_entity,_parse_type_flags,_add_entity_field,_parse_type_modifiers,_map_data_source
    _map_entity(spec;sel;block)
    _parse_type_flags(type_str)
    _add_entity_field(entity;name;type_str)
    _parse_type_modifiers(current_type)
    _map_data_source(spec;sel;block)
  doql/parsers/css_mappers/infra.py:
    e: _map_deploy,_map_database,_map_environment,_map_infrastructure,_map_ingress,_map_ci
    _map_deploy(spec;sel;block)
    _map_database(spec;sel;block)
    _map_environment(spec;sel;block)
    _map_infrastructure(spec;sel;block)
    _map_ingress(spec;sel;block)
    _map_ci(spec;sel;block)
  doql/parsers/css_mappers/integration.py:
    e: _map_integration
    _map_integration(spec;sel;block)
  doql/parsers/css_mappers/interface.py:
    e: _find_or_create_interface,_handle_interface_chain,_apply_interface_properties,_apply_nested_interface_children,_map_interface,_add_interface_page
    _find_or_create_interface(spec;name)
    _handle_interface_chain(iface;sel;block)
    _apply_interface_properties(iface;block)
    _apply_nested_interface_children(iface;block)
    _map_interface(spec;sel;block)
    _add_interface_page(iface;sel;block)
  doql/parsers/css_mappers/workflow.py:
    e: _parse_step_text,_append_inline_steps,_append_child_steps,_map_workflow,_map_role
    _parse_step_text(step_text)
    _append_inline_steps(wf;block;strip_quotes_fn)
    _append_child_steps(wf;block;parse_selector_fn;strip_quotes_fn)
    _map_workflow(spec;sel;block)
    _map_role(spec;sel;block)
  doql/parsers/css_parser.py:
    e: _map_to_spec,_apply_css_block,parse_css_file,parse_css_text,_detect_format
    _map_to_spec(blocks)
    _apply_css_block(spec;sel;block)
    parse_css_file(path)
    parse_css_text(text;format)
    _detect_format(path)
  doql/parsers/css_tokenizer.py:
    e: _make_css_block,_tokenise_css,_consume_pending,_process_decl_line,_parse_declarations
    _make_css_block(selector;body;line_num)
    _tokenise_css(text)
    _consume_pending(decls;pending_key;pending_value)
    _process_decl_line(stripped;pending_key;pending_value;decls)
    _parse_declarations(body)
  doql/parsers/css_transformers/__init__.py:
    e: _sass_to_css
    _sass_to_css(text)
  doql/parsers/css_transformers/indent.py:
    e: _close_indent_blocks,_convert_indent_to_braces
    _close_indent_blocks(result_lines;indent_stack;current_indent)
    _convert_indent_to_braces(lines)
  doql/parsers/css_transformers/mixins.py:
    e: _extract_mixins,_expand_includes
    _extract_mixins(lines)
    _expand_includes(lines;mixins)
  doql/parsers/css_transformers/selectors.py:
    e: _is_doql_property_decl,_is_selector_line,_is_step_line,_has_bracket_selector,_is_selector_starter,_find_step_block_end
    _is_doql_property_decl(stripped)
    _is_selector_line(stripped)
    _is_step_line(line)
    _has_bracket_selector(stripped)
    _is_selector_starter(line)
    _find_step_block_end(lines;start_idx;start_indent)
  doql/parsers/css_transformers/variables.py:
    e: _resolve_vars,_resolve_less_vars,_resolve_sass_vars
    _resolve_vars(text;prefix)
    _resolve_less_vars(text)
    _resolve_sass_vars(text)
  doql/parsers/css_utils.py:
    e: _strip_comments,_strip_quotes,_parse_list,_parse_selector,CssBlock,ParsedSelector
    CssBlock:  # Single CSS-like rule: selector + key-value declarations.
    ParsedSelector:  # Decomposed CSS selector.
    _strip_comments(text)
    _strip_quotes(val)
    _parse_list(val)
    _parse_selector(selector)
  doql/parsers/extractors.py:
    e: extract_val,extract_list,extract_yaml_list,_extract_page_from_format1,_extract_page_from_format2,extract_pages,_should_skip_line,_is_valid_field_name,_parse_field_flags,_parse_field_ref,_parse_field_default,_parse_field_type,extract_entity_fields,collect_env_refs
    extract_val(body;key)
    extract_list(body;key)
    extract_yaml_list(body;key)
    _extract_page_from_format1(body)
    _extract_page_from_format2(body)
    extract_pages(body)
    _should_skip_line(line)
    _is_valid_field_name(name)
    _parse_field_flags(ftype_raw)
    _parse_field_ref(ftype_raw)
    _parse_field_default(ftype_raw)
    _parse_field_type(ftype_raw)
    extract_entity_fields(body)
    collect_env_refs(text)
  doql/parsers/models.py:
    e: DoqlParseError,ValidationIssue,EntityField,Entity,DataSource,Template,Document,Report,Database,ApiClient,Webhook,Page,Interface,Integration,WorkflowStep,Workflow,Role,Deploy,Environment,Infrastructure,Ingress,CiConfig,Subproject,DoqlSpec
    DoqlParseError:  # Raised when a .doql file cannot be parsed.
    ValidationIssue:
    EntityField:
    Entity:
    DataSource:
    Template:
    Document:
    Report:
    Database:
    ApiClient:
    Webhook:
    Page:
    Interface:
    Integration:
    WorkflowStep:
    Workflow:
    Role:
    Deploy:
    Environment:
    Infrastructure:
    Ingress:
    CiConfig:
    Subproject:  # A named sub-project inside a monorepo DOQL manifest.
    DoqlSpec:
  doql/parsers/registry.py:
    e: register,get_handler,list_registered,_handle_app,_handle_version,_handle_domain,_handle_languages,_handle_author,_handle_default_language,_handle_entity,_handle_data,_handle_template,_handle_document,_handle_report,_handle_database,_handle_api_client,_handle_webhook,_handle_interface,_handle_integration,_handle_workflow,_handle_roles,_handle_role,_handle_import_block,_handle_scenarios,_handle_tests,_handle_deploy,_handle_infrastructure,_handle_ingress,_handle_ci,_handle_project
    register(keyword)
    get_handler(keyword)
    list_registered()
    _handle_app(spec;header;body)
    _handle_version(spec;header;body)
    _handle_domain(spec;header;body)
    _handle_languages(spec;header;body)
    _handle_author(spec;header;body)
    _handle_default_language(spec;header;body)
    _handle_entity(spec;header;body)
    _handle_data(spec;header;body)
    _handle_template(spec;header;body)
    _handle_document(spec;header;body)
    _handle_report(spec;header;body)
    _handle_database(spec;header;body)
    _handle_api_client(spec;header;body)
    _handle_webhook(spec;header;body)
    _handle_interface(spec;header;body)
    _handle_integration(spec;header;body)
    _handle_workflow(spec;header;body)
    _handle_roles(spec;header;body)
    _handle_role(spec;header;body)
    _handle_import_block(spec;body;target_attr)
    _handle_scenarios(spec;header;body)
    _handle_tests(spec;header;body)
    _handle_deploy(spec;header;body)
    _handle_infrastructure(spec;header;body)
    _handle_ingress(spec;header;body)
    _handle_ci(spec;header;body)
    _handle_project(spec;header;body)
  doql/parsers/validators.py:
    e: _validate_app_name,_validate_env_refs,_validate_data_source_files,_validate_file_refs,_validate_document_templates,_validate_template_files,_validate_document_partials,_validate_entity_refs,_validate_interfaces,_validate_deploy_strategy,validate
    _validate_app_name(spec)
    _validate_env_refs(spec;env_vars)
    _validate_data_source_files(spec;project_root)
    _validate_file_refs(items;project_root;item_type;name_attr;file_attr;error_msg)
    _validate_document_templates(spec;project_root)
    _validate_template_files(spec;project_root)
    _validate_document_partials(spec)
    _validate_entity_refs(spec)
    _validate_interfaces(spec)
    _validate_deploy_strategy(spec)
    validate(spec;env_vars;project_root)
  doql/plugins.py:
    e: _discover_entry_points,_discover_local,discover_plugins,run_plugins,Plugin
    Plugin:
    _discover_entry_points()
    _discover_local(project_root)
    discover_plugins(project_root)
    run_plugins(spec;env_vars;build_dir;project_root)
  doql/utils/__init__.py:
  doql/utils/clean.py:
    e: _clean
    _clean(obj)
  doql/utils/naming.py:
    e: snake,kebab,slug
    snake(name)
    kebab(name)
    slug(name)
  playground/doql_build.py:
    e: _collect_parse_errors,_build_env,_validate,_spec_summary,_try_generate,build
    _collect_parse_errors(spec;diags)
    _build_env(spec)
    _validate(spec;env;diags)
    _spec_summary(spec)
    _try_generate(spec;result)
    build(source)
  plugins/doql-plugin-erp/doql_plugin_erp/__init__.py:
    e: _odoo_client_module,_mapping_module,_sync_module,_webhook_module,_readme,generate
    _odoo_client_module()
    _mapping_module()
    _sync_module()
    _webhook_module()
    _readme(spec)
    generate(spec;env_vars;out;project_root)
  plugins/doql-plugin-fleet/doql_plugin_fleet/__init__.py:
    e: _readme,generate
    _readme(spec)
    generate(spec;env_vars;out;project_root)
  plugins/doql-plugin-fleet/doql_plugin_fleet/device_registry.py:
    e: _device_registry_module
    _device_registry_module()
  plugins/doql-plugin-fleet/doql_plugin_fleet/metrics.py:
    e: _metrics_module
    _metrics_module()
  plugins/doql-plugin-fleet/doql_plugin_fleet/migration.py:
    e: _migration_module
    _migration_module()
  plugins/doql-plugin-fleet/doql_plugin_fleet/ota.py:
    e: _ota_module
    _ota_module()
  plugins/doql-plugin-fleet/doql_plugin_fleet/tenant.py:
    e: _tenant_module
    _tenant_module()
  plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py:
    e: _audit_log_module,_e_signature_module,_audit_middleware,_migration_audit,_readme,generate
    _audit_log_module()
    _e_signature_module()
    _audit_middleware()
    _migration_audit()
    _readme(spec)
    generate(spec;env_vars;out;project_root)
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/__init__.py:
    e: generate
    generate(spec;env_vars;out;project_root)
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py:
    e: generate
    generate()
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/drift_monitor.py:
    e: generate
    generate()
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/migration.py:
    e: generate
    generate()
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/traceability.py:
    e: generate
    generate()
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/uncertainty.py:
    e: generate
    generate()
  plugins/doql-plugin-shared/doql_plugin_shared/__init__.py:
  plugins/doql-plugin-shared/doql_plugin_shared/base.py:
    e: plugin_generate
    plugin_generate(out;modules;readme_content)
  plugins/doql-plugin-shared/doql_plugin_shared/readme.py:
    e: generate_readme
    generate_readme(plugin_name;modules;description;usage_extra)
  tests/__init__.py:
  tests/env_manager.py:
    e: _find_free_port,_has_module,_run,_api_present_files,_api_compile_check,_check_postgres_skip,_wait_health,_check_api_openapi,check_api,check_web,check_mobile,_check_tauri_conf,_check_desktop_files,_check_main_rs,_check_cargo,check_desktop,check_infra,process_example,render_text,render_json,main,CheckResult,TargetReport,ExampleReport
    CheckResult: icon(0)
    TargetReport: ok(0)
    ExampleReport: ok(0)
    _find_free_port()
    _has_module(name)
    _run(cmd;cwd;timeout)
    _api_present_files(api_dir)
    _api_compile_check(api_dir;files)
    _check_postgres_skip(api_dir)
    _wait_health(port;proc)
    _check_api_openapi(port)
    check_api(api_dir)
    check_web(web_dir)
    check_mobile(mob_dir)
    _check_tauri_conf(src_tauri)
    _check_desktop_files(src_tauri)
    _check_main_rs(src_tauri)
    _check_cargo(cargo_check;src_tauri)
    check_desktop(desk_dir)
    check_infra(infra_dir)
    process_example(doql_dir)
    render_text(reports)
    render_json(reports)
    main(argv)
  tests/integration/__init__.py:
  tests/integration/test_adopt_from_device.py:
    e: _healthy_rpi_responses,_rpi5_podman_quadlet_responses,test_adopt_from_device_returns_less_text,test_adopt_from_device_writes_output,test_adopt_from_device_to_snapshot_contains_layer_data,test_adopt_output_is_parsable_by_doql,test_adopt_from_rpi5_podman_quadlet_returns_less_text,test_adopt_from_rpi5_to_snapshot_contains_all_services,test_adopt_from_rpi5_to_snapshot_contains_all_containers,test_adopt_from_rpi5_output_is_parsable_by_doql,_make_cli_args,test_cmd_adopt_from_device_writes_file,test_cmd_adopt_rejects_non_less_format,test_cmd_adopt_without_target_or_device_errors,test_cmd_adopt_refuses_to_overwrite
    _healthy_rpi_responses()
    _rpi5_podman_quadlet_responses()
    test_adopt_from_device_returns_less_text()
    test_adopt_from_device_writes_output(tmp_path)
    test_adopt_from_device_to_snapshot_contains_layer_data()
    test_adopt_output_is_parsable_by_doql(tmp_path)
    test_adopt_from_rpi5_podman_quadlet_returns_less_text()
    test_adopt_from_rpi5_to_snapshot_contains_all_services()
    test_adopt_from_rpi5_to_snapshot_contains_all_containers()
    test_adopt_from_rpi5_output_is_parsable_by_doql(tmp_path)
    _make_cli_args()
    test_cmd_adopt_from_device_writes_file(tmp_path;monkeypatch;capsys)
    test_cmd_adopt_rejects_non_less_format(capsys)
    test_cmd_adopt_without_target_or_device_errors(capsys)
    test_cmd_adopt_refuses_to_overwrite(tmp_path;monkeypatch;capsys)
  tests/integration/test_build_from_device.py:
    e: _healthy_rpi_responses,_build_args,_patch_context_factory,test_scan_device_writes_app_doql_less_in_root,test_scan_device_honours_global_file_flag,test_scan_device_refuses_to_overwrite_without_force,test_scan_device_force_overwrites,_minimal_env_file,test_cmd_build_from_device_runs_full_pipeline,test_cmd_build_refuses_to_clobber_without_force,test_cmd_build_without_from_device_skips_scan
    _healthy_rpi_responses()
    _build_args(root)
    _patch_context_factory(monkeypatch;responses)
    test_scan_device_writes_app_doql_less_in_root(tmp_path;monkeypatch;capsys)
    test_scan_device_honours_global_file_flag(tmp_path;monkeypatch)
    test_scan_device_refuses_to_overwrite_without_force(tmp_path;monkeypatch;capsys)
    test_scan_device_force_overwrites(tmp_path;monkeypatch)
    _minimal_env_file(root)
    test_cmd_build_from_device_runs_full_pipeline(tmp_path;monkeypatch;capsys)
    test_cmd_build_refuses_to_clobber_without_force(tmp_path;monkeypatch;capsys)
    test_cmd_build_without_from_device_skips_scan(tmp_path;monkeypatch)
  tests/integration/test_drift.py:
    e: _rpi_responses_with_service,_intended_less,test_parse_intended_attaches_source_path,test_parse_intended_missing_file,test_detect_drift_no_changes,test_detect_drift_service_state_mismatch,test_detect_drift_missing_file_raises,_args,_patch_context,test_cmd_drift_returns_drift_exit_code,test_cmd_drift_json_output_is_valid,test_cmd_drift_missing_from_device,test_cmd_drift_missing_file,test_cmd_drift_unsupported_format_gives_actionable_hint,test_cmd_drift_explicit_missing_file,test_cmd_drift_no_drift_exit_code_zero
    _rpi_responses_with_service(active_state)
    _intended_less(service_name;active)
    test_parse_intended_attaches_source_path(tmp_path)
    test_parse_intended_missing_file(tmp_path)
    test_detect_drift_no_changes(tmp_path)
    test_detect_drift_service_state_mismatch(tmp_path)
    test_detect_drift_missing_file_raises(tmp_path;monkeypatch)
    _args()
    _patch_context(monkeypatch;responses)
    test_cmd_drift_returns_drift_exit_code(tmp_path;monkeypatch;capsys)
    test_cmd_drift_json_output_is_valid(tmp_path;monkeypatch;capsys)
    test_cmd_drift_missing_from_device(capsys)
    test_cmd_drift_missing_file(tmp_path;monkeypatch;capsys)
    test_cmd_drift_unsupported_format_gives_actionable_hint(tmp_path;monkeypatch;capsys)
    test_cmd_drift_explicit_missing_file(tmp_path;capsys)
    test_cmd_drift_no_drift_exit_code_zero(tmp_path;monkeypatch;capsys)
  tests/integration/test_op3_bridge.py:
    e: test_op3_importable,test_op3_enabled_reads_env,test_should_use_op3_requires_both,test_require_op3_noop_when_available,test_build_layer_tree_defaults,test_build_layer_tree_explicit_leaf_pulls_deps,test_build_layer_tree_rejects_unknown,test_scanner_runs_against_mock_context,test_snapshot_to_less_produces_parsable_less
    test_op3_importable()
    test_op3_enabled_reads_env(monkeypatch;value;expected)
    test_should_use_op3_requires_both(monkeypatch)
    test_require_op3_noop_when_available()
    test_build_layer_tree_defaults()
    test_build_layer_tree_explicit_leaf_pulls_deps()
    test_build_layer_tree_rejects_unknown()
    test_scanner_runs_against_mock_context()
    test_snapshot_to_less_produces_parsable_less()
  tests/playground_e2e.py:
    e: serve,main,_QuietHandler
    _QuietHandler: log_message(0)
    serve()
    main()
  tests/runtime_smoke.py:
    e: step,main
    step(client;name;response;expected)
    main()
  tests/test_adopt.py:
    e: _write,_pyproject,test_jwt_secret_does_not_crash_renderer,test_pydantic_dtos_are_excluded_from_entities,test_generic_db_service_name_is_normalised,test_fastapi_dependency_alone_does_not_create_api_interface,test_fastapi_with_main_py_creates_api,test_api_entry_point_in_scripts_creates_api,_make_args,test_cmd_adopt_returns_zero_on_success,test_cmd_adopt_returns_nonzero_on_render_failure,test_cmd_adopt_refuses_to_overwrite_without_force,test_cmd_adopt_rejects_non_directory,test_makefile_targets_become_workflows,test_makefile_workflows_round_trip_to_css,test_taskfile_yml_tasks_become_workflows,test_dependency_only_targets_emit_depend_steps,test_empty_target_without_deps_is_skipped,test_makefile_variable_assignments_are_not_workflows,test_workflows_are_deduplicated_across_makefile_and_taskfile,_assert_oqlos_metadata,_assert_oqlos_interfaces,_assert_oqlos_deploy,_assert_oqlos_workflows,_assert_oqlos_entities,_assert_oqlos_environments,_assert_adopt_roundtrip,test_adopt_e2e_real_project_oqlos,test_discover_subprojects,test_click_not_inferred_from_comment_or_changelog,test_fastapi_detected_from_server_py
    _write(root;rel;body)
    _pyproject(name;deps)
    test_jwt_secret_does_not_crash_renderer(tmp_path)
    test_pydantic_dtos_are_excluded_from_entities(tmp_path)
    test_generic_db_service_name_is_normalised(tmp_path)
    test_fastapi_dependency_alone_does_not_create_api_interface(tmp_path)
    test_fastapi_with_main_py_creates_api(tmp_path)
    test_api_entry_point_in_scripts_creates_api(tmp_path)
    _make_args(target;output;force)
    test_cmd_adopt_returns_zero_on_success(tmp_path)
    test_cmd_adopt_returns_nonzero_on_render_failure(tmp_path;monkeypatch)
    test_cmd_adopt_refuses_to_overwrite_without_force(tmp_path)
    test_cmd_adopt_rejects_non_directory(tmp_path;capsys)
    test_makefile_targets_become_workflows(tmp_path)
    test_makefile_workflows_round_trip_to_css(tmp_path)
    test_taskfile_yml_tasks_become_workflows(tmp_path)
    test_dependency_only_targets_emit_depend_steps(tmp_path)
    test_empty_target_without_deps_is_skipped(tmp_path)
    test_makefile_variable_assignments_are_not_workflows(tmp_path)
    test_workflows_are_deduplicated_across_makefile_and_taskfile(tmp_path)
    _assert_oqlos_metadata(spec)
    _assert_oqlos_interfaces(spec)
    _assert_oqlos_deploy(spec)
    _assert_oqlos_workflows(spec)
    _assert_oqlos_entities(spec)
    _assert_oqlos_environments(spec)
    _assert_adopt_roundtrip(tmp_path)
    test_adopt_e2e_real_project_oqlos(tmp_path)
    test_discover_subprojects(tmp_path)
    test_click_not_inferred_from_comment_or_changelog(tmp_path)
    test_fastapi_detected_from_server_py(tmp_path)
  tests/test_css_parser.py:
    e: test_css_parse_minimal,test_css_parse_entity,test_css_parse_interface,test_css_parse_role,test_css_parse_deploy,test_less_variable_expansion,test_sass_basic_parsing,test_parses_css_example_file,test_detect_doql_file_prefers_less,test_detect_doql_file_prefers_sass,test_detect_doql_file_falls_back_to_classic,test_iot_fleet_less_has_entities,test_notes_app_sass_has_all_interfaces,test_css_parse_error_has_line_info,test_css_unknown_selector_gives_warning,test_less_syntax_error_recovery,_spec_to_comparable_dict,test_doql_vs_less_regression,test_css_parse_project_blocks
    test_css_parse_minimal()
    test_css_parse_entity()
    test_css_parse_interface()
    test_css_parse_role()
    test_css_parse_deploy()
    test_less_variable_expansion()
    test_sass_basic_parsing()
    test_parses_css_example_file(example;fmt)
    test_detect_doql_file_prefers_less(tmp_path)
    test_detect_doql_file_prefers_sass(tmp_path)
    test_detect_doql_file_falls_back_to_classic(tmp_path)
    test_iot_fleet_less_has_entities()
    test_notes_app_sass_has_all_interfaces()
    test_css_parse_error_has_line_info()
    test_css_unknown_selector_gives_warning()
    test_less_syntax_error_recovery()
    _spec_to_comparable_dict(spec)
    test_doql_vs_less_regression(example)
    test_css_parse_project_blocks()
  tests/test_deploy.py:
    e: _args,_spec_with_directives,test_run_directive_calls_shell,test_run_directive_returns_nonzero_on_failure,test_redeploy_api_returns_minus_one_when_not_installed,_import_without_redeploy,test_redeploy_cli_returns_minus_one_when_not_on_path,test_redeploy_cli_runs_subprocess_when_available,test_redeploy_cli_passes_dry_run_and_plan_only,test_deploy_uses_directives_when_no_migration_yaml,test_deploy_directive_failure_stops_pipeline,test_deploy_skips_missing_directive_phases,test_deploy_docker_compose_fallback_no_migration_no_directives,test_deploy_fallback_fails_when_no_build,test_deploy_prefers_redeploy_api_when_migration_yaml_exists,test_deploy_falls_back_to_redeploy_cli_when_api_unavailable,test_deploy_warns_when_redeploy_missing_and_no_directives,test_dry_run_and_plan_only_passed_to_redeploy,test_target_env_defaults_to_prod
    _args()
    _spec_with_directives()
    test_run_directive_calls_shell()
    test_run_directive_returns_nonzero_on_failure()
    test_redeploy_api_returns_minus_one_when_not_installed(tmp_path)
    _import_without_redeploy(name)
    test_redeploy_cli_returns_minus_one_when_not_on_path()
    test_redeploy_cli_runs_subprocess_when_available()
    test_redeploy_cli_passes_dry_run_and_plan_only()
    test_deploy_uses_directives_when_no_migration_yaml(tmp_path;capsys)
    test_deploy_directive_failure_stops_pipeline(tmp_path)
    test_deploy_skips_missing_directive_phases(tmp_path)
    test_deploy_docker_compose_fallback_no_migration_no_directives(tmp_path)
    test_deploy_fallback_fails_when_no_build(tmp_path)
    test_deploy_prefers_redeploy_api_when_migration_yaml_exists(tmp_path)
    test_deploy_falls_back_to_redeploy_cli_when_api_unavailable(tmp_path)
    test_deploy_warns_when_redeploy_missing_and_no_directives(tmp_path;capsys)
    test_dry_run_and_plan_only_passed_to_redeploy(tmp_path)
    test_target_env_defaults_to_prod(tmp_path)
  tests/test_exporters.py:
    e: sample_spec,test_yaml_roundtrip_real_example,test_css_export_real_example,test_markdown_export_real_example,test_css_export_project_blocks,TestYamlExporter,TestMarkdownExporter,TestCssExporter,TestYamlImporter
    TestYamlExporter: test_export_basic_fields(1),test_export_entities(1),test_export_interfaces(1),test_export_workflows(1),test_export_roles(1),test_export_deploy(1),test_clean_removes_empty_and_none(0)
    TestMarkdownExporter: test_export_has_title(1),test_export_has_entities(1),test_export_has_interfaces(1),test_export_has_workflows(1),test_export_has_roles(1),test_export_has_deploy(1),test_export_minimal_spec(0)
    TestCssExporter: test_export_app_block(1),test_export_entity_block(1),test_export_interface_and_pages(1),test_export_workflow(1),test_export_roles(1),test_export_deploy_no_duplicate(1),test_export_less_format(1),test_export_sass_format(1)
    TestYamlImporter: test_roundtrip_yaml(1),test_import_entities(0),test_import_interfaces_with_pages(0),test_import_workflows(0),test_import_roles(0),test_import_deploy(0),test_import_from_dict(0),test_invalid_yaml_root(0)
    sample_spec()
    test_yaml_roundtrip_real_example(example)
    test_css_export_real_example(example)
    test_markdown_export_real_example(example)
    test_css_export_project_blocks()
  tests/test_exporters_shims.py:
    e: test_css_exporter_shim_re_exports_public_api,test_css_exporter_shim_re_exports_renderers,test_css_exporter_shim_re_exports_format_helpers,test_markdown_exporter_shim_re_exports_public_api,test_markdown_exporter_shim_re_exports_writers,test_markdown_exporter_shim_re_exports_helpers,test_css_shim_roundtrip_matches_direct_subpackage
    test_css_exporter_shim_re_exports_public_api()
    test_css_exporter_shim_re_exports_renderers()
    test_css_exporter_shim_re_exports_format_helpers()
    test_markdown_exporter_shim_re_exports_public_api()
    test_markdown_exporter_shim_re_exports_writers()
    test_markdown_exporter_shim_re_exports_helpers()
    test_css_shim_roundtrip_matches_direct_subpackage(tmp_path)
  tests/test_generators.py:
    e: _run_doql,_compile_all_py,test_build_example,test_init_and_build_template,test_sync_no_changes_is_noop,test_list_templates_includes_all
    _run_doql()
    _compile_all_py(root)
    test_build_example(example;tmp_path)
    test_init_and_build_template(template;tmp_path)
    test_sync_no_changes_is_noop(tmp_path)
    test_list_templates_includes_all()
  tests/test_lsp.py:
    e: test_parse_doc_handles_valid_input,test_parse_doc_returns_none_on_crash,test_find_line_col_finds_needle,test_word_at_extracts_word,test_diagnostics_on_asset_management_example,test_keyword_completion_includes_common_top_level
    test_parse_doc_handles_valid_input()
    test_parse_doc_returns_none_on_crash()
    test_find_line_col_finds_needle()
    test_word_at_extracts_word()
    test_diagnostics_on_asset_management_example()
    test_keyword_completion_includes_common_top_level()
  tests/test_parser.py:
    e: test_parse_text_minimal,test_parse_text_full_entity,test_parse_text_languages_list,test_parse_text_workflow_with_schedule_and_inline_comment,test_parse_text_recovers_from_broken_block,test_parse_errors_is_a_list,test_parses_example_file,test_asset_management_entities,test_validate_detects_missing_env_ref,test_validation_issue_has_line_field,test_validate_detects_dangling_entity_ref,test_calibration_lab_has_no_dangling_refs,test_deprecated_docker_compose_strategy_warns,test_deprecated_quadlet_strategy_warns,test_canonical_strategy_no_warning
    test_parse_text_minimal()
    test_parse_text_full_entity()
    test_parse_text_languages_list()
    test_parse_text_workflow_with_schedule_and_inline_comment()
    test_parse_text_recovers_from_broken_block()
    test_parse_errors_is_a_list()
    test_parses_example_file(example)
    test_asset_management_entities()
    test_validate_detects_missing_env_ref()
    test_validation_issue_has_line_field()
    test_validate_detects_dangling_entity_ref()
    test_calibration_lab_has_no_dangling_refs()
    test_deprecated_docker_compose_strategy_warns()
    test_deprecated_quadlet_strategy_warns()
    test_canonical_strategy_no_warning()
  tests/test_parser_benchmark.py:
    e: test_css_parser_cold_start_under_threshold,test_less_parser_variable_resolution_under_threshold,test_real_example_parse_under_threshold,test_css_vs_classic_parse_time_parity,test_large_file_parse_under_threshold
    test_css_parser_cold_start_under_threshold()
    test_less_parser_variable_resolution_under_threshold()
    test_real_example_parse_under_threshold(example;fmt)
    test_css_vs_classic_parse_time_parity()
    test_large_file_parse_under_threshold()
  tests/test_plugins.py:
    e: test_entrypoint_discovery_finds_all_four,test_doql_plugins_module_import,_run_plugin_and_import,test_iso17025_uncertainty_budget_numerical,test_iso17025_drift_monitor_detects_stable,test_iso17025_drift_monitor_flags_excessive_drift,test_fleet_ota_canary_advances_on_success,test_gxp_audit_log_hash_is_deterministic
    test_entrypoint_discovery_finds_all_four()
    test_doql_plugins_module_import()
    _run_plugin_and_import(plugin_name;subpath;symbol)
    test_iso17025_uncertainty_budget_numerical()
    test_iso17025_drift_monitor_detects_stable()
    test_iso17025_drift_monitor_flags_excessive_drift()
    test_fleet_ota_canary_advances_on_success()
    test_gxp_audit_log_hash_is_deterministic()
  tests/test_runtime.py:
    e: _free_port,_has_module,test_api_boot_and_health,_check_web_artifacts,_check_mobile_artifacts,_check_desktop_artifacts,_check_infra_artifacts,test_build_produces_expected_targets
    _free_port()
    _has_module(name)
    test_api_boot_and_health(example;tmp_path)
    _check_web_artifacts(web)
    _check_mobile_artifacts(mobile)
    _check_desktop_artifacts(desktop)
    _check_infra_artifacts(infra)
    test_build_produces_expected_targets(example;tmp_path)
  tests/test_workspace.py:
    e: _make_doql_project,TestParseDoql,TestDiscoverLocal,TestProjectMarkers
    TestParseDoql: test_extracts_workflows(0),test_extracts_entities(0),test_extracts_databases(0),test_extracts_interfaces(0)
    TestDiscoverLocal: test_discovers_doql_projects(1),test_extracts_doql_metadata(1),test_respects_max_depth(1),test_excludes_logs_and_venv(1),test_does_not_dive_into_project(1)
    TestProjectMarkers: test_markers_do_not_include_doql_css(0),test_excluded_contains_logs(0)
    _make_doql_project(tmp_path;name;app_name;app_version;workflows;entities;databases;with_taskfile)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('doql', '1.0.35', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 151, 'less').
project_file('doql/__init__.py', 92, 'python').
project_file('doql/adopt/__init__.py', 11, 'python').
project_file('doql/adopt/device_scanner.py', 133, 'python').
project_file('doql/adopt/emitter.py', 19, 'python').
project_file('doql/adopt/scanner/__init__.py', 59, 'python').
project_file('doql/adopt/scanner/databases.py', 63, 'python').
project_file('doql/adopt/scanner/deploy.py', 151, 'python').
project_file('doql/adopt/scanner/entities.py', 186, 'python').
project_file('doql/adopt/scanner/environments.py', 89, 'python').
project_file('doql/adopt/scanner/integrations.py', 27, 'python').
project_file('doql/adopt/scanner/interfaces/__init__.py', 23, 'python').
project_file('doql/adopt/scanner/interfaces/api.py', 147, 'python').
project_file('doql/adopt/scanner/interfaces/cli.py', 57, 'python').
project_file('doql/adopt/scanner/interfaces/desktop.py', 36, 'python').
project_file('doql/adopt/scanner/interfaces/mobile.py', 38, 'python').
project_file('doql/adopt/scanner/interfaces/web.py', 89, 'python').
project_file('doql/adopt/scanner/metadata.py', 107, 'python').
project_file('doql/adopt/scanner/roles.py', 33, 'python').
project_file('doql/adopt/scanner/utils.py', 101, 'python').
project_file('doql/adopt/scanner/workflows.py', 264, 'python').
project_file('doql/adopt/scanner.py', 46, 'python').
project_file('doql/cli/__init__.py', 20, 'python').
project_file('doql/cli/__main__.py', 10, 'python').
project_file('doql/cli/build.py', 392, 'python').
project_file('doql/cli/commands/__init__.py', 56, 'python').
project_file('doql/cli/commands/adopt.py', 288, 'python').
project_file('doql/cli/commands/deploy.py', 143, 'python').
project_file('doql/cli/commands/docs.py', 22, 'python').
project_file('doql/cli/commands/doctor/__init__.py', 79, 'python').
project_file('doql/cli/commands/doctor/checks.py', 203, 'python').
project_file('doql/cli/commands/doctor/fixes.py', 51, 'python').
project_file('doql/cli/commands/doctor/remote.py', 68, 'python').
project_file('doql/cli/commands/doctor/report.py', 45, 'python').
project_file('doql/cli/commands/drift/__init__.py', 98, 'python').
project_file('doql/cli/commands/drift/export.py', 36, 'python').
project_file('doql/cli/commands/drift/render.py', 108, 'python').
project_file('doql/cli/commands/export.py', 59, 'python').
project_file('doql/cli/commands/generate.py', 35, 'python').
project_file('doql/cli/commands/import_cmd.py', 46, 'python').
project_file('doql/cli/commands/init.py', 44, 'python').
project_file('doql/cli/commands/kiosk.py', 21, 'python').
project_file('doql/cli/commands/plan.py', 116, 'python').
project_file('doql/cli/commands/publish.py', 183, 'python').
project_file('doql/cli/commands/quadlet.py', 113, 'python').
project_file('doql/cli/commands/query.py', 32, 'python').
project_file('doql/cli/commands/render.py', 27, 'python').
project_file('doql/cli/commands/run.py', 167, 'python').
project_file('doql/cli/commands/validate.py', 49, 'python').
project_file('doql/cli/commands/workspace/__init__.py', 105, 'python').
project_file('doql/cli/commands/workspace/analyze.py', 208, 'python').
project_file('doql/cli/commands/workspace/discovery.py', 114, 'python').
project_file('doql/cli/commands/workspace/list.py', 64, 'python').
project_file('doql/cli/commands/workspace/output.py', 37, 'python').
project_file('doql/cli/commands/workspace/run.py', 88, 'python').
project_file('doql/cli/context.py', 67, 'python').
project_file('doql/cli/lockfile.py', 84, 'python').
project_file('doql/cli/main.py', 199, 'python').
project_file('doql/cli/sync.py', 123, 'python').
project_file('doql/cli.py', 63, 'python').
project_file('doql/drift/__init__.py', 23, 'python').
project_file('doql/drift/detector.py', 126, 'python').
project_file('doql/exporters/__init__.py', 2, 'python').
project_file('doql/exporters/css/__init__.py', 114, 'python').
project_file('doql/exporters/css/format_convert.py', 68, 'python').
project_file('doql/exporters/css/helpers.py', 40, 'python').
project_file('doql/exporters/css/renderers.py', 368, 'python').
project_file('doql/exporters/css_exporter.py', 17, 'python').
project_file('doql/exporters/markdown/__init__.py', 41, 'python').
project_file('doql/exporters/markdown/sections.py', 122, 'python').
project_file('doql/exporters/markdown/writers.py', 102, 'python').
project_file('doql/exporters/markdown_exporter.py', 13, 'python').
project_file('doql/exporters/yaml_exporter.py', 37, 'python').
project_file('doql/generators/__init__.py', 6, 'python').
project_file('doql/generators/api_gen/__init__.py', 179, 'python').
project_file('doql/generators/api_gen/alembic.py', 153, 'python').
project_file('doql/generators/api_gen/auth.py', 155, 'python').
project_file('doql/generators/api_gen/common.py', 85, 'python').
project_file('doql/generators/api_gen/database.py', 42, 'python').
project_file('doql/generators/api_gen/main.py', 75, 'python').
project_file('doql/generators/api_gen/models.py', 83, 'python').
project_file('doql/generators/api_gen/routes.py', 116, 'python').
project_file('doql/generators/api_gen/schemas.py', 84, 'python').
project_file('doql/generators/api_gen.py', 26, 'python').
project_file('doql/generators/ci_gen.py', 242, 'python').
project_file('doql/generators/deploy.py', 21, 'python').
project_file('doql/generators/desktop_gen.py', 210, 'python').
project_file('doql/generators/docs_gen.py', 25, 'python').
project_file('doql/generators/document_gen.py', 183, 'python').
project_file('doql/generators/export_postman.py', 26, 'python').
project_file('doql/generators/export_ts_sdk.py', 27, 'python').
project_file('doql/generators/i18n_gen.py', 169, 'python').
project_file('doql/generators/infra_gen/__init__.py', 81, 'python').
project_file('doql/generators/infra_gen/docker.py', 104, 'python').
project_file('doql/generators/infra_gen/kiosk.py', 102, 'python').
project_file('doql/generators/infra_gen/kubernetes.py', 120, 'python').
project_file('doql/generators/infra_gen/migration.py', 74, 'python').
project_file('doql/generators/infra_gen/nginx.py', 55, 'python').
project_file('doql/generators/infra_gen/quadlet.py', 82, 'python').
project_file('doql/generators/infra_gen/terraform.py', 69, 'python').
project_file('doql/generators/integrations_gen.py', 337, 'python').
project_file('doql/generators/mobile_gen.py', 459, 'python').
project_file('doql/generators/report_gen.py', 143, 'python').
project_file('doql/generators/utils/codegen.py', 68, 'python').
project_file('doql/generators/vite_gen.py', 122, 'python').
project_file('doql/generators/web_gen/__init__.py', 201, 'python').
project_file('doql/generators/web_gen/common.py', 10, 'python').
project_file('doql/generators/web_gen/components.py', 77, 'python').
project_file('doql/generators/web_gen/config.py', 123, 'python').
project_file('doql/generators/web_gen/core.py', 58, 'python').
project_file('doql/generators/web_gen/pages.py', 167, 'python').
project_file('doql/generators/web_gen/pwa.py', 110, 'python').
project_file('doql/generators/web_gen/router.py', 44, 'python').
project_file('doql/generators/web_gen.py', 35, 'python').
project_file('doql/generators/workflow_gen.py', 319, 'python').
project_file('doql/importers/__init__.py', 2, 'python').
project_file('doql/importers/yaml_importer.py', 268, 'python').
project_file('doql/integrations/__init__.py', 21, 'python').
project_file('doql/integrations/op3_bridge.py', 75, 'python').
project_file('doql/lsp_server/__init__.py', 74, 'python').
project_file('doql/lsp_server/completion.py', 55, 'python').
project_file('doql/lsp_server/definition.py', 43, 'python').
project_file('doql/lsp_server/diagnostics.py', 93, 'python').
project_file('doql/lsp_server/hover.py', 82, 'python').
project_file('doql/lsp_server/symbols.py', 75, 'python').
project_file('doql/lsp_server/utils.py', 42, 'python').
project_file('doql/parser.py', 75, 'python').
project_file('doql/parsers/__init__.py', 155, 'python').
project_file('doql/parsers/blocks.py', 52, 'python').
project_file('doql/parsers/css_mappers/__init__.py', 99, 'python').
project_file('doql/parsers/css_mappers/config.py', 82, 'python').
project_file('doql/parsers/css_mappers/entity.py', 111, 'python').
project_file('doql/parsers/css_mappers/infra.py', 116, 'python').
project_file('doql/parsers/css_mappers/integration.py', 22, 'python').
project_file('doql/parsers/css_mappers/interface.py', 97, 'python').
project_file('doql/parsers/css_mappers/workflow.py', 87, 'python').
project_file('doql/parsers/css_parser.py', 138, 'python').
project_file('doql/parsers/css_tokenizer.py', 130, 'python').
project_file('doql/parsers/css_transformers/__init__.py', 31, 'python').
project_file('doql/parsers/css_transformers/indent.py', 58, 'python').
project_file('doql/parsers/css_transformers/mixins.py', 45, 'python').
project_file('doql/parsers/css_transformers/selectors.py', 88, 'python').
project_file('doql/parsers/css_transformers/variables.py', 46, 'python').
project_file('doql/parsers/css_utils.py', 75, 'python').
project_file('doql/parsers/extractors.py', 206, 'python').
project_file('doql/parsers/models.py', 270, 'python').
project_file('doql/parsers/registry.py', 332, 'python').
project_file('doql/parsers/validators.py', 201, 'python').
project_file('doql/plugins.py', 102, 'python').
project_file('doql/utils/__init__.py', 7, 'python').
project_file('doql/utils/clean.py', 21, 'python').
project_file('doql/utils/naming.py', 55, 'python').
project_file('doql.sh', 196, 'shell').
project_file('examples/app.doql.less', 60, 'less').
project_file('examples/asset-management/app.doql.css', 229, 'css').
project_file('examples/asset-management/app.doql.less', 235, 'less').
project_file('examples/asset-management.doql.css', 531, 'css').
project_file('examples/blog-cms/app.doql.less', 146, 'less').
project_file('examples/blog-cms.doql.css', 138, 'css').
project_file('examples/calibration-lab/app.doql.less', 318, 'less').
project_file('examples/calibration-lab.doql.css', 174, 'css').
project_file('examples/crm-contacts/app.doql.less', 171, 'less').
project_file('examples/crm-contacts.doql.css', 125, 'css').
project_file('examples/document-generator/app.doql.less', 321, 'less').
project_file('examples/document-generator.doql.css', 107, 'css').
project_file('examples/e-commerce-shop/app.doql.less', 130, 'less').
project_file('examples/e-commerce-shop.doql.css', 177, 'css').
project_file('examples/iot-fleet/app.doql.less', 329, 'less').
project_file('examples/iot-fleet.doql.css', 166, 'css').
project_file('examples/kiosk-station/app.doql.css', 75, 'css').
project_file('examples/kiosk-station/app.doql.less', 73, 'less').
project_file('examples/kiosk-station.doql.css', 384, 'css').
project_file('examples/notes-app.doql.css', 71, 'css').
project_file('examples/todo-pwa/app.doql.css', 27, 'css').
project_file('examples/todo-pwa/app.doql.less', 29, 'less').
project_file('examples/todo-pwa.doql.css', 37, 'css').
project_file('playground/app.js', 213, 'javascript').
project_file('playground/doql_build.py', 141, 'python').
project_file('playground/pyodide-bridge.js', 147, 'javascript').
project_file('playground/renderers.js', 94, 'javascript').
project_file('playground/serve.sh', 16, 'shell').
project_file('playground/style.css', 238, 'css').
project_file('plugins/doql-plugin-erp/app.doql.less', 60, 'less').
project_file('plugins/doql-plugin-erp/doql_plugin_erp/__init__.py', 358, 'python').
project_file('plugins/doql-plugin-fleet/app.doql.less', 60, 'less').
project_file('plugins/doql-plugin-fleet/doql_plugin_fleet/__init__.py', 85, 'python').
project_file('plugins/doql-plugin-fleet/doql_plugin_fleet/device_registry.py', 131, 'python').
project_file('plugins/doql-plugin-fleet/doql_plugin_fleet/metrics.py', 101, 'python').
project_file('plugins/doql-plugin-fleet/doql_plugin_fleet/migration.py', 82, 'python').
project_file('plugins/doql-plugin-fleet/doql_plugin_fleet/ota.py', 73, 'python').
project_file('plugins/doql-plugin-fleet/doql_plugin_fleet/tenant.py', 84, 'python').
project_file('plugins/doql-plugin-gxp/app.doql.less', 60, 'less').
project_file('plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py', 428, 'python').
project_file('plugins/doql-plugin-iso17025/app.doql.less', 60, 'less').
project_file('plugins/doql-plugin-iso17025/doql_plugin_iso17025/__init__.py', 40, 'python').
project_file('plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py', 136, 'python').
project_file('plugins/doql-plugin-iso17025/doql_plugin_iso17025/drift_monitor.py', 79, 'python').
project_file('plugins/doql-plugin-iso17025/doql_plugin_iso17025/migration.py', 75, 'python').
project_file('plugins/doql-plugin-iso17025/doql_plugin_iso17025/traceability.py', 94, 'python').
project_file('plugins/doql-plugin-iso17025/doql_plugin_iso17025/uncertainty.py', 127, 'python').
project_file('plugins/doql-plugin-shared/app.doql.less', 60, 'less').
project_file('plugins/doql-plugin-shared/doql_plugin_shared/__init__.py', 12, 'python').
project_file('plugins/doql-plugin-shared/doql_plugin_shared/base.py', 30, 'python').
project_file('plugins/doql-plugin-shared/doql_plugin_shared/readme.py', 38, 'python').
project_file('project.sh', 49, 'shell').
project_file('tests/__init__.py', 1, 'python').
project_file('tests/env_manager.py', 500, 'python').
project_file('tests/integration/__init__.py', 2, 'python').
project_file('tests/integration/test_adopt_from_device.py', 356, 'python').
project_file('tests/integration/test_build_from_device.py', 283, 'python').
project_file('tests/integration/test_drift.py', 290, 'python').
project_file('tests/integration/test_op3_bridge.py', 165, 'python').
project_file('tests/playground_e2e.py', 124, 'python').
project_file('tests/runtime_all_examples.sh', 116, 'shell').
project_file('tests/runtime_deploy.sh', 66, 'shell').
project_file('tests/runtime_smoke.py', 92, 'python').
project_file('tests/test_adopt.py', 489, 'python').
project_file('tests/test_css_parser.py', 326, 'python').
project_file('tests/test_deploy.py', 363, 'python').
project_file('tests/test_exporters.py', 437, 'python').
project_file('tests/test_exporters_shims.py', 93, 'python').
project_file('tests/test_generators.py', 122, 'python').
project_file('tests/test_lsp.py', 60, 'python').
project_file('tests/test_parser.py', 207, 'python').
project_file('tests/test_parser_benchmark.py', 217, 'python').
project_file('tests/test_plugins.py', 119, 'python').
project_file('tests/test_runtime.py', 245, 'python').
project_file('tests/test_workspace.py', 170, 'python').
project_file('tree.sh', 2, 'shell').
project_file('vscode-doql/app.doql.less', 75, 'less').
project_file('vscode-doql/src/extension.ts', 52, 'typescript').
project_file('vscode-doql/test/vscode-doql.test.js', 8, 'javascript').

% ── Python Functions ─────────────────────────────────────
python_function('doql/adopt/device_scanner.py', '_header', 3, 1, 2).
python_function('doql/adopt/device_scanner.py', 'adopt_from_device_to_snapshot', 1, 2, 5).
python_function('doql/adopt/device_scanner.py', 'adopt_from_device', 1, 4, 6).
python_function('doql/adopt/emitter.py', 'emit_css', 2, 1, 1).
python_function('doql/adopt/emitter.py', 'emit_spec', 3, 1, 2).
python_function('doql/adopt/scanner/__init__.py', 'scan_project', 1, 1, 12).
python_function('doql/adopt/scanner/databases.py', '_db_name', 2, 2, 1).
python_function('doql/adopt/scanner/databases.py', '_db_from_image', 2, 3, 2).
python_function('doql/adopt/scanner/databases.py', '_scan_compose_databases', 2, 5, 6).
python_function('doql/adopt/scanner/databases.py', 'scan_databases', 2, 6, 5).
python_function('doql/adopt/scanner/deploy.py', '_detect_deployment_indicators', 1, 10, 9).
python_function('doql/adopt/scanner/deploy.py', '_determine_deploy_target', 3, 8, 3).
python_function('doql/adopt/scanner/deploy.py', '_apply_deploy_config_flags', 2, 3, 0).
python_function('doql/adopt/scanner/deploy.py', '_is_database_service', 1, 2, 1).
python_function('doql/adopt/scanner/deploy.py', '_extract_container_config', 2, 5, 2).
python_function('doql/adopt/scanner/deploy.py', '_extract_containers_from_compose', 2, 5, 6).
python_function('doql/adopt/scanner/deploy.py', '_detect_rootless', 1, 2, 2).
python_function('doql/adopt/scanner/deploy.py', '_emit_infrastructure_blocks', 2, 4, 3).
python_function('doql/adopt/scanner/deploy.py', 'scan_deploy', 2, 5, 7).
python_function('doql/adopt/scanner/entities.py', '_is_dto_name', 1, 2, 2).
python_function('doql/adopt/scanner/entities.py', '_is_excluded_path', 1, 2, 2).
python_function('doql/adopt/scanner/entities.py', 'scan_entities', 2, 6, 7).
python_function('doql/adopt/scanner/entities.py', '_classify_bases', 1, 3, 4).
python_function('doql/adopt/scanner/entities.py', '_extract_entities_from_python', 3, 9, 11).
python_function('doql/adopt/scanner/entities.py', '_extract_annotation_fields', 2, 5, 6).
python_function('doql/adopt/scanner/entities.py', '_extract_sqlalchemy_fields', 2, 3, 6).
python_function('doql/adopt/scanner/entities.py', '_extract_fields', 3, 8, 7).
python_function('doql/adopt/scanner/entities.py', '_is_reserved_sql_keyword', 1, 1, 1).
python_function('doql/adopt/scanner/entities.py', '_extract_sql_columns', 1, 3, 6).
python_function('doql/adopt/scanner/entities.py', '_extract_entities_from_sql', 3, 5, 8).
python_function('doql/adopt/scanner/environments.py', '_detect_local_env', 2, 4, 4).
python_function('doql/adopt/scanner/environments.py', '_extract_env_refs', 2, 7, 6).
python_function('doql/adopt/scanner/environments.py', '_detect_env_files', 2, 4, 6).
python_function('doql/adopt/scanner/environments.py', '_assign_ssh_host', 3, 4, 1).
python_function('doql/adopt/scanner/environments.py', '_detect_compose_envs', 2, 7, 3).
python_function('doql/adopt/scanner/environments.py', 'scan_environments', 2, 1, 3).
python_function('doql/adopt/scanner/integrations.py', 'scan_integrations', 2, 4, 5).
python_function('doql/adopt/scanner/interfaces/__init__.py', 'scan_interfaces', 2, 1, 5).
python_function('doql/adopt/scanner/interfaces/api.py', '_detect_framework_from_pyproject', 1, 5, 3).
python_function('doql/adopt/scanner/interfaces/api.py', '_detect_framework_from_main_py', 1, 6, 2).
python_function('doql/adopt/scanner/interfaces/api.py', '_detect_framework_from_any_py', 1, 8, 4).
python_function('doql/adopt/scanner/interfaces/api.py', '_find_api_main_file', 1, 8, 5).
python_function('doql/adopt/scanner/interfaces/api.py', '_has_api_entry_point', 1, 7, 5).
python_function('doql/adopt/scanner/interfaces/api.py', '_detect_api_auth', 1, 4, 1).
python_function('doql/adopt/scanner/interfaces/api.py', '_detect_api_port', 1, 5, 1).
python_function('doql/adopt/scanner/interfaces/api.py', 'scan_python_api', 2, 9, 9).
python_function('doql/adopt/scanner/interfaces/cli.py', 'scan_python_cli', 2, 14, 12).
python_function('doql/adopt/scanner/interfaces/desktop.py', 'scan_desktop', 2, 7, 7).
python_function('doql/adopt/scanner/interfaces/mobile.py', 'scan_mobile', 2, 6, 7).
python_function('doql/adopt/scanner/interfaces/web.py', '_detect_web_framework', 1, 11, 5).
python_function('doql/adopt/scanner/interfaces/web.py', '_scan_pages_dir', 2, 9, 10).
python_function('doql/adopt/scanner/interfaces/web.py', '_extract_web_pages', 1, 3, 3).
python_function('doql/adopt/scanner/interfaces/web.py', 'scan_web_frontend', 2, 6, 5).
python_function('doql/adopt/scanner/metadata.py', 'scan_metadata', 2, 6, 6).
python_function('doql/adopt/scanner/metadata.py', '_extract_authors', 2, 6, 2).
python_function('doql/adopt/scanner/metadata.py', '_extract_keywords', 2, 3, 2).
python_function('doql/adopt/scanner/metadata.py', '_extract_urls', 2, 1, 1).
python_function('doql/adopt/scanner/metadata.py', '_extract_dependencies', 2, 3, 2).
python_function('doql/adopt/scanner/metadata.py', '_parse_pyproject', 2, 3, 8).
python_function('doql/adopt/scanner/metadata.py', '_parse_package_json', 2, 1, 3).
python_function('doql/adopt/scanner/metadata.py', '_parse_goal_yaml', 2, 4, 2).
python_function('doql/adopt/scanner/roles.py', '_scan_sql_roles', 2, 9, 9).
python_function('doql/adopt/scanner/roles.py', 'scan_roles', 2, 3, 5).
python_function('doql/adopt/scanner/utils.py', 'load_yaml', 1, 3, 2).
python_function('doql/adopt/scanner/utils.py', 'find_compose', 1, 3, 1).
python_function('doql/adopt/scanner/utils.py', 'find_dockerfiles', 1, 5, 3).
python_function('doql/adopt/scanner/utils.py', 'camel_to_kebab', 1, 1, 3).
python_function('doql/adopt/scanner/utils.py', 'snake_to_pascal', 1, 2, 3).
python_function('doql/adopt/scanner/utils.py', 'normalize_python_type', 1, 1, 3).
python_function('doql/adopt/scanner/utils.py', 'normalize_sqlalchemy_type', 1, 1, 2).
python_function('doql/adopt/scanner/utils.py', 'normalize_sql_type', 1, 4, 3).
python_function('doql/adopt/scanner/workflows.py', 'scan_workflows', 2, 4, 4).
python_function('doql/adopt/scanner/workflows.py', '_is_valid_target', 3, 5, 3).
python_function('doql/adopt/scanner/workflows.py', '_build_steps_from_body', 2, 7, 6).
python_function('doql/adopt/scanner/workflows.py', '_create_workflow', 2, 2, 1).
python_function('doql/adopt/scanner/workflows.py', '_extract_makefile_workflows', 2, 6, 8).
python_function('doql/adopt/scanner/workflows.py', '_parse_makefile_deps', 1, 4, 2).
python_function('doql/adopt/scanner/workflows.py', '_build_taskfile_steps', 1, 5, 5).
python_function('doql/adopt/scanner/workflows.py', '_extract_taskfile_schedule', 1, 2, 2).
python_function('doql/adopt/scanner/workflows.py', '_build_workflow_from_task', 2, 4, 4).
python_function('doql/adopt/scanner/workflows.py', '_extract_taskfile_workflows', 2, 9, 8).
python_function('doql/adopt/scanner/workflows.py', '_find_cli_candidates', 1, 9, 10).
python_function('doql/adopt/scanner/workflows.py', '_detect_cli_command_name', 1, 6, 5).
python_function('doql/adopt/scanner/workflows.py', '_build_workflow_steps', 2, 2, 2).
python_function('doql/adopt/scanner/workflows.py', '_scan_cli_file_for_workflows', 4, 7, 8).
python_function('doql/adopt/scanner/workflows.py', '_extract_python_cli_workflows', 2, 3, 3).
python_function('doql/cli/build.py', '_watch_files', 2, 15, 15).
python_function('doql/cli/build.py', 'should_generate_interface', 2, 3, 1).
python_function('doql/cli/build.py', 'run_core_generators', 4, 4, 5).
python_function('doql/cli/build.py', 'run_document_generators', 3, 2, 3).
python_function('doql/cli/build.py', '_run_conditional_generator', 7, 2, 3).
python_function('doql/cli/build.py', 'run_report_generators', 3, 1, 1).
python_function('doql/cli/build.py', 'run_i18n_generators', 3, 1, 1).
python_function('doql/cli/build.py', 'run_integration_generators', 3, 3, 2).
python_function('doql/cli/build.py', 'run_workflow_generators', 3, 1, 1).
python_function('doql/cli/build.py', 'run_ci_generator', 3, 1, 2).
python_function('doql/cli/build.py', 'run_vite_generator', 3, 4, 5).
python_function('doql/cli/build.py', 'run_plugins', 3, 1, 1).
python_function('doql/cli/build.py', '_scan_device_for_build', 2, 9, 9).
python_function('doql/cli/build.py', '_do_build', 2, 9, 20).
python_function('doql/cli/build.py', 'cmd_build', 1, 8, 9).
python_function('doql/cli/build.py', '_merge_no_overwrite', 2, 4, 6).
python_function('doql/cli/commands/adopt.py', '_print_item', 4, 5, 3).
python_function('doql/cli/commands/adopt.py', '_print_scan_summary', 1, 7, 3).
python_function('doql/cli/commands/adopt.py', '_cleanup_empty_output', 1, 4, 3).
python_function('doql/cli/commands/adopt.py', '_validate_output_written', 1, 3, 3).
python_function('doql/cli/commands/adopt.py', 'cmd_adopt', 1, 3, 4).
python_function('doql/cli/commands/adopt.py', '_discover_subprojects', 1, 7, 7).
python_function('doql/cli/commands/adopt.py', '_scan_and_emit_subproject', 5, 5, 9).
python_function('doql/cli/commands/adopt.py', '_write_root_manifest', 5, 6, 6).
python_function('doql/cli/commands/adopt.py', '_cmd_adopt_recursive', 1, 7, 13).
python_function('doql/cli/commands/adopt.py', '_cmd_adopt_from_directory', 1, 8, 11).
python_function('doql/cli/commands/adopt.py', '_cmd_adopt_from_device', 2, 10, 10).
python_function('doql/cli/commands/deploy.py', '_run_directive', 2, 1, 2).
python_function('doql/cli/commands/deploy.py', '_deploy_via_redeploy_api', 3, 12, 14).
python_function('doql/cli/commands/deploy.py', '_deploy_via_redeploy_cli', 3, 4, 6).
python_function('doql/cli/commands/deploy.py', 'cmd_deploy', 1, 9, 10).
python_function('doql/cli/commands/docs.py', 'cmd_docs', 1, 3, 6).
python_function('doql/cli/commands/doctor/__init__.py', 'cmd_doctor', 1, 7, 17).
python_function('doql/cli/commands/doctor/checks.py', '_check_parse', 3, 4, 3).
python_function('doql/cli/commands/doctor/checks.py', '_find_missing_env_refs', 2, 7, 4).
python_function('doql/cli/commands/doctor/checks.py', '_check_env', 3, 5, 6).
python_function('doql/cli/commands/doctor/checks.py', '_collect_missing_files', 2, 11, 4).
python_function('doql/cli/commands/doctor/checks.py', '_check_files', 3, 3, 2).
python_function('doql/cli/commands/doctor/checks.py', '_check_databases', 2, 5, 1).
python_function('doql/cli/commands/doctor/checks.py', '_warn_unknown_entity_refs', 3, 3, 1).
python_function('doql/cli/commands/doctor/checks.py', '_check_interfaces', 2, 10, 4).
python_function('doql/cli/commands/doctor/checks.py', '_collect_required_tools', 1, 8, 1).
python_function('doql/cli/commands/doctor/checks.py', '_check_tools', 2, 4, 4).
python_function('doql/cli/commands/doctor/checks.py', '_check_deploy', 3, 6, 3).
python_function('doql/cli/commands/doctor/checks.py', '_check_environments', 2, 5, 3).
python_function('doql/cli/commands/doctor/fixes.py', '_apply_fixes', 3, 11, 5).
python_function('doql/cli/commands/doctor/remote.py', '_ssh_run', 2, 3, 3).
python_function('doql/cli/commands/doctor/remote.py', '_check_remote_ssh', 2, 3, 2).
python_function('doql/cli/commands/doctor/remote.py', '_check_remote_runtime', 3, 4, 2).
python_function('doql/cli/commands/doctor/remote.py', '_check_remote', 3, 8, 5).
python_function('doql/cli/commands/doctor/report.py', '_print_report', 1, 3, 2).
python_function('doql/cli/commands/drift/__init__.py', 'cmd_drift', 1, 13, 14).
python_function('doql/cli/commands/drift/export.py', '_report_to_json', 3, 2, 1).
python_function('doql/cli/commands/drift/render.py', '_change_style', 1, 1, 1).
python_function('doql/cli/commands/drift/render.py', '_render_rich', 3, 7, 13).
python_function('doql/cli/commands/drift/render.py', '_render_plain', 3, 3, 3).
python_function('doql/cli/commands/drift/render.py', '_fmt_value', 1, 6, 5).
python_function('doql/cli/commands/export.py', 'cmd_export', 1, 7, 10).
python_function('doql/cli/commands/generate.py', 'cmd_generate', 1, 9, 6).
python_function('doql/cli/commands/import_cmd.py', 'cmd_import', 1, 7, 9).
python_function('doql/cli/commands/init.py', 'cmd_init', 1, 8, 11).
python_function('doql/cli/commands/kiosk.py', 'cmd_kiosk', 1, 2, 1).
python_function('doql/cli/commands/plan.py', '_print_header', 1, 3, 1).
python_function('doql/cli/commands/plan.py', '_print_entities', 1, 2, 2).
python_function('doql/cli/commands/plan.py', '_print_data_sources', 1, 3, 2).
python_function('doql/cli/commands/plan.py', '_print_documents', 1, 2, 2).
python_function('doql/cli/commands/plan.py', '_print_api_clients', 1, 3, 2).
python_function('doql/cli/commands/plan.py', '_print_interfaces', 1, 4, 1).
python_function('doql/cli/commands/plan.py', '_print_workflows', 1, 4, 2).
python_function('doql/cli/commands/plan.py', '_print_summary', 1, 4, 2).
python_function('doql/cli/commands/plan.py', '_print_file_counts', 1, 2, 3).
python_function('doql/cli/commands/plan.py', 'cmd_plan', 1, 3, 13).
python_function('doql/cli/commands/publish.py', '_publish_pypi', 2, 7, 5).
python_function('doql/cli/commands/publish.py', '_publish_npm', 2, 6, 5).
python_function('doql/cli/commands/publish.py', '_publish_docker', 3, 7, 7).
python_function('doql/cli/commands/publish.py', '_extract_changelog_notes', 2, 7, 5).
python_function('doql/cli/commands/publish.py', '_publish_github', 3, 4, 4).
python_function('doql/cli/commands/publish.py', 'cmd_publish', 1, 8, 13).
python_function('doql/cli/commands/quadlet.py', '_install_via_redeploy_api', 3, 9, 11).
python_function('doql/cli/commands/quadlet.py', '_install_via_systemctl', 3, 8, 8).
python_function('doql/cli/commands/quadlet.py', 'cmd_quadlet', 1, 6, 9).
python_function('doql/cli/commands/query.py', 'cmd_query', 1, 7, 6).
python_function('doql/cli/commands/render.py', 'cmd_render', 1, 4, 5).
python_function('doql/cli/commands/run.py', '_build_into', 2, 6, 13).
python_function('doql/cli/commands/run.py', '_workspace_for_file', 1, 1, 0).
python_function('doql/cli/commands/run.py', 'cmd_run', 1, 9, 12).
python_function('doql/cli/commands/run.py', '_run_api', 2, 3, 4).
python_function('doql/cli/commands/run.py', '_run_web', 2, 3, 4).
python_function('doql/cli/commands/run.py', '_run_desktop', 1, 2, 3).
python_function('doql/cli/commands/run.py', '_run_target', 3, 7, 7).
python_function('doql/cli/commands/validate.py', '_print_issues', 1, 8, 2).
python_function('doql/cli/commands/validate.py', 'cmd_validate', 1, 5, 9).
python_function('doql/cli/commands/workspace/__init__.py', 'cmd_workspace', 1, 3, 4).
python_function('doql/cli/commands/workspace/__init__.py', 'register_parser', 1, 1, 5).
python_function('doql/cli/commands/workspace/analyze.py', '_analyze_workflow_issues', 1, 4, 3).
python_function('doql/cli/commands/workspace/analyze.py', '_analyze_content_issues', 1, 2, 1).
python_function('doql/cli/commands/workspace/analyze.py', '_analyze_content_recs', 2, 4, 1).
python_function('doql/cli/commands/workspace/analyze.py', '_analyze_project', 1, 3, 8).
python_function('doql/cli/commands/workspace/analyze.py', '_output_csv', 2, 2, 8).
python_function('doql/cli/commands/workspace/analyze.py', '_output_table', 1, 10, 8).
python_function('doql/cli/commands/workspace/analyze.py', '_cmd_analyze', 1, 4, 9).
python_function('doql/cli/commands/workspace/analyze.py', '_cmd_validate', 1, 6, 9).
python_function('doql/cli/commands/workspace/analyze.py', '_cmd_fix', 1, 7, 11).
python_function('doql/cli/commands/workspace/discovery.py', '_is_project', 1, 2, 2).
python_function('doql/cli/commands/workspace/discovery.py', '_parse_doql', 1, 3, 2).
python_function('doql/cli/commands/workspace/discovery.py', '_load_project_doql', 1, 4, 4).
python_function('doql/cli/commands/workspace/discovery.py', '_walk_projects', 4, 10, 10).
python_function('doql/cli/commands/workspace/discovery.py', '_discover_local', 2, 1, 4).
python_function('doql/cli/commands/workspace/discovery.py', '_filter_projects', 3, 7, 0).
python_function('doql/cli/commands/workspace/list.py', '_print_project_table', 2, 5, 7).
python_function('doql/cli/commands/workspace/list.py', '_cmd_list', 1, 5, 10).
python_function('doql/cli/commands/workspace/output.py', '_print', 1, 2, 2).
python_function('doql/cli/commands/workspace/run.py', '_select_run_projects', 3, 6, 3).
python_function('doql/cli/commands/workspace/run.py', '_execute_single_project', 5, 5, 5).
python_function('doql/cli/commands/workspace/run.py', '_print_dry_run_commands', 2, 2, 1).
python_function('doql/cli/commands/workspace/run.py', '_print_run_summary', 2, 2, 1).
python_function('doql/cli/commands/workspace/run.py', '_cmd_run', 1, 6, 10).
python_function('doql/cli/context.py', 'build_context', 1, 3, 5).
python_function('doql/cli/context.py', 'load_spec', 1, 1, 2).
python_function('doql/cli/context.py', 'scaffold_from_template', 2, 2, 4).
python_function('doql/cli/context.py', 'estimate_file_count', 1, 5, 1).
python_function('doql/cli/lockfile.py', '_simple_items_hash', 4, 2, 2).
python_function('doql/cli/lockfile.py', 'spec_section_hashes', 2, 9, 10).
python_function('doql/cli/lockfile.py', 'read_lockfile', 1, 3, 3).
python_function('doql/cli/lockfile.py', 'diff_sections', 2, 8, 0).
python_function('doql/cli/lockfile.py', 'write_lockfile', 2, 1, 5).
python_function('doql/cli/main.py', 'create_parser', 0, 1, 6).
python_function('doql/cli/main.py', 'main', 0, 1, 3).
python_function('doql/cli/sync.py', 'determine_regeneration_set', 2, 10, 6).
python_function('doql/cli/sync.py', '_run_interface_generators', 4, 5, 3).
python_function('doql/cli/sync.py', 'run_generators', 4, 5, 5).
python_function('doql/cli/sync.py', 'cmd_sync', 1, 6, 13).
python_function('doql/drift/detector.py', 'find_intended_file', 1, 4, 2).
python_function('doql/drift/detector.py', '_has_unsupported_intended', 1, 3, 1).
python_function('doql/drift/detector.py', 'parse_intended', 1, 3, 9).
python_function('doql/drift/detector.py', 'detect_drift', 1, 3, 8).
python_function('doql/exporters/css/__init__.py', '_render_data_layer', 1, 4, 4).
python_function('doql/exporters/css/__init__.py', '_render_documentation_layer', 1, 3, 3).
python_function('doql/exporters/css/__init__.py', '_render_infrastructure_layer', 1, 4, 4).
python_function('doql/exporters/css/__init__.py', '_render_integration_layer', 1, 5, 5).
python_function('doql/exporters/css/__init__.py', '_render_css', 1, 7, 12).
python_function('doql/exporters/css/__init__.py', 'export_css', 2, 1, 2).
python_function('doql/exporters/css/__init__.py', 'export_less', 2, 1, 3).
python_function('doql/exporters/css/__init__.py', 'export_sass', 2, 1, 3).
python_function('doql/exporters/css/__init__.py', 'export_css_file', 3, 1, 3).
python_function('doql/exporters/css/format_convert.py', '_unquote_simple_value', 2, 8, 3).
python_function('doql/exporters/css/format_convert.py', '_css_to_less', 1, 4, 7).
python_function('doql/exporters/css/format_convert.py', '_css_to_sass', 1, 9, 7).
python_function('doql/exporters/css/helpers.py', '_indent', 2, 2, 1).
python_function('doql/exporters/css/helpers.py', '_prop', 3, 8, 3).
python_function('doql/exporters/css/helpers.py', '_field_line', 1, 7, 2).
python_function('doql/exporters/css/renderers.py', '_render_app', 1, 9, 4).
python_function('doql/exporters/css/renderers.py', '_render_dependencies', 1, 3, 4).
python_function('doql/exporters/css/renderers.py', '_render_entity', 1, 4, 5).
python_function('doql/exporters/css/renderers.py', '_render_data_source', 1, 9, 3).
python_function('doql/exporters/css/renderers.py', '_render_template', 1, 4, 4).
python_function('doql/exporters/css/renderers.py', '_render_document', 1, 7, 4).
python_function('doql/exporters/css/renderers.py', '_render_report', 1, 6, 4).
python_function('doql/exporters/css/renderers.py', '_render_database', 1, 5, 3).
python_function('doql/exporters/css/renderers.py', '_render_api_client', 1, 8, 4).
python_function('doql/exporters/css/renderers.py', '_render_webhook', 1, 5, 3).
python_function('doql/exporters/css/renderers.py', '_build_interface_props', 1, 10, 4).
python_function('doql/exporters/css/renderers.py', '_build_page_props', 1, 6, 4).
python_function('doql/exporters/css/renderers.py', '_render_interface', 1, 2, 4).
python_function('doql/exporters/css/renderers.py', '_render_integration', 1, 2, 4).
python_function('doql/exporters/css/renderers.py', '_render_workflow', 1, 9, 7).
python_function('doql/exporters/css/renderers.py', '_render_role', 1, 2, 2).
python_function('doql/exporters/css/renderers.py', '_render_deploy', 1, 5, 4).
python_function('doql/exporters/css/renderers.py', '_render_environment', 1, 5, 4).
python_function('doql/exporters/css/renderers.py', '_render_project', 1, 10, 6).
python_function('doql/exporters/markdown/__init__.py', 'export_markdown', 2, 1, 10).
python_function('doql/exporters/markdown/__init__.py', 'export_markdown_file', 2, 1, 2).
python_function('doql/exporters/markdown/sections.py', '_h', 2, 1, 0).
python_function('doql/exporters/markdown/sections.py', '_field_type_str', 1, 7, 2).
python_function('doql/exporters/markdown/sections.py', '_entity_section', 1, 5, 4).
python_function('doql/exporters/markdown/sections.py', '_interface_section', 1, 8, 3).
python_function('doql/exporters/markdown/sections.py', '_workflow_section', 1, 9, 5).
python_function('doql/exporters/markdown/sections.py', '_config_section', 3, 3, 3).
python_function('doql/exporters/markdown/sections.py', '_document_section', 1, 1, 1).
python_function('doql/exporters/markdown/sections.py', '_report_section', 1, 1, 1).
python_function('doql/exporters/markdown/writers.py', '_write_header', 2, 3, 3).
python_function('doql/exporters/markdown/writers.py', '_write_data_sources', 2, 5, 2).
python_function('doql/exporters/markdown/writers.py', '_write_section', 5, 3, 4).
python_function('doql/exporters/markdown/writers.py', '_write_entities', 2, 1, 1).
python_function('doql/exporters/markdown/writers.py', '_write_interfaces', 2, 1, 1).
python_function('doql/exporters/markdown/writers.py', '_write_documents', 2, 1, 1).
python_function('doql/exporters/markdown/writers.py', '_write_reports', 2, 1, 1).
python_function('doql/exporters/markdown/writers.py', '_write_workflows', 2, 1, 1).
python_function('doql/exporters/markdown/writers.py', '_write_roles', 2, 5, 2).
python_function('doql/exporters/markdown/writers.py', '_write_integrations', 2, 3, 2).
python_function('doql/exporters/markdown/writers.py', '_write_deployment', 2, 4, 2).
python_function('doql/exporters/yaml_exporter.py', 'spec_to_dict', 1, 1, 2).
python_function('doql/exporters/yaml_exporter.py', 'export_yaml', 2, 1, 2).
python_function('doql/exporters/yaml_exporter.py', 'export_yaml_file', 2, 1, 2).
python_function('doql/generators/api_gen/__init__.py', '_write_api_files', 4, 3, 10).
python_function('doql/generators/api_gen/__init__.py', '_write_alembic_files', 2, 1, 6).
python_function('doql/generators/api_gen/__init__.py', '_write_api_readme', 2, 3, 5).
python_function('doql/generators/api_gen/__init__.py', 'generate', 3, 2, 6).
python_function('doql/generators/api_gen/__init__.py', 'export_openapi', 2, 2, 2).
python_function('doql/generators/api_gen/alembic.py', 'gen_alembic_ini', 0, 1, 1).
python_function('doql/generators/api_gen/alembic.py', 'gen_alembic_env', 0, 1, 0).
python_function('doql/generators/api_gen/alembic.py', '_entity_table_columns', 1, 10, 5).
python_function('doql/generators/api_gen/alembic.py', 'gen_initial_migration', 1, 3, 6).
python_function('doql/generators/api_gen/auth.py', 'gen_auth', 1, 7, 5).
python_function('doql/generators/api_gen/common.py', 'sa_type', 1, 1, 1).
python_function('doql/generators/api_gen/common.py', 'py_type', 1, 4, 1).
python_function('doql/generators/api_gen/common.py', 'py_default', 1, 6, 1).
python_function('doql/generators/api_gen/common.py', 'safe_name', 1, 2, 1).
python_function('doql/generators/api_gen/common.py', 'snake', 1, 1, 2).
python_function('doql/generators/api_gen/database.py', 'gen_database', 2, 1, 2).
python_function('doql/generators/api_gen/main.py', 'gen_main', 1, 1, 1).
python_function('doql/generators/api_gen/main.py', 'gen_requirements', 1, 2, 1).
python_function('doql/generators/api_gen/models.py', 'gen_models', 1, 7, 5).
python_function('doql/generators/api_gen/models.py', '_gen_column_def', 2, 10, 6).
python_function('doql/generators/api_gen/routes.py', 'gen_routes', 1, 2, 3).
python_function('doql/generators/api_gen/routes.py', '_gen_entity_routes', 1, 1, 7).
python_function('doql/generators/api_gen/routes.py', '_gen_list_route', 2, 1, 0).
python_function('doql/generators/api_gen/routes.py', '_gen_get_route', 3, 1, 0).
python_function('doql/generators/api_gen/routes.py', '_gen_create_route', 3, 1, 0).
python_function('doql/generators/api_gen/routes.py', '_gen_update_route', 3, 1, 0).
python_function('doql/generators/api_gen/routes.py', '_gen_delete_route', 3, 1, 0).
python_function('doql/generators/api_gen/schemas.py', 'gen_schemas', 1, 2, 3).
python_function('doql/generators/api_gen/schemas.py', '_gen_entity_schemas', 1, 1, 5).
python_function('doql/generators/api_gen/schemas.py', '_gen_create_schema', 1, 6, 4).
python_function('doql/generators/api_gen/schemas.py', '_gen_response_schema', 1, 10, 4).
python_function('doql/generators/api_gen/schemas.py', '_gen_update_schema', 1, 7, 3).
python_function('doql/generators/ci_gen.py', '_gen_github_action', 1, 1, 1).
python_function('doql/generators/ci_gen.py', '_gen_gitlab_ci', 1, 1, 2).
python_function('doql/generators/ci_gen.py', '_gen_jenkinsfile', 1, 1, 1).
python_function('doql/generators/ci_gen.py', 'generate', 3, 7, 6).
python_function('doql/generators/deploy.py', 'run', 2, 2, 4).
python_function('doql/generators/desktop_gen.py', '_make_solid_png', 3, 2, 8).
python_function('doql/generators/desktop_gen.py', '_gen_cargo_toml', 1, 1, 2).
python_function('doql/generators/desktop_gen.py', '_gen_tauri_conf', 1, 1, 2).
python_function('doql/generators/desktop_gen.py', '_gen_main_rs', 1, 1, 1).
python_function('doql/generators/desktop_gen.py', '_gen_build_rs', 0, 1, 1).
python_function('doql/generators/desktop_gen.py', '_gen_package_json', 1, 1, 2).
python_function('doql/generators/desktop_gen.py', 'generate', 3, 6, 12).
python_function('doql/generators/docs_gen.py', 'generate', 2, 3, 5).
python_function('doql/generators/document_gen.py', '_find_template', 2, 3, 0).
python_function('doql/generators/document_gen.py', '_gen_render_script', 2, 2, 1).
python_function('doql/generators/document_gen.py', '_gen_preview_html', 3, 6, 7).
python_function('doql/generators/document_gen.py', 'generate', 4, 5, 5).
python_function('doql/generators/export_postman.py', 'run', 2, 2, 2).
python_function('doql/generators/export_ts_sdk.py', 'run', 2, 2, 2).
python_function('doql/generators/i18n_gen.py', '_humanize', 1, 1, 3).
python_function('doql/generators/i18n_gen.py', '_gen_translations', 2, 6, 4).
python_function('doql/generators/i18n_gen.py', 'generate', 3, 4, 6).
python_function('doql/generators/infra_gen/__init__.py', '_map_deploy_strategy', 1, 1, 1).
python_function('doql/generators/infra_gen/__init__.py', 'generate', 3, 12, 8).
python_function('doql/generators/infra_gen/docker.py', '_gen_docker_compose', 3, 8, 8).
python_function('doql/generators/infra_gen/kiosk.py', '_gen_kiosk', 3, 1, 5).
python_function('doql/generators/infra_gen/kubernetes.py', '_gen_kubernetes', 3, 6, 6).
python_function('doql/generators/infra_gen/migration.py', '_gen_migration_spec', 3, 6, 6).
python_function('doql/generators/infra_gen/nginx.py', '_gen_nginx', 3, 4, 5).
python_function('doql/generators/infra_gen/quadlet.py', '_gen_quadlet', 3, 4, 7).
python_function('doql/generators/infra_gen/terraform.py', '_gen_terraform', 3, 1, 4).
python_function('doql/generators/integrations_gen.py', '_gen_email_service', 0, 1, 1).
python_function('doql/generators/integrations_gen.py', '_gen_slack_service', 0, 1, 1).
python_function('doql/generators/integrations_gen.py', '_gen_storage_service', 0, 1, 1).
python_function('doql/generators/integrations_gen.py', '_gen_notifications', 1, 7, 2).
python_function('doql/generators/integrations_gen.py', '_gen_api_client', 1, 4, 4).
python_function('doql/generators/integrations_gen.py', '_gen_webhook_dispatcher', 1, 5, 3).
python_function('doql/generators/integrations_gen.py', '_setup_services_dir', 1, 1, 2).
python_function('doql/generators/integrations_gen.py', '_generate_integration_services', 3, 8, 7).
python_function('doql/generators/integrations_gen.py', '_generate_api_clients', 3, 2, 3).
python_function('doql/generators/integrations_gen.py', '_generate_webhooks', 3, 2, 3).
python_function('doql/generators/integrations_gen.py', 'generate', 3, 6, 6).
python_function('doql/generators/mobile_gen.py', '_gen_manifest', 1, 1, 2).
python_function('doql/generators/mobile_gen.py', '_gen_service_worker', 1, 1, 2).
python_function('doql/generators/mobile_gen.py', '_gen_index_html', 1, 4, 2).
python_function('doql/generators/mobile_gen.py', '_gen_app_js', 1, 3, 3).
python_function('doql/generators/mobile_gen.py', '_gen_style_css', 0, 1, 1).
python_function('doql/generators/mobile_gen.py', '_gen_icons', 2, 3, 5).
python_function('doql/generators/mobile_gen.py', 'generate', 3, 5, 10).
python_function('doql/generators/report_gen.py', '_gen_report_script', 2, 7, 3).
python_function('doql/generators/report_gen.py', 'generate', 3, 9, 5).
python_function('doql/generators/utils/codegen.py', 'write_code_block', 2, 1, 3).
python_function('doql/generators/utils/codegen.py', 'generate_file_from_template', 3, 2, 5).
python_function('doql/generators/vite_gen.py', '_gen_vite_config', 3, 1, 5).
python_function('doql/generators/vite_gen.py', '_gen_tsconfig', 2, 1, 3).
python_function('doql/generators/vite_gen.py', '_gen_index_html', 2, 1, 4).
python_function('doql/generators/vite_gen.py', 'generate', 3, 1, 3).
python_function('doql/generators/web_gen/__init__.py', '_setup_web_directories', 1, 2, 1).
python_function('doql/generators/web_gen/__init__.py', '_write_config_files', 2, 2, 9).
python_function('doql/generators/web_gen/__init__.py', '_write_core_files', 2, 1, 6).
python_function('doql/generators/web_gen/__init__.py', '_write_component_files', 3, 1, 3).
python_function('doql/generators/web_gen/__init__.py', '_write_page_files', 2, 2, 4).
python_function('doql/generators/web_gen/__init__.py', '_write_pwa_files', 3, 3, 7).
python_function('doql/generators/web_gen/__init__.py', '_write_readme', 3, 3, 3).
python_function('doql/generators/web_gen/__init__.py', 'generate', 3, 6, 10).
python_function('doql/generators/web_gen/components.py', '_gen_layout', 3, 2, 4).
python_function('doql/generators/web_gen/config.py', '_gen_package_json', 1, 1, 2).
python_function('doql/generators/web_gen/config.py', '_gen_vite_config', 0, 1, 1).
python_function('doql/generators/web_gen/config.py', '_gen_tailwind_config', 0, 1, 1).
python_function('doql/generators/web_gen/config.py', '_gen_postcss_config', 0, 1, 1).
python_function('doql/generators/web_gen/config.py', '_gen_tsconfig', 0, 1, 1).
python_function('doql/generators/web_gen/config.py', '_gen_index_html', 1, 1, 1).
python_function('doql/generators/web_gen/core.py', '_gen_main_tsx', 0, 1, 1).
python_function('doql/generators/web_gen/core.py', '_gen_index_css', 0, 1, 1).
python_function('doql/generators/web_gen/core.py', '_gen_api_ts', 0, 1, 1).
python_function('doql/generators/web_gen/pages.py', '_gen_dashboard', 1, 3, 4).
python_function('doql/generators/web_gen/pages.py', '_field_input', 1, 7, 0).
python_function('doql/generators/web_gen/pages.py', '_build_interface_body', 1, 4, 4).
python_function('doql/generators/web_gen/pages.py', '_gen_entity_page', 1, 10, 6).
python_function('doql/generators/web_gen/pwa.py', '_gen_manifest', 1, 1, 1).
python_function('doql/generators/web_gen/pwa.py', '_gen_service_worker', 1, 1, 3).
python_function('doql/generators/web_gen/pwa.py', '_gen_sw_register', 0, 1, 1).
python_function('doql/generators/web_gen/router.py', '_gen_app', 1, 3, 4).
python_function('doql/generators/workflow_gen.py', '_gen_engine', 0, 1, 1).
python_function('doql/generators/workflow_gen.py', '_step_fn_name', 1, 1, 4).
python_function('doql/generators/workflow_gen.py', '_gen_workflow_module', 2, 7, 7).
python_function('doql/generators/workflow_gen.py', '_extract_cron', 1, 4, 3).
python_function('doql/generators/workflow_gen.py', '_gen_scheduler', 1, 8, 4).
python_function('doql/generators/workflow_gen.py', '_gen_init', 1, 2, 3).
python_function('doql/generators/workflow_gen.py', '_gen_routes', 1, 1, 1).
python_function('doql/generators/workflow_gen.py', 'generate', 3, 3, 9).
python_function('doql/importers/yaml_importer.py', '_get', 3, 1, 1).
python_function('doql/importers/yaml_importer.py', '_build_entity_field', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_entity', 1, 2, 3).
python_function('doql/importers/yaml_importer.py', '_build_data_source', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_template', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_document', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_report', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_database', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_api_client', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_webhook', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_page', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_interface', 1, 2, 3).
python_function('doql/importers/yaml_importer.py', '_build_integration', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_workflow_step', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_workflow', 1, 2, 3).
python_function('doql/importers/yaml_importer.py', '_build_role', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_build_deploy', 1, 1, 2).
python_function('doql/importers/yaml_importer.py', '_import_metadata', 2, 1, 1).
python_function('doql/importers/yaml_importer.py', '_import_collection', 4, 2, 4).
python_function('doql/importers/yaml_importer.py', 'import_yaml', 1, 3, 4).
python_function('doql/importers/yaml_importer.py', 'import_yaml_text', 1, 2, 4).
python_function('doql/importers/yaml_importer.py', 'import_yaml_file', 1, 1, 2).
python_function('doql/integrations/op3_bridge.py', 'build_layer_tree', 1, 2, 2).
python_function('doql/integrations/op3_bridge.py', 'snapshot_to_less', 2, 1, 2).
python_function('doql/lsp_server/__init__.py', 'main', 0, 2, 5).
python_function('doql/lsp_server/completion.py', 'completion', 2, 5, 8).
python_function('doql/lsp_server/definition.py', 'definition', 2, 3, 14).
python_function('doql/lsp_server/diagnostics.py', '_diagnostics_for', 2, 10, 17).
python_function('doql/lsp_server/diagnostics.py', '_on_text_document_event', 2, 1, 3).
python_function('doql/lsp_server/diagnostics.py', 'did_open', 2, 1, 2).
python_function('doql/lsp_server/diagnostics.py', 'did_change', 2, 1, 2).
python_function('doql/lsp_server/diagnostics.py', 'did_save', 2, 1, 2).
python_function('doql/lsp_server/hover.py', '_hover_field', 2, 5, 4).
python_function('doql/lsp_server/hover.py', '_hover_entity', 2, 7, 5).
python_function('doql/lsp_server/hover.py', 'hover', 2, 5, 7).
python_function('doql/lsp_server/symbols.py', 'document_symbols', 2, 8, 10).
python_function('doql/lsp_server/utils.py', '_parse_doc', 1, 2, 1).
python_function('doql/lsp_server/utils.py', '_find_line_col', 2, 3, 3).
python_function('doql/lsp_server/utils.py', '_word_at', 2, 8, 3).
python_function('doql/parsers/__init__.py', '_is_css_format', 1, 2, 3).
python_function('doql/parsers/__init__.py', 'detect_doql_file', 1, 3, 1).
python_function('doql/parsers/__init__.py', 'parse_file', 1, 3, 6).
python_function('doql/parsers/__init__.py', 'parse_text', 1, 3, 6).
python_function('doql/parsers/__init__.py', 'parse_env', 1, 6, 6).
python_function('doql/parsers/blocks.py', 'split_blocks', 1, 4, 11).
python_function('doql/parsers/blocks.py', 'apply_block', 4, 2, 3).
python_function('doql/parsers/css_mappers/__init__.py', '_map_project', 3, 5, 5).
python_function('doql/parsers/css_mappers/config.py', '_map_config_block', 7, 4, 6).
python_function('doql/parsers/css_mappers/config.py', '_map_template', 3, 1, 1).
python_function('doql/parsers/css_mappers/config.py', '_map_document', 3, 1, 1).
python_function('doql/parsers/css_mappers/config.py', '_map_report', 3, 1, 3).
python_function('doql/parsers/css_mappers/entity.py', '_map_entity', 3, 9, 7).
python_function('doql/parsers/css_mappers/entity.py', '_parse_type_flags', 1, 3, 4).
python_function('doql/parsers/css_mappers/entity.py', '_add_entity_field', 3, 2, 3).
python_function('doql/parsers/css_mappers/entity.py', '_parse_type_modifiers', 1, 4, 6).
python_function('doql/parsers/css_mappers/entity.py', '_map_data_source', 3, 1, 4).
python_function('doql/parsers/css_mappers/infra.py', '_map_deploy', 3, 3, 4).
python_function('doql/parsers/css_mappers/infra.py', '_map_database', 3, 1, 3).
python_function('doql/parsers/css_mappers/infra.py', '_map_environment', 3, 6, 6).
python_function('doql/parsers/css_mappers/infra.py', '_map_infrastructure', 3, 5, 6).
python_function('doql/parsers/css_mappers/infra.py', '_map_ingress', 3, 3, 5).
python_function('doql/parsers/css_mappers/infra.py', '_map_ci', 3, 4, 5).
python_function('doql/parsers/css_mappers/integration.py', '_map_integration', 3, 1, 4).
python_function('doql/parsers/css_mappers/interface.py', '_find_or_create_interface', 2, 4, 3).
python_function('doql/parsers/css_mappers/interface.py', '_handle_interface_chain', 3, 5, 2).
python_function('doql/parsers/css_mappers/interface.py', '_apply_interface_properties', 2, 6, 4).
python_function('doql/parsers/css_mappers/interface.py', '_apply_nested_interface_children', 2, 3, 2).
python_function('doql/parsers/css_mappers/interface.py', '_map_interface', 3, 4, 5).
python_function('doql/parsers/css_mappers/interface.py', '_add_interface_page', 3, 7, 4).
python_function('doql/parsers/css_mappers/workflow.py', '_parse_step_text', 1, 6, 5).
python_function('doql/parsers/css_mappers/workflow.py', '_append_inline_steps', 3, 3, 5).
python_function('doql/parsers/css_mappers/workflow.py', '_append_child_steps', 4, 4, 6).
python_function('doql/parsers/css_mappers/workflow.py', '_map_workflow', 3, 6, 7).
python_function('doql/parsers/css_mappers/workflow.py', '_map_role', 3, 2, 4).
python_function('doql/parsers/css_parser.py', '_map_to_spec', 1, 3, 5).
python_function('doql/parsers/css_parser.py', '_apply_css_block', 3, 8, 9).
python_function('doql/parsers/css_parser.py', 'parse_css_file', 1, 2, 5).
python_function('doql/parsers/css_parser.py', 'parse_css_text', 2, 3, 6).
python_function('doql/parsers/css_parser.py', '_detect_format', 1, 3, 2).
python_function('doql/parsers/css_tokenizer.py', '_make_css_block', 3, 2, 3).
python_function('doql/parsers/css_tokenizer.py', '_tokenise_css', 1, 9, 6).
python_function('doql/parsers/css_tokenizer.py', '_consume_pending', 3, 1, 3).
python_function('doql/parsers/css_tokenizer.py', '_process_decl_line', 4, 7, 7).
python_function('doql/parsers/css_tokenizer.py', '_parse_declarations', 1, 11, 7).
python_function('doql/parsers/css_transformers/__init__.py', '_sass_to_css', 1, 1, 6).
python_function('doql/parsers/css_transformers/indent.py', '_close_indent_blocks', 3, 3, 3).
python_function('doql/parsers/css_transformers/indent.py', '_convert_indent_to_braces', 1, 9, 12).
python_function('doql/parsers/css_transformers/mixins.py', '_extract_mixins', 1, 6, 6).
python_function('doql/parsers/css_transformers/mixins.py', '_expand_includes', 2, 5, 4).
python_function('doql/parsers/css_transformers/selectors.py', '_is_doql_property_decl', 1, 1, 3).
python_function('doql/parsers/css_transformers/selectors.py', '_is_selector_line', 1, 11, 9).
python_function('doql/parsers/css_transformers/selectors.py', '_is_step_line', 1, 1, 2).
python_function('doql/parsers/css_transformers/selectors.py', '_has_bracket_selector', 1, 4, 3).
python_function('doql/parsers/css_transformers/selectors.py', '_is_selector_starter', 1, 8, 7).
python_function('doql/parsers/css_transformers/selectors.py', '_find_step_block_end', 3, 7, 6).
python_function('doql/parsers/css_transformers/variables.py', '_resolve_vars', 2, 6, 8).
python_function('doql/parsers/css_transformers/variables.py', '_resolve_less_vars', 1, 1, 1).
python_function('doql/parsers/css_transformers/variables.py', '_resolve_sass_vars', 1, 1, 1).
python_function('doql/parsers/css_utils.py', '_strip_comments', 1, 1, 1).
python_function('doql/parsers/css_utils.py', '_strip_quotes', 1, 4, 1).
python_function('doql/parsers/css_utils.py', '_parse_list', 1, 3, 2).
python_function('doql/parsers/css_utils.py', '_parse_selector', 1, 5, 7).
python_function('doql/parsers/extractors.py', 'extract_val', 2, 6, 6).
python_function('doql/parsers/extractors.py', 'extract_list', 2, 4, 3).
python_function('doql/parsers/extractors.py', 'extract_yaml_list', 2, 5, 7).
python_function('doql/parsers/extractors.py', '_extract_page_from_format1', 1, 5, 10).
python_function('doql/parsers/extractors.py', '_extract_page_from_format2', 1, 6, 13).
python_function('doql/parsers/extractors.py', 'extract_pages', 1, 2, 2).
python_function('doql/parsers/extractors.py', '_should_skip_line', 1, 4, 1).
python_function('doql/parsers/extractors.py', '_is_valid_field_name', 1, 2, 2).
python_function('doql/parsers/extractors.py', '_parse_field_flags', 1, 1, 1).
python_function('doql/parsers/extractors.py', '_parse_field_ref', 1, 2, 2).
python_function('doql/parsers/extractors.py', '_parse_field_default', 1, 2, 2).
python_function('doql/parsers/extractors.py', '_parse_field_type', 1, 1, 1).
python_function('doql/parsers/extractors.py', 'extract_entity_fields', 1, 5, 12).
python_function('doql/parsers/extractors.py', 'collect_env_refs', 1, 1, 3).
python_function('doql/parsers/registry.py', 'register', 1, 1, 0).
python_function('doql/parsers/registry.py', 'get_handler', 1, 1, 1).
python_function('doql/parsers/registry.py', 'list_registered', 0, 1, 2).
python_function('doql/parsers/registry.py', '_handle_app', 3, 2, 4).
python_function('doql/parsers/registry.py', '_handle_version', 3, 1, 2).
python_function('doql/parsers/registry.py', '_handle_domain', 3, 1, 2).
python_function('doql/parsers/registry.py', '_handle_languages', 3, 3, 3).
python_function('doql/parsers/registry.py', '_handle_author', 3, 3, 3).
python_function('doql/parsers/registry.py', '_handle_default_language', 3, 1, 2).
python_function('doql/parsers/registry.py', '_handle_entity', 3, 1, 8).
python_function('doql/parsers/registry.py', '_handle_data', 3, 2, 6).
python_function('doql/parsers/registry.py', '_handle_template', 3, 2, 7).
python_function('doql/parsers/registry.py', '_handle_document', 3, 4, 8).
python_function('doql/parsers/registry.py', '_handle_report', 3, 2, 6).
python_function('doql/parsers/registry.py', '_handle_database', 3, 2, 6).
python_function('doql/parsers/registry.py', '_handle_api_client', 3, 3, 8).
python_function('doql/parsers/registry.py', '_handle_webhook', 3, 1, 6).
python_function('doql/parsers/registry.py', '_handle_interface', 3, 3, 7).
python_function('doql/parsers/registry.py', '_handle_integration', 3, 1, 5).
python_function('doql/parsers/registry.py', '_handle_workflow', 3, 1, 6).
python_function('doql/parsers/registry.py', '_handle_roles', 3, 5, 6).
python_function('doql/parsers/registry.py', '_handle_role', 3, 4, 5).
python_function('doql/parsers/registry.py', '_handle_import_block', 3, 2, 5).
python_function('doql/parsers/registry.py', '_handle_scenarios', 3, 1, 2).
python_function('doql/parsers/registry.py', '_handle_tests', 3, 1, 2).
python_function('doql/parsers/registry.py', '_handle_deploy', 3, 6, 4).
python_function('doql/parsers/registry.py', '_handle_infrastructure', 3, 5, 8).
python_function('doql/parsers/registry.py', '_handle_ingress', 3, 3, 6).
python_function('doql/parsers/registry.py', '_handle_ci', 3, 3, 7).
python_function('doql/parsers/registry.py', '_handle_project', 3, 3, 7).
python_function('doql/parsers/validators.py', '_validate_app_name', 1, 3, 2).
python_function('doql/parsers/validators.py', '_validate_env_refs', 2, 6, 5).
python_function('doql/parsers/validators.py', '_validate_data_source_files', 2, 6, 5).
python_function('doql/parsers/validators.py', '_validate_file_refs', 6, 4, 5).
python_function('doql/parsers/validators.py', '_validate_document_templates', 2, 1, 1).
python_function('doql/parsers/validators.py', '_validate_template_files', 2, 1, 1).
python_function('doql/parsers/validators.py', '_validate_document_partials', 1, 5, 2).
python_function('doql/parsers/validators.py', '_validate_entity_refs', 1, 6, 2).
python_function('doql/parsers/validators.py', '_validate_interfaces', 1, 4, 2).
python_function('doql/parsers/validators.py', '_validate_deploy_strategy', 1, 4, 2).
python_function('doql/parsers/validators.py', 'validate', 3, 2, 10).
python_function('doql/plugins.py', '_discover_entry_points', 0, 5, 8).
python_function('doql/plugins.py', '_discover_local', 1, 8, 11).
python_function('doql/plugins.py', 'discover_plugins', 1, 1, 2).
python_function('doql/plugins.py', 'run_plugins', 4, 4, 5).
python_function('doql/utils/clean.py', '_clean', 1, 9, 3).
python_function('doql/utils/naming.py', 'snake', 1, 1, 3).
python_function('doql/utils/naming.py', 'kebab', 1, 1, 2).
python_function('doql/utils/naming.py', 'slug', 1, 1, 2).
python_function('playground/doql_build.py', '_collect_parse_errors', 2, 3, 3).
python_function('playground/doql_build.py', '_build_env', 1, 4, 3).
python_function('playground/doql_build.py', '_validate', 3, 2, 3).
python_function('playground/doql_build.py', '_spec_summary', 1, 6, 0).
python_function('playground/doql_build.py', '_try_generate', 2, 2, 4).
python_function('playground/doql_build.py', 'build', 1, 3, 9).
python_function('plugins/doql-plugin-erp/doql_plugin_erp/__init__.py', '_odoo_client_module', 0, 1, 1).
python_function('plugins/doql-plugin-erp/doql_plugin_erp/__init__.py', '_mapping_module', 0, 1, 1).
python_function('plugins/doql-plugin-erp/doql_plugin_erp/__init__.py', '_sync_module', 0, 1, 1).
python_function('plugins/doql-plugin-erp/doql_plugin_erp/__init__.py', '_webhook_module', 0, 1, 1).
python_function('plugins/doql-plugin-erp/doql_plugin_erp/__init__.py', '_readme', 1, 1, 1).
python_function('plugins/doql-plugin-erp/doql_plugin_erp/__init__.py', 'generate', 4, 2, 8).
python_function('plugins/doql-plugin-fleet/doql_plugin_fleet/__init__.py', '_readme', 1, 1, 1).
python_function('plugins/doql-plugin-fleet/doql_plugin_fleet/__init__.py', 'generate', 4, 2, 9).
python_function('plugins/doql-plugin-fleet/doql_plugin_fleet/device_registry.py', '_device_registry_module', 0, 1, 1).
python_function('plugins/doql-plugin-fleet/doql_plugin_fleet/metrics.py', '_metrics_module', 0, 1, 1).
python_function('plugins/doql-plugin-fleet/doql_plugin_fleet/migration.py', '_migration_module', 0, 1, 1).
python_function('plugins/doql-plugin-fleet/doql_plugin_fleet/ota.py', '_ota_module', 0, 1, 1).
python_function('plugins/doql-plugin-fleet/doql_plugin_fleet/tenant.py', '_tenant_module', 0, 1, 1).
python_function('plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py', '_audit_log_module', 0, 1, 1).
python_function('plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py', '_e_signature_module', 0, 1, 1).
python_function('plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py', '_audit_middleware', 0, 1, 1).
python_function('plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py', '_migration_audit', 0, 1, 1).
python_function('plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py', '_readme', 1, 1, 1).
python_function('plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py', 'generate', 4, 2, 8).
python_function('plugins/doql-plugin-iso17025/doql_plugin_iso17025/__init__.py', 'generate', 4, 1, 2).
python_function('plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py', 'generate', 0, 1, 1).
python_function('plugins/doql-plugin-iso17025/doql_plugin_iso17025/drift_monitor.py', 'generate', 0, 1, 1).
python_function('plugins/doql-plugin-iso17025/doql_plugin_iso17025/migration.py', 'generate', 0, 1, 1).
python_function('plugins/doql-plugin-iso17025/doql_plugin_iso17025/traceability.py', 'generate', 0, 1, 1).
python_function('plugins/doql-plugin-iso17025/doql_plugin_iso17025/uncertainty.py', 'generate', 0, 1, 1).
python_function('plugins/doql-plugin-shared/doql_plugin_shared/base.py', 'plugin_generate', 3, 3, 4).
python_function('plugins/doql-plugin-shared/doql_plugin_shared/readme.py', 'generate_readme', 4, 3, 1).
python_function('tests/env_manager.py', '_find_free_port', 0, 1, 3).
python_function('tests/env_manager.py', '_has_module', 1, 2, 3).
python_function('tests/env_manager.py', '_run', 3, 3, 1).
python_function('tests/env_manager.py', '_api_present_files', 1, 3, 1).
python_function('tests/env_manager.py', '_api_compile_check', 2, 3, 4).
python_function('tests/env_manager.py', '_check_postgres_skip', 1, 5, 4).
python_function('tests/env_manager.py', '_wait_health', 2, 5, 5).
python_function('tests/env_manager.py', '_check_api_openapi', 1, 2, 7).
python_function('tests/env_manager.py', 'check_api', 1, 14, 20).
python_function('tests/env_manager.py', 'check_web', 1, 6, 12).
python_function('tests/env_manager.py', 'check_mobile', 1, 9, 14).
python_function('tests/env_manager.py', '_check_tauri_conf', 1, 5, 6).
python_function('tests/env_manager.py', '_check_desktop_files', 1, 2, 2).
python_function('tests/env_manager.py', '_check_main_rs', 1, 3, 3).
python_function('tests/env_manager.py', '_check_cargo', 2, 6, 7).
python_function('tests/env_manager.py', 'check_desktop', 1, 6, 10).
python_function('tests/env_manager.py', 'check_infra', 1, 8, 12).
python_function('tests/env_manager.py', 'process_example', 1, 3, 10).
python_function('tests/env_manager.py', 'render_text', 1, 13, 10).
python_function('tests/env_manager.py', 'render_json', 1, 5, 6).
python_function('tests/env_manager.py', 'main', 1, 11, 13).
python_function('tests/integration/test_adopt_from_device.py', '_healthy_rpi_responses', 0, 1, 0).
python_function('tests/integration/test_adopt_from_device.py', '_rpi5_podman_quadlet_responses', 0, 1, 0).
python_function('tests/integration/test_adopt_from_device.py', 'test_adopt_from_device_returns_less_text', 0, 5, 3).
python_function('tests/integration/test_adopt_from_device.py', 'test_adopt_from_device_writes_output', 1, 4, 6).
python_function('tests/integration/test_adopt_from_device.py', 'test_adopt_from_device_to_snapshot_contains_layer_data', 0, 5, 4).
python_function('tests/integration/test_adopt_from_device.py', 'test_adopt_output_is_parsable_by_doql', 1, 2, 4).
python_function('tests/integration/test_adopt_from_device.py', 'test_adopt_from_rpi5_podman_quadlet_returns_less_text', 0, 5, 3).
python_function('tests/integration/test_adopt_from_device.py', 'test_adopt_from_rpi5_to_snapshot_contains_all_services', 0, 7, 4).
python_function('tests/integration/test_adopt_from_device.py', 'test_adopt_from_rpi5_to_snapshot_contains_all_containers', 0, 9, 4).
python_function('tests/integration/test_adopt_from_device.py', 'test_adopt_from_rpi5_output_is_parsable_by_doql', 1, 2, 4).
python_function('tests/integration/test_adopt_from_device.py', '_make_cli_args', 0, 1, 3).
python_function('tests/integration/test_adopt_from_device.py', 'test_cmd_adopt_from_device_writes_file', 3, 5, 10).
python_function('tests/integration/test_adopt_from_device.py', 'test_cmd_adopt_rejects_non_less_format', 1, 3, 3).
python_function('tests/integration/test_adopt_from_device.py', 'test_cmd_adopt_without_target_or_device_errors', 1, 3, 3).
python_function('tests/integration/test_adopt_from_device.py', 'test_cmd_adopt_refuses_to_overwrite', 3, 3, 5).
python_function('tests/integration/test_build_from_device.py', '_healthy_rpi_responses', 0, 1, 0).
python_function('tests/integration/test_build_from_device.py', '_build_args', 1, 1, 4).
python_function('tests/integration/test_build_from_device.py', '_patch_context_factory', 2, 1, 4).
python_function('tests/integration/test_build_from_device.py', 'test_scan_device_writes_app_doql_less_in_root', 3, 8, 8).
python_function('tests/integration/test_build_from_device.py', 'test_scan_device_honours_global_file_flag', 2, 3, 7).
python_function('tests/integration/test_build_from_device.py', 'test_scan_device_refuses_to_overwrite_without_force', 3, 5, 9).
python_function('tests/integration/test_build_from_device.py', 'test_scan_device_force_overwrites', 2, 3, 7).
python_function('tests/integration/test_build_from_device.py', '_minimal_env_file', 1, 1, 1).
python_function('tests/integration/test_build_from_device.py', 'test_cmd_build_from_device_runs_full_pipeline', 3, 5, 8).
python_function('tests/integration/test_build_from_device.py', 'test_cmd_build_refuses_to_clobber_without_force', 3, 4, 8).
python_function('tests/integration/test_build_from_device.py', 'test_cmd_build_without_from_device_skips_scan', 2, 2, 6).
python_function('tests/integration/test_drift.py', '_rpi_responses_with_service', 1, 1, 0).
python_function('tests/integration/test_drift.py', '_intended_less', 2, 1, 0).
python_function('tests/integration/test_drift.py', 'test_parse_intended_attaches_source_path', 1, 4, 4).
python_function('tests/integration/test_drift.py', 'test_parse_intended_missing_file', 1, 1, 2).
python_function('tests/integration/test_drift.py', 'test_detect_drift_no_changes', 1, 6, 6).
python_function('tests/integration/test_drift.py', 'test_detect_drift_service_state_mismatch', 1, 4, 6).
python_function('tests/integration/test_drift.py', 'test_detect_drift_missing_file_raises', 2, 1, 4).
python_function('tests/integration/test_drift.py', '_args', 0, 1, 3).
python_function('tests/integration/test_drift.py', '_patch_context', 2, 1, 4).
python_function('tests/integration/test_drift.py', 'test_cmd_drift_returns_drift_exit_code', 3, 3, 9).
python_function('tests/integration/test_drift.py', 'test_cmd_drift_json_output_is_valid', 3, 10, 12).
python_function('tests/integration/test_drift.py', 'test_cmd_drift_missing_from_device', 1, 3, 3).
python_function('tests/integration/test_drift.py', 'test_cmd_drift_missing_file', 3, 3, 4).
python_function('tests/integration/test_drift.py', 'test_cmd_drift_unsupported_format_gives_actionable_hint', 3, 5, 5).
python_function('tests/integration/test_drift.py', 'test_cmd_drift_explicit_missing_file', 2, 3, 4).
python_function('tests/integration/test_drift.py', 'test_cmd_drift_no_drift_exit_code_zero', 3, 2, 6).
python_function('tests/integration/test_op3_bridge.py', 'test_op3_importable', 0, 5, 2).
python_function('tests/integration/test_op3_bridge.py', 'test_op3_enabled_reads_env', 3, 2, 3).
python_function('tests/integration/test_op3_bridge.py', 'test_should_use_op3_requires_both', 1, 3, 3).
python_function('tests/integration/test_op3_bridge.py', 'test_require_op3_noop_when_available', 0, 1, 1).
python_function('tests/integration/test_op3_bridge.py', 'test_build_layer_tree_defaults', 0, 5, 2).
python_function('tests/integration/test_op3_bridge.py', 'test_build_layer_tree_explicit_leaf_pulls_deps', 0, 5, 3).
python_function('tests/integration/test_op3_bridge.py', 'test_build_layer_tree_rejects_unknown', 0, 1, 2).
python_function('tests/integration/test_op3_bridge.py', 'test_scanner_runs_against_mock_context', 0, 7, 5).
python_function('tests/integration/test_op3_bridge.py', 'test_snapshot_to_less_produces_parsable_less', 0, 3, 6).
python_function('tests/playground_e2e.py', 'serve', 0, 1, 5).
python_function('tests/playground_e2e.py', 'main', 0, 9, 21).
python_function('tests/runtime_smoke.py', 'step', 4, 5, 2).
python_function('tests/runtime_smoke.py', 'main', 0, 10, 11).
python_function('tests/test_adopt.py', '_write', 3, 1, 4).
python_function('tests/test_adopt.py', '_pyproject', 2, 1, 0).
python_function('tests/test_adopt.py', 'test_jwt_secret_does_not_crash_renderer', 1, 8, 9).
python_function('tests/test_adopt.py', 'test_pydantic_dtos_are_excluded_from_entities', 1, 5, 3).
python_function('tests/test_adopt.py', 'test_generic_db_service_name_is_normalised', 1, 5, 3).
python_function('tests/test_adopt.py', 'test_fastapi_dependency_alone_does_not_create_api_interface', 1, 4, 3).
python_function('tests/test_adopt.py', 'test_fastapi_with_main_py_creates_api', 1, 5, 4).
python_function('tests/test_adopt.py', 'test_api_entry_point_in_scripts_creates_api', 1, 4, 3).
python_function('tests/test_adopt.py', '_make_args', 3, 1, 2).
python_function('tests/test_adopt.py', 'test_cmd_adopt_returns_zero_on_success', 1, 3, 6).
python_function('tests/test_adopt.py', 'test_cmd_adopt_returns_nonzero_on_render_failure', 2, 2, 6).
python_function('tests/test_adopt.py', 'test_cmd_adopt_refuses_to_overwrite_without_force', 1, 3, 6).
python_function('tests/test_adopt.py', 'test_cmd_adopt_rejects_non_directory', 2, 2, 2).
python_function('tests/test_adopt.py', 'test_makefile_targets_become_workflows', 1, 12, 3).
python_function('tests/test_adopt.py', 'test_makefile_workflows_round_trip_to_css', 1, 3, 4).
python_function('tests/test_adopt.py', 'test_taskfile_yml_tasks_become_workflows', 1, 6, 3).
python_function('tests/test_adopt.py', 'test_dependency_only_targets_emit_depend_steps', 1, 12, 4).
python_function('tests/test_adopt.py', 'test_empty_target_without_deps_is_skipped', 1, 3, 2).
python_function('tests/test_adopt.py', 'test_makefile_variable_assignments_are_not_workflows', 1, 5, 2).
python_function('tests/test_adopt.py', 'test_workflows_are_deduplicated_across_makefile_and_taskfile', 1, 5, 3).
python_function('tests/test_adopt.py', '_assert_oqlos_metadata', 1, 3, 0).
python_function('tests/test_adopt.py', '_assert_oqlos_interfaces', 1, 8, 1).
python_function('tests/test_adopt.py', '_assert_oqlos_deploy', 1, 3, 0).
python_function('tests/test_adopt.py', '_assert_oqlos_workflows', 1, 3, 0).
python_function('tests/test_adopt.py', '_assert_oqlos_entities', 1, 3, 0).
python_function('tests/test_adopt.py', '_assert_oqlos_environments', 1, 3, 0).
python_function('tests/test_adopt.py', '_assert_adopt_roundtrip', 1, 5, 6).
python_function('tests/test_adopt.py', 'test_adopt_e2e_real_project_oqlos', 1, 1, 10).
python_function('tests/test_adopt.py', 'test_discover_subprojects', 1, 4, 3).
python_function('tests/test_adopt.py', 'test_click_not_inferred_from_comment_or_changelog', 1, 4, 4).
python_function('tests/test_adopt.py', 'test_fastapi_detected_from_server_py', 1, 5, 4).
python_function('tests/test_css_parser.py', 'test_css_parse_minimal', 0, 4, 1).
python_function('tests/test_css_parser.py', 'test_css_parse_entity', 0, 4, 2).
python_function('tests/test_css_parser.py', 'test_css_parse_interface', 0, 3, 2).
python_function('tests/test_css_parser.py', 'test_css_parse_role', 0, 3, 2).
python_function('tests/test_css_parser.py', 'test_css_parse_deploy', 0, 3, 1).
python_function('tests/test_css_parser.py', 'test_less_variable_expansion', 0, 3, 1).
python_function('tests/test_css_parser.py', 'test_sass_basic_parsing', 0, 2, 1).
python_function('tests/test_css_parser.py', 'test_parses_css_example_file', 2, 7, 5).
python_function('tests/test_css_parser.py', 'test_detect_doql_file_prefers_less', 1, 2, 2).
python_function('tests/test_css_parser.py', 'test_detect_doql_file_prefers_sass', 1, 2, 2).
python_function('tests/test_css_parser.py', 'test_detect_doql_file_falls_back_to_classic', 1, 2, 2).
python_function('tests/test_css_parser.py', 'test_iot_fleet_less_has_entities', 0, 6, 4).
python_function('tests/test_css_parser.py', 'test_notes_app_sass_has_all_interfaces', 0, 5, 4).
python_function('tests/test_css_parser.py', 'test_css_parse_error_has_line_info', 0, 1, 1).
python_function('tests/test_css_parser.py', 'test_css_unknown_selector_gives_warning', 0, 1, 1).
python_function('tests/test_css_parser.py', 'test_less_syntax_error_recovery', 0, 3, 1).
python_function('tests/test_css_parser.py', '_spec_to_comparable_dict', 1, 5, 2).
python_function('tests/test_css_parser.py', 'test_doql_vs_less_regression', 1, 10, 7).
python_function('tests/test_css_parser.py', 'test_css_parse_project_blocks', 0, 14, 2).
python_function('tests/test_deploy.py', '_args', 0, 1, 3).
python_function('tests/test_deploy.py', '_spec_with_directives', 0, 1, 2).
python_function('tests/test_deploy.py', 'test_run_directive_calls_shell', 0, 2, 3).
python_function('tests/test_deploy.py', 'test_run_directive_returns_nonzero_on_failure', 0, 2, 2).
python_function('tests/test_deploy.py', 'test_redeploy_api_returns_minus_one_when_not_installed', 1, 2, 4).
python_function('tests/test_deploy.py', '_import_without_redeploy', 1, 2, 3).
python_function('tests/test_deploy.py', 'test_redeploy_cli_returns_minus_one_when_not_on_path', 0, 2, 3).
python_function('tests/test_deploy.py', 'test_redeploy_cli_runs_subprocess_when_available', 0, 2, 4).
python_function('tests/test_deploy.py', 'test_redeploy_cli_passes_dry_run_and_plan_only', 0, 4, 3).
python_function('tests/test_deploy.py', 'test_deploy_uses_directives_when_no_migration_yaml', 2, 2, 7).
python_function('tests/test_deploy.py', 'test_deploy_directive_failure_stops_pipeline', 1, 3, 6).
python_function('tests/test_deploy.py', 'test_deploy_skips_missing_directive_phases', 1, 2, 7).
python_function('tests/test_deploy.py', 'test_deploy_docker_compose_fallback_no_migration_no_directives', 1, 5, 7).
python_function('tests/test_deploy.py', 'test_deploy_fallback_fails_when_no_build', 1, 2, 6).
python_function('tests/test_deploy.py', 'test_deploy_prefers_redeploy_api_when_migration_yaml_exists', 1, 2, 8).
python_function('tests/test_deploy.py', 'test_deploy_falls_back_to_redeploy_cli_when_api_unavailable', 1, 2, 8).
python_function('tests/test_deploy.py', 'test_deploy_warns_when_redeploy_missing_and_no_directives', 2, 2, 8).
python_function('tests/test_deploy.py', 'test_dry_run_and_plan_only_passed_to_redeploy', 1, 4, 7).
python_function('tests/test_deploy.py', 'test_target_env_defaults_to_prod', 1, 2, 7).
python_function('tests/test_exporters.py', 'sample_spec', 0, 1, 10).
python_function('tests/test_exporters.py', 'test_yaml_roundtrip_real_example', 1, 7, 8).
python_function('tests/test_exporters.py', 'test_css_export_real_example', 1, 4, 5).
python_function('tests/test_exporters.py', 'test_markdown_export_real_example', 1, 4, 5).
python_function('tests/test_exporters.py', 'test_css_export_project_blocks', 0, 5, 7).
python_function('tests/test_exporters_shims.py', 'test_css_exporter_shim_re_exports_public_api', 0, 5, 1).
python_function('tests/test_exporters_shims.py', 'test_css_exporter_shim_re_exports_renderers', 0, 3, 1).
python_function('tests/test_exporters_shims.py', 'test_css_exporter_shim_re_exports_format_helpers', 0, 3, 1).
python_function('tests/test_exporters_shims.py', 'test_markdown_exporter_shim_re_exports_public_api', 0, 3, 1).
python_function('tests/test_exporters_shims.py', 'test_markdown_exporter_shim_re_exports_writers', 0, 3, 1).
python_function('tests/test_exporters_shims.py', 'test_markdown_exporter_shim_re_exports_helpers', 0, 3, 1).
python_function('tests/test_exporters_shims.py', 'test_css_shim_roundtrip_matches_direct_subpackage', 1, 2, 5).
python_function('tests/test_generators.py', '_run_doql', 0, 2, 3).
python_function('tests/test_generators.py', '_compile_all_py', 1, 2, 3).
python_function('tests/test_generators.py', 'test_build_example', 2, 6, 9).
python_function('tests/test_generators.py', 'test_init_and_build_template', 2, 7, 8).
python_function('tests/test_generators.py', 'test_sync_no_changes_is_noop', 1, 6, 6).
python_function('tests/test_generators.py', 'test_list_templates_includes_all', 0, 4, 1).
python_function('tests/test_lsp.py', 'test_parse_doc_handles_valid_input', 0, 3, 1).
python_function('tests/test_lsp.py', 'test_parse_doc_returns_none_on_crash', 0, 2, 1).
python_function('tests/test_lsp.py', 'test_find_line_col_finds_needle', 0, 3, 1).
python_function('tests/test_lsp.py', 'test_word_at_extracts_word', 0, 2, 2).
python_function('tests/test_lsp.py', 'test_diagnostics_on_asset_management_example', 0, 4, 8).
python_function('tests/test_lsp.py', 'test_keyword_completion_includes_common_top_level', 0, 2, 2).
python_function('tests/test_parser.py', 'test_parse_text_minimal', 0, 4, 1).
python_function('tests/test_parser.py', 'test_parse_text_full_entity', 0, 7, 3).
python_function('tests/test_parser.py', 'test_parse_text_languages_list', 0, 2, 1).
python_function('tests/test_parser.py', 'test_parse_text_workflow_with_schedule_and_inline_comment', 0, 4, 2).
python_function('tests/test_parser.py', 'test_parse_text_recovers_from_broken_block', 0, 4, 2).
python_function('tests/test_parser.py', 'test_parse_errors_is_a_list', 0, 2, 2).
python_function('tests/test_parser.py', 'test_parses_example_file', 1, 4, 5).
python_function('tests/test_parser.py', 'test_asset_management_entities', 0, 6, 5).
python_function('tests/test_parser.py', 'test_validate_detects_missing_env_ref', 0, 2, 3).
python_function('tests/test_parser.py', 'test_validation_issue_has_line_field', 0, 5, 2).
python_function('tests/test_parser.py', 'test_validate_detects_dangling_entity_ref', 0, 5, 2).
python_function('tests/test_parser.py', 'test_calibration_lab_has_no_dangling_refs', 0, 7, 5).
python_function('tests/test_parser.py', 'test_deprecated_docker_compose_strategy_warns', 0, 5, 4).
python_function('tests/test_parser.py', 'test_deprecated_quadlet_strategy_warns', 0, 5, 4).
python_function('tests/test_parser.py', 'test_canonical_strategy_no_warning', 0, 5, 4).
python_function('tests/test_parser_benchmark.py', 'test_css_parser_cold_start_under_threshold', 0, 2, 2).
python_function('tests/test_parser_benchmark.py', 'test_less_parser_variable_resolution_under_threshold', 0, 3, 2).
python_function('tests/test_parser_benchmark.py', 'test_real_example_parse_under_threshold', 2, 4, 6).
python_function('tests/test_parser_benchmark.py', 'test_css_vs_classic_parse_time_parity', 0, 5, 4).
python_function('tests/test_parser_benchmark.py', 'test_large_file_parse_under_threshold', 0, 4, 7).
python_function('tests/test_plugins.py', 'test_entrypoint_discovery_finds_all_four', 0, 4, 3).
python_function('tests/test_plugins.py', 'test_doql_plugins_module_import', 0, 3, 1).
python_function('tests/test_plugins.py', '_run_plugin_and_import', 3, 4, 7).
python_function('tests/test_plugins.py', 'test_iso17025_uncertainty_budget_numerical', 0, 3, 5).
python_function('tests/test_plugins.py', 'test_iso17025_drift_monitor_detects_stable', 0, 5, 5).
python_function('tests/test_plugins.py', 'test_iso17025_drift_monitor_flags_excessive_drift', 0, 5, 5).
python_function('tests/test_plugins.py', 'test_fleet_ota_canary_advances_on_success', 0, 2, 2).
python_function('tests/test_plugins.py', 'test_gxp_audit_log_hash_is_deterministic', 0, 2, 2).
python_function('tests/test_runtime.py', '_free_port', 0, 1, 3).
python_function('tests/test_runtime.py', '_has_module', 1, 2, 2).
python_function('tests/test_runtime.py', 'test_api_boot_and_health', 2, 17, 26).
python_function('tests/test_runtime.py', '_check_web_artifacts', 1, 7, 4).
python_function('tests/test_runtime.py', '_check_mobile_artifacts', 1, 9, 4).
python_function('tests/test_runtime.py', '_check_desktop_artifacts', 1, 10, 5).
python_function('tests/test_runtime.py', '_check_infra_artifacts', 1, 7, 7).
python_function('tests/test_runtime.py', 'test_build_produces_expected_targets', 2, 4, 12).
python_function('tests/test_workspace.py', '_make_doql_project', 8, 9, 3).

% ── Python Classes ───────────────────────────────────────
python_class('doql/cli/commands/doctor/report.py', 'Check').
python_class('doql/cli/commands/doctor/report.py', 'DoctorReport').
python_method('DoctorReport', 'add', 3, 1, 2).
python_method('DoctorReport', 'ok', 0, 3, 1).
python_method('DoctorReport', 'warnings', 0, 3, 1).
python_method('DoctorReport', 'failures', 0, 3, 1).
python_class('doql/cli/commands/workspace/discovery.py', 'DoqlProject').
python_class('doql/cli/context.py', 'BuildContext').
python_class('doql/parsers/css_utils.py', 'CssBlock').
python_class('doql/parsers/css_utils.py', 'ParsedSelector').
python_class('doql/parsers/models.py', 'DoqlParseError').
python_class('doql/parsers/models.py', 'ValidationIssue').
python_class('doql/parsers/models.py', 'EntityField').
python_class('doql/parsers/models.py', 'Entity').
python_class('doql/parsers/models.py', 'DataSource').
python_class('doql/parsers/models.py', 'Template').
python_class('doql/parsers/models.py', 'Document').
python_class('doql/parsers/models.py', 'Report').
python_class('doql/parsers/models.py', 'Database').
python_class('doql/parsers/models.py', 'ApiClient').
python_class('doql/parsers/models.py', 'Webhook').
python_class('doql/parsers/models.py', 'Page').
python_class('doql/parsers/models.py', 'Interface').
python_class('doql/parsers/models.py', 'Integration').
python_class('doql/parsers/models.py', 'WorkflowStep').
python_class('doql/parsers/models.py', 'Workflow').
python_class('doql/parsers/models.py', 'Role').
python_class('doql/parsers/models.py', 'Deploy').
python_class('doql/parsers/models.py', 'Environment').
python_class('doql/parsers/models.py', 'Infrastructure').
python_class('doql/parsers/models.py', 'Ingress').
python_class('doql/parsers/models.py', 'CiConfig').
python_class('doql/parsers/models.py', 'Subproject').
python_class('doql/parsers/models.py', 'DoqlSpec').
python_class('doql/plugins.py', 'Plugin').
python_class('tests/env_manager.py', 'CheckResult').
python_method('CheckResult', 'icon', 0, 2, 0).
python_class('tests/env_manager.py', 'TargetReport').
python_method('TargetReport', 'ok', 0, 4, 1).
python_class('tests/env_manager.py', 'ExampleReport').
python_method('ExampleReport', 'ok', 0, 4, 2).
python_class('tests/playground_e2e.py', '_QuietHandler').
python_method('_QuietHandler', 'log_message', 0, 1, 0).
python_class('tests/test_exporters.py', 'TestYamlExporter').
python_method('TestYamlExporter', 'test_export_basic_fields', 1, 5, 4).
python_method('TestYamlExporter', 'test_export_entities', 1, 7, 2).
python_method('TestYamlExporter', 'test_export_interfaces', 1, 5, 2).
python_method('TestYamlExporter', 'test_export_workflows', 1, 4, 2).
python_method('TestYamlExporter', 'test_export_roles', 1, 3, 2).
python_method('TestYamlExporter', 'test_export_deploy', 1, 2, 1).
python_method('TestYamlExporter', 'test_clean_removes_empty_and_none', 0, 4, 2).
python_class('tests/test_exporters.py', 'TestMarkdownExporter').
python_method('TestMarkdownExporter', 'test_export_has_title', 1, 2, 3).
python_method('TestMarkdownExporter', 'test_export_has_entities', 1, 4, 3).
python_method('TestMarkdownExporter', 'test_export_has_interfaces', 1, 3, 3).
python_method('TestMarkdownExporter', 'test_export_has_workflows', 1, 3, 3).
python_method('TestMarkdownExporter', 'test_export_has_roles', 1, 3, 3).
python_method('TestMarkdownExporter', 'test_export_has_deploy', 1, 2, 3).
python_method('TestMarkdownExporter', 'test_export_minimal_spec', 0, 2, 4).
python_class('tests/test_exporters.py', 'TestCssExporter').
python_method('TestCssExporter', 'test_export_app_block', 1, 4, 3).
python_method('TestCssExporter', 'test_export_entity_block', 1, 6, 3).
python_method('TestCssExporter', 'test_export_interface_and_pages', 1, 4, 3).
python_method('TestCssExporter', 'test_export_workflow', 1, 3, 3).
python_method('TestCssExporter', 'test_export_roles', 1, 3, 3).
python_method('TestCssExporter', 'test_export_deploy_no_duplicate', 1, 2, 4).
python_method('TestCssExporter', 'test_export_less_format', 1, 3, 4).
python_method('TestCssExporter', 'test_export_sass_format', 1, 5, 3).
python_class('tests/test_exporters.py', 'TestYamlImporter').
python_method('TestYamlImporter', 'test_roundtrip_yaml', 1, 8, 5).
python_method('TestYamlImporter', 'test_import_entities', 0, 5, 3).
python_method('TestYamlImporter', 'test_import_interfaces_with_pages', 0, 4, 3).
python_method('TestYamlImporter', 'test_import_workflows', 0, 3, 3).
python_method('TestYamlImporter', 'test_import_roles', 0, 3, 3).
python_method('TestYamlImporter', 'test_import_deploy', 0, 3, 2).
python_method('TestYamlImporter', 'test_import_from_dict', 0, 4, 1).
python_method('TestYamlImporter', 'test_invalid_yaml_root', 0, 1, 2).
python_class('tests/test_workspace.py', 'TestParseDoql').
python_method('TestParseDoql', 'test_extracts_workflows', 0, 2, 1).
python_method('TestParseDoql', 'test_extracts_entities', 0, 2, 1).
python_method('TestParseDoql', 'test_extracts_databases', 0, 2, 1).
python_method('TestParseDoql', 'test_extracts_interfaces', 0, 2, 1).
python_class('tests/test_workspace.py', 'TestDiscoverLocal').
python_method('TestDiscoverLocal', 'test_discovers_doql_projects', 1, 5, 4).
python_method('TestDiscoverLocal', 'test_extracts_doql_metadata', 1, 7, 3).
python_method('TestDiscoverLocal', 'test_respects_max_depth', 1, 3, 3).
python_method('TestDiscoverLocal', 'test_excludes_logs_and_venv', 1, 5, 4).
python_method('TestDiscoverLocal', 'test_does_not_dive_into_project', 1, 4, 2).
python_class('tests/test_workspace.py', 'TestProjectMarkers').
python_method('TestProjectMarkers', 'test_markers_do_not_include_doql_css', 0, 2, 0).
python_method('TestProjectMarkers', 'test_excluded_contains_logs', 0, 4, 0).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────
taskfile_task('', 'Install Python dependencies (editable)').
taskfile_task('', 'Upgrade all outdated Python packages in the active / project venv (including plugins)').
taskfile_task('', 'Run pyqual quality pipeline').
taskfile_task('', 'Run pytest suite').
taskfile_task('', 'Run pyqual with auto-fix').
taskfile_task('', 'Generate pyqual quality report').
taskfile_task('', 'Build wheel + sdist').
taskfile_task('', 'Remove build artefacts').
taskfile_task('', 'Run install, quality check').
taskfile_task('', 'Generate project structure (app.doql.css + app.doql.less)').
taskfile_task('', 'Reverse-engineer doql project structure (CSS only)').
taskfile_task('', 'Export to LESS format').
taskfile_task('', 'Validate app.doql.less syntax').
taskfile_task('', 'Run doql health checks').
taskfile_task('', 'Generate code from app.doql.less').
taskfile_task('', 'Full doql analysis (adopt + validate + doctor)').
taskfile_task('', 'Show available tasks').
taskfile_task('', 'Run quality gates for doql (strict) and redeploy (catching up)').

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-api-integration.testql.toon.yaml', 'api').
testql_scenario('generated-api-smoke.testql.toon.yaml', 'api').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-api-integration.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-api-smoke.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('Taskfile.yml', 'taskfile').
sumd_declared_file('pyqual.yaml', 'pyqual').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('api', '').
sumd_interface('cli', 'click').
sumd_interface('cli', '').
sumd_workflow('install', 'manual').
sumd_workflow_step('install', 1, 'pip install -e plugins/doql-plugin-shared -e plugins/doql-plugin-gxp -e plugins/doql-plugin-iso17025 -e plugins/doql-plugin-fleet -e plugins/doql-plugin-erp -e .[dev]').
sumd_workflow('deps:update', 'manual').
sumd_workflow('quality', 'manual').
sumd_workflow_step('quality', 1, 'pyqual run').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, 'pytest -q').
sumd_workflow('quality:fix', 'manual').
sumd_quality_workflow('quality:fix', 'fix').
sumd_workflow_step('quality:fix', 1, 'pyqual run --fix').
sumd_workflow('quality:report', 'manual').
sumd_quality_workflow('quality:report', 'report').
sumd_workflow_step('quality:report', 1, 'pyqual report').
sumd_workflow('build', 'manual').
sumd_workflow_step('build', 1, 'python -m build').
sumd_workflow('clean', 'manual').
sumd_workflow_step('clean', 1, 'rm -rf build/ dist/ *.egg-info').
sumd_workflow('structure', 'manual').
sumd_workflow('doql:adopt', 'manual').
sumd_workflow('doql:export', 'manual').
sumd_workflow_step('doql:export', 1, 'if [ ! -f "app.doql.css" ]').
sumd_workflow('doql:validate', 'manual').
sumd_workflow('doql:doctor', 'manual').
sumd_workflow('doql:build', 'manual').
sumd_workflow('help', 'manual').
sumd_workflow_step('help', 1, 'task --list').
sumd_workflow('cross-quality', 'manual').
```

## Source Map

*Top 1 modules by symbol density — signatures for LLM orientation.*

### `doql.plugins` (`doql/plugins.py`)

```python
def _discover_entry_points()  # CC=5, fan=8
def _discover_local(project_root)  # CC=8, fan=11
def discover_plugins(project_root)  # CC=1, fan=2
def run_plugins(spec, env_vars, build_dir, project_root)  # CC=4, fan=5
class Plugin:
```

## Call Graph

*461 nodes · 500 edges · 121 modules · CC̄=3.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_prop` *(in doql.exporters.css.helpers)* | 8 | 80 | 6 | **86** |
| `create_parser` *(in doql.cli.main)* | 1 | 1 | 84 | **85** |
| `extract_val` *(in doql.parsers.extractors)* | 6 | 62 | 10 | **72** |
| `_deploy_via_redeploy_api` *(in doql.cli.commands.deploy)* | 12 ⚠ | 1 | 31 | **32** |
| `_convert_indent_to_braces` *(in doql.parsers.css_transformers.indent)* | 9 | 1 | 27 | **28** |
| `_render_app` *(in doql.exporters.css.renderers)* | 9 | 2 | 26 | **28** |
| `_output_table` *(in doql.cli.commands.workspace.analyze)* | 10 ⚠ | 1 | 26 | **27** |
| `cmd_drift` *(in doql.cli.commands.drift)* | 13 ⚠ | 0 | 27 | **27** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/doql
# generated in 0.54s
# nodes: 461 | edges: 500 | modules: 121
# CC̄=3.6

HUBS[20]:
  doql.exporters.css.helpers._prop
    CC=8  in:80  out:6  total:86
  doql.cli.main.create_parser
    CC=1  in:1  out:84  total:85
  doql.parsers.extractors.extract_val
    CC=6  in:62  out:10  total:72
  doql.cli.commands.deploy._deploy_via_redeploy_api
    CC=12  in:1  out:31  total:32
  doql.parsers.css_transformers.indent._convert_indent_to_braces
    CC=9  in:1  out:27  total:28
  doql.exporters.css.renderers._render_app
    CC=9  in:2  out:26  total:28
  doql.cli.commands.workspace.analyze._output_table
    CC=10  in:1  out:26  total:27
  doql.cli.commands.drift.cmd_drift
    CC=13  in:0  out:27  total:27
  doql.cli.build._do_build
    CC=9  in:2  out:25  total:27
  doql.cli.commands.workspace.output._print
    CC=2  in:24  out:3  total:27
  doql.parsers.registry.register
    CC=1  in:26  out:0  total:26
  doql.adopt.scanner.deploy._detect_deployment_indicators
    CC=10  in:1  out:25  total:26
  doql.cli.commands.workspace.list._print_project_table
    CC=5  in:1  out:24  total:25
  doql.cli.build._watch_files
    CC=15  in:1  out:23  total:24
  doql.cli.lockfile.spec_section_hashes
    CC=9  in:2  out:22  total:24
  doql.exporters.css._render_css
    CC=7  in:3  out:20  total:23
  doql.cli.sync.cmd_sync
    CC=6  in:0  out:23  total:23
  doql.cli.commands.init.cmd_init
    CC=8  in:0  out:22  total:22
  doql.cli.build._scan_device_for_build
    CC=9  in:1  out:21  total:22
  doql.exporters.css.renderers._render_data_source
    CC=9  in:1  out:21  total:22

MODULES:
  doql.adopt.device_scanner  [3 funcs]
    _header  CC=1  out:2
    adopt_from_device  CC=4  out:9
    adopt_from_device_to_snapshot  CC=2  out:5
  doql.adopt.emitter  [2 funcs]
    emit_css  CC=1  out:1
    emit_spec  CC=1  out:2
  doql.adopt.scanner  [1 funcs]
    scan_project  CC=1  out:12
  doql.adopt.scanner.databases  [4 funcs]
    _db_from_image  CC=3  out:2
    _db_name  CC=2  out:1
    _scan_compose_databases  CC=5  out:7
    scan_databases  CC=6  out:6
  doql.adopt.scanner.deploy  [9 funcs]
    _apply_deploy_config_flags  CC=3  out:0
    _detect_deployment_indicators  CC=10  out:25
    _detect_rootless  CC=2  out:2
    _determine_deploy_target  CC=8  out:3
    _emit_infrastructure_blocks  CC=4  out:6
    _extract_container_config  CC=5  out:5
    _extract_containers_from_compose  CC=5  out:7
    _is_database_service  CC=2  out:1
    scan_deploy  CC=5  out:7
  doql.adopt.scanner.entities  [10 funcs]
    _classify_bases  CC=3  out:8
    _extract_annotation_fields  CC=5  out:7
    _extract_entities_from_python  CC=9  out:12
    _extract_entities_from_sql  CC=5  out:9
    _extract_fields  CC=8  out:8
    _extract_sql_columns  CC=3  out:7
    _extract_sqlalchemy_fields  CC=3  out:7
    _is_excluded_path  CC=2  out:2
    _is_reserved_sql_keyword  CC=1  out:1
    scan_entities  CC=6  out:8
  doql.adopt.scanner.environments  [6 funcs]
    _assign_ssh_host  CC=4  out:3
    _detect_compose_envs  CC=7  out:4
    _detect_env_files  CC=4  out:6
    _detect_local_env  CC=4  out:4
    _extract_env_refs  CC=7  out:7
    scan_environments  CC=1  out:3
  doql.adopt.scanner.integrations  [1 funcs]
    scan_integrations  CC=4  out:5
  doql.adopt.scanner.interfaces  [1 funcs]
    scan_interfaces  CC=1  out:5
  doql.adopt.scanner.interfaces.api  [7 funcs]
    _detect_api_auth  CC=4  out:2
    _detect_framework_from_any_py  CC=8  out:4
    _detect_framework_from_main_py  CC=6  out:2
    _detect_framework_from_pyproject  CC=5  out:3
    _find_api_main_file  CC=8  out:5
    _has_api_entry_point  CC=7  out:6
    scan_python_api  CC=9  out:9
  doql.adopt.scanner.interfaces.cli  [1 funcs]
    scan_python_cli  CC=14  out:18
  doql.adopt.scanner.interfaces.desktop  [1 funcs]
    scan_desktop  CC=7  out:14
  doql.adopt.scanner.interfaces.mobile  [1 funcs]
    scan_mobile  CC=6  out:11
  doql.adopt.scanner.interfaces.web  [4 funcs]
    _detect_web_framework  CC=11  out:7
    _extract_web_pages  CC=3  out:3
    _scan_pages_dir  CC=9  out:14
    scan_web_frontend  CC=6  out:8
  doql.adopt.scanner.metadata  [8 funcs]
    _extract_authors  CC=6  out:7
    _extract_dependencies  CC=3  out:6
    _extract_keywords  CC=3  out:2
    _extract_urls  CC=1  out:4
    _parse_goal_yaml  CC=4  out:2
    _parse_package_json  CC=1  out:4
    _parse_pyproject  CC=3  out:16
    scan_metadata  CC=6  out:9
  doql.adopt.scanner.roles  [2 funcs]
    _scan_sql_roles  CC=9  out:10
    scan_roles  CC=3  out:5
  doql.adopt.scanner.utils  [8 funcs]
    camel_to_kebab  CC=1  out:5
    find_compose  CC=3  out:1
    find_dockerfiles  CC=5  out:5
    load_yaml  CC=3  out:2
    normalize_python_type  CC=1  out:3
    normalize_sql_type  CC=4  out:3
    normalize_sqlalchemy_type  CC=1  out:2
    snake_to_pascal  CC=2  out:3
  doql.adopt.scanner.workflows  [15 funcs]
    _build_steps_from_body  CC=7  out:8
    _build_taskfile_steps  CC=5  out:6
    _build_workflow_from_task  CC=4  out:4
    _build_workflow_steps  CC=2  out:4
    _create_workflow  CC=2  out:1
    _detect_cli_command_name  CC=6  out:6
    _extract_makefile_workflows  CC=6  out:10
    _extract_python_cli_workflows  CC=3  out:3
    _extract_taskfile_schedule  CC=2  out:2
    _extract_taskfile_workflows  CC=9  out:9
  doql.cli.build  [12 funcs]
    _do_build  CC=9  out:25
    _run_conditional_generator  CC=2  out:3
    _scan_device_for_build  CC=9  out:21
    _watch_files  CC=15  out:23
    cmd_build  CC=8  out:13
    run_core_generators  CC=4  out:5
    run_document_generators  CC=2  out:3
    run_i18n_generators  CC=1  out:1
    run_integration_generators  CC=3  out:2
    run_report_generators  CC=1  out:1
  doql.cli.commands.adopt  [11 funcs]
    _cleanup_empty_output  CC=4  out:3
    _cmd_adopt_from_device  CC=10  out:16
    _cmd_adopt_from_directory  CC=8  out:15
    _cmd_adopt_recursive  CC=7  out:18
    _discover_subprojects  CC=7  out:7
    _print_item  CC=5  out:5
    _print_scan_summary  CC=7  out:19
    _scan_and_emit_subproject  CC=5  out:12
    _validate_output_written  CC=3  out:4
    _write_root_manifest  CC=6  out:7
  doql.cli.commands.deploy  [3 funcs]
    _deploy_via_redeploy_api  CC=12  out:31
    _deploy_via_redeploy_cli  CC=4  out:7
    cmd_deploy  CC=9  out:15
  doql.cli.commands.doctor  [1 funcs]
    cmd_doctor  CC=7  out:21
  doql.cli.commands.doctor.checks  [10 funcs]
    _check_databases  CC=5  out:4
    _check_env  CC=5  out:11
    _check_files  CC=3  out:3
    _check_interfaces  CC=10  out:6
    _check_parse  CC=4  out:5
    _check_tools  CC=4  out:6
    _collect_missing_files  CC=11  out:8
    _collect_required_tools  CC=8  out:6
    _find_missing_env_refs  CC=7  out:4
    _warn_unknown_entity_refs  CC=3  out:1
  doql.cli.commands.doctor.remote  [4 funcs]
    _check_remote  CC=8  out:7
    _check_remote_runtime  CC=4  out:4
    _check_remote_ssh  CC=3  out:4
    _ssh_run  CC=3  out:4
  doql.cli.commands.drift  [1 funcs]
    cmd_drift  CC=13  out:27
  doql.cli.commands.drift.render  [2 funcs]
    _fmt_value  CC=6  out:6
    _render_plain  CC=3  out:7
  doql.cli.commands.export  [1 funcs]
    cmd_export  CC=7  out:13
  doql.cli.commands.import_cmd  [1 funcs]
    cmd_import  CC=7  out:14
  doql.cli.commands.init  [1 funcs]
    cmd_init  CC=8  out:22
  doql.cli.commands.plan  [10 funcs]
    _print_api_clients  CC=3  out:3
    _print_data_sources  CC=3  out:3
    _print_documents  CC=2  out:5
    _print_entities  CC=2  out:4
    _print_file_counts  CC=2  out:6
    _print_header  CC=3  out:3
    _print_interfaces  CC=4  out:2
    _print_summary  CC=4  out:13
    _print_workflows  CC=4  out:3
    cmd_plan  CC=3  out:14
  doql.cli.commands.publish  [4 funcs]
    _extract_changelog_notes  CC=7  out:8
    _publish_github  CC=4  out:6
    _publish_pypi  CC=7  out:12
    cmd_publish  CC=8  out:17
  doql.cli.commands.quadlet  [3 funcs]
    _install_via_redeploy_api  CC=9  out:15
    _install_via_systemctl  CC=8  out:19
    cmd_quadlet  CC=6  out:12
  doql.cli.commands.run  [7 funcs]
    _build_into  CC=6  out:16
    _run_api  CC=3  out:6
    _run_desktop  CC=2  out:5
    _run_target  CC=7  out:9
    _run_web  CC=3  out:7
    _workspace_for_file  CC=1  out:0
    cmd_run  CC=9  out:22
  doql.cli.commands.validate  [2 funcs]
    _print_issues  CC=8  out:4
    cmd_validate  CC=5  out:12
  doql.cli.commands.workspace  [1 funcs]
    cmd_workspace  CC=3  out:5
  doql.cli.commands.workspace.analyze  [6 funcs]
    _analyze_project  CC=3  out:13
    _cmd_analyze  CC=4  out:9
    _cmd_fix  CC=7  out:15
    _cmd_validate  CC=6  out:12
    _output_csv  CC=2  out:9
    _output_table  CC=10  out:26
  doql.cli.commands.workspace.discovery  [2 funcs]
    _discover_local  CC=1  out:4
    _filter_projects  CC=7  out:0
  doql.cli.commands.workspace.list  [2 funcs]
    _cmd_list  CC=5  out:12
    _print_project_table  CC=5  out:24
  doql.cli.commands.workspace.output  [1 funcs]
    _print  CC=2  out:3
  doql.cli.commands.workspace.run  [5 funcs]
    _cmd_run  CC=6  out:13
    _execute_single_project  CC=5  out:9
    _print_dry_run_commands  CC=2  out:1
    _print_run_summary  CC=2  out:1
    _select_run_projects  CC=6  out:3
  doql.cli.context  [4 funcs]
    build_context  CC=3  out:6
    estimate_file_count  CC=5  out:2
    load_spec  CC=1  out:2
    scaffold_from_template  CC=2  out:4
  doql.cli.lockfile  [5 funcs]
    _simple_items_hash  CC=2  out:2
    diff_sections  CC=8  out:0
    read_lockfile  CC=3  out:3
    spec_section_hashes  CC=9  out:22
    write_lockfile  CC=1  out:5
  doql.cli.main  [2 funcs]
    create_parser  CC=1  out:84
    main  CC=1  out:3
  doql.cli.sync  [4 funcs]
    _run_interface_generators  CC=5  out:3
    cmd_sync  CC=6  out:23
    determine_regeneration_set  CC=10  out:18
    run_generators  CC=5  out:5
  doql.drift.detector  [3 funcs]
    detect_drift  CC=3  out:8
    find_intended_file  CC=4  out:2
    parse_intended  CC=3  out:9
  doql.exporters.css  [9 funcs]
    _render_css  CC=7  out:20
    _render_data_layer  CC=4  out:6
    _render_documentation_layer  CC=3  out:4
    _render_infrastructure_layer  CC=4  out:6
    _render_integration_layer  CC=5  out:8
    export_css  CC=1  out:2
    export_css_file  CC=1  out:3
    export_less  CC=1  out:3
    export_sass  CC=1  out:3
  doql.exporters.css.format_convert  [3 funcs]
    _css_to_less  CC=4  out:8
    _css_to_sass  CC=9  out:18
    _unquote_simple_value  CC=8  out:4
  doql.exporters.css.helpers  [3 funcs]
    _field_line  CC=7  out:6
    _indent  CC=2  out:1
    _prop  CC=8  out:6
  doql.exporters.css.renderers  [19 funcs]
    _build_interface_props  CC=10  out:17
    _build_page_props  CC=6  out:12
    _render_api_client  CC=8  out:18
    _render_app  CC=9  out:26
    _render_data_source  CC=9  out:21
    _render_database  CC=5  out:12
    _render_dependencies  CC=3  out:6
    _render_deploy  CC=5  out:11
    _render_document  CC=7  out:20
    _render_entity  CC=4  out:10
  doql.exporters.markdown  [2 funcs]
    export_markdown  CC=1  out:10
    export_markdown_file  CC=1  out:2
  doql.exporters.markdown.sections  [8 funcs]
    _config_section  CC=3  out:4
    _document_section  CC=1  out:1
    _entity_section  CC=5  out:9
    _field_type_str  CC=7  out:7
    _h  CC=1  out:0
    _interface_section  CC=8  out:10
    _report_section  CC=1  out:1
    _workflow_section  CC=9  out:12
  doql.exporters.markdown.writers  [11 funcs]
    _write_data_sources  CC=5  out:7
    _write_deployment  CC=4  out:5
    _write_documents  CC=1  out:1
    _write_entities  CC=1  out:1
    _write_header  CC=3  out:6
    _write_integrations  CC=3  out:4
    _write_interfaces  CC=1  out:1
    _write_reports  CC=1  out:1
    _write_roles  CC=5  out:5
    _write_section  CC=3  out:5
  doql.exporters.yaml_exporter  [3 funcs]
    export_yaml  CC=1  out:2
    export_yaml_file  CC=1  out:2
    spec_to_dict  CC=1  out:2
  doql.generators.api_gen  [5 funcs]
    _write_alembic_files  CC=1  out:8
    _write_api_files  CC=3  out:10
    _write_api_readme  CC=3  out:6
    export_openapi  CC=2  out:2
    generate  CC=2  out:6
  doql.generators.api_gen.alembic  [4 funcs]
    _entity_table_columns  CC=10  out:11
    gen_alembic_env  CC=1  out:0
    gen_alembic_ini  CC=1  out:1
    gen_initial_migration  CC=3  out:12
  doql.generators.api_gen.auth  [1 funcs]
    gen_auth  CC=7  out:5
  doql.generators.api_gen.common  [4 funcs]
    py_default  CC=6  out:1
    py_type  CC=4  out:1
    sa_type  CC=1  out:1
    safe_name  CC=2  out:1
  doql.generators.api_gen.database  [1 funcs]
    gen_database  CC=1  out:2
  doql.generators.api_gen.main  [2 funcs]
    gen_main  CC=1  out:1
    gen_requirements  CC=2  out:1
  doql.generators.api_gen.models  [2 funcs]
    _gen_column_def  CC=10  out:10
    gen_models  CC=7  out:11
  doql.generators.api_gen.routes  [6 funcs]
    _gen_create_route  CC=1  out:0
    _gen_entity_routes  CC=1  out:11
    _gen_get_route  CC=1  out:0
    _gen_list_route  CC=1  out:0
    _gen_update_route  CC=1  out:0
    gen_routes  CC=2  out:3
  doql.generators.api_gen.schemas  [5 funcs]
    _gen_create_schema  CC=6  out:5
    _gen_entity_schemas  CC=1  out:7
    _gen_response_schema  CC=10  out:7
    _gen_update_schema  CC=7  out:4
    gen_schemas  CC=2  out:3
  doql.generators.ci_gen  [3 funcs]
    _gen_github_action  CC=1  out:1
    _gen_gitlab_ci  CC=1  out:2
    generate  CC=7  out:14
  doql.generators.desktop_gen  [1 funcs]
    _gen_package_json  CC=1  out:2
  doql.generators.document_gen  [3 funcs]
    _gen_preview_html  CC=6  out:8
    _gen_render_script  CC=2  out:1
    generate  CC=5  out:11
  doql.generators.i18n_gen  [3 funcs]
    _gen_translations  CC=6  out:8
    _humanize  CC=1  out:3
    generate  CC=4  out:12
  doql.generators.infra_gen  [2 funcs]
    _map_deploy_strategy  CC=1  out:1
    generate  CC=12  out:9
  doql.generators.infra_gen.docker  [1 funcs]
    _gen_docker_compose  CC=8  out:20
  doql.generators.infra_gen.kiosk  [1 funcs]
    _gen_kiosk  CC=1  out:8
  doql.generators.infra_gen.kubernetes  [1 funcs]
    _gen_kubernetes  CC=6  out:19
  doql.generators.infra_gen.migration  [1 funcs]
    _gen_migration_spec  CC=6  out:9
  doql.generators.infra_gen.nginx  [1 funcs]
    _gen_nginx  CC=4  out:9
  doql.generators.infra_gen.quadlet  [1 funcs]
    _gen_quadlet  CC=4  out:18
  doql.generators.infra_gen.terraform  [1 funcs]
    _gen_terraform  CC=1  out:10
  doql.generators.integrations_gen  [7 funcs]
    _gen_api_client  CC=4  out:5
    _gen_webhook_dispatcher  CC=5  out:20
    _generate_api_clients  CC=2  out:3
    _generate_integration_services  CC=8  out:14
    _generate_webhooks  CC=2  out:3
    _setup_services_dir  CC=1  out:2
    generate  CC=6  out:6
  doql.generators.mobile_gen  [4 funcs]
    _gen_icons  CC=3  out:5
    _gen_manifest  CC=1  out:2
    _gen_service_worker  CC=1  out:2
    generate  CC=5  out:21
  doql.generators.report_gen  [2 funcs]
    _gen_report_script  CC=7  out:3
    generate  CC=9  out:12
  doql.generators.utils.codegen  [2 funcs]
    generate_file_from_template  CC=2  out:5
    write_code_block  CC=1  out:3
  doql.generators.vite_gen  [4 funcs]
    _gen_index_html  CC=1  out:4
    _gen_tsconfig  CC=1  out:3
    _gen_vite_config  CC=1  out:7
    generate  CC=1  out:3
  doql.generators.web_gen  [8 funcs]
    _setup_web_directories  CC=2  out:1
    _write_component_files  CC=1  out:3
    _write_config_files  CC=2  out:9
    _write_core_files  CC=1  out:9
    _write_page_files  CC=2  out:6
    _write_pwa_files  CC=3  out:9
    _write_readme  CC=3  out:3
    generate  CC=6  out:10
  doql.generators.web_gen.components  [1 funcs]
    _gen_layout  CC=2  out:5
  doql.generators.web_gen.config  [2 funcs]
    _gen_postcss_config  CC=1  out:1
    _gen_tailwind_config  CC=1  out:1
  doql.generators.web_gen.core  [3 funcs]
    _gen_api_ts  CC=1  out:1
    _gen_index_css  CC=1  out:1
    _gen_main_tsx  CC=1  out:1
  doql.generators.web_gen.pages  [4 funcs]
    _build_interface_body  CC=4  out:4
    _field_input  CC=7  out:0
    _gen_dashboard  CC=3  out:8
    _gen_entity_page  CC=10  out:9
  doql.generators.web_gen.pwa  [1 funcs]
    _gen_sw_register  CC=1  out:1
  doql.generators.web_gen.router  [1 funcs]
    _gen_app  CC=3  out:9
  doql.generators.workflow_gen  [7 funcs]
    _extract_cron  CC=4  out:3
    _gen_engine  CC=1  out:1
    _gen_init  CC=2  out:5
    _gen_scheduler  CC=8  out:5
    _gen_workflow_module  CC=7  out:11
    _step_fn_name  CC=1  out:6
    generate  CC=3  out:16
  doql.importers.yaml_importer  [11 funcs]
    _build_entity  CC=2  out:5
    _build_entity_field  CC=1  out:8
    _build_interface  CC=2  out:10
    _build_page  CC=1  out:5
    _build_workflow  CC=2  out:6
    _build_workflow_step  CC=1  out:3
    _import_collection  CC=2  out:4
    _import_metadata  CC=1  out:5
    import_yaml  CC=3  out:15
    import_yaml_file  CC=1  out:2
  doql.integrations.op3_bridge  [1 funcs]
    snapshot_to_less  CC=1  out:2
  doql.parsers  [4 funcs]
    _is_css_format  CC=2  out:3
    detect_doql_file  CC=3  out:1
    parse_file  CC=3  out:6
    parse_text  CC=3  out:6
  doql.parsers.blocks  [2 funcs]
    apply_block  CC=2  out:3
    split_blocks  CC=4  out:15
  doql.parsers.css_mappers  [1 funcs]
    _map_project  CC=5  out:10
  doql.parsers.css_mappers.config  [3 funcs]
    _map_config_block  CC=4  out:9
    _map_document  CC=1  out:1
    _map_template  CC=1  out:1
  doql.parsers.css_mappers.interface  [1 funcs]
    _map_interface  CC=4  out:6
  doql.parsers.css_mappers.workflow  [5 funcs]
    _append_child_steps  CC=4  out:9
    _append_inline_steps  CC=3  out:5
    _map_role  CC=2  out:5
    _map_workflow  CC=6  out:11
    _parse_step_text  CC=6  out:9
  doql.parsers.css_parser  [5 funcs]
    _apply_css_block  CC=8  out:14
    _detect_format  CC=3  out:3
    _map_to_spec  CC=3  out:5
    parse_css_file  CC=2  out:5
    parse_css_text  CC=3  out:6
  doql.parsers.css_tokenizer  [5 funcs]
    _consume_pending  CC=1  out:3
    _make_css_block  CC=2  out:3
    _parse_declarations  CC=11  out:12
    _process_decl_line  CC=7  out:11
    _tokenise_css  CC=9  out:7
  doql.parsers.css_transformers  [1 funcs]
    _sass_to_css  CC=1  out:6
  doql.parsers.css_transformers.indent  [1 funcs]
    _convert_indent_to_braces  CC=9  out:27
  doql.parsers.css_transformers.mixins  [2 funcs]
    _expand_includes  CC=5  out:7
    _extract_mixins  CC=6  out:8
  doql.parsers.css_transformers.variables  [2 funcs]
    _resolve_less_vars  CC=1  out:1
    _resolve_sass_vars  CC=1  out:1
  doql.parsers.css_utils  [4 funcs]
    _parse_list  CC=3  out:6
    _parse_selector  CC=5  out:9
    _strip_comments  CC=1  out:2
    _strip_quotes  CC=4  out:1
  doql.parsers.extractors  [12 funcs]
    _extract_page_from_format1  CC=5  out:15
    _extract_page_from_format2  CC=6  out:21
    _parse_field_default  CC=2  out:2
    _parse_field_flags  CC=1  out:3
    _parse_field_ref  CC=2  out:2
    _parse_field_type  CC=1  out:1
    _should_skip_line  CC=4  out:1
    collect_env_refs  CC=1  out:3
    extract_entity_fields  CC=5  out:14
    extract_list  CC=4  out:7
  doql.parsers.registry  [7 funcs]
    _handle_app  CC=2  out:4
    _handle_author  CC=3  out:3
    _handle_domain  CC=1  out:2
    _handle_languages  CC=3  out:7
    _handle_version  CC=1  out:2
    get_handler  CC=1  out:1
    register  CC=1  out:0
  doql.utils.clean  [1 funcs]
    _clean  CC=9  out:5
  doql.utils.naming  [3 funcs]
    kebab  CC=1  out:2
    slug  CC=1  out:3
    snake  CC=1  out:4
  playground.app  [5 funcs]
    activateTab  CC=4  out:5
    initial  CC=2  out:1
    key  CC=3  out:2
    name  CC=2  out:1
    updateStats  CC=1  out:1
  playground.doql_build  [6 funcs]
    _build_env  CC=4  out:3
    _collect_parse_errors  CC=3  out:5
    _spec_summary  CC=6  out:0
    _try_generate  CC=2  out:5
    _validate  CC=2  out:3
    build  CC=3  out:10
  playground.pyodide-bridge  [6 funcs]
    _createBuildFunction  CC=2  out:5
    _installDoql  CC=1  out:6
    _loadPyodide  CC=1  out:1
    bootPyodide  CC=3  out:5
    buildFn  CC=1  out:0
    executeBuild  CC=7  out:8
  playground.renderers  [6 funcs]
    escapeHtml  CC=1  out:2
    keys  CC=3  out:2
    renderDiagnostics  CC=3  out:3
    renderEnv  CC=7  out:7
    renderFatal  CC=1  out:1
    renderFiles  CC=2  out:3
  plugins.doql-plugin-erp.doql_plugin_erp  [6 funcs]
    _mapping_module  CC=1  out:1
    _odoo_client_module  CC=1  out:1
    _readme  CC=1  out:1
    _sync_module  CC=1  out:1
    _webhook_module  CC=1  out:1
    generate  CC=2  out:8
  plugins.doql-plugin-fleet.doql_plugin_fleet  [2 funcs]
    _readme  CC=1  out:1
    generate  CC=2  out:9
  plugins.doql-plugin-fleet.doql_plugin_fleet.device_registry  [1 funcs]
    _device_registry_module  CC=1  out:1
  plugins.doql-plugin-fleet.doql_plugin_fleet.metrics  [1 funcs]
    _metrics_module  CC=1  out:1
  plugins.doql-plugin-fleet.doql_plugin_fleet.migration  [1 funcs]
    _migration_module  CC=1  out:1
  plugins.doql-plugin-fleet.doql_plugin_fleet.ota  [1 funcs]
    _ota_module  CC=1  out:1
  plugins.doql-plugin-fleet.doql_plugin_fleet.tenant  [1 funcs]
    _tenant_module  CC=1  out:1
  plugins.doql-plugin-gxp.doql_plugin_gxp  [6 funcs]
    _audit_log_module  CC=1  out:1
    _audit_middleware  CC=1  out:1
    _e_signature_module  CC=1  out:1
    _migration_audit  CC=1  out:1
    _readme  CC=1  out:1
    generate  CC=2  out:8
  plugins.doql-plugin-iso17025.doql_plugin_iso17025  [1 funcs]
    generate  CC=1  out:2
  plugins.doql-plugin-shared.doql_plugin_shared.base  [1 funcs]
    plugin_generate  CC=3  out:6
  plugins.doql-plugin-shared.doql_plugin_shared.readme  [1 funcs]
    generate_readme  CC=3  out:1

EDGES:
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._odoo_client_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._mapping_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._sync_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._webhook_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._readme
  playground.doql_build.build → playground.doql_build._collect_parse_errors
  playground.doql_build.build → playground.doql_build._build_env
  playground.doql_build.build → playground.doql_build._validate
  playground.doql_build.build → playground.doql_build._spec_summary
  playground.doql_build.build → playground.doql_build._try_generate
  playground.pyodide-bridge.executeBuild → playground.pyodide-bridge.buildFn
  playground.pyodide-bridge.bootPyodide → playground.pyodide-bridge._loadPyodide
  playground.pyodide-bridge.bootPyodide → playground.pyodide-bridge._installDoql
  playground.pyodide-bridge.bootPyodide → playground.pyodide-bridge._createBuildFunction
  playground.pyodide-bridge.bootPyodide → playground.pyodide-bridge.executeBuild
  playground.renderers.renderFatal → playground.renderers.escapeHtml
  playground.renderers.renderDiagnostics → playground.renderers.escapeHtml
  playground.renderers.renderEnv → playground.renderers.keys
  playground.renderers.renderFiles → playground.renderers.escapeHtml
  playground.app.name → playground.app.activateTab
  playground.app.initial → playground.app.activateTab
  playground.app.key → playground.app.updateStats
  doql.drift.detector.detect_drift → doql.drift.detector.parse_intended
  doql.drift.detector.detect_drift → doql.adopt.device_scanner.adopt_from_device_to_snapshot
  doql.drift.detector.detect_drift → doql.drift.detector.find_intended_file
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → plugins.doql-plugin-fleet.doql_plugin_fleet.tenant._tenant_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → plugins.doql-plugin-fleet.doql_plugin_fleet.device_registry._device_registry_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → plugins.doql-plugin-fleet.doql_plugin_fleet.metrics._metrics_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → plugins.doql-plugin-fleet.doql_plugin_fleet.ota._ota_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → plugins.doql-plugin-fleet.doql_plugin_fleet.migration._migration_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → plugins.doql-plugin-fleet.doql_plugin_fleet._readme
  doql.cli.lockfile.spec_section_hashes → doql.exporters.markdown.sections._h
  doql.cli.lockfile.spec_section_hashes → doql.cli.lockfile._simple_items_hash
  doql.cli.lockfile.write_lockfile → doql.cli.lockfile.spec_section_hashes
  doql.importers.yaml_importer._build_entity → doql.importers.yaml_importer._build_entity_field
  doql.importers.yaml_importer._build_interface → doql.importers.yaml_importer._build_page
  doql.importers.yaml_importer._build_workflow → doql.importers.yaml_importer._build_workflow_step
  doql.importers.yaml_importer.import_yaml → doql.importers.yaml_importer._import_metadata
  doql.importers.yaml_importer.import_yaml → doql.importers.yaml_importer._import_collection
  doql.importers.yaml_importer.import_yaml_text → doql.importers.yaml_importer.import_yaml
  doql.importers.yaml_importer.import_yaml_file → doql.importers.yaml_importer.import_yaml_text
  doql.cli.commands.validate.cmd_validate → doql.cli.commands.validate._print_issues
  doql.cli.commands.validate.cmd_validate → doql.parsers.detect_doql_file
  doql.cli.commands.init.cmd_init → doql.cli.context.scaffold_from_template
  doql.cli.sync._run_interface_generators → doql.cli.build.should_generate_interface
  doql.cli.sync.run_generators → doql.cli.sync._run_interface_generators
  doql.cli.sync.run_generators → doql.cli.build.run_document_generators
  doql.cli.sync.run_generators → doql.cli.build.run_report_generators
  doql.cli.sync.run_generators → doql.cli.build.run_i18n_generators
  doql.cli.sync.run_generators → doql.cli.build.run_integration_generators
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Api (2)

**`API Integration Tests`**
- `GET /health` → `200`
- `GET /api/v1/status` → `200`
- `POST /api/v1/test` → `201`
- assert `status == ok`
- assert `response_time < 1000`

**`Auto-generated API Smoke Tests`**
- `GET /api/v1/notebooks` → `200`
- `POST /api/v1/notebooks` → `201`
- `GET /api/v1/notes` → `200`
- assert `status < 500`
- assert `response_time < 2000`
- detectors: FastAPIDetector, ConfigEndpointDetector

### Integration (1)

**`Auto-generated from Python Tests`**

## Intent

Declarative OQL — build complete applications from a single .doql file
