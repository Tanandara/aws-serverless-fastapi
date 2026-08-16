from uuid import UUID

from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """Volatile repository used by the local POC and tests."""

    def __init__(self) -> None:
        self._tasks: dict[UUID, Task] = {}

    def save(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def list_all(self) -> list[Task]:
        return list(self._tasks.values())

    def get_by_id(self, task_id: UUID) -> Task | None:
        return self._tasks.get(task_id)
