from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.task import Task


class TaskRepository(ABC):
    """Persistence contract required by task use cases."""

    @abstractmethod
    def save(self, task: Task) -> Task:
        """Create or update a task."""

    @abstractmethod
    def list_all(self) -> list[Task]:
        """Return every task."""

    @abstractmethod
    def get_by_id(self, task_id: UUID) -> Task | None:
        """Return one task if it exists."""
