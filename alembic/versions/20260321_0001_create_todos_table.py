"""create todos table

Revision ID: 20260321_0001
Revises:
Create Date: 2026-03-21 11:05:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260321_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "todo" not in existing_tables:
        op.create_table(
            "todo",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_done", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "todo" in existing_tables:
        op.drop_table("todo")
