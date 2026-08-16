from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Task:
    """A task managed by the application."""

    title: str
    completed: bool = False
    id: UUID = field(default_factory=uuid4)
