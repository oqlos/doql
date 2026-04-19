# doql-plugin-iso17025

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
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

## Dependencies

### Runtime

```text markpact:deps python
doql>=0.1.0a1
doql-plugin-shared>=0.1.0
```

## Intent

ISO/IEC 17025:2017 compliance for doql — calibration certificates, traceability, uncertainty budgets
