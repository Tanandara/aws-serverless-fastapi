from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.application.use_cases.complete_task import CompleteTask
from app.application.use_cases.create_task import CreateTask
from app.application.use_cases.list_tasks import ListTasks
from app.domain.entities.task import Task
from app.presentation.schemas.task import CreateTaskRequest, TaskResponse


def _to_response(task: Task) -> TaskResponse:
    return TaskResponse(id=task.id, title=task.title, completed=task.completed)


def create_router(
    create_task: CreateTask,
    list_tasks: ListTasks,
    complete_task: CompleteTask,
) -> APIRouter:
    router = APIRouter(prefix="/tasks", tags=["tasks"])

    @router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
    def create(payload: CreateTaskRequest) -> TaskResponse:
        return _to_response(create_task.execute(payload.title))

    @router.get("", response_model=list[TaskResponse])
    def list_all() -> list[TaskResponse]:
        return [_to_response(task) for task in list_tasks.execute()]

    @router.patch("/{task_id}/complete", response_model=TaskResponse)
    def complete(task_id: UUID) -> TaskResponse:
        task = complete_task.execute(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return _to_response(task)

    return router
