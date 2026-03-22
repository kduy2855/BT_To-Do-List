from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from core.database import get_db, get_session
from main import app
from models.todo import Tag, Todo, TodoTagLink
from models.user import User


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_db] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    email = "tester@example.com"
    password = "secret123"

    register_response = client.post(
        "/api/v1/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
