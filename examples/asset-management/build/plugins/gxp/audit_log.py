"""Audit log — 21 CFR Part 11 §11.10(e): generate secure, computer-generated, time-stamped audit trails.

Records every create/update/delete with:
  - actor (user id + role)
  - timestamp (UTC, immutable)
  - entity + entity_id
  - before/after state (JSON)
  - ip_address + user_agent
  - previous_hash (tamper-evident chain)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import Session

try:
    from database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    actor_id = Column(String(36), nullable=True)
    actor_role = Column(String(64), nullable=True)
    action = Column(String(32), nullable=False)   # create | update | delete | sign | verify
    entity = Column(String(128), nullable=False)
    entity_id = Column(String(128), nullable=True)
    before_state = Column(Text, nullable=True)
    after_state = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    previous_hash = Column(String(64), nullable=True)
    record_hash = Column(String(64), nullable=False)


def _compute_hash(event: AuditEvent) -> str:
    payload = json.dumps({
        "ts": event.timestamp.isoformat() if event.timestamp else None,
        "actor": event.actor_id,
        "action": event.action,
        "entity": event.entity,
        "entity_id": event.entity_id,
        "before": event.before_state,
        "after": event.after_state,
        "prev": event.previous_hash or "",
    }, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def record(
    db: Session,
    *,
    action: str,
    entity: str,
    entity_id: Optional[str],
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
    before: Any = None,
    after: Any = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditEvent:
    """Record an audit event. Returns the persisted AuditEvent."""
    import uuid
    # Chain to previous event for tamper-evidence
    prev = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).first()
    event = AuditEvent(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id else None,
        before_state=json.dumps(before, default=str) if before else None,
        after_state=json.dumps(after, default=str) if after else None,
        ip_address=ip_address,
        user_agent=user_agent,
        previous_hash=prev.record_hash if prev else None,
    )
    event.record_hash = _compute_hash(event)
    db.add(event)
    db.commit()
    return event


def verify_chain(db: Session) -> tuple[bool, Optional[str]]:
    """Verify the audit chain is intact. Returns (is_valid, broken_event_id_or_None)."""
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc()).all()
    prev_hash = None
    for ev in events:
        if ev.previous_hash != prev_hash:
            return False, ev.id
        expected = _compute_hash(ev)
        if ev.record_hash != expected:
            return False, ev.id
        prev_hash = ev.record_hash
    return True, None
