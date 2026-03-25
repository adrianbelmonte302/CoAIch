"""add program days and future domain tables

Revision ID: 0003_add_program_days_domain
Revises: 0002_add_session_source_hash
Create Date: 2026-03-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_add_program_days_domain"
down_revision = "0002_add_session_source_hash"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workout_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("workout_type", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )

    op.create_table(
        "competitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("season_year", sa.Integer(), nullable=True),
        sa.Column("organizer", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )

    op.create_table(
        "program_days",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("raw_import_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("raw_imports.id"), nullable=False),
        sa.Column("day_id", sa.Text(), nullable=False),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("weekday", sa.Text(), nullable=True),
        sa.Column("display_title", sa.Text(), nullable=True),
        sa.Column("is_rest_day", sa.Boolean(), nullable=True, default=False),
        sa.Column("day_type", sa.Text(), nullable=True),
        sa.Column("deload_week", sa.Boolean(), nullable=True, default=False),
        sa.Column("program_source", sa.Text(), nullable=True),
        sa.Column("athlete_ref", sa.Text(), nullable=True),
        sa.Column("classification", postgresql.JSONB(), nullable=True),
        sa.Column("related_workout_ids", postgresql.JSONB(), nullable=True),
        sa.Column("related_competition_ids", postgresql.JSONB(), nullable=True),
        sa.Column("source_integrity", postgresql.JSONB(), nullable=True),
        sa.Column("raw_content", postgresql.JSONB(), nullable=True),
        sa.Column("session_context", postgresql.JSONB(), nullable=True),
        sa.Column("session_flow", postgresql.JSONB(), nullable=True),
        sa.Column("execution_log", postgresql.JSONB(), nullable=True),
        sa.Column("athlete_feedback", postgresql.JSONB(), nullable=True),
        sa.Column("derived_metrics", postgresql.JSONB(), nullable=True),
        sa.Column("ai_annotations", postgresql.JSONB(), nullable=True),
        sa.Column("schema_version", sa.Text(), nullable=True),
        sa.Column("entity_type", sa.Text(), nullable=True),
        sa.Column("source_hash", sa.Text(), nullable=True),
    )
    op.create_index("ix_program_days_source_hash", "program_days", ["source_hash"], unique=False)
    op.create_index("ix_program_days_day_id", "program_days", ["day_id"], unique=False)
    op.create_index("ix_program_days_date", "program_days", ["date"], unique=False)

    op.create_table(
        "athlete_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("program_day_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("program_days.id"), nullable=False),
        sa.Column("athlete_ref", sa.Text(), nullable=True),
        sa.Column("data", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "competition_workouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("competitions.id"), nullable=False),
        sa.Column("workout_definition_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workout_definitions.id"), nullable=True),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )

    op.create_table(
        "competition_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("competition_workout_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("competition_workouts.id"), nullable=False),
        sa.Column("athlete_ref", sa.Text(), nullable=True),
        sa.Column("result", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("competition_results")
    op.drop_table("competition_workouts")
    op.drop_table("athlete_executions")
    op.drop_index("ix_program_days_date", table_name="program_days")
    op.drop_index("ix_program_days_day_id", table_name="program_days")
    op.drop_index("ix_program_days_source_hash", table_name="program_days")
    op.drop_table("program_days")
    op.drop_table("competitions")
    op.drop_table("workout_definitions")
