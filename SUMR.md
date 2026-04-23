# Rodzina OQL — paczka kompletna

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `doql`
- **version**: `1.0.24`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, src(4 mod), project/(6 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: doql;
  version: 1.0.24;
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
pytest-cov>=4.0
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
def _find_line_col(source, needle)  # CC=3, fan=3
def _diagnostics_for(source, uri)  # CC=10, fan=17 ⚠
def _word_at(source, position)  # CC=8, fan=3
def _on_text_document_event(ls, uri)  # CC=1, fan=3
def did_open(ls, params)  # CC=1, fan=2
def did_change(ls, params)  # CC=1, fan=2
def did_save(ls, params)  # CC=1, fan=2
def completion(ls, params)  # CC=5, fan=8
def _hover_field(ent, f)  # CC=5, fan=5
def _hover_entity(spec, word)  # CC=7, fan=5
def hover(ls, params)  # CC=5, fan=6
def definition(ls, params)  # CC=3, fan=14
def document_symbols(ls, params)  # CC=8, fan=10
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

## Call Graph

*528 nodes · 500 edges · 71 modules · CC̄=1.1*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `create_parser` *(in doql.cli.main)* | 1 | 1 | 83 | **84** |
| `_prop` *(in SUMD)* | 0 | 80 | 0 | **80** |
| `extract_val` *(in SUMD)* | 0 | 55 | 0 | **55** |
| `_cmd_adopt_recursive` *(in doql.cli.commands.adopt)* | 15 ⚠ | 1 | 35 | **36** |
| `_render_project` *(in doql.exporters.css.renderers)* | 21 ⚠ | 1 | 35 | **36** |
| `_parse_pyproject` *(in doql.adopt.scanner.metadata)* | 15 ⚠ | 1 | 33 | **34** |
| `_deploy_via_redeploy_api` *(in doql.cli.commands.deploy)* | 12 ⚠ | 1 | 31 | **32** |
| `_render_rich` *(in doql.cli.commands.drift)* | 7 | 1 | 29 | **30** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/doql
# nodes: 528 | edges: 500 | modules: 71
# CC̄=1.1

HUBS[20]:
  doql.cli.main.create_parser
    CC=1  in:1  out:83  total:84
  SUMD._prop
    CC=0  in:80  out:0  total:80
  SUMD.extract_val
    CC=0  in:55  out:0  total:55
  doql.cli.commands.adopt._cmd_adopt_recursive
    CC=15  in:1  out:35  total:36
  doql.exporters.css.renderers._render_project
    CC=21  in:1  out:35  total:36
  doql.adopt.scanner.metadata._parse_pyproject
    CC=15  in:1  out:33  total:34
  doql.cli.commands.deploy._deploy_via_redeploy_api
    CC=12  in:1  out:31  total:32
  doql.cli.commands.drift._render_rich
    CC=7  in:1  out:29  total:30
  doql.parsers.css_transformers._convert_indent_to_braces
    CC=9  in:1  out:27  total:28
  doql.cli.commands.workspace._print
    CC=2  in:24  out:3  total:27
  doql.cli.commands.workspace._output_table
    CC=10  in:1  out:26  total:27
  doql.exporters.css.renderers._render_app
    CC=9  in:1  out:26  total:27
  doql.lsp_server._diagnostics_for
    CC=10  in:1  out:26  total:27
  doql.adopt.scanner.deploy._detect_deployment_indicators
    CC=10  in:1  out:25  total:26
  doql.parsers.registry.register
    CC=1  in:26  out:0  total:26
  doql.cli.commands.workspace._print_project_table
    CC=5  in:1  out:24  total:25
  doql.cli.sync.cmd_sync
    CC=6  in:0  out:23  total:23
  doql.cli.lockfile.spec_section_hashes
    CC=9  in:1  out:22  total:23
  doql.exporters.css._render_css
    CC=7  in:3  out:20  total:23
  doql.parsers.extractors._extract_page_from_format2
    CC=6  in:1  out:21  total:22

MODULES:
  SUMD  [122 funcs]
    _clean  CC=0  out:0
    _css_to_less  CC=0  out:0
    _css_to_sass  CC=0  out:0
    _device_registry_module  CC=0  out:0
    _field_line  CC=0  out:0
    _gen_api_ts  CC=0  out:0
    _gen_app  CC=0  out:0
    _gen_dashboard  CC=0  out:0
    _gen_entity_page  CC=0  out:0
    _gen_index_css  CC=0  out:0
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
  doql.adopt.scanner.interfaces  [15 funcs]
    _detect_api_auth  CC=4  out:2
    _detect_framework_from_any_py  CC=8  out:4
    _detect_framework_from_main_py  CC=6  out:2
    _detect_framework_from_pyproject  CC=5  out:3
    _detect_web_framework  CC=11  out:7
    _extract_web_pages  CC=3  out:3
    _find_api_main_file  CC=8  out:5
    _has_api_entry_point  CC=7  out:6
    _scan_desktop  CC=7  out:14
    _scan_mobile  CC=6  out:11
  doql.adopt.scanner.metadata  [4 funcs]
    _parse_goal_yaml  CC=4  out:2
    _parse_package_json  CC=1  out:4
    _parse_pyproject  CC=15  out:33
    scan_metadata  CC=6  out:9
  doql.adopt.scanner.roles  [2 funcs]
    _scan_sql_roles  CC=9  out:10
    scan_roles  CC=3  out:5
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
  doql.cli.commands.adopt  [8 funcs]
    _cmd_adopt_from_device  CC=10  out:16
    _cmd_adopt_from_directory  CC=8  out:15
    _cmd_adopt_recursive  CC=15  out:35
    _discover_subprojects  CC=7  out:7
    _print_item  CC=5  out:5
    _print_scan_summary  CC=7  out:19
    _validate_output_written  CC=3  out:4
    cmd_adopt  CC=3  out:5
  doql.cli.commands.deploy  [3 funcs]
    _deploy_via_redeploy_api  CC=12  out:31
    _deploy_via_redeploy_cli  CC=4  out:7
    cmd_deploy  CC=9  out:15
  doql.cli.commands.doctor  [15 funcs]
    _check_databases  CC=5  out:4
    _check_env  CC=5  out:11
    _check_files  CC=3  out:3
    _check_interfaces  CC=10  out:6
    _check_parse  CC=4  out:5
    _check_remote  CC=8  out:7
    _check_remote_runtime  CC=4  out:4
    _check_remote_ssh  CC=3  out:4
    _check_tools  CC=4  out:6
    _collect_missing_files  CC=11  out:8
  doql.cli.commands.drift  [5 funcs]
    _fmt_value  CC=6  out:6
    _render_plain  CC=3  out:7
    _render_rich  CC=7  out:29
    _report_to_json  CC=2  out:1
    cmd_drift  CC=12  out:22
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
  doql.cli.commands.publish  [2 funcs]
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
  doql.cli.commands.workspace  [21 funcs]
    _analyze_project  CC=3  out:13
    _cmd_analyze  CC=4  out:9
    _cmd_fix  CC=7  out:15
    _cmd_list  CC=5  out:12
    _cmd_run  CC=6  out:13
    _cmd_validate  CC=6  out:12
    _discover_local  CC=1  out:4
    _execute_single_project  CC=5  out:9
    _filter_projects  CC=7  out:0
    _is_project  CC=2  out:2
  doql.cli.context  [1 funcs]
    build_context  CC=3  out:6
  doql.cli.lockfile  [3 funcs]
    _simple_items_hash  CC=2  out:2
    spec_section_hashes  CC=9  out:22
    write_lockfile  CC=1  out:5
  doql.cli.main  [2 funcs]
    create_parser  CC=1  out:83
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
  doql.exporters.css  [8 funcs]
    _render_css  CC=7  out:20
    _render_data_layer  CC=4  out:6
    _render_documentation_layer  CC=3  out:4
    _render_infrastructure_layer  CC=4  out:6
    _render_integration_layer  CC=5  out:8
    export_css  CC=1  out:2
    export_less  CC=1  out:3
    export_sass  CC=1  out:3
  doql.exporters.css.format_convert  [2 funcs]
    _css_to_less  CC=4  out:8
    _unquote_simple_value  CC=8  out:4
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
  doql.generators.api_gen.alembic  [2 funcs]
    _entity_table_columns  CC=10  out:11
    gen_initial_migration  CC=3  out:12
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
    _gen_gitlab_ci  CC=1  out:4
    generate  CC=7  out:14
  doql.generators.document_gen  [3 funcs]
    _gen_preview_html  CC=6  out:8
    _gen_render_script  CC=2  out:1
    generate  CC=5  out:11
  doql.generators.i18n_gen  [3 funcs]
    _gen_translations  CC=6  out:8
    _humanize  CC=1  out:3
    generate  CC=4  out:12
  doql.generators.infra_gen  [10 funcs]
    _gen_docker_compose  CC=8  out:20
    _gen_kiosk  CC=1  out:8
    _gen_kubernetes  CC=6  out:19
    _gen_migration_spec  CC=6  out:9
    _gen_nginx  CC=4  out:9
    _gen_quadlet  CC=4  out:18
    _gen_terraform  CC=1  out:10
    _map_deploy_strategy  CC=1  out:1
    _slug  CC=1  out:3
    generate  CC=12  out:9
  doql.generators.integrations_gen  [7 funcs]
    _gen_api_client  CC=4  out:5
    _gen_webhook_dispatcher  CC=5  out:20
    _generate_api_clients  CC=2  out:3
    _generate_integration_services  CC=8  out:14
    _generate_webhooks  CC=2  out:3
    _setup_services_dir  CC=1  out:2
    generate  CC=6  out:6
  doql.generators.mobile_gen  [5 funcs]
    _gen_icons  CC=3  out:5
    _gen_manifest  CC=1  out:2
    _gen_service_worker  CC=1  out:2
    _slug  CC=2  out:3
    generate  CC=5  out:21
  doql.generators.report_gen  [2 funcs]
    _gen_report_script  CC=7  out:3
    generate  CC=9  out:12
  doql.generators.utils.codegen  [2 funcs]
    generate_file_from_template  CC=2  out:5
    write_code_block  CC=1  out:3
  doql.generators.vite_gen  [5 funcs]
    _gen_index_html  CC=1  out:4
    _gen_tsconfig  CC=1  out:3
    _gen_vite_config  CC=1  out:7
    _slug  CC=1  out:3
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
  doql.generators.web_gen.pages  [3 funcs]
    _build_interface_body  CC=4  out:4
    _field_input  CC=7  out:0
    _gen_entity_page  CC=10  out:9
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
  doql.lsp_server  [14 funcs]
    _diagnostics_for  CC=10  out:26
    _find_line_col  CC=3  out:3
    _hover_entity  CC=7  out:5
    _hover_field  CC=5  out:8
    _on_text_document_event  CC=1  out:3
    _parse_doc  CC=2  out:1
    _word_at  CC=8  out:5
    completion  CC=5  out:12
    definition  CC=3  out:15
    did_change  CC=1  out:2
  doql.parsers.blocks  [1 funcs]
    apply_block  CC=2  out:3
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
  doql.parsers.css_transformers  [14 funcs]
    _close_indent_blocks  CC=3  out:3
    _convert_indent_to_braces  CC=9  out:27
    _expand_includes  CC=5  out:7
    _extract_mixins  CC=6  out:8
    _find_step_block_end  CC=7  out:10
    _has_bracket_selector  CC=4  out:3
    _is_doql_property_decl  CC=1  out:3
    _is_selector_line  CC=11  out:11
    _is_selector_starter  CC=8  out:9
    _is_step_line  CC=1  out:2
  doql.parsers.extractors  [11 funcs]
    _extract_page_from_format1  CC=5  out:15
    _extract_page_from_format2  CC=6  out:21
    _parse_field_default  CC=2  out:2
    _parse_field_flags  CC=1  out:3
    _parse_field_ref  CC=2  out:2
    _parse_field_type  CC=1  out:1
    _should_skip_line  CC=4  out:1
    extract_entity_fields  CC=5  out:14
    extract_list  CC=4  out:7
    extract_pages  CC=2  out:2
  doql.parsers.registry  [13 funcs]
    _handle_app  CC=2  out:4
    _handle_author  CC=3  out:3
    _handle_data  CC=2  out:14
    _handle_database  CC=2  out:10
    _handle_default_language  CC=1  out:2
    _handle_document  CC=4  out:11
    _handle_domain  CC=1  out:2
    _handle_entity  CC=1  out:8
    _handle_languages  CC=3  out:7
    _handle_report  CC=2  out:9
  doql.plugins  [4 funcs]
    _discover_entry_points  CC=5  out:9
    _discover_local  CC=8  out:12
    discover_plugins  CC=1  out:2
    run_plugins  CC=4  out:8
  doql.utils.naming  [2 funcs]
    kebab  CC=1  out:2
    snake  CC=1  out:4
  playground.app  [5 funcs]
    activateTab  CC=4  out:5
    initial  CC=2  out:1
    key  CC=3  out:2
    name  CC=2  out:1
    updateStats  CC=1  out:1
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
  plugins.doql-plugin-gxp.doql_plugin_gxp  [6 funcs]
    _audit_log_module  CC=1  out:1
    _audit_middleware  CC=1  out:1
    _e_signature_module  CC=1  out:1
    _migration_audit  CC=1  out:1
    _readme  CC=1  out:1
    generate  CC=2  out:8
  plugins.doql-plugin-iso17025.doql_plugin_iso17025  [1 funcs]
    generate  CC=1  out:2

EDGES:
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._tenant_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._device_registry_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._metrics_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._ota_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._migration_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → plugins.doql-plugin-fleet.doql_plugin_fleet._readme
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._audit_log_module
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._e_signature_module
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._audit_middleware
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._migration_audit
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._readme
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._odoo_client_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._mapping_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._sync_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._webhook_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._readme
  plugins.doql-plugin-iso17025.doql_plugin_iso17025.generate → SUMD.generate_readme
  plugins.doql-plugin-iso17025.doql_plugin_iso17025.generate → SUMD.plugin_generate
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
  doql.plugins.discover_plugins → doql.plugins._discover_entry_points
  doql.plugins.discover_plugins → doql.plugins._discover_local
  doql.plugins.run_plugins → doql.plugins.discover_plugins
  doql.lsp_server._diagnostics_for → doql.lsp_server._parse_doc
  doql.lsp_server._on_text_document_event → doql.lsp_server._diagnostics_for
  doql.lsp_server.did_open → doql.lsp_server._on_text_document_event
  doql.lsp_server.did_change → doql.lsp_server._on_text_document_event
  doql.lsp_server.did_save → doql.lsp_server._on_text_document_event
  doql.lsp_server.completion → doql.lsp_server._parse_doc
  doql.lsp_server._hover_entity → doql.lsp_server._hover_field
  doql.lsp_server.hover → doql.lsp_server._word_at
  doql.lsp_server.hover → doql.lsp_server._parse_doc
  doql.lsp_server.hover → doql.lsp_server._hover_entity
  doql.lsp_server.definition → doql.lsp_server._word_at
  doql.lsp_server.document_symbols → doql.lsp_server._parse_doc
  doql.lsp_server.document_symbols → doql.lsp_server._find_line_col
  doql.drift.detector.detect_drift → doql.drift.detector.parse_intended
  doql.drift.detector.detect_drift → SUMD.adopt_from_device_to_snapshot
  doql.drift.detector.detect_drift → doql.drift.detector.find_intended_file
  doql.importers.yaml_importer._build_entity → doql.importers.yaml_importer._build_entity_field
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

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/doql
# nodes: 528 | edges: 500 | modules: 71
# CC̄=1.1

HUBS[20]:
  doql.cli.main.create_parser
    CC=1  in:1  out:83  total:84
  SUMD._prop
    CC=0  in:80  out:0  total:80
  SUMD.extract_val
    CC=0  in:55  out:0  total:55
  doql.cli.commands.adopt._cmd_adopt_recursive
    CC=15  in:1  out:35  total:36
  doql.exporters.css.renderers._render_project
    CC=21  in:1  out:35  total:36
  doql.adopt.scanner.metadata._parse_pyproject
    CC=15  in:1  out:33  total:34
  doql.cli.commands.deploy._deploy_via_redeploy_api
    CC=12  in:1  out:31  total:32
  doql.cli.commands.drift._render_rich
    CC=7  in:1  out:29  total:30
  doql.parsers.css_transformers._convert_indent_to_braces
    CC=9  in:1  out:27  total:28
  doql.cli.commands.workspace._print
    CC=2  in:24  out:3  total:27
  doql.cli.commands.workspace._output_table
    CC=10  in:1  out:26  total:27
  doql.exporters.css.renderers._render_app
    CC=9  in:1  out:26  total:27
  doql.lsp_server._diagnostics_for
    CC=10  in:1  out:26  total:27
  doql.adopt.scanner.deploy._detect_deployment_indicators
    CC=10  in:1  out:25  total:26
  doql.parsers.registry.register
    CC=1  in:26  out:0  total:26
  doql.cli.commands.workspace._print_project_table
    CC=5  in:1  out:24  total:25
  doql.cli.sync.cmd_sync
    CC=6  in:0  out:23  total:23
  doql.cli.lockfile.spec_section_hashes
    CC=9  in:1  out:22  total:23
  doql.exporters.css._render_css
    CC=7  in:3  out:20  total:23
  doql.parsers.extractors._extract_page_from_format2
    CC=6  in:1  out:21  total:22

MODULES:
  SUMD  [122 funcs]
    _clean  CC=0  out:0
    _css_to_less  CC=0  out:0
    _css_to_sass  CC=0  out:0
    _device_registry_module  CC=0  out:0
    _field_line  CC=0  out:0
    _gen_api_ts  CC=0  out:0
    _gen_app  CC=0  out:0
    _gen_dashboard  CC=0  out:0
    _gen_entity_page  CC=0  out:0
    _gen_index_css  CC=0  out:0
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
  doql.adopt.scanner.interfaces  [15 funcs]
    _detect_api_auth  CC=4  out:2
    _detect_framework_from_any_py  CC=8  out:4
    _detect_framework_from_main_py  CC=6  out:2
    _detect_framework_from_pyproject  CC=5  out:3
    _detect_web_framework  CC=11  out:7
    _extract_web_pages  CC=3  out:3
    _find_api_main_file  CC=8  out:5
    _has_api_entry_point  CC=7  out:6
    _scan_desktop  CC=7  out:14
    _scan_mobile  CC=6  out:11
  doql.adopt.scanner.metadata  [4 funcs]
    _parse_goal_yaml  CC=4  out:2
    _parse_package_json  CC=1  out:4
    _parse_pyproject  CC=15  out:33
    scan_metadata  CC=6  out:9
  doql.adopt.scanner.roles  [2 funcs]
    _scan_sql_roles  CC=9  out:10
    scan_roles  CC=3  out:5
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
  doql.cli.commands.adopt  [8 funcs]
    _cmd_adopt_from_device  CC=10  out:16
    _cmd_adopt_from_directory  CC=8  out:15
    _cmd_adopt_recursive  CC=15  out:35
    _discover_subprojects  CC=7  out:7
    _print_item  CC=5  out:5
    _print_scan_summary  CC=7  out:19
    _validate_output_written  CC=3  out:4
    cmd_adopt  CC=3  out:5
  doql.cli.commands.deploy  [3 funcs]
    _deploy_via_redeploy_api  CC=12  out:31
    _deploy_via_redeploy_cli  CC=4  out:7
    cmd_deploy  CC=9  out:15
  doql.cli.commands.doctor  [15 funcs]
    _check_databases  CC=5  out:4
    _check_env  CC=5  out:11
    _check_files  CC=3  out:3
    _check_interfaces  CC=10  out:6
    _check_parse  CC=4  out:5
    _check_remote  CC=8  out:7
    _check_remote_runtime  CC=4  out:4
    _check_remote_ssh  CC=3  out:4
    _check_tools  CC=4  out:6
    _collect_missing_files  CC=11  out:8
  doql.cli.commands.drift  [5 funcs]
    _fmt_value  CC=6  out:6
    _render_plain  CC=3  out:7
    _render_rich  CC=7  out:29
    _report_to_json  CC=2  out:1
    cmd_drift  CC=12  out:22
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
  doql.cli.commands.publish  [2 funcs]
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
  doql.cli.commands.workspace  [21 funcs]
    _analyze_project  CC=3  out:13
    _cmd_analyze  CC=4  out:9
    _cmd_fix  CC=7  out:15
    _cmd_list  CC=5  out:12
    _cmd_run  CC=6  out:13
    _cmd_validate  CC=6  out:12
    _discover_local  CC=1  out:4
    _execute_single_project  CC=5  out:9
    _filter_projects  CC=7  out:0
    _is_project  CC=2  out:2
  doql.cli.context  [1 funcs]
    build_context  CC=3  out:6
  doql.cli.lockfile  [3 funcs]
    _simple_items_hash  CC=2  out:2
    spec_section_hashes  CC=9  out:22
    write_lockfile  CC=1  out:5
  doql.cli.main  [2 funcs]
    create_parser  CC=1  out:83
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
  doql.exporters.css  [8 funcs]
    _render_css  CC=7  out:20
    _render_data_layer  CC=4  out:6
    _render_documentation_layer  CC=3  out:4
    _render_infrastructure_layer  CC=4  out:6
    _render_integration_layer  CC=5  out:8
    export_css  CC=1  out:2
    export_less  CC=1  out:3
    export_sass  CC=1  out:3
  doql.exporters.css.format_convert  [2 funcs]
    _css_to_less  CC=4  out:8
    _unquote_simple_value  CC=8  out:4
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
  doql.generators.api_gen.alembic  [2 funcs]
    _entity_table_columns  CC=10  out:11
    gen_initial_migration  CC=3  out:12
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
    _gen_gitlab_ci  CC=1  out:4
    generate  CC=7  out:14
  doql.generators.document_gen  [3 funcs]
    _gen_preview_html  CC=6  out:8
    _gen_render_script  CC=2  out:1
    generate  CC=5  out:11
  doql.generators.i18n_gen  [3 funcs]
    _gen_translations  CC=6  out:8
    _humanize  CC=1  out:3
    generate  CC=4  out:12
  doql.generators.infra_gen  [10 funcs]
    _gen_docker_compose  CC=8  out:20
    _gen_kiosk  CC=1  out:8
    _gen_kubernetes  CC=6  out:19
    _gen_migration_spec  CC=6  out:9
    _gen_nginx  CC=4  out:9
    _gen_quadlet  CC=4  out:18
    _gen_terraform  CC=1  out:10
    _map_deploy_strategy  CC=1  out:1
    _slug  CC=1  out:3
    generate  CC=12  out:9
  doql.generators.integrations_gen  [7 funcs]
    _gen_api_client  CC=4  out:5
    _gen_webhook_dispatcher  CC=5  out:20
    _generate_api_clients  CC=2  out:3
    _generate_integration_services  CC=8  out:14
    _generate_webhooks  CC=2  out:3
    _setup_services_dir  CC=1  out:2
    generate  CC=6  out:6
  doql.generators.mobile_gen  [5 funcs]
    _gen_icons  CC=3  out:5
    _gen_manifest  CC=1  out:2
    _gen_service_worker  CC=1  out:2
    _slug  CC=2  out:3
    generate  CC=5  out:21
  doql.generators.report_gen  [2 funcs]
    _gen_report_script  CC=7  out:3
    generate  CC=9  out:12
  doql.generators.utils.codegen  [2 funcs]
    generate_file_from_template  CC=2  out:5
    write_code_block  CC=1  out:3
  doql.generators.vite_gen  [5 funcs]
    _gen_index_html  CC=1  out:4
    _gen_tsconfig  CC=1  out:3
    _gen_vite_config  CC=1  out:7
    _slug  CC=1  out:3
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
  doql.generators.web_gen.pages  [3 funcs]
    _build_interface_body  CC=4  out:4
    _field_input  CC=7  out:0
    _gen_entity_page  CC=10  out:9
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
  doql.lsp_server  [14 funcs]
    _diagnostics_for  CC=10  out:26
    _find_line_col  CC=3  out:3
    _hover_entity  CC=7  out:5
    _hover_field  CC=5  out:8
    _on_text_document_event  CC=1  out:3
    _parse_doc  CC=2  out:1
    _word_at  CC=8  out:5
    completion  CC=5  out:12
    definition  CC=3  out:15
    did_change  CC=1  out:2
  doql.parsers.blocks  [1 funcs]
    apply_block  CC=2  out:3
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
  doql.parsers.css_transformers  [14 funcs]
    _close_indent_blocks  CC=3  out:3
    _convert_indent_to_braces  CC=9  out:27
    _expand_includes  CC=5  out:7
    _extract_mixins  CC=6  out:8
    _find_step_block_end  CC=7  out:10
    _has_bracket_selector  CC=4  out:3
    _is_doql_property_decl  CC=1  out:3
    _is_selector_line  CC=11  out:11
    _is_selector_starter  CC=8  out:9
    _is_step_line  CC=1  out:2
  doql.parsers.extractors  [11 funcs]
    _extract_page_from_format1  CC=5  out:15
    _extract_page_from_format2  CC=6  out:21
    _parse_field_default  CC=2  out:2
    _parse_field_flags  CC=1  out:3
    _parse_field_ref  CC=2  out:2
    _parse_field_type  CC=1  out:1
    _should_skip_line  CC=4  out:1
    extract_entity_fields  CC=5  out:14
    extract_list  CC=4  out:7
    extract_pages  CC=2  out:2
  doql.parsers.registry  [13 funcs]
    _handle_app  CC=2  out:4
    _handle_author  CC=3  out:3
    _handle_data  CC=2  out:14
    _handle_database  CC=2  out:10
    _handle_default_language  CC=1  out:2
    _handle_document  CC=4  out:11
    _handle_domain  CC=1  out:2
    _handle_entity  CC=1  out:8
    _handle_languages  CC=3  out:7
    _handle_report  CC=2  out:9
  doql.plugins  [4 funcs]
    _discover_entry_points  CC=5  out:9
    _discover_local  CC=8  out:12
    discover_plugins  CC=1  out:2
    run_plugins  CC=4  out:8
  doql.utils.naming  [2 funcs]
    kebab  CC=1  out:2
    snake  CC=1  out:4
  playground.app  [5 funcs]
    activateTab  CC=4  out:5
    initial  CC=2  out:1
    key  CC=3  out:2
    name  CC=2  out:1
    updateStats  CC=1  out:1
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
  plugins.doql-plugin-gxp.doql_plugin_gxp  [6 funcs]
    _audit_log_module  CC=1  out:1
    _audit_middleware  CC=1  out:1
    _e_signature_module  CC=1  out:1
    _migration_audit  CC=1  out:1
    _readme  CC=1  out:1
    generate  CC=2  out:8
  plugins.doql-plugin-iso17025.doql_plugin_iso17025  [1 funcs]
    generate  CC=1  out:2

EDGES:
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._tenant_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._device_registry_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._metrics_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._ota_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → SUMD._migration_module
  plugins.doql-plugin-fleet.doql_plugin_fleet.generate → plugins.doql-plugin-fleet.doql_plugin_fleet._readme
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._audit_log_module
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._e_signature_module
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._audit_middleware
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._migration_audit
  plugins.doql-plugin-gxp.doql_plugin_gxp.generate → plugins.doql-plugin-gxp.doql_plugin_gxp._readme
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._odoo_client_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._mapping_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._sync_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._webhook_module
  plugins.doql-plugin-erp.doql_plugin_erp.generate → plugins.doql-plugin-erp.doql_plugin_erp._readme
  plugins.doql-plugin-iso17025.doql_plugin_iso17025.generate → SUMD.generate_readme
  plugins.doql-plugin-iso17025.doql_plugin_iso17025.generate → SUMD.plugin_generate
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
  doql.plugins.discover_plugins → doql.plugins._discover_entry_points
  doql.plugins.discover_plugins → doql.plugins._discover_local
  doql.plugins.run_plugins → doql.plugins.discover_plugins
  doql.lsp_server._diagnostics_for → doql.lsp_server._parse_doc
  doql.lsp_server._on_text_document_event → doql.lsp_server._diagnostics_for
  doql.lsp_server.did_open → doql.lsp_server._on_text_document_event
  doql.lsp_server.did_change → doql.lsp_server._on_text_document_event
  doql.lsp_server.did_save → doql.lsp_server._on_text_document_event
  doql.lsp_server.completion → doql.lsp_server._parse_doc
  doql.lsp_server._hover_entity → doql.lsp_server._hover_field
  doql.lsp_server.hover → doql.lsp_server._word_at
  doql.lsp_server.hover → doql.lsp_server._parse_doc
  doql.lsp_server.hover → doql.lsp_server._hover_entity
  doql.lsp_server.definition → doql.lsp_server._word_at
  doql.lsp_server.document_symbols → doql.lsp_server._parse_doc
  doql.lsp_server.document_symbols → doql.lsp_server._find_line_col
  doql.drift.detector.detect_drift → doql.drift.detector.parse_intended
  doql.drift.detector.detect_drift → SUMD.adopt_from_device_to_snapshot
  doql.drift.detector.detect_drift → doql.drift.detector.find_intended_file
  doql.importers.yaml_importer._build_entity → doql.importers.yaml_importer._build_entity_field
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 276f 55122L | python:124,md:63,yaml:31,json:15,yml:14,doql:13,toml:6,shell:3,javascript:3,txt:1,typescript:1 | 2026-04-23
# CC̄=1.1 | critical:3/2117 | dups:0 | cycles:0

HEALTH[3]:
  🟡 CC    _cmd_adopt_recursive CC=15 (limit:15)
  🟡 CC    _render_project CC=21 (limit:15)
  🟡 CC    _parse_pyproject CC=15 (limit:15)

REFACTOR[1]:
  1. split 3 high-CC methods  (CC>15)

PIPELINES[253]:
  [1] Src [generate_readme]: generate_readme
      PURITY: 100% pure
  [2] Src [plugin_generate]: plugin_generate
      PURITY: 100% pure
  [3] Src [generate]: generate → _tenant_module
      PURITY: 100% pure
  [4] Src [_metrics_module]: _metrics_module
      PURITY: 100% pure
  [5] Src [_device_registry_module]: _device_registry_module
      PURITY: 100% pure

LAYERS:
  doql/                           CC̄=3.9    ←in:0  →out:4
  │ !! infra_gen                  647L  0C   10m  CC=12     ←0
  │ !! workspace                  544L  1C   25m  CC=10     ←0
  │ !! css_mappers                521L  0C   28m  CC=9      ←0
  │ mobile_gen                 462L  0C    8m  CC=5      ←0
  │ doctor                     407L  2C   20m  CC=11     ←0
  │ lsp_server                 378L  0C   15m  CC=10     ←0
  │ !! renderers                  374L  0C   19m  CC=21     ←1
  │ interfaces                 363L  0C   16m  CC=14     ←0
  │ integrations_gen           336L  0C   11m  CC=8      ←0
  │ registry                   331L  0C   30m  CC=6      ←0
  │ workflow_gen               318L  0C    8m  CC=8      ←0
  │ !! adopt                      269L  0C    9m  CC=15     ←0
  │ models                     269L  24C    0m  CC=0.0    ←0
  │ yaml_importer              267L  0C   22m  CC=3      ←0
  │ workflows                  263L  0C   15m  CC=9      ←0
  │ css_transformers           246L  0C   14m  CC=11     ←0
  │ ci_gen                     240L  0C    4m  CC=7      ←0
  │ drift                      231L  0C    6m  CC=12     ←0
  │ desktop_gen                209L  0C    7m  CC=6      ←0
  │ extractors                 205L  0C   14m  CC=6      ←0
  │ __init__                   200L  0C    8m  CC=6      ←0
  │ validators                 200L  0C   11m  CC=6      ←0
  │ main                       196L  0C    2m  CC=1      ←0
  │ entities                   185L  0C   11m  CC=9      ←0
  │ document_gen               182L  0C    4m  CC=6      ←0
  │ __init__                   178L  0C    5m  CC=3      ←0
  │ i18n_gen                   168L  0C    3m  CC=6      ←0
  │ run                        166L  0C    7m  CC=9      ←0
  │ pages                      166L  0C    4m  CC=10     ←0
  │ auth                       154L  0C    1m  CC=7      ←0
  │ __init__                   154L  0C    5m  CC=6      ←0
  │ alembic                    152L  0C    4m  CC=10     ←0
  │ publish                    151L  0C    5m  CC=8      ←0
  │ deploy                     150L  0C    9m  CC=10     ←0
  │ deploy                     142L  0C    4m  CC=12     ←0
  │ report_gen                 142L  0C    2m  CC=9      ←0
  │ css_parser                 137L  0C    5m  CC=8      ←0
  │ app.doql                   135L  0C    0m  CC=0.0    ←0
  │ device_scanner             132L  0C    3m  CC=4      ←0
  │ css_tokenizer              129L  0C    5m  CC=11     ←0
  │ detector                   125L  0C    4m  CC=4      ←0
  │ vite_gen                   124L  0C    5m  CC=1      ←0
  │ sync                       122L  0C    4m  CC=10     ←0
  │ config                     122L  0C    6m  CC=1      ←0
  │ sections                   121L  0C    8m  CC=9      ←0
  │ plan                       115L  0C   10m  CC=4      ←0
  │ routes                     115L  0C    7m  CC=2      ←0
  │ __init__                   113L  0C    9m  CC=7      ←0
  │ quadlet                    112L  0C    3m  CC=9      ←0
  │ pwa                        109L  0C    3m  CC=1      ←0
  │ !! metadata                   103L  0C    4m  CC=15     ←0
  │ plugins                    101L  1C    4m  CC=8      ←0
  │ writers                    101L  0C   11m  CC=5      ←0
  │ utils                      100L  0C    8m  CC=5      ←0
  │ app.doql                    99L  0C    0m  CC=0.0    ←0
  │ app.doql                    97L  0C    0m  CC=0.0    ←0
  │ __init__                    91L  0C    0m  CC=0.0    ←0
  │ environments                88L  0C    6m  CC=7      ←0
  │ common                      84L  0C    5m  CC=6      ←0
  │ lockfile                    83L  0C    5m  CC=9      ←0
  │ schemas                     83L  0C    5m  CC=10     ←0
  │ models                      82L  0C    2m  CC=10     ←0
  │ components                  76L  0C    1m  CC=2      ←0
  │ main                        74L  0C    2m  CC=2      ←0
  │ css_utils                   74L  2C    4m  CC=5      ←0
  │ op3_bridge                  74L  0C    2m  CC=2      ←0
  │ parser                      74L  0C    0m  CC=0.0    ←0
  │ format_convert              67L  0C    3m  CC=9      ←0
  │ codegen                     67L  0C    2m  CC=2      ←0
  │ context                     66L  1C    4m  CC=5      ←0
  │ databases                   62L  0C    4m  CC=6      ←0
  │ export                      58L  0C    1m  CC=7      ←0
  │ __init__                    58L  0C    1m  CC=1      ←0
  │ core                        57L  0C    3m  CC=1      ←0
  │ __init__                    55L  0C    0m  CC=0.0    ←0
  │ blocks                      51L  0C    2m  CC=4      ←0
  │ validate                    48L  0C    2m  CC=8      ←0
  │ import_cmd                  45L  0C    1m  CC=7      ←0
  │ init                        43L  0C    1m  CC=8      ←0
  │ router                      43L  0C    1m  CC=3      ←0
  │ database                    41L  0C    1m  CC=1      ←0
  │ __init__                    40L  0C    2m  CC=1      ←0
  │ helpers                     39L  0C    3m  CC=8      ←0
  │ naming                      37L  0C    2m  CC=1      ←0
  │ yaml_exporter               36L  0C    3m  CC=1      ←0
  │ app.doql                    35L  0C    0m  CC=0.0    ←0
  │ generate                    34L  0C    1m  CC=9      ←0
  │ roles                       32L  0C    2m  CC=9      ←0
  │ query                       31L  0C    1m  CC=7      ←0
  │ render                      26L  0C    1m  CC=4      ←0
  │ export_ts_sdk               26L  0C    1m  CC=2      ←0
  │ integrations                26L  0C    1m  CC=4      ←0
  │ export_postman              25L  0C    1m  CC=2      ←0
  │ docs_gen                    24L  0C    1m  CC=3      ←1
  │ __init__                    22L  0C    0m  CC=0.0    ←0
  │ docs                        21L  0C    1m  CC=3      ←0
  │ kiosk                       20L  0C    1m  CC=2      ←0
  │ deploy                      20L  0C    1m  CC=2      ←0
  │ clean                       20L  0C    1m  CC=9      ←0
  │ __init__                    20L  0C    0m  CC=0.0    ←0
  │ __init__                    19L  0C    0m  CC=0.0    ←0
  │ emitter                     18L  0C    2m  CC=1      ←0
  │ css_exporter                16L  0C    0m  CC=0.0    ←0
  │ markdown_exporter           12L  0C    0m  CC=0.0    ←0
  │ __init__                    10L  0C    0m  CC=0.0    ←0
  │ __main__                     9L  0C    0m  CC=0.0    ←0
  │ common                       9L  0C    0m  CC=0.0    ←0
  │ __init__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  playground/                     CC̄=2.1    ←in:0  →out:0
  │ app.js                     212L  0C    9m  CC=5      ←0
  │ pyodide-bridge.js          146L  0C   15m  CC=7      ←0
  │ renderers.js                93L  0C   10m  CC=7      ←0
  │ README.md                   67L  0C    1m  CC=0.0    ←0
  │ serve.sh                    15L  0C    0m  CC=0.0    ←0
  │
  vscode-doql/                    CC̄=1.5    ←in:0  →out:0
  │ SUMD.md                    183L  0C    0m  CC=0.0    ←0
  │ SUMR.md                    122L  0C    0m  CC=0.0    ←0
  │ package.json               101L  0C    0m  CC=0.0    ←0
  │ doql-css.tmLanguage.json    79L  0C    0m  CC=0.0    ←0
  │ doql.tmLanguage.json        64L  0C    0m  CC=0.0    ←0
  │ sumd.json                   60L  0C    0m  CC=0.0    ←0
  │ extension.ts                51L  0C    4m  CC=2      ←0
  │ README.md                   46L  0C    0m  CC=0.0    ←0
  │ language-configuration.json    28L  0C    0m  CC=0.0    ←0
  │ tsconfig.json               12L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml               11L  0C    0m  CC=0.0    ←0
  │
  plugins/                        CC̄=0.5    ←in:0  →out:0
  │ __init__                   427L  0C    6m  CC=2      ←0
  │ __init__                   357L  0C    6m  CC=2      ←0
  │ SUMD.md                    166L  0C    7m  CC=0.0    ←0
  │ SUMD.md                    166L  0C    1m  CC=0.0    ←0
  │ SUMD.md                    150L  0C    6m  CC=0.0    ←0
  │ SUMD.md                    150L  0C    6m  CC=0.0    ←0
  │ SUMD.md                    142L  0C    2m  CC=0.0    ←0
  │ certificate                135L  0C    1m  CC=1      ←0
  │ device_registry            130L  0C    1m  CC=1      ←0
  │ uncertainty                126L  0C    1m  CC=1      ←0
  │ SUMR.md                    110L  0C    0m  CC=0.0    ←0
  │ SUMR.md                    109L  0C    0m  CC=0.0    ←0
  │ SUMR.md                    109L  0C    0m  CC=0.0    ←0
  │ SUMR.md                    109L  0C    0m  CC=0.0    ←0
  │ metrics                    100L  0C    1m  CC=1      ←0
  │ SUMR.md                    100L  0C    0m  CC=0.0    ←0
  │ traceability                93L  0C    1m  CC=1      ←0
  │ __init__                    84L  0C    2m  CC=2      ←0
  │ tenant                      83L  0C    1m  CC=1      ←0
  │ migration                   81L  0C    1m  CC=1      ←0
  │ drift_monitor               78L  0C    1m  CC=1      ←0
  │ migration                   74L  0C    1m  CC=1      ←0
  │ ota                         72L  0C    1m  CC=1      ←0
  │ sumd.json                   60L  0C    0m  CC=0.0    ←0
  │ sumd.json                   60L  0C    0m  CC=0.0    ←0
  │ sumd.json                   60L  0C    0m  CC=0.0    ←0
  │ sumd.json                   60L  0C    0m  CC=0.0    ←0
  │ sumd.json                   48L  0C    0m  CC=0.0    ←0
  │ README.md                   43L  0C    0m  CC=0.0    ←0
  │ __init__                    39L  0C    1m  CC=1      ←0
  │ readme                      37L  0C    1m  CC=3      ←0
  │ map.toon.yaml               34L  0C    7m  CC=0.0    ←0
  │ map.toon.yaml               33L  0C    1m  CC=0.0    ←0
  │ README.md                   33L  0C    0m  CC=0.0    ←0
  │ README.md                   31L  0C    0m  CC=0.0    ←0
  │ base                        29L  0C    1m  CC=3      ←0
  │ README.md                   25L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              25L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              24L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              24L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              24L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              23L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml               19L  0C    2m  CC=0.0    ←0
  │ map.toon.yaml               18L  0C    6m  CC=0.0    ←0
  │ map.toon.yaml               18L  0C    6m  CC=0.0    ←0
  │ __init__                    11L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! SUMD.md                   2464L  1C  705m  CC=0.0    ←42
  │ !! SUMR.md                   2346L  1C   19m  CC=0.0    ←0
  │ !! SPEC.md                    983L  0C    0m  CC=0.0    ←0
  │ !! CHANGELOG.md               876L  0C    1m  CC=0.0    ←0
  │ !! README.md                  597L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ OQLOS-REQUIREMENTS.md      491L  9C   10m  CC=0.0    ←0
  │ PARSER_AUDIT.md            206L  0C    0m  CC=0.0    ←0
  │ doql.sh                    195L  0C    1m  CC=0.0    ←0
  │ TODO.md                    191L  4C   10m  CC=0.0    ←0
  │ GLOSSARY.md                174L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml               168L  0C    0m  CC=0.0    ←0
  │ sumd.json                  162L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             132L  0C    0m  CC=0.0    ←0
  │ ROADMAP.md                 129L  0C    0m  CC=0.0    ←0
  │ test_all_desktop.yml       102L  0C    0m  CC=0.0    ←0
  │ test_playbook.yml           70L  0C    0m  CC=0.0    ←0
  │ pyqual.yaml                 49L  0C    0m  CC=0.0    ←0
  │ Taskfile.testql.yml         47L  0C    0m  CC=0.0    ←0
  │ project.sh                  44L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │ Jenkinsfile                  0L  0C    3m  CC=0.0    ←0
  │
  docs/                           CC̄=0.0    ←in:0  →out:0
  │ !! README.md                 1542L  0C    1m  CC=0.0    ←0
  │ !! context.md                 593L  0C    0m  CC=0.0    ←0
  │ !! context.md                 591L  0C    0m  CC=0.0    ←0
  │ refactoring-plan.md        260L  0C    4m  CC=0.0    ←0
  │ analysis.toon.yaml         184L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         49L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                7042L  0C    0m  CC=0.0    ←0
  │ !! map.toon.yaml             2976L  0C  705m  CC=0.0    ←0
  │ !! calls.toon.yaml            590L  0C    0m  CC=0.0    ←0
  │ !! context.md                 581L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         359L  0C    0m  CC=0.0    ←0
  │ README.md                  339L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml      177L  0C    0m  CC=0.0    ←0
  │ validation.toon.yaml        68L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         66L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           51L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │
  code2llm_output/                CC̄=0.0    ←in:0  →out:0
  │ !! context.md                 595L  0C    0m  CC=0.0    ←0
  │ !! context.md                 589L  0C    0m  CC=0.0    ←0
  │ !! flow.toon.yaml             567L  0C    0m  CC=0.0    ←0
  │ !! flow.toon.yaml             567L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         185L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         49L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         49L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=0.0    ←in:0  →out:0
  │ app.doql                   433L  0C    0m  CC=0.0    ←0
  │ app.doql                   350L  0C    0m  CC=0.0    ←0
  │ README.md                  262L  0C    0m  CC=0.0    ←0
  │ README.md                  262L  0C    0m  CC=0.0    ←0
  │ app.doql                   259L  0C    0m  CC=0.0    ←0
  │ README.md                  228L  0C    0m  CC=0.0    ←0
  │ app.doql                   223L  0C    0m  CC=0.0    ←0
  │ app.doql                   178L  0C    0m  CC=0.0    ←0
  │ SUMD.md                    153L  0C    0m  CC=0.0    ←0
  │ app.doql                   144L  0C    0m  CC=0.0    ←0
  │ app.doql                   131L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml               130L  0C    0m  CC=0.0    ←0
  │ app.doql                   128L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml               100L  0C    0m  CC=0.0    ←0
  │ SUMR.md                     98L  0C    0m  CC=0.0    ←0
  │ README.md                   90L  0C    0m  CC=0.0    ←0
  │ README.md                   89L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml                88L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml                88L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml                88L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml                88L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml                88L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml                88L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml                88L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml                88L  0C    0m  CC=0.0    ←0
  │ README.md                   83L  0C    0m  CC=0.0    ←0
  │ README.md                   82L  0C    0m  CC=0.0    ←0
  │ README.md                   82L  0C    0m  CC=0.0    ←0
  │ README.md                   73L  0C    0m  CC=0.0    ←0
  │ EXAMPLES-TEST-REPORT.md     69L  0C    0m  CC=0.0    ←0
  │ sumd.json                   48L  0C    0m  CC=0.0    ←0
  │ pyqual.yaml                 33L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml               32L  0C    0m  CC=0.0    ←0
  │ organization.json           24L  0C    0m  CC=0.0    ←0
  │ app.doql                    24L  0C    0m  CC=0.0    ←0
  │ customers.json              23L  0C    0m  CC=0.0    ←0
  │ index.md                    16L  0C    0m  CC=0.0    ←0
  │
  TODO/                           CC̄=0.0    ←in:0  →out:0
  │ 03-doql-less-calibration-lab-example.md   317L  0C    0m  CC=0.0    ←0
  │ 04-doql-sass-notes-app-example.md   296L  0C    0m  CC=0.0    ←0
  │ 02-doql-css-iot-fleet-example.md   295L  0C    0m  CC=0.0    ←0
  │ 05-doql-migration-guide.md   261L  0C    0m  CC=0.0    ←0
  │ 01-doql-format-migration-analysis.md   114L  0C    0m  CC=0.0    ←0
  │ README.md                   22L  0C    0m  CC=0.0    ←0
  │
  analysis-20260421/              CC̄=0.0    ←in:0  →out:0
  │ !! context.md                 589L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         184L  0C    0m  CC=0.0    ←0
  │
  analysis/                       CC̄=0.0    ←in:0  →out:0
  │ analysis.toon.yaml         184L  0C    0m  CC=0.0    ←0
  │
  .redeploy/                      CC̄=0.0    ←in:0  →out:0
  │ infra-local-9dd2f59b.yaml    11L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-api-smoke.testql.toon.yaml    31L  0C    0m  CC=0.0    ←0
  │ generated-api-integration.testql.toon.yaml    18L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    13L  0C    0m  CC=0.0    ←0
  │
  articles/                       CC̄=0.0    ←in:0  →out:0
  │ 04-doql-ogloszenie.md      163L  0C    0m  CC=0.0    ←0
  │ 06-doql-v02-dokumenty-kiosk.md   142L  0C    0m  CC=0.0    ←0
  │ 05-wizja-ekosystemu-oqlos.md   141L  0C    0m  CC=0.0    ←0
  │ 02-testql-status-2026-q2.md   109L  0C    0m  CC=0.0    ←0
  │ 03-saas-www-status-2026-q2.md   101L  0C    0m  CC=0.0    ←0
  │ 01-oqlos-status-2026-q2.md    88L  0C    0m  CC=0.0    ←0
  │ README.md                   57L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     Jenkinsfile                               0L

COUPLING:
                                                        SUMD                doql.exporters                  doql.parsers               doql.generators                      doql.cli                    doql.adopt     plugins.doql-plugin-fleet                          doql  plugins.doql-plugin-iso17025                    doql.drift
                          SUMD                            ──                          ←133                           ←86                           ←44                           ←41                           ←23                            ←5                            ←4                            ←2                            ←1  hub
                doql.exporters                           133                            ──                                                                                                                                                                                                                                                  !! fan-out
                  doql.parsers                            86                                                          ──                                                                                                                                                                                                                    !! fan-out
               doql.generators                            44                                                                                        ──                            ←1                                                                                                                                                        !! fan-out
                      doql.cli                            41                                                                                         1                            ──                                                                                                                                                        !! fan-out
                    doql.adopt                            23                                                                                                                                                    ──                                                                                                                          !! fan-out
     plugins.doql-plugin-fleet                             5                                                                                                                                                                                  ──                                                                                          
                          doql                             4                                                                                                                                                                                                                ──                                                            
  plugins.doql-plugin-iso17025                             2                                                                                                                                                                                                                                              ──                              
                    doql.drift                             1                                                                                                                                                                                                                                                                            ──
  CYCLES: none
  HUB: SUMD/ (fan-in=339)
  SMELL: doql.exporters/ fan-out=133 → split needed
  SMELL: doql.adopt/ fan-out=23 → split needed
  SMELL: doql.generators/ fan-out=44 → split needed
  SMELL: doql.cli/ fan-out=42 → split needed
  SMELL: doql.parsers/ fan-out=86 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 13 groups | 129f 16261L | 2026-04-23

SUMMARY:
  files_scanned: 129
  total_lines:   16261
  dup_groups:    13
  dup_fragments: 56
  saved_lines:   847
  scan_ms:       8423

HOTSPOTS[7] (files with most duplication):
  plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py  dup=382L  groups=2  frags=5  (2.3%)
  plugins/doql-plugin-erp/doql_plugin_erp/__init__.py  dup=317L  groups=2  frags=5  (1.9%)
  doql/generators/mobile_gen.py  dup=148L  groups=1  frags=1  (0.9%)
  doql/generators/ci_gen.py  dup=132L  groups=1  frags=2  (0.8%)
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py  dup=129L  groups=1  frags=1  (0.8%)
  plugins/doql-plugin-fleet/doql_plugin_fleet/device_registry.py  dup=124L  groups=1  frags=1  (0.8%)
  plugins/doql-plugin-iso17025/doql_plugin_iso17025/uncertainty.py  dup=120L  groups=1  frags=1  (0.7%)

DUPLICATES[13] (ranked by impact):
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
  [5f642514e6b6222c] ! STRU  _gen_github_action  L=90 N=2 saved=90 sim=1.00
      doql/generators/ci_gen.py:14-103  (_gen_github_action)
      doql/generators/ci_gen.py:171-212  (_gen_jenkinsfile)
  [dcc2f8e70f6321a7]   STRU  _render_data_layer  L=10 N=2 saved=10 sim=1.00
      doql/exporters/css/__init__.py:23-32  (_render_data_layer)
      doql/exporters/css/__init__.py:45-54  (_render_infrastructure_layer)
  [5f48ca70777b1005]   STRU  _map_template  L=10 N=2 saved=10 sim=1.00
      doql/parsers/css_mappers.py:153-162  (_map_template)
      doql/parsers/css_mappers.py:165-174  (_map_document)
  [30f08c1670d767e9]   STRU  _document_section  L=7 N=2 saved=7 sim=1.00
      doql/exporters/markdown/sections.py:106-112  (_document_section)
      doql/exporters/markdown/sections.py:115-121  (_report_section)
  [9c0032ea2b7c1d5e]   STRU  run_report_generators  L=3 N=3 saved=6 sim=1.00
      doql/cli/build.py:88-90  (run_report_generators)
      doql/cli/build.py:93-95  (run_i18n_generators)
      doql/cli/build.py:104-106  (run_workflow_generators)
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
      doql/exporters/css/__init__.py:98-100  (export_less)
      doql/exporters/css/__init__.py:103-105  (export_sass)
  [b1191467b99382f4]   STRU  _resolve_less_vars  L=3 N=2 saved=3 sim=1.00
      doql/parsers/css_transformers.py:45-47  (_resolve_less_vars)
      doql/parsers/css_transformers.py:50-52  (_resolve_sass_vars)

REFACTOR[13] (ranked by priority):
  [1] ◐ extract_function   → utils/gen_alembic_ini.py
      WHY: 13 occurrences of 40-line block across 9 files — saves 480 lines
      FILES: doql/generators/api_gen/alembic.py, doql/generators/web_gen/config.py, doql/generators/web_gen/core.py, doql/generators/web_gen/pwa.py, plugins/doql-plugin-iso17025/doql_plugin_iso17025/certificate.py +4 more
  [2] ◐ extract_module     → plugins/utils/_readme.py
      WHY: 3 occurrences of 58-line block across 3 files — saves 116 lines
      FILES: plugins/doql-plugin-erp/doql_plugin_erp/__init__.py, plugins/doql-plugin-fleet/doql_plugin_fleet/__init__.py, plugins/doql-plugin-gxp/doql_plugin_gxp/__init__.py
  [3] ○ extract_function   → utils/_gen_build_rs.py
      WHY: 19 occurrences of 6-line block across 11 files — saves 108 lines
      FILES: doql/generators/desktop_gen.py, doql/generators/integrations_gen.py, doql/generators/mobile_gen.py, doql/generators/workflow_gen.py, plugins/doql-plugin-erp/doql_plugin_erp/__init__.py +6 more
  [4] ○ extract_module     → doql/generators/utils/_gen_github_action.py
      WHY: 2 occurrences of 90-line block across 1 files — saves 90 lines
      FILES: doql/generators/ci_gen.py
  [5] ○ extract_function   → doql/exporters/css/utils/_render_data_layer.py
      WHY: 2 occurrences of 10-line block across 1 files — saves 10 lines
      FILES: doql/exporters/css/__init__.py
  [6] ○ extract_function   → doql/parsers/utils/_map_template.py
      WHY: 2 occurrences of 10-line block across 1 files — saves 10 lines
      FILES: doql/parsers/css_mappers.py
  [7] ○ extract_function   → doql/exporters/markdown/utils/_document_section.py
      WHY: 2 occurrences of 7-line block across 1 files — saves 7 lines
      FILES: doql/exporters/markdown/sections.py
  [8] ○ extract_function   → doql/cli/utils/run_report_generators.py
      WHY: 3 occurrences of 3-line block across 1 files — saves 6 lines
      FILES: doql/cli/build.py
  [9] ○ extract_function   → doql/parsers/utils/_validate_document_templates.py
      WHY: 2 occurrences of 6-line block across 1 files — saves 6 lines
      FILES: doql/parsers/validators.py
  [10] ○ extract_function   → doql/exporters/utils/export_markdown_file.py
      WHY: 2 occurrences of 4-line block across 2 files — saves 4 lines
      FILES: doql/exporters/markdown/__init__.py, doql/exporters/yaml_exporter.py
  [11] ○ extract_function   → doql/parsers/utils/_parse_field_ref.py
      WHY: 2 occurrences of 4-line block across 1 files — saves 4 lines
      FILES: doql/parsers/extractors.py
  [12] ○ extract_function   → doql/exporters/css/utils/export_less.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: doql/exporters/css/__init__.py
  [13] ○ extract_function   → doql/parsers/utils/_resolve_less_vars.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: doql/parsers/css_transformers.py

QUICK_WINS[7] (low risk, high savings — do first):
  [3] extract_function   saved=108L  → utils/_gen_build_rs.py
      FILES: desktop_gen.py, integrations_gen.py, mobile_gen.py +8
  [4] extract_module     saved=90L  → doql/generators/utils/_gen_github_action.py
      FILES: ci_gen.py
  [5] extract_function   saved=10L  → doql/exporters/css/utils/_render_data_layer.py
      FILES: __init__.py
  [6] extract_function   saved=10L  → doql/parsers/utils/_map_template.py
      FILES: css_mappers.py
  [7] extract_function   saved=7L  → doql/exporters/markdown/utils/_document_section.py
      FILES: sections.py
  [8] extract_function   saved=6L  → doql/cli/utils/run_report_generators.py
      FILES: build.py
  [9] extract_function   saved=6L  → doql/parsers/utils/_validate_document_templates.py
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

EFFORT_ESTIMATE (total ≈ 67.3h):
  hard   gen_alembic_ini                     saved=480L  ~2880min
  hard   _readme                             saved=116L  ~348min
  hard   _gen_build_rs                       saved=108L  ~432min
  hard   _gen_github_action                  saved=90L  ~270min
  easy   _render_data_layer                  saved=10L  ~20min
  easy   _map_template                       saved=10L  ~20min
  easy   _document_section                   saved=7L  ~14min
  easy   run_report_generators               saved=6L  ~12min
  easy   _validate_document_templates        saved=6L  ~12min
  easy   export_markdown_file                saved=4L  ~8min
  ... +3 more (~20min)

METRICS-TARGET:
  dup_groups:  13 → 0
  saved_lines: 847 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 2117 func | 132f | 2026-04-23

NEXT[6] (ranked by impact):
  [1] !! SPLIT           doql/generators/infra_gen.py
      WHY: 647L, 0 classes, max CC=12
      EFFORT: ~4h  IMPACT: 7764

  [2] !! SPLIT           doql/cli/commands/workspace.py
      WHY: 544L, 1 classes, max CC=10
      EFFORT: ~4h  IMPACT: 5440

  [3] !! SPLIT           doql/parsers/css_mappers.py
      WHY: 521L, 0 classes, max CC=9
      EFFORT: ~4h  IMPACT: 4689

  [4] !  SPLIT-FUNC      _render_project  CC=21  fan=18
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 378

  [5] !  SPLIT-FUNC      _cmd_adopt_recursive  CC=15  fan=19
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 285

  [6] !  SPLIT-FUNC      _parse_pyproject  CC=15  fan=11
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 165


RISKS[3]:
  ⚠ Splitting doql/generators/infra_gen.py may break 10 import paths
  ⚠ Splitting doql/cli/commands/workspace.py may break 25 import paths
  ⚠ Splitting doql/parsers/css_mappers.py may break 28 import paths

METRICS-TARGET:
  CC̄:          1.1 → ≤0.8
  max-CC:      21 → ≤10
  god-modules: 3 → 0
  high-CC(≥15): 3 → ≤1
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
  prev CC̄=1.1 → now CC̄=1.1
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
