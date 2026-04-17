"""Metrics module generator for doql-plugin-fleet."""
from __future__ import annotations

import textwrap


def _metrics_module() -> str:
    return textwrap.dedent('''\
        """Metrics ingestion — simple time-series store for device telemetry."""
        from __future__ import annotations

        from datetime import datetime, timedelta, timezone
        from typing import Optional

        from fastapi import APIRouter, Depends, HTTPException
        from pydantic import BaseModel
        from sqlalchemy import Column, String, DateTime, Float, Index
        from sqlalchemy.orm import Session

        try:
            from database import Base, get_db
        except ImportError:
            from sqlalchemy.orm import declarative_base
            Base = declarative_base()
            get_db = lambda: None  # noqa


        router = APIRouter(prefix="/fleet/metrics", tags=["fleet"])


        class MetricSample(Base):
            __tablename__ = "fleet_metrics"
            id = Column(String(36), primary_key=True)
            tenant_id = Column(String(36), nullable=False)
            device_id = Column(String(64), nullable=False)
            metric = Column(String(64), nullable=False)
            value = Column(Float, nullable=False)
            timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

            __table_args__ = (
                Index("ix_metric_lookup", "tenant_id", "device_id", "metric", "timestamp"),
            )


        class IngestRequest(BaseModel):
            device_id: str
            metric: str
            value: float
            timestamp: Optional[datetime] = None


        @router.post("/ingest", status_code=201)
        def ingest(req: IngestRequest, db: Session = Depends(get_db)):
            import uuid
            from .tenant import current_tenant_id
            tid = current_tenant_id.get()
            if not tid:
                raise HTTPException(400, "Missing tenant context")
            sample = MetricSample(
                id=str(uuid.uuid4()),
                tenant_id=tid,
                device_id=req.device_id,
                metric=req.metric,
                value=req.value,
                timestamp=req.timestamp or datetime.now(timezone.utc),
            )
            db.add(sample)
            db.commit()
            return {"ok": True}


        @router.get("/query")
        def query(
            device_id: str,
            metric: str,
            minutes: int = 60,
            db: Session = Depends(get_db),
        ):
            from .tenant import current_tenant_id
            tid = current_tenant_id.get()
            if not tid:
                raise HTTPException(400, "Missing tenant context")
            since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            rows = (
                db.query(MetricSample)
                .filter(
                    MetricSample.tenant_id == tid,
                    MetricSample.device_id == device_id,
                    MetricSample.metric == metric,
                    MetricSample.timestamp >= since,
                )
                .order_by(MetricSample.timestamp.asc())
                .all()
            )
            return {
                "device_id": device_id,
                "metric": metric,
                "samples": [{"t": r.timestamp.isoformat(), "v": r.value} for r in rows],
            }
    ''')
