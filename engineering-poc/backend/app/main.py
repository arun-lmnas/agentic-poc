from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from app.jobs import JobManager

app = FastAPI(title="Engineering POC Task API")
tasks: list[str] = []
job_manager = JobManager()


class TaskRequest(BaseModel):
    title: str


class JobRequest(BaseModel):
    job_type: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tasks")
def list_tasks() -> dict[str, list[str]]:
    return {"tasks": tasks}


@app.post("/api/tasks", status_code=201)
def create_task(request: TaskRequest) -> dict[str, str]:
    title = request.title.strip()
    if not 3 <= len(title) <= 6:
        raise HTTPException(status_code=400, detail="Task title must be between 3 and 6 characters")
    tasks.append(title)
    return {"title": title}


@app.post("/api/jobs", status_code=status.HTTP_202_ACCEPTED)
def submit_job(request: JobRequest) -> dict[str, str]:
    try:
        job = job_manager.submit(request.job_type)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"job_id": job.job_id, "status": "queued"}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, object]:
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
