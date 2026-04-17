"""Certificate module generator for ISO/IEC 17025:2017 compliance."""
from __future__ import annotations

import textwrap


def generate() -> str:
    """Generate certificate.py module content."""
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
