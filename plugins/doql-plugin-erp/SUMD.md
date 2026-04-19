# doql-plugin-erp

ERP integration for doql — Odoo XML-RPC client + bidirectional sync adapters

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Intent](#intent)

## Metadata

- **name**: `doql-plugin-erp`
- **version**: `0.1.0`
- **python_requires**: `>=3.10`
- **license**: {'text': 'Apache-2.0'}
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

## Configuration

```yaml
project:
  name: doql-plugin-erp
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
pip install doql-plugin-erp

# development install
pip install -e .[dev]
```

## Intent

ERP integration for doql — Odoo XML-RPC client + bidirectional sync adapters
