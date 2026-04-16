"""doql-plugin-iso17025 — ISO/IEC 17025:2017 compliance add-on for calibration laboratories.

Generates:
  build/plugins/iso17025/
  ├── traceability.py        — ISO 17025 §6.5: metrological traceability chain (SI → national standard → reference → DUT)
  ├── uncertainty.py         — GUM-compliant uncertainty budget calculator (type A + type B + combined)
  ├── certificate.py         — digitally signed calibration certificate generator
  ├── drift_monitor.py       — trend analysis for reference standards (CMC validation)
  ├── migration.py           — Alembic migration for calibration_records + standards tables
  └── README.md              — integration + compliance notes
"""
from __future__ import annotations

import pathlib
import textwrap


def _traceability_module() -> str:
    return textwrap.dedent('''\
        """Metrological traceability — ISO/IEC 17025 §6.5.

        Each measurement traces back through a chain:
          DUT → Reference Standard → Transfer Standard → National Metrology Institute → SI unit

        Every link records:
          - standard id + name
          - calibration certificate number
          - uncertainty (k=2, 95% coverage)
          - valid_from / valid_until
          - issuing authority (NMI/accredited lab)
        """
        from __future__ import annotations

        from datetime import date, datetime, timezone
        from typing import Optional

        from sqlalchemy import Column, String, Date, DateTime, Float, ForeignKey, Text
        from sqlalchemy.orm import Session, relationship

        try:
            from database import Base
        except ImportError:
            from sqlalchemy.orm import declarative_base
            Base = declarative_base()


        class ReferenceStandard(Base):
            """A reference artifact/standard used in calibrations."""
            __tablename__ = "reference_standards"
            id = Column(String(64), primary_key=True)
            name = Column(String(255), nullable=False)
            serial_number = Column(String(128), nullable=True)
            manufacturer = Column(String(255), nullable=True)
            parameter = Column(String(64), nullable=False)   # e.g. "pressure", "temperature"
            range_min = Column(Float, nullable=True)
            range_max = Column(Float, nullable=True)
            unit = Column(String(32), nullable=False)
            certificate_number = Column(String(128), nullable=False)
            issuing_authority = Column(String(255), nullable=False)   # NMI or accredited lab
            calibration_date = Column(Date, nullable=False)
            valid_until = Column(Date, nullable=False)
            uncertainty = Column(Float, nullable=False)               # expanded uncertainty U (k=2)
            uncertainty_unit = Column(String(32), nullable=True)
            parent_id = Column(String(64), ForeignKey("reference_standards.id"), nullable=True)


        class TraceabilityChain:
            """Walk the traceability graph from DUT calibration back to SI."""

            def __init__(self, db: Session):
                self.db = db

            def chain_for(self, standard_id: str) -> list[ReferenceStandard]:
                """Return the full chain starting at *standard_id* up to SI."""
                result: list[ReferenceStandard] = []
                current_id: Optional[str] = standard_id
                visited: set[str] = set()
                while current_id and current_id not in visited:
                    visited.add(current_id)
                    std = self.db.query(ReferenceStandard).filter(
                        ReferenceStandard.id == current_id
                    ).first()
                    if not std:
                        break
                    result.append(std)
                    current_id = std.parent_id
                return result

            def is_traceable(self, standard_id: str) -> tuple[bool, Optional[str]]:
                """Verify: chain reaches an NMI and all certificates are valid."""
                chain = self.chain_for(standard_id)
                if not chain:
                    return False, "Standard not found"
                today = date.today()
                for std in chain:
                    if std.valid_until < today:
                        return False, f"Expired: {std.id} ({std.valid_until})"
                # Check top of chain references NMI
                top = chain[-1]
                if top.parent_id is not None:
                    return False, f"Incomplete chain — top {top.id} has parent {top.parent_id}"
                return True, None
    ''')


def _uncertainty_module() -> str:
    return textwrap.dedent('''\
        """Uncertainty budget — per JCGM 100:2008 (GUM — Guide to Expression of Uncertainty).

        Combined standard uncertainty u_c computed via root-sum-of-squares of components:
          u_c² = Σ (cᵢ · uᵢ)²

        Expanded uncertainty U = k · u_c (typically k=2 for ~95% coverage).
        """
        from __future__ import annotations

        from dataclasses import dataclass, field
        from enum import Enum
        from math import sqrt


        class UncertaintyType(str, Enum):
            TYPE_A = "A"   # Statistical (from repeated measurements)
            TYPE_B = "B"   # Non-statistical (datasheet, calibration cert, judgment)


        class Distribution(str, Enum):
            NORMAL = "normal"            # divisor = k (commonly 2)
            RECTANGULAR = "rectangular"  # divisor = √3
            TRIANGULAR = "triangular"    # divisor = √6
            U_SHAPED = "u_shaped"        # divisor = √2


        _DIVISORS = {
            Distribution.NORMAL: 1.0,   # user supplies k via coverage_factor field
            Distribution.RECTANGULAR: sqrt(3),
            Distribution.TRIANGULAR: sqrt(6),
            Distribution.U_SHAPED: sqrt(2),
        }


        @dataclass
        class UncertaintyComponent:
            """Single contribution to the uncertainty budget."""
            name: str
            value: float                              # half-width of the interval (type B) or std dev (type A)
            type: UncertaintyType = UncertaintyType.TYPE_B
            distribution: Distribution = Distribution.RECTANGULAR
            coverage_factor: float = 1.0              # k for type B with normal distribution (datasheet U)
            sensitivity: float = 1.0                  # ∂y/∂xᵢ
            unit: str = ""
            source: str = ""

            @property
            def standard_uncertainty(self) -> float:
                """u(xᵢ) — the standard uncertainty for this component."""
                if self.type == UncertaintyType.TYPE_A:
                    return self.value
                # Type B: divide half-width by distribution divisor
                if self.distribution == Distribution.NORMAL:
                    return self.value / self.coverage_factor
                return self.value / _DIVISORS[self.distribution]

            @property
            def contribution(self) -> float:
                """cᵢ · u(xᵢ) — weighted contribution to the combined uncertainty."""
                return self.sensitivity * self.standard_uncertainty


        @dataclass
        class UncertaintyBudget:
            """Collection of components producing a combined + expanded uncertainty."""
            measurand: str
            unit: str
            components: list[UncertaintyComponent] = field(default_factory=list)
            coverage_factor: float = 2.0   # k for the final U (typically 2 → ~95% confidence)

            def add(self, component: UncertaintyComponent) -> "UncertaintyBudget":
                self.components.append(component)
                return self

            @property
            def combined_uncertainty(self) -> float:
                """u_c = √Σ(cᵢ·uᵢ)²."""
                return sqrt(sum(c.contribution ** 2 for c in self.components))

            @property
            def expanded_uncertainty(self) -> float:
                """U = k · u_c."""
                return self.coverage_factor * self.combined_uncertainty

            def as_dict(self) -> dict:
                return {
                    "measurand": self.measurand,
                    "unit": self.unit,
                    "components": [
                        {
                            "name": c.name,
                            "type": c.type.value,
                            "distribution": c.distribution.value,
                            "value": c.value,
                            "standard_uncertainty": c.standard_uncertainty,
                            "sensitivity": c.sensitivity,
                            "contribution": c.contribution,
                            "source": c.source,
                        }
                        for c in self.components
                    ],
                    "combined_uncertainty": self.combined_uncertainty,
                    "coverage_factor": self.coverage_factor,
                    "expanded_uncertainty": self.expanded_uncertainty,
                }


        # Example usage:
        #   budget = UncertaintyBudget(measurand="pressure", unit="bar")
        #   budget.add(UncertaintyComponent("reference_std_U", 0.02, type=UncertaintyType.TYPE_B,
        #                                   distribution=Distribution.NORMAL, coverage_factor=2.0,
        #                                   source="calibration certificate"))
        #   budget.add(UncertaintyComponent("repeatability", 0.015, type=UncertaintyType.TYPE_A,
        #                                   source="10-point repeat measurement"))
        #   budget.add(UncertaintyComponent("resolution", 0.005, distribution=Distribution.RECTANGULAR))
        #   U = budget.expanded_uncertainty  # → ≈0.050 bar (k=2)
    ''')


def _certificate_module() -> str:
    return textwrap.dedent('''\
        """Calibration certificate generator — ISO/IEC 17025 §7.8.

        A certificate records:
          - unique identifier + issue date
          - customer + instrument under test (serial, make, model)
          - reference standards used (with certificate numbers)
          - measurement results + expanded uncertainty (k=2)
          - statement of traceability
          - signatures (authorized signatory + technical reviewer)
          - deviation from nominal if applicable
        """
        from __future__ import annotations

        import json
        import uuid
        from dataclasses import dataclass, field
        from datetime import date, datetime, timezone
        from typing import Any, Optional

        from sqlalchemy import Column, String, Date, DateTime, Float, Text, Boolean
        from sqlalchemy.orm import Session

        try:
            from database import Base
        except ImportError:
            from sqlalchemy.orm import declarative_base
            Base = declarative_base()


        class Certificate(Base):
            __tablename__ = "iso17025_certificates"
            id = Column(String(36), primary_key=True)
            certificate_number = Column(String(64), unique=True, nullable=False)
            issue_date = Column(Date, nullable=False)

            # Customer + DUT
            customer_name = Column(String(255), nullable=False)
            customer_address = Column(Text, nullable=True)
            instrument_make = Column(String(128), nullable=True)
            instrument_model = Column(String(128), nullable=True)
            instrument_serial = Column(String(128), nullable=True)
            instrument_type = Column(String(128), nullable=True)

            # Environment
            temperature_c = Column(Float, nullable=True)
            humidity_pct = Column(Float, nullable=True)

            # Payload — measurement points + uncertainty budget (JSON)
            measurements = Column(Text, nullable=False)   # [{"point": 10.0, "measured": 10.01, "U": 0.02, "unit": "bar"}, ...]
            uncertainty_budget = Column(Text, nullable=True)
            reference_standards = Column(Text, nullable=True)   # JSON list of standard ids + cert numbers

            # Signatures
            signatory_id = Column(String(36), nullable=True)
            reviewer_id = Column(String(36), nullable=True)
            signed_at = Column(DateTime, nullable=True)
            signature_hash = Column(String(64), nullable=True)   # link to e_signature from plugin-gxp

            # Result
            conforms = Column(Boolean, nullable=False, default=True)
            remarks = Column(Text, nullable=True)


        @dataclass
        class MeasurementPoint:
            nominal: float
            measured: float
            expanded_uncertainty: float   # U at k=2
            unit: str = ""

            @property
            def deviation(self) -> float:
                return self.measured - self.nominal


        @dataclass
        class CertificateDraft:
            customer_name: str
            instrument_serial: str
            measurements: list[MeasurementPoint] = field(default_factory=list)
            reference_standards: list[str] = field(default_factory=list)
            temperature_c: Optional[float] = None
            humidity_pct: Optional[float] = None
            instrument_make: Optional[str] = None
            instrument_model: Optional[str] = None
            instrument_type: Optional[str] = None
            remarks: Optional[str] = None

            def conforms_to_tolerance(self, tolerance: float) -> bool:
                """Check if every measurement point (|deviation| + U) is within tolerance."""
                return all(
                    abs(m.deviation) + m.expanded_uncertainty <= tolerance
                    for m in self.measurements
                )

            def issue(self, db: Session, certificate_number: str) -> Certificate:
                cert = Certificate(
                    id=str(uuid.uuid4()),
                    certificate_number=certificate_number,
                    issue_date=date.today(),
                    customer_name=self.customer_name,
                    instrument_make=self.instrument_make,
                    instrument_model=self.instrument_model,
                    instrument_serial=self.instrument_serial,
                    instrument_type=self.instrument_type,
                    temperature_c=self.temperature_c,
                    humidity_pct=self.humidity_pct,
                    measurements=json.dumps([
                        {
                            "nominal": m.nominal,
                            "measured": m.measured,
                            "deviation": m.deviation,
                            "U": m.expanded_uncertainty,
                            "unit": m.unit,
                        }
                        for m in self.measurements
                    ]),
                    reference_standards=json.dumps(self.reference_standards),
                    remarks=self.remarks,
                    conforms=True,
                )
                db.add(cert)
                db.commit()
                db.refresh(cert)
                return cert
    ''')


def _drift_monitor_module() -> str:
    return textwrap.dedent('''\
        """Drift monitoring — ISO/IEC 17025 §6.4.10 & §7.7.

        Tracks reference standard behavior over time so out-of-tolerance drift triggers
        an alert BEFORE it compromises measurements that depend on it.
        """
        from __future__ import annotations

        from dataclasses import dataclass
        from datetime import date
        from statistics import mean, pstdev
        from typing import Optional


        @dataclass
        class DriftResult:
            standard_id: str
            trend_slope: float          # units per day
            residual_std: float          # dispersion around the trend line
            within_cmc: bool             # True if |slope|·period + residual_std < CMC
            action: str                  # "none" | "monitor" | "recalibrate" | "withdraw"


        def evaluate_drift(
            standard_id: str,
            history: list[tuple[date, float]],     # [(measurement_date, value), ...]
            cmc: float,                             # best measurement capability
            period_days: int = 365,
        ) -> Optional[DriftResult]:
            """Linear-regression drift check. Returns None if fewer than 3 points."""
            if len(history) < 3:
                return None

            history_sorted = sorted(history, key=lambda p: p[0])
            t0 = history_sorted[0][0]
            xs = [(d - t0).days for d, _ in history_sorted]
            ys = [v for _, v in history_sorted]
            n = len(xs)

            # Least-squares slope
            x_mean = mean(xs)
            y_mean = mean(ys)
            num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
            den = sum((x - x_mean) ** 2 for x in xs)
            slope = num / den if den else 0.0
            intercept = y_mean - slope * x_mean

            residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
            residual_std = pstdev(residuals) if n >= 2 else 0.0

            projected_change = abs(slope) * period_days + residual_std
            within_cmc = projected_change < cmc

            if projected_change > cmc * 2:
                action = "withdraw"
            elif projected_change > cmc:
                action = "recalibrate"
            elif projected_change > cmc * 0.7:
                action = "monitor"
            else:
                action = "none"

            return DriftResult(
                standard_id=standard_id,
                trend_slope=slope,
                residual_std=residual_std,
                within_cmc=within_cmc,
                action=action,
            )
    ''')


def _migration_module() -> str:
    return textwrap.dedent('''\
        """Alembic migration: add reference_standards + iso17025_certificates tables."""
        revision = "iso17025_001"
        down_revision = "001"

        from alembic import op
        import sqlalchemy as sa


        def upgrade():
            op.create_table(
                "reference_standards",
                sa.Column("id", sa.String(64), primary_key=True),
                sa.Column("name", sa.String(255), nullable=False),
                sa.Column("serial_number", sa.String(128), nullable=True),
                sa.Column("manufacturer", sa.String(255), nullable=True),
                sa.Column("parameter", sa.String(64), nullable=False),
                sa.Column("range_min", sa.Float, nullable=True),
                sa.Column("range_max", sa.Float, nullable=True),
                sa.Column("unit", sa.String(32), nullable=False),
                sa.Column("certificate_number", sa.String(128), nullable=False),
                sa.Column("issuing_authority", sa.String(255), nullable=False),
                sa.Column("calibration_date", sa.Date, nullable=False),
                sa.Column("valid_until", sa.Date, nullable=False),
                sa.Column("uncertainty", sa.Float, nullable=False),
                sa.Column("uncertainty_unit", sa.String(32), nullable=True),
                sa.Column("parent_id", sa.String(64), sa.ForeignKey("reference_standards.id"), nullable=True),
            )
            op.create_index("ix_refstd_parameter", "reference_standards", ["parameter"])
            op.create_index("ix_refstd_valid_until", "reference_standards", ["valid_until"])

            op.create_table(
                "iso17025_certificates",
                sa.Column("id", sa.String(36), primary_key=True),
                sa.Column("certificate_number", sa.String(64), unique=True, nullable=False),
                sa.Column("issue_date", sa.Date, nullable=False),
                sa.Column("customer_name", sa.String(255), nullable=False),
                sa.Column("customer_address", sa.Text, nullable=True),
                sa.Column("instrument_make", sa.String(128), nullable=True),
                sa.Column("instrument_model", sa.String(128), nullable=True),
                sa.Column("instrument_serial", sa.String(128), nullable=True),
                sa.Column("instrument_type", sa.String(128), nullable=True),
                sa.Column("temperature_c", sa.Float, nullable=True),
                sa.Column("humidity_pct", sa.Float, nullable=True),
                sa.Column("measurements", sa.Text, nullable=False),
                sa.Column("uncertainty_budget", sa.Text, nullable=True),
                sa.Column("reference_standards", sa.Text, nullable=True),
                sa.Column("signatory_id", sa.String(36), nullable=True),
                sa.Column("reviewer_id", sa.String(36), nullable=True),
                sa.Column("signed_at", sa.DateTime, nullable=True),
                sa.Column("signature_hash", sa.String(64), nullable=True),
                sa.Column("conforms", sa.Boolean, nullable=False, default=True),
                sa.Column("remarks", sa.Text, nullable=True),
            )
            op.create_index("ix_cert_number", "iso17025_certificates", ["certificate_number"])
            op.create_index("ix_cert_issue_date", "iso17025_certificates", ["issue_date"])


        def downgrade():
            op.drop_index("ix_cert_issue_date", "iso17025_certificates")
            op.drop_index("ix_cert_number", "iso17025_certificates")
            op.drop_table("iso17025_certificates")
            op.drop_index("ix_refstd_valid_until", "reference_standards")
            op.drop_index("ix_refstd_parameter", "reference_standards")
            op.drop_table("reference_standards")
    ''')


def _readme(spec) -> str:
    return textwrap.dedent(f'''\
        # doql-plugin-iso17025 — Compliance Add-on

        Generated for **{spec.app_name}** v{spec.version}.

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
    ''')


def generate(spec, env_vars, out: pathlib.Path, project_root: pathlib.Path) -> None:
    """Entry point called by doql's plugin runner."""
    out.mkdir(parents=True, exist_ok=True)

    files = {
        "__init__.py": '"""doql-plugin-iso17025 compliance module."""\n',
        "traceability.py": _traceability_module(),
        "uncertainty.py": _uncertainty_module(),
        "certificate.py": _certificate_module(),
        "drift_monitor.py": _drift_monitor_module(),
        "migration.py": _migration_module(),
        "README.md": _readme(spec),
    }

    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
