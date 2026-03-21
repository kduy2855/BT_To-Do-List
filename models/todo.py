from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text, event
from sqlmodel import Field, SQLModel

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(100), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    is_done: bool = Field(default=False)
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


@event.listens_for(Todo, "before_insert")
def set_timestamps(mapper, connection, target) -> None:
    now = datetime.utcnow()
    if not target.created_at:
        target.created_at = now
    target.updated_at = now


@event.listens_for(Todo, "before_update")
def touch_updated_at(mapper, connection, target) -> None:
    target.updated_at = datetime.utcnow()
