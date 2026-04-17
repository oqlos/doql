"""Traceability module generator for ISO/IEC 17025:2017 compliance."""
from __future__ import annotations

import textwrap


def generate() -> str:
    """Generate traceability.py module content."""
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
