from fastapi import FastAPI
from core.config import settings
from routers.health import router as health_router
from routers.todo import router as todo_router
from routers.auth import router as auth_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version=settings.version,
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(todo_router, prefix=settings.api_prefix)
