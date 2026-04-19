# doql-plugin-iso17025

ISO/IEC 17025:2017 compliance for doql — calibration certificates, traceability, uncertainty budgets

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Intent](#intent)

## Metadata

- **name**: `doql-plugin-iso17025`
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
  name: doql-plugin-iso17025
  version: 0.1.0
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
doql>=0.1.0a1
doql-plugin-shared>=0.1.0
```

## Deployment

```bash markpact:run
pip install doql-plugin-iso17025

# development install
pip install -e .[dev]
```

## Intent

ISO/IEC 17025:2017 compliance for doql — calibration certificates, traceability, uncertainty budgets
