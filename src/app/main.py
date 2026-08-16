from fastapi import FastAPI
from mangum import Mangum
import uvicorn

from app.application.use_cases.complete_task import CompleteTask
from app.application.use_cases.create_task import CreateTask
from app.application.use_cases.list_tasks import ListTasks
from app.infrastructure.repositories.in_memory_task_repository import InMemoryTaskRepository
from app.presentation.routes.health import router as health_router
from app.presentation.routes.tasks import create_router as create_tasks_router


def create_app() -> FastAPI:
    """Build the HTTP app and wire its concrete dependencies."""
    app = FastAPI(title="Tasks POC", version="0.1.0")
    repository = InMemoryTaskRepository()

    app.include_router(health_router)
    app.include_router(
        create_tasks_router(
            create_task=CreateTask(repository),
            list_tasks=ListTasks(repository),
            complete_task=CompleteTask(repository),
        )
    )
    return app


app = create_app()
# AWS Lambda handler: translates API Gateway HTTP API events into ASGI requests.
handler = Mangum(app)


def main() -> None:
    """Run the Tasks API using the installed console command."""
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
