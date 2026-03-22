from datetime import UTC, date, datetime
from pathlib import Path
import sys
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.todo import Tag, Todo
from schemas.todo import ToDoCreate, ToDoUpdate


class TodoRepository:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _not_deleted():
        return Todo.deleted_at.is_(None)

    def _get_or_create_tags(self, tag_names: list[str]) -> list[Tag]:
        if not tag_names:
            return []

        existing_tags = self.session.exec(select(Tag).where(Tag.name.in_(tag_names))).all()
        tag_map = {tag.name: tag for tag in existing_tags}

        ordered_tags: list[Tag] = []
        for name in tag_names:
            tag = tag_map.get(name)
            if tag is None:
                tag = Tag(name=name)
                self.session.add(tag)
                self.session.flush()
                tag_map[name] = tag
            ordered_tags.append(tag)
        return ordered_tags

    def create(self, todo_in: ToDoCreate, owner_id: int) -> Todo:
        payload = todo_in.model_dump()
        tag_names = payload.pop("tags", [])

        todo = Todo(**payload, owner_id=owner_id)
        todo.tags = self._get_or_create_tags(tag_names)

        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return self.get_by_id(todo.id, owner_id=owner_id)

    def list_and_count(
        self,
        *,
        owner_id: int,
        is_done: Optional[bool] = None,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[Todo], int]:
        statement = (
            select(Todo)
            .where(Todo.owner_id == owner_id, self._not_deleted())
            .options(selectinload(Todo.tags))
        )
        count_statement = (
            select(func.count())
            .select_from(Todo)
            .where(Todo.owner_id == owner_id, self._not_deleted())
        )

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
        elif sort == "due_date":
            statement = statement.order_by(Todo.due_date.asc().nullslast(), Todo.created_at.desc())
        elif sort == "-due_date":
            statement = statement.order_by(Todo.due_date.desc().nullslast(), Todo.created_at.desc())
        else:
            statement = statement.order_by(Todo.created_at.desc())

        statement = statement.offset(offset).limit(limit)

        items = self.session.exec(statement).all()
        total = self.session.exec(count_statement).one()
        return items, total

    def list_due_and_count(
        self,
        *,
        owner_id: int,
        target_date: date,
        only_overdue: bool,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[Todo], int]:
        statement = (
            select(Todo)
            .where(
                Todo.owner_id == owner_id,
                Todo.is_done.is_(False),
                Todo.due_date.is_not(None),
                self._not_deleted(),
            )
            .options(selectinload(Todo.tags))
        )
        count_statement = (
            select(func.count())
            .select_from(Todo)
            .where(
                Todo.owner_id == owner_id,
                Todo.is_done.is_(False),
                Todo.due_date.is_not(None),
                self._not_deleted(),
            )
        )

        if only_overdue:
            statement = statement.where(Todo.due_date < target_date)
            count_statement = count_statement.where(Todo.due_date < target_date)
        else:
            statement = statement.where(Todo.due_date == target_date)
            count_statement = count_statement.where(Todo.due_date == target_date)

        statement = statement.order_by(Todo.due_date.asc(), Todo.created_at.desc()).offset(offset).limit(limit)

        items = self.session.exec(statement).all()
        total = self.session.exec(count_statement).one()
        return items, total

    def get_by_id(self, todo_id: int, owner_id: Optional[int] = None) -> Optional[Todo]:
        statement = (
            select(Todo)
            .where(Todo.id == todo_id, self._not_deleted())
            .options(selectinload(Todo.tags))
        )
        if owner_id is not None:
            statement = statement.where(Todo.owner_id == owner_id)
        return self.session.exec(statement).first()

    def update(self, todo_id: int, owner_id: int, todo_in: ToDoUpdate) -> Optional[Todo]:
        todo = self.get_by_id(todo_id, owner_id=owner_id)
        if not todo:
            return None

        update_data = todo_in.model_dump(exclude_unset=True)
        if "tags" in update_data:
            todo.tags = self._get_or_create_tags(update_data.pop("tags") or [])

        for key, value in update_data.items():
            setattr(todo, key, value)

        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return self.get_by_id(todo.id, owner_id=owner_id)

    def delete(self, todo_id: int, owner_id: int) -> bool:
        todo = self.get_by_id(todo_id, owner_id=owner_id)
        if not todo:
            return False

        todo.deleted_at = datetime.now(UTC)
        self.session.add(todo)
        self.session.commit()
        return True

