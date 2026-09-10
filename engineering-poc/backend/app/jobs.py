from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from threading import Event, RLock
from typing import Any, Callable, Literal
from uuid import uuid4

JobStatus = Literal["queued", "running", "completed", "failed"]
JobHandler = Callable[[], dict[str, Any]]


@dataclass
class Job:
    job_id: str
    job_type: str
    status: JobStatus = "queued"
    result: dict[str, Any] | None = None
    error: str | None = None
    completed: Event = field(default_factory=Event, repr=False)

    def response(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


def health_check() -> dict[str, str]:
    """A small, deterministic job that is independent of HTTP handlers."""
    return {
        "status": "ok",
        "service": "engineering-poc-backend",
        "version": "1.0.0",
    }


class JobManager:
    """In-memory job lifecycle manager for this single-process POC."""

    def __init__(self, handlers: dict[str, JobHandler] | None = None) -> None:
        self._handlers = handlers or {"health-check": health_check}
        self._jobs: dict[str, Job] = {}
        self._lock = RLock()
        self._executor = ThreadPoolExecutor(thread_name_prefix="engineering-poc-job")

    @property
    def supported_job_types(self) -> set[str]:
        return set(self._handlers)

    def submit(self, job_type: str) -> Job:
        if job_type not in self._handlers:
            raise ValueError(f"Unsupported job type: {job_type}")

        job = Job(job_id=str(uuid4()), job_type=job_type)
        with self._lock:
            self._jobs[job.job_id] = job
        self._executor.submit(self._execute, job.job_id)
        return job

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return job.response() if job else None

    def wait(self, job_id: str, timeout: float = 1) -> bool:
        """Wait for a submitted job without polling or exposing executor details."""
        with self._lock:
            job = self._jobs.get(job_id)
        return bool(job and job.completed.wait(timeout=timeout))

    def _execute(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "running"

        try:
            result = self._handlers[job.job_type]()
        except Exception:
            # Preserve a useful, safe error without exposing exception details or traces.
            with self._lock:
                job.status = "failed"
                job.error = "Job execution failed"
        else:
            with self._lock:
                job.status = "completed"
                job.result = result
        finally:
            job.completed.set()

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
