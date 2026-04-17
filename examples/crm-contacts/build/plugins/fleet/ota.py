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
