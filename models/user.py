from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(), default=datetime.utcnow, nullable=False)
    )