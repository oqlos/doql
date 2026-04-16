# doql-plugin-iso17025 — Compliance Add-on

Generated for **Notes** v1.0.0.

ISO/IEC 17025:2017 primitives for calibration laboratories:

## Components

| File | Purpose | Standard Reference |
|------|---------|--------------------|
| `traceability.py` | Reference standards chain to SI | §6.5 |
| `uncertainty.py` | GUM-compliant uncertainty budgets | JCGM 100:2008 |
| `certificate.py` | Calibration certificates with signatures | §7.8 |
| `drift_monitor.py` | Drift analysis for reference standards | §6.4.10 / §7.7 |
| `migration.py` | Alembic migration for tables | — |

## Integration

```python
# Issue a certificate
from plugins.iso17025.certificate import CertificateDraft, MeasurementPoint

draft = CertificateDraft(
    customer_name="ACME Metrology Ltd",
    instrument_serial="PX-2024-0042",
    instrument_type="digital pressure gauge",
    reference_standards=["REF-001", "REF-002"],
    temperature_c=23.0, humidity_pct=45.0,
    measurements=[
        MeasurementPoint(nominal=10.0, measured=10.015, expanded_uncertainty=0.02, unit="bar"),
        MeasurementPoint(nominal=50.0, measured=50.042, expanded_uncertainty=0.02, unit="bar"),
    ],
)
cert = draft.issue(db, certificate_number="CAL-2026-001")
```

```python
# Verify traceability
from plugins.iso17025.traceability import TraceabilityChain

tc = TraceabilityChain(db)
ok, err = tc.is_traceable("REF-001")
assert ok, err
```

```python
# Build uncertainty budget
from plugins.iso17025.uncertainty import UncertaintyBudget, UncertaintyComponent, Distribution

budget = UncertaintyBudget(measurand="pressure", unit="bar")
budget.add(UncertaintyComponent("ref_std", 0.02, coverage_factor=2.0, source="cal cert"))
budget.add(UncertaintyComponent("repeatability", 0.015, source="10 readings"))
budget.add(UncertaintyComponent("resolution", 0.005, distribution=Distribution.RECTANGULAR))
U = budget.expanded_uncertainty   # k=2
```

## Complementary plugins

- `doql-plugin-gxp` — 21 CFR Part 11 audit log + e-signatures (pair with this plugin for GMP labs).
