from typing import Optional
from fastapi import HTTPException
from schemas.todo import ToDo, ToDoCreate, ToDoUpdate, ToDoListResponse
from repositories.todo import TodoRepository

class TodoService:
    def __init__(self, repo: TodoRepository):
        self.repo = repo

    def create_todo(self, todo_in: ToDoCreate) -> ToDo:
        return self.repo.create(todo_in)

    def list_todos(
        self,
        is_done: Optional[bool] = None,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> ToDoListResponse:
        items, total = self.repo.list_and_count(
            is_done=is_done,
            q=q,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        return ToDoListResponse(items=items, total=total, limit=limit, offset=offset)

    def get_todo(self, todo_id: int) -> ToDo:
        todo = self.repo.get_by_id(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo

    def update_todo(self, todo_id: int, todo_in: ToDoUpdate) -> ToDo:
        updated = self.repo.update(todo_id, todo_in)
        if not updated:
            raise HTTPException(status_code=404, detail="Todo not found")
        return updated

    def complete_todo(self, todo_id: int) -> ToDo:
        update_data = ToDoUpdate(is_done=True)
        return self.update_todo(todo_id, update_data)

    def delete_todo(self, todo_id: int) -> None:
        if not self.repo.delete(todo_id):
            raise HTTPException(status_code=404, detail="Todo not found")
