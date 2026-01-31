"""add integration configuration tables

Revision ID: 0006_add_integration_config_tables
Revises: 0005_create_workflow_engine_tables
Create Date: 2025-02-14 12:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0006_add_integration_config_tables"
down_revision = "0005_create_workflow_engine_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "integration_connections",
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("service_type", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=256)),
        sa.Column("connection_uri", sa.String(length=512), nullable=False),
        sa.Column("credential_reference", sa.String(length=256)),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("tenant_id", "connection_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "service_type",
            "name",
            name="uq_integration_connections_tenant_service_name",
        ),
    )
    op.create_index(
        "ix_integration_connections_tenant_id",
        "integration_connections",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_integration_connections_service_type",
        "integration_connections",
        ["service_type"],
        unique=False,
    )

    op.create_table(
        "integration_credentials",
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("credential_id", sa.String(length=64), nullable=False),
        sa.Column("service_type", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("credential_reference", sa.String(length=256), nullable=False),
        sa.Column("scopes", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("tenant_id", "credential_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "service_type",
            "name",
            name="uq_integration_credentials_tenant_service_name",
        ),
    )
    op.create_index(
        "ix_integration_credentials_tenant_id",
        "integration_credentials",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_integration_credentials_service_type",
        "integration_credentials",
        ["service_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_integration_credentials_service_type", table_name="integration_credentials")
    op.drop_index("ix_integration_credentials_tenant_id", table_name="integration_credentials")
    op.drop_table("integration_credentials")
    op.drop_index("ix_integration_connections_service_type", table_name="integration_connections")
    op.drop_index("ix_integration_connections_tenant_id", table_name="integration_connections")
    op.drop_table("integration_connections")
