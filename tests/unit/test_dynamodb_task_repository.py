from uuid import uuid4

from app.domain.entities.task import Task
from app.infrastructure.repositories.dynamodb_task_repository import DynamoDBTaskRepository


class FakeDynamoDBTable:
    def __init__(self) -> None:
        self.items: dict[str, dict[str, object]] = {}

    def put_item(self, *, Item: dict[str, object]) -> None:
        self.items[Item["id"]] = Item

    def get_item(self, *, Key: dict[str, str]) -> dict[str, dict[str, object]]:
        item = self.items.get(Key["id"])
        return {"Item": item} if item is not None else {}

    def scan(self, **_: object) -> dict[str, list[dict[str, object]]]:
        return {"Items": list(self.items.values())}


def repository_with_fake_table() -> DynamoDBTaskRepository:
    return DynamoDBTaskRepository(table=FakeDynamoDBTable())


def test_save_and_read_task() -> None:
    repository = repository_with_fake_table()
    task = Task(title="Persist me")

    repository.save(task)

    assert repository.get_by_id(task.id) == task
    assert repository.list_all() == [task]


def test_get_by_id_returns_none_when_task_does_not_exist() -> None:
    assert repository_with_fake_table().get_by_id(uuid4()) is None
