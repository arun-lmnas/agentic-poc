from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Engineering POC Task API")
tasks: list[str] = []


class TaskRequest(BaseModel):
    title: str


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
