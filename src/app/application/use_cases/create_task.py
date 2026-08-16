from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository


class CreateTask:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def execute(self, title: str) -> Task:
        return self._repository.save(Task(title=title))
