"""create initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-21 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "raw_imports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_file", sa.Text(), nullable=False),
        sa.Column("source_month", sa.Text(), nullable=False),
        sa.Column("raw_json", postgresql.JSONB(), nullable=False),
        sa.Column("parser_version", sa.Text(), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("raw_import_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("raw_imports.id"), nullable=False),
        sa.Column("source_session_id", sa.Text(), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("weekday", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("is_rest_day", sa.Boolean(), nullable=True, default=False),
        sa.Column("deload_week", sa.Boolean(), nullable=True, default=False),
        sa.Column("data_status", sa.Text(), nullable=True, default="complete"),
        sa.Column("estimated_duration_min", sa.Integer(), nullable=True),
        sa.Column("session_tags", postgresql.JSONB(), nullable=True),
        sa.Column("source_ref_file", sa.Text(), nullable=True),
    )

    op.create_table(
        "warmups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("quote", sa.Text(), nullable=True),
        sa.Column("mobility", sa.Text(), nullable=True),
        sa.Column("activation", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
    )

    op.create_table(
        "session_blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("block_order", sa.Integer(), nullable=False, default=0),
        sa.Column("original_block_id", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("type", sa.Text(), nullable=True),
        sa.Column("is_optional", sa.Boolean(), nullable=True, default=False),
        sa.Column("content_mode", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("coach_notes", sa.Text(), nullable=True),
        sa.Column("has_external_reference", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("external_reference_text", sa.Text(), nullable=True),
        sa.Column("parsed_confidence", sa.Integer(), nullable=True),
    )

    op.create_table(
        "block_exercises_raw",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("block_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("session_blocks.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("format", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=False),
    )

    op.create_table(
        "block_items_canonical",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("block_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("session_blocks.id"), nullable=False),
        sa.Column("movement_name", sa.Text(), nullable=True),
        sa.Column("movement_family", sa.Text(), nullable=True),
        sa.Column("pattern_primary", sa.Text(), nullable=True),
        sa.Column("pattern_secondary", sa.Text(), nullable=True),
        sa.Column("modality", sa.Text(), nullable=True),
        sa.Column("sets", sa.Integer(), nullable=True),
        sa.Column("reps", sa.Text(), nullable=True),
        sa.Column("intensity_type", sa.Text(), nullable=True),
        sa.Column("intensity_value_json", postgresql.JSONB(), nullable=True),
        sa.Column("execution_notes", sa.Text(), nullable=True),
        sa.Column("raw_origin_text", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("block_items_canonical")
    op.drop_table("block_exercises_raw")
    op.drop_table("session_blocks")
    op.drop_table("warmups")
    op.drop_table("sessions")
    op.drop_table("raw_imports")
