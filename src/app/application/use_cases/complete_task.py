from uuid import UUID

from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository


class CompleteTask:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, task_id: UUID) -> Task | None:
        task = self._repository.get_by_id(task_id)
        if task is None:
            return None

        task.completed = True
        return self._repository.save(task)
