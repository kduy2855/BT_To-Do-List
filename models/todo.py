from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text, event
from sqlmodel import Field, Relationship, SQLModel


class TodoTagLink(SQLModel, table=True):
    todo_id: Optional[int] = Field(
        default=None,
        foreign_key="todo.id",
        primary_key=True,
    )
    tag_id: Optional[int] = Field(
        default=None,
        foreign_key="tag.id",
        primary_key=True,
    )


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(50), unique=True, nullable=False, index=True))

    todos: list["Todo"] = Relationship(back_populates="tags", link_model=TodoTagLink)


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(100), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    is_done: bool = Field(default=False)
    due_date: Optional[date] = Field(default=None, sa_column=Column(Date(), nullable=True))
    owner_id: int = Field(sa_column=Column(ForeignKey("user.id"), nullable=False))
    created_at: datetime = Field(
        sa_column=Column(DateTime(), default=datetime.utcnow, nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(),
            default=datetime.utcnow,
            nullable=False,
        )
    )

    tags: list[Tag] = Relationship(back_populates="todos", link_model=TodoTagLink)


@event.listens_for(Todo, "before_insert")
def set_timestamps(mapper, connection, target) -> None:
    now = datetime.utcnow()
    if not target.created_at:
        target.created_at = now
    target.updated_at = now


@event.listens_for(Todo, "before_update")
def touch_updated_at(mapper, connection, target) -> None:
    target.updated_at = datetime.utcnow()
