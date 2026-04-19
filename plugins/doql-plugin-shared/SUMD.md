# doql-plugin-shared

Shared utilities for doql plugins

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Intent](#intent)

## Metadata

- **name**: `doql-plugin-shared`
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

## Intent

Shared utilities for doql plugins
