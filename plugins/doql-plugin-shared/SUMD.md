# doql-plugin-shared

Shared utilities for doql plugins

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Code Analysis](#code-analysis)
- [Intent](#intent)

## Metadata

- **name**: `doql-plugin-shared`
- **version**: `0.1.0`
- **python_requires**: `>=3.10`
- **license**: {'text': 'Apache-2.0'}
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, project/(1 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

## Configuration

```yaml
project:
  name: doql-plugin-shared
  version: 0.1.0
  env: local
```

## Deployment

```bash markpact:run
pip install doql-plugin-shared

# development install
pip install -e .[dev]
```

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# doql-plugin-shared | 3f 80L | python:3 | 2026-04-20
# stats: 2 func | 0 cls | 3 mod | CC̄=3.0 | critical:0 | cycles:0
# alerts[5]: CC plugin_generate=3; CC generate_readme=3; fan-out plugin_generate=4; fan-out generate_readme=1
# hotspots[5]: plugin_generate fan=4; generate_readme fan=1
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[3]:
  doql_plugin_shared/__init__.py,12
  doql_plugin_shared/base.py,30
  doql_plugin_shared/readme.py,38
D:
  doql_plugin_shared/__init__.py:
  doql_plugin_shared/base.py:
    e: plugin_generate
    plugin_generate(out;modules;readme_content)
  doql_plugin_shared/readme.py:
    e: generate_readme
    generate_readme(plugin_name;modules;description;usage_extra)
```

## Intent

Shared utilities for doql plugins
