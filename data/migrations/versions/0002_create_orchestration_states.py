"""create orchestration states table

Revision ID: 0002_create_orchestration_states
Revises: 0001_create_core_tables
Create Date: 2025-02-14 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_create_orchestration_states"
down_revision = "0001_create_core_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "orchestration_states",
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("last_checkpoint", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("tenant_id", "run_id"),
    )
    op.create_index(
        "ix_orchestration_states_tenant_id",
        "orchestration_states",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_orchestration_states_tenant_id", table_name="orchestration_states")
    op.drop_table("orchestration_states")
