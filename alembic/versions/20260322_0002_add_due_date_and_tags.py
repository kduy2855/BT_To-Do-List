"""add due date and tags

Revision ID: 20260322_0002
Revises: 20260321_0001
Create Date: 2026-03-22 00:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260322_0002"
down_revision = "20260321_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    todo_columns = {column["name"] for column in inspector.get_columns("todo")}

    if "owner_id" not in todo_columns:
        op.add_column("todo", sa.Column("owner_id", sa.Integer(), nullable=True))

    if "due_date" not in todo_columns:
        op.add_column("todo", sa.Column("due_date", sa.Date(), nullable=True))

    existing_tables = set(inspector.get_table_names())

    if "tag" not in existing_tables:
        op.create_table(
            "tag",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )
        op.create_index("ix_tag_name", "tag", ["name"], unique=True)

    if "todotaglink" not in existing_tables:
        op.create_table(
            "todotaglink",
            sa.Column("todo_id", sa.Integer(), nullable=False),
            sa.Column("tag_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["tag_id"], ["tag.id"]),
            sa.ForeignKeyConstraint(["todo_id"], ["todo.id"]),
            sa.PrimaryKeyConstraint("todo_id", "tag_id"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())
    todo_columns = {column["name"] for column in inspector.get_columns("todo")}

    if "todotaglink" in existing_tables:
        op.drop_table("todotaglink")

    if "tag" in existing_tables:
        indexes = {index["name"] for index in inspector.get_indexes("tag")}
        if "ix_tag_name" in indexes:
            op.drop_index("ix_tag_name", table_name="tag")
        op.drop_table("tag")

    if "due_date" in todo_columns:
        op.drop_column("todo", "due_date")

    if "owner_id" in todo_columns:
        op.drop_column("todo", "owner_id")
