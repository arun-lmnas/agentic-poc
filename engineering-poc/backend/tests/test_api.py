from threading import Event

import pytest

from fastapi.testclient import TestClient

from app.jobs import JobManager
from app.main import app, job_manager, tasks

client = TestClient(app)


def setup_function() -> None:
    tasks.clear()

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


def wait_for_terminal_status(job_id: str) -> dict[str, object]:
    assert job_manager.wait(job_id)
    return client.get(f"/api/jobs/{job_id}").json()


def test_submit_health_check_returns_accepted_queued_job_and_result() -> None:
    response = client.post("/api/jobs", json={"job_type": "health-check"})

    assert response.status_code == 202
    submitted = response.json()
    assert submitted["status"] == "queued"
    assert submitted["job_id"]
    job = wait_for_terminal_status(submitted["job_id"])
    assert job == {
        "job_id": submitted["job_id"],
        "status": "completed",
        "result": {"status": "ok", "service": "engineering-poc-backend", "version": "1.0.0"},
        "error": None,
    }


def test_unknown_job_and_unsupported_job_type_return_clear_errors() -> None:
    assert client.get("/api/jobs/not-a-job").status_code == 404
    response = client.post("/api/jobs", json={"job_type": "not-supported"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported job type: not-supported"


def test_job_manager_tracks_running_completed_and_failed_lifecycles() -> None:
    started = Event()
    release = Event()

    def controlled_job() -> dict[str, str]:
        started.set()
        assert release.wait(timeout=1)
        return {"answer": "done"}

    manager = JobManager({"controlled": controlled_job, "broken": lambda: (_ for _ in ()).throw(RuntimeError())})
    try:
        controlled = manager.submit("controlled")
        assert started.wait(timeout=1)
        assert manager.get(controlled.job_id)["status"] == "running"
        release.set()
        failed = manager.submit("broken")
        manager.shutdown()
        assert manager.get(controlled.job_id) == {
            "job_id": controlled.job_id, "status": "completed", "result": {"answer": "done"}, "error": None
        }

        assert manager.get(failed.job_id) == {
            "job_id": failed.job_id, "status": "failed", "result": None, "error": "Job execution failed"
        }
    finally:
        manager.shutdown()


def test_concurrent_submissions_have_unique_ids_and_complete() -> None:
    responses = [client.post("/api/jobs", json={"job_type": "health-check"}) for _ in range(12)]
    assert all(response.status_code == 202 for response in responses)
    job_ids = [response.json()["job_id"] for response in responses]
    assert len(set(job_ids)) == len(job_ids)
    assert all(wait_for_terminal_status(job_id)["status"] == "completed" for job_id in job_ids)
