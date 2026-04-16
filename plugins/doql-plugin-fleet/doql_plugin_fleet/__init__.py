"""doql-plugin-fleet — Multi-tenant fleet manager.

Generates:
  build/plugins/fleet/
  ├── tenant.py           — Tenant model + context middleware (row-level isolation)
  ├── device_registry.py  — Device enrollment + heartbeat + health rollup
  ├── metrics.py          — Time-series metrics ingestion + aggregation
  ├── ota.py              — OTA update campaigns with canary rollout
  ├── migration.py        — Alembic migration for fleet tables
  └── README.md
"""
from __future__ import annotations

import pathlib
import textwrap


def _tenant_module() -> str:
    return textwrap.dedent('''\
        """Tenant model + row-level isolation middleware."""
        from __future__ import annotations

        import contextvars
        from datetime import datetime, timezone
        from typing import Optional

        from fastapi import Request
        from sqlalchemy import Column, String, DateTime, Boolean, Text, event
        from sqlalchemy.orm import Session, Query
        from starlette.middleware.base import BaseHTTPMiddleware

        try:
            from database import Base
        except ImportError:
            from sqlalchemy.orm import declarative_base
            Base = declarative_base()


        # Current tenant stored in context var (async-safe)
        current_tenant_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
            "current_tenant_id", default=None
        )


        class Tenant(Base):
            __tablename__ = "tenants"
            id = Column(String(36), primary_key=True)
            slug = Column(String(64), unique=True, nullable=False)    # URL-safe
            name = Column(String(255), nullable=False)
            plan = Column(String(32), nullable=False, default="free")   # free | pro | enterprise
            created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
            active = Column(Boolean, default=True)
            settings = Column(Text, nullable=True)   # JSON config per tenant


        class TenantMiddleware(BaseHTTPMiddleware):
            """Resolve tenant from subdomain / header / JWT and set context var."""

            async def dispatch(self, request: Request, call_next):
                tenant_id = self._resolve(request)
                token = current_tenant_id.set(tenant_id)
                try:
                    request.state.tenant_id = tenant_id
                    return await call_next(request)
                finally:
                    current_tenant_id.reset(token)

            def _resolve(self, request: Request) -> Optional[str]:
                # 1. Explicit header wins (for service-to-service)
                header = request.headers.get("X-Tenant-Id")
                if header:
                    return header
                # 2. Subdomain pattern: {slug}.app.example.com
                host = request.headers.get("host", "")
                parts = host.split(".")
                if len(parts) >= 3:
                    return parts[0]
                # 3. JWT claim — assumes auth ran earlier
                user = getattr(request.state, "user", None)
                if user is not None:
                    return getattr(user, "tenant_id", None)
                return None


        def apply_tenant_filter(query: Query, model: type) -> Query:
            """Apply row-level isolation to a query if the model has a tenant_id column."""
            if not hasattr(model, "tenant_id"):
                return query
            tid = current_tenant_id.get()
            if tid is None:
                # No tenant context = no data (defense in depth)
                return query.filter(False)
            return query.filter(model.tenant_id == tid)
    ''')


def _device_registry_module() -> str:
    return textwrap.dedent('''\
        """Device registry — enrollment, heartbeat, health rollup."""
        from __future__ import annotations

        from datetime import datetime, timedelta, timezone
        from enum import Enum
        from typing import Optional

        from fastapi import APIRouter, Depends, HTTPException, Request
        from pydantic import BaseModel
        from sqlalchemy import Column, String, DateTime, Integer, Text
        from sqlalchemy.orm import Session

        try:
            from database import Base, get_db
        except ImportError:
            from sqlalchemy.orm import declarative_base
            Base = declarative_base()
            get_db = lambda: None  # noqa


        router = APIRouter(prefix="/fleet/devices", tags=["fleet"])


        class DeviceStatus(str, Enum):
            PROVISIONED = "provisioned"
            ONLINE = "online"
            OFFLINE = "offline"
            DEGRADED = "degraded"
            RETIRED = "retired"


        class Device(Base):
            __tablename__ = "fleet_devices"
            id = Column(String(64), primary_key=True)
            tenant_id = Column(String(36), nullable=False, index=True)
            name = Column(String(255), nullable=True)
            serial = Column(String(128), unique=True, nullable=True)
            hardware = Column(String(128), nullable=True)   # e.g. "rpi4b", "nuc12"
            firmware_version = Column(String(64), nullable=True)
            status = Column(String(32), nullable=False, default=DeviceStatus.PROVISIONED.value)
            last_seen = Column(DateTime, nullable=True)
            enrolled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
            metadata_json = Column(Text, nullable=True)


        class EnrollRequest(BaseModel):
            id: str
            name: Optional[str] = None
            serial: Optional[str] = None
            hardware: Optional[str] = None
            firmware_version: Optional[str] = None


        class HeartbeatRequest(BaseModel):
            device_id: str
            firmware_version: Optional[str] = None
            metrics: Optional[dict] = None


        OFFLINE_THRESHOLD = timedelta(minutes=5)
        DEGRADED_THRESHOLD = timedelta(minutes=2)


        @router.post("/enroll", status_code=201)
        def enroll(req: EnrollRequest, request: Request, db: Session = Depends(get_db)):
            tid = getattr(request.state, "tenant_id", None)
            if not tid:
                raise HTTPException(400, "Missing tenant context")
            existing = db.query(Device).filter(Device.id == req.id).first()
            if existing:
                raise HTTPException(409, f"Device {req.id} already enrolled")
            device = Device(
                id=req.id,
                tenant_id=tid,
                name=req.name,
                serial=req.serial,
                hardware=req.hardware,
                firmware_version=req.firmware_version,
                status=DeviceStatus.PROVISIONED.value,
            )
            db.add(device)
            db.commit()
            return {"id": device.id, "status": device.status}


        @router.post("/heartbeat")
        def heartbeat(req: HeartbeatRequest, db: Session = Depends(get_db)):
            device = db.query(Device).filter(Device.id == req.device_id).first()
            if not device:
                raise HTTPException(404, "Device not enrolled")
            device.last_seen = datetime.now(timezone.utc)
            device.status = DeviceStatus.ONLINE.value
            if req.firmware_version:
                device.firmware_version = req.firmware_version
            db.commit()
            return {"ok": True}


        @router.get("/health")
        def fleet_health(request: Request, db: Session = Depends(get_db)):
            """Aggregate fleet health for the current tenant."""
            tid = getattr(request.state, "tenant_id", None)
            if not tid:
                raise HTTPException(400, "Missing tenant context")
            now = datetime.now(timezone.utc)
            devices = db.query(Device).filter(Device.tenant_id == tid).all()
            counts = {s.value: 0 for s in DeviceStatus}
            for d in devices:
                # Live status computation from last_seen
                if d.status == DeviceStatus.RETIRED.value:
                    live = DeviceStatus.RETIRED
                elif d.last_seen is None:
                    live = DeviceStatus.PROVISIONED
                elif now - d.last_seen > OFFLINE_THRESHOLD:
                    live = DeviceStatus.OFFLINE
                elif now - d.last_seen > DEGRADED_THRESHOLD:
                    live = DeviceStatus.DEGRADED
                else:
                    live = DeviceStatus.ONLINE
                counts[live.value] += 1
            return {"total": len(devices), "by_status": counts}
    ''')


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


def _ota_module() -> str:
    return textwrap.dedent('''\
        """OTA update campaigns with canary rollout."""
        from __future__ import annotations

        from datetime import datetime, timezone
        from enum import Enum
        from typing import Optional

        from sqlalchemy import Column, String, DateTime, Integer, Text, Float
        from sqlalchemy.orm import Session

        try:
            from database import Base
        except ImportError:
            from sqlalchemy.orm import declarative_base
            Base = declarative_base()


        class CampaignStatus(str, Enum):
            DRAFT = "draft"
            CANARY = "canary"
            ROLLING = "rolling"
            COMPLETED = "completed"
            ROLLED_BACK = "rolled_back"


        class UpdateCampaign(Base):
            __tablename__ = "fleet_campaigns"
            id = Column(String(36), primary_key=True)
            tenant_id = Column(String(36), nullable=False, index=True)
            firmware_version = Column(String(64), nullable=False)
            target_filter = Column(Text, nullable=True)   # JSON predicate describing which devices
            status = Column(String(32), nullable=False, default=CampaignStatus.DRAFT.value)
            canary_pct = Column(Float, nullable=False, default=5.0)
            rollback_on_failure_pct = Column(Float, nullable=False, default=1.0)
            created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
            started_at = Column(DateTime, nullable=True)
            completed_at = Column(DateTime, nullable=True)


        def advance_campaign(db: Session, campaign_id: str, success_rate: float) -> str:
            """Move a campaign forward based on observed success rate.

            Returns the new status.
            """
            c = db.query(UpdateCampaign).filter(UpdateCampaign.id == campaign_id).first()
            if not c:
                raise ValueError(f"Campaign {campaign_id} not found")

            failure_pct = (1 - success_rate) * 100

            if c.status == CampaignStatus.CANARY.value:
                if failure_pct > c.rollback_on_failure_pct:
                    c.status = CampaignStatus.ROLLED_BACK.value
                else:
                    c.status = CampaignStatus.ROLLING.value
            elif c.status == CampaignStatus.ROLLING.value:
                if failure_pct > c.rollback_on_failure_pct:
                    c.status = CampaignStatus.ROLLED_BACK.value
                elif success_rate >= 0.99:
                    c.status = CampaignStatus.COMPLETED.value
                    c.completed_at = datetime.now(timezone.utc)
            db.commit()
            return c.status
    ''')


def _migration_module() -> str:
    return textwrap.dedent('''\
        """Alembic migration: fleet tables."""
        revision = "fleet_001"
        down_revision = "001"

        from alembic import op
        import sqlalchemy as sa


        def upgrade():
            op.create_table(
                "tenants",
                sa.Column("id", sa.String(36), primary_key=True),
                sa.Column("slug", sa.String(64), unique=True, nullable=False),
                sa.Column("name", sa.String(255), nullable=False),
                sa.Column("plan", sa.String(32), nullable=False, default="free"),
                sa.Column("created_at", sa.DateTime),
                sa.Column("active", sa.Boolean, default=True),
                sa.Column("settings", sa.Text, nullable=True),
            )
            op.create_table(
                "fleet_devices",
                sa.Column("id", sa.String(64), primary_key=True),
                sa.Column("tenant_id", sa.String(36), nullable=False),
                sa.Column("name", sa.String(255), nullable=True),
                sa.Column("serial", sa.String(128), unique=True, nullable=True),
                sa.Column("hardware", sa.String(128), nullable=True),
                sa.Column("firmware_version", sa.String(64), nullable=True),
                sa.Column("status", sa.String(32), nullable=False),
                sa.Column("last_seen", sa.DateTime, nullable=True),
                sa.Column("enrolled_at", sa.DateTime),
                sa.Column("metadata_json", sa.Text, nullable=True),
            )
            op.create_index("ix_device_tenant", "fleet_devices", ["tenant_id"])
            op.create_index("ix_device_last_seen", "fleet_devices", ["last_seen"])

            op.create_table(
                "fleet_metrics",
                sa.Column("id", sa.String(36), primary_key=True),
                sa.Column("tenant_id", sa.String(36), nullable=False),
                sa.Column("device_id", sa.String(64), nullable=False),
                sa.Column("metric", sa.String(64), nullable=False),
                sa.Column("value", sa.Float, nullable=False),
                sa.Column("timestamp", sa.DateTime, nullable=False),
            )
            op.create_index("ix_metric_lookup", "fleet_metrics",
                            ["tenant_id", "device_id", "metric", "timestamp"])

            op.create_table(
                "fleet_campaigns",
                sa.Column("id", sa.String(36), primary_key=True),
                sa.Column("tenant_id", sa.String(36), nullable=False),
                sa.Column("firmware_version", sa.String(64), nullable=False),
                sa.Column("target_filter", sa.Text, nullable=True),
                sa.Column("status", sa.String(32), nullable=False),
                sa.Column("canary_pct", sa.Float, default=5.0),
                sa.Column("rollback_on_failure_pct", sa.Float, default=1.0),
                sa.Column("created_at", sa.DateTime),
                sa.Column("started_at", sa.DateTime, nullable=True),
                sa.Column("completed_at", sa.DateTime, nullable=True),
            )
            op.create_index("ix_campaign_tenant", "fleet_campaigns", ["tenant_id"])


        def downgrade():
            op.drop_index("ix_campaign_tenant", "fleet_campaigns")
            op.drop_table("fleet_campaigns")
            op.drop_index("ix_metric_lookup", "fleet_metrics")
            op.drop_table("fleet_metrics")
            op.drop_index("ix_device_last_seen", "fleet_devices")
            op.drop_index("ix_device_tenant", "fleet_devices")
            op.drop_table("fleet_devices")
            op.drop_table("tenants")
    ''')


def _readme(spec) -> str:
    return textwrap.dedent(f'''\
        # doql-plugin-fleet — Multi-tenant Fleet Manager

        Generated for **{spec.app_name}** v{spec.version}.

        Tenant isolation + device registry + metrics + OTA in one drop-in plugin.

        ## Components

        | File | Purpose |
        |------|---------|
        | `tenant.py` | `Tenant` model + `TenantMiddleware` (subdomain/header/JWT resolution) + `apply_tenant_filter()` for query isolation |
        | `device_registry.py` | `/fleet/devices/enroll`, `/heartbeat`, `/health` — device lifecycle |
        | `metrics.py` | `/fleet/metrics/ingest`, `/query` — time-series telemetry |
        | `ota.py` | `UpdateCampaign` model + `advance_campaign()` canary gate logic |
        | `migration.py` | Alembic migration for all tables |

        ## Wire it up

        ```python
        from plugins.fleet.tenant import TenantMiddleware
        from plugins.fleet.device_registry import router as devices_router
        from plugins.fleet.metrics import router as metrics_router

        app.add_middleware(TenantMiddleware)
        app.include_router(devices_router)
        app.include_router(metrics_router)
        ```

        ## Tenant resolution order

        1. `X-Tenant-Id` header (for service-to-service)
        2. Subdomain `{{slug}}.app.example.com`
        3. JWT claim (`user.tenant_id`)

        ## Canary rollout

        `advance_campaign(db, campaign_id, success_rate)` transitions status:
        - `canary` → `rolling` (if failure_pct ≤ rollback threshold)
        - `rolling` → `completed` (if success_rate ≥ 99%)
        - any → `rolled_back` (if failure_pct > rollback threshold)
    ''')


def generate(spec, env_vars, out: pathlib.Path, project_root: pathlib.Path) -> None:
    """Entry point called by doql's plugin runner."""
    out.mkdir(parents=True, exist_ok=True)

    files = {
        "__init__.py": '"""doql-plugin-fleet multi-tenant module."""\n',
        "tenant.py": _tenant_module(),
        "device_registry.py": _device_registry_module(),
        "metrics.py": _metrics_module(),
        "ota.py": _ota_module(),
        "migration.py": _migration_module(),
        "README.md": _readme(spec),
    }

    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
