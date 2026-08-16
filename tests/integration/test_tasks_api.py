from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_task_lifecycle() -> None:
    client = TestClient(create_app())

    created = client.post("/tasks", json={"title": "Learn SAM"})
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Learn SAM"
    assert task["completed"] is False

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert listed.json() == [task]

    completed = client.patch(f"/tasks/{task['id']}/complete")
    assert completed.status_code == 200
    assert completed.json()["completed"] is True


def test_complete_missing_task_returns_not_found() -> None:
    client = TestClient(create_app())

    response = client.patch("/tasks/00000000-0000-0000-0000-000000000000/complete")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
