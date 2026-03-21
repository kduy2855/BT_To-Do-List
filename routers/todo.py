from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from core.database import get_session
from repositories.todo import TodoRepository
from schemas.todo import ToDo, ToDoCreate, ToDoUpdate, ToDoListResponse
from services.todo import TodoService

router = APIRouter()

def get_todo_service(session: Session = Depends(get_session)) -> TodoService:
    repo = TodoRepository(session)
    return TodoService(repo)

@router.post("/todos", response_model=ToDo, status_code=201)
def create_todo(todo_in: ToDoCreate, service: TodoService = Depends(get_todo_service)):
    return service.create_todo(todo_in)

@router.get("/todos", response_model=ToDoListResponse)
def list_todos(
    is_done: Optional[bool] = Query(None),
    q: Optional[str] = Query(None, min_length=1),
    sort: Optional[str] = Query(None, pattern="^-?created_at$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: TodoService = Depends(get_todo_service),
):
    return service.list_todos(is_done, q, sort, limit, offset)

@router.get("/todos/{todo_id}", response_model=ToDo)
def get_todo(todo_id: int, service: TodoService = Depends(get_todo_service)):
    return service.get_todo(todo_id)

@router.put("/todos/{todo_id}", response_model=ToDo)
def update_todo(todo_id: int, todo_in: ToDoCreate, service: TodoService = Depends(get_todo_service)):
    return service.update_todo(todo_id, ToDoUpdate(**todo_in.model_dump()))

@router.patch("/todos/{todo_id}", response_model=ToDo)
def partial_update_todo(todo_id: int, todo_in: ToDoUpdate, service: TodoService = Depends(get_todo_service)):
    return service.update_todo(todo_id, todo_in)

@router.post("/todos/{todo_id}/complete", response_model=ToDo)
def complete_todo(todo_id: int, service: TodoService = Depends(get_todo_service)):
    return service.complete_todo(todo_id)

@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, service: TodoService = Depends(get_todo_service)):
    service.delete_todo(todo_id)
