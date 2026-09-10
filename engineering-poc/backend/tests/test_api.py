import pytest

from fastapi.testclient import TestClient

from app.main import app, tasks

client = TestClient(app)


def setup_function() -> None:
    tasks.clear()


def test_health_info_returns_application_information() -> None:
    response = client.get("/api/health-info")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "engineering-poc-backend",
        "version": "1.0.0",
    }


def test_create_task_accepts_trimmed_three_character_title() -> None:
    response = client.post("/api/tasks", json={"title": "  abc  "})

    assert response.status_code == 201
    assert response.json() == {"title": "abc"}
    assert client.get("/api/tasks").json() == {"tasks": ["abc"]}


def test_create_task_accepts_six_character_title() -> None:
    response = client.post("/api/tasks", json={"title": "abcdef"})

    assert response.status_code == 201
    assert response.json() == {"title": "abcdef"}
    assert client.get("/api/tasks").json() == {"tasks": ["abcdef"]}


@pytest.mark.parametrize("title", ["ab", "abcdefg"])
def test_create_task_rejects_title_outside_three_to_six_characters(title: str) -> None:
    response = client.post("/api/tasks", json={"title": title})

    assert response.status_code == 400
    assert response.json()["detail"] == "Task title must be between 3 and 6 characters"
    assert client.get("/api/tasks").json() == {"tasks": []}
