from collections.abc import Mapping
import os
from typing import Any
from uuid import UUID

import boto3

from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository


class DynamoDBTaskRepository(TaskRepository):
    """DynamoDB-backed task persistence for the Lambda deployment."""

    def __init__(self, table_name: str | None = None, *, table: Any | None = None) -> None:
        if table is not None:
            self._table = table
        elif table_name is not None:
            endpoint_url = os.getenv("DYNAMODB_ENDPOINT_URL")
            dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
            self._table = dynamodb.Table(table_name)
        else:
            raise ValueError("Either table_name or table must be provided.")

    def save(self, task: Task) -> Task:
        self._table.put_item(
            Item={
                "id": str(task.id),
                "title": task.title,
                "completed": task.completed,
            }
        )
        return task

    def list_all(self) -> list[Task]:
        tasks: list[Task] = []
        scan_arguments: dict[str, Any] = {}

        while True:
            response = self._table.scan(**scan_arguments)
            tasks.extend(self._to_task(item) for item in response.get("Items", []))

            last_evaluated_key = response.get("LastEvaluatedKey")
            if last_evaluated_key is None:
                return tasks

            scan_arguments["ExclusiveStartKey"] = last_evaluated_key

    def get_by_id(self, task_id: UUID) -> Task | None:
        response = self._table.get_item(Key={"id": str(task_id)})
        item = response.get("Item")
        return self._to_task(item) if item is not None else None

    @staticmethod
    def _to_task(item: Mapping[str, Any]) -> Task:
        return Task(
            id=UUID(item["id"]),
            title=item["title"],
            completed=item["completed"],
        )
