from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, constr, field_validator, model_validator


class ToDoCreate(BaseModel):
    title: constr(min_length=3, max_length=100)
    description: Optional[str] = None
    is_done: bool = False
    due_date: Optional[date] = None
    tags: List[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            value = [value]

        cleaned: List[str] = []
        seen: set[str] = set()
        for item in value:
            tag = str(item).strip().lower()
            if tag and tag not in seen:
                cleaned.append(tag)
                seen.add(tag)
        return cleaned


class ToDoUpdate(BaseModel):
    title: Optional[constr(min_length=3, max_length=100)] = None
    description: Optional[str] = None
    is_done: Optional[bool] = None
    due_date: Optional[date] = None
    tags: Optional[List[str]] = None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> Optional[List[str]]:
        if value is None:
            return None
        return ToDoCreate.normalize_tags(value)


class ToDo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    is_done: bool
    due_date: Optional[date] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def from_todo_model(cls, value: Any) -> Any:
        if hasattr(value, "title") and hasattr(value, "tags"):
            return {
                "id": value.id,
                "title": value.title,
                "description": value.description,
                "is_done": value.is_done,
                "due_date": value.due_date,
                "tags": [tag.name for tag in value.tags],
                "created_at": value.created_at,
                "updated_at": value.updated_at,
            }
        return value


class ToDoListResponse(BaseModel):
    items: List[ToDo]
    total: int
    limit: int
    offset: int
