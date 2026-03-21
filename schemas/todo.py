from pydantic import BaseModel, ConfigDict, constr
from typing import List, Optional
from datetime import datetime

class ToDoCreate(BaseModel):
    title: constr(min_length=3, max_length=100)
    description: Optional[str] = None
    is_done: bool = False

class ToDoUpdate(BaseModel):
    title: Optional[constr(min_length=3, max_length=100)] = None
    description: Optional[str] = None
    is_done: Optional[bool] = None

class ToDo(ToDoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class ToDoListResponse(BaseModel):
    items: List[ToDo]
    total: int
    limit: int
    offset: int
