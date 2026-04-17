"""Migration module generator for ISO/IEC 17025:2017 compliance."""
from __future__ import annotations

import textwrap


def generate() -> str:
    """Generate migration.py module content."""
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
