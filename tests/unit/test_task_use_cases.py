from uuid import uuid4

from app.application.use_cases.complete_task import CompleteTask
from app.application.use_cases.create_task import CreateTask
from app.application.use_cases.list_tasks import ListTasks
from app.infrastructure.repositories.in_memory_task_repository import InMemoryTaskRepository


def test_create_task_persists_a_new_incomplete_task() -> None:
    repository = InMemoryTaskRepository()

    task = CreateTask(repository).execute("Learn SAM")

    assert task.title == "Learn SAM"
    assert task.completed is False
    assert repository.get_by_id(task.id) == task


def test_list_tasks_returns_saved_tasks() -> None:
    repository = InMemoryTaskRepository()
    create_task = CreateTask(repository)
    create_task.execute("First")
    create_task.execute("Second")

    tasks = ListTasks(repository).execute()

    assert [task.title for task in tasks] == ["First", "Second"]


def test_complete_task_marks_an_existing_task_complete() -> None:
    repository = InMemoryTaskRepository()
    task = CreateTask(repository).execute("Ship POC")

    completed_task = CompleteTask(repository).execute(task.id)

    assert completed_task is not None
    assert completed_task.completed is True


def test_complete_task_returns_none_for_unknown_task() -> None:
    result = CompleteTask(InMemoryTaskRepository()).execute(uuid4())

    assert result is None
