"""add session source_hash

Revision ID: 0002_add_session_source_hash
Revises: 0001_initial
Create Date: 2026-03-22 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_session_source_hash"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sessions", sa.Column("source_hash", sa.Text(), nullable=True))
    op.create_index("ix_sessions_source_hash", "sessions", ["source_hash"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sessions_source_hash", table_name="sessions")
    op.drop_column("sessions", "source_hash")
