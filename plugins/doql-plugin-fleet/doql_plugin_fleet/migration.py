"""Migration module generator for doql-plugin-fleet."""
from __future__ import annotations

import textwrap


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
