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
