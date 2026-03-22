from datetime import date
from typing import Optional

from fastapi import HTTPException

from repositories.todo import TodoRepository
from schemas.todo import ToDo, ToDoCreate, ToDoListResponse, ToDoUpdate


class TodoService:
    def __init__(self, repo: TodoRepository):
        self.repo = repo

    def create_todo(self, todo_in: ToDoCreate, owner_id: int) -> ToDo:
        return self.repo.create(todo_in, owner_id)

    def list_todos(
        self,
        owner_id: int,
        is_done: Optional[bool] = None,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> ToDoListResponse:
        items, total = self.repo.list_and_count(
            owner_id=owner_id,
            is_done=is_done,
            q=q,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        return ToDoListResponse(items=items, total=total, limit=limit, offset=offset)

    def list_overdue_todos(self, owner_id: int, limit: int = 10, offset: int = 0) -> ToDoListResponse:
        items, total = self.repo.list_due_and_count(
            owner_id=owner_id,
            target_date=date.today(),
            only_overdue=True,
            limit=limit,
            offset=offset,
        )
        return ToDoListResponse(items=items, total=total, limit=limit, offset=offset)

    def list_today_todos(self, owner_id: int, limit: int = 10, offset: int = 0) -> ToDoListResponse:
        items, total = self.repo.list_due_and_count(
            owner_id=owner_id,
            target_date=date.today(),
            only_overdue=False,
            limit=limit,
            offset=offset,
        )
        return ToDoListResponse(items=items, total=total, limit=limit, offset=offset)

    def get_todo(self, todo_id: int, owner_id: int) -> ToDo:
        todo = self.repo.get_by_id(todo_id, owner_id=owner_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo

    def update_todo(self, todo_id: int, owner_id: int, todo_in: ToDoUpdate) -> ToDo:
        updated = self.repo.update(todo_id, owner_id, todo_in)
        if not updated:
            raise HTTPException(status_code=404, detail="Todo not found")
        return updated

    def complete_todo(self, todo_id: int, owner_id: int) -> ToDo:
        return self.update_todo(todo_id, owner_id, ToDoUpdate(is_done=True))

    def delete_todo(self, todo_id: int, owner_id: int) -> None:
        if not self.repo.delete(todo_id, owner_id):
            raise HTTPException(status_code=404, detail="Todo not found")
