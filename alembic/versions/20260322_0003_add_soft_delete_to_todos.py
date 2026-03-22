"""add soft delete to todos

Revision ID: 20260322_0003
Revises: 20260322_0002
Create Date: 2026-03-22 12:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260322_0003"
down_revision = "20260322_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    todo_columns = {column["name"] for column in inspector.get_columns("todo")}

    if "deleted_at" not in todo_columns:
        op.add_column("todo", sa.Column("deleted_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    todo_columns = {column["name"] for column in inspector.get_columns("todo")}

    if "deleted_at" in todo_columns:
        op.drop_column("todo", "deleted_at")
