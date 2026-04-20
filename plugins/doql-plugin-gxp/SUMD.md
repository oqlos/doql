# doql-plugin-gxp

21 CFR Part 11 / EU Annex 11 compliance for doql — audit log, e-signatures, immutability

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Code Analysis](#code-analysis)
- [Intent](#intent)

## Metadata

- **name**: `doql-plugin-gxp`
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
  name: doql-plugin-gxp
  version: 0.1.0
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
doql>=0.1.0a1
```

## Deployment

```bash markpact:run
pip install doql-plugin-gxp

# development install
pip install -e .[dev]
```

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# doql-plugin-gxp | 1f 428L | python:1 | 2026-04-20
# stats: 6 func | 0 cls | 1 mod | CC̄=1.2 | critical:0 | cycles:0
# alerts[5]: CC generate=2; CC _audit_log_module=1; CC _e_signature_module=1; CC _audit_middleware=1; CC _migration_audit=1
# hotspots[5]: generate fan=8; _audit_log_module fan=1; _e_signature_module fan=1; _audit_middleware fan=1; _migration_audit fan=1
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[1]:
  doql_plugin_gxp/__init__.py,428
D:
  doql_plugin_gxp/__init__.py:
    e: _audit_log_module,_e_signature_module,_audit_middleware,_migration_audit,_readme,generate
    _audit_log_module()
    _e_signature_module()
    _audit_middleware()
    _migration_audit()
    _readme(spec)
    generate(spec;env_vars;out;project_root)
```

## Intent

21 CFR Part 11 / EU Annex 11 compliance for doql — audit log, e-signatures, immutability
