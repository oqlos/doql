"""Alembic migration: add audit_events + e_signatures tables."""
revision = "gxp_001"
down_revision = "001"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("timestamp", sa.DateTime, nullable=False),
        sa.Column("actor_id", sa.String(36), nullable=True),
        sa.Column("actor_role", sa.String(64), nullable=True),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("entity", sa.String(128), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=True),
        sa.Column("before_state", sa.Text, nullable=True),
        sa.Column("after_state", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("previous_hash", sa.String(64), nullable=True),
        sa.Column("record_hash", sa.String(64), nullable=False),
    )
    op.create_index("ix_audit_entity", "audit_events", ["entity", "entity_id"])
    op.create_index("ix_audit_timestamp", "audit_events", ["timestamp"])

    op.create_table(
        "e_signatures",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("signer_id", sa.String(36), nullable=False),
        sa.Column("signer_role", sa.String(64), nullable=True),
        sa.Column("intent", sa.String(32), nullable=False),
        sa.Column("entity", sa.String(128), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("signed_at", sa.DateTime, nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
    )
    op.create_index("ix_sig_entity", "e_signatures", ["entity", "entity_id"])


def downgrade():
    op.drop_index("ix_sig_entity", "e_signatures")
    op.drop_table("e_signatures")
    op.drop_index("ix_audit_timestamp", "audit_events")
    op.drop_index("ix_audit_entity", "audit_events")
    op.drop_table("audit_events")
