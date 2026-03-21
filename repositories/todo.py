from pathlib import Path
import sys
from typing import Optional

from sqlalchemy import func, or_
from sqlmodel import Session, select

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.todo import Todo
from schemas.todo import ToDoCreate, ToDoUpdate


class TodoRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, todo_in: ToDoCreate) -> Todo:
        todo = Todo(**todo_in.model_dump())
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def list_and_count(
        self,
        *,
        is_done: Optional[bool] = None,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[Todo], int]:
        statement = select(Todo)
        count_statement = select(func.count()).select_from(Todo)

        if is_done is not None:
            statement = statement.where(Todo.is_done == is_done)
            count_statement = count_statement.where(Todo.is_done == is_done)

        if q:
            search_term = f"%{q}%"
            search_filter = or_(Todo.title.ilike(search_term), Todo.description.ilike(search_term))
            statement = statement.where(search_filter)
            count_statement = count_statement.where(search_filter)

        if sort == "created_at":
            statement = statement.order_by(Todo.created_at.asc())
        else:
            statement = statement.order_by(Todo.created_at.desc())

        statement = statement.offset(offset).limit(limit)

        items = self.session.exec(statement).all()
        total = self.session.exec(count_statement).one()
        return items, total

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        return self.session.get(Todo, todo_id)

    def update(self, todo_id: int, todo_in: ToDoUpdate) -> Optional[Todo]:
        todo = self.get_by_id(todo_id)
        if not todo:
            return None

        update_data = todo_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(todo, key, value)

        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete(self, todo_id: int) -> bool:
        todo = self.get_by_id(todo_id)
        if not todo:
            return False

        self.session.delete(todo)
        self.session.commit()
        return True
