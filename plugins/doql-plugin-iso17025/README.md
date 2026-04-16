# doql-plugin-iso17025

ISO/IEC 17025:2017 compliance primitives for calibration laboratories — pairs naturally with `doql-plugin-gxp` for regulated labs (pharma/medical devices).

## What it generates

When `doql build` runs, this plugin emits files into `build/plugins/iso17025/`:

- **`traceability.py`** — `ReferenceStandard` model + `TraceabilityChain` helper that walks from a DUT's reference standard back to SI through NMIs. Verifies certificate validity at each link.
- **`uncertainty.py`** — GUM-compliant `UncertaintyBudget` with `UncertaintyComponent` (Type A / Type B, multiple distributions: normal, rectangular, triangular, U-shaped). Computes combined + expanded uncertainty at any coverage factor.
- **`certificate.py`** — `Certificate` ORM + `CertificateDraft` builder. Checks conformance to tolerance (`|deviation| + U ≤ tol`).
- **`drift_monitor.py`** — Linear-regression drift analysis for reference standards. Returns action verdict: `none` / `monitor` / `recalibrate` / `withdraw` based on CMC thresholds.
- **`migration.py`** — Alembic migration adding the two tables with appropriate indexes.

## Install

```bash
pip install doql-plugin-iso17025
```

Auto-discovered via `doql_plugins` entry-point — no configuration needed.

## Example: issue a calibration certificate

```python
from plugins.iso17025.certificate import CertificateDraft, MeasurementPoint

draft = CertificateDraft(
    customer_name="ACME Metrology Ltd",
    instrument_serial="PX-2024-0042",
    instrument_type="digital pressure gauge",
    reference_standards=["REF-001"],
    temperature_c=23.0, humidity_pct=45.0,
    measurements=[
        MeasurementPoint(nominal=10.0, measured=10.015, expanded_uncertainty=0.02, unit="bar"),
    ],
)
cert = draft.issue(db, certificate_number="CAL-2026-001")
```

## Compliance disclaimer

Technical primitives only. Accreditation (ILAC/EA MRA) requires documented quality management, proficiency testing, management reviews, competence records — none of which code alone provides.
