from sqlmodel import select

from models.todo import Todo


def test_create_todo_success(client, auth_headers):
    response = client.post(
        "/api/v1/todos",
        headers=auth_headers,
        json={
            "title": "Buy groceries",
            "description": "Milk and bread",
            "tags": ["Home", "urgent", "home"],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk and bread"
    assert data["is_done"] is False
    assert data["tags"] == ["home", "urgent"]
    assert data["id"] > 0


def test_create_todo_validation_fail(client, auth_headers):
    response = client.post(
        "/api/v1/todos",
        headers=auth_headers,
        json={"title": "ab"},
    )

    assert response.status_code == 422


def test_get_todo_not_found_returns_404(client, auth_headers):
    response = client.get("/api/v1/todos/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


def test_create_todo_auth_fail(client):
    response = client.post(
        "/api/v1/todos",
        json={"title": "Unauthorized request"},
    )

    assert response.status_code == 401


def test_delete_todo_sets_deleted_at_and_hides_item(client, auth_headers, db_session):
    create_response = client.post(
        "/api/v1/todos",
        headers=auth_headers,
        json={"title": "Soft delete me"},
    )
    todo_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert get_response.status_code == 404

    list_response = client.get("/api/v1/todos", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0

    deleted_todo = db_session.exec(select(Todo).where(Todo.id == todo_id)).first()
    assert deleted_todo is not None
    assert deleted_todo.deleted_at is not None


def test_soft_deleted_todo_cannot_be_updated(client, auth_headers):
    create_response = client.post(
        "/api/v1/todos",
        headers=auth_headers,
        json={"title": "Cannot update me"},
    )
    todo_id = create_response.json()["id"]

    client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)

    update_response = client.patch(
        f"/api/v1/todos/{todo_id}",
        headers=auth_headers,
        json={"title": "Updated title"},
    )

    assert update_response.status_code == 404
