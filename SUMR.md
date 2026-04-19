# Rodzina OQL — paczka kompletna

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `doql`
- **version**: `0.1.3`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, src(4 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: doql;
  version: 0.1.2;
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="doql"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=pip install -e .[dev];
}

workflow[name="quality"] {
  trigger: manual;
  step-1: run cmd=pyqual run;
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

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
}
```

### Source Modules

- `doql.cli`
- `doql.lsp_server`
- `doql.parser`
- `doql.plugins`

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
# Taskfile.yml — doql project runner
# https://taskfile.dev

version: "3"

vars:
  APP_NAME: doql
  DOQL_OUTPUT: app.doql.less

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
```

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: doql-quality

  metrics:
    cc_max: 15
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
ruff
mypy
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Source Map

*Top 2 modules by symbol density — signatures for LLM orientation.*

### `doql.lsp_server` (`doql/lsp_server.py`)

```python
def _parse_doc(source)  # CC=2, fan=1
def _find_line_col(source, needle)  # CC=2, fan=3
def _diagnostics_for(source, uri)  # CC=4, fan=17
def _word_at(source, position)  # CC=8, fan=3
def _on_text_document_event(ls, uri)  # CC=1, fan=3
def did_open(ls, params)  # CC=1, fan=2
def did_change(ls, params)  # CC=1, fan=2
def did_save(ls, params)  # CC=1, fan=2
def completion(ls, params)  # CC=5, fan=8
def hover(ls, params)  # CC=12, fan=9 ⚠
def definition(ls, params)  # CC=3, fan=14
def document_symbols(ls, params)  # CC=7, fan=10
def main()  # CC=2, fan=5
```

### `doql.plugins` (`doql/plugins.py`)

```python
def _discover_entry_points()  # CC=5, fan=8
def _discover_local(project_root)  # CC=8, fan=11
def discover_plugins(project_root)  # CC=1, fan=2
def run_plugins(spec, env_vars, build_dir, project_root)  # CC=4, fan=5
class Plugin:
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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 125f 14282L | python:117,shell:3,javascript:3,typescript:1 | 2026-04-18
# CC̄=3.7 | critical:3/515 | dups:0 | cycles:0

HEALTH[3]:
  🟡 CC    _extract_python_cli_workflows CC=24 (limit:15)
  🟡 CC    scan_entities CC=16 (limit:15)
  🟡 CC    _map_workflow CC=16 (limit:15)

REFACTOR[1]:
  1. split 3 high-CC methods  (CC>15)

PIPELINES[140]:
  [1] Src [generate]: generate → _tenant_module
      PURITY: 100% pure
  [2] Src [generate]: generate
      PURITY: 100% pure
  [3] Src [generate]: generate → _audit_log_module
      PURITY: 100% pure
  [4] Src [generate]: generate → _odoo_client_module
      PURITY: 100% pure
  [5] Src [generate]: generate → generate_readme
      PURITY: 100% pure

LAYERS:
  doql/                           CC̄=4.0    ←in:4  →out:4
  │ !! workspace                  538L  1C   23m  CC=10     ←0
  │ mobile_gen                 462L  0C    8m  CC=5      ←1
  │ !! css_mappers                399L  0C   19m  CC=16     ←1
  │ lsp_server                 364L  0C   13m  CC=14     ←0
  │ integrations_gen           336L  0C   11m  CC=8      ←0
  │ interfaces                 324L  0C   14m  CC=11     ←1
  │ doctor                     321L  2C   12m  CC=13     ←0
  │ infra_gen                  321L  0C    5m  CC=8      ←0
  │ workflow_gen               315L  0C    7m  CC=11     ←0
  │ renderers                  296L  0C   17m  CC=10     ←1
  │ !! workflows                  275L  0C   10m  CC=24     ←1
  │ css_transformers           268L  0C    8m  CC=12     ←1
  │ yaml_importer              267L  0C   22m  CC=3      ←1
  │ registry                   267L  0C   24m  CC=6      ←1
  │ models                     219L  20C    0m  CC=0.0    ←0
  │ desktop_gen                209L  0C    7m  CC=6      ←1
  │ extractors                 205L  0C   14m  CC=6      ←3
  │ __init__                   200L  0C    8m  CC=6      ←0
  │ document_gen               182L  0C    4m  CC=6      ←0
  │ !! entities                   182L  0C    7m  CC=16     ←1
  │ __init__                   178L  0C    5m  CC=3      ←1
  │ validators                 169L  0C   10m  CC=6      ←0
  │ i18n_gen                   168L  0C    3m  CC=6      ←0
  │ pages                      163L  0C    3m  CC=13     ←1
  │ main                       159L  0C    2m  CC=1      ←0
  │ run                        157L  0C    4m  CC=12     ←0
  │ alembic                    154L  0C    3m  CC=12     ←1
  │ auth                       154L  0C    1m  CC=7      ←1
  │ __init__                   153L  0C    5m  CC=6      ←4
  │ publish                    151L  0C    5m  CC=8      ←0
  │ css_parser                 144L  0C    6m  CC=7      ←2
  │ report_gen                 142L  0C    2m  CC=9      ←0
  │ config                     122L  0C    6m  CC=1      ←1
  │ sections                   121L  0C    8m  CC=9      ←2
  │ css_tokenizer              120L  0C    2m  CC=14     ←1
  │ sync                       119L  0C    3m  CC=11     ←0
  │ plan                       115L  0C   10m  CC=4      ←0
  │ routes                     115L  0C    7m  CC=2      ←1
  │ ci_gen                     112L  0C    2m  CC=1      ←0
  │ pwa                        109L  0C    3m  CC=1      ←1
  │ __init__                   107L  0C    9m  CC=5      ←3
  │ deploy                     107L  0C    8m  CC=5      ←1
  │ writers                    101L  0C   11m  CC=5      ←1
  │ plugins                    101L  1C    4m  CC=8      ←0
  │ utils                      100L  0C    8m  CC=5      ←5
  │ adopt                       93L  0C    5m  CC=7      ←0
  │ lockfile                    88L  0C    4m  CC=12     ←2
  │ environments                86L  0C    6m  CC=7      ←1
  │ common                      84L  0C    5m  CC=6      ←5
  │ schemas                     83L  0C    5m  CC=10     ←1
  │ models                      82L  0C    2m  CC=10     ←1
  │ components                  76L  0C    1m  CC=2      ←1
  │ format_convert              75L  0C    2m  CC=9      ←1
  │ main                        74L  0C    2m  CC=2      ←1
  │ parser                      74L  0C    0m  CC=0.0    ←0
  │ css_utils                   72L  2C    4m  CC=4      ←3
  │ metadata                    68L  0C    4m  CC=6      ←1
  │ codegen                     67L  0C    2m  CC=2      ←0
  │ export                      66L  0C    1m  CC=14     ←0
  │ context                     66L  1C    4m  CC=5      ←6
  │ databases                   58L  0C    2m  CC=14     ←1
  │ __init__                    58L  0C    1m  CC=1      ←1
  │ core                        57L  0C    3m  CC=1      ←1
  │ __init__                    53L  0C    0m  CC=0.0    ←0
  │ blocks                      50L  0C    2m  CC=4      ←1
  │ deploy                      48L  0C    2m  CC=6      ←0
  │ validate                    45L  0C    1m  CC=12     ←0
  │ import_cmd                  45L  0C    1m  CC=7      ←0
  │ init                        43L  0C    1m  CC=8      ←0
  │ router                      43L  0C    1m  CC=3      ←1
  │ database                    41L  0C    1m  CC=1      ←1
  │ __init__                    40L  0C    2m  CC=1      ←1
  │ helpers                     39L  0C    3m  CC=8      ←1
  │ naming                      37L  0C    2m  CC=1      ←0
  │ yaml_exporter               36L  0C    3m  CC=1      ←2
  │ integrations                35L  0C    1m  CC=13     ←1
  │ generate                    34L  0C    1m  CC=9      ←0
  │ query                       31L  0C    1m  CC=7      ←0
  │ roles                       28L  0C    1m  CC=11     ←1
  │ render                      26L  0C    1m  CC=4      ←0
  │ export_ts_sdk               26L  0C    1m  CC=2      ←1
  │ export_postman              25L  0C    1m  CC=2      ←1
  │ docs_gen                    24L  0C    1m  CC=3      ←1
  │ quadlet                     22L  0C    1m  CC=2      ←0
  │ docs                        21L  0C    1m  CC=3      ←0
  │ kiosk                       20L  0C    1m  CC=2      ←0
  │ deploy                      20L  0C    1m  CC=2      ←0
  │ clean                       20L  0C    1m  CC=9      ←1
  │ __init__                    19L  0C    0m  CC=0.0    ←0
  │ css_exporter                16L  0C    0m  CC=0.0    ←0
  │ emitter                     13L  0C    1m  CC=1      ←1
  │ markdown_exporter           12L  0C    0m  CC=0.0    ←0
  │ __init__                    10L  0C    0m  CC=0.0    ←0
  │ __main__                     9L  0C    0m  CC=0.0    ←0
  │ common                       9L  0C    0m  CC=0.0    ←0
  │ __init__                     7L  0C    0m  CC=0.0    ←0
  │ __init__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  playground/                     CC̄=2.2    ←in:0  →out:0
  │ app.js                     212L  0C    9m  CC=5      ←0
  │ pyodide-bridge.js          146L  0C   15m  CC=7      ←0
  │ renderers.js                93L  0C   10m  CC=7      ←0
  │ serve.sh                    15L  0C    0m  CC=0.0    ←0
  │
  vscode-doql/                    CC̄=1.5    ←in:0  →out:0
  │ extension.ts                51L  0C    4m  CC=2      ←0
  │
  plugins/                        CC̄=1.3    ←in:0  →out:0
  │ __init__                   427L  0C    6m  CC=2      ←0
  │ __init__                   357L  0C    6m  CC=2      ←0
  │ certificate                135L  0C    1m  CC=1      ←0
  │ device_registry            130L  0C    1m  CC=1      ←1
  │ uncertainty                126L  0C    1m  CC=1      ←0
  │ metrics                    100L  0C    1m  CC=1      ←1
  │ traceability                93L  0C    1m  CC=1      ←0
  │ __init__                    84L  0C    2m  CC=2      ←0
  │ tenant                      83L  0C    1m  CC=1      ←1
  │ migration                   81L  0C    1m  CC=1      ←1
  │ drift_monitor               78L  0C    1m  CC=1      ←0
  │ migration                   74L  0C    1m  CC=1      ←0
  │ ota                         72L  0C    1m  CC=1      ←1
  │ __init__                    39L  0C    1m  CC=1      ←0
  │ readme                      37L  0C    1m  CC=3      ←1
  │ base                        29L  0C    1m  CC=3      ←1
  │ __init__                    11L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ doql.sh                    195L  0C    1m  CC=0.0    ←0
  │ project.sh                  35L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                                                    doql.cli                doql.exporters                          doql               doql.generators                  doql.parsers                    doql.adopt  plugins.doql-plugin-iso17025    plugins.doql-plugin-shared                doql.importers                    doql.utils
                      doql.cli                            ──                            14                             4                             4                                                           2                                                                                         1                                !! fan-out
                doql.exporters                           ←14                            ──                                                                                                                      ←1                                                                                                                       1  hub
                          doql                            ←4                                                          ──                                                           4                                                                                                                                                      
               doql.generators                            ←4                                                                                        ──                                                                                                                                                                                    
                  doql.parsers                                                                                        ←4                                                          ──                                                                                                                                                      
                    doql.adopt                            ←2                             1                                                                                                                      ──                                                                                                                        
  plugins.doql-plugin-iso17025                                                                                                                                                                                                                ──                             2                                                            
    plugins.doql-plugin-shared                                                                                                                                                                                                                ←2                            ──                                                            
                doql.importers                            ←1                                                                                                                                                                                                                                              ──                              
                    doql.utils                                                          ←1                                                                                                                                                                                                                                              ──
  CYCLES: none
  HUB: doql.exporters/ (fan-in=15)
  SMELL: doql.cli/ fan-out=25 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 12 groups | 122f 13823L | 2026-04-18

SUMMARY:
  files_scanned: 122
  total_lines:   13823
  dup_groups:    12
  dup_fragments: 54
  saved_lines:   757
  scan_ms:       5254

HOTSPOTS[7] (files with most duplication):
  plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py  dup=382L  groups=2  frags=5  (2.8%)
  plugins/doql-plugin-erp/doql_plugin_erp/__init__.py  dup=317L  groups=2  frags=5  (2.3%)
  doql/generators/mobile_gen.py  dup=148L  groups=1  frags=1  (1.1%)
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py  dup=129L  groups=1  frags=1  (0.9%)
  plugins/doql-plugin-fleet/doql_plugin_fleet/device_registry.py  dup=124L  groups=1  frags=1  (0.9%)
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/uncertainty.py  dup=120L  groups=1  frags=1  (0.9%)
  doql/generators/integrations_gen.py  dup=113L  groups=1  frags=3  (0.8%)

DUPLICATES[12] (ranked by impact):
  [ea3eb19d82437e63] !! STRU  gen_alembic_ini  L=40 N=13 saved=480 sim=1.00
      doql/generators/api_gen/alembic.py:13-52  (gen_alembic_ini)
      doql/generators/web_gen/config.py:46-60  (_gen_vite_config)
      doql/generators/web_gen/config.py:63-72  (_gen_tailwind_config)
      doql/generators/web_gen/config.py:75-84  (_gen_postcss_config)
      doql/generators/web_gen/core.py:7-23  (_gen_main_tsx)
      doql/generators/web_gen/core.py:26-32  (_gen_index_css)
      doql/generators/web_gen/core.py:35-57  (_gen_api_ts)
      doql/generators/web_gen/pwa.py:95-109  (_gen_sw_register)
      plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py:7-135  (generate)
      plugins/doql-plugin-iso17025/doql_plugin_iso17025/drift_monitor.py:7-78  (generate)
      plugins/doql-plugin-iso17025/doql_plugin_iso17025/migration.py:7-74  (generate)
      plugins/doql-plugin-iso17025/doql_plugin_iso17025/traceability.py:7-93  (generate)
      plugins/doql-plugin-iso17025/doql_plugin_iso17025/uncertainty.py:7-126  (generate)
  [0b19fbe92436de71] !! STRU  _readme  L=58 N=3 saved=116 sim=1.00
      plugins/doql-plugin-erp/doql_plugin_erp/__init__.py:284-341  (_readme)
      plugins/doql-plugin-fleet/doql_plugin_fleet/__init__.py:24-66  (_readme)
      plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py:369-410  (_readme)
  [8d8164856e051e29] !! STRU  _gen_build_rs  L=6 N=19 saved=108 sim=1.00
      doql/generators/desktop_gen.py:127-132  (_gen_build_rs)
      doql/generators/integrations_gen.py:20-55  (_gen_email_service)
      doql/generators/integrations_gen.py:58-87  (_gen_slack_service)
      doql/generators/integrations_gen.py:90-136  (_gen_storage_service)
      doql/generators/mobile_gen.py:250-397  (_gen_style_css)
      doql/generators/workflow_gen.py:19-120  (_gen_engine)
      plugins/doql-plugin-erp/doql_plugin_erp/__init__.py:17-96  (_odoo_client_module)
      plugins/doql-plugin-erp/doql_plugin_erp/__init__.py:99-158  (_mapping_module)
      plugins/doql-plugin-erp/doql_plugin_erp/__init__.py:161-226  (_sync_module)
      plugins/doql-plugin-erp/doql_plugin_erp/__init__.py:229-281  (_webhook_module)
      plugins/doql-plugin-fleet/doql_plugin_fleet/device_registry.py:7-130  (_device_registry_module)
      plugins/doql-plugin-fleet/doql_plugin_fleet/metrics.py:7-100  (_metrics_module)
      plugins/doql-plugin-fleet/doql_plugin_fleet/migration.py:7-81  (_migration_module)
      plugins/doql-plugin-fleet/doql_plugin_fleet/ota.py:7-72  (_ota_module)
      plugins/doql-plugin-fleet/doql_plugin_fleet/tenant.py:7-83  (_tenant_module)
      plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py:21-130  (_audit_log_module)
      plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py:133-251  (_e_signature_module)
      plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py:254-312  (_audit_middleware)
      plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py:315-366  (_migration_audit)
  [dcc2f8e70f6321a7]   STRU  _render_data_layer  L=10 N=2 saved=10 sim=1.00
      doql/exporters/css/__init__.py:23-32  (_render_data_layer)
      doql/exporters/css/__init__.py:45-54  (_render_infrastructure_layer)
  [5f48ca70777b1005]   STRU  _map_template  L=10 N=2 saved=10 sim=1.00
      doql/parsers/css_mappers.py:141-150  (_map_template)
      doql/parsers/css_mappers.py:153-162  (_map_document)
  [30f08c1670d767e9]   STRU  _document_section  L=7 N=2 saved=7 sim=1.00
      doql/exporters/markdown/sections.py:106-112  (_document_section)
      doql/exporters/markdown/sections.py:115-121  (_report_section)
  [9c0032ea2b7c1d5e]   STRU  run_report_generators  L=3 N=3 saved=6 sim=1.00
      doql/cli/build.py:86-88  (run_report_generators)
      doql/cli/build.py:91-93  (run_i18n_generators)
      doql/cli/build.py:102-104  (run_workflow_generators)
  [785017c94366e6c6]   STRU  _validate_document_templates  L=6 N=2 saved=6 sim=1.00
      doql/parsers/validators.py:91-96  (_validate_document_templates)
      doql/parsers/validators.py:99-104  (_validate_template_files)
  [4e86b74b44179336]   STRU  export_markdown_file  L=4 N=2 saved=4 sim=1.00
      doql/exporters/markdown/__init__.py:37-40  (export_markdown_file)
      doql/exporters/yaml_exporter.py:33-36  (export_yaml_file)
  [1d3025851fd7ce65]   STRU  _parse_field_ref  L=4 N=2 saved=4 sim=1.00
      doql/parsers/extractors.py:158-161  (_parse_field_ref)
      doql/parsers/extractors.py:164-167  (_parse_field_default)
  [563e71404cb3cb69]   STRU  export_less  L=3 N=2 saved=3 sim=1.00
      doql/exporters/css/__init__.py:93-95  (export_less)
      doql/exporters/css/__init__.py:98-100  (export_sass)
  [b1191467b99382f4]   STRU  _resolve_less_vars  L=3 N=2 saved=3 sim=1.00
      doql/parsers/css_transformers.py:45-47  (_resolve_less_vars)
      doql/parsers/css_transformers.py:50-52  (_resolve_sass_vars)

REFACTOR[12] (ranked by priority):
  [1] ◐ extract_function   → utils/gen_alembic_ini.py
      WHY: 13 occurrences of 40-line block across 9 files — saves 480 lines
      FILES: doql/generators/api_gen/alembic.py, doql/generators/web_gen/config.py, doql/generators/web_gen/core.py, doql/generators/web_gen/pwa.py, plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py +4 more
  [2] ◐ extract_module     → plugins/utils/_readme.py
      WHY: 3 occurrences of 58-line block across 3 files — saves 116 lines
      FILES: plugins/doql-plugin-erp/doql_plugin_erp/__init__.py, plugins/doql-plugin-fleet/doql_plugin_fleet/__init__.py, plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py
  [3] ○ extract_function   → utils/_gen_build_rs.py
      WHY: 19 occurrences of 6-line block across 11 files — saves 108 lines
      FILES: doql/generators/desktop_gen.py, doql/generators/integrations_gen.py, doql/generators/mobile_gen.py, doql/generators/workflow_gen.py, plugins/doql-plugin-erp/doql_plugin_erp/__init__.py +6 more
  [4] ○ extract_function   → doql/exporters/css/utils/_render_data_layer.py
      WHY: 2 occurrences of 10-line block across 1 files — saves 10 lines
      FILES: doql/exporters/css/__init__.py
  [5] ○ extract_function   → doql/parsers/utils/_map_template.py
      WHY: 2 occurrences of 10-line block across 1 files — saves 10 lines
      FILES: doql/parsers/css_mappers.py
  [6] ○ extract_function   → doql/exporters/markdown/utils/_document_section.py
      WHY: 2 occurrences of 7-line block across 1 files — saves 7 lines
      FILES: doql/exporters/markdown/sections.py
  [7] ○ extract_function   → doql/cli/utils/run_report_generators.py
      WHY: 3 occurrences of 3-line block across 1 files — saves 6 lines
      FILES: doql/cli/build.py
  [8] ○ extract_function   → doql/parsers/utils/_validate_document_templates.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: doql/parsers/validators.py
  [9] ○ extract_function   → doql/exporters/utils/export_markdown_file.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: doql/exporters/markdown/__init__.py, doql/exporters/yaml_exporter.py
  [10] ○ extract_function   → doql/parsers/utils/_parse_field_ref.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: doql/parsers/extractors.py
  [11] ○ extract_function   → doql/exporters/css/utils/export_less.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: doql/exporters/css/__init__.py
  [12] ○ extract_function   → doql/parsers/utils/_resolve_less_vars.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: doql/parsers/css_transformers.py

QUICK_WINS[6] (low risk, high savings — do first):
  [3] extract_function   saved=108L  → utils/_gen_build_rs.py
      FILES: desktop_gen.py, integrations_gen.py, mobile_gen.py +8
  [4] extract_function   saved=10L  → doql/exporters/css/utils/_render_data_layer.py
      FILES: __init__.py
  [5] extract_function   saved=10L  → doql/parsers/utils/_map_template.py
      FILES: css_mappers.py
  [6] extract_function   saved=7L  → doql/exporters/markdown/utils/_document_section.py
      FILES: sections.py
  [7] extract_function   saved=6L  → doql/cli/utils/run_report_generators.py
      FILES: build.py
  [8] extract_function   saved=6L  → doql/parsers/utils/_validate_document_templates.py
      FILES: validators.py

DEPENDENCY_RISK[2] (duplicates spanning multiple packages):
  gen_alembic_ini  packages=2  files=9
      doql/generators/api_gen/alembic.py
      doql/generators/web_gen/config.py
      doql/generators/web_gen/core.py
      doql/generators/web_gen/pwa.py
      +5 more
  _gen_build_rs  packages=2  files=11
      doql/generators/desktop_gen.py
      doql/generators/integrations_gen.py
      doql/generators/mobile_gen.py
      doql/generators/workflow_gen.py
      +7 more

EFFORT_ESTIMATE (total ≈ 62.8h):
  hard   gen_alembic_ini                     saved=480L  ~2880min
  hard   _readme                             saved=116L  ~348min
  hard   _gen_build_rs                       saved=108L  ~432min
  easy   _render_data_layer                  saved=10L  ~20min
  easy   _map_template                       saved=10L  ~20min
  easy   _document_section                   saved=7L  ~14min
  easy   run_report_generators               saved=6L  ~12min
  easy   _validate_document_templates        saved=6L  ~12min
  easy   export_markdown_file                saved=4L  ~8min
  easy   _parse_field_ref                    saved=4L  ~8min
  ... +2 more (~12min)

METRICS-TARGET:
  dup_groups:  12 → 0
  saved_lines: 757 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 514 func | 107f | 2026-04-18

NEXT[2] (ranked by impact):
  [1] !! SPLIT           doql/cli/commands/workspace.py
      WHY: 538L, 1 classes, max CC=10
      EFFORT: ~4h  IMPACT: 5380

  [2] !  SPLIT-FUNC      _map_workflow  CC=16  fan=20
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 320


RISKS[1]:
  ⚠ Splitting doql/cli/commands/workspace.py may break 23 import paths

METRICS-TARGET:
  CC̄:          3.6 → ≤2.5
  max-CC:      16 → ≤8
  god-modules: 1 → 0
  high-CC(≥15): 1 → ≤0
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=3.7 → now CC̄=3.6
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 302f | 176✓ 12⚠ 3✗ | 2026-04-18

SUMMARY:
  scanned: 302  passed: 176 (58.3%)  warnings: 12  errors: 3  unsupported: 122

WARNINGS[12]{path,score}:
  vscode-doql/src/extension.ts,0.78
    issues[2]{rule,severity,message,line}:
      js.import.resolvable,warning,Module 'vscode' not found,2
      js.import.resolvable,warning,Module 'vscode-languageclient/node' not found,3
  plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py,0.93
    issues[2]{rule,severity,message,line}:
      complexity.lizard_length,warning,_audit_log_module: 110 lines exceeds limit 100,21
      complexity.lizard_length,warning,_e_signature_module: 119 lines exceeds limit 100,133
  tests/env_manager.py,0.93
    issues[4]{rule,severity,message,line}:
      complexity.cyclomatic,warning,check_api has cyclomatic complexity 25 (max: 15),113
      complexity.cyclomatic,warning,check_desktop has cyclomatic complexity 17 (max: 15),268
      complexity.lizard_cc,warning,check_api: CC=26 exceeds limit 15,113
      complexity.lizard_cc,warning,check_desktop: CC=17 exceeds limit 15,268
  tests/test_runtime.py,0.96
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,test_api_boot_and_health has cyclomatic complexity 17 (max: 15),66
      complexity.cyclomatic,warning,test_build_produces_expected_targets has cyclomatic complexity 33 (max: 15),169
  doql/adopt/scanner/entities.py,0.97
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,scan_entities has cyclomatic complexity 16 (max: 15),36
      complexity.lizard_cc,warning,scan_entities: CC=16 exceeds limit 15,36
  doql/generators/mobile_gen.py,0.97
    issues[1]{rule,severity,message,line}:
      complexity.lizard_length,warning,_gen_style_css: 148 lines exceeds limit 100,250
  doql/generators/workflow_gen.py,0.97
    issues[1]{rule,severity,message,line}:
      complexity.lizard_length,warning,_gen_engine: 102 lines exceeds limit 100,19
  doql/parsers/css_mappers.py,0.97
    issues[2]{rule,severity,message,line}:
      complexity.cyclomatic,warning,_map_workflow has cyclomatic complexity 16 (max: 15),279
      complexity.lizard_cc,warning,_map_workflow: CC=16 exceeds limit 15,279
  plugins/doql-plugin-fleet/doql_plugin_fleet/device_registry.py,0.97
    issues[1]{rule,severity,message,line}:
      complexity.lizard_length,warning,_device_registry_module: 124 lines exceeds limit 100,7
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py,0.97
    issues[1]{rule,severity,message,line}:
      complexity.lizard_length,warning,generate: 128 lines exceeds limit 100,7
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/uncertainty.py,0.97
    issues[1]{rule,severity,message,line}:
      complexity.lizard_length,warning,generate: 119 lines exceeds limit 100,7
  tests/test_exporters.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.maintainability,warning,Low maintainability index: 16.5 (threshold: 20),

ERRORS[3]{path,score}:
  doql/adopt/scanner/interfaces.py,0.88
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'tomli' not found,80
      python.import.resolvable,error,Module 'tomli' not found,159
  tests/test_lsp.py,0.91
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'lsprotocol' not found,39
  doql/adopt/scanner/metadata.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'tomli' not found,36

UNSUPPORTED[4]{bucket,count}:
  *.md,41
  *.txt,1
  *.yml,16
  other,64
```

## Intent

Declarative OQL — build complete applications from a single .doql file
