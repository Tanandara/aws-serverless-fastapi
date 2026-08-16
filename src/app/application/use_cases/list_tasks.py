from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository


class ListTasks:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Task]:
        return self._repository.list_all()
